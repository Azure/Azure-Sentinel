# Vectra Decorate Incident Based On Tag

## Summary

This playbook will add pre-defined or user customizable comment to an incident generated based on tags and add pre-defined or user customizable note to associated Vectra Entity.

### Prerequisites

1. The Vectra XDR data connector should be configured to create alerts and generate an incident based on entity data in Microsoft Sentinel.
2. Obtain keyvault name and tenantId where client credentials are stored using which access token will be generated.
  * Create a Key Vault with unique name
  * Go to Keyvaults → *your keyvault* → Overview and copy DirectoryID which will be used as tenantId
  * NOTE: Ensure the Permission model in the Access Configuration of Key Vault is set to **'Vault access policy'**.

3. Make sure that VectraGenerateAccessToken playbook is deployed before deploying VectraDecorateIncidentBasedOnTag playbook.

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
  * PlaybookName: Enter the playbook name here.
  * KeyVaultName: Name of keyvault where secrets are stored.
  * TenantId: TenantId where keyvault is located.
  * BaseURL: Enter baseurl of your Vectra account.
  * IncidentComment: Enter comment you want to add in incident create based on tag.
  * EntityNote: Enter a note you want to add in Vectra Entity.
  * GenerateAccessCredPlaybookName: Playbook name which is deployed as part of prerequisites.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraDecorateIncidentBasedOnTag%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraDecorateIncidentBasedOnTag%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select keyvault connection resource.
2. Go to General → Edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for other connections.

#### b. Assign Role to add a comment in the incident

After authorizing each connection, assign a role to this playbook.
1. Go to Log Analytics Workspace → *your workspace* → Access Control → Add
2. Add role assignment
3. Assignment type: Job function roles
4. Role: Microsoft Sentinel Contributor
5. Members: select managed identity for "assigned access to" and add your logic app as a member.
6. Click on review+assign

#### c. Add Access policy in Keyvault

Add access policy for the playbook's managed identity and authorized user to read, and write secrets of key vault.
1. Go to logic app → *your Logic App* → identity → System assigned Managed identity and copy Object (principal) ID.
2. Go to keyvaults → *your keyvault* → Access policies → create.
3. Select all keys & secrets permissions. Click next.
4. In the principal section, search by copied object ID. Click next.
5. Click review + create.
6. Repeat the above step 2 to 5 to add access policy for the user account using which connection is authorized.

#### d. Configurations in Microsoft Sentinel

1. In Microsoft sentinel, below analytical rules should be configured to trigger an incident.
  * Vectra Create Incident Based On Tag For Entity Type Account
  * Vectra Create Incident Based On Tag For Entity Type Host
2. In Microsoft Sentinel, Configure the automation rules to trigger the playbook. 
  * Go to Microsoft Sentinel → *your workspace* → Automation 
  * Click on **Create** → **Automation rule**
  * Provide a name for your rule
  * In the Analytic rule name condition, select the analytic rule that you have created.
  * In Actions dropdown select **Run playbook**
  * In the second dropdown select your deployed playbook
  * Click on **Apply**
  * Save the Automation rule.

**NOTE:** If you want to manually run the playbook on a particular incident follow the below steps:
- Go to Microsoft Sentinel → *your workspace* → Incidents
- Select an incident.
- In the right pane, click on Actions, and from the dropdown select the 'Run Playbook' option.
- click on the Run button beside this playbook.
