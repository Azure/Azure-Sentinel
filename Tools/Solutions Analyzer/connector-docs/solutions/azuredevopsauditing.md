# AzureDevOpsAuditing

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Microsoft Corporation |
| **Support Tier** | Microsoft |
| **Support Link** | [https://support.microsoft.com/](https://support.microsoft.com/) |
| **Categories** | domains |
| **First Published** | 2022-09-20 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Azure DevOps Audit Logs (via Codeless Connector Platform)](../connectors/azuredevopsauditlogs.md)

## Tables Reference

This solution uses **2 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) | [Azure DevOps Audit Logs (via Codeless Connector Platform)](../connectors/azuredevopsauditlogs.md) | Analytics, Hunting |
| [`false`](../tables/false.md) | - | Analytics |

### Internal Tables

The following **1 table(s)** are used internally by this solution's playbooks:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`SecurityAlert`](../tables/securityalert.md) | - | Analytics, Hunting |

## Content Items

This solution includes **37 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 19 |
| Hunting Queries | 17 |
| Parsers | 1 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Azure DevOps Administrator Group Monitoring](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/AzDOAdminGroupAdditions.yaml) | Medium | Persistence | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md)<br>[`false`](../tables/false.md) |
| [Azure DevOps Agent Pool Created Then Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADOAgentPoolCreatedDeleted.yaml) | High | DefenseEvasion | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps Audit Detection for known malicious tooling](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADOMaliciousToolingDetections1.yaml) | High | Collection | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps Audit Stream Disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADOAuditStreamDisabled.yaml) | High | DefenseEvasion | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps Build Variable Modified by New User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADOVariableModifiedByNewUser.yaml) | Medium | DefenseEvasion | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps New Extension Added](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADONewExtensionAdded.yaml) | Low | Persistence | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps PAT used with Browser](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADOPATUsedWithBrowser.yaml) | Medium | CredentialAccess | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps Personal Access Token (PAT) misuse](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/AzDOPatSessionMisuse.yaml) | High | Execution, Impact | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps Pipeline Created and Deleted on the Same Day](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/AzDOPipelineCreatedDeletedOneDay.yaml) | Medium | Execution | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps Pipeline modified by a new user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADOPipelineModifiedbyNewUser.yaml) | Medium | Execution, DefenseEvasion | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Azure DevOps Pull Request Policy Bypassing - Historic allow list](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/AzDOHistoricPrPolicyBypassing.yaml) | Medium | Persistence | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps Retention Reduced](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADORetentionReduced.yaml) | Low | DefenseEvasion | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps Service Connection Abuse](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/AzDOServiceConnectionUsage.yaml) | Medium | Persistence, Impact | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps Service Connection Addition/Abuse - Historic allow list](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/AzDOHistoricServiceConnectionAdds.yaml) | Medium | Persistence, Impact | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps Variable Secret Not Secured](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADOSecretNotSecured.yaml) | Medium | CredentialAccess | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [External Upstream Source Added to Azure DevOps Feed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ExternalUpstreamSourceAddedtoAzureDevOpsFeed.yaml) | Medium | InitialAccess | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [NRT Azure DevOps Audit Stream Disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/NRT_ADOAuditStreamDisabled.yaml) | High | DefenseEvasion | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [New Agent Added to Pool by New User or Added to a New OS Type](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/NewAgentAddedToPoolbyNewUserorofNewOS.yaml) | Medium | Execution | - |
| [New PA, PCA, or PCAS added to Azure DevOps](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/NewPAPCAPCASaddedtoADO.yaml) | Medium | InitialAccess | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |

### Hunting Queries

| Name | Tactics | Tables Used |
|:-----|:--------|:------------|
| [Azure DevOps - Build Check Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADOBuildCheckDeleted.yaml) | DefenseEvasion | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps - Build Deleted After Pipeline Modification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADOBuildDeletedAfterPipelineMod.yaml) | Persistence | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps - Internal Upstream Package Feed Added](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADOInternalUpstreamPacakgeFeedAdded.yaml) | InitialAccess | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps - New Agent Pool Created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADONewAgentPoolCreated.yaml) | DefenseEvasion | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps - New PAT Operation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADONewPATOperation.yaml) | DefenseEvasion | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps - New Package Feed Created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADONewPackageFeedCreated.yaml) | InitialAccess | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Azure DevOps - New Release Approver](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADONewReleaseApprover.yaml) | DefenseEvasion | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps - New Release Pipeline Created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADOReleasePipelineCreated.yaml) | Persistence, Execution, PrivilegeEscalation | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md)<br>*Internal use:*<br>[`SecurityAlert`](../tables/securityalert.md) |
| [Azure DevOps - Variable Created and Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADOVariableCreatedDeleted.yaml) | DefenseEvasion | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps Display Name Changes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/AzDODisplayNameSwapping.yaml) | Persistence, DefenseEvasion | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps Pull Request Policy Bypassing](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/AzDOPrPolicyBypassers.yaml) | Execution | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps- Addtional Org Admin added](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/Addtional%20Org%20Admin%20Added.yaml) | Persistence, DefenseEvasion | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps- Guest users access enabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/Guest%20users%20access%20enabled.yaml) | Persistence, DefenseEvasion | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps- Microsoft Entra ID Protection Conditional Access Disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/EntraID%20Conditional%20Access%20Disabled.yaml) | Persistence, DefenseEvasion | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps- Project visibility changed to public](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/Project%20visibility%20changed%20to%20public.yaml) | Collection | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps- Public project created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/Public%20project%20created.yaml) | Persistence, DefenseEvasion | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |
| [Azure DevOps- Public project enabled by admin](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/Public%20Projects%20enabled.yaml) | Persistence, DefenseEvasion | [`ADOAuditLogs_CL`](../tables/adoauditlogs-cl.md) |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [ADOAuditLogs](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Parsers/ADOAuditLogs.yaml) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                         |
|-------------|--------------------------------|----------------------------------------------------------------------------|
| 3.0.6       | 19-06-2025                     | Updated **Data Connector** instructions to include a note about User permissions.                                   |
| 3.0.5       | 05-05-2025                     | Updated **Data Connector** instructions.                                   |
| 3.0.4       | 15-04-2025                     | Added new **CCP Connector** - Azure DevOps Audit Logs. 					   		   |
| 3.0.3       | 16-07-2024                     | Updated the **Analytic rules** for missing TTP.					   		   |
| 3.0.2       | 23-01-2024                     | Updated the solution to fix **Analytic Rules** deployment issue.            |
| 3.0.1       | 27-11-2023                     | Added new Entity Mappings to **Analytic Rules**.                            |
| 3.0.0       | 06-11-2023                     | Modified text as there is rebranding from Azure Active Directory to Microsoft Entra ID.   |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
