# Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|-------------|--------------------------------|--------------------|
| 3.0.2       | 20-02-2026                     | Fixed RequestDisallowedByPolicy error on Function App storage account in policy-restricted subscriptions. Set `allowSharedKeyAccess: false`, migrated to identity-based `AzureWebJobsStorage__accountName`, added Storage Blob Data Owner + Queue Data Contributor + Table Data Contributor RBAC roles for managed identity. Also fixed InvalidTemplate on hyphenated workspace names. |
| 3.0.1       | 11-02-2026                     | Fixed deployment failure: Restored functionCode.zip package removed in prior commit. Removed workspace-scoped roleAssignments from Function App template to resolve InvalidTemplate error during Content Hub deployment. |
| 3.0.0       | 09-12-2025                     | Initial release of TacitRed Defender Threat Intelligence solution with Azure Function and Logic App playbook for syncing TacitRed compromised credentials to Microsoft Defender Threat Intelligence. |
