#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "========================================================"
echo " Running Promptfoo Evaluation on LiteLLM + Model Armor"
echo "========================================================"

# Load .env from parent if present
if [ -f ../.env ]; then
    export $(grep -v '^#' ../.env | xargs)
fi

echo "[*] Target Proxy: ${LITELLM_PROXY_URL:-https://llm.ds-sandbox.reputation.com}"
echo "[*] Target Model: ${LITELLM_MODEL:-gemini-2.5-flash}"

if [[ "$1" == "--redteam" || "$1" == "-r" ]]; then
    echo "[*] Running Automated Red-Team Audit with redteam_config.yaml..."
    npx promptfoo redteam run -c redteam_config.yaml
else
    echo "[*] Running Guardrail Evaluation Suite with promptfooconfig.yaml..."
    npx promptfoo eval -c promptfooconfig.yaml
fi

echo ""
echo "[*] Run completed."
echo "To view full visual evaluation report in browser, run:"
echo "  cd model_armor/promptfoo && npx promptfoo view"
