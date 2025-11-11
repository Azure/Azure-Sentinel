terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.73.0"
    }
  }

  required_version = ">= 0.15.0"
}

variable "project-id" {
  type        = string
  description = "Enter your project ID"
}

variable "topic-name" {
  type        = string
  default     = "sentinelGcpCloudRun-topic"
  description = "Name of existing topic"
}

variable "organization-id" {
  type        = string
  default     = ""
  description = "Organization id"
}

data "google_project" "project" {
  project_id = var.project-id
}

resource "google_project_service" "enable-logging-api" {
  service = "logging.googleapis.com"
  project = data.google_project.project.project_id
}

resource "google_pubsub_topic" "sentinelGcpCloudRun-topic" {
  count   = "${var.topic-name != "sentinelGcpCloudRun-topic" ? 0 : 1}"
  name    = var.topic-name
  project = data.google_project.project.project_id
}

resource "google_pubsub_subscription" "sentinel-subscription" {
  project = data.google_project.project.project_id
  name    = "sentinel-subscription-GcpCloudRunlogs"
  topic   = var.topic-name
  depends_on = [google_pubsub_topic.sentinelGcpCloudRun-topic]
}

resource "google_logging_project_sink" "sentinel-sink" {
  project    = data.google_project.project.project_id
  count      = var.organization-id == "" ? 1 : 0
  name       = "GcpCloudRun-logs-sentinel-sink"
  destination = "pubsub.googleapis.com/projects/${data.google_project.project.project_id}/topics/${var.topic-name}"
  depends_on = [google_pubsub_topic.sentinelGcpCloudRun-topic]

  filter = "protoPayload.serviceName=run.googleapis.com OR (resource.type=cloud_run_job) OR (resource.type=cloud_run_revision)"
  unique_writer_identity = true
}

resource "google_logging_organization_sink" "sentinel-organization-sink" {
  count = var.organization-id == "" ? 0 : 1
  name   = "GcpCloudRun-logs-organization-sentinel-sink"
  org_id = var.organization-id
  destination = "pubsub.googleapis.com/projects/${data.google_project.project.project_id}/topics/${var.topic-name}"

  filter = "protoPayload.serviceName=run.googleapis.com OR (resource.type=cloud_run_job) OR (resource.type=cloud_run_revision)"
  include_children = true
}

resource "google_project_iam_binding" "log-writer" {
  count   = var.organization-id == "" ? 1 : 0
  project = data.google_project.project.project_id
  role    = "roles/pubsub.publisher"

  members = [
    google_logging_project_sink.sentinel-sink[0].writer_identity
  ]
}

resource "google_project_iam_binding" "log-writer-organization" {
  count   = var.organization-id == "" ? 0 : 1
  project = data.google_project.project.project_id
  role    = "roles/pubsub.publisher"

  members = [
    google_logging_organization_sink.sentinel-organization-sink[0].writer_identity
  ]
}

output "An_output_message" {
  value = "Please copy the following values to Sentinel"
}

output "GCP_project_id" {
  value = data.google_project.project.project_id
}

output "GCP_project_number" {
  value = data.google_project.project.number
}

output "GCP_subscription_name" {
  value = google_pubsub_subscription.sentinel-subscription.name
}
