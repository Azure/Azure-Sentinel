# Cloudflare CCF combined connector reference

> Reference implementation for partner review. Do not merge, publish, or deploy
> to production solely because local checks pass. Deployment and ingestion tests
> must use the exact generated package being reviewed.

This reference brings together per-account Blob collectors, Microsoft first-party
collector authentication, Event Grid managed-identity delivery, column
descriptions, and ASIM account attribution. Government-cloud enablement is outside
this change.

## Qualification status

The current 3.2.0 candidate is **not yet end-to-end qualified**. Local generator,
schema, and package checks passed, but the live first-party connection test is
blocked by `BLB40011`.

Storage diagnostics showed the connectivity check authenticating as the legacy
application `4f05ce56-95b6-4612-9d98-a45c8cc33f9f`, while the submitted connector
specified `ManagedServicePrincipal` and permissions were assigned to the intended
first-party application `7ae5462d-d9d1-42f6-93ca-198d7b0ca997`. Engineering must
confirm the supported authentication/API contract and rollout requirements.
This observation concerns the connectivity check; it does not establish how a
successfully created first-party collector would authenticate during ingestion.

The managed-identity storage topology, table, and DCR deployed, but no new
Cloudflare test events were ingested and the existing test collectors were not
migrated. Earlier successful tests of the separate legacy reference are not
qualification evidence for this package. Do not mask this blocker by granting
the legacy application access, weakening validation, or treating structural
checks as a successful first-party ingestion test.

## What changes together

| Component | Purpose |
|---|---|
| [Connector definition](Data%20Connectors/CloudflareLog_CCF/CloudflareLog_ConnectorDefinition.json) | Connections grid and nested, multi-step collector inputs, including tenant-local principal, account identity, storage region, and Event Grid permissions. |
| [Poller configuration](Data%20Connectors/CloudflareLog_CCF/CloudflareLog_PollerConfig.json) | Opts into `connectionDeployment.mode: PerInstance`, `ManagedServicePrincipal`, and Event Grid managed identity. Preserves nested account attributes and storage subscription/resource-group context. |
| [DCR](Data%20Connectors/CloudflareLog_CCF/CloudflareLog_DCR.json) | Authoritative input schema and transformation. The per-instance generator supplies configured account attribution, rather than trusting those fields in the blob payload. |
| [Table schema](Data%20Connectors/CloudflareLog_CCF/CloudflareLog_Table.json) | All 498 output columns, including two collector-attribution columns, have descriptions. |
| [Packaging tools](../../Tools/Create-Azure-Sentinel-Solution/) | Generate isolated per-instance resources and the first-party/managed-identity storage topology. These shared changes are part of the reference, not optional files to omit when rebuilding. |
| [Parameterless ASIM parser](../../Parsers/ASimWebSession/Parsers/ASimWebSessionCloudflareOne.yaml) and [filtering ASIM parser](../../Parsers/ASimWebSession/Parsers/vimWebSessionCloudflareOne.yaml) | Preserve configured account identity in `DvcScopeId` and `DvcScope`, with a native `AccountID` fallback for older table schemas. |

### Identity and isolation

- Each immutable account/storage-container/workspace identity gets its own
  connector, notification queue, dead-letter queue, DCR, DCE, and Event Grid
  subscription. Changing only the friendly account label must not create another
  collector.
- Event Grid system topics are shared at storage-account scope. When a topic
  already exists, supply its name and verify that its source is the selected
  storage account.
- The Microsoft first-party collector application ID is
  `7ae5462d-d9d1-42f6-93ca-198d7b0ca997`. Use the enterprise application's
  **object ID in the target tenant**, not the application ID or another tenant's
  object ID, for `principalId`.
- Collector access is Storage Blob Data Reader on the selected container and
  Storage Queue Data Contributor on its queues. Event Grid's topic identity
  separately needs Storage Queue Data Message Sender on the storage account.
- `UseExistingRoleAssignment` applies only to the Event Grid sender grant. It
  does not waive the collector's required permissions.
- Cloudflare Logpush's ability to write blobs is a third, separate permission
  boundary. First-party collector authentication does not configure Logpush.
- Avoid overlapping collectors over the same blob objects. Different configured
  account identities do not deduplicate a source exported to multiple collectors.

## Partner workflow

1. Check out the complete reference PR, including its shared packaging-tool
   changes. Review it against the current supported connector, not only against
   the older generated ZIP.
2. Review the account identity, folder selection, permissions, and table
   descriptions against the Cloudflare datasets you support. Keep the literal
   connector definition ID `CloudflareDefinition`.
3. Run the shared storage-generator regression tests, then rebuild and validate
   using the repository's documented runner. To reproduce the version already
   recorded in the source without bumping it again:

   ```powershell
   pwsh -NoProfile -File .script/local-validation/build-and-validate.ps1 `
     -SolutionName "Cloudflare CCF" -VersionBump none `
     -ReleaseNotes "Combined Cloudflare multi-account, identity, and schema reference"
   ```

   Treat skipped checks and failures explicitly. Do not change validators or
   manually patch the generated ZIP to make a check pass.
4. Record the package SHA-256, source commit, and embedded version. After explicit
   approval for a non-production workspace, install that same package and add two
   collectors using separate storage containers. Check the actual storage-account
   region rather than assuming it matches the resource group's location.
5. Test both fresh creation and repeat connection with unchanged identity values.
   Exercise an existing Event Grid topic and both sender-assignment modes when
   applicable. A deployment that passes ARM validation alone is not sufficient.
6. Generate the synthetic data described below, upload through Blob Storage, and
   let CCF consume the events. Do not substitute direct Logs Ingestion API writes
   for a connector test.
7. Verify source and normalized row counts, per-account attribution, queue health,
   DCR diagnostics, and absence of unexpected resource recreation. Keep the
   evidence tied to the final package hash.
8. Only after review and qualification should Cloudflare prepare its own
   submission/publication. This reference PR is not a request to merge or publish
   an unreviewed partner release.

### Synthetic data and coverage

[New-CloudflareReferenceData.ps1](Samples/New-CloudflareReferenceData.ps1) is an
offline generator; it does not access Azure or require credentials:

```powershell
pwsh -NoProfile -File "Solutions/Cloudflare CCF/Samples/New-CloudflareReferenceData.ps1" `
  -OutputDirectory "<local-evidence-directory>" -RunId "<unique-test-run>"
```

It creates two gzip-compressed NDJSON files and a manifest: **24 records per
account, 48 total**, with six records from each of `http_requests`, `gateway_http`,
`firewall_events`, and `sinkhole_http_logs`. It uses documentation IP ranges,
example domains, and a sanitized email. Multiple event times, status codes, user agents, and source IPs allow more
meaningful filter tests than a single successful HTTP case.
The payload intentionally omits `CloudflareAccountId` and `CloudflareAccountName`;
verify that the per-instance DCR supplies the configured values.

The ASIM pair covers these four **WebSession** event families, not every dataset
represented in the broad table. The global ASIM YAML files are separate from the
solution's existing `Cloudflare()` compatibility parser; rebuilding the solution
package does not, by itself, install the updated global ASIM functions. Deploy or
invoke the reviewed ASIM source explicitly when qualifying normalization. An
inline test-only table binding is useful for an isolated lab, but is not evidence
that a saved or built-in function has been updated.

Record generic filter-test failures caused by insufficient data rather than
silently treating them as a complete pass. For Sinkhole events, multiple requests
can share a `SinkholeID`; use normalized `EventUid` and request context when
checking row preservation, not an assumption that every `EventOriginalUid` is
unique.

### Cleanup and rollout

Do not remove shared tables or system topics while another collector uses them.
Deleting a connector alone does not remove its supporting resources. Inventory
the exact resources and role assignments created for each instance, and remove
temporary test-uploader grants separately from collector grants.

A legacy collector rollout must account for existing role assignments. Azure
does not allow replacing a role under an existing assignment GUID. Review legacy
compatibility and any intentional permission migration before reconnecting
existing customers; an empty-lab deployment cannot prove upgrade safety.

## Table schema

The connector's authoritative output schema is
[CloudflareLog_Table.json](Data%20Connectors/CloudflareLog_CCF/CloudflareLog_Table.json).
Each column has a `description` alongside its existing `name` and `type`, following
the table-metadata pattern used by the BigID CCF connector. These descriptions are
table metadata, not DCR input-stream fields or connector UI instructions. Repackage
and deploy the updated solution to apply them; editing the source does not update
an installed workspace.

## Interpreting the columns

`CloudflareV2_CL` combines fields from multiple Cloudflare Logpush datasets. A field
is populated only when the source dataset supplies it, and shared field names can
have dataset-specific meanings. The descriptions explain those differences where
applicable; they do not imply that every field is present in every event.

- `TimeGenerated` is assigned by the ingestion transform using `now()`. It is not
  the original event timestamp.
- `NELType` is the source `Type` field renamed by the transform. It can contain a
  Network Error Logging error type or another dataset's `Type` value, such as a
  browser-isolation action.
- `CloudflareAccountId` and `CloudflareAccountName` are configured collector
  attribution, independent of the native `AccountID` field. ASIM exposes them as
  device scope ID/name so normalization does not lose account context.
- Timestamp fields retained as strings use the source's configured Logpush output
  format. Duration units vary: for example, `ClientTcpRtt` is in nanoseconds,
  `ClientTCPRTTMs` is in milliseconds, and `WorkerCPUTime` is in microseconds.
- Descriptions do not change field types or source semantics. The two
  collector-attribution fields are the deliberate schema/transform additions.
  In particular, the integer `Status` column does not represent textual status
  values emitted by some other datasets. Metadata is not a schema-conversion fix.

## Description sources and attribution

Field descriptions are adapted from
[Cloudflare's Logpush dataset documentation](https://developers.cloudflare.com/logs/logpush/logpush-job/datasets/),
by Cloudflare and its documentation contributors, under
[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).
The [Cloudflare Docs license](https://github.com/cloudflare/cloudflare-docs/blob/a1853c1650eb48166054c2f8f48dc8eb4da56eb8/LICENSE)
applies to the adapted field-description material.

Changes include plain-text formatting, shorter descriptions, reconciliation of
shared names across datasets, removal of misleading examples, and explanations of
the connector-derived fields. Sources were checked on 13 November 2026 using the
[dataset archive consumed by Cloudflare Docs](https://middlecache.ced.cloudflare.com/v1/logpush-datasets/datasets.tar.gz)
(SHA-256 `46285659e77379715398de2e13f2882112985e0ec03c93aa4f315c8bdc3e66a1`).
