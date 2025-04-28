Commvault - Sentinel Integration
================================

Integrate Commvault with Sentinel for automated alert/data ingestion and incident creation via Analytic Rules.

Prerequisites
-------------

*   Commvault/Metallic admin access.
*   Azure RG/Subscription admin access.
*   Azure Cloud Shell access.
*   Microsoft Sentinel instance (in Azure RG).
*   Azure Log Analytic Workspace (in Azure RG).

Required Assets
---------------

*   **KeyVault:** Stores credentials as secrets.
    *   **Secrets:**
        *   access-token : Commvault/Metallic access token.
        *   environment-endpoint-url : Commvault/Metallic endpoint URL (e.g., https://`hostname`/commandcenter/api or http://`hostname`:`port`/SearchSvc/CVWebService.svc).

Installation
------------

**1\. Create Access Token in Commvault:**

*   Follow the instructions in [Creating an Access Token](https://documentation.commvault.com/2024e/essential/creating_access_token.html).
*   Ensure the user creating the token has **Admin** or **Tenant Admin** privileges.

**2\. Create KeyVault:**

*   Azure Portal -> KeyVault -> Create -> Basics (select subscription, RG).

**3\. Create KeyVault Secrets:**

*   Azure Portal -> KeyVault -> Secrets -> Generate/Import -> Manual:
    *   Name: access-token, Value: (Your Commvault/Metallic access token), Enabled: Yes -> Create.
    *   Name: environment-endpoint-url, Value: (Your Commvault/Metallic endpoint's URL), Enabled: Yes -> Create.

**4\. Install Commvault Cloud Solution:**

*   Sentinel -> Content hub -> Search "Commvault Cloud" -> Install.

**5\. Configure Data Connector:**

*   Commvault Cloud -> CommvaultSecurityIQ (using Azure Functions) -> Open connector page -> Deploy to Azure -> Fill details -> Create.
*   For a detailed step-by-step guide, refer to [DataConnector.md](./DataConnector.md).

**6\. Upload and Run Setup Script:**

> **Note:** You must have sufficient permissions to view and purge secrets in the Azure Key Vault before running the setup script. Without these permissions, the script will fail to update or remove existing secrets as required.

*   Open **Azure Cloud Shell** in PowerShell mode:
    1. Navigate to the **Azure Portal**.
    2. Click on the **Cloud Shell** icon in the top-right corner of the portal.
    3. If prompted, select **PowerShell** as the shell environment (instead of Bash).
    4. If this is your first time using Cloud Shell, you may need to create a storage account to persist your files. Follow the on-screen instructions to set it up.

*   Manage files -> [Setup-CommvaultAutomation.ps1](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ/Tools/Setup-CommvaultAutomation.ps1) -> Run: `./Setup-CommvaultAutomation.ps1`

**7\. Create Analytic Rules:**

*   Sentinel -> Content hub -> "Commvault Cloud" -> Manage -> "Commvault Cloud Alert" -> Create Rule -> Next -> Save.
*   Repeat for other Analytic Rules.

**8\. Create Playbooks:**

*   Sentinel -> Content hub -> "Commvault Cloud" -> Manage -> "logic-app-disable-data-aging" -> Configuration -> "Commvault Disable Data Aging Logic App Playbook" -> Create Playbook -> Next -> Enter keyvaultName -> Create Playbook.
*   Repeat for other playbooks.

**9\. Add Additional Permissions:**

*   After completing all the steps, ensure that the necessary additional permissions are configured.
*   Follow the instructions in [Permissions.md](./Permissions.md) to grant the required permissions for the Logic Apps.
*   Additionally, refer to **6. Post-Deployment Steps** in [DataConnector.md](./DataConnector.md) to ensure the Function App has the necessary permissions to access the Key Vault.
