# GCP Unified Connector onboarding

[Overview](../README.md) | [AWS onboarding](../AWS/README.md)

These Bash scripts configure Workload Identity Federation, a service account,
custom collection roles, and IAM bindings. Complete the Defender connector setup
after running the selected script.

## Scripts

| Script | Use when |
| --- | --- |
| [provision-pubsub-and-sink.sh](provision-pubsub-and-sink.sh) | A new topic, subscription, and audit-log sink are required |
| [existing-pubsub-and-sink.sh](existing-pubsub-and-sink.sh) | The topic, subscription, sink, and sink-writer publish permission already exist and are correctly wired |

Both scripts can update existing pools, providers, service accounts, and custom
roles. They are not create-only, transactional, or safe dry runs.

## Prerequisites

- Bash and an authenticated Google Cloud CLI (`gcloud`), such as Google Cloud
  Shell.
- An approved provisioning identity with permission to enable the required
  APIs, create/update WIF resources, service accounts and custom roles, and
  read/update the affected project, service-account, and subscription IAM
  policies. The new-resource script also needs topic/subscription creation, topic IAM,
  `pubsub.topics.attachSubscription`, and `logging.sinks.create`. Its reuse
  preflight requires `pubsub.topics.list`, `pubsub.subscriptions.list`,
  `logging.sinks.list`, `pubsub.subscriptions.get`, and `logging.sinks.get`.
  The existing-resource variant requires `pubsub.subscriptions.get` and
  `pubsub.topics.get` to check the subscription and its topic.
- Verify the active account and project before execution:

```bash
gcloud auth list --filter=status:ACTIVE --format='value(account)'
gcloud projects describe '<project-id>' --format='value(projectId,projectNumber)'
```

- Check billing, organization policies, quotas, resource-name collisions, and
  any customer-managed encryption requirements. API enablement and subsequent
  log/messaging usage can incur charges.
- For the existing-resource variant, independently verify topic/subscription
  wiring, sink filter/destination, and writer publish access. The script checks
  that the supplied subscription and its referenced topic are readable. It does
  not discover or validate the logging sink, whose name is not an input.

## Parameters

| Environment variable | Meaning |
| --- | --- |
| `PROJECT_ID` | Customer GCP project ID |
| `PROJECT_NUMBER` | Matching numeric project number |
| `TENANT_ID` | Customer Microsoft Entra tenant UUID |
| `WORKLOAD_IDENTITY_PROVIDER_ID` | Provider ID to create/update inside the derived pool |
| `SERVICE_ACCOUNT_EMAIL` | Service account in the selected project |
| `SUBSCRIPTION_NAME` | Short Pub/Sub subscription name in that project |

The script derives the pool ID by removing hyphens from `TENANT_ID`.
`WORKLOAD_IDENTITY_POOL_ID` is not an input. All six inputs must be set; the
scripts check nonempty values, not project-number correspondence, tenant UUID
format, or email ownership. Verify those yourself. Resource compatibility checks
are described below.

## Configuration steps

1. Download the chosen script from the table above using GitHub's **Download raw
   file** control.
2. Inspect the script and confirm the six parameters.
3. Syntax-check it without provisioning:

```bash
bash -n ./provision-pubsub-and-sink.sh
```

4. After review and authorization, fill in all placeholders and run from the
   directory containing the downloaded script:

```bash
PROJECT_ID='<project-id>' \
PROJECT_NUMBER='<project-number>' \
TENANT_ID='<customer-entra-tenant-id>' \
WORKLOAD_IDENTITY_PROVIDER_ID='<new-or-approved-provider-id>' \
SERVICE_ACCOUNT_EMAIL='<service-account-id>@<project-id>.iam.gserviceaccount.com' \
SUBSCRIPTION_NAME='<subscription-name>' \
bash ./provision-pubsub-and-sink.sh
```

Use `bash ./existing-pubsub-and-sink.sh` instead when reusing an existing
pipeline, with the same six variables. Both scripts change the active `gcloud`
project. They execute changes immediately and offer no preview/rollback mode.

## Resources, APIs, and permissions

Both scripts enable IAM, STS, Cloud Resource Manager, IAM Credentials, Compute,
API Keys, and Pub/Sub APIs. The provisioning variant additionally enables
Logging and Storage APIs.

Both create/update the tenant-derived pool, selected OIDC provider, selected
service account, and these project custom-role definitions:

- `UccPubSubDataCollectionRole`: `pubsub.subscriptions.consume` and
  `pubsub.subscriptions.get`; granted on the selected subscription.
- `UccHydrationDataCollectionRole`: `logging.logEntries.list` and
  `logging.privateLogEntries.list`; granted on the project.

The provisioning variant uses the fixed names `UCC-ControlPlane-Topic` and
`UCC-ControlPlane-Sink`, the supplied subscription name, and the filter
`logName:"cloudaudit.googleapis.com"`. It grants Pub/Sub Publisher to
`cloud-logs@system.gserviceaccount.com` at project scope and to the actual sink
writer on the topic.

## Permissions and resource reuse

The issuer is `https://sts.windows.net/33e01921-4d64-4f8c-a055-5bdaffd5e33d`;
the allowed audience is `api://2041288c-b303-4ca0-9076-9612db3beeb2`.
These identify Microsoft's commercial service, not the customer tenant and not
credentials. This version accepts one audience. Keep these service settings
unchanged.

The service-account Workload Identity User grant covers the entire derived pool,
not just the named provider or a single subject. The provider maps
`google.subject=assertion.sub` without adding an attribute condition. The
customer tenant's pool name alone does not establish token tenant isolation.
Review the trust boundary and any other providers in the pool before granting
access.

Existing provider trust settings and custom-role permissions are updated in
place. Before identity or IAM changes, the provisioning variant checks existing
subscriptions against `projects/PROJECT_ID/topics/UCC-ControlPlane-Topic` and
existing sinks against that topic's Pub/Sub destination and the exact filter
`logName:"cloudaudit.googleapis.com"`. A mismatch stops the script with expected
and actual values; it never repoints, replaces, or deletes these resources.
Choose an unused subscription name or resolve the conflicting configuration
with its owner before rerunning. Different but logically equivalent filter
expressions are not automatically accepted.

The existing-resource variant preserves arbitrary customer topic/sink names.
It checks the subscription and its referenced topic, but sink destination,
filter, and writer publish access still require independent verification.

## Complete connector setup

Use the project ID/number, provider ID, service-account email, and subscription
name in the GCP Pub/Sub Unified Connector setup in the Microsoft Defender portal.
Confirm the intended tenant and new instance before submitting. Verify connector
health and recent source-specific ingestion separately.

## Troubleshooting

The scripts stop on a failed command but leave earlier successful cloud changes
in place, including API enablement before resource preflight. Pub/Sub and sink
read failures stop onboarding instead of being treated as proof of absence.
Other resource helpers retain their existing create/update behavior. Inspect
errors and partial state before rerunning; do not delete or overwrite shared
resources to recover.

## Offline regression checks

From this directory, run `bash tests/resource-reuse.test.sh`. The tests use a
local `gcloud` stub; they do not authenticate, provision, or consume cloud data.
