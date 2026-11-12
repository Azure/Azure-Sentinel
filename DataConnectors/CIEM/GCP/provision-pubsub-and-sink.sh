#!/usr/bin/env bash
#
# UCC (Unified Connectors) - GCP connector onboarding
# =============================================================================
# VERSION 2 of 2:  PROVISION Pub/Sub + logging sink
# =============================================================================
# This script provisions everything the unified connector needs, INCLUDING the
# Pub/Sub topic, the Pub/Sub subscription and the logging sink that streams GCP
# audit logs into the subscription.
#
# Use the companion "bring your own" script (existing-pubsub-and-sink.sh) instead when
# the Pub/Sub topic, subscription and logging sink already exist in the project.
#
# Identity model: a SINGLE Workload Identity Provider accepting the configured
# UCC log-collection audience and a SINGLE service account are created.
#
# Existing resources may be updated or skipped. Verify ownership and wiring
# before running; failures can leave partial changes without rollback.
# =============================================================================
set -euo pipefail

# -----------------------------------------------------------------------------
# 1. Connector parameters (collected by the unified connectors experience)
#    REQUIRED — provide all six values (supplied by the UCC experience) either as
#    environment variables or by filling them in below. The script aborts if any
#    value is left blank. This does not validate project or tenant identity.
# -----------------------------------------------------------------------------
PROJECT_ID="${PROJECT_ID:-}"
PROJECT_NUMBER="${PROJECT_NUMBER:-}"
TENANT_ID="${TENANT_ID:-}"
WORKLOAD_IDENTITY_PROVIDER_ID="${WORKLOAD_IDENTITY_PROVIDER_ID:-}"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_EMAIL:-}"
SUBSCRIPTION_NAME="${SUBSCRIPTION_NAME:-}"

# -----------------------------------------------------------------------------
# 2. Unified Connectors (UCC) constants (do not change)
# -----------------------------------------------------------------------------
ISSUER_URI="https://sts.windows.net/33e01921-4d64-4f8c-a055-5bdaffd5e33d"
LOG_COLLECTION_AUDIENCE="api://2041288c-b303-4ca0-9076-9612db3beeb2"
ATTRIBUTE_MAPPING="google.subject=assertion.sub"

# -----------------------------------------------------------------------------
# 3. Resource configuration
# -----------------------------------------------------------------------------
POOL_DISPLAY_NAME="Microsoft"
POOL_DESCRIPTION="Microsoft"
SERVICE_ACCOUNT_DISPLAY_NAME="Unified Connectors"

# Pub/Sub data-collection role (granted on the Pub/Sub subscription)
PUBSUB_ROLE_ID="UccPubSubDataCollectionRole"
PUBSUB_ROLE_TITLE="Unified Connectors Pub/Sub Data Collection Custom Role"
PUBSUB_ROLE_DESCRIPTION="Unified Connectors Pub/Sub Data Collection Custom Role"
PUBSUB_ROLE_PERMISSIONS="pubsub.subscriptions.consume,pubsub.subscriptions.get"
PUBSUB_ROLE_STAGE="ALPHA"

# Hydration (historic data collection) role (granted at the project level)
HYDRATION_ROLE_ID="UccHydrationDataCollectionRole"
HYDRATION_ROLE_TITLE="Unified Connectors Hydration Data Collection Custom Role"
HYDRATION_ROLE_DESCRIPTION="Unified Connectors hydration (historic data collection) custom role"
HYDRATION_ROLE_PERMISSIONS="logging.logEntries.list,logging.privateLogEntries.list"
HYDRATION_ROLE_STAGE="ALPHA"

# Pub/Sub + logging sink (created by THIS script)
TOPIC_NAME="UCC-ControlPlane-Topic"
SINK_NAME="UCC-ControlPlane-Sink"
LOG_FILTER='logName:"cloudaudit.googleapis.com"'
LOGGING_SERVICE_AGENT="cloud-logs@system.gserviceaccount.com"

# -----------------------------------------------------------------------------
# 4. Derived values
# -----------------------------------------------------------------------------
# The Workload Identity Pool ID is the Microsoft Entra tenant ID with the
# hyphens removed (GCP pool IDs may not contain hyphens beyond 4-32 chars).
WORKLOAD_IDENTITY_POOL_ID="${TENANT_ID//-/}"
SERVICE_ACCOUNT_ID="${SERVICE_ACCOUNT_EMAIL%%@*}"
ALLOWED_AUDIENCES="${LOG_COLLECTION_AUDIENCE}"
POOL_PRINCIPAL_SET="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${WORKLOAD_IDENTITY_POOL_ID}/*"

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
log() { echo; echo "==> $*"; }

require_params() {
  local var
  for var in PROJECT_ID PROJECT_NUMBER TENANT_ID \
             WORKLOAD_IDENTITY_PROVIDER_ID SERVICE_ACCOUNT_EMAIL SUBSCRIPTION_NAME; do
    if [[ -z "${!var}" ]]; then
      echo "ERROR: required parameter '$var' is empty." >&2
      exit 1
    fi
  done
}

ensure_workload_identity_pool() {
  if gcloud iam workload-identity-pools describe "$WORKLOAD_IDENTITY_POOL_ID" \
       --location="global" --project="$PROJECT_ID" >/dev/null 2>&1; then
    gcloud iam workload-identity-pools update "$WORKLOAD_IDENTITY_POOL_ID" \
      --location="global" --project="$PROJECT_ID" \
      --display-name="$POOL_DISPLAY_NAME" \
      --description="$POOL_DESCRIPTION"
  else
    gcloud iam workload-identity-pools create "$WORKLOAD_IDENTITY_POOL_ID" \
      --location="global" --project="$PROJECT_ID" \
      --display-name="$POOL_DISPLAY_NAME" \
      --description="$POOL_DESCRIPTION"
  fi
}

# Single OIDC provider that accepts the UCC log-collection audience.
ensure_oidc_provider() {
  local action="create-oidc"
  if gcloud iam workload-identity-pools providers describe "$WORKLOAD_IDENTITY_PROVIDER_ID" \
       --location="global" --workload-identity-pool="$WORKLOAD_IDENTITY_POOL_ID" \
       --project="$PROJECT_ID" >/dev/null 2>&1; then
    action="update-oidc"
  fi
  gcloud iam workload-identity-pools providers "$action" "$WORKLOAD_IDENTITY_PROVIDER_ID" \
    --location="global" \
    --workload-identity-pool="$WORKLOAD_IDENTITY_POOL_ID" \
    --project="$PROJECT_ID" \
    --issuer-uri="$ISSUER_URI" \
    --allowed-audiences="$ALLOWED_AUDIENCES" \
    --attribute-mapping="$ATTRIBUTE_MAPPING"
}

ensure_service_account() {
  if gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" \
       --project="$PROJECT_ID" >/dev/null 2>&1; then
    gcloud iam service-accounts update "$SERVICE_ACCOUNT_EMAIL" \
      --display-name="$SERVICE_ACCOUNT_DISPLAY_NAME" --project="$PROJECT_ID"
  else
    gcloud iam service-accounts create "$SERVICE_ACCOUNT_ID" \
      --display-name="$SERVICE_ACCOUNT_DISPLAY_NAME" --project="$PROJECT_ID"
  fi
}

# Creates the custom role if it does not exist, otherwise updates it in place.
# Usage: ensure_custom_role <role_id> <title> <description> <permissions> <stage>
ensure_custom_role() {
  local role_id="$1" title="$2" description="$3" permissions="$4" stage="$5"
  local action="create"
  if gcloud iam roles describe "$role_id" --project="$PROJECT_ID" >/dev/null 2>&1; then
    action="update"
  fi
  gcloud iam roles "$action" "$role_id" --project="$PROJECT_ID" \
    --title="$title" \
    --description="$description" \
    --permissions="$permissions" \
    --stage="$stage"
}

# =============================================================================
# Execution
# =============================================================================
command -v gcloud >/dev/null 2>&1 || { echo "ERROR: gcloud CLI not found. Install the Google Cloud SDK." >&2; exit 1; }
require_params

log "Setting active project to '$PROJECT_ID'"
gcloud config set project "$PROJECT_ID"

log "Enabling required Google Cloud APIs"
gcloud services enable \
  iam.googleapis.com \
  sts.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iamcredentials.googleapis.com \
  compute.googleapis.com \
  apikeys.googleapis.com \
  logging.googleapis.com \
  pubsub.googleapis.com \
  storage.googleapis.com \
  --project="$PROJECT_ID"

log "Configuring Workload Identity Pool '$WORKLOAD_IDENTITY_POOL_ID'"
ensure_workload_identity_pool

log "Configuring OIDC provider '$WORKLOAD_IDENTITY_PROVIDER_ID' (UCC log-collection audience)"
ensure_oidc_provider

log "Configuring service account '$SERVICE_ACCOUNT_EMAIL'"
ensure_service_account

log "Allowing the Workload Identity Pool to impersonate the service account"
gcloud iam service-accounts add-iam-policy-binding "$SERVICE_ACCOUNT_EMAIL" \
  --project="$PROJECT_ID" \
  --role="roles/iam.workloadIdentityUser" \
  --member="$POOL_PRINCIPAL_SET"

log "Configuring custom Pub/Sub data-collection role '$PUBSUB_ROLE_ID'"
ensure_custom_role "$PUBSUB_ROLE_ID" "$PUBSUB_ROLE_TITLE" "$PUBSUB_ROLE_DESCRIPTION" \
  "$PUBSUB_ROLE_PERMISSIONS" "$PUBSUB_ROLE_STAGE"

log "Configuring custom hydration (historic data collection) role '$HYDRATION_ROLE_ID'"
ensure_custom_role "$HYDRATION_ROLE_ID" "$HYDRATION_ROLE_TITLE" "$HYDRATION_ROLE_DESCRIPTION" \
  "$HYDRATION_ROLE_PERMISSIONS" "$HYDRATION_ROLE_STAGE"

# ----- Provision Pub/Sub + logging sink (this is the create-everything version) -----
log "Granting the Cloud Logging service agent permission to publish to Pub/Sub"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$LOGGING_SERVICE_AGENT" \
  --role="roles/pubsub.publisher"

log "Creating Pub/Sub topic '$TOPIC_NAME'"
if gcloud pubsub topics describe "$TOPIC_NAME" --project="$PROJECT_ID" >/dev/null 2>&1; then
  echo "    Topic already exists; skipping."
else
  gcloud pubsub topics create "$TOPIC_NAME" --project="$PROJECT_ID"
fi

log "Creating Pub/Sub subscription '$SUBSCRIPTION_NAME'"
if gcloud pubsub subscriptions describe "$SUBSCRIPTION_NAME" --project="$PROJECT_ID" >/dev/null 2>&1; then
  echo "    Subscription already exists; skipping."
else
  gcloud pubsub subscriptions create "$SUBSCRIPTION_NAME" \
    --topic="$TOPIC_NAME" --project="$PROJECT_ID"
fi

log "Creating logging sink '$SINK_NAME'"
if gcloud logging sinks describe "$SINK_NAME" --project="$PROJECT_ID" >/dev/null 2>&1; then
  echo "    Sink already exists; skipping creation."
else
  gcloud logging sinks create "$SINK_NAME" \
    "pubsub.googleapis.com/projects/$PROJECT_ID/topics/$TOPIC_NAME" \
    --log-filter="$LOG_FILTER" \
    --project="$PROJECT_ID"
fi

log "Granting the sink's writer identity permission to publish to the topic"
SINK_SERVICE_ACCOUNT="$(gcloud logging sinks describe "$SINK_NAME" \
  --project="$PROJECT_ID" --format='value(writerIdentity)')"
gcloud pubsub topics add-iam-policy-binding "$TOPIC_NAME" \
  --member="$SINK_SERVICE_ACCOUNT" \
  --role="roles/pubsub.publisher" \
  --project="$PROJECT_ID"
# ------------------------------------------------------------------------------------

log "Granting the service account the Pub/Sub data-collection role on the subscription"
gcloud pubsub subscriptions add-iam-policy-binding "$SUBSCRIPTION_NAME" \
  --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
  --role="projects/$PROJECT_ID/roles/$PUBSUB_ROLE_ID" \
  --project="$PROJECT_ID"

log "Granting the service account the hydration role at the project level"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
  --role="projects/$PROJECT_ID/roles/$HYDRATION_ROLE_ID"

log "Done. GCP resources for the UCC connector are configured."
