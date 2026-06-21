# BitSight Risk Findings Data Connector (Codeless Connector Framework)

* [Introduction](#introduction)
* [Description](#description)
* [Package contents](#package-contents)
* [Prerequisites](#prerequisites)
* [Deployment](#deployment)
* [Connecting a BitSight company](#connecting-a-bitsight-company)
* [What the template creates](#what-the-template-creates)
* [How it works](#how-it-works)
* [Validation](#validation)
* [Notes and limitations](#notes-and-limitations)

## Introduction

This package contains the Microsoft Sentinel **Codeless Connector Framework (CCF)** artifact for the reduced BitSight Risk Findings connector.

It is designed to ingest BitSight risk-vector findings for a single portfolio company per connection into Microsoft Sentinel, without using an Azure Function App. The template packages the connector UI, the Content Hub solution metadata, the custom table schema, the Data Collection Rule (DCR), and the `RestApiPoller` connection content used by the connector.

The connector ingests only normalized **WARN** and **BAD** findings for a selected set of BitSight risk vectors. The filtering and normalization logic is implemented in the DCR transform.

## Description

The connector brings targeted BitSight finding data into Microsoft Sentinel for one BitSight company per connection. It covers the following monitoring factors:

1. Botnet Infections
2. Spam Propagation
3. Malware Servers
4. Unsolicited Communications
5. Potentially Exploited
6. TLS/SSL Certificates
7. Patching Cadence
8. Mobile Software
9. Open Ports
10. File Sharing

Only **WARN** and **BAD** findings are ingested. **FAIR** findings can be added later by modifying the DCR `transformKql` filter.

Publisher: **Microsoft Security Community**.
Author: ** Konstantinos Lianos**

## Package contents

1. `BitsightRiskFindings_CCF.json` — the complete CCF solution as a single ARM template.
2. `BitsightRiskFindings.kql` — sample KQL queries for validation and operational monitoring.
3. `README.md` — this file.
4. `ReleaseNotes.md` — package release history.

## Prerequisites

1. A Microsoft Sentinel-enabled Log Analytics workspace.
2. A valid BitSight API token with access to the target company.
3. The BitSight **company GUID** to monitor.

No Data Collection Endpoint (DCE) needs to be created in advance — see the note below.

### Data Collection Endpoint (DCE)

You do **not** need to create a DCE manually. When you connect the connector, Microsoft Sentinel automatically provisions a shared Data Collection Endpoint for the workspace (named `ASI-<workspaceId>`) and associates it with the DCR. The DCR carries a `dataCollectionEndpointId` reference that the platform resolves during connection.

If, in your environment, you intend to point the DCR at a specific pre-existing DCE instead, update the `dataCollectionEndpointId` value in the template before deployment.

## Deployment

The connector deploys as a single custom ARM template.

1. In the Azure portal, open **Deploy a custom template**.
2. Select **Build your own template in the editor**.
3. Paste the contents of `BitsightRiskFindings_CCF.json` and save.
4. Select the subscription, resource group, workspace, and workspace region, then deploy.

This deployment registers the BitSight Risk Findings connector package and its associated metadata in Microsoft Sentinel.

## Connecting a BitSight company

1. Go to **Microsoft Sentinel -> Data connectors**.
2. Open **Bitsight Risk Findings (CCF)**.
3. Provide:
   - **Company GUID** — the BitSight company to ingest findings for.
   - **Bitsight API token** — entered as a secret.
4. Select **Connect**.

Each connection ingests findings for one company. To ingest multiple companies, create multiple connections.

## What the template creates

### At template deployment time

The template registers the following solution and connector artifacts:

- Content Hub solution package and metadata
- Connector definition metadata
- Connector UI definition
- Packaged connector-definition content template
- Packaged connection content template

These artifacts are created by the ARM template itself.

### Defined in the connector package and used during connection deployment

The connector package includes the resources required for data ingestion:

- The custom table `BitsightRiskFindings_CL`
- The DCR `BitsightDCR`
- One `RestApiPoller` data connector connection

### Provisioned automatically by Microsoft Sentinel

- The Data Collection Endpoint (DCE), created when the connector is connected (`ASI-<workspaceId>`).

## How it works

- **Authentication**
  The connector uses BitSight API token authentication and sends it through the poller authentication configuration as a Basic authorization header (the token as the username, with an empty password).

- **Endpoint**
  The connector calls:

  `GET https://api.bitsighttech.com/ratings/v1/companies/{companyGuid}/findings`

  for the configured company.

- **Polling**
  Each poll retrieves the **current set of findings** for the configured company and pages through all results using the `$.links.next` link header. The connector does **not** apply a `last_seen` time-window filter. BitSight findings represent current state rather than a time-ordered event stream, and a rolling window keyed on `last_seen` would miss findings that were not re-observed inside the window. Repeated findings across polls are collapsed downstream by the hunting queries using `arg_max(TimeGenerated, *) by finding_uid`.

- **Response parsing and paging**
  Findings are read from the `$.results` array of the BitSight response body, and paging follows the `$.links.next` value.

- **Normalization and filtering**
  The DCR transform:
  - derives `normalized_risk_state`
  - filters findings to `warn` and `bad`
  - limits ingestion to the ten configured BitSight risk vectors
  - maps the output to `BitsightRiskFindings_CL`

  The transform also builds `finding_uid`, projects the normalized columns, and stores both `details` and `raw` payloads for investigation.

## Validation

After connecting, allow time for the first polling cycle to complete, then run the sample queries in `BitsightRiskFindings.kql`.

Quick checks:

```kusto
BitsightRiskFindings_CL
| take 10
```

```kusto
// Current deduplicated WARN/BAD findings
BitsightRiskFindings_CL
| summarize arg_max(TimeGenerated, *) by finding_uid
| where normalized_risk_state in ('warn','bad')
| order by TimeGenerated desc
```

If no data appears after a polling cycle, enable Sentinel **Health Monitoring** diagnostic settings (DataConnectors) and inspect connector polling status:

```kusto
SentinelHealth
| where SentinelResourceType == "Data connector"
| where SentinelResourceName has "BitSight"
| order by TimeGenerated desc
```

## Notes and limitations

- **WARN/BAD only.** Only `warn` and `bad` findings are ingested. To include `fair` findings, edit the `where normalized_risk_state in ('warn','bad')` line in the DCR `transformKql`.

- **Risk-vector scope.** Ingestion is limited to the ten risk vectors listed under [Description](#description) via the `where rv in (...)` filter in the transform. Add or remove vectors there as needed.

- **One company per connection.** Each `RestApiPoller` connection ingests findings for a single company GUID. Create additional connections for additional companies.

- **Full-set polling.** Because no time-window filter is applied, each poll re-ingests the current findings set. The raw `BitsightRiskFindings_CL` table therefore accumulates repeated rows over time; queries de-duplicate with `arg_max(TimeGenerated, *) by finding_uid`. Factor this into ingestion-volume expectations, especially if polling frequently or monitoring large finding sets.

- **Company identity columns.** BitSight's per-company findings payload does not always echo the company identity inside each finding, so `company_guid` and `company_name` may be empty and `finding_uid` may begin with a leading colon. Risk-vector, severity, and state data are unaffected.

- **Analytic rule.** The bundled analytic rule ships disabled by default; enable it after confirming data flow.

- **Packaging validation.** When packaged with the Azure-Sentinel V3 tool, the arm-ttk test `IDs Should Be Derived From ResourceIDs` reports the auto-generated `id` and `contentProductId` properties. These values are produced by the packaging tool, not authored in the solution source, and are a documented, accepted false positive (see the V3 packaging README). There is no functional impact.
