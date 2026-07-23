# Vectra Operate On Entity Source IP

## Summary

This Playbook will extract the IP address from entities associated with an incident on which the playbook is triggered.

### Prerequisites

1. The Vectra XDR data connector should be configured to create alerts and generate an incident.
2. Obtain the key vault name and tenantId where client credentials are stored using which access token will be generated.
   * Create a Key Vault with a unique name.
   * Go to Keyvaults → *your keyvault* → Overview and copy DirectoryID which will be used as tenantId.
   * NOTE: Ensure the Permission model in the Access Configuration of Key Vault is set to **'Vault access policy'**.
3. Ensure that VectraGenerateAccessToken playbook is deployed before deploying the VectraOperateOnEntitySourceIP playbook.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here.
   * KeyVaultName: Name of the Key Vault where secrets are stored.
   * TenantId: Tenant ID where the Key Vault is located.
   * BaseURL: Enter the base URL of your Vectra account.
   * GenerateAccessCredPlaybookName: Playbook name which is deployed as part of prerequisites.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraOperateOnEntitySourceIP%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraOperateOnEntitySourceIP%2Fazuredeploy.json)

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

Add access policy for the playbook's managed identity and authorized user to read and write secrets of the key vault.
1. Go to logic app → *your logic app* → identity → System assigned Managed identity and copy Object (principal) ID.
2. Go to key vaults → *your keyvault* → Access policies → create.
3. Select all keys & secrets permissions. Click next.
4. In the principal section, search by copied object ID. Click next.
5. Click review + create.
6. Repeat the above steps 2 to 5 to add access policy for the user account using which connection is authorized.

#### c. Configurations in Microsoft Sentinel

1. In Microsoft Sentinel, an analytical rule should be configured to trigger an incident that has Host Entity mapped.
2. To manually run the playbook on a particular incident, follow the steps below:
   * Go to Microsoft Sentinel → *your workspace* → Incidents.
   * Select an incident.
   * In the right pane, click on Actions, and from the dropdown select the 'Run Playbook' option.
   * Click on the Run button beside this playbook.
