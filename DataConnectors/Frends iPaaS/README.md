# Frends iPaaS Audit Logs — Microsoft Sentinel Data Connector (CCF)

Ingests the [Frends iPaaS](https://frends.com) Tenant **audit trail** (configuration
changes, user actions and system events such as process builds and deployments)
into Microsoft Sentinel using the **Codeless Connector Framework (CCF)** — fully
SaaS, no Function Apps or Logic Apps to maintain.

| Field | Value |
|---|---|
| **Solution** | Frends iPaaS Audit Logs |
| **Author** | Konstantinos Lianos |
| **Support** | KanenasCS — Konstantinos_lianos@hotmail.com |
| **Provider** | Microsoft Security Community |
| **Version** | 1.0.1 |
| **Table** | `FrendsAuditLogs_CL` |
| **Source** | Frends Platform API — `GET /api/v1/audit-log` |
| **Auth** | Entra ID OAuth 2.0 client credentials |

## Contents

- `FrendsAuditLogs_Sentinel_CCF.json` — single ARM template: custom table, DCE,
  DCR, content package, connector definition (UI), DataConnector +
  ResourcesDataConnector content templates, metadata.
- `FrendsAuditLogs_CL.json` — table schema reference.

## Architecture

```
Frends Platform API                    Microsoft Sentinel (SaaS)
┌──────────────────────┐   HTTPS    ┌─────────────────────────────┐
│ /api/v1/audit-log    │◄───────────│ CCF RestApiPoller ("Scuba") │
│ (Entra-protected)    │  polling   │  OAuth2 client credentials  │
└──────────────────────┘  windows   └──────────────┬──────────────┘
                                                   ▼
                                       DCE ─► DCR (transformKql)
                                                   ▼
                                          FrendsAuditLogs_CL
```

The poller queries in time windows (`startDateTimeUtc`/`endDateTimeUtc`,
`PageSize=200`) and reads entries from the response `data` array
(`eventsJsonPaths: ["$.data[*]"]`). The DCR transform maps the raw entry
(`action`, `user`, `timestampUtc`, `description`, `parameters`) to the table
columns, parses the JSON-serialized `parameters` string into a dynamic object,
and guarantees `TimeGenerated` is never null.

## Prerequisites

1. **Frends Platform API enabled** for your Tenant (via Frends Support),
   including registration of the Entra **Application ID URI** (audience) and,
   if enforced, the **IP allowlist** — see [Whitelisting Microsoft Sentinel](#whitelisting-microsoft-sentinel-with-frends).
2. **Audit Log API route enabled**: ask Frends Support to set
   `Flags:EnableFrendsApiAuditLogRoute = true` for your Tenant. Verify: the
   **AuditLog** section appears in `https://<TENANT>.frendsapp.com/swagger/index.html`.
3. **Entra ID app registration** with:
   - A client secret.
   - An **`Administrator` app role** — App roles ➜ Create app role, allowed
     member type **Applications**, value `Administrator`.
   - The role added under **API permissions** (APIs my organization uses ➜
     select this same app) and **admin consent granted** (green checkmark).
   - ⚠ A token acquired *without* the role still returns HTTP 200 from the
     token endpoint but the Platform API answers **403**. Verify the token
     contains `"roles": ["Administrator"]` (decode the JWT payload — it is
     plain base64).
4. Microsoft Sentinel enabled on the target Log Analytics workspace, and
   Contributor (or equivalent) rights on its resource group to deploy the ARM.

## Deployment

1. Azure Portal ➜ **Deploy a custom template** ➜ *Build your own template in
   the editor* ➜ paste `FrendsAuditLogs_Sentinel_CCF.json`.
2. Deploy into the **resource group of the Sentinel workspace**. Parameters:
   - `workspaceName` — the Log Analytics / Sentinel workspace name.
   - `location` — workspace region.
3. Deployment creates the table, DCE, DCR and registers the connector in the
   gallery. **No credentials are part of the ARM deployment.**

## Connect

1. Sentinel ➜ **Data connectors** ➜ *Frends iPaaS Audit Logs (via Codeless
   Connector Framework)* ➜ **Open connector page**.
2. Fill in:
   - **Entra ID Tenant ID** — Directory (tenant) ID.
   - **Application (client) ID** — the OAuth scope is derived from it as
     `api://<clientId>/.default`. If a *custom* Application ID URI was
     registered with Frends Support, the scope in the connection template must
     be adjusted to match it.
   - **Client Secret**.
   - **Frends Tenant Name** — subdomain only (`contoso` for
     `contoso.frendsapp.com`).
3. **Connect**. Events appear after the next poll cycle, provided the Tenant
   has audit activity in the query window:

```kusto
FrendsAuditLogs_CL
| sort by TimeGenerated desc
| take 50
```

## Whitelisting Microsoft Sentinel with Frends

If the Frends Platform API enforces an **IP allowlist**, the CCF poller runs on
Microsoft-managed infrastructure, so office/agent IPs will not cover it — an
unlisted poller receives **403** on every call and the connector ingests
nothing while showing "Connected".

The poller's egress addresses are published by Microsoft under the **`Scuba`
service tag**. Per Microsoft's guidance for the CCF, network-isolated sources
should allowlist the current Scuba public IP ranges, resolved via the Service
Tag Discovery API.

### Option A — whitelist the Scuba service tag ranges (recommended)

```bash
# Azure CLI — replace <region> with your workspace region
az network list-service-tags --location <region> \
  --query "values[?name=='Scuba'].properties.addressPrefixes[]" -o tsv
```

The `Scuba` tag is published as a single global list (region argument scopes
the API call, not the result). Caveats for the Frends Support ticket:
- Ranges are **updated weekly**; request the allowlist be reviewed if ingestion
  later starts returning 403s.
- Frends' enablement format may expect `{ "address": "x.x.x.x", "mask": "..." }`
  pairs, so CIDR prefixes may need conversion; IPv6 entries may not be accepted.

### Option B — static-egress relay (single fixed IP)

Place a relay with a static public IP (Azure API Management, or a Function /
Container App behind a NAT Gateway) between Sentinel and Frends, forwarding
`GET /api/v1/audit-log` with the `Authorization` header unchanged, and point
the connector's `apiEndpoint` at the relay. One IP to whitelist. Trade-off:
reintroduces a component to run and patch.

### Option C — push from inside Frends (no Sentinel whitelisting)

Run a scheduled Frends process on your own Agents that calls the local
`/api/v1/audit-log` and pushes results to the workspace **Logs Ingestion API**
(DCE + DCR, Entra app with *Monitoring Metrics Publisher* on the DCR). The
Agent IPs are already on the allowlist. This replaces the RestApiPoller while
keeping the same table/DCR.

### Verifying after whitelisting

```kusto
FrendsAuditLogs_CL
| summarize LastEvent = max(TimeGenerated), Count = count()
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Token endpoint 200, API 403 | Token has no `roles` claim | App role + admin consent (Prerequisite 3) |
| API 403 with valid roles | Caller IP not on Frends allowlist | Whitelisting section above |
| API 403 with valid roles + IP | Audience mismatch | Scope must be `<Application ID URI>/.default` exactly as registered with Frends Support |
| Audit endpoint 404 / absent from swagger | `EnableFrendsApiAuditLogRoute` not set | Frends Support ticket |
| Connected but zero ingestion | No audit activity in the window, or response path/schema drift | Confirm the Tenant produced events in range; confirm the response wraps entries in `data[]` and field names match the mapped set |

## Schema — FrendsAuditLogs_CL

| Column | Type | Source |
|---|---|---|
| `TimeGenerated` | datetime | `timestampUtc` (fallback `now()` — never null) |
| `ActionName` | string | `action` — `{Controller}.{Action}` format, e.g. `Process.PostProcessBpmn` |
| `UserName` | string | `user` |
| `EventTimestampUtc` | datetime | `timestampUtc` (original event time) |
| `Description` | string | `description` (additional detail, e.g. operation duration) |
| `Parameters` | dynamic | `parameters` (parsed from JSON-serialized string; the change payload) |

## Notes

- The API returns entries under a `data` envelope; each entry's `parameters`
  field arrives as a JSON-serialized string and is parsed with `todynamic()`.
- The poller uses a 5-minute query window with `PageSize` 200. Audit events
  are low-frequency (human/configuration actions), so a single window is very
  unlikely to exceed the page size; add pagination only if per-window volume
  ever approaches 200. The CCF framework de-duplicates across overlapping windows.
- Frends retains audit data upstream for approximately 60 days.
- `solutionIcon` is empty in the template — supply a hosted Frends SVG URL if
  publishing to the gallery.
- Rotate any client secret that has appeared in screenshots or tickets.
