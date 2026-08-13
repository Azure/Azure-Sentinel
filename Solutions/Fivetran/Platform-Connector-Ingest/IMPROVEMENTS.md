# Improvements in this reference build

This connector is a hardened, fully-IaC evolution of a first-generation
"Platform Connector to Sentinel" build. Each improvement below is a concrete change you
can see in the files, with the reason it matters.

## 1. Flex Consumption hosting (removes the packaging gotcha)

- **Before:** Linux Consumption (Y1). A Python function with a compiled dependency
  (`pyarrow`) had to be published with a remote build, and a run-from-package mismatch
  could leave the app showing "zero functions" with no clear error.
- **Now:** **Flex Consumption**. Flex builds Python dependencies remotely as part of the
  platform deployment flow, so `pyarrow` and friends resolve without the run-from-package
  workaround. Deploy with `az functionapp create --flexconsumption-location <region>`.
- **Why it matters:** removes the single most common first-deploy failure for a
  parquet-reading Python function.

## 2. User-assigned managed identity (removes the RBAC chicken-and-egg)

- **Before:** system-assigned identity. It does not exist until the app is created, so
  the `Storage Blob Data Reader` and `Monitoring Metrics Publisher` grants could only be
  made after first deploy, and were lost if the app was recreated.
- **Now:** a **user-assigned managed identity** created first. You pre-grant both roles
  to a stable principal, then attach it to the app. The `sentinel-tables-dcr.bicep`
  `functionPrincipalId` parameter grants Monitoring Metrics Publisher on the DCR at
  deploy time, so the role is in place before the first event. Set `AZURE_CLIENT_ID` so
  `DefaultAzureCredential` selects the identity.
- **Why it matters:** RBAC survives app recreation and there is no ordering trap.

## 3. Event Grid hardening (reliability + cost + no shared secret)

- **Before:** a webhook subscription that embedded the function system key in the
  endpoint URL, with no dead-letter and coarse filtering.
- **Now:**
  - **`azurefunction` endpoint type** so Event Grid manages the handshake and the
    function key is not pasted into a URL you have to rotate by hand.
  - **Dead-letter destination** on a storage container, so events are never silently
    lost if the function is briefly unavailable.
  - **Retry policy** (max delivery attempts + event TTL) made explicit.
  - **Tight subject filter** (`subject-begins-with` the lake root, `subject-ends-with
    .parquet`) so `_delta_log` checkpoint parquet and Iceberg metadata never invoke the
    function, cutting invocation cost and noise. The function still re-checks
    `/<table>/data/*.parquet` as defence in depth.
- **Why it matters:** at-least-once delivery is real, cheaper, and has no long-lived
  secret in a URL.

## 4. Reference table on Analytics with tuned retention (not Basic/Auxiliary)

- **Consideration:** it is tempting to put the high-volume reference table on the Basic
  or Auxiliary plan to cut cost.
- **Decision:** keep `Fivetran_Platform_CL` on the **Analytics** plan. Basic and
  Auxiliary plans restrict cross-table joins, and the entire purpose of these
  reference/dimension tables is to be **joined** for enrichment (for example resolving a
  `user_id` to an email). Instead, control cost with a **shorter interactive retention**
  (`referenceRetentionInDays`, default 90 days) because dimension data changes rarely.
- **Why it matters:** a Basic/Auxiliary "saving" would break the enrichment use case the
  table exists for.

## 5. Security hardening on the function app

Applied in the deploy guide:
- HTTPS only, minimum TLS 1.2.
- SCM and FTP **basic auth disabled** (managed-identity / OIDC publishing only).
- No storage account keys in app settings for data access; the Logs Ingestion and blob
  reads both use the managed identity.

## 6. Portability and safety

- Every environment-specific value is a `<placeholder>`; there are no customer names,
  resource ids, subscription ids, or lake paths anywhere in this folder.
- The two custom tables are registered in
  `.script/tests/KqlvalidationsTests/CustomTables/` so the shipped parsers and hunting
  query validate in CI against a known schema.

## Unchanged on purpose

- The **at-least-once + dedupe-by-id** design. Delta/Iceberg compaction re-emits rows;
  the ASIM parser dedupes with `arg_max(TimeGenerated, *) by id`. This is correct and is
  kept as-is.
- The **two-tables-one-DCR** split (typed audit vs generic reference envelope).
- The parser logic and ASIM AuditEvent mapping.
