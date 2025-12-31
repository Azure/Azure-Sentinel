# Microsoft Entra ID Protection

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-18 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID%20Protection](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID%20Protection) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Microsoft Entra ID Protection](../connectors/azureactivedirectoryidentityprotection.md)

## Tables Reference

### Internal Tables

The following **2 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`IdentityInfo`](../tables/identityinfo.md) | - | Analytics |
| [`SecurityAlert`](../tables/securityalert.md) | [Microsoft Entra ID Protection](../connectors/azureactivedirectoryidentityprotection.md) | Analytics |

## Content Items

This solution includes **6 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Playbooks | 5 |
| Analytic Rules | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Correlate Unfamiliar sign-in properties & atypical travel alerts](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID%20Protection/Analytic%20Rules/CorrelateIPC_Unfamiliar-Atypical.yaml) | High | InitialAccess | *Internal use:*<br>[`IdentityInfo`](../tables/identityinfo.md)<br>[`SecurityAlert`](../tables/securityalert.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Confirm Microsoft Entra ID Risky User - Alert Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID%20Protection/Playbooks/Confirm-EntraIDRiskyUser/alert-trigger/azuredeploy.json) | This playbook will set the Risky User property in Microsoft Entra ID using Graph API. | - |
| [Confirm Microsoft Entra ID Risky User - Incident Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID%20Protection/Playbooks/Confirm-EntraIDRiskyUser/incident-trigger/azuredeploy.json) | For each account entity included in the incident, this playbook will set the Risky User property in ... | - |
| [Dismiss Microsoft Entra ID Risky User - Alert Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID%20Protection/Playbooks/Dismiss-EntraIDRiskyUser/Dismiss-EntraIDRisky-Useralert-trigger/azuredeploy.json) | This playbook will dismiss the Risky User property in Microsoft Entra ID using Microsoft Entra ID Co... | - |
| [Dismiss Microsoft Entra ID Risky User – Incident Triggered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID%20Protection/Playbooks/Dismiss-EntraIDRiskyUser/Dismiss-EntraIDRisky-Userincident-trigger/azuredeploy.json) | This playbook will dismiss the Risky User property in Microsoft Entra ID using Microsoft Entra ID Co... | - |
| [Identity Protection response from Teams](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID%20Protection/Playbooks/IdentityProtection-TeamsBotResponse/azuredeploy.json) | Run this playbook on incidents which contains suspicious Microsoft Entra ID identities. For each acc... | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.0.3       | 07-07-2025                     | To enhance functionality, improve entity mappings, and update **playbook** configurations. |
| 3.0.2       | 07-04-2025                     | Updated ConnectivityCriteria Type in **Data Connector**.				   |
| 3.0.1       | 01-18-2024                     | Updated mapping in **Analytic Rule** for better correlation   | 
| 3.0.0       | 09-11-2023                     | Changes for rebranding from Azure Active Directory Identity Protection to Microsoft Entra ID Protection   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
