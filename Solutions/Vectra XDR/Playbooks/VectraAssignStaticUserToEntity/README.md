# Vectra Assign Static User To Entity

## Summary

This playbook will assign a predefined user to an entity in Vectra when the status of an incident changes from 'New' to 'Active'.

### Prerequisites

1. The Vectra XDR data connector should be configured to create alerts and generate an incident based on entity data in Microsoft Sentinel.
2. Obtain the Key Vault name and Tenant ID where client credentials are stored using which the access token will be generated.
   * Create a Key Vault with a unique name.
   * Go to Key Vaults → *your Key Vault* → Overview and copy Directory ID, which will be used as the tenant ID.
   * NOTE: Ensure the Permission model in the Access Configuration of Key Vault is set to **'Vault access policy'**.
3. Make sure that the VectraGenerateAccessToken playbook is deployed before deploying the VectraAssignStaticUserToEntity playbook.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here.
   * KeyVaultName: Name of the Key Vault where secrets are stored.
   * tenantId: Tenant ID where the Key Vault is located.
   * BaseURL: Enter the base URL of your Vectra account.
   * UserId: Enter a user id which will be assign to entity.
   * GenerateAccessCredPlaybookName: Playbook name which is deployed as part of prerequisites.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraAssignStaticUserToEntity%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraAssignStaticUserToEntity%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize Connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select the Key Vault connection resource.
2. Go to General → Edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for other connections.

#### b. Add Access Policy in Key Vault

Add access policy for the playbook's managed identity and authorized user to read and write secrets of the Key Vault.
1. Go to Logic App → *your Logic App* → Identity → System assigned Managed identity and copy Object (principal) ID.
2. Go to Key Vaults → *your Key Vault* → Access policies → Create.
3. Select all keys & secrets permissions. Click Next.
4. In the principal section, search by copied Object ID. Click Next.
5. Click Review + Create.
6. Repeat steps 2 to 5 to add access policy for the user account using which connection is authorized.

#### c. Configurations in Microsoft Sentinel

1. In Microsoft Sentinel, analytical rule should be configured to trigger an incident based on data ingested from Vectra. Incident should have Entity mapping.
2. In Microsoft Sentinel, Configure the automation rules to trigger the playbook.
   * Go to Microsoft Sentinel → *your workspace* → Automation.
   * Click on Create → Automation rule.
   * Provide a name for your rule.
   * Select Trigger as When incident is updated.
   * In Conditions, select Status changed from 'New' and status changed to 'Active'.
   * In Actions dropdown, select Run playbook.
   * In the second dropdown, select your deployed playbook.
   * Click on Apply.
   * Save the Automation rule.

**NOTE:** If you want to manually run the playbook on a particular incident, follow the below steps:
1. Go to Microsoft Sentinel → *your workspace* → Incidents.
2. Select an incident.
3. In the right pane, click on Actions, and from the dropdown select the 'Run Playbook' option.
4. Click on the Run button beside this playbook.
