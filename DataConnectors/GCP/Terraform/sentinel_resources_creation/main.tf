terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.73.0"
    }
  }

  required_version = ">= 0.15.0"
}

provider "google" {
  region  = "us-central1"
  zone    = "us-central1-c"
}

variable "topicName" {
  type    = string
  default = "SentinelTopic"
  description = "Topic name"
}

data "google_project" "project" {}

resource "google_project_service" "enable-api" {
  service = "iam.googleapis.com"
  project = data.google_project.project.project_id
}

resource "google_pubsub_topic" "sentinel-topic" {
  name = var.topicName
  project = data.google_project.project.project_id
}

resource "google_pubsub_subscription" "sentinel-subscription" {
  project = data.google_project.project.project_id
  name  = "SentinelSubscription"
  topic = google_pubsub_topic.sentinel-topic.name
}

resource "google_iam_workload_identity_pool" "sentinel-workload-identity-pool" {
  provider                           = google-beta
  project = data.google_project.project.project_id
  workload_identity_pool_id = "sentinel-workload-identity-pool"
  display_name              = "Sentinel Workload Identity Pool"
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