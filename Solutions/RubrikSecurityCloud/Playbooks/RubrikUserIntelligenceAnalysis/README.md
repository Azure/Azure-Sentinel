# Rubrik User Intelligence Analysis
## Summary
This playbook queries Rubrik Security Cloud to get user sensitive data and update severity of incident accordingly. This playbook calls the RubrikRetrieveUserIntelligenceInformation playbook internally to get user risk details and policy hits details to enrich the incident
### Prerequisites
1. The Rubrik Security Cloud solution should be configured to [connect to Rubrik Security Cloud API end points using a Service Account](https://docs.rubrik.com/en-us/saas/saas/polaris_api_access_with_service_accounts.html), the service account should be assigned a role that includes the relevant privileges necessary to perform the desired operations (see [Roles and Permissions](https://docs.rubrik.com/en-us/saas/saas/common/roles_and_permissions.html) in the Rubrik Security Cloud user guide).
2. Store Service account credentials in Key Vault and obtain keyvault name and tenantId
    * Create a Key Vault with a unique name
    * Go to KeyVault -> secrets, click on Generate/import and create 'Rubrik-AS-Int-ClientId' & 'Rubrik-AS-Int-ClientSecret' for storing client_id and client_secret respectively
    **NOTE:** Make sure the Permission model in the Access Configuration of Keyvault is selected to the Vault access policy. If not then change it to **'Vault access policy'**
3. Make sure that RubrikRetrieveUserIntelligenceInformation playbook is deployed before deploying RubrikUserIntelligenceAnalysis playbook.
### Deployment instructions
1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
* PlaybookName: Enter the playbook name here.
* KeyvaultName: Name of keyvault where secrets are stored.
* TenantId: TenantId where keyvault is located.
* BaseUrl: Baseurl of the RubrikApi instance.
* RiskPolicyHitsPlaybookName: Playbook name which is deployed as part of prerequisites

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikUserIntelligenceAnalysis%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikUserIntelligenceAnalysis%2Fazuredeploy.json)
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
#### c. Add Access policy in Keyvault
Add access policy for the playbook's managed identity to read, and write secrets of key vault.
1. Go to the logic app → <your logic app> → identity → System assigned Managed identity and copy Object (principal) ID.
2. Go to keyvaults → <your keyvault> → Access policies → create.
3. Select all keys & secrets permissions. Click next.
4. In the principal section, search by copied object ID. Click next.
5. Click review + create.
#### d. Configurations in Microsoft Sentinel
1. In Microsoft Sentinel, Configure the analytic rules to trigger an incident.
  * Analytic Rule must contain at least one of the below fields mapped in Custom Details to successfully run this playbook.
    * Username
    * Email
2. In Microsoft Sentinel, Configure the automation rules to trigger the playbook. 
  * Go to Microsoft Sentinel -> <your workspace> -> Automation 
  * Click on **Create** -> **Automation rule**
  * Provide a name for your rule
  * In the Analytic rule name condition, select the analytic rule that you have created.
  * In Actions dropdown select **Run playbook**
  * In the second dropdown select your deployed playbook
  * Click on **Apply**
  * Save the Automation rule.
**NOTE:** If you want to manually run the playbook on a particular incident follow the below steps:
    
- Go to Microsoft Sentinel -> <your workspace> -> Incidents
- Select an incident.
- In the right pane, click on Actions, and from the dropdown select the 'Run Playbook' option.
- click on the Run button beside this playbook.
