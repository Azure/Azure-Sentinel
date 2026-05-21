# 42Crunch API Protection — Migration Guide
## From Legacy HTTP Data Collector API to CCF Push Connector

---

## Overview

This guide describes how to migrate the 42Crunch API Protection integration from the **legacy HTTP Data Collector API** (deprecated, Workspace ID + Primary Key) to the **new CCF Push Connector** (OAuth2 Entra ID + DCE/DCR). It covers architecture changes, deployment steps, sample deployment testing, and analytic rule updates.

> **Docker container replacement:** The legacy integration already runs entirely in Docker — both the `42crunch/firewall` container and the `42c-fw-2la` forwarder container. The migration is a **low-friction container swap**: you keep your existing firewall container completely unchanged and replace only the forwarder container. No new infrastructure is required.

> **E2E validated:** This migration has been end-to-end tested and confirmed working — data flows correctly into the `FortyTwoCrunchAPIProtectionV2_CL` table in Microsoft Sentinel.

---

## Architecture Comparison

### Legacy Architecture (42c-fw-2la)

```
┌─────────────────────────────────────┐
│  42Crunch API Firewall (Docker)     │
│  42crunch/firewall or               │
│  42crunch/secured-httpbin           │
│                                     │
│  Writes line-delimited JSON logs to │
│  /opt/guardian/logs/<node>/         │
│    api-<uuid>.transaction.log       │
│    api-unknown.transaction.log      │
└──────────────────┬──────────────────┘
                   │ shared Docker volume
┌──────────────────▼──────────────────┐
│  42c-fw-2la container               │
│  (42Crunch's official forwarder)    │
│                                     │
│  Auth: Workspace ID + Primary Key   │
│        (HMAC-SHA256, deprecated)    │
│                                     │
│  POST → HTTP Data Collector API     │
│  https://<workspaceId>.ods          │
│  .opinsights.azure.com/api/logs     │
│  ?api-version=2016-04-01            │
└──────────────────┬──────────────────┘
                   │ HTTPS
┌──────────────────▼──────────────────┐
│  Log Analytics (deprecated API)     │
│  Table: apifirewall_log_1_CL        │
│  17 columns with type suffixes:     │
│  UUID_g, Status_d, Source_IP_s,     │
│  Non_blocking_mode_b, Timestamp_t…  │
└─────────────────────────────────────┘
```

### New CCF Push Architecture

```
┌─────────────────────────────────────┐
│  42Crunch API Firewall (Docker)     │
│  Same image — unchanged             │
│                                     │
│  Writes same log files to disk      │
└──────────────────┬──────────────────┘
                   │ shared Docker volume
┌──────────────────▼──────────────────┐
│  ccf-forwarder (new container)      │
│  Replaces 42c-fw-2la                │
│                                     │
│  Auth: OAuth2 Client Credentials    │
│        Entra ID → JWT bearer token  │
│        login.microsoftonline.com    │
│                                     │
│  POST → Azure Monitor DCE/DCR       │
│  https://<dce>.ingest.monitor       │
│  .azure.com/dataCollectionRules/    │
│  <dcr>/streams/Custom-Forty...      │
│  ?api-version=2023-01-01            │
└──────────────────┬──────────────────┘
                   │ HTTPS
┌──────────────────▼───────────────────┐
│  Azure Monitor DCE + DCR             │
│  (ingestion-time transform)          │
│                                      │
│  Table: FortyTwoCrunchAPIProtectionV2│
│         _CL                          │
│  17 PascalCase columns:              │
│  Uuid, Status, SourceIp,             │
│  NonBlockingMode, Timestamp…         │
└──────────────────────────────────────┘
```

---

## What Changes for the Customer

| Aspect | Legacy | New CCF Push |
|---|---|---|
| API Firewall container | `42crunch/firewall` or `42crunch/secured-httpbin` | **Unchanged — same image** |
| Forwarder container | `42crunch/42c-fw-2la` | `ccf-forwarder` (custom, in this repo) |
| Auth env vars | `WORKSPACE_ID` + `WORKSPACE_KEY` | `TENANT_ID` + `CLIENT_ID` + `CLIENT_SECRET` + `DCE_ENDPOINT` + `DCR_IMMUTABLE_ID` |
| Sentinel setup | Nothing (table auto-created on first ingest) | Deploy ARM template first (creates DCE, DCR, table, Entra app registration) |
| Table name | `apifirewall_log_1_CL` | `FortyTwoCrunchAPIProtectionV2_CL` |
| Column naming | `_s`, `_d`, `_b`, `_t`, `_g` type suffixes | PascalCase (e.g. `SourceIp`, `Status`, `Timestamp`) |
| Ingest API | HTTP Data Collector API v2016 (deprecated) | DCE/DCR REST API v2023 (current) |
| Auth model | HMAC-SHA256 shared key (deprecated) | OAuth2 Client Credentials (Entra ID) |

---

## Column Mapping: Legacy → New CCF

| Legacy Column (`apifirewall_log_1_CL`) | New Column (`FortyTwoCrunchAPIProtectionV2_CL`) | Notes |
|---|---|---|
| `UUID_g` | `Uuid` | GUID → string |
| `Timestamp_t` | `Timestamp` | datetime |
| `Instance_Name_s` | `InstanceName` | string |
| `Hostname_s` | `Hostname` | string |
| `Source_IP_s` | `SourceIp` | string |
| `Source_Port_d` | `SourcePort` | double → int |
| `Destination_Port_d` | `DestinationPort` | double → int |
| `URI_Path_s` | `UriPath` | string |
| `Query_s` | `Query` | string |
| `Status_d` | `Status` | double → int |
| `Error_Message_s` | `ErrorMessage` | string |
| `Errors_s` | `Errors` | JSON string |
| `Request_Header_s` | `RequestHeader` | JSON string |
| `Response_Header_s` | `ResponseHeader` | JSON string |
| `API_ID_g` | `ApiId` | GUID → string |
| `Non_blocking_mode_b` | `NonBlockingMode` | bool |
| `Type` | `EventType` | string (renamed to avoid KQL reserved word) |

---

## Prerequisites

Before starting:

1. **Microsoft Sentinel workspace** with Contributor access
2. **Azure subscription** with permissions to create:
   - Data Collection Endpoints (DCE)
   - Data Collection Rules (DCR)
   - Log Analytics custom tables
   - Entra ID app registrations
3. **Docker** — already installed if you are using the legacy connector (both `42crunch/firewall` and `42c-fw-2la` are Docker containers)
4. **Azure CLI** or access to Azure Portal

---

## Step 1 — Deploy the CCF ARM Template

1. Open **Microsoft Sentinel** → **Data connectors**
2. Find **42Crunch API Protection (Push Connector via Codeless Connector Framework)**
3. Click **Open connector page**
4. Under **Configuration**, click **Deploy 42Crunch API Protection connector resources**
5. You will be prompted a confirmation dialog, please click OK to proceed
6. After connector gets deployer, you will be shown copiable text with: 
  - Tenant ID (Directory ID)
  - Entra App Registration Application ID
  - Entra App Registration Secret (save it as it will be shown only one time)
  - Data Collection Endpoint Url
  - Data Collection Rule Immutable ID
  - Stream Name (FortyTwoCrunchAPIProtectionV2)
  **Important**. Connector will remain disconnected for a while till data gets ingested into Sentinel. then connector will remain connected.

This creates:
- A **Data Collection Endpoint (DCE)** — the HTTPS ingestion URL
- A **Data Collection Rule (DCR)** — defines the stream schema and routing
- The **`FortyTwoCrunchAPIProtectionV2_CL`** Log Analytics table
- An **Entra ID app registration** with `Monitoring Metrics Publisher` role

6. After deployment completes, copy these values from the deployment outputs:
   - `DCE_ENDPOINT` — e.g. `https://xxx.eastus-1.ingest.monitor.azure.com`
   - `DCR_IMMUTABLE_ID` — e.g. `dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - `TENANT_ID` — your Azure tenant ID
   - `CLIENT_ID` — the Entra app client ID
   - `CLIENT_SECRET` — the Entra app client secret (**store securely, never commit to git**)

---

## Step 2 — Set Up the Sample Deployment

> **Context:** If you are an existing customer, you already have a `docker-compose.yml` (or Helm chart) running your `42crunch/firewall` and `42c-fw-2la` containers. This step shows the equivalent configuration using `ccf-forwarder` in place of `42c-fw-2la`. The firewall container and its shared log volume remain exactly the same.

The sample deployment is in `sample-deployment/` and contains:

```
sample-deployment/
  docker-compose.yml       ← 2 services: api-firewall + ccf-forwarder
  .env.example             ← template for non-secret config values
  ccf-forwarder/
    forwarder.py           ← reads guardian logs, pushes to DCE/DCR
    Dockerfile             ← python:3.11-alpine
    requirements.txt       ← requests==2.31.0
```

### 2a — Create the `.env` file

```powershell
cd "C:\path\to\42Crunch API Protection\sample-deployment"
Copy-Item .env.example .env
notepad .env
```

Fill in the non-secret values and save:

```env
TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
DCE_ENDPOINT=https://xxx.eastus-1.ingest.monitor.azure.com
DCR_IMMUTABLE_ID=dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> **Security:** Do NOT put `CLIENT_SECRET` in the `.env` file. It is passed as a shell environment variable in the next step so it is never written to disk.

### 2b — Start the stack

Set the secret securely at the prompt (it will not appear in shell history):

```powershell
$env:CLIENT_SECRET = (Read-Host -Prompt "CLIENT_SECRET" -AsSecureString | ConvertFrom-SecureString -AsPlainText)
docker compose up --build
```

Docker Compose automatically merges `$env:CLIENT_SECRET` from the shell with the `.env` file.

Expected startup output:

```
api-firewall-1   | API Firewall started
ccf-forwarder-1  | INFO 42Crunch CCF Log Forwarder starting
ccf-forwarder-1  | INFO   DCE_ENDPOINT     = https://...
ccf-forwarder-1  | INFO   DCR_IMMUTABLE_ID = dcr-...
ccf-forwarder-1  | INFO   DCR_STREAM_NAME  = Custom-FortyTwoCrunchAPIProtectionV2_CL
ccf-forwarder-1  | INFO   TICK_INTERVAL    = 10s
```

> **Note:** The sample deployment runs in **online mode** — the firewall connects to the 42Crunch platform using a `PROTECTION_TOKEN` (set in `.env`). This is how the product works in real customer deployments.

### 2d — Test with a real 42Crunch Firewall Protection Token

The sample deployment uses [kennethreitz/httpbin](https://hub.docker.com/r/kennethreitz/httpbin) as the backend API and `42crunch/apifirewall:latest` as the firewall. httpbin is a simple HTTP echo service that is useful for generating realistic API traffic.

#### Step 1 — Create a 42Crunch account and a Collection

1. Sign up for a free trial at [https://platform.42crunch.com](https://platform.42crunch.com)
   - Enterprise customers: use your organisation's URL (e.g. `https://us.42crunch.cloud`)
   - Trial customers: [https://platform.42crunch.com](https://platform.42crunch.com)

2. After logging in, click **+ New Collection** and give it a name (e.g. `httpbin-test`)

   > A **Collection** is just a folder for grouping APIs. You need at least one before you can add an API.

#### Step 2 — Import an OpenAPI Specification

The 42Crunch platform needs an OpenAPI spec (OAS) to know what your API is allowed to do. For testing with httpbin you can use any valid Swagger 2.0 / OpenAPI 3.0 file.

1. Inside your collection, click **+ New API**
2. Choose **Import from file** (or paste the spec directly)
3. Upload your OAS JSON/YAML file
4. The platform will score the spec — a higher score means better security coverage. For testing purposes, any valid spec works.

#### Step 3 — Create a Protection and get the Firewall Token

1. Open the API you just imported
2. Click the **Protection** tab
3. Click **Create Protection**
4. Inside the protection, click **Firewall Instances** → **Add instance**
5. Give it a name (e.g. `local-docker`) and click **Create**
6. Copy the **Protection Token** shown on screen

   > ⚠️ The token is shown **only once**. Copy it immediately. If lost, delete the instance and create a new one.

7. Note your **platform hostname** — visible in the browser address bar, e.g.:
   - `protection.42crunch.com:8001` (enterprise)
   - `protection.trials.42crunch.com:8001` (trials account)

#### Token types — do not confuse these

| Token type | Where found | Used for |
|---|---|---|
| **Firewall Protection Token** | Protect → API → Protection → Firewall Instances | `PROTECTION_TOKEN` env var on the firewall container |
| IDE / VS Code token | Account settings → API tokens | VS Code extension only — **not valid** for the firewall |
| API key | Account settings | Platform REST API calls — not for the firewall |

#### Step 4 — Update `.env` and switch to online mode

Add `PROTECTION_TOKEN` to your `.env` file:

```env
TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
DCE_ENDPOINT=https://xxx.eastus-1.ingest.monitor.azure.com
DCR_IMMUTABLE_ID=dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PROTECTION_TOKEN=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

The `docker-compose.yml` in this repo is already configured for online mode with `kennethreitz/httpbin` as the backend and `42crunch/apifirewall:latest` as the firewall:

```yaml
services:
  api:                                  # httpbin — the backend API being protected
    image: kennethreitz/httpbin
    expose:
      - "80"

  api-firewall:                         # production firewall image (actively maintained)
    image: 42crunch/apifirewall:latest
    ports:
      - "8080:8080"
    command: ["/bin/squire", "-platform", "protection.trials.42crunch.com:8001"]
    environment:
      - PROTECTION_TOKEN=${PROTECTION_TOKEN}
      # - PLATFORM_CONNECTIVITY=NONE   # comment this out for online mode
      - TARGET_URL=http://api:80
      - LISTEN_NO_TLS=true
      - LISTEN_PORT=8080
    depends_on:
      - api
```

> **Note on the firewall image:** The sample uses `42crunch/apifirewall:latest` (the current production image, actively maintained). Do **not** use `42crunch/secured-httpbin` — that image is several years old and contains an expired TLS certificate that prevents it from connecting to the platform.

#### Step 5 — Restart the stack

```powershell
docker compose down
docker volume rm sample-deployment_firewall-logs sample-deployment_forwarder-state
$env:CLIENT_SECRET = (Read-Host -Prompt "CLIENT_SECRET" -AsSecureString | ConvertFrom-SecureString -AsPlainText)
docker compose up
```

The firewall will connect to the 42Crunch platform at startup. Expected logs:

```
api-firewall-1  | Dialin to 'protection.trials.42crunch.com:8001'...
api-firewall-1  | Connected to 'protection.trials.42crunch.com:8001'
api-firewall-1  | Platform connected
api-firewall-1  | New configuration persisted
api-firewall-1  | API Firewall started
ccf-forwarder-1 | INFO 42Crunch CCF Log Forwarder starting
```

### 2c — Troubleshooting: Docker Desktop network issues

If the forwarder logs show `[Errno 101] Network unreachable` when connecting to `login.microsoftonline.com`, the container has no internet access. This is fixed by adding explicit DNS to the `ccf-forwarder` service in `docker-compose.yml`:

```yaml
ccf-forwarder:
  dns:
    - 8.8.8.8
    - 8.8.4.4
```

This is already included in the `docker-compose.yml` in this repo.

To verify connectivity from the container:

```powershell
docker exec sample-deployment-ccf-forwarder-1 wget -qO- https://login.microsoftonline.com 2>&1 | Select-Object -First 5
# Expected: "wget: server returned error: HTTP/1.1 400 Bad Request"
# A 400 response means the container CAN reach the internet (server responded).
```

---

## Step 3 — Generate Traffic and Verify

### 3a — Send test requests through the firewall

Open a new terminal and send HTTP requests to the firewall (port 8080):

```powershell
curl http://localhost:8080/get
curl http://localhost:8080/get
curl http://localhost:8080/status/429
curl http://localhost:8080/status/500
```

### 3b — Confirm the forwarder pushed events

Within 10 seconds (one tick), check the forwarder logs:

```powershell
docker logs sample-deployment-ccf-forwarder-1 --tail 20
```

Expected output:

```
2026-xx-xxTxx:xx:xx INFO Obtained new access token (expires in 3599s)
2026-xx-xxTxx:xx:xx INFO Pushed 4 event(s) → HTTP 204
```

`HTTP 204` confirms the events were accepted by Azure Monitor.

### 3c — Verify data in Sentinel

Wait 2–5 minutes for Log Analytics ingestion, then run in the Sentinel query editor:

```kql
FortyTwoCrunchAPIProtectionV2_CL
| where TimeGenerated > ago(15m)
| project TimeGenerated, SourceIp, UriPath, Status, EventType, InstanceName
| take 20
```

### 3d — Verify with a real Firewall Token

If you completed Step 2d and are running with a real firewall token, generate more meaningful traffic by using the API protected by the 42Crunch firewall. The firewall validates requests against your OpenAPI spec and returns:

- `200` — valid request, passed through to backend
- `400` / `422` — request blocked (schema violation)
- `401` / `403` — authentication/authorisation violation (e.g. missing JWT)
- `429` — rate limit exceeded

Example requests to trigger different event types:

```powershell
# Valid request (200)
curl http://localhost:8080/get

# Missing auth header — triggers JWT validation alert
curl http://localhost:8080/api/login -X POST -H "Content-Type: application/json" -d '{"user":"test","pass":"test"}'

# Rapid repeated requests — triggers rate limiting alert
1..25 | ForEach-Object { curl -s http://localhost:8080/api/login > $null }

# Invalid path — triggers Kiterunner detection (if > 500 404s)
1..10 | ForEach-Object { curl -s http://localhost:8080/nonexistent-$_ > $null }
```

Then verify the analytic rules fire in Sentinel:

```kql
// Check all recent events with their types
FortyTwoCrunchAPIProtectionV2_CL
| where TimeGenerated > ago(15m)
| summarize Count = count() by Status, UriPath, InstanceName
| order by Count desc

// JWT validation failures
FortyTwoCrunchAPIProtectionV2_CL
| where TimeGenerated > ago(15m)
| where ErrorMessage has "x-access-token"
| project TimeGenerated, SourceIp, UriPath, Status, ErrorMessage

// Rate limiting events
FortyTwoCrunchAPIProtectionV2_CL
| where TimeGenerated > ago(15m)
| where Status == 429
| project TimeGenerated, SourceIp, UriPath, InstanceName
```

---

## Step 4 — Update Analytic Rules

All 11 analytic rules in `Analytic Rules/` have been updated from the legacy table schema to the new CCF schema. The changes applied to every rule are:

### Changes per rule

| What changed | Before | After |
|---|---|---|
| Table name | `apifirewall_log_1_CL` | `FortyTwoCrunchAPIProtectionV2_CL` |
| Connector ID | `42CrunchAPIProtection` | `FortyTwoCrunchAPIProtection` |
| Data type | `apifirewall_log_1_CL` | `FortyTwoCrunchAPIProtectionV2_CL` |
| `Instance_Name_s` | `_s` string suffix | `InstanceName` |
| `Source_IP_s` | `_s` string suffix | `SourceIp` |
| `URI_Path_s` | `_s` string suffix | `UriPath` |
| `Status_d` | `_d` double suffix | `Status` |
| `Timestamp_t` | `_t` datetime suffix | `Timestamp` |
| `Error_Message_s` | `_s` string suffix | `ErrorMessage` |
| `Error_Step_s` | `_s` string suffix | `ErrorMessage` |
| `Hostname_s` | `_s` string suffix | `Hostname` |
| `project-away` columns | all old suffix names | all PascalCase names |
| `entityMappings` columns | `Source_IP_s`, `Hostname_s`, `Instance_Name_s` | `SourceIp`, `Hostname`, `InstanceName` |

### Updated rule files

| File | Rule Name | Tactic |
|---|---|---|
| `APIAccountTakeover.yaml` | API - Account Takeover | CredentialAccess, Discovery |
| `APIAnomalyDetection.yaml` | API - Anomaly Detection | Reconnaissance |
| `APIAPIScaping.yaml` | API - API Scraping | Reconnaissance, Collection |
| `APIBOLA.yaml` | API - BOLA | Exfiltration |
| `APIFirstTimeAccess.yaml` | API - Rate limiting (first-time access) | Discovery, InitialAccess |
| `APIInvalidHostAccess.yaml` | API - Invalid host access | Reconnaissance |
| `APIJWTValidation.yaml` | API - JWT validation | InitialAccess, CredentialAccess |
| `APIKiterunnerDetection.yaml` | API - Kiterunner detection | Reconnaissance, Discovery |
| `APIPasswordCracking.yaml` | API - Password Cracking | CredentialAccess |
| `APIRateLimiting.yaml` | API - Rate limiting | Impact |
| `APISuspiciousLogin.yaml` | API - Suspicious Login | CredentialAccess, InitialAccess |

### Example: APIJWTValidation.yaml before and after

**Before:**
```yaml
requiredDataConnectors:
  - connectorId: 42CrunchAPIProtection
    dataTypes:
      - apifirewall_log_1_CL
query: |
  apifirewall_log_1_CL
  | where TimeGenerated >= ago(5m)
  | where Error_Message_s has "missing [\"x-access-token\"]"
  | project-away Non_blocking_mode_b, Source_Port_d, ..., UUID_g
  | sort by TimeGenerated desc
entityMappings:
  - entityType: IP
    fieldMappings:
      - identifier: Address
        columnName: Source_IP_s
```

**After:**
```yaml
requiredDataConnectors:
  - connectorId: FortyTwoCrunchAPIProtection
    dataTypes:
      - FortyTwoCrunchAPIProtectionV2_CL
query: |
  FortyTwoCrunchAPIProtectionV2_CL
  | where TimeGenerated >= ago(5m)
  | where ErrorMessage has "missing [\"x-access-token\"]"
  | project-away NonBlockingMode, SourcePort, ..., Uuid
  | sort by TimeGenerated desc
entityMappings:
  - entityType: IP
    fieldMappings:
      - identifier: Address
        columnName: SourceIp
```

---

## Step 5 — Customer Migration Checklist

For customers already using the legacy connector, follow these steps:

- [ ] Deploy the new CCF ARM template (Step 1)
- [ ] Create a new Entra ID app registration client secret (or use the one from the deployment output)
- [ ] Update Docker Compose / Helm chart:
  - Remove `42c-fw-2la` service
  - Remove `WORKSPACE_ID` and `WORKSPACE_KEY` environment variables
  - Add `ccf-forwarder` service (from this repo's `sample-deployment/ccf-forwarder/`)
  - Add new env vars: `TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET`, `DCE_ENDPOINT`, `DCR_IMMUTABLE_ID`
- [ ] Keep the `42crunch/firewall` container unchanged — it writes the same log files
- [ ] Restart the stack and confirm `Pushed N event(s) → HTTP 204` in forwarder logs
- [ ] Verify `FortyTwoCrunchAPIProtectionV2_CL` receives data in Sentinel
- [ ] Redeploy the 11 updated analytic rules from `Analytic Rules/`
- [ ] Update any custom workbooks or queries that reference `apifirewall_log_1_CL` using the column mapping table above
- [ ] Decommission the old `42c-fw-2la` container once the new pipeline is confirmed working

---

## Security Notes

- **Never commit `CLIENT_SECRET` to git.** Always pass it via shell environment variable or a secret manager.
- **Rotate the client secret** periodically via Entra ID → App registrations → Certificates & secrets.
- In Kubernetes, store the secret as a `kubectl create secret generic` command (not in YAML files).
- In Docker Compose, use `$env:CLIENT_SECRET` in PowerShell or `read -rs` in bash — both avoid writing to disk.

---

## File Structure Reference

```
42Crunch API Protection/
  MIGRATION_GUIDE.md                    ← this file
  Analytic Rules/                       ← 11 updated rules (new schema)
    APIAccountTakeover.yaml
    APIAnomalyDetection.yaml
    APIAPIScaping.yaml
    APIBOLA.yaml
    APIFirstTimeAccess.yaml
    APIInvalidHostAccess.yaml
    APIJWTValidation.yaml
    APIKiterunnerDetection.yaml
    APIPasswordCracking.yaml
    APIRateLimiting.yaml
    APISuspiciousLogin.yaml
  Data Connectors/
    42CrunchAPIProtection.json          ← original legacy connector definition (reference only)
  sample-deployment/
    docker-compose.yml                  ← 2-service stack (api-firewall + ccf-forwarder)
    .env.example                        ← fill in non-secret values, CLIENT_SECRET via shell
    ccf-forwarder/
      forwarder.py                      ← reads guardian logs, pushes to DCE/DCR
      Dockerfile
      requirements.txt

ConnectorsGenerator/Connectors/
  42CrunchAPIProtectionConnectorDefinition.cs   ← CCF connector definition (PublicPreview)

ConnectorsGenerator/GeneratedDataConnectors/FortyTwoCrunchAPIProtectionV2/
  ConnectorDefinition.json
  DCR.json
  table_FortyTwoCrunchAPIProtectionV2.json
  mainTemplate.json
  createUiDefinition.json
```
