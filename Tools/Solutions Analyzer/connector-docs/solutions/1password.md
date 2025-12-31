# 1Password

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | 1Password |
| **Support Tier** | Partner |
| **Support Link** | [https://support.1password.com/](https://support.1password.com/) |
| **Categories** | domains |
| **First Published** | 2023-12-01 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password) |

## Data Connectors

This solution provides **3 data connector(s)**:

- [1Password](../connectors/1password.md)
- [1Password (Serverless)](../connectors/1password%28serverless%29.md)
- [1Password (Serverless)](../connectors/1passwordccpdefinition.md)

## Tables Reference

This solution uses **3 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`IP_Data`](../tables/ip-data.md) | - | Workbooks |
| [`OnePasswordEventLogs_CL`](../tables/onepasswordeventlogs-cl.md) | [1Password](../connectors/1password.md), [1Password (Serverless)](../connectors/1passwordccpdefinition.md), [1Password (Serverless)](../connectors/1password(serverless).md) | Analytics, Workbooks |
| [`SigninLogs`](../tables/signinlogs.md) | - | Workbooks |

## Content Items

This solution includes **19 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 18 |
| Workbooks | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [1Password - Changes to SSO configuration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20Changes%20to%20SSO%20configuration.yaml) | Medium | Persistence | [`OnePasswordEventLogs_CL`](../tables/onepasswordeventlogs-cl.md) |
| [1Password - Changes to firewall rules](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20Changes%20to%20firewall%20rules.yaml) | Medium | DefenseEvasion | [`OnePasswordEventLogs_CL`](../tables/onepasswordeventlogs-cl.md) |
| [1Password - Disable MFA factor or type for all user accounts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20Disable%20MFA%20factor%20or%20type%20for%20all%20user%20accounts.yaml) | High | DefenseEvasion | [`OnePasswordEventLogs_CL`](../tables/onepasswordeventlogs-cl.md) |
| [1Password - Log Ingestion Failure](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20Log%20Ingestion%20Failure.yaml) | Medium | DefenseEvasion | [`OnePasswordEventLogs_CL`](../tables/onepasswordeventlogs-cl.md) |
| [1Password - Manual account creation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20Manual%20account%20creation.yaml) | Medium | Persistence | [`OnePasswordEventLogs_CL`](../tables/onepasswordeventlogs-cl.md) |
| [1Password - New service account integration created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20New%20service%20account%20integration%20created.yaml) | Medium | Persistence | [`OnePasswordEventLogs_CL`](../tables/onepasswordeventlogs-cl.md) |
| [1Password - Non-privileged vault user permission change](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20Non-privileged%20vault%20user%20permission%20change.yaml) | Medium | Persistence | - |
| [1Password - Potential insider privilege escalation via group](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20Potential%20insider%20privilege%20escalation%20via%20group.yaml) | Medium | PrivilegeEscalation | [`OnePasswordEventLogs_CL`](../tables/onepasswordeventlogs-cl.md) |
| [1Password - Potential insider privilege escalation via vault](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20Potential%20insider%20privilege%20escalation%20via%20vault.yaml) | Medium | PrivilegeEscalation | [`OnePasswordEventLogs_CL`](../tables/onepasswordeventlogs-cl.md) |
| [1Password - Privileged vault permission change](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20Privileged%20vault%20permission%20change.yaml) | High | Persistence | - |
| [1Password - Secret extraction post vault access change by administrator](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20Secret%20Extraction%20Post%20Vault%20Access%20Change%20By%20Administrator.yaml) | High | CredentialAccess | [`OnePasswordEventLogs_CL`](../tables/onepasswordeventlogs-cl.md) |
| [1Password - Service account integration token adjustment](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20Service%20account%20integration%20token%20adjustment.yaml) | Medium | DefenseEvasion | [`OnePasswordEventLogs_CL`](../tables/onepasswordeventlogs-cl.md) |
| [1Password - Successful anomalous sign-in](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20Successful%20anomalous%20sign-in.yaml) | Low | InitialAccess | [`OnePasswordEventLogs_CL`](../tables/onepasswordeventlogs-cl.md) |
| [1Password - User account MFA settings changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20User%20account%20MFA%20settings%20changed.yaml) | Medium | Persistence, DefenseEvasion | [`OnePasswordEventLogs_CL`](../tables/onepasswordeventlogs-cl.md) |
| [1Password - User added to privileged group](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20User%20added%20to%20privileged%20group.yaml) | Medium | Persistence | - |
| [1Password - Vault export](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20Vault%20Export.yaml) | Low | CredentialAccess | [`OnePasswordEventLogs_CL`](../tables/onepasswordeventlogs-cl.md) |
| [1Password - Vault export post account creation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20Vault%20Export%20Post%20Account%20Creation.yaml) | Medium | CredentialAccess, Persistence | [`OnePasswordEventLogs_CL`](../tables/onepasswordeventlogs-cl.md) |
| [1Password - Vault export prior to account suspension or deletion](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Analytic%20Rules/1Password%20-%20Vault%20export%20prior%20to%20account%20suspension%20or%20deletion.yaml) | Medium | CredentialAccess | [`OnePasswordEventLogs_CL`](../tables/onepasswordeventlogs-cl.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [1Password](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/Workbooks/1Password.json) | [`IP_Data`](../tables/ip-data.md)<br>[`OnePasswordEventLogs_CL`](../tables/onepasswordeventlogs-cl.md)<br>[`SigninLogs`](../tables/signinlogs.md) |

## Additional Documentation

> 📄 *Source: [1Password/README.md](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/1Password/README.md)*

# 1Password (Preview)

## Overview

The key function of this Solution is to retrieve sign-in attempts, item usage, and audit events logs from your 1Password Business account using the 1Password Events Reporting API, and store it in an Azure Log Analytics Workspace using Microsoft cloud native features.

## Azure services needed

### Required

- [1Password Business account](https://1password.com/business)
- [1Password Events API key](https://support.1password.com/events-reporting/#appendix-issue-or-revoke-bearer-tokens)
- [Microsoft Azure](https://azure.microsoft.com/free)
- [Microsoft Sentinel](https://azure.microsoft.com/products/microsoft-sentinel/)
- Contributor role with User Access Administrator role on the Microsoft Sentinel Resource Group <br>
**or**
- Owner on the Microsoft Sentinel Resource Group 

## Automated Installation

Installing the 1Password Solution for Microsoft Sentinel is easy and can be completed in only a few minutes. 
Just click the button below to get started with the deployment wizard. <br>

[![Deploy To Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazure.svg?sanitize=true)](https://aka.ms/sentinel-OnePassword-azuredeploy)

> NOTE: To deploy the solution, the Azure user account executing the deployment needs to have `Owner` permissions on the Microsoft Sentinel `Resource Group` in Azure.<br>
> This is required to assign the correct RBAC role to the managed identity of the FunctionApp!  

## Manual Installation using the ARM template

<details>

<summary>Deployment steps</summary>
<br/>

## Manual Installation using the ARM template

1. Install the data connector using the ARM template or use this link to skip the steps below

![Alt text](https://github.com/Azure/Azure-Sentinel/blob/f3655ba6a4891acdda67c3c3bf2414401de323b6/Solutions/1Password/images/image.png)

2. After the deployment of the template has completed open the Microsoft Sentinel portal and select the data connector

![Alt text](https://github.com/Azure/Azure-Sentinel/blob/f3655ba6a4891acdda67c3c3bf2414401de323b6/Solutions/1Password/images/dataconnector.png)

3. Select the `Open connector page` button to open the data connector configuration
4. click on the `Deploy to Azure` button<br>
This will open a new browser page containing a deployment wizard in Microsoft Azure.<br>
Fill in all the required fields and select `create` on the last page.

![Alt text](https://github.com/Azure/Azure-Sentinel/blob/fd9527ab432fa3e4e6115e4ee823ed5c2a92c163/Solutions/1Password/images/summary.png)

The required resources for the deployment will now be created.

</details>

## Deployed Resources

The 1Password Solution for Microsoft Sentinel is comprised of following Azure resources:

> Click on the topics below to fold them out.

<details>

<summary>Resource Group</summary>
<br/>

### **Resource Group**


*[Content truncated...]*

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                     |
|-------------|--------------------------------|----------------------------------------|
| 3.0.2       | 17-09-2024                     | Added new CCP **Data Connector**.               | 
| 3.0.1       | 27-06-2024                     | Fixed typo error in **Analytic Rule**  1Password - Changes to SSO configuration.yaml. </br> Fixed Logo link and typo in CreateUI.              |
| 3.0.0       | 12-06-2024                     | Initial Solution Release.               |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
