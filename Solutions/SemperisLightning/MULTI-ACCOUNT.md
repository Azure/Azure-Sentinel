# Multi-account setup (Semperis Lightning CCF)

One workspace. Many Semperis tenants. Each row must say which tenant it came from.

## The mechanism

CCF merges `addOnAttributes` into every polled event. The DCR then treats them as
normal input fields. Three things must line up or the value is silently dropped:

1. Poller sets `addOnAttributes`.
2. DCR `streamDeclarations` declares the column.
3. DCR `transformKql` projects the column.

Miss any one and the column lands empty. Nothing errors.

## Shipped precedent

| Connector | Discriminator | Source |
|---|---|---|
| Auth0 | `Auth0Domain` | `addOnAttributes` |
| Citrix DaaS | `CitrixCustomerId` | `addOnAttributes` |
| SailPoint IdentityNow | `Org`, `Pod`, `Stack` | API response |

Auth0 is the proof. `Solutions/Auth0/Data Connectors/Auth0_CCP/PollingConfig.json`
sets `"Auth0Domain": "[[parameters('domain')]"`. The DCR declares and projects it.
The Auth0 API never returns that field.

Note the Auth0 transform projects `TenantName` and `Auth0Domain` side by side.
`TenantName` comes from the API's `tenant_name`. `Auth0Domain` comes from
`addOnAttributes`. Same row, two different sources.

SailPoint does not need this. Its API returns `org`, `pod` and `stack` already.
Semperis has no such field, so Semperis must use the Auth0 route.

## What this solution does

Poller — `SemperisLightning_PollerConfig.json`:

```json
"addOnAttributes": {
  "SemperisInstanceName": "[[parameters('connectionName')]",
  "SemperisZone": "[[parameters('zone')[0]]",
  "SemperisDataStream": "Tier0Nodes"
}
```

DCR — `SemperisLightning_DCR.json`, every one of the 7 streams:

```
... SemperisInstanceName=tostring(SemperisInstanceName),
    SemperisZone=tostring(SemperisZone),
    SemperisDataStream=tostring(SemperisDataStream)
```

All 7 destination tables declare the 3 columns.

## V2 table names (4.0.0)

All 7 tables now end in `V2_CL`:

| Legacy (Function App keeps writing these) | This solution writes |
|---|---|
| `LightningTier0Nodes_CL` | `LightningTier0NodesV2_CL` |
| `LightningAttackPaths_CL` | `LightningAttackPathsV2_CL` |
| `LightningAttackPathLinks_CL` | `LightningAttackPathLinksV2_CL` |
| `LightningTier0Attackers_CL` | `LightningTier0AttackersV2_CL` |
| `LightningIndicatorExecutions_CL` | `LightningIndicatorExecutionsV2_CL` |
| `LightningIOEsMetadata_CL` | `LightningIOEsMetadataV2_CL` |
| `LightningIOEResults_CL` | `LightningIOEResultsV2_CL` |

Why: zero overlap with the legacy `SemperisLightning` Function App solution, which
still writes the v1 tables. Both can run in one workspace with no schema
interaction. Form matches the shipped SailPoint convention
(`SailPointIDN_EventsV2_CL`).

The `ConnectorName` column is gone. It only existed to satisfy the Log Analytics
additive-only rule against tables a prior 3.1.0 deploy had created, and it just
duplicated `SemperisInstanceName`. V2 tables are new, so there is no constraint and
no legacy consumer. Use `SemperisInstanceName`.

`tests/baselines/published_table_schemas.json` is re-based to the V2 schemas, not
deleted, so once 4.0.0 ships a later column drop or retype is still caught.

## The `[[` escape

Use `[[parameters('x')]`. Two opening brackets.

One bracket resolves at solution-install time. The value would be fixed for every
connection. Two brackets defer to connection-creation time, so each connection
gets its own value.

`tests/test_candidate.py::test_multi_account_attributes_reach_ingested_rows`
enforces all of this.

## Operational notes

The DCR is shared. CCF deploys one DCR per connector definition. Every connection
reuses it. Per-connection DCRs are not part of the model. This is why
`addOnAttributes` exists.

This solution runs 6 pollers per connection. So one connection creates 6
`dataConnectors` resources, and the grid shows 6 rows for it. The **Data Stream**
column separates them. `DeleteConnector` removes one row only, so removing a
tenant means deleting all 6.

## Querying

```kusto
LightningTier0NodesV2_CL
| summarize Nodes = count() by SemperisInstanceName, SemperisZone
```

Scope any detection to one tenant:

```kusto
LightningAttackPathsV2_CL
| where SemperisInstanceName == "contoso-prod"
```

## Open

Auth is unresolved. See `docs/call-brief-2026-08-10.md`. The token endpoint takes a
single `apiKey` field. CCF `JwtToken` models a `userName`/`password` pair. The
current config pads with `ccfCompatibility`, which is invented and unverified.
Semperis must confirm the accepted shape before this is real.

`addOnAttributes` is also undocumented on Microsoft Learn. The behaviour above is
taken from shipped connectors, not from a spec.

Documented `JwtToken` limitations say it requires username/password token
acquisition and does not support API-key token requests, so the invented
`ccfCompatibility` field has no documented basis. Two alternatives to raise with
Semperis, neither applied here:

- `APIKey` auth with `IsApiKeyInPostPayload`, if the polling endpoints accept the
  API key directly and no JWT exchange is needed.
- `OAuth2` client credentials, if the token service supports it.

Source: learn.microsoft.com/azure/sentinel/data-connector-connection-rules-reference#authentication-configuration

## Upgrading from 3.1.1

Poller resource names are unchanged (`SemperisLightning<Stream>-<uniqueString>`),
so installing 4.0.0 over an existing 3.1.1 connection updates those six pollers
in place and repoints them at the V2 tables. The v1 tables are left behind with
their existing data; the Function App keeps writing them. Nothing is deleted.

A DCR transform that projects a column the destination table does not declare is
**silently discarded** — accepted without error, billed, not stored. That is why
`test_every_transform_output_column_exists_in_its_destination_table` exists.
Source: learn.microsoft.com/azure/azure-monitor/data-collection/data-collection-transformations-create
