# UniFi Syslog (CCF)

Microsoft Sentinel solution that ingests UniFi UDM, switch and access-point **syslog** telemetry via a self-hosted Logstash relay that pushes events to the Codeless Connector Framework (CCF) Push endpoint provisioned by this solution.

- **CCF Push connector** (preview) - 1-click `Deploy` provisions Entra app + DCR + custom table + role assignments
- **Dual-output DCR** - CEF / synthetic-CEF security events route to `CommonSecurityLog`, forensic / non-CEF events route to `Unifi_Syslog_CL`
- **Ingest-time enrichment** built into the Logstash pipeline: MaxMind GeoIP + ASN, FireHOL Level 1 + Spamhaus DROP/EDROP + Tor exit threat-intel feeds
- **8 analytic rules** + **10 hunting queries** covering identity, network, IDS/IPS, brute force, exfiltration and operational signals
- **No Logstash side changes** when you click Connect - the same container that already runs on your network simply consumes five env values from the Connector card

---

## Table of contents

1. [How the pipeline fits together](#1-how-the-pipeline-fits-together)
2. [Pre-requisites](#2-pre-requisites)
3. [Installation - 4 steps](#3-installation---4-steps)
4. [Verification](#4-verification)
5. [Custom table reference](#5-custom-table-reference)
6. [Analytic rules](#6-analytic-rules)
7. [Hunting queries](#7-hunting-queries)
8. [Synthetic-CEF event classes](#8-synthetic-cef-event-classes)
9. [Architecture notes](#9-architecture-notes)
10. [Limitations](#10-limitations)
11. [Troubleshooting](#11-troubleshooting)
12. [Support](#12-support)

---

## 1. How the pipeline fits together

```
   UniFi UDM / Switch / AP                       Microsoft Sentinel
   -----------------------                       ------------------
        |                                              |
        | syslog UDP/TCP 514                           |
        v                                              ^
   Logstash relay (your host)                          |
   - Parse dual-timestamp UniFi syslog                 |
   - Promote CEF + synthetic CEF                       |
   - Enrich with MaxMind GeoIP/ASN                     |
   - Match TI feeds (FireHOL / Spamhaus / Tor)         |
        |                                              |
        | OAuth2 client_credentials                    |
        | HTTPS POST                                   |
        v                                              |
   Data Collection Endpoint (DCE) ------ Data Collection Rule (DCR) --+
                                          |                          |
                                          | transformKql split       |
                                          v                          v
                                CommonSecurityLog          Unifi_Syslog_CL
                                (CEF security events)      (forensic catch-all)
```

The Logstash container ships inside this Solution at [`Logstash/`](./Logstash) - Dockerfile, `logstash.conf`, the MaxMind GeoIP/ASN updater, the TI feed refresher, and `.env.example`. It uses the `microsoft-sentinel-log-analytics-logstash-output-plugin` (v2.1.1) with OAuth2 client-credentials - exactly what CCF Push expects. The Sentinel Deploy Push button auto-creates the Entra app, DCR, DCE, table, and role assignment; you only have to copy five values into the `.env`.

---

## 2. Pre-requisites

1. **Microsoft Sentinel-enabled Log Analytics workspace.**
2. **Permissions:**
   - Microsoft Entra ID Application Developer (or higher) to register the connector's Entra app.
   - Owner / User Access Administrator on the workspace's resource group to assign `Monitoring Metrics Publisher` on the DCR.
3. **A Linux host** reachable from your UniFi devices on UDP/TCP 514. UnRAID, Docker host, k8s node, generic VM - anywhere you can run a Docker container. ~512 MB RAM is plenty for a single-site deployment.
4. **MaxMind account** (optional but recommended) - free GeoLite2 tier provides GeoIP + ASN enrichment. Sign up at [maxmind.com](https://www.maxmind.com/en/geolite2/signup).

---

## 3. Installation - 4 steps

### 3.1. Install the Solution

Microsoft Sentinel -> **Content hub** -> search "UniFi Syslog" -> Install.

### 3.2. Deploy the Sentinel-side resources

Sentinel -> **Data connectors** -> open **UniFi Syslog (CCF Push)** -> click **Deploy UniFi Syslog Push connector resources**.

Azure auto-provisions:
- `Unifi_Syslog_CL` custom log table
- Data Collection Rule with two transforms (CEF -> CommonSecurityLog, non-CEF -> Unifi_Syslog_CL)
- Entra application with a client secret
- Role assignment granting the application `Monitoring Metrics Publisher` on the DCR

The connector card then displays five copyable values.

### 3.3. Deploy the Logstash relay

The container Dockerfile + Logstash configuration ship inside this Solution at `Logstash/`. On your Linux host:

```bash
# Clone the upstream Azure-Sentinel repo (or the fork you installed this Solution from)
git clone https://github.com/Azure/Azure-Sentinel
cd "Azure-Sentinel/Solutions/UniFi Syslog (CCF)/Logstash"
```

Copy `.env.example` to `.env` and fill in the five values from step 3.2 plus your MaxMind credentials:

```bash
cp .env.example .env
# Edit .env with your editor of choice

SENTINEL_TENANT_ID=<Tenant ID>
SENTINEL_CLIENT_APP_ID=<Application ID>
SENTINEL_CLIENT_APP_SECRET=<Client Secret>
SENTINEL_DCE_URL=<DCE URI>
SENTINEL_DCR_IMMUTABLE_ID=<DCR Immutable ID>
SENTINEL_DCR_STREAM_NAME=Custom-Unifi_CL

# MaxMind (optional - leaves geo/ASN columns empty if blank)
MAXMIND_ACCOUNT_ID=<your account ID>
MAXMIND_LICENSE_KEY=<your license key>
```

Start the container:

```bash
docker compose build --no-cache
docker compose up -d
```

Confirm UDP/TCP 514 is listening:

```bash
ss -tulpn | grep 514
```

### 3.4. Point UniFi at the Logstash host

In the UniFi Network application:
- **Settings -> Logging -> Remote Logging** - enable, set **Server** to the Logstash host IP, **Port** 514. Tick **Security Detections** to capture Suricata IDS/IPS alerts.
- **System Settings -> Console Settings -> Remote Logging** (for UniFi OS-level events: sshd, sudo, ubios-udapi-server, switch TRAPMGR) - same host and port.

Within ~30 seconds you should see events flowing in the Logstash logs and in your workspace within 1-2 minutes.

---

## 4. Verification

```kql
// CEF events arriving in CommonSecurityLog
CommonSecurityLog
| where TimeGenerated > ago(15m)
| where DeviceVendor =~ "Ubiquiti"
| summarize Events = count() by DeviceEventCategory, DeviceEventClassID
| order by Events desc

// Forensic catch-all in Unifi_Syslog_CL
Unifi_Syslog_CL
| where TimeGenerated > ago(15m)
| summarize Events = count() by ProcessName
| order by Events desc

// Logstash pipeline freshness across both tables
union 
    (CommonSecurityLog | where DeviceVendor =~ "Ubiquiti" | extend _T = "CommonSecurityLog (UniFi)"),
    (Unifi_Syslog_CL                                     | extend _T = "Unifi_Syslog_CL")
| where TimeGenerated > ago(2h)
| summarize Rows = count(), Latest = max(TimeGenerated) by _T
```

A healthy install returns rows in both tables. If only `Unifi_Syslog_CL` has rows, the Logstash CEF promotion isn't matching - see [Troubleshooting](#11-troubleshooting).

---

## 5. Custom table reference

`Unifi_Syslog_CL` is the forensic catch-all for events that aren't promoted to CEF. Columns:

| Column | Type | Notes |
|---|---|---|
| `TimeGenerated` | datetime | Ingestion time |
| `EventTime` | datetime | Original syslog header timestamp |
| `Computer` | string | Source host (UDM hostname, AP name) |
| `Facility` | string | Syslog facility (kern, daemon, auth, ...) |
| `SyslogSeverity` | string | emergency / alert / critical / error / warning / notice / info / debug |
| `ProcessName` | string | Daemon name (sshd, sudo, dnsmasq, kernel, ubios-udapi-server, ...) |
| `SourceIP` | string | Source IP if present in payload |
| `SourcePort` | int | Source port |
| `SourceUserName` | string | Source user |
| `DestinationIP` | string | Destination IP |
| `DestinationPort` | int | Destination port |
| `DestinationUserName` | string | Destination user |
| `Protocol` | string | TCP / UDP / ICMP |
| `DeviceAction` | string | ALLOW / DROP / ACK / NAK / EXECUTE / ... |
| `DeviceEventCategory` | string | firewall / vpn / dhcp / wifi / dns / audit / ... |
| `Message` | string | Lowercased original message body |
| `RawJson` | dynamic | All parser fields not promoted to columns |

CEF events do NOT land here. They land in the built-in `CommonSecurityLog` table with the full CEF column set plus the ingest-time TI/Geo columns (`MaliciousIP`, `ThreatSeverity`, `MaliciousIPCountry`, `MaliciousIPLatitude`, `MaliciousIPLongitude`, `IndicatorThreatType`, `ThreatDescription`, `DeviceCustomString3` = country, `DeviceCustomString4` = ASN org, `DeviceCustomNumber1` = ASN number).

---

## 6. Analytic rules

| # | Rule | Severity | Tactics | Watches |
|---|---|---|---|---|
| 1 | UniFi: Threat-intel match on inbound traffic | High | InitialAccess, Reconnaissance, CommandAndControl | `ThreatSeverity >= 7` source IPs in any traffic |
| 2 | UniFi: IDS / IPS signature hit | Medium | CommandAndControl, InitialAccess | Suricata `DeviceEventClassID == "201"` plus plain-syslog suricata events |
| 3 | UniFi: SSH brute force | High | CredentialAccess, InitialAccess | 5+ `sshd_auth_fail` events from one source in 15 min |
| 4 | UniFi: Repeated firewall drops from single source | Medium | Discovery, InitialAccess | 50+ DROP/REJECT from one source in 1 hour |
| 5 | UniFi: Admin activity from non-LAN source | High | InitialAccess, CredentialAccess, LateralMovement | sshd success or admin CEF from non-RFC1918 source |
| 6 | UniFi: VPN authentication failures | High | CredentialAccess, InitialAccess | 10+ VPN auth failures in 1 hour (CEF + plain-syslog daemons) |
| 7 | UniFi: Traffic from Tor exit node | Medium | CommandAndControl | `IndicatorThreatType has "Anonymization"` or `ThreatDescription has "tor_exit"` |
| 8 | UniFi: Critical-severity system event | High | Impact | CEF `LogSeverity >= 8` or syslog severity emergency/alert/critical |

---

## 7. Hunting queries

| # | Query | Tactics | Use case |
|---|---|---|---|
| 1 | UniFi: Top external attackers (TI-flagged) | InitialAccess, Reconnaissance, CommandAndControl | Prioritise blocklist additions |
| 2 | UniFi: Port scanner sweep detection | Discovery, Reconnaissance | 10+ distinct dst ports in 5 min |
| 3 | UniFi: TI-flagged probes against application ports | InitialAccess, Reconnaissance | Which of your services attract most scans |
| 4 | UniFi: First-seen external source IPs | InitialAccess, Reconnaissance | New-source anomaly vs 30-day baseline |
| 5 | UniFi: Geo-anomalous admin / SSH activity | InitialAccess, CredentialAccess | Admin actions from countries outside expected list |
| 6 | UniFi: Sudo activity audit | PrivilegeEscalation, Execution | Real admin sudo (filters out service accounts) |
| 7 | UniFi: SSH brute force - most-targeted accounts | CredentialAccess | What usernames attackers guess |
| 8 | UniFi: WiFi deauth flooding (possible Karma / Evil Twin) | CredentialAccess, Discovery | 20+ deauth/disassoc on one AP in 5 min |
| 9 | UniFi: DHCP NAK / DECLINE anomalies | Discovery, Impact | Rogue DHCP, IP conflict, pool exhaustion |
| 10 | UniFi: TI feed effectiveness comparison | Reconnaissance | Which TI feed is pulling its weight |

---

## 8. Synthetic-CEF event classes

The Logstash pipeline promotes the following non-CEF UniFi events into CEF so they land in `CommonSecurityLog`:

| `DeviceEventClassID` | Source | What it captures |
|---|---|---|
| `LAN_LAN` / `WAN_LOCAL` / etc. | UniFi zone-based firewall | Zone direction; action in `DeviceAction`; policy ID in `DCS6` |
| `sudo_command` | UniFi OS sudo | Real admin sudo events (health-check noise demoted to Unifi_Syslog_CL) |
| `dhcp_ACK` / `dhcp_NAK` / `dhcp_REQUEST` / `dhcp_DECLINE` / `dhcp_RELEASE` / `dhcp_OFFER` / `dhcp_DISCOVER` | dnsmasq-dhcp | Identity tracking, IP conflicts |
| `wifi_deauth` / `wifi_disassoc` | AP kernel | 802.11 deauth/disassoc with TA, RA, reason |
| `EVT_GW_*` | ubios-udapi-server | Gateway signal-out events |
| `switch_link_up` / `switch_link_down` | TRAPMGR | Switch port link state |
| `sshd_auth_success` / `sshd_auth_fail` | sshd | Four message patterns: standard Failed, PAM, Invalid user, Accepted |

The full mapping lives in [`Logstash/logstash.conf`](./Logstash/logstash.conf) section 5.

---

## 9. Architecture notes

### CCF Push vs RestApiPoller

UniFi devices emit syslog by pushing UDP/TCP. There's no REST API exposing the same per-event stream, so CCF RestApiPoller (used by our Tailscale and UniFi Site Manager solutions) doesn't fit. CCF Push (public preview in 2026) is purpose-built for this: your app authenticates with OAuth client credentials and POSTs JSON to the DCE. The existing Logstash output plugin already does exactly this.

### Why the DCR has two dataFlows

A single input stream (`Custom-Unifi_CL`) is split by an `EventFormat` discriminator that Logstash sets per event:
- `EventFormat == 'cef'` -> projected with full CEF schema -> `Microsoft-CommonSecurityLog`
- otherwise -> projected with forensic schema -> `Custom-Unifi_Syslog_CL`

Net result: one stream from Logstash, two tables in Sentinel, no duplicate ingestion.

### Why columns declared as `string` get cast to int/real in transformKql

The v2 Logstash output plugin (Java-based, replaced the deprecated Ruby v1 in 2025) has a known quirk where it doesn't always serialise native int columns correctly. Working around it: declare port/severity/lat/long columns as string in the DCR stream, then `toint()` / `toreal()` cast in `transformKql`. Don't switch them back to int - values will silently drop.

### Microsoft already publishes a UniFi solution

Microsoft's existing "Ubiquiti UniFi" solution uses **Custom Logs via AMA** - install AMA on a VM, configure a custom-log file path. It captures the raw syslog but does no enrichment. This CCF Push solution complements it by adding:
- Synthetic-CEF promotion for non-CEF events
- MaxMind GeoIP + ASN enrichment at ingest
- TI feed matching (FireHOL, Spamhaus, Tor) writing native CSL columns

Pick whichever matches your operational appetite - the AMA version is simpler, this one is richer.

---

## 10. Limitations

- **CCF Push is in public preview.** Microsoft can change schema / behaviour. Stable enough that Keeper Security, Obsidian Security and Varonis ship CCF Push connectors today, but expect schema churn until GA.
- **You run the relay.** This is not an agentless connector. You need a Linux host on the same network as your UniFi devices.
- **No VPN tunnel connect/disconnect events.** UniFi doesn't expose per-tunnel events via syslog. VPN auth failures come through (covered by Rule #6), but session start/stop don't.
- **Single-site assumption.** The shipped Logstash conf assumes one tailnet / one UniFi controller. Multi-site needs duplicating the container per site or extending the conf to tag events by site_id.

---

## 11. Troubleshooting

### "Connected" but no rows in either table

Check Logstash health:

```bash
docker logs --tail 50 unifi-syslog-logstash
curl -s http://<logstash-host>:9600/_node/stats/pipelines | jq '.pipelines.main.events'
```

If `events.in == 0`, UniFi isn't reaching Logstash - check syslog config in Network and System Settings, and check firewall rules.

If `events.in > 0` but `events.out < events.in`, events are getting dropped by filters - check `_grokparsefailure` or `_jsonparsefailure` tags in `docker logs`.

### Rows in `Unifi_Syslog_CL` but not in `CommonSecurityLog`

Logstash isn't tagging events as CEF (`EventFormat == 'cef'`). Confirm:

```bash
ssh root@<logstash-host> 'docker logs --tail 2000 unifi-syslog-logstash 2>&1 | grep "EventFormat" | head -5'
```

If you see `EventFormat = ""`, your UniFi version may not be sending CEF natively - the synthetic-CEF promoters in section 5 of `logstash.conf` should still convert the major event classes.

### `MaliciousIP` / `ThreatSeverity` columns are always empty

The Logstash container refreshes TI feeds every 6 hours via `refresh-ti-feeds.sh`. Verify on the host:

```bash
docker exec unifi-syslog-logstash ls -la /usr/share/logstash/data/ti/
```

You should see `firehol_level1.txt`, `spamhaus_drop.txt`, `spamhaus_edrop.txt`, `tor_exits.txt`. If they're missing or empty, check `docker exec unifi-syslog-logstash cat /var/log/refresh-ti-feeds.log`.

### MaxMind enrichment empty

Confirm credentials are in `.env`:

```bash
docker exec unifi-syslog-logstash printenv | grep MAXMIND
```

Then check the GeoIP database was downloaded at build time:

```bash
docker exec unifi-syslog-logstash ls /usr/share/logstash/data/maxmind/
```

### Logstash plugin upgrade

The Microsoft-Sentinel output plugin retires the v1 (Ruby) variant on 2027-01-01. This solution uses v2 (Java) at `microsoft-sentinel-log-analytics-logstash-output-plugin` v2.1.1+. If you upgrade Logstash, ensure the plugin is fresh:

```bash
docker exec unifi-syslog-logstash bin/logstash-plugin update microsoft-sentinel-log-analytics-logstash-output-plugin
```

### "Invalid Token Endpoint query parameters" on Logstash startup

Check that the `client_id`, `client_secret`, `grant_type` keys are NOT inside the `TokenEndpointQueryParameters` block of any custom config. The plugin injects them automatically.

---

## 12. Support

Community-tier solution.

- **GitHub Issues**: <https://github.com/Azure/Azure-Sentinel/issues> (tag the title with `[UniFi Syslog (CCF)]`)
- **Logstash assets**: shipped inside this Solution at [`Logstash/`](./Logstash)
- **Maintainer**: noodlemctwoodle

No SLA. PRs welcome.
