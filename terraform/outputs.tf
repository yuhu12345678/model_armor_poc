output "template_name" {
  description = "The full resource name of the Model Armor template"
  value       = google_model_armor_template.guardrails_template.name
}

output "template_id" {
  description = "The ID of the Model Armor template"
  value       = google_model_armor_template.guardrails_template.template_id
}

output "project_id" {
  description = "The GCP project ID"
  value       = var.project_id
}

output "location" {
  description = "The GCP region"
  value       = var.location
}

output "floor_setting_enabled" {
  description = "Whether Terraform manages a Model Armor floor setting for this parent"
  value       = var.enable_floor_settings
}

output "floor_setting_name" {
  description = "The full resource name of the Model Armor floor setting (null when the feature flag is off)"
  value       = try(google_model_armor_floorsetting.floor_setting[0].name, null)
}

output "floor_setting_confidence_level" {
  description = "Confidence threshold applied by the floor setting (null when the feature flag is off)"
  value       = var.enable_floor_settings ? var.floor_setting_confidence_level : null
}
