# Frends iPaaS Audit Logs — Microsoft Sentinel Data Connector (CCF)

Ingests the [Frends iPaaS](https://frends.com) Tenant **audit trail** (configuration
changes, user actions and system events) into Microsoft Sentinel using the
**Codeless Connector Framework (CCF)** — fully SaaS, no Function Apps or Logic
Apps to maintain.

| | |
|---|---|
| **Solution** | Frends iPaaS Audit Logs |
| **Support** | KanenasCS — konstantinos_lianos@hotmail.com |
| **Version** | 1.0.0 |
| **Table** | `FrendsAuditLogs_CL` (Analytics plan, 365-day retention) |
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
│ (Entra-protected)    │  5-min     │  OAuth2 client credentials  │
└──────────────────────┘  windows   └──────────────┬──────────────┘
                                                   ▼
                                       DCE ─► DCR (transformKql)
                                                   ▼
                                          FrendsAuditLogs_CL
```

The poller queries in 5-minute windows (`startDateTimeUtc`/`endDateTimeUtc`,
`PageSize=200`). The DCR transform maps the raw entry
(`actionName`, `userName`, `timestamp`, `parameters`) to the table columns and
guarantees `TimeGenerated` is never null.

## Prerequisites

1. **Frends Platform API enabled** for your Tenant (via Frends Support),
   including registration of the Entra **Application ID URI** (audience) and
   the **IP allowlist** — see [Whitelisting Microsoft Sentinel](#whitelisting-microsoft-sentinel-with-frends).
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
     contains `"roles": ["Administrator"]` (decode at the JWT payload —
     it is plain base64).
4. Microsoft Sentinel enabled on the target Log Analytics workspace, and
   Contributor (or equivalent) rights on its resource group to deploy the ARM.

## Deployment

1. Azure Portal ➜ **Deploy a custom template** ➜ *Build your own template in
   the editor* ➜ paste `FrendsAuditLogs_Sentinel_CCF.json`.
2. Deploy into the **resource group of the Sentinel workspace**. Parameters:
   - `workspaceName` — the Log Analytics / Sentinel workspace name.
   - `location` — workspace region (default `westeurope`).
3. Deployment creates the table, DCE (`dce-frendsauditlogs`),
   DCR (`dcr-frendsauditlogs`) and registers the connector in the gallery.
   **No credentials are part of the ARM deployment.**

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
3. **Connect**. First events should appear within ~10–15 minutes:

```kusto
FrendsAuditLogs_CL
| sort by TimeGenerated desc
| take 50
```

## Whitelisting Microsoft Sentinel with Frends

The Frends Platform API enforces an **IP allowlist** (submitted to Frends
Support at enablement). The CCF poller runs on Microsoft-managed
infrastructure, so your office/agent IPs will not cover it — an unlisted
poller receives **403** on every call and the connector ingests nothing while
showing "Connected".

The poller's egress addresses are published by Microsoft under the **`Scuba`
service tag** (the CCF polling service). Three options, in order of preference:

### Option A — whitelist the Scuba service tag ranges (recommended)

Extract the CIDR ranges for your workspace region and send them to Frends
Support as the allowlist:

```bash
# Azure CLI — replace westeurope with your workspace region
az network list-service-tags --location westeurope \
  --query "values[?name=='Scuba'].properties.addressPrefixes" -o json
```

```powershell
# PowerShell
$tags = Get-AzNetworkServiceTag -Location westeurope
($tags.Values | Where-Object { $_.Name -eq 'Scuba' }).Properties.AddressPrefixes
```

If the tag is not exposed in your subscription's API results, download the
weekly **"Azure IP Ranges and Service Tags – Public Cloud"** JSON from the
Microsoft Download Center and take the `Scuba` (or `Scuba.<Region>`) entry.

Caveats to state in the Frends Support ticket:
- Ranges are **updated weekly**; request the allowlist be reviewed when
  ingestion stops with 403s, or provide the whole (region-independent) `Scuba`
  tag to reduce churn.
- Ask whether Frends can accept a **subnet-mask formatted** list — their
  enablement JSON uses `{ "address": "x.x.x.x", "mask": "255.255.255.0" }`
  entries, so CIDR prefixes may need conversion.

### Option B — static-egress relay (exact single IP)

If Frends requires a small, fixed set of IPs, place a relay with a static
public IP between Sentinel and Frends and whitelist only that:

- **Azure API Management** (has a fixed public VIP) or an **Azure
  Function/Container App behind a NAT Gateway** with a static Public IP.
- The relay forwards `GET /api/v1/audit-log` (and the query string) to
  `https://<tenant>.frendsapp.com`, passing the `Authorization` header
  through unchanged.
- Point the connector's `apiEndpoint` at the relay instead of
  `frendsapp.com`. One IP to whitelist, never changes.

Trade-off: reintroduces a component to run and patch — the thing CCF exists
to avoid. Choose only if Option A is rejected.

### Option C — push from inside Frends (no Sentinel whitelisting at all)

Run a **scheduled Frends process on your own Agents** that calls the local
`/api/v1/audit-log` and pushes results to the workspace **Logs Ingestion API**
(DCE + DCR, Entra app with *Monitoring Metrics Publisher* on the DCR). The
Frends Agent IPs are already on the allowlist, so nothing new is exposed.
This replaces the RestApiPoller entirely (keep the same table/DCR); the
connector page then serves only as documentation.

### Verifying after whitelisting

```kusto
// Ingestion heartbeat — run after 30+ minutes connected
FrendsAuditLogs_CL
| summarize LastEvent = max(TimeGenerated), Count = count()
```

Zero rows with a "Connected" status usually means the poller is being 403'd
(allowlist) or the response path is off — see Troubleshooting.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Token endpoint 200, API 403 | Token has no `roles` claim | App role + admin consent (Prerequisite 3) |
| API 403 with valid roles | Caller IP not on Frends allowlist | Section above |
| API 403 with valid roles + IP | Audience mismatch | Scope must be `<Application ID URI>/.default` exactly as registered with Frends Support |
| Audit endpoint 404 / absent from swagger | `EnableFrendsApiAuditLogRoute` not set | Frends Support ticket |
| Connected but zero ingestion | Events JSON path or schema drift | Confirm response wraps entries in `items[]`; check for renamed/extra fields vs. the 4 mapped ones |
| Duplicates near window edges | Overlapping windows | Dedupe in analytics: `summarize arg_max(TimeGenerated, *) by ActionName, UserName, EventTimestampUtc` |

## Schema — FrendsAuditLogs_CL

| Column | Type | Source |
|---|---|---|
| `TimeGenerated` | datetime | `timestamp` (fallback `now()` — never null) |
| `ActionName` | string | `actionName`, `{Controller}.{Action}` format |
| `UserName` | string | `userName` |
| `EventTimestampUtc` | datetime | `timestamp` (original event time) |
| `Parameters` | dynamic | `parameters` (HTTP request parameter data) |

Schema is derived from the documented API contract. The Frends docs mark the
entry shape as "typical" and mention affected-resource and Agent Group data —
when the first live payload is available, diff it against these five columns
and extend table + DCR stream + transform accordingly.

## Notes

- Frends retains audit data upstream for ~60 days; Sentinel retention for the
  table is set to 365 days.
- No pager is configured: `PageSize=200` per 5-minute window. Audit actions
  are low-volume human/config events; revisit only if a window ever exceeds
  200 entries (`totalCount` in the response tells you).
- `solutionIcon` is empty — supply a hosted Frends SVG URL before gallery
  publishing.
- Rotate any client secret that has appeared in screenshots or tickets.
