# RubrikWorkloadAnalysis
## Summary
This playbook retrieves sensitive IP and Host data to enrich the incident details, and adjusts the incident's severity level based on the gathered information.
### Prerequisites
1. User must have a valid Rubrik Client ID and Client Secret.
2. Store Service account credentials in Key Vault and obtain keyvault name and tenantId
    * Create a Key Vault with a unique name
    * Go to KeyVault -> secrets, click on Generate/import and create 'Rubrik--Client-Id' & 'Rubrik-Client-Secret' for storing client_id and client_secret respectively
    **NOTE:** Make sure the Permission model in the Access Configuration of Keyvault is selected to the Vault access policy. If not then change it to **'Vault access policy'**
### Deployment instructions
1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
* Playbook Name: Enter the playbook name here.
* Keyvault Name: Enter name of keyvault where service account credentials are stored(e.g. RubrikSentinelKeyVault).
* Tenant ID: Enter Tenant ID of your Microsoft EntraID where keyvault is available.
* Rubrik Base URL: Enter Base URL of the RubrikApi instance (Example: https://rubrik-tme.my.rubrik.com).
* Increase Severity Level: Enter a value to increase the severity level of the incident.(Example: for value 1 incident severity will change from Low to Medium)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikWorkloadAnalysis%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikWorkloadAnalysis%2Fazuredeploy.json)

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
    * IP
    * Host
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