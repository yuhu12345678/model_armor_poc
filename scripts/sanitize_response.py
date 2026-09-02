#!/usr/bin/env python3
"""CLI utility to sanitize and evaluate a model response with Google Cloud Model Armor."""

import sys
import os
import argparse
import json

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from model_armor.client.model_armor_client import ModelArmorClient, SanitizationAction


def main() -> None:
    parser = argparse.ArgumentParser(description="Test model response sanitization with Model Armor")
    parser.add_argument(
        "--response-text",
        "-r",
        type=str,
        default="User secret email is alice.smith@example.com and phone is +1-555-0199.",
        help="Model response text to inspect",
    )
    parser.add_argument("--project", type=str, default=None, help="GCP Project ID")
    parser.add_argument("--location", type=str, default=None, help="GCP Region")
    parser.add_argument("--template", type=str, default=None, help="Template ID")
    parser.add_argument("--json", action="store_true", help="Output full JSON response")

    args = parser.parse_args()

    client = ModelArmorClient(
        project_id=args.project,
        location=args.location,
        template_id=args.template,
    )

    print(f"[*] Target Template: {client.default_template_name}")
    print(f"[*] Inspecting Response: {args.response_text}\n")

    result = client.sanitize_model_response(args.response_text)

    if args.json:
        print(json.dumps(result.raw_response, indent=2))
        return

    print("=" * 60)
    print(f"Safety Status    : {'SAFE' if result.is_safe else 'UNSAFE / BLOCKED'}")
    print(f"Action           : {result.action.value}")
    if result.sanitized_text:
        print(f"Sanitized Text   : {result.sanitized_text}")
    print(f"Violations Count : {len(result.violations)}")

    if result.violations:
        print("\nDetected Violations:")
        for v in result.violations:
            conf = f" (Confidence: {v.confidence_level})" if v.confidence_level else ""
            print(f"  - [{v.filter_type}]{conf}: {v.message}")

    print("=" * 60)


if __name__ == "__main__":
    main()
