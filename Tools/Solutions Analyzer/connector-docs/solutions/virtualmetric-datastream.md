# VirtualMetric DataStream

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | VirtualMetric |
| **Support Tier** | Partner |
| **Support Link** | [https://support.virtualmetric.com](https://support.virtualmetric.com) |
| **Categories** | domains |
| **Author** | VirtualMetric |
| **First Published** | 2025-09-15 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirtualMetric%20DataStream](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirtualMetric%20DataStream) |

## Data Connectors

This solution provides **3 data connector(s)**.

### [VirtualMetric Director Proxy](../connectors/virtualmetricdirectorproxy.md)

**Publisher:** VirtualMetric

### [VirtualMetric DataStream for Microsoft Sentinel](../connectors/virtualmetricmssentinelconnector.md)

**Publisher:** VirtualMetric

### [VirtualMetric DataStream for Microsoft Sentinel data lake](../connectors/virtualmetricmssentineldatalakeconnector.md)

**Publisher:** VirtualMetric

VirtualMetric DataStream connector deploys Data Collection Rules to ingest security telemetry into Microsoft Sentinel data lake.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required.

**Custom Permissions:**
- **App Registration or Azure Managed Identity**: VirtualMetric DataStream requires an Entra ID identity to authenticate and send logs to Microsoft Sentinel data lake. You can choose between creating an App Registration with Client ID and Client Secret, or using Azure Managed Identity for enhanced security without credential management.
- **Resource Group Role Assignment**: The chosen identity (App Registration or Managed Identity) must be assigned to the resource group containing the Data Collection Endpoint with the following roles: Monitoring Metrics Publisher (for log ingestion) and Monitoring Reader (for reading stream configuration).

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configure VirtualMetric DataStream for Microsoft Sentinel data lake**

Configure the VirtualMetric DataStream for Microsoft Sentinel data lake to send data.
**Register Application in Microsoft Entra ID (Optional)**

  **Choose your authentication method:**

**Option A: Use Azure Managed Identity (Recommended)**
- Skip this step if you plan to use Azure Managed Identity for authentication.
- Azure Managed Identity provides a more secure authentication method without managing credentials.

**Option B: Register a Service Principal Application**

1. **Open the [Microsoft Entra ID page](https://entra.microsoft.com/)**:
   - Click the provided link to open the **Microsoft Entra ID** registration page in a new tab.
   - Ensure you are logged in with an account that has **Application Administrator** or **Global Administrator** permissions.

2. **Create a New Application**:
   - In the **Microsoft Entra ID portal**, select **App registrations** from the left-hand navigation.
   - Click on **+ New registration**.
   - Fill out the following fields:
     - **Name**: Enter a descriptive name for the app (e.g., "VirtualMetric ASIM Connector").
     - **Supported account types**: Choose **Accounts in this organizational directory only** (Single tenant).
     - **Redirect URI**: Leave this blank.
   - Click **Register** to create the application.

3. **Copy Application and Tenant IDs**:
   - Once the app is registered, note the **Application (client) ID** and **Directory (tenant) ID** from the **Overview** page. You'll need these for VirtualMetric DataStream configuration.

4. **Create a Client Secret**:
   - In the **Certificates & secrets** section, click **+ New client secret**.
   - Add a description (e.g., 'VirtualMetric ASIM Secret') and set an appropriate expiration period.
   - Click **Add**.
   - **Copy the client secret value immediately**, as it will not be shown again. Store this securely for VirtualMetric DataStream configuration.

  **Assign Required Permissions**

  Assign the required roles to your chosen authentication method (Service Principal or Managed Identity) in the resource group.

**For Service Principal (if you completed Step 1):**

1. **Navigate to Your Resource Group**:
   - Open the **Azure Portal** and navigate to the **Resource Group** that contains your **Log Analytics Workspace** and where **Data Collection Rules (DCRs)** will be deployed.

2. **Assign the Monitoring Metrics Publisher Role**:
   - In the **Resource Group**, click on **Access control (IAM)** from the left-hand menu.
   - Click **+ Add** and select **Add role assignment**.
   - In the **Role** tab, search for and select **Monitoring Metrics Publisher**.
   - Click **Next** to go to the **Members** tab.
   - Under **Assign access to**, select **User, group, or service principal**.
   - Click **+ Select members** and search for your registered application by name or client ID.
   - Select your application and click **Select**.
   - Click **Review + assign** twice to complete the assignment.

3. **Assign the Monitoring Reader Role**:
   - Repeat the same process to assign the **Monitoring Reader** role:
   - Click **+ Add** and select **Add role assignment**.
   - In the **Role** tab, search for and select **Monitoring Reader**.
   - Follow the same member selection process as above.
   - Click **Review + assign** twice to complete the assignment.

**For Azure Managed Identity:**

1. **Create or Identify Your Managed Identity**:
   - If using **System-assigned Managed Identity**: Enable it on your Azure resource (VM, App Service, etc.).
   - If using **User-assigned Managed Identity**: Create one in your resource group if it doesn't exist.

2. **Assign the Monitoring Metrics Publisher Role**:
   - Follow the same steps as above, but in the **Members** tab:
   - Under **Assign access to**, select **Managed identity**.
   - Click **+ Select members** and choose the appropriate managed identity type and select your identity.
   - Click **Select**, then **Review + assign** twice to complete.

3. **Assign the Monitoring Reader Role**:
   - Repeat the process to assign the **Monitoring Reader** role to the same managed identity.

**Required Permission Summary:**
The assigned roles provide the following capabilities:
- **Monitoring Metrics Publisher**: Write data to Data Collection Endpoints (DCE) and send telemetry through Data Collection Rules (DCR)
- **Monitoring Reader**: Read stream configuration and access Log Analytics workspace for ASIM table ingestion

  **Deploy Azure Infrastructure**

  Deploy the required Data Collection Endpoint (DCE) and Data Collection Rules (DCR) for Microsoft Sentinel data lake tables using our ARM template.

1. **Deploy to Azure**:
   - Click the Deploy to Azure button below to automatically deploy the required infrastructure:
   - [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVirtualMetric%2520DataStream%2FData%2520Connectors%2FVirtualMetric-SentinelDataLake%2FDeployToAzure.json)
   - This will take you directly to the Azure portal to start the deployment.

2. **Configure Deployment Parameters**:
   - On the custom deployment page, configure the following settings:
   
   **Project details:**
   - **Subscription**: Select your Azure subscription from the dropdown
   - **Resource group**: Select an existing resource group or click **Create new** to create a new one
   
   **Instance details:**
   - **Region**: Select the Azure region where your Log Analytics workspace is located (e.g., West Europe)
   - **Workspace**: Enter your Log Analytics workspace name
   - **DCE Name**: Provide a name for the Data Collection Endpoint (e.g., "vmetric-dce")
   - **DCR Name Prefix**: Provide a prefix for the Data Collection Rules (e.g., "vmetric-dcr")

3. **Complete the Deployment**:
   - Click **Review + create** to validate the template.
   - Review the parameters and click **Create** to deploy the resources.
   - Wait for the deployment to complete (typically takes 2-5 minutes).

4. **Verify Deployed Resources**:
   - After deployment, verify the following resources were created:
     - **Data Collection Endpoint (DCE)**: Check **Azure Portal > Monitor > Data Collection Endpoints**
     - **Data Collection Rules (DCRs)**: Check **Azure Portal > Monitor > Data Collection Rules**
   - **Copy the DCE Logs Ingestion URI** from the DCE **Overview** page (format: `https://<dce-name>.<region>.ingest.monitor.azure.com`)
   - **Copy the DCE Resource ID** from the DCE **Overview** page (format: `/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>/providers/Microsoft.Insights/dataCollectionEndpoints/<dce-name>`)
   - For each DCR, note the **Immutable ID** from the **Overview** page - you'll need these for VirtualMetric DataStream configuration.

  **Configure VirtualMetric DataStream Integration**

  Set up VirtualMetric DataStream to send security telemetry to Microsoft Sentinel data lake tables.

1. **Access VirtualMetric DataStream Configuration**:
   - Log into your **VirtualMetric DataStream** management console.
   - Navigate to **Fleet Management** > **Targets** section.
   - Click **Add new target** button.
   - Select **Microsoft Sentinel** target.

2. **Configure General Settings**:
   - **Name**: Enter a name for your target (e.g., "cus01-ms-sentinel")
   - **Description**: Optionally provide a description for the target configuration

3. **Configure Azure Authentication** (choose based on Step 1):
   
   **For Service Principal Authentication:**
   - **Managed Identity for Azure**: Keep **Disabled**
   - **Tenant ID**: Enter the Directory (tenant) ID from Step 1
   - **Client ID**: Enter the Application (client) ID from Step 1
   - **Client Secret**: Enter the client secret value from Step 1
   
   **For Azure Managed Identity:**
   - **Managed Identity for Azure**: Set to **Enabled**

4. **Configure Stream Properties**:
   - **Endpoint**: Choose your configuration method:
     - **For manual stream configuration**: Enter the DCE Logs Ingestion URI (format: `https://<dce-name>.<region>.ingest.monitor.azure.com`)
     - **For auto stream detection**: Enter the DCE Resource ID (format: `/subscriptions/<subscription-id>/resourceGroups/<resource-group-name>/providers/Microsoft.Insights/dataCollectionEndpoints/<dce-name>`)
   - **Streams**: Select **Auto** for automatic stream detection, or configure specific streams if needed

5. **Verify Data Ingestion in Microsoft Sentinel data lake**:
   - Return to your **Log Analytics Workspace**
   - Run sample queries on the ASIM tables to confirm data is being received:
     ```kql
     ASimNetworkSessionLogs
     | where TimeGenerated > ago(1h)
     | take 10
     ```
   - Check the **Microsoft Sentinel Overview** dashboard for new data sources and event counts.

| | |
|--------------------------|---|
| **Tables Ingested** | `CommonSecurityLog` |
| **Connector Definition Files** | [Template_SentinelDataLake.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/VirtualMetric%20DataStream/Data%20Connectors/VirtualMetric-SentinelDataLake/Template_SentinelDataLake.json) |

[→ View full connector details](../connectors/virtualmetricmssentineldatalakeconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `CommonSecurityLog` | [VirtualMetric DataStream for Microsoft Sentinel](../connectors/virtualmetricmssentinelconnector.md), [VirtualMetric DataStream for Microsoft Sentinel data lake](../connectors/virtualmetricmssentineldatalakeconnector.md), [VirtualMetric Director Proxy](../connectors/virtualmetricdirectorproxy.md) |

[← Back to Solutions Index](../solutions-index.md)
