# Tailscale (CCF)

Microsoft Sentinel solution that ingests Tailscale identity, device, configuration, audit and (Premium) network-flow telemetry via the OAuth2-secured Tailscale API. Built on the Codeless Connector Framework (CCF) - no Function App or container required.

- **2 data connectors** (Standard, Premium) - install whichever matches your Tailscale plan
- **24 analytic rules** (16 Standard + 8 Premium-only)
- **22 hunting queries** (12 Standard + 10 Premium-only)
- **2 workbooks** (Standard Operations, Premium Operations)
- **2 ASIM NetworkSession parsers** (`vimNetworkSessionTailscale` + `ASimNetworkSessionTailscale` wrapper) - Premium only
- **9 custom tables** ingested via 9-11 polling rules behind a single Connect button

---

## Table of contents

1. [Pick your tier](#1-pick-your-tier)
2. [Pre-requisites](#2-pre-requisites)
3. [Installation](#3-installation)
4. [Verification](#4-verification)
5. [Custom tables](#5-custom-tables)
6. [Analytic rules](#6-analytic-rules)
7. [Hunting queries](#7-hunting-queries)
8. [Workbooks](#8-workbooks)
9. [Architecture notes](#9-architecture-notes)
10. [Limitations](#10-limitations)
11. [Troubleshooting](#11-troubleshooting)
12. [Support](#12-support)
13. [Acknowledgements](#13-acknowledgements)

---

## 1. Pick your tier

Install **one** of the two connectors based on your Tailscale plan. The split mirrors what the Tailscale API actually exposes per tier - network flow logs are only available on Premium and Enterprise tailnets.

| | Tailscale Standard (CCF) | Tailscale Premium (CCF) |
|---|---|---|
| **Tailscale plan** | Personal (Free), Starter, Premium\* | Premium, Enterprise |
| **Pollers behind one Connect** | 9 | 11 |
| **Custom tables created** | 7 | 9 |
| **Analytic rules wired** | 16 | 24 (Standard 16 + Premium 8) |
| **Hunting queries wired** | 12 | 22 (Standard 12 + Premium 10) |
| **Workbook** | Standard Operations | Premium Operations |
| **Network flow logs** | not exposed by API | `Tailscale_Network_CL` |
| **Posture integrations** | not exposed by API | `Tailscale_PostureIntegrations_CL` |
| **Required OAuth scopes** | `logs:configuration:read`, `devices:read`, `users:read`, `keys:read`, `webhooks:read`, `dns:read`, `settings:read` | All of Standard plus `logs:network:read`, `posture-integrations:read` |

\* Premium tailnets can use the Standard connector if you don't want network-flow data, but the Premium connector is the recommended path.

---

## 2. Pre-requisites

You need four things before clicking Connect:

1. **A Microsoft Sentinel-enabled Log Analytics workspace** in any region.
2. **A Data Collection Endpoint (DCE)** in the same region as the workspace. The Sentinel Content Hub installer creates one automatically if you don't already have a shared DCE.
3. **A Tailscale OAuth client** generated at <https://login.tailscale.com/admin/settings/oauth>. Personal API tokens (`tskey-api-...`) do **not** work - see [Architecture notes](#9-architecture-notes) for the reason.
   - Tick the scopes listed in the table above for your tier.
   - Copy the **Client ID** and **Client Secret** when prompted - the secret is shown only once.
4. **Your tailnet name** (e.g. `tailb094d7.ts.net`). Find it on the [Keys page](https://login.tailscale.com/admin/settings/keys) or in your Tailscale admin URL.

### OAuth scope checklist

Tick exactly the scopes for your tier - extra scopes don't hurt but the connector won't ask for them, and missing a scope means the corresponding poller will return `200 OK` with no data (Tailscale doesn't error on missing scope, it just returns empty).

**Standard (7 scopes)**

- `logs:configuration:read` - audit log
- `devices:read` - device inventory, including tailnet-lock state, SSH enablement, advertised routes
- `users:read` - user roles and last-seen
- `keys:read` - auth keys and OAuth clients (for sprawl/expiry detection)
- `webhooks:read` - webhook configuration
- `dns:read` - nameservers, MagicDNS, split-DNS, search paths
- `settings:read` - tailnet-wide settings

**Premium adds (2 scopes)**

- `logs:network:read` - network flow logs
- `posture-integrations:read` - device posture integration list and status

---

## 3. Installation

1. Open **Microsoft Sentinel** -> **Content hub**, search for "Tailscale" and install **Tailscale (CCF)**.
2. Go to **Data connectors**, search "Tailscale", and open either **Tailscale Standard (CCF)** or **Tailscale Premium (CCF)**.
3. Supply:
   - **Tailnet name** (e.g. `tailb094d7.ts.net`)
   - **OAuth Client ID**
   - **OAuth Client Secret**
4. Click **Connect**. The connector page shows "Connected" within ~30 seconds; the first audit poll completes within 5 minutes and the first snapshot pollers (devices, users, ...) within 60 minutes.

That single Connect click deploys 9 (Standard) or 11 (Premium) Sentinel `RestApiPoller` data connectors behind the scenes - see [Architecture notes](#9-architecture-notes) for how that works.

---

## 4. Verification

Run these in **Sentinel** -> **Logs** after the first poll cycle completes (~5 min for audit, ~60 min for snapshots).

```kql
// Audit logs received in the last 15 min (should be > 0 if any config activity happened)
Tailscale_Audit_CL
| where TimeGenerated > ago(15m)
| project TimeGenerated, EventTime, Action, Actor, Target

// Snapshot of every tailnet device on the latest poll
Tailscale_Devices_CL
| summarize arg_max(TimeGenerated, *) by DeviceId
| project DeviceName, Hostname, User, Os, ClientVersion, LastSeen, Authorized, ConnectedToControl

// All tables receiving data in the last 2 hours
union 
    (Tailscale_Audit_CL                | extend _T = "Tailscale_Audit_CL"),
    (Tailscale_Devices_CL              | extend _T = "Tailscale_Devices_CL"),
    (Tailscale_Users_CL                | extend _T = "Tailscale_Users_CL"),
    (Tailscale_Keys_CL                 | extend _T = "Tailscale_Keys_CL"),
    (Tailscale_Webhooks_CL             | extend _T = "Tailscale_Webhooks_CL"),
    (Tailscale_Settings_CL             | extend _T = "Tailscale_Settings_CL"),
    (Tailscale_Dns_CL                  | extend _T = "Tailscale_Dns_CL"),
    (Tailscale_Network_CL              | extend _T = "Tailscale_Network_CL"),
    (Tailscale_PostureIntegrations_CL  | extend _T = "Tailscale_PostureIntegrations_CL")
| where TimeGenerated > ago(2h)
| summarize Rows = count(), Latest = max(TimeGenerated) by _T
| order by _T asc
```

A working Standard tier should return rows for 7 tables; Premium should return rows for 9. `Tailscale_Network_CL` and `Tailscale_PostureIntegrations_CL` are Premium-only.

---

## 5. Custom tables

All tables are Log Analytics custom tables (`_CL`) populated via Sentinel CCF poller -> DCE -> DCR transform.

| Table | Cols | Cadence | Source endpoint | Tier |
|---|---|---|---|---|
| `Tailscale_Audit_CL` | 11 | 5 min | `/logging/configuration` | Standard + Premium |
| `Tailscale_Devices_CL` | 27 | 60 min | `/devices?fields=all` | Standard + Premium |
| `Tailscale_Users_CL` | 13 | 60 min | `/users` | Standard + Premium |
| `Tailscale_Keys_CL` | 10 | 60 min | `/keys?all=true` | Standard + Premium |
| `Tailscale_Webhooks_CL` | 8 | 60 min | `/webhooks` | Standard + Premium |
| `Tailscale_Settings_CL` | 9 | 60 min | `/settings` | Standard + Premium |
| `Tailscale_Dns_CL` | 5 | 60 min | merged from `/dns/nameservers`, `/dns/preferences`, `/dns/searchpaths` | Standard + Premium |
| `Tailscale_Network_CL` | 27 | 5 min | `/logging/network` | Premium only |
| `Tailscale_PostureIntegrations_CL` | 8 | 60 min | `/posture/integrations` | Premium only |

**Snapshot semantics.** All `_CL` tables except `Audit` and `Network` are snapshot tables - each poll writes the full current state of the endpoint. Use `summarize arg_max(TimeGenerated, *) by <key>` to get the latest snapshot. The 5-min audit and network tables are append-only event streams.

**`Tailscale_Devices_CL` is the richest snapshot table** at 27 columns. The 5 most interesting columns for detection are surfaced via `?fields=all`:

- `AdvertisedRoutes` / `EnabledRoutes` - dynamic arrays of CIDRs the device offers/has approved
- `SshEnabled` - bool, is Tailscale SSH active on this device
- `ConnectedToControl` / `Authorized` - control-plane state pair (unauthorized + connected = the rule trigger)
- `TailnetLockKey` / `TailnetLockError` - cryptographic node-key validation state
- `UpdateAvailable` - bool, client behind latest release

**`Tailscale_Network_CL` is the richest event table** (Premium only) at 27 columns. The DCR transform promotes the most useful inner-object fields out of the source `srcNode` / `dstNodes` dynamics so hunting queries don't have to traverse dynamic JSON:

- `SrcUser` / `SrcNodeName` / `SrcOs` / `SrcTags` / `SrcAddresses` - src device identity + tagging
- `DstCount` / `DstNodeId` / `DstNodeName` / `DstUser` / `DstOs` / `DstTags` / `DstAddresses` - dst device identity + tagging
- `HasVirtualTraffic` / `HasSubnetTraffic` / `HasExitTraffic` / `HasPhysicalTraffic` - traffic-shape flags
- `IsRelayed` - bool, true when the flow used a DERP relay (detected via `127.3.3.40` in `physicalTraffic`)

---

## 6. Analytic rules

### Standard tier (16 rules)

**Identity & access (5)**

| Rule | Severity | Tactics | What it watches |
|---|---|---|---|
| New API access token or OAuth client created | Medium | Persistence, CredentialAccess | New `API_ACCESS_TOKEN_CREATE` / `OAUTH_CLIENT_CREATE` audit events |
| OAuth client or API key created with write scopes | High | Persistence, PrivilegeEscalation | New OAuth client or API key whose granted scopes include any `:write` permission |
| Auth key created | Low | Persistence | Any new auth key (incl. ephemeral / reusable / preauthorized) |
| User role elevated to admin or owner | High | PrivilegeEscalation, Persistence | `USER_ROLE_UPDATE` audit events targeting `admin` or `owner` |
| Unauthorized device connected to control plane | High | InitialAccess, Persistence | `Authorized=false AND ConnectedToControl=true` in devices snapshot |

**Configuration (3)**

| Rule | Severity | Tactics | What it watches |
|---|---|---|---|
| Policy file (ACL) modified | Medium | DefenseEvasion, Persistence | `ACL_FILE_UPDATE` events |
| Mass credential revocation in short window | High | DefenseEvasion, Impact | More than N delete-key events in a 30-min sliding window |
| External (shared-in) device added | Medium | InitialAccess | New `IsExternal=true` device vs 24-hour baseline |

**Devices (3)**

| Rule | Severity | Tactics | What it watches |
|---|---|---|---|
| Device started advertising subnet routes | Medium | LateralMovement, Persistence | Non-exit-node CIDRs newly appear in `AdvertisedRoutes` |
| Device key expiring within 7 days | Medium | InitialAccess | Devices whose key expiry is within 7 days |
| Device Tailscale SSH newly enabled | Medium | Persistence, LateralMovement | `SshEnabled` transition from false to true vs 24-hour baseline |

**Network & exit (2)**

| Rule | Severity | Tactics | What it watches |
|---|---|---|---|
| Exit node advertised or approved | Low | CommandAndControl, Exfiltration | `0.0.0.0/0` or `::/0` newly appears in `AdvertisedRoutes` / `EnabledRoutes` |
| Tailnet lock validation failed | High | DefenseEvasion, InitialAccess | Non-empty `TailnetLockError` field in devices snapshot |

**DNS (3)**

| Rule | Severity | Tactics | What it watches |
|---|---|---|---|
| DNS nameservers modified | High | DefenseEvasion, CommandAndControl | `DNS_UPDATE` audit events affecting global nameservers |
| MagicDNS disabled | Medium | DefenseEvasion | `MAGICDNS_DISABLE` audit event |
| Split-DNS configuration modified | High | DefenseEvasion, CommandAndControl | `SPLIT_DNS_UPDATE` audit events (per-domain DNS override) |

### Premium tier (additional 8 rules)

These require `Tailscale_Network_CL` (flow logs) or `Tailscale_PostureIntegrations_CL`.

| Rule | Severity | Tactics | What it watches |
|---|---|---|---|
| Network flow beaconing detected | Medium | CommandAndControl, Exfiltration | Regular periodic flows from a single source over 24h (jitter-tolerant) |
| DERP relay traffic surge | Low | CommandAndControl | More than 75% of a source node's recent flows fell back to DERP relay (`IsRelayed=true`); signals NAT/firewall failure, UDP-blocking middlebox, or attempted evasion |
| Large outbound transfer over tailnet | Medium | Exfiltration, Collection | Single flow tx-bytes > 1GB in any 5-min window |
| Mass fan-out from single node | High | Discovery, LateralMovement | Source node initiated flows to N+ distinct destinations within 5 min |
| Subnet router throughput anomaly | Low | Exfiltration, CommandAndControl | Subnet-router src->dst throughput exceeds 3-sigma of its 7-day baseline |
| Unexpected exit-node egress | Medium | CommandAndControl, Exfiltration | Egress through a node that wasn't approved as exit node in the last hour |
| New posture integration added | Medium | Persistence | New entry in `Tailscale_PostureIntegrations_CL` snapshot vs prior |
| Posture integration disabled or removed | High | DefenseEvasion, Persistence | Posture integration disappeared or status changed to disabled |

---

## 7. Hunting queries

### Standard (12)

| Query | Tactics | Use case |
|---|---|---|
| First-seen actor making configuration changes | InitialAccess, Persistence | New principal performing privileged audit actions |
| ACL policy churn | DefenseEvasion, PrivilegeEscalation | How often is the policy file edited - high churn = governance risk |
| Off-hours configuration changes | InitialAccess, Persistence | Privileged audit actions outside business hours |
| Auth key sprawl | Persistence, CredentialAccess | Users with many active reusable auth keys |
| Auth keys with no expiry | Persistence, CredentialAccess | Long-lived auth keys (compliance / hygiene) |
| Devices not seen in 30+ days | Discovery | Stale devices - candidates for offboarding |
| Devices with outdated client version | DefenseEvasion | Client behind latest release |
| Users with zero devices | InitialAccess | Orphaned user accounts |
| Split-DNS per-domain change history | DefenseEvasion, CommandAndControl | Audit-log slice of per-domain DNS routing changes |
| Devices with Tailscale SSH enabled | LateralMovement, Persistence | Cross-reference with the SSH ACL block |
| External (shared-in) device inventory | InitialAccess | Devices admitted via Tailscale sharing |
| Subnet router CIDR exposure inventory | LateralMovement | Every CIDR currently bridged into the tailnet |

### Premium (10)

| Query | Tactics | Use case |
|---|---|---|
| Beaconing candidates (regular periodic flows) | CommandAndControl, Exfiltration | Looser threshold than the analytic rule - investigation aid |
| Cross-tag flow matrix | LateralMovement, Discovery | Flows pivoted by src-tag x dst-tag over 7 days; surfaces tag-to-same-tag loops as worm/service-mesh signal |
| Devices with persistent DERP relay usage | CommandAndControl | Devices that consistently fall back to DERP relay over 24h; long-window companion to the surge rule |
| Exit-node usage patterns | CommandAndControl, Exfiltration | Who uses which exit node, how often, how much data |
| New src->dst node pairs (lateral movement candidates) | LateralMovement, Discovery | First-time observed flow pair vs 7-day baseline |
| Network flows outside business hours | Exfiltration, CommandAndControl | Off-hours flows with `TaggedSource` discriminator to separate service-account from human activity |
| Tagged services with broad inbound exposure | LateralMovement, InitialAccess | Tagged services ranked by inbound `DistinctSrcDevices` / `DistinctSrcUsers` / `DistinctSrcOs` - surfaces ACL drift |
| Top talkers by bytes (virtual traffic) | Exfiltration, Collection | Highest tx/rx nodes over time window |
| Users generating traffic from multiple devices | InitialAccess, Persistence | Multi-device users joined against `Tailscale_Devices_CL.Created` to flag newly-added devices |
| Current posture integration inventory | DefenseEvasion | Snapshot of every posture integration and its enabled state |

---

## 8. Workbooks

Both workbooks are wired automatically when you install the matching connector. Open Sentinel -> **Workbooks** -> search "Tailscale".

**Tailscale Standard Operations**

Tabs for Devices, Users, Keys, DNS, Audit and Health. Quick-look tiles for total devices, devices with updates available, devices with SSH enabled, subnet routers and exit nodes, dormant devices, tailnet-lock state. All KQL validated against live data.

**Tailscale Premium Operations**

Everything in Standard plus Network tab (top talkers, src->dst pairs, exit-node egress, beaconing candidates) and Posture tab (integration inventory, posture state per device).

---

## 9. Architecture notes

### Why two connectors

Tailscale's `/logging/network` endpoint is gated to Premium and Enterprise tailnets. We could put a single connector behind a single Connect button and let pollers silently fail on Free/Standard, but that would generate noisy errors and confuse operators. Splitting the connector by tier means each card only registers pollers the user's API tier actually supports.

### Why one Connect button per connector deploys N pollers

Sentinel CCF normally maps one Connect card to one polling rule. To fan out to 9-11 pollers from a single click, the polling-rule contentTemplate uses the **Proofpoint TAP** pattern - a `guidValue` parameter (`defaultValue: '[newGuid()]'`) and an `innerWorkspace` parameter that defer evaluation to inner-deploy scope (Connect-click time), producing one shared GUID across every poller resource name. Without this exact shape, Sentinel silently deploys only the first poller - the most painful bug we hit in this project.

### Why OAuth clients are required (not personal API tokens)

Tailscale's `/logging/configuration`, `/logging/network`, posture, and DNS endpoints require scoped credentials. Personal API tokens (`tskey-api-...`) are unscoped - against scope-gated endpoints they return HTTP 200 with `"logs": null` (or empty arrays) rather than 401, so the misconfiguration is **silent**. OAuth client credentials carry explicit scopes and fail closed.

### How three DNS endpoints become one table

Tailscale exposes DNS configuration across three endpoints (`/dns/nameservers`, `/dns/preferences`, `/dns/searchpaths`) but the Sentinel UX is cleaner with one logical table. Both connectors land all three into a single `Tailscale_Dns_CL` table with a `ConfigType` discriminator column - the mechanism differs by connector because Azure DCRs are capped at 10 `dataFlows` and the Premium connector is already at the limit:

- **Standard connector** (7 tables, 9 dataFlows): each DNS poller writes to its own input stream (`Custom-Tailscale_DnsNameservers_CL`, `Custom-Tailscale_DnsPreferences_CL`, `Custom-Tailscale_DnsSearchPaths_CL`) and three separate `dataFlows` apply per-source transforms before merging into the shared `Tailscale_Dns_CL` output.
- **Premium connector** (9 tables, 9 dataFlows): all three DNS pollers write to a single unified input stream (`Custom-Tailscale_DnsConfig_CL`) so the DCR uses just one `dataFlow` for DNS. Without this consolidation the Premium DCR would be at 11 dataFlows and Azure would reject the deployment.

Net effect for the operator is identical: one table, filter by `ConfigType`.

### Cadence rationale

- **5 min** for `/logging/configuration` (Standard + Premium) and `/logging/network` (Premium only) - these are event streams with `start` / `end` query parameters
- **60 min** for snapshot endpoints (devices, users, keys, ...) - the data doesn't change frequently and a 1-hour granularity is enough for snapshot-based rules; reducing this would mostly burn ingestion cost without improving detection

---

## 10. Limitations

- **Network flow logs are Premium-only.** The eight Premium rules and ten Premium hunts depend on `Tailscale_Network_CL` and won't run on a Standard install.
- **Microsoft pre-built "Network Session Essentials" detections require a clone-and-rewire.** This solution ships a `vimNetworkSessionTailscale` ASIM NetworkSession parser (and the param-less `ASimNetworkSessionTailscale` wrapper) that maps `Tailscale_Network_CL` to the ASIM NetworkSession schema. Microsoft's pre-built detections call the sealed workspace function `_Im_NetworkSession`, which can't be extended from a Solution - so to apply those detections to Tailscale data, clone the rule and replace `_Im_NetworkSession(...)` with `vimNetworkSessionTailscale(...)` (or `union vimNetworkSessionTailscale(...), _Im_NetworkSession(...)` if you want both sources in one query).
- **Snapshot tables overwrite, they don't diff.** Each 60-min snapshot is a complete current-state poll, not a delta. Rules that need transition detection (e.g. "SSH newly enabled") compare the latest snapshot against a 24-hour baseline.

---

## 11. Troubleshooting

### "Connected" but no rows in any `_CL` table after 30 min

```kql
// Were any pollers dispatched? (DCR ingestion is logged by the workspace)
union AzureDiagnostics
| where Category == "DataCollectionRuleLogs"
| where _ResourceId contains "dcr-tailscale"
| where TimeGenerated > ago(1h)
| project TimeGenerated, Status_s, ResultDescription_s
```

If you see no entries, the connector hasn't been dispatched yet - wait the 5-minute or 60-minute cadence. If you see entries with `Status_s != "Succeeded"`, paste `ResultDescription_s` into a support thread.

### "Connected" but only `Tailscale_Audit_CL` has rows

The remaining endpoints poll on 60-min cadence - the first non-audit snapshot won't land until 60 minutes after Connect. Wait an hour.

### Audit has rows but specific endpoints (devices, dns, ...) don't

Almost always a missing OAuth scope. Tailscale returns HTTP 200 with empty data when a scope is missing, so the poller doesn't error. Re-check the OAuth client at <https://login.tailscale.com/admin/settings/oauth> against the [scope checklist](#oauth-scope-checklist) above.

### `Tailscale_Devices_CL` is missing `AdvertisedRoutes`, `SshEnabled`, etc.

The connector polls `/devices?fields=all`. If those columns are empty in your workspace, the most likely cause is that the DCR transform isn't projecting them - confirm the deployed `dcr-tailscale*` DCR `transformKql` matches the version in this solution and re-Connect.

### OAuth deployment fails with "Invalid Token Endpoint query parameters"

You hit the Sentinel CCF reserved-key bug - the connector definition is including OAuth reserved keys (`client_id`, `client_secret`, `grant_type`, `scope`) inside `TokenEndpointQueryParameters`. The shipped connector definition omits these correctly; if you're seeing this error after edits, remove those keys from the connector definition JSON and redeploy.

### Premium rules silently never fire

Confirm you installed the **Premium** connector (not Standard) and that `Tailscale_Network_CL` and `Tailscale_PostureIntegrations_CL` are receiving rows (see the verification query in [section 4](#4-verification)). Premium rules query those two tables exclusively.

---

## 12. Support

This is a Community-tier solution. Bugs, feature requests, and PRs:

- **GitHub Issues**: <https://github.com/Azure/Azure-Sentinel/issues> (tag the title with `[Tailscale (CCF)]`)
- **Maintainer**: noodlemctwoodle

No SLA - the maintainer responds when convenient. PRs that include tests + a reproducer trip the response time considerably.

---

## 13. Acknowledgements

Thanks to [Tailscale](https://tailscale.com/) for the support that made the Premium-tier features of this solution (network flow log ingestion, posture integration inventory, the seven Premium analytic rules, the five Premium hunting queries, and the Premium Operations workbook) buildable and verifiable against live data.
