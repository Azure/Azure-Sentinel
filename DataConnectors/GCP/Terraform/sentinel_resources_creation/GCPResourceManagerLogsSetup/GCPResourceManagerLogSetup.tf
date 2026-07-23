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
  description = "Enter the GCP project ID where Pub/Sub topic and subscription should be created"
}

variable "topic-name" {
  type        = string
  default     = "sentinelgcp-rm-audit-topic"
  description = "Name of the Pub/Sub topic"
}

variable "organization-id" {
  type        = string
  description = "Organization ID for organization-level sink"
}

data "google_project" "project" {
  project_id = var.project-id
}

resource "google_project_service" "enable-logging-api" {
  service = "logging.googleapis.com"
  project = data.google_project.project.project_id
}

resource "google_pubsub_topic" "sentinelgcp-rm-audit-topic" {
  name    = var.topic-name
  project = data.google_project.project.project_id
}

resource "google_pubsub_subscription" "sentinel-subscription" {
  project     = data.google_project.project.project_id
  name        = "sentinel-subscription-gcp-rm-auditlogs"
  topic       = google_pubsub_topic.sentinelgcp-rm-audit-topic.id
  depends_on  = [google_pubsub_topic.sentinelgcp-rm-audit-topic]
}

resource "google_logging_organization_sink" "sentinel-organization-sink" {
  name        = "gcp-rm-audit-logs-organization-sentinel-sink"
  org_id      = var.organization-id
  destination = "pubsub.googleapis.com/projects/${data.google_project.project.project_id}/topics/${google_pubsub_topic.sentinelgcp-rm-audit-topic.name}"

  filter                  = "protoPayload.serviceName=cloudresourcemanager.googleapis.com OR protoPayload.serviceName=orgpolicy.googleapis.com"
  include_children        = true
  #unique_writer_identity  = true
  depends_on              = [google_pubsub_topic.sentinelgcp-rm-audit-topic]
}

resource "google_project_iam_binding" "log-writer-organization" {
  project = data.google_project.project.project_id
  role    = "roles/pubsub.publisher"

  members = [
    google_logging_organization_sink.sentinel-organization-sink.writer_identity
  ]
}

output "An_output_message" {
  value = "Organization sink created. Use the following values in Sentinel:"
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
