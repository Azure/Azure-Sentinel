# UniFi Site Manager

The UniFi Site Manager solution for Microsoft Sentinel ingests cloud-side telemetry from the [UniFi Site Manager API](https://developer.ui.com/site-manager-api/) and ships analytics rules + a workbook for monitoring UniFi-managed networks.

## Contents

- **Data Connector** — single Sentinel UI card ("UniFi Site Manager (CCF)") that deploys four polling rules from one API key. Polls Sites, Devices, Hosts and ISP Metrics every 5 minutes.
- **Custom tables** — `Unifi_Cloud_Sites_CL`, `Unifi_Cloud_Devices_CL`, `Unifi_Cloud_Hosts_CL`, `Unifi_Cloud_ISPMetrics_CL`
- **21 analytics rules** — covering ISP downtime, latency, packet loss, SLA breach, WAN issues (incl. WAN2/secondary failover), IPS/IDS posture changes, firmware drift, device offline events, controller connection state, critical notifications (delta-based), external WAN IP rotation, system-log shipping disabled (defense-evasion), and data connector health.
- **8 hunting queries** — firmware-drift hotspots, long-tail latency, device flapping, WAN IP geographic deviation, firmware version diversity, persistent WAN issues, off-hours device adoption, console group membership churn.
- **Workbook** — Operations dashboard with 6 tabs: Overview, Sites, ISP Performance, Devices, Security, Operations. Includes open-incident view, multi-WAN status panels, severity-classified incident feed, and color-coded latency thresholds.

## Pre-requisites

1. A Microsoft Sentinel-enabled Log Analytics workspace.
2. A Data Collection Endpoint (DCE) in the same region.
3. A UniFi Site Manager API key. Generate one at <https://unifi.ui.com/api> (Site Manager → Account → API → Create API Key). Required scope: **Audit Logs - Read** is optional; the four ingestion endpoints used here do not require it.

## Connect

1. Microsoft Sentinel → **Content hub** → install the **UniFi Site Manager** solution.
2. Sentinel → **Data connectors** → search **"UniFi Site Manager (CCF)"** → **Open connector page**.
3. Paste your API key → **Connect**. All four poll rules instantiate from a single click.

## Tier requirements

Site Manager API endpoints used by this connector are available on all UniFi cloud plans. The connector does **not** depend on UniFi network flow logs or the audit log API, both of which require Pro+.

## Analytics rule strategy

State-based rules (IPS/IDS disabled, WAN issues, critical notifications, system-log shipping disabled) fire only on **state transitions** — they detect the change from `enabled → disabled`, not the persistent state. This keeps incident volume proportional to actual events and avoids alert storms during sustained outages.

ISP performance rules (downtime, latency, packet loss, SLA) operate on rolling windows of the `Unifi_Cloud_ISPMetrics_CL` table.

## Support

This is a community-supported solution maintained by Fetch Labs. File issues at <https://github.com/noodlemctwoodle/Azure-Sentinel/issues>.
