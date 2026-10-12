# Model Armor floor settings (feature-flagged via var.enable_floor_settings).
#
# A floor setting is a singleton per parent (project/folder/org) that defines the
# MINIMUM filtering every Model Armor template under that parent must apply.
# Templates may be stricter than the floor, never weaker. It lives at
# locations/global, independent of the regional template in main.tf.
resource "google_model_armor_floorsetting" "floor_setting" {
  count    = var.enable_floor_settings ? 1 : 0
  provider = google-beta

  parent   = coalesce(var.floor_setting_parent, "projects/${var.project_id}")
  location = var.floor_setting_location

  enable_floor_setting_enforcement = var.enable_floor_setting_enforcement
  integrated_services              = var.floor_setting_integrated_services

  filter_config {
    # Prompt Injection and Jailbreak Filter Settings
    pi_and_jailbreak_filter_settings {
      filter_enforcement = "ENABLED"
      confidence_level   = var.floor_setting_confidence_level
    }

    # Responsible AI (RAI) Content Safety Filters
    rai_settings {
      rai_filters {
        filter_type      = "HARASSMENT"
        confidence_level = var.floor_setting_confidence_level
      }
      rai_filters {
        filter_type      = "HATE_SPEECH"
        confidence_level = var.floor_setting_confidence_level
      }
      rai_filters {
        filter_type      = "DANGEROUS"
        confidence_level = var.floor_setting_confidence_level
      }
      rai_filters {
        filter_type      = "SEXUALLY_EXPLICIT"
        confidence_level = var.floor_setting_confidence_level
      }
    }

    # Sensitive Data Protection (SDP / DLP) Settings
    sdp_settings {
      basic_config {
        filter_enforcement = var.floor_setting_enable_sdp_basic_filter ? "ENABLED" : "DISABLED"
      }
    }

    # Malicious URI Filter Settings
    malicious_uri_filter_settings {
      filter_enforcement = var.floor_setting_enable_malicious_uri_filter ? "ENABLED" : "DISABLED"
    }
  }

  # Applies the floor to Vertex AI / AI Platform traffic.
  ai_platform_floor_setting {
    enable_cloud_logging = true
    # The provider accepts exactly one of these, so the unused mode must be null
    # (unset) rather than false.
    inspect_and_block = var.floor_setting_enforcement_type == "INSPECT_AND_BLOCK" ? true : null
    inspect_only      = var.floor_setting_enforcement_type == "INSPECT_ONLY" ? true : null
  }

  floor_setting_metadata {
    multi_language_detection {
      enable_multi_language_detection = var.enable_multi_language_detection
    }
  }

  depends_on = [google_project_service.model_armor_api]
}
