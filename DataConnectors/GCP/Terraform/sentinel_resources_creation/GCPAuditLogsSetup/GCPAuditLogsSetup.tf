terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "3.73.0"
    }
  }

  required_version = ">= 0.15.0"
}

data "google_project" "project" {}

variable "topic-name" {
  type    = string
  default = "sentinel-topic"
  description = "Name of existing topic"
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
  depends_on = [google_pubsub_topic.sentinel-topic]
}

resource "google_logging_project_sink" "sentinel-sink" {
  name = "audit-logs-sentinel-sink"
  destination = "pubsub.googleapis.com/projects/${data.google_project.project.project_id}/topics/${var.topic-name}"
  depends_on = [google_pubsub_topic.sentinel-topic]
  unique_writer_identity = true
}

resource "google_project_iam_binding" "log-writer" {
  project = data.google_project.project.project_id
  role = "roles/pubsub.publisher"

  members = [
    google_logging_project_sink.sentinel-sink.writer_identity,
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
