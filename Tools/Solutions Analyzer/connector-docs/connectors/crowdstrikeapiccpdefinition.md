# CrowdStrike API Data Connector (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `CrowdStrikeAPICCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`CrowdStrikeAlerts`](../tables-index.md#crowdstrikealerts), [`CrowdStrikeDetections`](../tables-index.md#crowdstrikedetections), [`CrowdStrikeHosts`](../tables-index.md#crowdstrikehosts), [`CrowdStrikeIncidents`](../tables-index.md#crowdstrikeincidents), [`CrowdStrikeVulnerabilities`](../tables-index.md#crowdstrikevulnerabilities) |
| **Used in Solutions** | [CrowdStrike Falcon Endpoint Protection](../solutions/crowdstrike-falcon-endpoint-protection.md) |
| **Connector Definition Files** | [CrowdStrikeAPI_Definition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/CrowdStrikeAPI_ccp/CrowdStrikeAPI_Definition.json) |

The [CrowdStrike Data Connector](https://www.crowdstrike.com/) allows ingesting logs from the CrowdStrike API into Microsoft Sentinel. This connector is built on the Microsoft Sentinel Codeless Connector Platform and uses the CrowdStrike API to fetch logs for Alerts, Detections, Hosts, Incidents, and Vulnerabilities. It supports DCR-based ingestion time transformations so that queries can run more efficiently.

[← Back to Connectors Index](../connectors-index.md)
