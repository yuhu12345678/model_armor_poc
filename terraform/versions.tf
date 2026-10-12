terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 6.0.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = ">= 6.0.0"
    }
  }
}

# user_project_override/billing_project make the providers attribute API usage
# to this project rather than to the caller's ADC quota project. Without it,
# APIs that require a quota project (dlp.googleapis.com) fail with
# SERVICE_DISABLED against an unrelated consumer project.
provider "google" {
  project               = var.project_id
  region                = var.location
  billing_project       = var.project_id
  user_project_override = true
}

provider "google-beta" {
  project               = var.project_id
  region                = var.location
  billing_project       = var.project_id
  user_project_override = true
}
