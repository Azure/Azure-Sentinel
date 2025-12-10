# Microsoft Entra ID

| | |
|----------|-------|
| **Connector ID** | `AzureActiveDirectory` |
| **Publisher** | Microsoft |
| **Tables Ingested** | [`AADManagedIdentitySignInLogs`](../tables-index.md#aadmanagedidentitysigninlogs), [`AADNonInteractiveUserSignInLogs`](../tables-index.md#aadnoninteractiveusersigninlogs), [`AADProvisioningLogs`](../tables-index.md#aadprovisioninglogs), [`AADRiskyServicePrincipals`](../tables-index.md#aadriskyserviceprincipals), [`AADRiskyUsers`](../tables-index.md#aadriskyusers), [`AADServicePrincipalRiskEvents`](../tables-index.md#aadserviceprincipalriskevents), [`AADServicePrincipalSignInLogs`](../tables-index.md#aadserviceprincipalsigninlogs), [`AADUserRiskEvents`](../tables-index.md#aaduserriskevents), [`ADFSSignInLogs`](../tables-index.md#adfssigninlogs), [`AuditLogs`](../tables-index.md#auditlogs), [`ManagedIdentitySignInLogs`](../tables-index.md#managedidentitysigninlogs), [`NetworkAccessTraffic`](../tables-index.md#networkaccesstraffic), [`NetworkAccessTrafficLogs`](../tables-index.md#networkaccesstrafficlogs), [`NonInteractiveUserSignInLogs`](../tables-index.md#noninteractiveusersigninlogs), [`ProvisioningLogs`](../tables-index.md#provisioninglogs), [`RiskyServicePrincipals`](../tables-index.md#riskyserviceprincipals), [`RiskyUsers`](../tables-index.md#riskyusers), [`ServicePrincipalRiskEvents`](../tables-index.md#serviceprincipalriskevents), [`ServicePrincipalSignInLogs`](../tables-index.md#serviceprincipalsigninlogs), [`SignInLogs`](../tables-index.md#signinlogs), [`SigninLogs`](../tables-index.md#signinlogs), [`UserRiskEvents`](../tables-index.md#userriskevents) |
| **Used in Solutions** | [Microsoft Entra ID](../solutions/microsoft-entra-id.md) |
| **Connector Definition Files** | [template_AzureActiveDirectory.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Data%20Connectors/template_AzureActiveDirectory.JSON) |

Gain insights into Microsoft Entra ID by connecting Audit and Sign-in logs to Microsoft Sentinel to gather insights around Microsoft Entra ID scenarios. You can learn about app usage, conditional access policies, legacy auth relate details using our Sign-in logs. You can get information on your Self Service Password Reset (SSPR) usage, Microsoft Entra ID Management activities like user, group, role, app management using our Audit logs table. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/?linkid=2219715&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

## Permissions

**Resource Provider Permissions:**
- **Workspace** (Workspace): read and write permissions.
- **Diagnostic Settings** (/providers/microsoft.aadiam): read and write permissions to AAD diagnostic settings.

**Tenant Permissions:**
Requires GlobalAdmin, SecurityAdmin on the workspace's tenant

## Setup Instructions

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

[← Back to Connectors Index](../connectors-index.md)
