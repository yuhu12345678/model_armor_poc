"""Google Cloud Model Armor Client.

Provides a unified interface for inspecting and sanitizing user prompts and
model responses using Google Cloud Model Armor templates.
Supports both the official google-cloud-modelarmor SDK and direct REST API fallback.
"""

from __future__ import annotations

import os
import ssl
import json
import logging
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("model_armor_client")


class SanitizationAction(str, Enum):
    """Result action taken by Model Armor."""
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"
    SANITIZED = "SANITIZED"
    UNKNOWN = "UNKNOWN"


@dataclass
class FilterViolation:
    """Details of a single filter violation."""
    filter_type: str
    confidence_level: Optional[str] = None
    message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SanitizationResult:
    """Normalized result from a Model Armor sanitization operation."""
    is_safe: bool
    action: SanitizationAction
    sanitized_text: Optional[str] = None
    original_text: str = ""
    violations: List[FilterViolation] = field(default_factory=list)
    raw_response: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

    @property
    def has_violations(self) -> bool:
        return len(self.violations) > 0

    @property
    def effective_text(self) -> str:
        """Returns the sanitized text if available, otherwise original text."""
        return self.sanitized_text if self.sanitized_text is not None else self.original_text


class ModelArmorClient:
    """Client for interacting with Google Cloud Model Armor API."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        template_id: Optional[str] = None,
        credentials_path: Optional[str] = None,
        verify_ssl: Optional[bool] = None,
    ) -> None:
        self.project_id = (
            project_id
            or os.getenv("GCP_PROJECT_ID")
            or os.getenv("GOOGLE_CLOUD_PROJECT")
            or "rep-ds-sandbox"
        )
        self.location = (
            location
            or os.getenv("GCP_LOCATION")
            or os.getenv("GCP_PROJECT_LOCATION")
            or "us-central1"
        )
        self.template_id = (
            template_id
            or os.getenv("MODEL_ARMOR_TEMPLATE_ID")
            or "llm-guardrails-template"
        )
        self.credentials_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        if verify_ssl is not None:
            self.verify_ssl = verify_ssl
        else:
            env_verify = os.getenv("MODEL_ARMOR_VERIFY_SSL", "true").lower()
            self.verify_ssl = env_verify not in ("false", "0", "no")

        self._sdk_client = None
        self._init_client()

    def _init_client(self) -> None:
        """Initializes the SDK client if available, otherwise uses REST mode."""
        if self.credentials_path and os.path.exists(self.credentials_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path

        try:
            from google.api_core.client_options import ClientOptions
            from google.cloud import modelarmor_v1

            api_endpoint = f"modelarmor.{self.location}.rep.googleapis.com"
            client_options = ClientOptions(api_endpoint=api_endpoint)
            self._sdk_client = modelarmor_v1.ModelArmorClient(
                transport="rest",
                client_options=client_options,
            )
            logger.info("Initialized official google-cloud-modelarmor SDK client.")
        except Exception as exc:
            logger.debug("SDK client not available or initialization skipped (%s). Using REST mode.", exc)
            self._sdk_client = None

    @property
    def default_template_name(self) -> str:
        """Returns the fully qualified resource name for the template."""
        return f"projects/{self.project_id}/locations/{self.location}/templates/{self.template_id}"

    def sanitize_user_prompt(
        self,
        text: str,
        template_name: Optional[str] = None,
    ) -> SanitizationResult:
        """Sanitizes and evaluates a user prompt against Model Armor security filters."""
        template = template_name or self.default_template_name

        if self._sdk_client:
            try:
                return self._sanitize_prompt_via_sdk(text, template)
            except Exception as exc:
                logger.warning("SDK call failed: %s. Falling back to REST API.", exc)

        return self._sanitize_prompt_via_rest(text, template)

    def sanitize_model_response(
        self,
        text: str,
        template_name: Optional[str] = None,
    ) -> SanitizationResult:
        """Sanitizes and evaluates a model response against Model Armor security filters."""
        template = template_name or self.default_template_name

        if self._sdk_client:
            try:
                return self._sanitize_response_via_sdk(text, template)
            except Exception as exc:
                logger.warning("SDK call failed: %s. Falling back to REST API.", exc)

        return self._sanitize_response_via_rest(text, template)

    def _sanitize_prompt_via_sdk(self, text: str, template: str) -> SanitizationResult:
        """Executes prompt sanitization using the Python SDK."""
        from google.cloud import modelarmor_v1

        data_item = modelarmor_v1.DataItem(text=text)
        request = modelarmor_v1.SanitizeUserPromptRequest(
            name=template,
            user_prompt_data=data_item,
        )
        response = self._sdk_client.sanitize_user_prompt(request=request)
        response_dict = type(response).to_dict(response) if hasattr(type(response), "to_dict") else {}
        return self._parse_api_response(response_dict, original_text=text)

    def _sanitize_response_via_sdk(self, text: str, template: str) -> SanitizationResult:
        """Executes response sanitization using the Python SDK."""
        from google.cloud import modelarmor_v1

        data_item = modelarmor_v1.DataItem(text=text)
        request = modelarmor_v1.SanitizeModelResponseRequest(
            name=template,
            model_response_data=data_item,
        )
        response = self._sdk_client.sanitize_model_response(request=request)
        response_dict = type(response).to_dict(response) if hasattr(type(response), "to_dict") else {}
        return self._parse_api_response(response_dict, original_text=text)

    def _get_auth_token(self) -> str:
        """Retrieves a Google Cloud access token via google-auth or gcloud."""
        try:
            import google.auth
            import google.auth.transport.requests

            credentials, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            auth_req = google.auth.transport.requests.Request()
            credentials.refresh(auth_req)
            return credentials.token
        except Exception:
            # Fallback to gcloud CLI
            import subprocess

            cmd = ["gcloud", "auth", "print-access-token"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()

    def _create_ssl_context(self) -> ssl.SSLContext:
        """Creates an SSLContext configured with system CA bundles or fallback."""
        if not self.verify_ssl:
            return ssl._create_unverified_context()

        try:
            ca_file = os.getenv("SSL_CERT_FILE") or os.getenv("REQUESTS_CA_BUNDLE")
            if ca_file and os.path.exists(ca_file):
                ctx = ssl.create_default_context(cafile=ca_file)
            else:
                try:
                    import certifi
                    ctx = ssl.create_default_context(cafile=certifi.where())
                except ImportError:
                    ctx = ssl.create_default_context()
            return ctx
        except Exception as exc:
            logger.debug("Default SSL context creation error: %s. Using fallback.", exc)
            return ssl._create_unverified_context()

    def _http_post(self, url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any], str]:
        """Executes an HTTP POST request using urllib."""
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        ssl_ctx = self._create_ssl_context()

        try:
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=15) as resp:
                status_code = resp.status
                body = resp.read().decode("utf-8")
                try:
                    json_data = json.loads(body)
                except Exception:
                    json_data = {}
                return status_code, json_data, body
        except urllib.error.HTTPError as err:
            body = err.read().decode("utf-8") if err.fp else ""
            try:
                json_data = json.loads(body)
            except Exception:
                json_data = {}
            return err.code, json_data, body
        except urllib.error.URLError as uerr:
            # Handle certificate verify failure with automatic fallback
            if "CERTIFICATE_VERIFY_FAILED" in str(uerr):
                logger.warning("SSL verification failed for Model Armor endpoint. Retrying with unverified SSL context.")
                unverified_ctx = ssl._create_unverified_context()
                with urllib.request.urlopen(req, context=unverified_ctx, timeout=15) as resp:
                    status_code = resp.status
                    body = resp.read().decode("utf-8")
                    try:
                        json_data = json.loads(body)
                    except Exception:
                        json_data = {}
                    return status_code, json_data, body
            raise uerr

    def _sanitize_prompt_via_rest(self, text: str, template: str) -> SanitizationResult:
        """Executes prompt sanitization via REST API."""
        url = f"https://modelarmor.{self.location}.rep.googleapis.com/v1/{template}:sanitizeUserPrompt"
        token = self._get_auth_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "userPromptData": {
                "text": text
            }
        }

        try:
            status_code, data, raw_text = self._http_post(url, headers=headers, payload=payload)
            if status_code == 200:
                return self._parse_api_response(data, original_text=text)
            else:
                return SanitizationResult(
                    is_safe=False,
                    action=SanitizationAction.BLOCKED,
                    original_text=text,
                    error_message=f"Model Armor API error HTTP {status_code}: {raw_text}",
                    raw_response={"status_code": status_code, "text": raw_text},
                )
        except Exception as exc:
            logger.error("REST call failed: %s", exc)
            return SanitizationResult(
                is_safe=True,
                action=SanitizationAction.UNKNOWN,
                original_text=text,
                error_message=str(exc),
            )

    def _sanitize_response_via_rest(self, text: str, template: str) -> SanitizationResult:
        """Executes model response sanitization via REST API."""
        url = f"https://modelarmor.{self.location}.rep.googleapis.com/v1/{template}:sanitizeModelResponse"
        token = self._get_auth_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        payload = {
            "modelResponseData": {
                "text": text
            }
        }

        try:
            status_code, data, raw_text = self._http_post(url, headers=headers, payload=payload)
            if status_code == 200:
                return self._parse_api_response(data, original_text=text)
            else:
                return SanitizationResult(
                    is_safe=False,
                    action=SanitizationAction.BLOCKED,
                    original_text=text,
                    error_message=f"Model Armor API error HTTP {status_code}: {raw_text}",
                    raw_response={"status_code": status_code, "text": raw_text},
                )
        except Exception as exc:
            logger.error("REST call failed: %s", exc)
            return SanitizationResult(
                is_safe=True,
                action=SanitizationAction.UNKNOWN,
                original_text=text,
                error_message=str(exc),
            )

    def _parse_api_response(self, response_dict: Dict[str, Any], original_text: str) -> SanitizationResult:
        """Parses Model Armor API JSON response into a structured SanitizationResult."""
        violations: List[FilterViolation] = []
        is_safe = True
        action = SanitizationAction.ALLOWED
        sanitized_text: Optional[str] = None

        sanitization_result = response_dict.get("sanitizationResult", response_dict)
        filter_results = sanitization_result.get("filterResults", {})

        # Top-level match check
        top_match = sanitization_result.get("filterMatchState")
        if top_match == "MATCH_FOUND":
            is_safe = False
            action = SanitizationAction.BLOCKED

        # 1. Prompt Injection and Jailbreak
        pi_data = filter_results.get("pi_and_jailbreak") or filter_results.get("piAndJailbreak") or {}
        pi_inner = pi_data.get("piAndJailbreakFilterResult") or pi_data
        if pi_inner.get("matchState") == "MATCH_FOUND":
            is_safe = False
            action = SanitizationAction.BLOCKED
            violations.append(
                FilterViolation(
                    filter_type="PROMPT_INJECTION_AND_JAILBREAK",
                    confidence_level=pi_inner.get("confidenceLevel"),
                    message="Prompt injection or jailbreak attempt detected.",
                    details=pi_inner,
                )
            )

        # 2. Responsible AI (RAI) filters
        rai_data = filter_results.get("rai") or {}
        rai_inner = rai_data.get("raiFilterResult") or rai_data
        if rai_inner.get("matchState") == "MATCH_FOUND":
            is_safe = False
            action = SanitizationAction.BLOCKED
            rai_types = rai_inner.get("raiFilterTypeResults", {})
            for f_type, f_data in rai_types.items():
                if f_data.get("matchState") == "MATCH_FOUND":
                    violations.append(
                        FilterViolation(
                            filter_type=f"RAI_{f_type.upper()}",
                            confidence_level=f_data.get("confidenceLevel"),
                            message=f"Responsible AI violation detected: {f_type}",
                            details=f_data,
                        )
                    )

        # 3. Sensitive Data Protection (SDP)
        sdp_data = filter_results.get("sdp") or {}
        sdp_inner = sdp_data.get("sdpFilterResult") or sdp_data
        inspect_res = sdp_inner.get("inspectResult") or sdp_inner
        if inspect_res.get("matchState") == "MATCH_FOUND" or sdp_inner.get("matchState") == "MATCH_FOUND":
            violations.append(
                FilterViolation(
                    filter_type="SENSITIVE_DATA_PROTECTION",
                    message="Sensitive data / PII detected.",
                    details=sdp_inner,
                )
            )
            deident = sdp_inner.get("sdpDeidentifyResult") or sdp_data.get("sdpDeidentifyResult", {})
            if "data" in deident and "text" in deident["data"]:
                sanitized_text = deident["data"]["text"]
                if is_safe:
                    action = SanitizationAction.SANITIZED

        # 4. Malicious URIs
        uri_data = filter_results.get("malicious_uris") or filter_results.get("maliciousUris") or {}
        uri_inner = uri_data.get("maliciousUriFilterResult") or uri_data
        if uri_inner.get("matchState") == "MATCH_FOUND":
            is_safe = False
            action = SanitizationAction.BLOCKED
            violations.append(
                FilterViolation(
                    filter_type="MALICIOUS_URI",
                    message="Malicious URI detected in content.",
                    details=uri_inner,
                )
            )

        # 5. CSAM
        csam_data = filter_results.get("csam") or {}
        csam_inner = csam_data.get("csamFilterFilterResult") or csam_data
        if csam_inner.get("matchState") == "MATCH_FOUND":
            is_safe = False
            action = SanitizationAction.BLOCKED
            violations.append(
                FilterViolation(
                    filter_type="CSAM",
                    message="CSAM violation detected.",
                    details=csam_inner,
                )
            )

        # Sanitized text from top-level sanitizedItem
        if any(v.filter_type == "SENSITIVE_DATA_PROTECTION" for v in violations):
            sanitized_item = sanitization_result.get("sanitizedItem", {})
            if sanitized_item.get("text"):
                sanitized_text = sanitized_item["text"]
            if is_safe:
                action = SanitizationAction.SANITIZED

        metadata = sanitization_result.get("sanitizationMetadata", {})
        err_msg = metadata.get("errorMessage")

        return SanitizationResult(
            is_safe=is_safe,
            action=action,
            sanitized_text=sanitized_text,
            original_text=original_text,
            violations=violations,
            raw_response=response_dict,
            error_message=err_msg,
        )
