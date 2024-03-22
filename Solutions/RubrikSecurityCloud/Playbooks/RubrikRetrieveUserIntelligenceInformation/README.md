# Rubrik Retrieve User Intelligence Information
## Summary
This playbook queries Rubrik Security Cloud to get risk detail and policy hits details for a username or email address, and enriches the incident by adding incident comment
### Prerequisites
1. The Rubrik Security Cloud solution should be configured to [connect to Rubrik Security Cloud API end points using a Service Account](https://docs.rubrik.com/en-us/saas/saas/polaris_api_access_with_service_accounts.html), the service account should be assigned a role that includes the relevant privileges necessary to perform the desired operations (see [Roles and Permissions](https://docs.rubrik.com/en-us/saas/saas/common/roles_and_permissions.html) in the Rubrik Security Cloud user guide).
### Deployment instructions
1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
* PlaybookName: Enter the playbook name here.
* LogAnalyticsWorkspaceId: Id of the log analytics workspace where you want to ingest data in Microsoft Sentinel.
* LogAnalyticsWorkspaceKey: PrimaryKey of log analytics workspace where you want to ingest data in Microsoft Sentinel.
* UserDetailsTableName: Table name to store userdetails in Log Analytics Workspace.
* UserPolicyHitsTableName: Table name to store user policy hits data into Log Analytics Workspace.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikRetrieveUserIntelligenceInformation%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikRetrieveUserIntelligenceInformation%2Fazuredeploy.json)
### Post-Deployment instructions
#### a. Authorize connections
Once deployment is complete, authorize each connection like keyvault, azureloganalytics.
1. Go to your logic app -> API connections -> Select keyvault connection resource
2. Go to General -> edit API connection
3. Click the keyvault connection resource
4. Click edit API connection
5. Click Authorize
6. Sign in
7. Click Save
8. Repeat steps for other connections
#### b. Assign Role to add a comment in the incident
After authorizing each connection, assign a role to this playbook.
1. Go to Log Analytics Workspace → <your workspace> → Access Control → Add
2. Add role assignment
3. Assignment type: Job function roles
4. Role: Microsoft Sentinel Contributor
5. Members: select managed identity for "assigned access to" and add your logic app as a member.
6. Click on review+assign
