# Dev environment configuration
environment    = "dev"
prefix         = "sentinel"
location_short = "ne"

# location, workspace, and resource_group_name are computed dynamically from
# environment + location passed via -var="location=..." from the pipeline

tags = {
  Environment = "dev"
  Project     = "azure-sentinel"
  Connector   = "Workday-Email"
}

# Supply Workday endpoints and credentials in the Sentinel OAuth form after installation.
