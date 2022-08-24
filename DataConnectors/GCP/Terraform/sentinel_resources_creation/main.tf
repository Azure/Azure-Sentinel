terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.73.0"
    }
  }

  required_version = ">= 0.15.0"
}

variable "topic-name" {
  type    = string
  default = "sentinel-topic"
  description = "Name of existing topic"
}

data "google_project" "project" {}

resource "google_project_service" "enable-api" {
  service = "iam.googleapis.com"
  project = data.google_project.project.project_id
}

resource "google_pubsub_topic" "sentinel-topic" {
  count = "${var.topic-name != "sentinel-topic" ? 0 : 1}"
  name = var.topic-name
  project = data.google_project.project.project_id
}

resource "google_pubsub_subscription" "sentinel-subscription" {
  project = data.google_project.project.project_id
  name  = "sentinel-subscription"
  topic = var.topic-name
}

resource "google_iam_workload_identity_pool" "sentinel-workload-identity-pool" {
  provider                           = google-beta
  project = data.google_project.project.project_id
  workload_identity_pool_id = "33e019214d644f8ca0555bdaffd5e33d"
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
    allowed_audiences = ["api://f9245cc7-ba46-4568-bc0e-fdbf4aa42e80"]
    issuer_uri        = "https://sts.windows.net/33e01921-4d64-4f8c-a055-5bdaffd5e33d"
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

  condition {
    title       = "Permissions only for sentinel-subscription"
    expression  = "resource.name == (\"projects/_/subscriptions/${google_pubsub_subscription.sentinel-subscription.name}\")"
  }
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

output "GCP_subscription_name" {
  value       = google_pubsub_subscription.sentinel-subscription.name
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