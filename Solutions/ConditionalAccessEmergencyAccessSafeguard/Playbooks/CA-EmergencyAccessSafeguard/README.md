# CA-EmergencyAccessSafeguard

## Summary

This playbook runs once a day and checks every Microsoft Entra Conditional Access policy. If either of your two emergency access (break-glass) accounts is not excluded from a policy, the playbook:

1. Adds the missing exclusion through Microsoft Graph.
2. Waits 15 seconds and re-reads the policy to confirm the change.
3. Emails a **remediation verified** or **remediation verification failed** message to the recipient you choose.

Policies that already exclude both accounts are left unchanged.

## Prerequisites

1. Two emergency access accounts in Microsoft Entra ID, and the object ID of each.
2. A mailbox to receive notifications.
3. Permission to grant Microsoft Graph application permissions to a managed identity (Privileged Role Administrator or Global Administrator).

## Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FConditionalAccessEmergencyAccessSafeguard%2FPlaybooks%2FCA-EmergencyAccessSafeguard%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FConditionalAccessEmergencyAccessSafeguard%2FPlaybooks%2FCA-EmergencyAccessSafeguard%2Fazuredeploy.json)

| Parameter | Description |
|---|---|
| PlaybookName | Name of the Logic App. |
| BreakGlassAccountId1 | Object ID of the first emergency access account. |
| BreakGlassAccountId2 | Object ID of the second emergency access account. |
| NotificationEmail | Email address that receives results. |
| GraphEndpoint | `https://graph.microsoft.com` (Commercial/GCC), `https://graph.microsoft.us` (GCC High) or `https://dod-graph.microsoft.us` (DoD). |

## Post-deployment

1. **Grant Graph permissions to the managed identity.** Assign `Policy.Read.All` and `Policy.ReadWrite.ConditionalAccess` (application permissions) to the playbook's system-assigned managed identity. Example:

```powershell
Connect-MgGraph -Scopes "AppRoleAssignment.ReadWrite.All","Application.Read.All"
$mi    = Get-MgServicePrincipal -Filter "displayName eq '<PlaybookName>'"
$graph = Get-MgServicePrincipal -Filter "appId eq '00000003-0000-0000-c000-000000000000'"
foreach ($perm in "Policy.Read.All","Policy.ReadWrite.ConditionalAccess") {
  $role = $graph.AppRoles | Where-Object { $_.Value -eq $perm }
  New-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $mi.Id -PrincipalId $mi.Id -ResourceId $graph.Id -AppRoleId $role.Id
}
```

2. **Authorize the Office 365 connection.** Open the `Office365-<PlaybookName>` API connection, select **Edit API connection**, select **Authorize**, sign in and save.

3. **Test safely.** Remove one emergency access exclusion from a Report-only or disabled test policy, run the playbook manually, and confirm the exclusion is restored and the verification email arrives.

## Considerations

- The playbook updates **every** Conditional Access policy that is missing either exclusion, including Report-only and disabled policies. Review your policies before enabling it in production.
- If you have a policy that deliberately targets your emergency access accounts (for example, to require phishing-resistant MFA for them), this playbook will add the exclusion to that policy too. Review those policies and adjust before deploying.
- Policies are read from a single Graph page. Very large tenants may need paging support.
