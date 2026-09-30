# GitHub audit log schema coverage

These notes cover the [REST/CCF connector](GitHubAuditLogs_CCF/) and the
[Azure Storage connector](GitHubAuditLogs_AzStorage/).

## Source contracts

The REST poller requests the Enterprise Cloud endpoint
`GET /enterprises/{enterprise}/audit-log?include=all`. The Storage connector reads
the compressed JSON files produced by GitHub enterprise audit-log streaming.
Neither transport automatically creates new stream or table columns.

The schema expansion is based on the following official sources, captured on
2026-09-10:

- [Enterprise audit-event metadata](https://github.com/github/docs/blob/ec1bf28d8f72ebbe3890eaf841ac3e1616d14565/src/audit-logs/data/ghec/enterprise.json)
  and [organization audit-event metadata](https://github.com/github/docs/blob/ec1bf28d8f72ebbe3890eaf841ac3e1616d14565/src/audit-logs/data/ghec/organization.json):
  985 displayed actions and 491 distinct field names. The generated metadata
  additionally names `new_emu_repo_runners_policy` and
  `old_emu_repo_runners_policy` on an action hidden from the rendered catalog.
- The linked [user security-event metadata](https://github.com/github/docs/blob/ec1bf28d8f72ebbe3890eaf841ac3e1616d14565/src/audit-logs/data/ghec/user.json)
  adds ten previously undeclared names: five displayed and five generated-only.
  The enterprise REST and streaming guides link this catalog for managed-user
  activity. This does not establish that every personal-account action can
  occur in an Enterprise Managed Users enterprise.
- [Enterprise REST audit-log schema](https://github.com/github/rest-api-description/blob/2273ec035b7e1e682066b8b8cc819406bea5dfb7/descriptions/ghec/ghec.2022-11-28.json#L142197-L142361):
  43 top-level properties, without an action-specific, closed schema.
- [Enterprise audit-log streaming](https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/streaming-the-audit-log-for-your-enterprise)
  and the separately documented
  [Copilot usage record format](https://github.com/github/docs/blob/ec1bf28d8f72ebbe3890eaf841ac3e1616d14565/content/copilot/reference/enterprise-administrators/agentic-audit-log-events.md).

`oauth_application_name` is documented for `org.oauth_app_access_approved`,
`org.oauth_app_access_denied`, and `org.oauth_app_access_requested`, despite not
being enumerated in the generic REST schema. It is exposed as
`OauthApplicationName` in both destination tables.
The user security catalog also lists this property on OAuth access and
authorization events.

This is coverage of the cited field inventories, not a guarantee of every
runtime GitHub property. Most catalog entries specify field names but not JSON
types. Fields are optional and depend on the action, enterprise configuration,
and enabled GitHub features.

## Output compatibility and field allocation

Existing output columns retain their names and types. The tables are
`GitHubAuditLogsV2_CL` for REST/CCF and `GitHubAuditLogsV3_CL` for Storage. The V2
table definition belongs only to `GitHubAuditLogs_CCF`; `GitHubAuditLogs_AzStorage`
contains only the V3 table definition used by its DCR.

The expansion adds 291 input fields to REST and 289 to Storage. The difference
accounts for the existing transport-specific schemas, streaming-only events,
the managed-user catalog, seven generated-only field names across the catalogs,
and the optional Copilot record format.

| Connector | Input fields | Output columns |
| --- | ---: | ---: |
| REST | 523 | 481 |
| Azure Storage | 531 | 489 |

The allocation is intentional:

- `OauthApplicationName`, `ActorIsAgent`, and `AgentSessionId` are named columns.
  New fields already represented by the other connector reuse its output names.
- Other new columns retain GitHub's native `snake_case` names. Most use
  `dynamic`, because the catalogs do not provide a JSON type contract. This
  preserves objects, arrays, numbers, booleans, and strings without guessing
  their shape. Use an explicit conversion such as `tostring()` when querying a
  scalar from these columns.
- Forty-five event-specific properties are retained under `AdditionalFields`
  using their original GitHub names. They cover billing details, audit-stream
  destination changes, managed-user security details, marketplace-plan
  metadata, four long security-configuration names, and `title`.

Keeping every property as another PascalCase column would exceed the
[Azure Monitor limits](https://learn.microsoft.com/azure/azure-monitor/fundamentals/service-limits)
of 500 table columns and 15,360 transformation characters. Native names avoid
repeating every new field name in the transformation. The explicit property bag
keeps the output table below the column limit and accommodates reserved or
overlength new column names.

`AdditionalFields` is **not** an automatic catch-all for undeclared source
properties. Its keys are explicitly declared and packed by the DCR:

```text
budget_limit_type, bullets, customer_id, exclude_cost_center_usage, expires_at,
gist, gist_id, has_free_trial, marketplace_listing_plan, monthly_price_in_cents,
new_azure_blob_container, new_event_hub_instance, new_gc_bucket,
new_s3_arn_role, new_s3_bucket, new_splunk_domain, new_splunk_port,
nickname,
old_azure_blob_container, old_budget_limit_type, old_event_hub_instance,
old_expires_at, old_gc_bucket, old_pricing_target_id, old_pricing_target_type,
old_s3_arn_role, old_s3_bucket, old_splunk_domain, old_splunk_port,
old_target_amount, old_target_id, old_target_type,
passkey_nickname, pat_field_changed,
pricing_target_id, pricing_target_type,
security_configuration_code_scanning_delegated_alert_dismissal,
security_configuration_dependabot_delegated_alert_dismissal,
security_configuration_secret_scanning_delegated_alert_dismissal,
security_configuration_secret_scanning_extended_metadata,
target_amount, target_id, target_type, title, yearly_price_in_cents
```

The transformation suppresses the bag only when every packed value is null.
Its anchored null-only JSON pattern avoids storing a large, empty key list on
unrelated events. Empty strings, zero, false, empty arrays, and empty objects are
not suppressed. The pattern applies to the known lowercase letter/digit/underscore
keys above; revisit it if that key alphabet changes.
The null branch uses `parse_json('null')`, following the
[transformation guidance for dynamic literals](https://learn.microsoft.com/azure/azure-monitor/data-collection/data-collection-transformations-kql#dynamic-literals).
General Kusto syntax checks and ARM preflight do not establish compatibility
with the ingestion transformation compiler.

## Other ingestion corrections

- `ActorLocation` retains the complete `actor_location` value, including the
  REST-documented `country_name`. `CountryCode` retains its existing extraction.
- Both `public_repo` and `repository_public` are accepted. Their original values
  are exposed as `public_repo` and `RepositoryPublic`. `PublicRepo` prefers the
  connector's previously used property and falls back only when that value is
  null, preserving an explicit `false` and both original values if they differ.
- REST `data`, `config`, `config_was`, `events`, and `events_were` now enter the
  DCR as `dynamic`, matching the documented object/array shapes. Explicit
  `tostring()` projections preserve their existing string output columns.

## Transport and rollout boundaries

`include=all` includes web and Git audit events; it does not enable
streaming-only `api.request` records. `request_body` and `rate_limit_remaining`
remain Storage-only. Do not confuse `request_body` with `api_request_body`:
the latter is documented for `external_group.scim_api_failure`. Other HTTP
metadata also occurs on that event and is therefore included in REST.

Storage also accepts `body`, `endpoint`, `enterprise_id`, `event_id`,
`github_request_id`, and `truncated` from the optional Copilot usage record
format. These records require GitHub's separate Copilot usage streaming setting;
the connector does not enable that feature. `body` remains a JSON-encoded string.
These fields are not added to the ordinary audit-log REST poller.

Azure Monitor's ingestion-size limits still apply. In particular, field values
larger than 64 KB are truncated; accepting the optional Copilot `body` property
does not guarantee retention of the full, potentially much larger GitHub record.
Retaining more populated properties can also increase ingestion volume.

Apply the destination table schema before its DCR update. Updating source files
does not update an installed Content Hub package or an existing workspace's DCR.
Previously discarded values are not retroactively reconstructed.

The `GitHubAuditData` parser, outside these connector directories, has its own
explicit projection. Query the destination tables directly for these additional
fields unless that parser is separately extended.

For subsequent schema updates, update the input declaration, the transformation,
and the connector's destination table together. Recheck
case-sensitive field names, JSON types, exact projected output types, column
counts, and transformation length. A property added only to a table still will
not be ingested.

## Azure Storage Event Grid setup

Leave the existing-topic name empty to create a system topic with a
system-assigned identity. Supply an existing topic name to enable its
system-assigned identity in place. The connector reads the existing topic first
and preserves its tags, attached user-assigned identities, and any already
enabled system-assigned principal.

Choose **Create** to deploy Storage Queue Data Message Sender at the destination
storage-account scope, or **Use existing** when the topic's current
system-assigned identity already has that permission. Use Create for a new
topic or a newly enabled system-assigned identity. The generated event
subscription is always created or updated with
system-assigned delivery and the connector's filters. It waits for the topic
and notification queue, plus the sender-role deployment when Create is selected.
The existing ScubaSentinelToStorageProd collector application
(`4f05ce56-95b6-4612-9d98-a45c8cc33f9f`) and its three Sentinel service-principal
grants remain unchanged; those grants retain their legacy GUIDs.

**RBAC propagation:** If Connect fails with **Managed Identity Authorization Error**, wait about five minutes and retry with the same values. Propagation can take up to ten minutes.

NSP configuration is optional and remains customer-managed; the connector does
not enable it or change its rules or access mode. Existing sender assignments
are not deleted when Use existing is selected.
