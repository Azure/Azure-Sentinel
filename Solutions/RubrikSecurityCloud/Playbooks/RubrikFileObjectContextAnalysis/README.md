# Rubrik File Object Context Analysis

## Summary

This playbook will retrieve policy hits from Rubrik Security Cloud for a given object, for a particular file, folder, or file share.

### Prerequisites

1. The Rubrik Security Cloud solution should be configured to [connect to Rubrik Security Cloud API end points using a Service Account](https://docs.rubrik.com/en-us/saas/saas/polaris_api_access_with_service_accounts.html), the service account should be assigned a role that includes the relevant privileges necessary to perform the desired operations (see [Roles and Permissions](https://docs.rubrik.com/en-us/saas/saas/common/roles_and_permissions.html) in the Rubrik Security Cloud user guide).
2. Obtain Teams GroupId and ChannelId
    * Create a Team with public channel.
    * Click on three dots (...) present on right side of the your newly created teams channel and Get link to the channel.
    * Copy the text from the link between /channel and /, decode it using online url decoder and copy it to use as channelId.
    * Copy the text of groupId parameter from link to use as groupId. 
3. Store Service account credentials in Key Vault and obtain keyvault name and tenantId
    * Create a Key Vault with unique name
    * Go to KeyVault -> secrets, click on Generate/import and create 'Rubrik-AS-Int-ClientId' & 'Rubrik-AS-Int-ClientSecret' for storing client_id and client_secret respectively
    NOTE: Make sure Permission model in Access Configuration of Keyvault is selected to Vault access policy. If not then change it to 'Vault access policy'

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * Playbook Name: Enter the playbook name here
    * Teams Group Id: Id of the Teams Group where the adaptive card will be posted
    * Teams Channel Id: Id of the Teams Channel where the adaptive card will be posted
    * Keyvault Name: Name of keyvault where secrets are stored.
    * Tenant Id: TenantId where keyvault is located.
    * BaseUrl: BaseUrl of the RubrikApi instance.
    * LogAnalyticsWorkspaceId: Id of log analytics workspace where you want to ingest data in Microsoft Sentinel.
    * LogAnalyticsWorkspaceKey: PrimaryKey of log analytics workspace where you want to ingest data in Microsoft Sentinel.
    * PolicyHitsTableName: Tablename to store policyhits data of file object in Log Analytics Workspace.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikFileObjectContextAnalysis%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikFileObjectContextAnalysis%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection like keyvault, azureloganalytics, teams.
1. Go to your logic app -> API connections -> Select keyvault connection resource
2. Go to General -> edit API connection
3. Click the keyvault connection resource
4. Click edit API connection
5. Click Authorize
6. Sign in
7. Click Save
8. Repeat steps for other connections

#### b. Add Access policy in Keyvault

Add access policy for playbook's managed identity to read, write secrets of keyvault.

1. Go to logic app → <your logic app> → identity → System assigned Managed identity and copy Object (principal) ID.
2. Go to keyvaults → <your keyvault> → Access policies → create.
3. Select all keys & secrets permissions. Click next.
4. In principal section, search by copied object ID. Click next.
5. Click review + create.
