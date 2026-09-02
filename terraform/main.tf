# Optional: Enable Google Cloud APIs (only if enable_project_services is true)
resource "google_project_service" "model_armor_api" {
  count                      = var.enable_project_services ? 1 : 0
  project                    = var.project_id
  service                    = "modelarmor.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_project_service" "dlp_api" {
  count                      = var.enable_project_services ? 1 : 0
  project                    = var.project_id
  service                    = "dlp.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

# Google Cloud Model Armor Template
resource "google_model_armor_template" "guardrails_template" {
  provider    = google-beta
  project     = var.project_id
  location    = var.location
  template_id = var.template_id
  labels      = var.labels

  filter_config {
    # Prompt Injection and Jailbreak Filter Settings
    pi_and_jailbreak_filter_settings {
      filter_enforcement = "ENABLED"
      confidence_level   = var.pi_and_jailbreak_confidence_level
    }

    # Responsible AI (RAI) Content Safety Filters
    rai_settings {
      rai_filters {
        filter_type      = "HARASSMENT"
        confidence_level = var.rai_harassment_confidence_level
      }
      rai_filters {
        filter_type      = "HATE_SPEECH"
        confidence_level = var.rai_hate_speech_confidence_level
      }
      rai_filters {
        filter_type      = "DANGEROUS"
        confidence_level = var.rai_dangerous_confidence_level
      }
      rai_filters {
        filter_type      = "SEXUALLY_EXPLICIT"
        confidence_level = var.rai_sexually_explicit_confidence_level
      }
    }

    # Sensitive Data Protection (SDP / DLP) Settings
    sdp_settings {
      basic_config {
        filter_enforcement = var.enable_sdp_basic_filter ? "ENABLED" : "DISABLED"
      }
    }

    # Malicious URI Filter Settings
    malicious_uri_filter_settings {
      filter_enforcement = var.enable_malicious_uri_filter ? "ENABLED" : "DISABLED"
    }
  }

  template_metadata {
    enforcement_type = var.enforcement_type

    log_template_operations = true
    log_sanitize_operations = true

    multi_language_detection {
      enable_multi_language_detection = var.enable_multi_language_detection
    }

    custom_prompt_safety_error_code    = 400
    custom_prompt_safety_error_message = "Your request was blocked by Model Armor security policies (detected prompt injection, sensitive data, or prohibited content)."

    custom_llm_response_safety_error_code    = 403
    custom_llm_response_safety_error_message = "The model response was blocked by Model Armor security policies."

    filter_version_selector {
      alias = "FILTER_VERSION_ALIAS_LATEST"
    }
  }
}
