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
  default     = "sentinel_nat_topic"
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

resource "google_project_service" "enable_logging_api" {
  service = "logging.googleapis.com"
  project = data.google_project.project.project_id
}

resource "google_pubsub_topic" "sentinel_nat_topic" {
  count   = "${var.topic-name != "sentinel_nat_topic" ? 0 : 1}"
  name    = var.topic-name
  project = data.google_project.project.project_id
}

# NAT subscription name
resource "google_pubsub_subscription" "sentinel-subscription_natlogs" {
  project = data.google_project.project.project_id
  name    = "sentinel-subscription_natlogs"
  topic   = var.topic-name
  depends_on = [google_pubsub_topic.sentinel_nat_topic]
}

# Audit subscription name must start with NAT subscription name and end with "_audit" — essential for connector to work.
# Example: If NAT subscription is "sentinel-subscription_natlogs", audit subscription should be "sentinel-subscription_natlogs_audit"

resource "google_pubsub_subscription" "sentinel-subscription_natlogs_audit" {
  project = data.google_project.project.project_id
  name    = "sentinel-subscription_natlogs_audit"
  topic   = var.topic-name
  depends_on = [google_pubsub_topic.sentinel_nat_topic]
}

resource "google_logging_project_sink" "sentinel_sink" {
  project    = data.google_project.project.project_id
  count      = var.organization-id == "" ? 1 : 0
  name       = "nat-logs-sentinel-sink"
  destination = "pubsub.googleapis.com/projects/${data.google_project.project.project_id}/topics/${var.topic-name}"
  depends_on = [google_pubsub_topic.sentinel_nat_topic]

 filter = <<EOT
  logName="compute.googleapis.com%2Fnat_flows" OR (resource.type="gce_router" AND protoPayload.serviceName="compute.googleapis.com" AND protoPayload.methodName:"v1.compute.routers.")
  EOT 
  unique_writer_identity = true
}

resource "google_logging_organization_sink" "sentinel_organization_sink" {
  count = var.organization-id == "" ? 0 : 1
  name   = "nat-logs-organization-sentinel-sink"
  org_id = var.organization-id
  destination = "pubsub.googleapis.com/projects/${data.google_project.project.project_id}/topics/${var.topic-name}"

 filter = <<EOT
  logName="compute.googleapis.com%2Fnat_flows" OR (resource.type="gce_router" AND protoPayload.serviceName="compute.googleapis.com" AND protoPayload.methodName:"v1.compute.routers.")
  EOT 

  include_children = true
}

resource "google_project_iam_binding" "log_writer" {
  count   = var.organization-id == "" ? 1 : 0
  project = data.google_project.project.project_id
  role    = "roles/pubsub.publisher"

  members = [
    google_logging_project_sink.sentinel_sink[0].writer_identity
  ]
}

resource "google_project_iam_binding" "log_writer_organization" {
  count   = var.organization-id == "" ? 0 : 1
  project = data.google_project.project.project_id
  role    = "roles/pubsub.publisher"

  members = [
    google_logging_organization_sink.sentinel_organization_sink[0].writer_identity
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
  value = google_pubsub_subscription.sentinel-subscription_natlogs.name
}

