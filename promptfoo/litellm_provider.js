/**
 * Custom LiteLLM Provider Class for Promptfoo with Model Armor Guardrails Support.
 *
 * A non-2xx response means one of two very different things, and they must not
 * be conflated:
 *
 *   1. A guardrail rejection -- Model Armor blocked the prompt or the response.
 *      That is a successful test outcome for the block-expected cases, so it is
 *      returned as `output` with a "[BLOCKED ...]" prefix for assertions to match.
 *
 *   2. Anything else -- bad credentials, unknown model, proxy timeout, 5xx.
 *      That is an infrastructure failure, not a guardrail decision. It is
 *      returned as `error` so promptfoo reports it as an errored test rather
 *      than scoring it as a successful block.
 *
 * Reporting both as "[BLOCKED ...]: Model Armor" lets a dead proxy or an expired
 * key masquerade as a passing guardrail suite.
 */

// A rejection is only attributable to the guardrail if the proxy says so.
const GUARDRAIL_MARKERS = [/model\s*armor/i, /guardrail/i, /blocked by/i];

class LiteLLMModelArmorProvider {
  constructor(options = {}) {
    this.providerId = options.id || 'litellm-model-armor';
    this.config = options.config || {};
  }

  id() {
    return this.providerId;
  }

  async callApi(prompt, context) {
    const baseUrl = (process.env.LITELLM_PROXY_URL || this.config.apiBaseUrl || 'https://llm.ds-sandbox.reputation.com').replace(/\/+$/, '');
    const endpoint = baseUrl.endsWith('/v1') ? `${baseUrl}/chat/completions` : `${baseUrl}/v1/chat/completions`;
    const apiKey = process.env.LITELLM_API_KEY || process.env.LITELLM_MASTER_KEY || this.config.apiKey;
    const model = process.env.LITELLM_MODEL || this.config.model || 'gemini-2.5-flash';
    const guardrail = process.env.LITELLM_GUARDRAIL || 'model-armor-guardrail';

    const payload = {
      model: model,
      messages: [{ role: 'user', content: prompt }],
      guardrails: [guardrail],
      temperature: 0.0,
    };

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`,
        },
        body: JSON.stringify(payload),
      });

      const responseText = await response.text();
      let responseJson = {};
      try {
        responseJson = JSON.parse(responseText);
      } catch (e) {
        // Non-JSON response -- leave responseJson empty and fall back to text.
      }

      if (response.ok) {
        const content = responseJson.choices?.[0]?.message?.content;
        if (content === undefined || content === null) {
          return {
            error: `LiteLLM returned ${response.status} with no message content: ${responseText.slice(0, 500)}`,
          };
        }
        return { output: content };
      }

      const errorMsg = responseJson.error?.message || responseText || `HTTP ${response.status}`;

      // 5xx is never a guardrail decision, whatever the body says.
      const isGuardrailBlock =
        response.status < 500 && GUARDRAIL_MARKERS.some((re) => re.test(errorMsg));

      if (isGuardrailBlock) {
        return { output: `[BLOCKED HTTP ${response.status}]: ${errorMsg}` };
      }

      return {
        error: `LiteLLM request failed (HTTP ${response.status}), not a guardrail block: ${errorMsg}`,
      };
    } catch (err) {
      return {
        error: `Network error connecting to LiteLLM: ${err.message}`,
      };
    }
  }
}

module.exports = LiteLLMModelArmorProvider;
