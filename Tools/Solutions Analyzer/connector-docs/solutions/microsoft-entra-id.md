# Microsoft Entra ID

## Solution Information

| | |
|------------------------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID) |

## Data Connectors

This solution provides **1 data connector(s)**.

### [Microsoft Entra ID](../connectors/azureactivedirectory.md)

**Publisher:** Microsoft

Gain insights into Microsoft Entra ID by connecting Audit and Sign-in logs to Microsoft Sentinel to gather insights around Microsoft Entra ID scenarios. You can learn about app usage, conditional access policies, legacy auth relate details using our Sign-in logs. You can get information on your Self Service Password Reset (SSPR) usage, Microsoft Entra ID Management activities like user, group, role, app management using our Audit logs table. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/?linkid=2219715&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

**Permissions:**

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.
- **Diagnostic Settings** (/providers/microsoft.aadiam): read and write permissions to AAD diagnostic settings.

**Tenant Permissions:**
Requires GlobalAdmin, SecurityAdmin on the workspace's tenant

**Setup Instructions:**

> ⚠️ **Note**: These instructions were automatically generated from the connector's user interface definition file using AI and may not be fully accurate. Please verify all configuration steps in the Microsoft Sentinel portal.

**1. Connect Microsoft Entra ID logs to Microsoft Sentinel**

Select Microsoft Entra ID log types:
**Select Microsoft Entra ID Data Types**

In the Microsoft Sentinel portal, select which data types to enable:

- ☐ **Sign-In Logs**
- ☐ **Audit Logs**
- ☐ **Non-Interactive User Sign-In Log**
- ☐ **Service Principal Sign-In Logs**
- ☐ **Managed Identity Sign-In Logs**
- ☐ **Provisioning Logs**
- ☐ **ADFS Sign-In Logs**
- ☐ **User Risk Events**
- ☐ **Risky Users**
- ☐ **Network Access Traffic Logs**
- ☐ **Risky Service Principals**
- ☐ **Service Principal Risk Events**

Each data type may have specific licensing requirements. Review the information provided for each type in the portal before enabling.

> 💡 **Portal-Only Feature**: Data type selection is only available in the Microsoft Sentinel portal.

| | |
|--------------------------|---|
| **Tables Ingested** | `AADManagedIdentitySignInLogs` |
| | `AADNonInteractiveUserSignInLogs` |
| | `AADProvisioningLogs` |
| | `AADRiskyServicePrincipals` |
| | `AADRiskyUsers` |
| | `AADServicePrincipalRiskEvents` |
| | `AADServicePrincipalSignInLogs` |
| | `AADUserRiskEvents` |
| | `ADFSSignInLogs` |
| | `AuditLogs` |
| | `ManagedIdentitySignInLogs` |
| | `NetworkAccessTraffic` |
| | `NetworkAccessTrafficLogs` |
| | `NonInteractiveUserSignInLogs` |
| | `ProvisioningLogs` |
| | `RiskyServicePrincipals` |
| | `RiskyUsers` |
| | `ServicePrincipalRiskEvents` |
| | `ServicePrincipalSignInLogs` |
| | `SignInLogs` |
| | `SigninLogs` |
| | `UserRiskEvents` |
| **Connector Definition Files** | [template_AzureActiveDirectory.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Data%20Connectors/template_AzureActiveDirectory.JSON) |

[→ View full connector details](../connectors/azureactivedirectory.md)

## Tables Reference

This solution ingests data into **22 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AADManagedIdentitySignInLogs` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `AADNonInteractiveUserSignInLogs` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `AADProvisioningLogs` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `AADRiskyServicePrincipals` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `AADRiskyUsers` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `AADServicePrincipalRiskEvents` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `AADServicePrincipalSignInLogs` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `AADUserRiskEvents` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `ADFSSignInLogs` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `AuditLogs` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `ManagedIdentitySignInLogs` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `NetworkAccessTraffic` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `NetworkAccessTrafficLogs` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `NonInteractiveUserSignInLogs` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `ProvisioningLogs` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `RiskyServicePrincipals` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `RiskyUsers` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `ServicePrincipalRiskEvents` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `ServicePrincipalSignInLogs` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `SignInLogs` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `SigninLogs` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |
| `UserRiskEvents` | [Microsoft Entra ID](../connectors/azureactivedirectory.md) |

[← Back to Solutions Index](../solutions-index.md)
