# Vectra Static Assign Members To Group

## Summary

This playbook will take input of group id and members from user via MS teams and assign members to the provided group.

### Prerequisites

1. Obtain the Key Vault name and Tenant ID where client credentials are stored using which the access token will be generated.
   * Create a Key Vault with a unique name.
   * Go to Key Vaults → *your Key Vault* → Overview and copy Directory ID, which will be used as the tenant ID.
   * NOTE: Ensure the Permission model in the Access Configuration of Key Vault is set to **'Vault access policy'**.
2. Obtain Teams GroupId and ChannelId.
   * Create a Team with a public channel.
   * Click on the three dots (...) next to your newly created Teams channel and select **Get link to channel**.
   * Copy the text from the link between `/channel` and `/`, decode it using an online URL decoder, and copy it to use as the Channel ID.
   * Copy the text of the GroupId parameter from the link to use as the GroupId.
3. Make sure that the VectraGenerateAccessToken playbook is deployed before deploying the VectraStaticAssignMembersToGroup playbook.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here.
   * KeyVaultName: Name of the Key Vault where secrets are stored.
   * TenantId: Tenant ID where the Key Vault is located.
   * BaseURL: Enter the base URL of your Vectra account.
   * TeamsGroupId: Enter Id of the Teams Group where the adaptive card will be posted.
   * TeamsChannelId: Enter Id of the Teams Channel where the adaptive card will be posted.
   * GenerateAccessCredPlaybookName: Playbook name which is deployed as part of prerequisites.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraStaticAssignMembersToGroup%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraStaticAssignMembersToGroup%2Fazuredeploy.json)

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
