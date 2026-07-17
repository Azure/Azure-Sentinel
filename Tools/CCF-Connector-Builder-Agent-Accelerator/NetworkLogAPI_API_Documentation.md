# Network Log API – Reference Documentation

> **Purpose:** This API is a mock network activity log data source deployed as an Azure Function App.  
> It is designed to be consumed by the **Microsoft Sentinel Codeless Connector Framework (CCF)** API Poller
> to ingest simulated firewall/network log data into a Sentinel workspace for connector development and testing.

---

## Table of Contents

1. [Overview](#overview)
2. [Base URL](#base-url)
3. [Authentication](#authentication)
4. [Common Request Headers](#common-request-headers)
5. [Common Response Headers](#common-response-headers)
6. [Endpoints](#endpoints)
   - [GET /api/GetNetworkLogs](#get-apigetnetworklogs)
   - [POST /api/RefreshData](#post-apirefreshdata)
7. [Data Schema – NetworkLogRecord](#data-schema--networklogrecord)
8. [Pagination](#pagination)
9. [Incremental Pull (Time-Based Filtering)](#incremental-pull-time-based-filtering)
10. [Error Responses](#error-responses)
11. [CCF API Poller Connector Configuration](#ccf-api-poller-connector-configuration)
12. [Deployment](#deployment)
13. [Packaging the Function App](#packaging-the-function-app)

---

## Overview

The **Network Log API** exposes 50 simulated network activity log records representing realistic firewall
traffic events including web browsing, DNS lookups, blocked RDP/SSH brute-force attempts, lateral movement
alerts, malware C2 blocks, VPN sessions, and more.

| Property | Value |
|---|---|
| Data format | JSON |
| Authentication | API Key (header) |
| Pagination | Offset/page-based with `nextLink` |
| Incremental pull | `since` query parameter (ISO 8601) |
| Default page size | **5 records** |
| Maximum page size | 100 records |
| Total sample records | 50 |
| Timestamp window | Rolling ~48 hours behind current time |

---

## Base URL

```
https://<FunctionAppName>.azurewebsites.net/api
```

The exact `<FunctionAppName>` is output by the ARM template deployment as **`FunctionAppName`**
and **`FunctionAppUrl`**.

---

## Authentication

All endpoints require an **API key** passed in a request header.

| Header | Required | Description |
|---|---|---|
| `X-API-Key` | **Yes** | The API key provisioned at deployment time via the `ApiKey` ARM parameter. |

Missing or incorrect keys return HTTP `401 Unauthorized`.

> **Security note:** The API key is stored as an encrypted Azure Function App setting (`NETWORK_LOG_API_KEY`)
> and is never exposed in logs or responses.

### Example

```http
GET /api/GetNetworkLogs?page=1&pageSize=5 HTTP/1.1
Host: <FunctionAppName>.azurewebsites.net
X-API-Key: your-api-key-here
```

---

## Common Request Headers

| Header | Required | Value | Description |
|---|---|---|---|
| `X-API-Key` | **Yes** | `<api-key>` | Authentication key |
| `Content-Type` | For POST | `application/json` | Only needed if sending a request body |

---

## Common Response Headers

Every response includes the following headers:

| Header | Description |
|---|---|
| `Content-Type` | `application/json` |
| `X-Request-ID` | UUID uniquely identifying this server-side request. Use for correlation/debugging. |

The **`GET /api/GetNetworkLogs`** endpoint additionally returns:

| Header | Description |
|---|---|
| `X-Total-Count` | Total number of matching records (after any `since` filter) |
| `X-Page` | Current page number (1-based) |
| `X-Page-Size` | Number of records per page |
| `X-Total-Pages` | Total number of pages |

---

## Endpoints

---

### GET /api/GetNetworkLogs

Returns a paginated list of network activity log records.

**URL**

```
GET /api/GetNetworkLogs
```

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `page` | integer | No | `1` | 1-based page number to retrieve. |
| `pageSize` | integer | No | `5` | Number of records per page. Minimum `1`, maximum `100`. |
| `since` | string (ISO 8601) | No | *(none)* | Return only records where `timestamp >= since`. Format: `YYYY-MM-DDTHH:MM:SSZ`. Used for incremental/delta pulls. |

#### Request Example – First Page

```http
GET /api/GetNetworkLogs?page=1&pageSize=5 HTTP/1.1
Host: <FunctionAppName>.azurewebsites.net
X-API-Key: your-api-key-here
```

#### Request Example – Incremental Pull

```http
GET /api/GetNetworkLogs?page=1&pageSize=5&since=2025-01-15T08:00:00Z HTTP/1.1
Host: <FunctionAppName>.azurewebsites.net
X-API-Key: your-api-key-here
```

#### Response – 200 OK

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Request-ID: 3fa85f64-5717-4562-b3fc-2c963f66afa6
X-Total-Count: 50
X-Page: 1
X-Page-Size: 5
X-Total-Pages: 10
```

```json
{
  "status": "success",
  "metadata": {
    "totalCount": 50,
    "page": 1,
    "pageSize": 5,
    "totalPages": 10,
    "hasNextPage": true,
    "nextLink": "https://<FunctionAppName>.azurewebsites.net/api/GetNetworkLogs?page=2&pageSize=5",
    "hasPreviousPage": false,
    "previousLink": null
  },
  "data": [
    {
      "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "timestamp": "2025-01-13T10:00:00Z",
      "sourceIp": "10.0.1.15",
      "destinationIp": "151.101.1.140",
      "sourcePort": 52341,
      "destinationPort": 443,
      "protocol": "TCP",
      "action": "ALLOW",
      "bytesIn": 1240,
      "bytesOut": 87654,
      "packets": 62,
      "durationMs": 345,
      "networkZone": "internal",
      "deviceId": "fw-001",
      "deviceName": "Firewall-Primary",
      "ruleName": "AllowHTTPS",
      "severity": "Low",
      "category": "Web",
      "threatIndicator": null,
      "geoCountry": "US"
    }
  ]
}
```

#### Response – 401 Unauthorized

```json
{
  "status": "error",
  "code": 401,
  "message": "Unauthorized: missing or invalid X-API-Key header"
}
```

#### Response – 400 Bad Request

```json
{
  "status": "error",
  "code": 400,
  "message": "Invalid 'since' format. Use ISO 8601 (e.g. 2024-01-01T00:00:00Z)."
}
```

---

### POST /api/RefreshData

Triggers a data refresh job. After this call, the next request to `GetNetworkLogs` will return
records with timestamps anchored to the new current time (the API always generates timestamps
relative to the moment of each call, so data naturally appears fresh after a refresh).

No request body is required.

**URL**

```
POST /api/RefreshData
```

#### Request Example

```http
POST /api/RefreshData HTTP/1.1
Host: <FunctionAppName>.azurewebsites.net
X-API-Key: your-api-key-here
Content-Length: 0
```

#### Response – 200 OK

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Request-ID: 9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d
```

```json
{
  "status": "success",
  "message": "Data refresh completed. Record timestamps have been regenerated relative to the current time.",
  "jobId": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "refreshedAt": "2025-01-15T12:00:00Z",
  "recordCount": 50
}
```

#### Response – 401 Unauthorized

```json
{
  "status": "error",
  "code": 401,
  "message": "Unauthorized: missing or invalid X-API-Key header"
}
```

---

## Data Schema – NetworkLogRecord

Each record in the `data` array represents a single network flow/firewall event.

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | string (UUID) | No | Stable deterministic UUID for this record. Consistent across pages and calls — safe for deduplication. |
| `timestamp` | string (ISO 8601 UTC) | No | Event timestamp in `YYYY-MM-DDTHH:MM:SSZ` format. Records span roughly the last 48 hours relative to the current server time, oldest first. |
| `sourceIp` | string (IPv4) | No | Source IP address of the network flow. |
| `destinationIp` | string (IPv4) | No | Destination IP address of the network flow. |
| `sourcePort` | integer | No | Source port number (0 for ICMP). |
| `destinationPort` | integer | No | Destination port number (0 for ICMP). |
| `protocol` | string (enum) | No | Network protocol. Values: `TCP`, `UDP`, `ICMP`. |
| `action` | string (enum) | No | Firewall disposition. Values: `ALLOW`, `DENY`, `DROP`. |
| `bytesIn` | integer | No | Bytes received (inbound). `0` for blocked sessions. |
| `bytesOut` | integer | No | Bytes sent (outbound). `0` for blocked sessions. |
| `packets` | integer | No | Total packet count for the flow. |
| `durationMs` | integer | No | Flow duration in milliseconds. `0` for blocked sessions. |
| `networkZone` | string (enum) | No | Network segment. Values: `internal`, `dmz`, `external`. |
| `deviceId` | string | No | Identifier of the reporting device (e.g. `fw-001`). |
| `deviceName` | string | No | Human-readable device name (e.g. `Firewall-Primary`). |
| `ruleName` | string | No | Name of the firewall rule that matched this flow. |
| `severity` | string (enum) | No | Event severity. Values: `Low`, `Medium`, `High`, `Critical`. |
| `category` | string (enum) | No | Traffic category. Values: `Web`, `DNS`, `SSH`, `RDP`, `Email`, `Database`, `CloudStorage`, `VPN`, `NetworkOps`, `Recon`, `Malware`, `LateralMovement`. |
| `threatIndicator` | string \| null | Yes | Threat intelligence tag, if applicable. Examples: `BruteForce`, `C2Server`, `RDPBruteForce`, `PortScan`, `KnownScanner`, `LargeUpload`, `WannaCry`. `null` for benign events. |
| `geoCountry` | string \| null | Yes | ISO 3166-1 alpha-2 country code for the external IP (source or destination). `null` for internal-only flows. |

### Severity Distribution

| Severity | Count | Example categories |
|---|---|---|
| Low | 26 | Web, DNS, Email, VPN, NetworkOps |
| Medium | 7 | SSH (internal), Email, CloudStorage, RDP (internal) |
| High | 9 | SSH (blocked), Recon, LateralMovement, Database (unauthorized) |
| Critical | 8 | RDP (blocked), Malware C2, SMB scan, IRC Botnet |

### Action Distribution

| Action | Count |
|---|---|
| ALLOW | 30 |
| DENY | 20 |
| DROP | 0 |

---

## Pagination

The API uses **offset/page-based pagination**.

| Concept | Detail |
|---|---|
| Page numbering | 1-based (first page = `page=1`) |
| Default page size | `5` |
| Max page size | `100` |
| Navigate forward | Use `metadata.nextLink` (full URL) or manually increment `page` |
| Navigate backward | Use `metadata.previousLink` (full URL) or manually decrement `page` |
| End of data | `metadata.hasNextPage` is `false` and `metadata.nextLink` is `null` |
| Total count | Available in `metadata.totalCount` and `X-Total-Count` header |

### Full Traversal Example (10 pages × 5 records)

```
GET /api/GetNetworkLogs?page=1&pageSize=5   → metadata.nextLink → page=2
GET /api/GetNetworkLogs?page=2&pageSize=5   → metadata.nextLink → page=3
...
GET /api/GetNetworkLogs?page=10&pageSize=5  → metadata.hasNextPage = false
```

---

## Incremental Pull (Time-Based Filtering)

The `since` query parameter enables **delta/incremental ingestion**.

1. On the **initial full pull**, call without `since` and paginate through all pages.
2. Record the `timestamp` of the most recently ingested record.
3. On subsequent polls, supply that timestamp as `?since=<timestamp>` to retrieve only newer records.

```http
GET /api/GetNetworkLogs?page=1&pageSize=5&since=2025-01-15T08:00:00Z
```

- The `since` filter is applied **before** pagination, so `metadata.totalCount` reflects the filtered count.
- `nextLink` and `previousLink` automatically carry the `since` parameter forward.
- If no records match the filter, `metadata.totalCount` returns `0` and `data` is an empty array.

> **CCF Note:** Use the `timestamp` field as the CCF connector's **Last Cursor** or **Start Time** field.

---

## Error Responses

All errors return a JSON body with a consistent structure:

```json
{
  "status": "error",
  "code": <HTTP status code>,
  "message": "<human-readable description>"
}
```

| HTTP Status | Meaning |
|---|---|
| `400 Bad Request` | Invalid query parameter value (e.g. non-numeric `page`, malformed `since`). |
| `401 Unauthorized` | Missing or incorrect `X-API-Key` header. |
| `500 Internal Server Error` | Unexpected server-side error (check Application Insights for details). |

---

## CCF API Poller Connector Configuration

> This section is the primary reference for building a **Microsoft Sentinel Codeless Connector Framework (CCF)**
> connector that polls this API.

### Authentication Configuration

| CCF Setting | Value |
|---|---|
| Auth Type | `APIKey` |
| API Key Header Name | `X-API-Key` |
| API Key Value | *(the key provisioned at deployment)* |

### Poller / Request Configuration

| CCF Setting | Value |
|---|---|
| HTTP Method | `GET` |
| Endpoint Path | `/api/GetNetworkLogs` |
| Base URL | `https://<FunctionAppName>.azurewebsites.net` |

### Pagination Configuration

| CCF Setting | Value |
|---|---|
| Pagination Type | **Page-based** (offset paging) |
| Page Query Parameter | `page` |
| Page Size Query Parameter | `pageSize` |
| Default Page Size | `5` |
| Next Page Token Location | Response body: `metadata.nextLink` (full URL) |
| Has Next Page Field | Response body: `metadata.hasNextPage` (boolean) |
| Total Count Location | Response body: `metadata.totalCount` **or** response header `X-Total-Count` |
| Total Pages Location | Response body: `metadata.totalPages` **or** response header `X-Total-Pages` |
| Records Array Path | `data` |
| Last Page Condition | `metadata.hasNextPage == false` |

### Incremental / Delta Ingestion Configuration

| CCF Setting | Value |
|---|---|
| Time Field Name | `timestamp` |
| Time Field Format | ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`) |
| Start Time Query Parameter | `since` |
| Start Time Format | ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`) |

### Response Parsing

| CCF Setting | Value |
|---|---|
| Response Content Type | `application/json` |
| Events Array JSON Path | `$.data[*]` |
| Event Timestamp Path | `$.timestamp` |
| Unique ID Path | `$.id` (stable UUID – use for deduplication) |

### Rate Limiting / Throttling

This API does not enforce rate limiting. For production connector compatibility, configure:

| CCF Setting | Suggested Value |
|---|---|
| Request delay (ms) | `0` (no rate limit enforced) |
| Retry on 429 | Not applicable (API does not return 429) |

### Sample CCF Connector JSON Snippet

The following fragment illustrates the key connectivity settings for the CCF Data Connector manifest
(`<connectorDefinition>`):

```json
{
  "connectorUiConfig": {
    "title": "Network Log API",
    "publisher": "Custom",
    "descriptionMarkdown": "Ingests network activity log data from the Network Log API mock data source.",
    "graphQueriesTableName": "NetworkLogs_CL"
  },
  "pollingConfig": {
    "auth": {
      "authType": "APIKey",
      "APIKeyName": "X-API-Key",
      "APIKeyIdentifier": ""
    },
    "request": {
      "apiEndpoint": "https://<FunctionAppName>.azurewebsites.net/api/GetNetworkLogs",
      "httpMethod": "GET",
      "queryParameters": {
        "pageSize": "5"
      },
      "headers": {}
    },
    "paging": {
      "pagingType": "NextPageToken",
      "nextPageTokenJsonPath": "$.metadata.nextLink",
      "hasNextFlagJsonPath": "$.metadata.hasNextPage",
      "pageSize": 5,
      "pageSizeParamterName": "pageSize"
    },
    "response": {
      "eventsJsonPaths": ["$.data[*]"]
    }
  }
}
```

> **Note on incremental pulls:** To enable incremental polling, configure the CCF connector's
> `startTimeAttributeName` to `since` and `timeFormat` to `yyyy-MM-ddTHH:mm:ssZ`.
> The connector framework will automatically append `&since=<lastEvent.timestamp>` on subsequent runs.

---

## Deployment

### Prerequisites

- Azure subscription with Contributor access to a resource group
- A Log Analytics workspace (for Application Insights)
- The `NetworkLogAPI.zip` deployment package uploaded to a public URL (see [Packaging](#packaging-the-function-app))

### Deploy via Azure Portal (One-Click)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Frobermoriarty12%2FSentinel-CCF-Pull-Connector-Builder-Agent-Accelerator%2Fmain%2Fazuredeploy_NetworkLogAPI.json)

### Deploy via Azure CLI

```bash
az deployment group create \
  --resource-group <your-resource-group> \
  --template-file azuredeploy_NetworkLogAPI.json \
  --parameters \
      FunctionName="NetLogAPI" \
      ApiKey="<your-strong-api-key>" \
      AppInsightsWorkspaceResourceID="/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.OperationalInsights/workspaces/<workspace-name>" \
      PackageUrl="https://raw.githubusercontent.com/robertmoriarty12/Sentinel-CCF-Pull-Connector-Builder-Agent-Accelerator/main/AzureFunctionNetworkLogAPI/NetworkLogAPI.zip"
```

### ARM Template Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `FunctionName` | string | No | `NetLogAPI` | Short prefix for all resource names. A unique suffix is appended automatically. Max 11 chars. |
| `ApiKey` | securestring | **Yes** | *(none)* | The API key callers must supply in `X-API-Key`. Use a strong random string (≥32 chars recommended). |
| `AppInsightsWorkspaceResourceID` | string | **Yes** | *(none)* | Full Resource ID of the Log Analytics workspace for Application Insights. |
| `PackageUrl` | string | No | GitHub placeholder | Public URL of `NetworkLogAPI.zip` on GitHub. Update after committing the zip. |
| `FunctionAppLocation` | string | No | Resource group location | Azure region for all deployed resources. |

### ARM Template Outputs

| Output | Description |
|---|---|
| `FunctionAppName` | The fully resolved Function App name (with unique suffix). |
| `FunctionAppUrl` | Base HTTPS URL of the Function App. |
| `GetNetworkLogsEndpoint` | Full URL for the `GetNetworkLogs` endpoint. |
| `RefreshDataEndpoint` | Full URL for the `RefreshData` endpoint. |

---

## Packaging the Function App

The ARM template uses `WEBSITE_RUN_FROM_PACKAGE` to deploy the function code from a zip file hosted on GitHub.

### Creating the Zip

From the `AzureFunctionNetworkLogAPI/` directory:

**PowerShell (Windows):**
```powershell
Compress-Archive -Path .\AzureFunctionNetworkLogAPI\* -DestinationPath .\AzureFunctionNetworkLogAPI\NetworkLogAPI.zip
```

**Bash / macOS / Linux:**
```bash
cd AzureFunctionNetworkLogAPI
zip -r NetworkLogAPI.zip function_app.py host.json requirements.txt
```

The zip must contain these three files at the **root** of the archive (no sub-folder):

```
NetworkLogAPI.zip
├── function_app.py
├── host.json
└── requirements.txt
```

### Publishing to GitHub

1. Commit `NetworkLogAPI.zip` to your repository.
2. The raw file URL is already set as the default: `https://raw.githubusercontent.com/robertmoriarty12/Sentinel-CCF-Pull-Connector-Builder-Agent-Accelerator/main/AzureFunctionNetworkLogAPI/NetworkLogAPI.zip`.
3. Pass that URL as the `PackageUrl` ARM parameter at deployment time.

> After updating the zip in GitHub, you can force the running Function App to reload it without redeployment:
> ```bash
> az webapp restart --name <FunctionAppName> --resource-group <your-rg>
> ```
