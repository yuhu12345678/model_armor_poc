# Promptfoo Safety Evaluation & Red-Teaming for Model Armor

This directory contains the [Promptfoo](https://promptfoo.dev) evaluation suite and automated adversarial red-teaming configuration to benchmark and audit **Google Cloud Model Armor** guardrails integrated with **LiteLLM**.

---

## Files

| File | Purpose |
| :--- | :--- |
| [`litellm_provider.js`](file:///Users/yhu/Code/llm-poc/model_armor/promptfoo/litellm_provider.js) | Custom Provider class that captures LiteLLM HTTP 200 completions and HTTP 400 Model Armor blocks into evaluated test outputs. |
| [`promptfooconfig.yaml`](file:///Users/yhu/Code/llm-poc/model_armor/promptfoo/promptfooconfig.yaml) | Standard test suite asserting that benign prompts pass through while attack prompts are intercepted. |
| [`redteam_config.yaml`](file:///Users/yhu/Code/llm-poc/model_armor/promptfoo/redteam_config.yaml) | Automated red-team sweep configuration covering prompt injections, jailbreaks, PII leakage, and harmful content. |
| [`run_promptfoo.sh`](file:///Users/yhu/Code/llm-poc/model_armor/promptfoo/run_promptfoo.sh) | Runner script with automated `.env` loading and `--redteam` flag support. |

---

## Environment Setup

Configure your LiteLLM API key and proxy endpoint in `model_armor/.env`:

```bash
cp ../.env_example ../.env
```

Ensure `model_armor/.env` contains:
```ini
LITELLM_PROXY_URL=https://llm.ds-sandbox.reputation.com
LITELLM_API_KEY=sk-your-active-api-key
LITELLM_MODEL=gemini-2.5-flash
LITELLM_GUARDRAIL=model-armor-guardrail
```

---

## Running Evaluations

### 1. Guardrail Evaluation Suite

Runs defined test cases asserting that Model Armor allows benign inputs and blocks attacks:

```bash
cd model_armor/promptfoo
./run_promptfoo.sh
```

*(Or via CLI: `npx promptfoo eval -c promptfooconfig.yaml`)*

---

### 2. Automated Red-Team Audit

Generates dynamic attack variations and audits guardrail robustness:

```bash
cd model_armor/promptfoo
./run_promptfoo.sh --redteam
```

*(Or via CLI: `npx promptfoo redteam run -c redteam_config.yaml`)*

---

### 3. Step-by-Step Red-Team Flow

```bash
cd model_armor/promptfoo

# Step 1: Generate adversarial probes
npx promptfoo redteam generate -c redteam_config.yaml

# Step 2: Evaluate probes against LiteLLM + Model Armor
npx promptfoo redteam eval -c redteam_config.yaml

# Step 3: Launch interactive visual dashboard
npx promptfoo view
```
