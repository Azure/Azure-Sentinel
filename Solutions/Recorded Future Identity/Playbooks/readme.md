# Recorded Future Identity Installation Guide

Link to [Recorded Future Identity main readme](../readme.md)

## Table of Contents

1. [Overview](#overview)
1. [Deployment](#deployment)
1. [Prerequisites](#prerequisites)
1. [Playbooks](#playbooks)
   1. ["Connector" playbooks](#connector_playbooks)
      1. [RFI-CustomConnector](#RFI-CustomConnector)
   1. ["Alert" playbooks](#alert_playbooks)
      1. [RFI-playbook-alert-importer](#RFI-playbook-alert-importer)
      1. [RFI-playbook-alert-importer-law](#RFI-playbook-alert-importer-law)
      1. [RFI-playbook-alert-importer-law-sentinel](#RFI-playbook-alert-importer-law-sentinel)
1. [How to configure playbooks](#configuration)
   1. [How to find the playbooks (Logic Apps) after deployment](#find_playbooks_after_deployment)
   1. [Configuring Playbooks Connections](#configuration_connections)
   1. [API connector authorization](#API-connector-authorization)
   1. [Configuring Playbooks Parameters](#configuration_parameters)
1. [How to Run Playbooks](#how_to_run_playbooks)
1. [Suggestions for advanced users](#suggestions_for_advanced_users)
1. [How to access Log Analytics Custom Logs](#how_to_access_log_analytics_custom_logs)
1. [Customization](#customization)
1. [Known Issues](#known-issues)
1. [Useful Azure documentation](#useful_documentation)
1. [How to obtain Recorded Future API token](#how_to_obtain_Recorded_Future_API_token)
1. [How to contact Recorded Future](#how_to_contact_Recorded_Future)

<a id="overview"></a>
## Overview

This solution contains two approaches to deal with exposed credentials.
- The recommended variant (based on Recorded Future Playbook Alerts) is described in this readme
- The old variant (based on the Recorded Future Identity API) is located in the [v3.0](./v3.0/readme.md) folder

The playbooks need to be installed in the following order: custom-connector, and one of the alert playbooks.

<details>
<summary>Expand playbook overview</summary>

<br/>

Connector playbooks:
Custom connector are used to communicate and authorize towards Recorded Future backend API.

| Playbook Name| Description  |
|-|-|
| **RFI-CustomConnector** | RFI-CustomConnector connection and authorization to Recorded Future Backend API.|

Alert playbook:
These are the main playbooks

| Playbook Name | Description |
|-|-|
| **RFI-playbook-alert-importer** | Search new exposures for Workforce users. Choose this one if only Entra ID is available |
| **RFI-playbook-alert-importer-law** | Search new exposures for Workforce users. Choose this one if Entra ID  and Log Analytics Workspace (LAW) is available |
| **RFI-playbook-alert-importer-law-sentinel** | Search new exposures for Workforce users. Choose this one if Entra ID, Log Analytics Workspace (LAW) and Microsoft Sentinel is available  |
</details>

## Deployment

Recorded Future recommend deploying playbooks in this solution from this README, first the connector and then deploy a playbook dependent on your use case. After installation, configure the connectors inside of the playbook. Lastly, configure playbook parameters in the playbook.

### Prerequisites

- A Microsoft Entra ID Tenant and subscription.
- A Microsoft Entra ID security group to which you want to assign any users who have leaked credentials.
- The user who installs the Logic Apps requires the permissions Azure Subscription Owner or Contributor. [Azure roles - Classic subscription administrator roles, Azure roles, and Entra ID roles](https://docs.microsoft.com/azure/role-based-access-control/rbac-and-directory-admin-roles#azure-roles).
- If a user authorizes the Entra ID connectors, they must have the Entra role `Directory Writers`. If a service principal (e.g., managed identity of app registration) authorizes the Entra ID connectors, they must have the permissions `Group.ReadWrite.All User.ReadWrite.All and Directory.ReadWrite.All`. For more information read <a href="https://learn.microsoft.com/en-us/connectors/azuread/" target="_blank"> ***here*** </a>
- If a user authorizes the Entra Identity Protection connector, they must have the Entra role `Security Administrator`. If a service principal (e.g., managed identity of app registration) authorizes the Entra ID connectors, they must have the permission `IdentityRiskyUser.ReadWrite.All`
- In Consumption Logic Apps, before you can create or manage Logic Apps and their connections, you need specific permissions. For more information about these permissions, review [Secure operations - Secure access and data in Azure Logic Apps](https://docs.microsoft.com/azure/logic-apps/logic-apps-securing-a-logic-app#secure-operations).

- For `Recorded Future Identity` Connections you will need `Recorded Future Identity API` token. To obtain one - check out [this section](#how_to_obtain_Recorded_Future_API_token).
- Configure `Recorded Future Identity Exposure Playbook Alerts` for your use case within the Recorded Future portal. For detailed instructions, see <a href="https://support.recordedfuture.com/hc/en-us/articles/21314816259859-Identity-Exposure-Playbook-Alert-Configuration" target="_blank">this guide</a> (requires Recorded Future login).

#### Optional prerequisites
These prerequisites is required for the **RFI-playbook-alert-importer-law** and **RFI-playbook-alert-importer-law-sentinel** playbooks:
- A [Log Analytics workspace](https://docs.microsoft.com/azure/azure-monitor/essentials/resource-logs#send-to-log-analytics-workspace). If you don't have a workspace, learn [how to create a Log Analytics workspace](https://docs.microsoft.com/azure/azure-monitor/logs/quick-create-workspace). Note that the custom logs specified as parameters in these Logic Apps will be created automatically if they don’t already exist. Note the name of the Log Analytic Workspace, it will be used at a later stage of the deployment.
- The user who installs the Logic Apps require <a href="https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#logic-app-contributor" target="_blank">_**Logic App Contributor**_</a> and <a href="https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#microsoft-sentinel-contributor" target="_blank">_**Microsoft Sentinel Contributor**_ </a> permissions on a **Resource Group** level.


<a id="playbooks"></a>
## Playbooks

> [!IMPORTANT]
> Deploy connector before deploying the alert importer playbooks.

<a id="connector_playbooks"></a>
### Connector-playbooks

Connector playbooks are used by other playbooks in this solution to communicate with Recorded Future backend API.

## RFI-CustomConnector

This connector is used by other playbooks in this solution to communicate with Recorded Future backend API.

### Deployment

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%20Future%20Identity%2FPlaybooks%2FConnectors%2FRFI-CustomConnector-0-2-0%2Fazuredeploy.json" target="_blank">![Deploy to Azure](https://aka.ms/deploytoazurebutton)</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%20Future%20Identity%2FPlaybooks%2FConnectors%2FRFI-CustomConnector-0-2-0%2Fazuredeploy.json" target="_blank">![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)</a>

<details>
<summary>Expand deployment parameters:</summary>

| Parameter | Description |
|-|-|
| **Subscription** | Your Azure Subscription to deploy the Solution in. All resources in an Azure subscription are billed together. |
| **Resource group** | Resource group in your Subscription to deploy the Solution in. A resource group is a collection of resources that share the same lifecycle, permissions, and policies. |
| **Region** | Choose the Azure region that's right for you and your customers. Not every resource is available in every region. |
| **Connector-Name**  | Connector name to use for this playbook (ex. `RFI-CustomConnector-0-2-0`). |
|**Service Endpoint**| API Endpoint, always use the default ```https://api.recordedfuture.com/gw/azure-identity```|
</details>
<hr/>

<a id="alert_playbooks"></a>

## Alert Playbooks

Search the Recorded Future Identity Intelligence Module for compromised identities. Depending on your use case, select the playbook that fits.

<details>
<summary> Workflow of Alert Playbooks</summary>

| # | Action                                                                                                                                                                                       |
|-|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | Pull novel identity exposure Playbook Alerts from Recorded Future based on previously done Playbook Alert setup.                                                                             |
| 2 | For each user, check if they exist within the domain, if so, place them in a specified security group. If the user is already flagged as a "Risky user" by Microsoft, confirm them as risky. |
| 3 | (Optional) Save all information related to the Playbook Alert in a Log Analytics Workspace.                                                                                                  |
| 3 | (Optional) Create a Microsoft Sentinel incident with information pertaining the identity exposure.                                                                                           |
| 4 | Report back actions taken for each specific Playbook Alert to Recorded Future, for viewing in Recorded Future Portal.                                                                        |

</details>

Depending on your use case, deploy **one** of the following playbooks:

- `RFI-playbook-alert-importer` contains the base use case, ingesting novel identity exposures and remediation of those exposures trough Entra ID.
- `RFI-playbook-alert-importer-law` does all of the above and saves detailed information to a Log Analytics Workspace (LAW).
- `RFI-playbook-alert-importer-law-sentinel` does all of the above and creates a **Microsoft Sentinel** incident, for easier investigation and follow up.

<a id="RFI-playbook-alert-importer"></a>
### Deployment RFI-playbook-alert-importer

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%20Future%20Identity%2FPlaybooks%2FRFI-Playbook-Alert-Importer%2Fazuredeploy.json" target="_blank">![Deploy to Azure](https://aka.ms/deploytoazurebutton)</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%20Future%20Identity%2FPlaybooks%2FRFI-Playbook-Alert-Importer%2Fazuredeploy.json" target="_blank">![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)</a>

<details>
<summary>Expand deployment parameters:</summary>

| Parameter                      | Description                                                                                                                                                            |
|--------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Subscription**               | Your Azure Subscription to deploy the Solution in. All resources in an Azure subscription are billed together.                                                         |
| **Resource group**             | Resource group in your Subscription to deploy the Solution in. A resource group is a collection of resources that share the same lifecycle, permissions, and policies. |
| **Region**                     | Choose the Azure region that's right for you and your customers. Not every resource is available in every region.                                                      |
| **Playbook Name**              | Playbook name to use for this playbook (ex. `RFI-Playbook-Alert-Importer`).                                                                                            |
| **Entra_id_security_group_id** | (Optional) ID of the the group in which to place risky users. If left empty, a user will **not** be placed in a Entra ID security group.                                                                                                                    |
|**Confirm_user_as_risky**| Boolean parameter to determine if a user should be confirmed as risky. Requires Microsoft Entra ID P1 or P2 license.  |
| **Entra_id_domain**            | (Optional) If domains does not match between external and Entra ID domains specify the domain used in Entra ID. Example: john.smith@acme -> john.smith@onmicrosoft.com |
| **RFI Custom Connector**       | Name of the custom connector which to connect to Recorded Future with, should typically not deviate from `RFI-CustomConnector-0-2-0`                                   |
</details>
<hr/>

<a id="RFI-playbook-alert-importer-law"></a>
### Deployment RFI-playbook-alert-importer-law

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%20Future%20Identity%2FPlaybooks%2FRFI-Playbook-Alert-Importer-LAW%2Fazuredeploy.json" target="_blank">![Deploy to Azure](https://aka.ms/deploytoazurebutton)</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%20Future%20Identity%2FPlaybooks%2FRFI-Playbook-Alert-Importer-LAW%2Fazuredeploy.json" target="_blank">![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)</a>

<details>
<summary>Expand deployment parameters:</summary>

| Parameter                                        | Description                                                                                                                                                            |
|--------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Subscription**                                 | Your Azure Subscription to deploy the Solution in. All resources in an Azure subscription are billed together.                                                         |
| **Resource group**                               | Resource group in your Subscription to deploy the Solution in. A resource group is a collection of resources that share the same lifecycle, permissions, and policies. |
| **Region**                                       | Choose the Azure region that's right for you and your customers. Not every resource is available in every region.                                                      |
| **Playbook Name**                                | Playbook name to use for this playbook (ex. "RFI-Playbook-Alert-Importer-LAW").                                                                                        |
| **Save_to_log_analytics_workspace**              | Boolean parameter to determine if the playbook should save the detailed Playbook Alert information to Log Analytics Workspace (LAW).                                   |
| **Entra_id_security_group_id** | (Optional) ID of the the group in which to place risky users. If left empty, a user will **not** be placed in a Entra ID security group.                                                                                                                   |
|**Confirm_user_as_risky**| Boolean parameter to determine if a user should be confirmed as risky. Requires Microsoft Entra ID P1 or P2 license.  |
| **Entra_id_domain**                              | (Optional) If domains does not match between external and Entra ID domains specify the domain used in Entra ID. Example: john.smith@acme -> john.smith@onmicrosoft.com |
| **Playbook_alert_log_analytics_custom_log_name** | Name of the custom log in Log Analytics Workspace, defaults to `RecordedFutureIdentity_PlaybookAlertResults_CL`.                                                       |
| **RFI Custom Connector**                         | Name of the custom connector which to connect to Recorded Future with, should typically not deviate from `RFI-CustomConnector-0-2-0`                                   |
</details>
<hr/>

<a id="RFI-playbook-alert-importer-law-sentinel"></a>
### Deployment RFI-playbook-alert-importer-law-sentinel

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%20Future%20Identity%2FPlaybooks%2FRFI-Playbook-Alert-Importer-LAW-Sentinel%2Fazuredeploy.json" target="_blank">![Deploy to Azure](https://aka.ms/deploytoazurebutton)</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRecorded%20Future%20Identity%2FPlaybooks%2FRFI-Playbook-Alert-Importer-LAW-Sentinel%2Fazuredeploy.json" target="_blank">![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)</a>

<details>
<summary>Expand deployment parameters:</summary>

| Parameter                                        | Description |
|--------------------------------------------------|-|
| **Subscription**                                 | Your Azure Subscription to deploy the Solution in. All resources in an Azure subscription are billed together. |
| **Resource group**                               | Resource group in your Subscription to deploy the Solution in. A resource group is a collection of resources that share the same lifecycle, permissions, and policies. |
| **Region**                                       | Choose the Azure region that's right for you and your customers. Not every resource is available in every region. |
| **Playbook Name**                                | Playbook name to use for this playbook (ex. "RFI-Playbook-Alert-Importer-LAW-Sentinel"). |
| **Save_to_log_analytics_workspace**              |Boolean parameter to determine if the playbook should save the detailed Playbook Alert information to Log Analytics Workspace (LAW)|
| **Entra_id_security_group_id** | (Optional) ID of the the group in which to place risky users. If left empty, a user will **not** be placed in a Entra ID security group.                                                                                                                  |
|**Confirm_user_as_risky**| Boolean parameter to determine if a user should be confirmed as risky. Requires Microsoft Entra ID P1 or P2 license.  |
| **Create_incident**                              |Boolean parameter to determine if the playbook should create a incident in Microsoft Sentinel|
| **Sentinel_workspace_name**                      |Workspace name in which to create Microsoft Sentinel incidents|
| **Entra_id_domain**                              | (Optional) If domains does not match between external and Entra ID domains specify the domain used in Entra ID. Example: john.smith@acme -> john.smith@onmicrosoft.com |
| **Playbook_alert_log_analytics_custom_log_name** |Name of the custom log in Log Analytics Workspace, defaults to `RecordedFutureIdentity_PlaybookAlertResults_CL`|
| **RFI Custom Connector**                         | Name of the custom connector which to connect to Recorded Future with, should typically not deviate from `RFI-CustomConnector-0-2-0`|
</details>
<hr/>

## Configuration

### How to find the playbooks (Logic Apps) after deployment

To find installed Playbooks (Logic Apps) after deployment - you can search for `Logic Apps` from the [Azure Portal](https://portal.azure.com/) page and find deployed Logic Apps there.

<a id="configuration_connections"></a>
### Configuring Playbook Connections

After deployment - create/validate the Connections in each of deployed Playbooks. The Logic App will have errors and save is disabled until all connectors are authorized.

<img src="./images/playbookauth2.png" alt="Logic Apps Parameters #1" width="70%"/>


<a id="API-connector-authorization"></a>
### API connector authorization
The Recorded Future identity solution uses the following connectors, some are required and and some optional. Information on how to authorize connectors is documented in the provided links. Playbooks use connectors that have to be individually authorized during deployment.

| Connector | Description |
|-|-|
| **/RFI-CustomConnector** | [RecordedFuture-CustomConnector](../../Recorded%20Future/Playbooks/Connectors/RecordedFuture-CustomConnector/readme.md) <br/> [How to obtain Recorded Future API token](#how_to_obtain_Recorded_Future_API_token) |
| **/azuread** | [Microsoft Entra ID power platform connectors](https://learn.microsoft.com/en-us/connectors/azuread/). |
| **/azureadip** | [Azure AD Identity Protection](https://learn.microsoft.com/en-us/connectors/azureadip/) |
| **/azureloganalyticsdatacollector** (Optional) | [Azure Log Analytics Data Collector](https://learn.microsoft.com/en-us/connectors/azureloganalyticsdatacollector/) <br/> [How to find Log Analytics Workspace key.](https://learn.microsoft.com/en-us/answers/questions/1154380/where-is-azure-is-the-primary-key-and-workspace-id)
| **/azuresentinel** (Optional)| <a href="https://learn.microsoft.com/en-us/connectors/azuresentinel/" target="_blank">Documentation on Microsoft power platform connectors </a> |


Each installed Logic App uses various connectors that needs to be authorized, each of the connectors needs to be authorized in different ways depending on their type.

Below are guides that are tailored to our recommended authorization flow (Managed Identity, when possible). Depending on your organizational rules, the flow might be different. Please consult with your Azure administrator in those cases. Multi-tenant authorizations are untested, please consult with your Azure administrators for proper authorization flow.
<details>
<summary>Expand to see rfi-custom-connector authorization guide</summary>

<br>

After a Logic App has been installed, the **RFI-CustomConnector-0-2-0** needs to be authorized. This only needs to be done once. If there are any uncertainties expand all nodes in the Logic App after installation and look for blocks marked with a warning sign.

1. Go to the specific Logic App,  in the left menu click on the section _**Development tools**_
2. Click on **_API connections_**
3. Click on **_RFI-CustomConnector-0-2-0_**
4. Click on **_General_** in the left menu on the newly opened section
5. Click on **_Edit API Connection_**
6. Paste the **Recorded Future API Key** and click **_Save_**

![apiconnection](images/apiconnection.png)

</details>

<details>
<summary>Expand to see azuread authorization information</summary>

<br>

The Microsoft Entra ID connector needs to be authorized via **OAuth** by a user who has the `Group.ReadWrite.All User.ReadWrite.All and Directory.ReadWrite.All` permissions. For more information, see <a href="https://learn.microsoft.com/en-us/connectors/azuread/" target="_blank">this article</a>.

<br>

</details>

<details>
<summary>Expand to see azureadip authorization information</summary>

<br>

The Azure AD Identity Protection needs to be authorized via **OAuth**. For more information, see <a href="https://learn.microsoft.com/en-us/connectors/azureadip/" target="_blank">this article</a>.
</details>
<br>

***Optional connectors***
<details>
<summary>Expand to see azuresentinel managed identity authorization guide</summary>

<br>

The **azuresentinel** connector needs to be authorized for the solution to write to Microsoft Sentinel. There are multiple ways to do this, but our recommendation is using <a href="https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview" target="_blank">**system assigned managed identity**</a>, this requires that the user performing the installation needs to have the role of **Owner (with highest permissions)** or **Role Based Access Control Administrator** on resource group level.

For more detailed information check out this Microsoft <a href="https://learn.microsoft.com/en-us/azure/logic-apps/authenticate-with-managed-identity?tabs=consumption" target="_blank">guide</a>

These steps will be needed for each Logic App that uses the **azuresentinel** / **RecordedFuture-MicrosoftSentinelConnection**
1. Go to the specific Logic App,  in the left menu click on the section _**Settings**_
2. Click on _**Identity**_
2. Click on the _**System Assinged**_ tab at the top of the page
3. If needed, Toggle the _**Status**_ to _**On**_ then click _**Save**_
![managedidentity1](images/managedidentity1.png)
4. Click on _**Azure role assignments**_
5. Click on _**Add new role assignment (Preview)**_
6. Set _**Scope**_ to _**Resource Group**_, choose **Subscription**, choose the **Resource Group** in which the Logic App is installed on and set the _**Role**_ to _**Microsoft Sentinel Contributor**_
![managedidentity2](images/managedidentity2.png)

7. Click _**Save**_

</details>
<details>
<summary>Expand to see azureloganalyticsdatacollector managed identity authorization guide</summary>

<br>

1. Identify your **Workspace ID** and **Workspace Key**, for guidance, see <a href="https://learn.microsoft.com/en-us/answers/questions/1154380/where-is-azure-is-the-primary-key-and-workspace-id" target="_blank">this</a>
1. Follow the steps outlined in the **azuresentinel** authorization guide
2. Add the role _**Log Analytics Contributor**_ instead of _**Microsoft Sentinel Contributor**_

</details>

<a id="how_to_obtain_Recorded_Future_API_token"></a>
### How to obtain Recorded Future API token

Recorded Future clients interested in API access for custom scripts or to enable a paid integration can request an API Token via this [Integration Support Ticket form](https://support.recordedfuture.com/hc/en-us/articles/4411077373587-Requesting-API-Tokens).  Please fill out the following fields, based on intended API usage.

<details>
<summary>Expand for example image of request form</summary>

![API request form](images/APIRequest2.png)
</details>
Select:

- Recorded Future API Services - Playbook Alert API
- Integration Partner Category - Recorded Future Owned Integrations (Premier)
- Premier Integration - Recorded Future Identity Intelligence for Azure Active Directory (Entra ID)
- Select Your Type of Inquiry (optional) - New Installation

Recorded Future Support will connect with your account team to confirm licensing and ensure the token is set up with the correct specifications and permissions. Additional questions about API token requests not covered by the above can be sent via email to our support team, support@recordedfuture.com.


<a id="configuration_parameters"></a>
### Configuring playbook parameters

The playbook parameters can be found and set in the Logic App designer:

<img src="./images/playbookparameters2.png" alt="Logic Apps Parameters #1" width="80%"/>

(Example above shows some parameters, number of parameters depends on playbook used)

### Playbook parameters

- **You need to create a Microsoft Entra ID group, and provide the Object ID as a parameter to the Playbook. For more information, see [Microsoft EntraID Groups](https://learn.microsoft.com/en-us/entra/fundamentals/how-to-manage-groups) documentation.**

| Parameter | Description |
|-|-|
| **entra_id_security_group_id** | Object ID of Microsoft EntraID Group for users at risk. You need to pre-create it by hand: search for "Groups" in Service search at the top of the page. For more information, see [Microsoft EntraID Groups](https://docs.microsoft.com/windows/security/identity-protection/access-control/active-directory-security-groups) documentation. If left empty, a user will **not** be placed in a Entra ID security group.  |
|**Confirm_user_as_risky**| Boolean parameter to determine if a user should be confirmed as risky. **Requires** Microsoft Entra ID P1 or P2 license to function properly. For more information about the Azure AD Identity Protection, click <a href="https://learn.microsoft.com/en-us/connectors/azureadip/" target="_blank">here</a> |
| **entra_id_domain** | (Optional, can be left empty) - in case your Microsoft EntraID domain is different from your organization domain, this parameter will be used to transform compromised credentials to find corresponding user in your Microsoft EntraID (ex. Compromised email: leaked@mycompany.com), your Microsoft EntraID domain: `@mycompany.onmicrosoft.com`, so you set parameter `entra_id_domain = mycompany.onmicrosoft.com` (**just domain, without "@"**), and search playbooks will replace the domain from the leaked email with the provided domain from the entra_id_domain parameter, before searching for the corresponding user in your Microsoft EntraID: `leaked@mycompany.com ->  leaked@mycompany.onmicrosoft.com`. (Lookup playbook - will still use the original email to Lookup the data). |
| **save_to_log_analytics_workspace** |(Optional, requires Log Analytics Workspace) - Boolean parameter to determine if the playbook should save the detailed Playbook Alert information to Log Analytics Workspace (LAW)|
| **create_incident** | (Optional, requires Microsoft Sentinel) - Boolean parameter to determine if the playbook should create a incident in Microsoft Sentinel|
|**playbook_alert_log_analytics_custom_log_name**| (Optional, requires Log Analytics Workspace) - Name of custom log where detailed Playbook Alert lookup information will be stored. Defaults to `RecordedFutureIdentity_PlaybookAlertResults_CL`|


<br/>

<a id="how_to_run_playbooks"></a>
## How to run Playbooks

`RFI-playbook-alert-importer` (`-law`/`-law-sentinel`) runs on a recurring schedule. It's possible to reschedule or change interval.

<img src="./images/runningPlaybooks2.png" alt="Empty Lookup results" width="90%"/>

<a id="how_to_access_log_analytics_custom_logs"></a>
## How to access Log Analytics Custom Logs

To see Log Analytics Custom Logs:
-   From then Azure Portal, navigate to the `Log Analytics workspaces` service
-   There, select the Log Analytic Workspace in which you have deployed the Solution
-   There, in the left-side menu click on Logs, and expand second left side menu, and select Custom Logs

<a id="customization"></a>
## Customization
Recorded Future Identity Solution is a baseline solution, there are ways to customize it to your preferred workflow.

#### Automatic remediation of identity exposures
The default configuration for this playbook provides remediation in the form of placing a user in a security group and confirming a user as risky (requires Microsoft Entra ID P1 or P2 license). Based on this there is other remediation actions that can be done, either manual or automatic. The various ways to configure automatic remediation are based on organizational needs and knowledge of the Azure environment to find a appropriate remediation path.


Depending of Entra ID licensing levels, some solutions available are:
 - Conditional Access Policies (requires Microsoft Entra ID P1 or P2 license) - More information <a href="https://learn.microsoft.com/en-us/entra/identity/conditional-access/overview" target="_blank">here<a>
 - Microsoft Entra ID Protection (requires Microsoft Entra ID P1 or P2 license) - More information <a href="https://learn.microsoft.com/en-us/entra/id-protection/overview-identity-protection" target="_blank"> here<a>
 - Microsoft Graph API - Powerful, no license requirements but requires extensive configuration - More information <a href="https://learn.microsoft.com/en-us/graph/identity-network-access-overview" target="_blank"> here</a>. For advanced guidance, please contact your Recorded Future Customer Success Manager.

#### Recorded Future Playbook Alert Onward Actions
Onward Actions is a way to keep the Recorded Future Playbook Alert up to date with actions taken in regards to a specific alert, to get a overview of actions taken on alerts.
By default the Playbook Alert Update steps have been configured with `added_actions_taken` set to `identity_novel_exposures.placed_in_risky_group`, if the solution is extended with actions such as blocking users or forcing password resets, you can submit this information to Recorded Future. Currently the following actions are supported:
| Action |
|-|
|identity_novel_exposures.enforced_password_reset|
|identity_novel_exposures.placed_in_risky_group|
|identity_novel_exposures.reviewed_incident_report|
|identity_novel_exposures.account_disabled_or_terminated|
|identity_novel_exposures.account_remediated|
|identity_novel_exposures.other|

To change/add actions, modify the items under `added_actions_taken` parameter in the Playbook Alerts Update step:

![Changing the Added actions taken parameter](images/added_actions_taken.png)

<a id="known_issues"></a>
## Known Issues

#### Risky Users (Microsoft Entra ID P1 or P2 license)
Microsoft Entra ID Protection is a premium feature. You need an Microsoft Entra ID P1 or P2 license to access the `riskDetection` API (note: P1 licenses receive limited risk information). The `riskyUsers` API is only available to Microsoft Entra ID P2 licenses only. If your organization does not have P1 or P2 license, then the `Confirm as risky user as compromised` step will fail, but the run will continue and complete.


#### Playbook Alert set to resolved but not added to Security Group
When the user that authorizes the Entra ID connector can search for a user in Entra ID, but lacks sufficient privileges to add the user to a group (e.g, same organization, but no permissions to modify users) there can be a scenario where the Logic App does not fail, and the Playbook Alert is incorrectly set to resolve, even if no remediation action has been done. A possible remediation can be that the user which authorizes the Entra ID connector has sufficient privileges to modify all users in  a organization.

<a id="useful_documentation"></a>
## Useful Azure documentation

Microsoft Sentinel:
- [Playbooks](https://docs.microsoft.com/azure/sentinel/automate-responses-with-playbooks)

Permissions / Roles:
- [Azure](https://docs.microsoft.com/azure/role-based-access-control/rbac-and-directory-admin-roles#azure-roles)
- [Log Analytics](https://docs.microsoft.com/azure/role-based-access-control/built-in-roles#log-analytics-contributor)
- [Logic Apps](https://docs.microsoft.com/azure/role-based-access-control/built-in-roles#logic-app-contributor)



<a id="how_to_contact_Recorded_Future"></a>
## How to contact Recorded Future

If you are already a Recorded Future client and wish to learn more about using Recorded Future’s Microsoft integrations, including how to obtain an API Token to enable an integration contact us at **support@recordedfuture.com**.

If you not a current Recorded Future client and wish to become one, contact **sales@recordedfuture.com** to setup a discussion with one of our business development associates.