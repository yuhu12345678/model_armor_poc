#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "========================================================"
echo " Running Promptfoo Evaluation on LiteLLM + Model Armor"
echo "========================================================"

if ! command -v promptfoo &> /dev/null; then
    echo "promptfoo command not found. Installing via npm..."
    npm install
fi

echo "[*] Executing guardrail test suite..."
npx promptfoo eval -c promptfooconfig.yaml

echo ""
echo "[*] Evaluation completed successfully."
echo "To view full visual evaluation report in browser, run:"
echo "  cd model_armor/promptfoo && npx promptfoo view"
