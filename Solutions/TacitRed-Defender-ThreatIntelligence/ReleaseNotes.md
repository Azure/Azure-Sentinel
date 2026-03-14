# Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History** |
|-------------|--------------------------------|--------------------|
| 3.0.2       | 10-03-2026                     | Fixed policy-restricted deployment failures for the Function App resources. Set `allowSharedKeyAccess: false`, migrated host storage to identity-based `AzureWebJobsStorage__accountName`, and bound Application Insights to the selected Log Analytics workspace with `WorkspaceResourceId` to avoid Azure creating a managed resource group that can be denied by tenant policy. Removed automatic storage role assignments from ARM so Content Hub deployments don't require `Microsoft.Authorization/roleAssignments/write`; post-deployment guidance still requires manually assigning `Storage Blob Data Owner` to the Function App managed identity on the deployed storage account. |
| 3.0.1       | 11-02-2026                     | Fixed deployment failure: Restored functionCode.zip package removed in prior commit. Removed workspace-scoped roleAssignments from Function App template to resolve InvalidTemplate error during Content Hub deployment. |
| 3.0.0       | 09-12-2025                     | Initial release of TacitRed Defender Threat Intelligence solution with Azure Function and Logic App playbook for syncing TacitRed compromised credentials to Microsoft Defender Threat Intelligence. |
