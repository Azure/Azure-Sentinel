# SentinelOne Integration for Microsoft Sentinel

## SentinelOne V2 (via Codeless Connector Framework)

> Folder: [`SentinelOneV2_ccf/`](./SentinelOneV2_ccf)

### Why this connector was added

The legacy connectors (the Azure Function connector and the original `SentinelOne_ccp` CCF connector) collect alerts from the SentinelOne REST endpoints (`/cloud-detection/alerts`, `/threats`). Those endpoints **do not** surface SentinelOne's newer **Unified Alert Management (UAM)** detections — Wayfinder threat-hunting, cloud, identity, STAR and 3rd-party alerts — which are only available through the SentinelOne **GraphQL API** (`POST /web/api/v2.1/unifiedalerts/graphql`).

It is built entirely on the Microsoft Sentinel **Codeless Connector Framework (CCF)** — no Azure Function to deploy or maintain — and uses DCR-based ingestion-time transformations so the data lands parsed into custom tables.

### What it ingests

| Data type | Source API | Log Analytics table |
|-----------|-----------|---------------------|
| Activities | `GET /web/api/v2.1/activities` (REST) | `SentinelOneActivities_CL` |
| Agents (created & updated) | `GET /web/api/v2.1/agents` (REST) | `SentinelOneAgents_CL` |
| Groups | `GET /web/api/v2.1/groups` (REST) | `SentinelOneGroups_CL` |
| Threats (created & updated) | `GET /web/api/v2.1/threats` (REST) | `SentinelOneThreats_CL` |
| Unified Alert Management alerts | `POST /web/api/v2.1/unifiedalerts/graphql` (GraphQL) | `SentinelOneAlertsV2_CL` |

The solution's `SentinelOne` parser surfaces the new `SentinelOneAlertsV2_CL` (V2) UAM alerts **without changing how the legacy data is mapped**. The existing V1 mapping (Activities, Agents, Groups, Threats and the legacy `SentinelOneAlerts_CL` table) is left exactly as-is, so any analytic rule, hunting query, workbook or **custom customer detection** built on the `SentinelOne` function keeps working unchanged. V2 UAM alerts are added as a separate, isolated branch that exposes their own columns — `AlertId`, `AlertName`, `DetectedAt`, `AlertCreatedAt`, `AlertUpdatedAt`, `Status`, `Severity`, `AnalystVerdict`, `AlertExternalId`, `StorylineId`, `AttackSurfaces`, `ConfidenceLevel`, `Classification`, `Product`, `Vendor`, `AssigneeName`, `AssigneeEmail`, `Assets` and `DataSources`. Because these columns are unique to the V2 branch, existing queries never see them and are never affected; new content can opt in, e.g. `SentinelOne | where isnotempty(AlertName)`.

### How to use it

1. In Microsoft Sentinel, open **Data connectors** and search for **SentinelOne V2 (via Codeless Connector Framework)**.
2. Open the connector page and click **Add new instance**.
3. In the context pane provide:
   - **SentinelOne Management URL** — e.g. `https://example.sentinelone.net` (the console URL without any path).
   - **API Token** — an API token from a SentinelOne **Service User** (see below).
4. Click **Connect**. Data begins flowing within roughly 10–15 minutes.

The connector supports **multiple instances** — add one instance per SentinelOne Management URL + API Token pair (e.g. MSSP scenarios). Each configured instance is listed in the connector grid with its Management URL and Data Type.

#### Obtaining the SentinelOne API Token

1. Log in to the SentinelOne **Management Console** with an Admin user.
2. Go to **Settings → USERS → Service Users → Actions → Create new service user**.
3. Choose an **Expiration date** and **scope** (by site) and click **Create User**.
4. Copy the generated **API Token** and click **Save**. Use this token in step 3 above.

### Migration from the legacy connectors

You can run SentinelOne V2 **alongside** the existing connectors. During the overlap period the legacy REST alerts (`SentinelOneAlerts_CL`) and the UAM alerts (`SentinelOneAlertsV2_CL`) may contain overlapping events, so run both only long enough to confirm data parity, then disconnect the connector you no longer need.

---

## SentinelOne (Azure Function connector)

### Introduction

This folder contains the Azure function time trigger code for SentinelOne-Microsoft Sentinel connector. The connector will run periodically and ingest the SentinelOne data into the Microsoft Sentinel logs custom table `SentinelOne_CL`. 
## Folders

1. `SentinelOne/` - This contains the package, requirements, ARM JSON file, connector page template JSON, and other dependencies. 
2. `SentinelOneSentinelConnector/` - This contains the Azure function source code along with sample data.


## Installing for the users

After the solution is published, we can find the connector in the connector gallery of Microsoft Sentinel among other connectors in Data connectors section of Sentinel. 

i. Go to Microsoft Sentinel -> Data Connectors

ii. Click on the SentinelOne connector, connector page will open. 

iii. Click on the blue `Deploy to Azure` button.   


It will lead to a custom deployment page where after entering accurate credentials and other information, the resources will get created. 


The connector should start ingesting the data into the logs in next 10-15 minutes.


## Installing for testing


i. Log in to Azure portal using the URL - [https://portal.azure.com/?feature.BringYourOwnConnector=true](https://portal.azure.com/?feature.BringYourOwnConnector=true).

ii. Go to Microsoft Sentinel -> Data Connectors

iii. Click the “import” button at the top and select the json file `SentinelOne_API_FunctionApp.JSON` downloaded on your local machine from Github.

iv. This will load the connector page and rest of the process will be same as the Installing for users guideline above.


Each invocation and its logs of the function can be seen in Function App service of Azure, available in the Azure Portal outside the Microsoft Sentinel.

i. Go to Function App and click on the function which you have deployed, identified with the given name at the deployment stage.

ii. Go to Functions -> SentinelOneSentinelConnector -> Monitor

iii. By clicking on invocation time, you can see all the logs for that run. 

**Note: Furthermore we can check logs in Application Insights of the given function in detail if needed. We can search the logs by operation ID in Transaction search section.**
