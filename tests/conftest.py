"""Pytest fixtures for Model Armor tests."""

import pytest
from typing import Dict, Any


@pytest.fixture
def mock_clean_response() -> Dict[str, Any]:
    """Mock API response for a safe/benign prompt."""
    return {
        "invocationResult": "SUCCESS",
        "sanitizationResult": {
            "filterResults": {
                "piAndJailbreak": {
                    "executionState": "EXECUTION_SUCCESS",
                    "matchState": "NO_MATCH_FOUND",
                },
                "rai": {
                    "executionState": "EXECUTION_SUCCESS",
                    "matchState": "NO_MATCH_FOUND",
                    "raiFilterTypeResults": {
                        "HARASSMENT": {"matchState": "NO_MATCH_FOUND"},
                        "HATE_SPEECH": {"matchState": "NO_MATCH_FOUND"},
                        "DANGEROUS": {"matchState": "NO_MATCH_FOUND"},
                        "SEXUALLY_EXPLICIT": {"matchState": "NO_MATCH_FOUND"},
                    },
                },
                "sdp": {
                    "executionState": "EXECUTION_SUCCESS",
                    "matchState": "NO_MATCH_FOUND",
                },
                "maliciousUris": {
                    "executionState": "EXECUTION_SUCCESS",
                    "matchState": "NO_MATCH_FOUND",
                },
            },
            "sanitizedItem": {
                "text": "Tell me a fun fact about space."
            },
        },
    }


@pytest.fixture
def mock_jailbreak_response() -> Dict[str, Any]:
    """Mock API response for a prompt injection / jailbreak attack."""
    return {
        "invocationResult": "BLOCKED",
        "sanitizationResult": {
            "filterResults": {
                "piAndJailbreak": {
                    "executionState": "EXECUTION_SUCCESS",
                    "matchState": "MATCH_FOUND",
                    "confidenceLevel": "HIGH",
                },
                "rai": {
                    "executionState": "EXECUTION_SUCCESS",
                    "matchState": "NO_MATCH_FOUND",
                },
            },
        },
    }


@pytest.fixture
def mock_sdp_masked_response() -> Dict[str, Any]:
    """Mock API response with SDP / PII masking applied."""
    return {
        "invocationResult": "SUCCESS",
        "sanitizationResult": {
            "filterResults": {
                "piAndJailbreak": {
                    "executionState": "EXECUTION_SUCCESS",
                    "matchState": "NO_MATCH_FOUND",
                },
                "sdp": {
                    "executionState": "EXECUTION_SUCCESS",
                    "matchState": "MATCH_FOUND",
                    "sdpDeidentifyResult": {
                        "data": {
                            "text": "My email is [EMAIL_ADDRESS] and phone is [PHONE_NUMBER]."
                        }
                    },
                },
            },
            "sanitizedItem": {
                "text": "My email is [EMAIL_ADDRESS] and phone is [PHONE_NUMBER]."
            },
        },
    }


@pytest.fixture
def mock_rai_violation_response() -> Dict[str, Any]:
    """Mock API response for a dangerous / hate speech RAI violation."""
    return {
        "invocationResult": "BLOCKED",
        "sanitizationResult": {
            "filterResults": {
                "rai": {
                    "executionState": "EXECUTION_SUCCESS",
                    "matchState": "MATCH_FOUND",
                    "raiFilterTypeResults": {
                        "DANGEROUS": {
                            "matchState": "MATCH_FOUND",
                            "confidenceLevel": "HIGH",
                        },
                        "HATE_SPEECH": {
                            "matchState": "NO_MATCH_FOUND",
                        },
                    },
                },
            },
        },
    }
