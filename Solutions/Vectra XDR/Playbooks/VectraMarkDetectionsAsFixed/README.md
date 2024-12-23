# Vectra Mark Detections As Fixed

## Summary

This playbook will mark all active detection as fixed associated with an entity. Also it adds a pre-defined but user customizable comment to an incident and also adds a pre-defined but user customizable note to Vectra Entity.

### Prerequisites

1. The Vectra XDR data connector should be configured to create alerts and generate an incident based on entity data in Microsoft Sentinel.
2. Obtain the key vault name and tenantId where client credentials are stored using which access token will be generated.
   * Create a Key Vault with a unique name.
   * Go to Keyvaults → *your Key Vault* → Overview and copy DirectoryID which will be used as tenantId.
   * NOTE: Ensure the Permission model in the Access Configuration of Key Vault is set to **'Vault access policy'**.
3. Ensure that the VectraGenerateAccessToken playbook is deployed before deploying VectraMarkDetectionsAsFixed playbook.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here.
   * KeyVaultName: Name of the Key Vault where secrets are stored.
   * TenantId: Tenant ID where the Key Vault is located.
   * BaseURL: Enter the base URL of your Vectra account.
   * IncidentComment: All Active Detections associated with an Entity has been fixed successfully.
   * EntityNote: All Active Detections associated with an Entity has been fixed successfully..
   * GenerateAccessCredPlaybookName: Playbook name which is deployed as part of prerequisites.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraMarkDetectionsAsFixed%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraMarkDetectionsAsFixed%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize Connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select keyvault connection resource.
2. Go to General → Edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for other connections.

#### b. Add Access Policy in Key Vault

Add access policy for the playbook's managed identity and authorized user to read and write secrets of the Key Vault.
1. Go to logic app → *your Logic App* → identity → System assigned Managed identity and copy Object (principal) ID.
2. Go to key vaults → *your Key Vault* → Access policies → create.
3. Select all keys & secrets permissions. Click next.
4. In the principal section, search by copied Object ID. Click next.
5. Click review + create.
6. Repeat the above steps 2 to 5 to add access policy for the user account using which connection is authorized.

#### c. Assign Role to Add Comment in Incident

Assign a role to this playbook.
1. Go to Log Analytics Workspace → *your workspace* → Access Control → Add.
2. Add role assignment.
3. Assignment type: Job function roles.
4. Role: Microsoft Sentinel Contributor.
5. Members: Select managed identity for assigned access to and add your logic app as a member.
6. Click on review+assign.

#### d. Configurations in Microsoft Sentinel

1. In Microsoft Sentinel, an analytical rule should be configured to trigger an incident based on data ingested from Vectra. The incident should have Entity mapping.
2. To manually run the playbook on a particular incident, follow the below steps:
   a. Go to Microsoft Sentinel → *your workspace* → Incidents.
   b. Select an incident.
   c. In the right pane, click on Actions, and from the dropdown select the 'Run Playbook' option.
   d. Click on the Run button beside this playbook.
