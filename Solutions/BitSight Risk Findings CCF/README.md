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

Publisher: **Obrela**.

## Package contents

1. `BitsightRiskFindings_CCF.json` — the complete CCF solution as a single ARM template.
2. `BitsightRiskFindings.kql` — sample KQL queries for validation and operational monitoring.
3. `README.md` — this file.
4. `ReleaseNotes.md` — package release history.

## Prerequisites

1. A Microsoft Sentinel-enabled Log Analytics workspace.
2. A valid BitSight API token with access to the target company.
3. The BitSight **company GUID** to monitor.
4. An **existing Data Collection Endpoint (DCE)** in the same workspace region.

### Important DCE note

This template does **not** create a DCE resource. Instead, the DCR references an existing DCE through `dataCollectionEndpointId`. The current template assumes the DCE resource ID format below:

`/subscriptions/{subscription}/resourceGroups/{resourceGroupName}/providers/Microsoft.Insights/dataCollectionEndpoints/{workspace}`

If your DCE has a different name, update the `dataCollectionEndpointId` value in the template before deployment.

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

### Not created by this template

- A Data Collection Endpoint (DCE)

An existing DCE is required and must be reachable through the `dataCollectionEndpointId` referenced by the DCR.

## How it works

- **Authentication**  
  The connector uses BitSight API token authentication and sends it through the poller authentication configuration as a Basic authorization header.

- **Endpoint**  
  The connector calls:

  `GET https://api.bitsighttech.com/ratings/v1/companies/{companyGuid}/findings`

  for the configured company.

- **Time window**  
  Incremental polling uses:
  - `last_seen_gte`
  - `last_seen_lte`

  with a one-day (`1440` minute) polling window and `yyyy-MM-dd` formatting.

- **Response parsing and paging**  
  Findings are read from the BitSight response body and paging follows the `$.links.next` value.

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
