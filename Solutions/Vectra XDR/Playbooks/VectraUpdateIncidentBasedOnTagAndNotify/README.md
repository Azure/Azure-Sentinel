# Vectra Update Incident Based on Tag ANd Notify

## Summary

This playbook runs hourly to identify entities with Medium severity incidents, checks for user-defined tags in Vectra, and if found, upgrades the incident severity to High, adds a comment, and sends a notification to a specified MS Teams channel.

### Prerequisites

1. The Vectra XDR data connector should be configured to create alerts and generate an incident based on entity data in Microsoft Sentinel.
2. Obtain Key Vault name and Tenant ID where client credentials are stored using which access token will be generated.
   * Create a Key Vault with a unique name.
   * Go to Key Vaults → *your Key Vault* → Overview and copy Directory ID, which will be used as the tenant ID.
   * NOTE: Ensure the Permission model in the Access Configuration of Key Vault is set to **'Vault access policy'**.
3. User must have a Microsoft Teams account.
4. Ensure the VectraGenerateAccessToken playbook is deployed before deploying VectraUpdateIncidentBasedOnTagAndNotify playbook.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here.
   * KeyVaultName: Enter Name of the Key Vault where secrets are stored.
   * TenantId: Enter Tenant ID where the Key Vault is located.
   * BaseURL: Enter the base URL of your Vectra account.
   * Tags: Enter a tag through which incident will be updated.
   * TeamsGroupId: Enter Id of the Teams Group where the adaptive card will be posted.
   * TeamsChannelId: Enter Id of the Teams Channel where the adaptive card will be posted.
   * IncidentComment: Enter comment you want to add in incident which will be updated based on tag.
   * WorkspaceName: Enter name of the log analytics workspace where incidents are available using generated using analytic rule.
   * GenerateAccessCredPlaybookName: Enter Playbook name which is deployed as part of prerequisites.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraUpdateIncidentBasedOnTagAndNotify%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraUpdateIncidentBasedOnTagAndNotify%2Fazuredeploy.json)

## Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select keyvault connection resource.
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
6. Repeat steps 2 to 5 to add access policy for the user account used to authorize the connection.

#### c. Assign Role to add comment in incident

Assign role to this playbook.
1. Go to Log Analytics Workspace → *your workspace* → Access Control → Add.
2. Add role assignment.
3. Assignment type: Job function roles.
4. Role: Microsoft Sentinel Contributor.
5. Members: select managed identity for assigned access to and add your logic app as member.
6. Click on Review + Assign.

#### d. Configurations in Microsoft Sentinel

1. In Microsoft Sentinel, the below analytical rules should be configured to trigger an incident:
   - Vectra Create Incident Based On Tag For Entity Type Account.
   - Vectra Create Incident Based On Tag For Entity Type Host.
   - Vectra Priority Account Incidents.
   - Vectra Priority Host Incidents.
