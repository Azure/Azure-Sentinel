# Netskope Alerts and Events

| | |
|----------|-------|
| **Connector ID** | `NetskopeAlertsEvents` |
| **Publisher** | Netskope |
| **Tables Ingested** | [`NetskopeAlerts_CL`](../tables-index.md#netskopealerts_cl), [`NetskopeEventsApplication_CL`](../tables-index.md#netskopeeventsapplication_cl), [`NetskopeEventsAudit_CL`](../tables-index.md#netskopeeventsaudit_cl), [`NetskopeEventsConnection_CL`](../tables-index.md#netskopeeventsconnection_cl), [`NetskopeEventsDLP_CL`](../tables-index.md#netskopeeventsdlp_cl), [`NetskopeEventsEndpoint_CL`](../tables-index.md#netskopeeventsendpoint_cl), [`NetskopeEventsInfrastructure_CL`](../tables-index.md#netskopeeventsinfrastructure_cl), [`NetskopeEventsNetwork_CL`](../tables-index.md#netskopeeventsnetwork_cl), [`NetskopeEventsPage_CL`](../tables-index.md#netskopeeventspage_cl) |
| **Used in Solutions** | [Netskopev2](../solutions/netskopev2.md) |
| **Connector Definition Files** | [NetskopeAlertsEvents_ConnectorDefination.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Netskopev2/Data%20Connectors/NetskopeAlertsEvents_RestAPI_CCP/NetskopeAlertsEvents_ConnectorDefination.json) |

Netskope Security Alerts and Events

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): Read and Write permissions are required.

**Custom Permissions:**
- **Netskope organisation url**: The Netskope data connector requires you to provide your organisation url. You can find your organisation url by signing into the Netskope portal.
- **Netskope API key**: The Netskope data connector requires you to provide a valid API key. You can create one by following the [Netskope documentation](https://docs.netskope.com/en/rest-api-v2-overview-312207/).

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. STEP 1 - Create a Netskope API key.**

Follow the [Netskope documentation](https://docs.netskope.com/en/rest-api-v2-overview-312207/) for guidance on this step.

**2. STEP 2 - Enter your Netskope product Details**

Enter your Netskope organisation url & API Token below:
- **Organisation Url**: Enter your organisation url
- **API Key**: (password field)
- **Netskope Alerts Remediation** (select)
  - Yes
  - No
- **Netskope Alerts Uba** (select)
  - Yes
  - No
- **Netskope Alerts Security Assessment** (select)
  - Yes
  - No
- **Netskope Alerts Quarantine** (select)
  - Yes
  - No
- **Netskope Alerts Policy** (select)
  - Yes
  - No
- **Netskope Alerts Malware** (select)
  - Yes
  - No
- **Netskope Alerts Malsite** (select)
  - Yes
  - No
- **Netskope Alerts DLP** (select)
  - Yes
  - No
- **Netskope Alerts CTEP** (select)
  - Yes
  - No
- **Netskope Alerts Watchlist** (select)
  - Yes
  - No
- **Netskope Alerts Compromised Credentials** (select)
  - Yes
  - No
- **Netskope Alerts Content** (select)
  - Yes
  - No
- **Netskope Alerts Device** (select)
  - Yes
  - No
- **Netskope Events Application** (select)
  - Yes
  - No
- **Netskope Events Audit** (select)
  - Yes
  - No
- **Netskope Events Connection** (select)
  - Yes
  - No
- **Netskope Events DLP** (select)
  - Yes
  - No
- **Netskope Events Endpoint** (select)
  - Yes
  - No
- **Netskope Events Infrastructure** (select)
  - Yes
  - No
- **Netskope Events Network** (select)
  - Yes
  - No
- **Netskope Events Page** (select)
  - Yes
  - No
**OPTIONAL: Specify the Index the API uses.**

  **Configuring the index is optional and only required in advanced scenario's.** 
 Netskope uses an [index](https://docs.netskope.com/en/using-the-rest-api-v2-dataexport-iterator-endpoints/#how-do-iterator-endpoints-function) to retrieve events. In some advanced cases (consuming the event in multiple Microsoft Sentinel workspaces, or pre-fatiguing the index to only retrieve recent data), a customer might want to have direct control over the index.
  - **Index**: NetskopeCCP

**3. STEP 3 - Click Connect**

Verify all fields above were filled in correctly. Press the Connect to connect Netskope to Microsoft Sentinel.
- Click 'connect' to establish connection

[← Back to Connectors Index](../connectors-index.md)
