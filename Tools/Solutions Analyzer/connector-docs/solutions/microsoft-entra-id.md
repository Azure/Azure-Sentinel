# Microsoft Entra ID

## Solution Information

| Property | Value |
|----------|-------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-05-16 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID) |\n\n## Data Connectors

This solution provides **1 data connector(s)**.

### Microsoft Entra ID

**Publisher:** Microsoft

Gain insights into Microsoft Entra ID by connecting Audit and Sign-in logs to Microsoft Sentinel to gather insights around Microsoft Entra ID scenarios. You can learn about app usage, conditional access policies, legacy auth relate details using our Sign-in logs. You can get information on your Self Service Password Reset (SSPR) usage, Microsoft Entra ID Management activities like user, group, role, app management using our Audit logs table. For more information, see the [Microsoft Sentinel documentation](https://go.microsoft.com/fwlink/?linkid=2219715&wt.mc_id=sentinel_dataconnectordocs_content_cnl_csasci).

**Tables Ingested:**

- `AADManagedIdentitySignInLogs`
- `AADNonInteractiveUserSignInLogs`
- `AADProvisioningLogs`
- `AADRiskyServicePrincipals`
- `AADRiskyUsers`
- `AADServicePrincipalRiskEvents`
- `AADServicePrincipalSignInLogs`
- `AADUserRiskEvents`
- `ADFSSignInLogs`
- `AuditLogs`
- `ManagedIdentitySignInLogs`
- `NetworkAccessTraffic`
- `NetworkAccessTrafficLogs`
- `NonInteractiveUserSignInLogs`
- `ProvisioningLogs`
- `RiskyServicePrincipals`
- `RiskyUsers`
- `ServicePrincipalRiskEvents`
- `ServicePrincipalSignInLogs`
- `SignInLogs`
- `SigninLogs`
- `UserRiskEvents`

**Connector Definition Files:**

- [template_AzureActiveDirectory.JSON](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Microsoft%20Entra%20ID/Data%20Connectors/template_AzureActiveDirectory.JSON)

## Tables Reference

This solution ingests data into **22 table(s)**:

| Table | Used By Connectors |
|-------|-------------------|
| `AADManagedIdentitySignInLogs` | Microsoft Entra ID |
| `AADNonInteractiveUserSignInLogs` | Microsoft Entra ID |
| `AADProvisioningLogs` | Microsoft Entra ID |
| `AADRiskyServicePrincipals` | Microsoft Entra ID |
| `AADRiskyUsers` | Microsoft Entra ID |
| `AADServicePrincipalRiskEvents` | Microsoft Entra ID |
| `AADServicePrincipalSignInLogs` | Microsoft Entra ID |
| `AADUserRiskEvents` | Microsoft Entra ID |
| `ADFSSignInLogs` | Microsoft Entra ID |
| `AuditLogs` | Microsoft Entra ID |
| `ManagedIdentitySignInLogs` | Microsoft Entra ID |
| `NetworkAccessTraffic` | Microsoft Entra ID |
| `NetworkAccessTrafficLogs` | Microsoft Entra ID |
| `NonInteractiveUserSignInLogs` | Microsoft Entra ID |
| `ProvisioningLogs` | Microsoft Entra ID |
| `RiskyServicePrincipals` | Microsoft Entra ID |
| `RiskyUsers` | Microsoft Entra ID |
| `ServicePrincipalRiskEvents` | Microsoft Entra ID |
| `ServicePrincipalSignInLogs` | Microsoft Entra ID |
| `SignInLogs` | Microsoft Entra ID |
| `SigninLogs` | Microsoft Entra ID |
| `UserRiskEvents` | Microsoft Entra ID |

---\n\n[← Back to Solutions Index](../solutions-index.md)\n