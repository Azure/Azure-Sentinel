# meshStack Event Logs Data Connector for Microsoft Sentinel

This solution provides a data connector to ingest meshStack Event Logs into Microsoft Sentinel using the Codeless Connector Framework (CCF) with OAuth2 authentication. 
meshStack is a cloud platform management solution that helps platform engineering teams build, operate, and scale internal developer platforms (IDPs).
See [meshcloud](https://meshcloud.io) for more information.

## Quick Start

### Prerequisites

- An existing **Log Analytics workspace** with **Microsoft Sentinel enabled**
- Appropriate permissions to:
  - Deploy ARM templates
  - Create Data Collection Endpoints
  - Configure Microsoft Sentinel data connectors
- A meshStack instance with Events API enabled
- Admin access to create meshStack API Keys

### 1. Deploy to Azure

**Note**: Azure Sentinel automatically creates a Data Collection Endpoint (DCE) once you add your first data connector. 
The DCE is named as `ASI-<worspace-uuid>`.

**Option A: Azure Portal**
1. Navigate to "Deploy a custom template"
2. Upload `Package/mainTemplate.json`
3. Select your subscription, resource group, and workspace
4. Deploy

**Option B: Azure CLI**
```bash
# Basic deployment (minimum required parameters)
az deployment group create \
  --resource-group <rg-name> \
  --template-file Package/mainTemplate.json \
  --parameters workspace=<workspace-name> \
               workspace-location=<workspace-region>

# Example with all parameters explicitly set
az deployment group create \
  --resource-group myResourceGroup \
  --template-file Package/mainTemplate.json \
  --parameters workspace=mySentinelWorkspace \
               workspace-location=eastus \
               resourceGroupName=myResourceGroup \
               subscription=12345678-1234-1234-1234-123456789abc \
               location=eastus
```

### 2. Configure Data Connector

1. In Azure Portal, go to **Microsoft Sentinel > Data connectors**
2. Search for **"meshStack Event Logs"**
3. Click **"Open connector page"**
4. Fill in the connection form:
   - **meshStack API URL**: `https://your-meshstack-instance.io`
   - **Client ID (Key ID)**: The **Key ID** from your meshStack API Key
   - **Client Secret (Key Secret)**: The **Key Secret** from your meshStack API Key
5. Toggle the **Connect** button to enable the connector

## Authentication Setup

### Understanding meshStack API Keys

When you create an API Key in meshStack, it provides **OAuth2 credentials**:
- `client_id`: OAuth2 client identifier (shown as **Key ID** in meshStack Admin Panel)
- `client_secret`: OAuth2 client secret (shown as **Key Secret** in meshStack Admin Panel)

These credentials are used in the OAuth2 client credentials flow:
1. Connector exchanges `client_id` + `client_secret` for an access token at `/api/login`
2. Access token is used in `Authorization: Bearer` header for API requests
3. Tokens are automatically refreshed when expired

### Creating an API Key in meshStack

1. Log in to your meshStack instance as administrator
2. Navigate to **Admin Panel > Access Control > API Keys**
3. Click **"Create API Key"**
4. Configure:
   - **Name**: `sentinel-event-logs`
   - **Workspace**: Select any workspace (key is bound here but can access all workspaces)
   - **Permission**: `Admin: List Event Logs in any Workspace`
5. Save and **copy both Key ID and Key Secret** - they won't be shown again!

**Important Notes:**
- The API Key provides **Key ID** (`client_id`) and **Key Secret** (`client_secret`)
- These are OAuth2 credentials, NOT a simple API key
- The permission `Admin: List Event Logs in any Workspace` allows cross-workspace access
- The API Key is bound to a workspace but this is administrative - the permission scope is global

## Event Schema

The connector creates a custom table `meshStackEventLogs_CL` with 8 columns:

| Column | Type | Description |
|--------|------|-------------|
| `TimeGenerated` | datetime | The timestamp (UTC) reflecting the time in which the event was generated |
| `EventTitle` | string | Event title |
| `EventDescription` | string | Event description |
| `EventType` | string | Event type identifier |
| `WorkspaceName` | string | meshStack workspace name |
| `EventContent` | dynamic | Event content with additional details |
| `AuthorIdentifier` | string | Author identifier extracted from author object |
| `AuthorType` | string | Author type extracted from author object |

## References

- [meshStack Events API](https://docs.meshcloud.io/api/mesh-event-log-list/)
- [meshStack OAuth2 Authentication](https://docs.meshcloud.io/api/authentication/api-keys/)
- [Microsoft Sentinel Codeless Connector](https://docs.microsoft.com/azure/sentinel/create-codeless-connector)

## Support

- **meshStack**: support@meshcloud.io or https://feedback.meshcloud.io/
- **Microsoft Sentinel**: https://github.com/Azure/Azure-Sentinel/issues
