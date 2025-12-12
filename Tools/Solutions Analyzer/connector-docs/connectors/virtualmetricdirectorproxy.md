# VirtualMetric Director Proxy

| | |
|----------|-------|
| **Connector ID** | `VirtualMetricDirectorProxy` |
| **Publisher** | VirtualMetric |
| **Tables Ingested** | [`CommonSecurityLog`](../tables-index.md#commonsecuritylog) |
| **Used in Solutions** | [VirtualMetric DataStream](../solutions/virtualmetric-datastream.md) |
| **Connector Definition Files** | [Template_DirectorProxy.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirtualMetric%20DataStream/Data%20Connectors/VirtualMetric-DirectorProxy/Template_DirectorProxy.json) |

VirtualMetric Director Proxy deploys an Azure Function App to securely bridge VirtualMetric DataStream with Azure services including Microsoft Sentinel, Azure Data Explorer, and Azure Storage.

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required.

**Custom Permissions:**
- **Azure Function App**: An Azure Function App must be deployed to host the Director Proxy. Requires read, write, and delete permissions on Microsoft.Web/sites resources within your resource group to create and manage the Function App.
- **VirtualMetric DataStream Configuration**: You need VirtualMetric DataStream configured with authentication credentials to connect to the Director Proxy. The Director Proxy acts as a secure bridge between VirtualMetric DataStream and Azure services.
- **Target Azure Services**: Configure your target Azure services such as Microsoft Sentinel Data Collection Endpoints, Azure Data Explorer clusters, or Azure Storage accounts where the Director Proxy will forward data.

## Setup Instructions

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Deploy VirtualMetric Director Proxy**

Deploy the Azure Function App that serves as a secure proxy between VirtualMetric DataStream and Microsoft Sentinel.
**Prerequisites and Deployment Order**

  **Recommended Deployment Order:**

For optimal configuration, consider deploying the target connectors first:

1. **Deploy Microsoft Sentinel Connector**: Deploy the VirtualMetric DataStream for Microsoft Sentinel connector first to create the required Data Collection Endpoints and Rules.

2. **Deploy Microsoft Sentinel data lake Connector** (optional): If using Microsoft Sentinel data lake tables, deploy the VirtualMetric DataStream for Microsoft Sentinel data lake connector.

3. **Deploy Director Proxy** (this step): The Director Proxy can then be configured with your Microsoft Sentinel targets.

**Note:** This order is recommended but not required. You can deploy the Director Proxy independently and configure it with your targets later.

  **Deploy Azure Function App**

  Deploy the VirtualMetric Director Proxy Azure Function App using the Deploy to Azure button.

1. **Deploy to Azure**:
   - Click the Deploy to Azure button below to deploy the Function App:
   - [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVirtualMetric%2520DataStream%2FData%2520Connectors%2FVirtualMetric-DirectorProxy%2FDeployToAzure.json)

2. **Configure Deployment Parameters**:
   - **Subscription**: Select your Azure subscription
   - **Resource Group**: Choose the same resource group as your Microsoft Sentinel workspace or create a new one
   - **Region**: Select the Azure region (should match your Microsoft Sentinel workspace region)
   - **Function App Name**: Provide a unique name for the Function App (e.g., "vmetric-director-proxy")

3. **Complete Deployment**:
   - Click **Review + create** to validate the parameters
   - Click **Create** to deploy the Function App
   - Wait for deployment to complete (typically 3-5 minutes)
   - Note the Function App URL: `https://<function-app-name>.azurewebsites.net`

  **Configure Function App Permissions**

  Assign the necessary permissions to the Function App's managed identity to access Microsoft Sentinel resources.

1. **Enable System-Assigned Managed Identity**:
   - Navigate to your deployed Function App in Azure Portal
   - Go to **Identity** under Settings
   - Toggle **Status** to **On** for System assigned identity
   - Click **Save** and confirm

2. **Navigate to Resource Group**:
   - Go to the resource group containing your Microsoft Sentinel workspace and Data Collection Endpoints

3. **Assign Required Roles**:
   - Open **Access control (IAM)**
   - Click **+ Add** > **Add role assignment**
   - Assign the following roles to the Function App's system-assigned managed identity:
     - **Monitoring Metrics Publisher**: For sending data to Data Collection Endpoints
     - **Monitoring Reader**: For reading Data Collection Rules configuration

4. **Select the Function App Identity**:
   - In **Members** tab, select **Managed identity**
   - Choose **Function App** and select your deployed Director Proxy Function App
   - Complete the role assignment

5. **Get Function App Access Token** (Optional for Function Key authentication):
   - Navigate to your Function App
   - Go to **App keys** under Functions
   - Copy the default host key or create a new function key for authentication

  **Configure VirtualMetric DataStream Integration**

  Set up VirtualMetric DataStream to send security telemetry to Microsoft Sentinel through the Director Proxy.

1. **Access VirtualMetric DataStream Configuration**:
   - Log into your **VirtualMetric DataStream** management console
   - Navigate to **Targets** section
   - Click **Microsoft Sentinel Targets**
   - Click **Add new target** or edit an existing Microsoft Sentinel target

2. **Configure General Settings**:
   - **Name**: Enter a name for your target (e.g., "sentinel-with-proxy")
   - **Description**: Optionally provide a description for the target configuration

3. **Configure Azure Authentication**:
   
   **For Service Principal Authentication:**
   - **Managed Identity for Azure**: Keep **Disabled**
   - **Tenant ID**: Enter your Azure Active Directory tenant ID
   - **Client ID**: Enter your service principal application ID
   - **Client Secret**: Enter your service principal client secret
   
   **For Azure Managed Identity:**
   - **Managed Identity for Azure**: Set to **Enabled**

4. **Configure Director Proxy** (in Azure Properties tab):
   - **Endpoint Address**: Enter the Function App URL from Step 2 (format: `https://<function-app-name>.azurewebsites.net`)
   - **Access Token**: Enter the Function App host key from Step 3 (optional if using Managed Identity)

5. **Configure Stream Properties**:
   - **Endpoint**: Enter the DCE Logs Ingestion URI (format: `https://<dce-name>.<region>.ingest.monitor.azure.com`)
   - **Streams**: Select **Auto** for automatic stream detection, or configure specific streams if needed

6. **Verify Data Ingestion in Microsoft Sentinel**:
   - Return to your **Log Analytics Workspace**
   - Run sample queries to confirm data is being received:
     ```kql
     CommonSecurityLog
     | where TimeGenerated > ago(1h)
     | take 10
     ```
   - Check the **Microsoft Sentinel Overview** dashboard for new data sources and event counts

[← Back to Connectors Index](../connectors-index.md)
