# ADOAuditLogs_CL

## Solutions (1)

This table is used by the following solutions:

- [AzureDevOpsAuditing](../solutions/azuredevopsauditing.md)

## Connectors (1)

This table is ingested by the following connectors:

- [Azure DevOps Audit Logs (via Codeless Connector Platform)](../connectors/azuredevopsauditlogs.md)

---

## Content Items Using This Table (35)

### Analytic Rules (18)

**In solution [AzureDevOpsAuditing](../solutions/azuredevopsauditing.md):**
- [Azure DevOps Administrator Group Monitoring](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/AzDOAdminGroupAdditions.yaml)
- [Azure DevOps Agent Pool Created Then Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADOAgentPoolCreatedDeleted.yaml)
- [Azure DevOps Audit Detection for known malicious tooling](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADOMaliciousToolingDetections1.yaml)
- [Azure DevOps Audit Stream Disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADOAuditStreamDisabled.yaml)
- [Azure DevOps Build Variable Modified by New User](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADOVariableModifiedByNewUser.yaml)
- [Azure DevOps New Extension Added](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADONewExtensionAdded.yaml)
- [Azure DevOps PAT used with Browser](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADOPATUsedWithBrowser.yaml)
- [Azure DevOps Personal Access Token (PAT) misuse](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/AzDOPatSessionMisuse.yaml)
- [Azure DevOps Pipeline Created and Deleted on the Same Day](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/AzDOPipelineCreatedDeletedOneDay.yaml)
- [Azure DevOps Pipeline modified by a new user](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADOPipelineModifiedbyNewUser.yaml)
- [Azure DevOps Pull Request Policy Bypassing - Historic allow list](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/AzDOHistoricPrPolicyBypassing.yaml)
- [Azure DevOps Retention Reduced](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADORetentionReduced.yaml)
- [Azure DevOps Service Connection Abuse](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/AzDOServiceConnectionUsage.yaml)
- [Azure DevOps Service Connection Addition/Abuse - Historic allow list](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/AzDOHistoricServiceConnectionAdds.yaml)
- [Azure DevOps Variable Secret Not Secured](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ADOSecretNotSecured.yaml)
- [External Upstream Source Added to Azure DevOps Feed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/ExternalUpstreamSourceAddedtoAzureDevOpsFeed.yaml)
- [NRT Azure DevOps Audit Stream Disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/NRT_ADOAuditStreamDisabled.yaml)
- [New PA, PCA, or PCAS added to Azure DevOps](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Analytic%20Rules/NewPAPCAPCASaddedtoADO.yaml)

### Hunting Queries (17)

**In solution [AzureDevOpsAuditing](../solutions/azuredevopsauditing.md):**
- [Azure DevOps - Build Check Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADOBuildCheckDeleted.yaml)
- [Azure DevOps - Build Deleted After Pipeline Modification](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADOBuildDeletedAfterPipelineMod.yaml)
- [Azure DevOps - Internal Upstream Package Feed Added](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADOInternalUpstreamPacakgeFeedAdded.yaml)
- [Azure DevOps - New Agent Pool Created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADONewAgentPoolCreated.yaml)
- [Azure DevOps - New PAT Operation](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADONewPATOperation.yaml)
- [Azure DevOps - New Package Feed Created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADONewPackageFeedCreated.yaml)
- [Azure DevOps - New Release Approver](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADONewReleaseApprover.yaml)
- [Azure DevOps - New Release Pipeline Created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADOReleasePipelineCreated.yaml)
- [Azure DevOps - Variable Created and Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/ADOVariableCreatedDeleted.yaml)
- [Azure DevOps Display Name Changes](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/AzDODisplayNameSwapping.yaml)
- [Azure DevOps Pull Request Policy Bypassing](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/AzDOPrPolicyBypassers.yaml)
- [Azure DevOps- Addtional Org Admin added](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/Addtional%20Org%20Admin%20Added.yaml)
- [Azure DevOps- Guest users access enabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/Guest%20users%20access%20enabled.yaml)
- [Azure DevOps- Microsoft Entra ID Protection Conditional Access Disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/EntraID%20Conditional%20Access%20Disabled.yaml)
- [Azure DevOps- Project visibility changed to public](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/Project%20visibility%20changed%20to%20public.yaml)
- [Azure DevOps- Public project created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/Public%20project%20created.yaml)
- [Azure DevOps- Public project enabled by admin](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/AzureDevOpsAuditing/Hunting%20Queries/Public%20Projects%20enabled.yaml)

---

**Browse:**

- [← Back to Tables Index](../tables-index.md)
- [Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
