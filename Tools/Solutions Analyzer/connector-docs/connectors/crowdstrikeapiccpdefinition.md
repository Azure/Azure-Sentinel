# CrowdStrike API Data Connector (via Codeless Connector Framework)

| | |
|----------|-------|
| **Connector ID** | `CrowdStrikeAPICCPDefinition` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`CrowdStrikeAlerts`](../tables-index.md#crowdstrikealerts), [`CrowdStrikeDetections`](../tables-index.md#crowdstrikedetections), [`CrowdStrikeHosts`](../tables-index.md#crowdstrikehosts), [`CrowdStrikeIncidents`](../tables-index.md#crowdstrikeincidents), [`CrowdStrikeVulnerabilities`](../tables-index.md#crowdstrikevulnerabilities) |
| **Used in Solutions** | [CrowdStrike Falcon Endpoint Protection](../solutions/crowdstrike-falcon-endpoint-protection.md) |
| **Connector Definition Files** | [CrowdStrikeAPI_Definition.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/CrowdStrikeAPI_ccp/CrowdStrikeAPI_Definition.json) |

The [CrowdStrike Data Connector](https://www.crowdstrike.com/) allows ingesting logs from the CrowdStrike API into Microsoft Sentinel. This connector is built on the Microsoft Sentinel Codeless Connector Platform and uses the CrowdStrike API to fetch logs for Alerts, Detections, Hosts, Incidents, and Vulnerabilities. It supports DCR-based ingestion time transformations so that queries can run more efficiently.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configuration steps for the CrowdStrike API**

Follow the instructions below to obtain your CrowdStrike API credentials. Click [here](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions/CrowdStrike%20Falcon%20Endpoint%20Protection/Data%20Connectors/CrowdStrikeAPI_ccp#crowdstrike-falcon--api-data-connector-ccp-framework) for full details.
#### 1. Retrieve API URL
Log in to your CrowdStrike Console and navigate to the API section to copy your Base API URL.
#### 2. Retrieve Client Credentials
Obtain your Client ID and Client Secret from the API credentials section in your CrowdStrike account.
- **Base API URL**: https://api.us-2.crowdstrike.com
- **Client ID**: Your Client ID
- **Client Secret**: (password field)
- Click 'Connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
