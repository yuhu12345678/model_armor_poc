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

# --- Model Armor floor settings (floor_settings.tf) ---
# Flip enable_floor_settings to true to have Terraform manage the project's
# floor setting. Confidence HIGH = only high-confidence detections trip the
# floor; use LOW_AND_ABOVE for the strictest baseline.
enable_floor_settings                     = true
floor_setting_confidence_level            = "HIGH"
floor_setting_enforcement_type            = "INSPECT_AND_BLOCK"
enable_floor_setting_enforcement          = true
floor_setting_location                    = "global"
floor_setting_integrated_services         = ["AI_PLATFORM"]
floor_setting_enable_sdp_basic_filter     = true
floor_setting_enable_malicious_uri_filter = true
# floor_setting_parent                    = "projects/rep-ds-sandbox"  # or folders/... / organizations/...

# --- SDP advanced inspection (sdp.tf) ---
# basic_config misses US_SOCIAL_SECURITY_NUMBER. Flip this to screen via a DLP
# inspect template instead; requires dlp.googleapis.com enabled on the project.
# advanced_config REPLACES basic_config, so sdp_info_types must also list the
# types basic_config already covered (credit card, GCP creds/API key).
enable_sdp_advanced_filter = true
sdp_min_likelihood         = "POSSIBLE"
