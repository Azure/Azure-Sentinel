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

*   **KeyVault:** Stores credentials as secrets (access policy enabled).
    *   **Secrets:**
        *   access-token : Commvault/Metallic access token.
        *   environment-endpoint-url : Commvault/Metallic endpoint URL (e.g., https://<hostname>/commandcenter/api or http://<hostname>:<port>/SearchSvc/CVWebService.svc).

Installation
------------

**1\. Create KeyVault:**

*   Azure Portal -> KeyVault -> Create -> Basics (select subscription, RG).

**2\. Create KeyVault Secrets:**

*   Azure Portal -> KeyVault -> Secrets -> Generate/Import -> Manual:
    *   Name: access-token, Value: (Your Commvault/Metallic access token), Enabled: Yes -> Create.
    *   Name: environment-endpoint-url, Value: (Your Commvault/Metallic endpoint's URL), Enabled: Yes -> Create.

**3\. Install Commvault Cloud Solution:**

*   Sentinel -> Content hub -> Search "Commvault Cloud" -> Install.

**4\. Configure Data Connector:**

*   Commvault Cloud -> Commvault Cloud Alert (Azure Functions) -> Open connector page -> Deploy to Azure -> Fill details -> Create.

**5\. Upload and Run Setup Script:**

*   Azure Cloud Shell -> Manage files -> [Setup-CommvaultAutomation.ps1](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ/Tools/Setup-CommvaultAutomation.ps1) -> Run: ./Setup-CommvaultAutomation.ps1

**6\. Create Analytic Rules:**

*   Sentinel -> Content hub -> "Commvault Cloud" -> Manage -> "Commvault Cloud Alert" -> Create Rule -> Next -> Save.
*   Repeat for other Analytic Rules.

**7\. Create Playbooks:**

*   Sentinel -> Content hub -> "Commvault Cloud" -> Manage -> "logic-app-disable-data-aging" -> Configuration -> "Commvault Disable Data Aging Logic App Playbook" -> Create Playbook -> Next -> Enter keyvaultName -> Create Playbook.
*   Repeat for other playbooks.

**8\. Upload and Run Role Assignment Script:**

*   Azure Cloud Shell -> Manage files -> [AssignLogicAppRoles.ps1](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Commvault%20Security%20IQ/Tools/AssignLogicAppRoles.ps1) -> Run: ./AssignLogicAppRoles.ps1
