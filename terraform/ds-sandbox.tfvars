project_id                             = "rep-ds-sandbox"
location                               = "us-central1"
template_id                            = "llm-guardrails-template"
enforcement_type                       = "INSPECT_AND_BLOCK"
pi_and_jailbreak_confidence_level      = "MEDIUM_AND_ABOVE"
rai_harassment_confidence_level        = "MEDIUM_AND_ABOVE"
rai_hate_speech_confidence_level       = "HIGH"
rai_dangerous_confidence_level         = "MEDIUM_AND_ABOVE"
rai_sexually_explicit_confidence_level = "HIGH"
enable_sdp_basic_filter                = true
enable_malicious_uri_filter            = true
enable_multi_language_detection        = true

labels = {
  environment = "sandbox"
  managed_by  = "terraform"
  service     = "model-armor"
}
