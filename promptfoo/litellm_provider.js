/**
 * Custom LiteLLM Provider Class for Promptfoo with Model Armor Guardrails Support.
 */

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
        // Non-JSON response
      }

      if (response.ok) {
        const content = responseJson.choices?.[0]?.message?.content || responseText;
        return {
          output: content,
        };
      } else {
        // Model Armor blocked or error returned
        const errorMsg = responseJson.error?.message || responseText || `HTTP ${response.status}`;
        return {
          output: `[BLOCKED HTTP ${response.status}]: ${errorMsg}`,
        };
      }
    } catch (err) {
      return {
        error: `Network error connecting to LiteLLM: ${err.message}`,
      };
    }
  }
}

module.exports = LiteLLMModelArmorProvider;
