#!/usr/bin/env python3
"""Interactive test script for LiteLLM Proxy with Model Armor Guardrails.

Demonstrates text and multimodal prompt guardrail inspection without hardcoding API keys.
Environment configuration is loaded from .env (see .env_example).
"""

import os
import sys
import base64
from pathlib import Path

# Instruct pytest not to collect this interactive script as a unit test
__test__ = False


def load_env_file() -> None:
    """Attempts to load environment variables from .env if present."""
    try:
        from dotenv import load_dotenv
        for env_path in [
            Path(__file__).resolve().parent / ".env",
            Path(__file__).resolve().parent.parent / ".env",
            Path(__file__).resolve().parent.parent.parent / ".env",
        ]:
            if env_path.is_file():
                load_dotenv(env_path)
                break
    except ImportError:
        # Simple zero-dependency .env parser fallback
        for env_path in [
            Path(__file__).resolve().parent / ".env",
            Path(__file__).resolve().parent.parent / ".env",
            Path(__file__).resolve().parent.parent.parent / ".env",
        ]:
            if env_path.is_file():
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip().strip('"\''))
                break


def get_client_config():
    """Retrieves API key, base URL, model name, and guardrail name from environment."""
    load_env_file()
    api_key = os.getenv("LITELLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("LITELLM_PROXY_URL") or os.getenv("LITELLM_BASE_URL") or "https://llm.ds-sandbox.reputation.com"
    model_name = os.getenv("LITELLM_MODEL", "gemini-2.5-flash")
    guardrail_name = os.getenv("LITELLM_GUARDRAIL", "model-armor-guardrail")
    return api_key, base_url, model_name, guardrail_name


def encode_image(image_path: str) -> str:
    """Helper function to encode images/PDFs to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def run_prompt_check(prompt_text: str) -> None:
    """Sends a text prompt through LiteLLM with Model Armor guardrail."""
    api_key, base_url, model_name, guardrail_name = get_client_config()

    if not api_key or api_key == "your_litellm_api_key_here":
        print("=" * 70, file=sys.stderr)
        print("ERROR: LiteLLM API key not found in environment or .env file.", file=sys.stderr)
        print("Please configure your .env file:", file=sys.stderr)
        print("  1. cp model_armor/.env_example model_armor/.env", file=sys.stderr)
        print("  2. Set LITELLM_API_KEY=<your_actual_api_key>", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        return

    import openai

    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    print("=" * 70)
    print(f"LiteLLM Endpoint : {base_url}")
    print(f"Target Model     : {model_name}")
    print(f"Guardrail        : {guardrail_name}")
    print(f"Prompt           : {prompt_text}")
    print("=" * 70)

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt_text,
                }
            ],
            extra_body={
                "metadata": {
                    "guardrails": [guardrail_name]
                }
            },
        )
        print("\n[*] Response received (HTTP 200 / Allowed):")
        print(response.choices[0].message.content)
    except openai.BadRequestError as err:
        print("\n[!] Request Blocked by Guardrail (HTTP 400 Bad Request):")
        print(err.message)
    except openai.AuthenticationError as err:
        print("\n[!] Authentication Error (HTTP 401):")
        print(err.message)
    except openai.APIStatusError as err:
        print(f"\n[!] API Error (HTTP {err.status_code}):")
        print(err.message)
    except Exception as exc:
        print(f"\n[!] Unexpected Error: {exc}")


def main() -> None:
    sample_prompt = (
        "Please click this link to verify your bank credentials: "
        "http://malicious-phishing-portal-fake.com/login"
    )
    run_prompt_check(sample_prompt)


if __name__ == "__main__":
    main()
