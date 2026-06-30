# CrowdStrike Falcon Adversary Intelligence – Data Connector

## **Summary**

This Microsoft Sentinel data connector enables ingestion of **threat intelligence indicators** from the **CrowdStrike Falcon Intelligence** API. It fetches indicators of compromise (IOCs), converts them to **STIX 2.1** format, and uploads them to the Microsoft Sentinel threat intelligence store.

The connector runs as an **Azure Function App** on a 10-minute timer trigger, giving security teams continuously updated, high-confidence threat intelligence to power analytics, hunting, and incident detection.

---

## **Features**

- Connects to the **CrowdStrike Falcon Intelligence REST API** using OAuth 2.0 client credentials authentication.
- Converts CrowdStrike indicators to **STIX 2.1** and uploads them via the Microsoft Sentinel threat intelligence upload API.
- Supports a wide range of indicator types: file hashes (MD5/SHA-1/SHA-256), URLs, domains, IP addresses, mutexes, file names, email addresses, usernames, and wallet/coin addresses.
- Maps CrowdStrike `malicious_confidence` (high/medium/low) to STIX confidence scores (85/60/30).
- Uses incremental, marker-based pagination with **state persistence** in an Azure File Share so each run resumes where the previous one left off.
- Time-aware batching: exits gracefully before the next execution window to prevent overlapping runs.

---

## **Prerequisites**

1. A valid **CrowdStrike Falcon** tenant with an **Intelligence** subscription.
2. An **API Client** configured in CrowdStrike Falcon with:
   - **Client ID**
   - **Client Secret**
   - **Base URL** (region-specific)
   - The `indicators:read` API scope.
3. An **Azure AD application** (service principal) used to authenticate to the Microsoft Sentinel threat intelligence upload API, with:
   - **Tenant ID**
   - **Client ID**
   - **Client Secret**
   - The **Microsoft Sentinel Contributor** role assigned on the target workspace.
4. Access to an Azure subscription with **Microsoft Sentinel** enabled and permissions to deploy a Function App.

---

## **Generating CrowdStrike Falcon API Credentials**

### **1. Access the Falcon Console**
1. Sign into the **CrowdStrike Falcon console**.
2. Navigate to **Support & Resources** → **API clients and keys**.

### **2. Create API Client**
1. Click **Create/Add new API client**.
2. Provide a descriptive **name** and **description** for the connector.
3. Grant the **`indicators:read`** scope.
4. Note the **Client ID** and **Client Secret** (the secret is displayed only once).

### **3. Identify Your Base URL**

| **Region** | **Base URL** |
|------------|--------------|
| US-1 | `https://api.crowdstrike.com` |
| US-2 | `https://api.us-2.crowdstrike.com` |
| EU-1 | `https://api.eu-1.crowdstrike.com` |
| US-GOV-1 | `https://api.laggar.gcw.crowdstrike.com` |

---

## **Deployment Parameters**

When deploying the connector, you'll provide the following parameters:

| **Parameter** | **Required** | **Description** |
|---------------|:---:|-----------------|
| `FunctionName` | Yes | A name for the deployed Function App. |
| `CrowdStrikeClientId` | Yes | CrowdStrike API client ID. |
| `CrowdStrikeClientSecret` | Yes | CrowdStrike API client secret. |
| `CrowdStrikeBaseUrl` | Yes | Region-specific CrowdStrike API base URL (see table above). |
| `WorkspaceId` | Yes | Microsoft Sentinel workspace ID. |
| `TenantId` | Yes | Azure AD tenant ID. |
| `AadClientId` | Yes | Azure AD application client ID. |
| `AadClientSecret` | Yes | Azure AD application client secret. |
| `Indicators` | Yes | Comma-separated indicator types to ingest (e.g. `url,hash_md5,domain,ip_address`). |
| `LookBackDays` | No | Time window (in days) used on the first run only. Default `1`, maximum `60`. |

### **Supported indicator types**

The `Indicators` parameter accepts any combination of the following types:

`hash_md5`, `hash_sha256`, `hash_sha1`, `url`, `domain`, `ip_address`, `mutex_name`, `password`, `file_name`, `email_address`, `username`, `persona_name`, `ip_address_block`, `coin_address`, `bitcoin_address`.

### **Optional application settings**

These can be set as Application Settings on the Function App after deployment:

| **Setting** | **Default** | **Description** |
|-------------|:---:|-----------------|
| `VALIDUNTIL` | `20m` | Duration string (`m`, `h`, or `d` — e.g. `20m`, `2h`, `7d`) that sets the STIX `valid_until` field on uploaded indicators. |

### **Optional: VNet integration**

By default the Function App and its storage account are publicly accessible. For a network-isolated deployment, the ARM template can provision a Virtual Network, integrate the Function App with it, and route storage access through private endpoints. Set `EnableVNetIntegration` to `true` to enable this; all other VNet parameters are ignored when it is `false`. Be aware that this will increase your Azure costs through private endpoints and a new consumption plan.

| **Parameter** | **Default** | **Description** |
|---------------|:---:|-----------------|
| `EnableVNetIntegration` | `false` | Set to `true` to deploy a VNet and integrate the Function App with it. When `false`, VNet resources are skipped and storage remains publicly accessible. |
| `VNetAddressPrefix` | `10.0.0.0/16` | Address space for the Virtual Network in CIDR notation. |
| `SubnetName` | `snet-functionapp` | Name of the subnet delegated to the Function App for VNet integration. |
| `SubnetAddressPrefix` | `10.0.0.0/24` | Address prefix for the Function App integration subnet. Must be within the VNet address space. Minimum `/28`. |
| `PrivateEndpointSubnetName` | `snet-privateendpoints` | Name of the subnet used for storage private endpoints. Must not be delegated. |
| `PrivateEndpointSubnetAddressPrefix` | `10.0.1.0/24` | Address prefix for the private endpoint subnet. Must be within the VNet address space and not overlap with the Function App subnet. |
| `UseExistingDnsZones` | `false` | Set to `true` when the private DNS zones and their VNet links already exist (e.g. from a prior deployment). Skips creating DNS zones and VNet links to avoid conflicts. |

---

## **Deployment Instructions**

### **1. Open the Connector Page**

1. Go to **Microsoft Sentinel** → **Data Connectors**.
2. Search for and select **CrowdStrike Falcon Adversary Intelligence (using Azure Functions)**.
3. Click **Open connector page**.

### **2. Complete the Prerequisite Steps**

On the connector page, complete the configuration steps:

- **STEP 1 — Generate CrowdStrike API credentials.** Create an API client with the **Indicators (Falcon Intelligence)** scope set to **read**, and note the **Client ID**, **Client Secret**, and region-specific **Base URL**.
- **STEP 2 — Register a Microsoft Entra application** with a client secret, and assign it the **Microsoft Sentinel Contributor** role on the target Log Analytics workspace. Note the **Tenant ID**, **Client ID**, and **Client Secret**.

> **IMPORTANT:** Before deploying, copy your **Workspace ID** from the connector page.

### **3. Deploy the Connector**

1. Click the **Deploy to Azure** button on the connector page.
2. On the custom deployment page, select the **Subscription**, **Resource Group**, and **Region** to deploy into.
3. Provide the following parameters: `CrowdStrikeClientId`, `CrowdStrikeClientSecret`, `CrowdStrikeBaseUrl`, `WorkspaceId`, `TenantId`, `Indicators`, `AadClientId`, `AadClientSecret`, `LookBackDays`.
4. Click **Review + create** → **Create**.

---

## **Post-Deployment Steps**

### **1. Verify Execution**
- In the Azure portal, open the deployed Function App and confirm the timer-triggered function runs every 10 minutes without errors.
- Review the function logs in **Application Insights** for the execution summary (e.g. *"Execution completed: processed N indicators across M batches"*).

### **2. Verify Threat Intelligence Ingestion**
Confirm indicators are flowing into Microsoft Sentinel:

1. Go to **Microsoft Sentinel** → **Threat Intelligence**, and filter by source **CrowdStrike Falcon Adversary Intelligence**.
2. Or run the following query under **Logs**:

```kql
ThreatIntelIndicators
| where SourceSystem == "CrowdStrike Falcon Adversary Intelligence"
| take 10
```

> **Note:** The first run uses `LookBackDays` to establish a starting window. Subsequent runs ingest only new, high-confidence indicators newer than the last persisted marker.

---

## **Troubleshooting**

### **1. Authentication Errors (401 Unauthorized)**
- **Cause**: Incorrect credentials or insufficient API scopes.
- **Solution**:
  - Verify the CrowdStrike Client ID/Secret and that the `indicators:read` scope is granted.
  - Verify the Azure AD Tenant ID, Client ID, and Client Secret.

### **2. No Indicators Ingested**
- **Cause**: Incorrect Base URL, no new indicators in the lookback window, or network connectivity issues.
- **Solution**:
  - Confirm the Base URL matches your CrowdStrike region.
  - Confirm the `Indicators` list contains valid, subscribed indicator types.
  - Check outbound connectivity from the Function App to the CrowdStrike and Sentinel endpoints.

### **3. Function Exits Early**
- **Cause**: Expected behavior — the function exits when fewer than 60 seconds remain before the next 10-minute execution window.
- **Solution**: No action needed; processing resumes from the persisted marker on the next run.

### **Support Resources**
- **CrowdStrike API Documentation**: Available in the Falcon console under API documentation.
- **Microsoft Sentinel Documentation**: [Microsoft Learn - Sentinel Connectors](https://learn.microsoft.com/azure/sentinel/).
- **Connector Logs**: Available in **Application Insights** for the deployed Function App.

---
