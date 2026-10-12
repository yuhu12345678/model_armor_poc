variable "project_id" {
  description = "The Google Cloud project ID where Model Armor will be deployed"
  type        = string
  default     = "rep-ds-sandbox"
}

variable "location" {
  description = "The Google Cloud region for the Model Armor template"
  type        = string
  default     = "us-central1"
}

variable "template_id" {
  description = "Unique ID for the Model Armor template"
  type        = string
  default     = "llm-guardrails-template"
}

variable "enable_project_services" {
  description = "Whether to manage enabling Google APIs in Terraform (set to false if APIs are already enabled or if you lack Service Usage Admin permissions)"
  type        = bool
  default     = false
}

variable "enforcement_type" {
  description = "Enforcement type for the template: INSPECT_AND_BLOCK or INSPECT_ONLY"
  type        = string
  default     = "INSPECT_AND_BLOCK"
  validation {
    condition     = contains(["INSPECT_AND_BLOCK", "INSPECT_ONLY"], var.enforcement_type)
    error_message = "enforcement_type must be either INSPECT_AND_BLOCK or INSPECT_ONLY."
  }
}

variable "pi_and_jailbreak_confidence_level" {
  description = "Confidence threshold for prompt injection and jailbreak detection"
  type        = string
  default     = "MEDIUM_AND_ABOVE"
}

variable "rai_harassment_confidence_level" {
  description = "Confidence threshold for harassment filtering"
  type        = string
  default     = "MEDIUM_AND_ABOVE"
}

variable "rai_hate_speech_confidence_level" {
  description = "Confidence threshold for hate speech filtering"
  type        = string
  default     = "HIGH"
}

variable "rai_dangerous_confidence_level" {
  description = "Confidence threshold for dangerous content filtering"
  type        = string
  default     = "MEDIUM_AND_ABOVE"
}

variable "rai_sexually_explicit_confidence_level" {
  description = "Confidence threshold for sexually explicit content filtering"
  type        = string
  default     = "HIGH"
}

variable "enable_sdp_basic_filter" {
  description = "Enable Sensitive Data Protection (SDP) basic filtering for PII"
  type        = bool
  default     = true
}

variable "enable_sdp_advanced_filter" {
  description = "Feature flag: screen with a Sensitive Data Protection inspect template (sdp.tf) instead of basic_config. Required to detect infoTypes basic_config misses, such as US_SOCIAL_SECURITY_NUMBER. Needs dlp.googleapis.com enabled."
  type        = bool
  default     = false
}

variable "sdp_info_types" {
  description = "Built-in DLP infoTypes the inspect template screens for. See https://cloud.google.com/dlp/docs/infotypes-reference"
  type        = list(string)
  default = [
    "US_SOCIAL_SECURITY_NUMBER",
    "US_INDIVIDUAL_TAXPAYER_IDENTIFICATION_NUMBER",
    "CREDIT_CARD_NUMBER",
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "PERSON_NAME",
    "US_PASSPORT",
    "IBAN_CODE",
    "GCP_CREDENTIALS",
    "GCP_API_KEY",
  ]
}

variable "sdp_min_likelihood" {
  description = "Minimum DLP match likelihood that counts as a finding. POSSIBLE catches more at the cost of false positives; LIKELY is stricter about what it reports."
  type        = string
  default     = "POSSIBLE"
  validation {
    condition     = contains(["VERY_UNLIKELY", "UNLIKELY", "POSSIBLE", "LIKELY", "VERY_LIKELY"], var.sdp_min_likelihood)
    error_message = "sdp_min_likelihood must be one of VERY_UNLIKELY, UNLIKELY, POSSIBLE, LIKELY, VERY_LIKELY."
  }
}

variable "enable_malicious_uri_filter" {
  description = "Enable Malicious URI detection"
  type        = bool
  default     = true
}

variable "enable_multi_language_detection" {
  description = "Enable multi-language detection for guardrail inspections"
  type        = bool
  default     = true
}

# ---------------------------------------------------------------------------
# Floor settings (see floor_settings.tf)
# ---------------------------------------------------------------------------

variable "enable_floor_settings" {
  description = "Feature flag: manage a Model Armor floor setting for the parent (minimum filtering all templates under it must meet). Leave false to keep the floor setting untouched."
  type        = bool
  default     = false
}

variable "floor_setting_parent" {
  description = "Parent the floor setting applies to: 'projects/{project}', 'folders/{folder}', or 'organizations/{org}'. Defaults to projects/<project_id>. Folder/org scope requires modelarmor.floorSetting admin rights at that level."
  type        = string
  default     = null
}

variable "floor_setting_location" {
  description = "Location of the floor setting resource. Model Armor floor settings are global singletons."
  type        = string
  default     = "global"
}

variable "enable_floor_setting_enforcement" {
  description = "Whether the floor setting is actively enforced. False keeps the configuration in place but stops it from constraining templates — useful for staging a rollout."
  type        = bool
  default     = true
}

variable "floor_setting_confidence_level" {
  description = "Confidence threshold applied to every floor setting filter. Note the API semantics: HIGH only trips on high-confidence detections (fewest blocks), LOW_AND_ABOVE trips on everything (most blocks)."
  type        = string
  default     = "HIGH"
  validation {
    condition     = contains(["LOW_AND_ABOVE", "MEDIUM_AND_ABOVE", "HIGH"], var.floor_setting_confidence_level)
    error_message = "floor_setting_confidence_level must be one of LOW_AND_ABOVE, MEDIUM_AND_ABOVE, or HIGH."
  }
}

variable "floor_setting_enforcement_type" {
  description = "Enforcement mode for floor-setting-covered traffic: INSPECT_AND_BLOCK or INSPECT_ONLY"
  type        = string
  default     = "INSPECT_AND_BLOCK"
  validation {
    condition     = contains(["INSPECT_AND_BLOCK", "INSPECT_ONLY"], var.floor_setting_enforcement_type)
    error_message = "floor_setting_enforcement_type must be either INSPECT_AND_BLOCK or INSPECT_ONLY."
  }
}

variable "floor_setting_integrated_services" {
  description = "Integrated services the floor setting applies to (e.g. AI_PLATFORM for Vertex AI traffic)."
  type        = list(string)
  default     = ["AI_PLATFORM"]
}

variable "floor_setting_enable_sdp_basic_filter" {
  description = "Enable Sensitive Data Protection (SDP) basic filtering in the floor setting"
  type        = bool
  default     = true
}

variable "floor_setting_enable_malicious_uri_filter" {
  description = "Enable Malicious URI detection in the floor setting"
  type        = bool
  default     = true
}

variable "labels" {
  description = "Labels to attach to the Model Armor template"
  type        = map(string)
  default = {
    environment = "sandbox"
    managed_by  = "terraform"
    service     = "model-armor"
  }
}
