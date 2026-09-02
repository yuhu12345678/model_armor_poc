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
