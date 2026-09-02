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

variable "labels" {
  description = "Labels to attach to the Model Armor template"
  type        = map(string)
  default = {
    environment = "sandbox"
    managed_by  = "terraform"
    service     = "model-armor"
  }
}
