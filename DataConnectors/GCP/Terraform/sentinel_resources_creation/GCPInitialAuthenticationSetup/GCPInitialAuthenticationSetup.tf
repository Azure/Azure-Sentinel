terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.73.0"
    }
  }

  required_version = ">= 0.15.0"
}

locals{
  sentinel_app_id = "2041288c-b303-4ca0-9076-9612db3beeb2" // Do not change it. It's our Azure Active Directory app id that will be used for authentication with your project.
  sentinel_tenant_id = "33e01921-4d64-4f8c-a055-5bdaffd5e33d" // Do not change it. It's our tenant id that will be used for authentication with your project.
}

data "google_project" "project" {}

variable "tenant-id" {
  type    = string
  nullable = false
  description = "Please enter your Sentinel tenant id"
}

resource "google_project_service" "enable-api" {
  service = "iam.googleapis.com"
  project = data.google_project.project.project_id
}

resource "google_iam_workload_identity_pool" "sentinel-workload-identity-pool" {
  provider                           = google-beta
  project = data.google_project.project.project_id
  workload_identity_pool_id = replace(var.tenant-id, "-", "")
  display_name              = "sentinel-workload-identity-pool"
}

resource "google_iam_workload_identity_pool_provider" "sentinel-workload-identity-pool-provider" {
  provider                           = google-beta
  workload_identity_pool_id          = google_iam_workload_identity_pool.sentinel-workload-identity-pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "sentinel-identity-provider"
  project = data.google_project.project.project_id
  attribute_mapping                  = {
    "google.subject"                  = "assertion.sub"
  }

  oidc {
    allowed_audiences = ["api://${local.sentinel_app_id}"]
    issuer_uri        = "https://sts.windows.net/${local.sentinel_tenant_id}"
  }
}

resource "google_service_account" "sentinel-service-account" {
  account_id   = "sentinel-service-account"
  display_name = "Sentinel Service Account"
  project = data.google_project.project.project_id
}

resource "google_project_iam_custom_role" "sentinel-custom-role" {
  role_id     = "SentinelCustomRole"
  title       = "Sentinel Custom Role"
  description = "Role that allowes pulling messages from pub/sub"
  permissions = ["pubsub.subscriptions.consume", "pubsub.subscriptions.get"]
  project = data.google_project.project.project_id
}

resource "google_project_iam_member" "bind-sentinel-custom-role-to-sentinel-service-account" {
  provider = google-beta
  project = data.google_project.project.project_id
  role    = google_project_iam_custom_role.sentinel-custom-role.name

  member = "serviceAccount:${google_service_account.sentinel-service-account.account_id}@${data.google_project.project.project_id}.iam.gserviceaccount.com"
}

resource "google_service_account_iam_binding" "bind-workloadIdentityUser-role-to-sentinel-service-account"{
  provider = google-beta
  service_account_id = google_service_account.sentinel-service-account.name
  role    = "roles/iam.workloadIdentityUser"

  members = [
    "principalSet://iam.googleapis.com/projects/${data.google_project.project.number}/locations/global/workloadIdentityPools/${google_iam_workload_identity_pool.sentinel-workload-identity-pool.workload_identity_pool_id}/*",
  ]
}

output "GCP_project_id" {
  value       = data.google_project.project.project_id
}

output "GCP_project_number" {
  value       = data.google_project.project.number
}

output "Identity_federation_pool_name" {
  value       = google_iam_workload_identity_pool.sentinel-workload-identity-pool.display_name
}

output "Service_account_name" {
  value       = "${google_service_account.sentinel-service-account.account_id}@${data.google_project.project.project_id}.iam.gserviceaccount.com"
}

output "Identity_provider_id" {
  value       = google_iam_workload_identity_pool_provider.sentinel-workload-identity-pool-provider.workload_identity_pool_provider_id
}