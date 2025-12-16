# Doppel

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Doppel |
| **Support Tier** | Partner |
| **Support Link** | [https://www.doppel.com/request-a-demo](https://www.doppel.com/request-a-demo) |
| **Categories** | domains |
| **First Published** | 2024-11-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Doppel](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Doppel) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Doppel Data Connector](../connectors/doppel-dataconnector.md)

**Publisher:** Doppel

The data connector is built on Microsoft Sentinel for Doppel events and alerts and supports DCR-based [ingestion time transformations](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/ingestion-time-transformations) that parses the received security event data into a custom columns so that queries don't need to parse it again, thus resulting in better performance.

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions are required.
- **Keys** (Workspace): read permissions to shared keys for the workspace are required.

**Custom Permissions:**
- **Microsoft Entra Tenant ID, Client ID and Client Secret**: Microsoft Entra ID requires a Client ID and Client Secret to authenticate your application. Additionally, Global Admin/Owner level access is required to assign the Entra-registered application a Resource Group Monitoring Metrics Publisher role.
- **Requires Workspace ID, DCE-URI, DCR-ID**: You will need to get the Log Analytics Workspace ID, DCE Logs Ingestion URI and DCR Immutable ID for the configuration.

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Configure Doppel Webhook**

Configure the Webhook in Doppel and Endpoint with permissions in Microsoft Sentinel to send data.
**Register the Application in Microsoft Entra ID**

  1. **Open the [Microsoft Entra ID page](https://entra.microsoft.com/)**:
   - Click the provided link to open the **Microsoft Entra ID** registration page in a new tab.
   - Ensure you are logged in with an account that has **Admin level** permissions.

2. **Create a New Application**:
   - In the **Microsoft Entra ID portal**, select **App registrations** mentioned on the left-hand side tab.
   - Click on **+ New registration**.
   - Fill out the following fields:
     - **Name**: Enter a name for the app (e.g., “Doppel App”).
     - **Supported account types**: Choose **Accounts in this organizational directory only** (Default Directory only - Single tenant).
     - **Redirect URI**: Leave this blank unless required otherwise.
   - Click **Register** to create the application.

3. **Copy Application and Tenant IDs**:
   - Once the app is registered, note the **Application (client) ID** and **Directory (tenant) ID** from the **Overview** page. You’ll need these for the integration.

4. **Create a Client Secret**:
   - In the **Certificates & secrets** section, click **+ New client secret**.
   - Add a description (e.g., 'Doppel Secret') and set an expiration (e.g., 1 year).
   - Click **Add**.
   - **Copy the client secret value immediately**, as it will not be shown again.

  **Assign the "Monitoring Metrics Publisher" Role to the App**

  1. **Open the Resource Group in Azure Portal**:
   - Navigate to the **Resource Group** that contains the **Log Analytics Workspace** and **Data Collection Rules (DCRs)** where you want the app to push data.

2. **Assign the Role**:
   - In the **Resource Group** menu, click on **Access control (IAM)** mentioned on the left-hand side tab ..
   - Click on **+ Add** and select **Add role assignment**.
   - In the **Role** dropdown, search for and select the **Monitoring Metrics Publisher** role.
   - Under **Assign access to**, choose **Azure AD user, group, or service principal**.
   - In the **Select** field, search for your registered app by **name** or **client ID**.
   - Click **Save** to assign the role to the application.

  **Deploy the ARM Template**

  1. **Retrieve the Workspace ID**:
   - After assigning the role, you will need the **Workspace ID**.
   - Navigate to the **Log Analytics Workspace** within the **Resource Group**.
   - In the **Overview** section, locate the **Workspace ID** field under **Workspace details**.
   - **Copy the Workspace ID** and keep it handy for the next steps.

2. **Click the Deploy to Azure Button**:
   - [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmetron-labs%2FAzure-Sentinel%2Frefs%2Fheads%2FDoppelSolution%2FSolutions%2FDoppel%2FData%2520Connectors%2FDeployToAzure.json).
   - This will take you directly to the Azure portal to start the deployment.

3. **Review and Customize Parameters**:
   - On the custom deployment page, ensure you’re deploying to the correct **subscription** and **resource group**.
   - Fill in the parameters like **workspace name**, **workspace ID**, and **workspace location**.

4. **Click Review + Create** and then **Create** to deploy the resources.

  **Verify DCE, DCR, and Log Analytics Table Setup**

  1. **Check the Data Collection Endpoint (DCE)**:
   - After deploying, go to **Azure Portal > Data Collection Endpoints**.
   - Verify that the **DoppelDCE** endpoint has been created successfully.
   - **Copy the DCE Logs Ingestion URI**, as you’ll need this for generating the webhook URL.

2. **Confirm Data Collection Rule (DCR) Setup**:
   - Go to **Azure Portal > Data Collection Rules**.
   - Ensure the **DoppelDCR** rule is present.
   - **Copy the Immutable ID** of the DCR from the Overview page, as you’ll need it for the webhook URL.

3. **Validate Log Analytics Table**:
   - Navigate to your **Log Analytics Workspace** (linked to Microsoft Sentinel).
   - Under the **Tables** section, verify that the **DoppelTable_CL** table has been created successfully and is ready to receive data.

  **Integrate Doppel Alerts with Microsoft Sentinel**

  1. **Gather Necessary Information**:
   - Collect the following details required for integration:
     - **Data Collection Endpoint ID (DCE-ID)**
     - **Data Collection Rule ID (DCR-ID)**
     - **Microsoft Entra Credentials**: Tenant ID, Client ID, and Client Secret.

2. **Coordinate with Doppel Support**:
   - Share the collected DCE-ID, DCR-ID, and Microsoft Entra credentials with Doppel support.
   - Request assistance to configure these details in the Doppel tenant to enable webhook setup.

3. **Webhook Setup by Doppel**:
   - Doppel will use the provided Resource IDs and credentials to configure a webhook.
   - This webhook will facilitate the forwarding of alerts from Doppel to Microsoft Sentinel.

4. **Verify Alert Delivery in Microsoft Sentinel**:
   - Check that alerts from Doppel are successfully forwarded to Microsoft Sentinel.
   - Validate that the **Workbook** in Microsoft Sentinel is updated with the alert statistics, ensuring seamless data integration.

| | |
|--------------------------|---|
| **Tables Ingested** | `DoppelTable_CL` |
| **Connector Definition Files** | [Template_Doppel.json](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Doppel/Data%20Connectors/Template_Doppel.json) |

[→ View full connector details](../connectors/doppel-dataconnector.md)

## Tables Reference

This solution ingests data into **1 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `DoppelTable_CL` | [Doppel Data Connector](../connectors/doppel-dataconnector.md) |

[← Back to Solutions Index](../solutions-index.md)
