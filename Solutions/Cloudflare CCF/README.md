# Cloudflare CCF table schema

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
- Timestamp fields retained as strings use the source's configured Logpush output
  format. Duration units vary: for example, `ClientTcpRtt` is in nanoseconds,
  `ClientTCPRTTMs` is in milliseconds, and `WorkerCPUTime` is in microseconds.
- Existing names, types, column order, and transforms are unchanged by descriptions.
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
