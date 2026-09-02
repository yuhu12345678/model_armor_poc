"""LiteLLM Custom Guardrail Hook for Google Cloud Model Armor.

This hook intercepts pre-call requests and post-call responses to apply
Model Armor sanitization and security policies seamlessly.
"""

from __future__ import annotations

import os
import sys
import logging
from typing import Any, Dict, List, Optional

# Add parent directory to sys.path so we can import client
_current_dir = os.path.dirname(os.path.abspath(__file__))
_model_armor_root = os.path.dirname(os.path.dirname(_current_dir))
if _model_armor_root not in sys.path:
    sys.path.insert(0, _model_armor_root)

from model_armor.client.model_armor_client import (
    ModelArmorClient,
    SanitizationAction,
    SanitizationResult,
)

logger = logging.getLogger("litellm.model_armor_hook")

# Import LiteLLM CustomLogger if available, otherwise define a base class
try:
    from litellm.integrations.custom_logger import CustomLogger
    from litellm.exceptions import BadRequestError
except ImportError:
    class CustomLogger:  # type: ignore
        pass

    class BadRequestError(Exception):  # type: ignore
        def __init__(self, message: str, model: str = "", llm_provider: str = ""):
            super().__init__(message)
            self.message = message
            self.model = model
            self.llm_provider = llm_provider


class ModelArmorLiteLLMHook(CustomLogger):
    """LiteLLM Custom Logger / Hook for Google Cloud Model Armor."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        template_id: Optional[str] = None,
        default_on: bool = True,
        fail_on_error: bool = True,
    ) -> None:
        super().__init__()
        self.default_on = default_on
        self.fail_on_error = fail_on_error
        self.client = ModelArmorClient(
            project_id=project_id,
            location=location,
            template_id=template_id,
        )
        logger.info(
            "ModelArmorLiteLLMHook initialized for template: %s",
            self.client.default_template_name,
        )

    async def async_pre_call_hook(
        self,
        user_api_key_dict: Dict[str, Any],
        cache: Any,
        data: Dict[str, Any],
        call_type: str,
    ) -> Optional[Dict[str, Any]]:
        """Inspects and sanitizes user prompt before forwarding to LLM.

        Args:
            user_api_key_dict: User auth metadata.
            cache: Cache instance.
            data: LLM completion request parameters (messages, model, etc.).
            call_type: 'completion', 'chat_completion', etc.

        Returns:
            Updated data dict if modified, or None.
        """
        # Check if guardrail is enabled for this request
        guardrails = data.get("guardrails") or data.get("metadata", {}).get("guardrails", [])
        is_enabled = self.default_on or "model_armor" in guardrails or "model-armor" in guardrails

        if not is_enabled:
            return None

        messages: List[Dict[str, Any]] = data.get("messages", [])
        if not messages:
            return None

        # Extract user messages to sanitize
        modified = False
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content")
                if isinstance(content, str) and content.strip():
                    result: SanitizationResult = self.client.sanitize_user_prompt(content)
                    
                    # Store inspection metadata in request metadata
                    if "metadata" not in data:
                        data["metadata"] = {}
                    data["metadata"]["model_armor_prompt_result"] = {
                        "is_safe": result.is_safe,
                        "action": result.action.value,
                        "violations": [v.filter_type for v in result.violations],
                    }

                    if not result.is_safe:
                        violation_msg = (
                            f"Blocked by Google Cloud Model Armor: "
                            f"{', '.join([v.filter_type for v in result.violations])}"
                        )
                        logger.warning("Pre-call guardrail blocked prompt: %s", violation_msg)
                        raise BadRequestError(
                            message=violation_msg,
                            model=data.get("model", "unknown"),
                            llm_provider="model_armor_guardrail",
                        )

                    if result.action == SanitizationAction.SANITIZED and result.sanitized_text:
                        logger.info("Pre-call prompt sanitized/masked by Model Armor.")
                        msg["content"] = result.sanitized_text
                        modified = True

                break  # Sanitize latest user message

        return data if modified else None

    async def async_post_call_success_hook(
        self,
        data: Dict[str, Any],
        user_api_key_dict: Dict[str, Any],
        response: Any,
    ) -> Any:
        """Inspects and sanitizes model output after completion.

        Args:
            data: LLM request parameters.
            user_api_key_dict: User auth metadata.
            response: LLM completion response object.

        Returns:
            Updated response object.
        """
        guardrails = data.get("guardrails") or data.get("metadata", {}).get("guardrails", [])
        is_enabled = self.default_on or "model_armor" in guardrails or "model-armor" in guardrails

        if not is_enabled or not response:
            return response

        # Extract choices text
        choices = getattr(response, "choices", [])
        if not choices:
            return response

        for choice in choices:
            message = getattr(choice, "message", None)
            if message and hasattr(message, "content") and message.content:
                result: SanitizationResult = self.client.sanitize_model_response(message.content)

                if not result.is_safe:
                    violation_msg = (
                        f"LLM response blocked by Google Cloud Model Armor: "
                        f"{', '.join([v.filter_type for v in result.violations])}"
                    )
                    logger.warning("Post-call guardrail blocked response: %s", violation_msg)
                    if self.fail_on_error:
                        raise BadRequestError(
                            message=violation_msg,
                            model=data.get("model", "unknown"),
                            llm_provider="model_armor_guardrail",
                        )
                    else:
                        message.content = "[Response blocked due to content policy violation]"
                elif result.action == SanitizationAction.SANITIZED and result.sanitized_text:
                    logger.info("Post-call response sanitized/masked by Model Armor.")
                    message.content = result.sanitized_text

        return response

    async def async_post_call_failure_hook(
        self,
        request_data: Dict[str, Any],
        original_exception: Exception,
        user_api_key_dict: Dict[str, Any],
    ) -> None:
        """Logs guardrail exceptions."""
        logger.error("LiteLLM call failed with exception: %s", original_exception)


# Singleton instance for LiteLLM callbacks config
model_armor_hook_instance = ModelArmorLiteLLMHook()
