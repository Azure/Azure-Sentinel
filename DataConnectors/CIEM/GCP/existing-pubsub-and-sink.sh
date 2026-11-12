#!/usr/bin/env bash
#
# UCC (Unified Connectors) - GCP connector onboarding
# =============================================================================
# VERSION 1 of 2:  BRING YOUR OWN Pub/Sub + logging sink
# =============================================================================
# This script configures ONLY the identity and permissions the unified
# connector needs. It assumes the customer already has:
#   - a Pub/Sub topic
#   - a Pub/Sub subscription   (its name is provided as a parameter)
#   - a logging sink that streams GCP audit logs into the topic
#
# It does NOT create the topic, the subscription or the logging filter/sink.
# Use the companion script (provision-pubsub-and-sink.sh) when those resources
# still need to be created.
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
POOL_DISPLAY_NAME="unified connectors"
POOL_DESCRIPTION="UnifiedConnectors"
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

# Pub/Sub API must be enabled to bind IAM on the existing subscription; the
# logging and storage APIs are intentionally omitted because this script does
# not create a logging sink (the sink/topic/subscription already exist).
log "Enabling required Google Cloud APIs"
gcloud services enable \
  iam.googleapis.com \
  sts.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iamcredentials.googleapis.com \
  compute.googleapis.com \
  apikeys.googleapis.com \
  pubsub.googleapis.com \
  --project="$PROJECT_ID"

# Fail fast if the customer-provided subscription does not exist.
log "Verifying that the existing Pub/Sub subscription '$SUBSCRIPTION_NAME' is present"
if ! gcloud pubsub subscriptions describe "$SUBSCRIPTION_NAME" --project="$PROJECT_ID" >/dev/null 2>&1; then
  echo "ERROR: Pub/Sub subscription '$SUBSCRIPTION_NAME' was not found in project '$PROJECT_ID'." >&2
  echo "       This script assumes the topic, subscription and logging sink already exist." >&2
  echo "       Use provision-pubsub-and-sink.sh to create them." >&2
  exit 1
fi

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

log "Granting the service account the Pub/Sub data-collection role on the existing subscription"
gcloud pubsub subscriptions add-iam-policy-binding "$SUBSCRIPTION_NAME" \
  --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
  --role="projects/$PROJECT_ID/roles/$PUBSUB_ROLE_ID" \
  --project="$PROJECT_ID"

log "Granting the service account the hydration role at the project level"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
  --role="projects/$PROJECT_ID/roles/$HYDRATION_ROLE_ID"

log "Done. GCP identity and permissions for the UCC connector are configured."
