# Vectra Add Note To Detections

## Summary

This playbook extracts notes from incident comments and adds them to each detection listed in the incident's custom details. If no comment with proper structure is found and Teams is configured, it prompts the user for note input via an Adaptive Card. If Teams is not configured, the playbook exits gracefully with Succeeded status.

### Prerequisites

1. The Vectra XDR data connector should be configured to create alerts and generate an incident based on entity data in Microsoft Sentinel.
2. Obtain Key Vault name and Tenant ID where client credentials are stored and using which access token will be generated.
   * Create a Key Vault with a unique name.
   * Go to Key Vaults → *your Key Vault* → Overview and copy Directory ID, which will be used as the tenant ID.
   **NOTE:** Ensure the Permission model in the Access Configuration of Key Vault is set to **'Vault access policy'**.
3. *(Optional)* Obtain Teams GroupId and ChannelId if you want the playbook to prompt for notes when no structured comment is found.
   * Create a Team with a public channel.
   * Click on the three dots (...) next to your newly created Teams channel and select **Get link to channel**.
   * Copy the text from the link between `/channel` and `/`, decode it using an online URL decoder, and copy it to use as Channel ID.
   * Copy the text of the GroupId parameter from the link to use as GroupId.
4. Ensure the VectraGenerateAccessToken playbook is deployed before deploying VectraAddNoteToDetections playbook.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here.
   * KeyVaultName: Name of the Key Vault where secrets are stored.
   * TenantId: Tenant ID where the Key Vault is located.
   * BaseURL: Enter the base URL of your Vectra account.
   * TeamsGroupId: *(Optional)* Enter Id of the Teams Group where the adaptive card will be posted. Leave empty to skip Teams prompts.
   * TeamsChannelId: *(Optional)* Enter Id of the Teams Channel where the adaptive card will be posted. Leave empty to skip Teams prompts.
   * GenerateAccessCredPlaybookName: Playbook name which is deployed as part of prerequisites.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraAddNoteToDetections%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraAddNoteToDetections%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select keyvault connection resource.
2. Go to General → Edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for other connections (Teams connection if Teams parameters are configured).

#### b. Add Access Policy in Key Vault

Add access policy for the playbook's managed identity and authorized user to read and write secrets of the Key Vault.
1. Go to Logic App → *your Logic App* → Identity → System assigned Managed identity and copy Object (principal) ID.
2. Go to Key Vaults → *your Key Vault* → Access policies → Create.
3. Select all keys & secrets permissions. Click Next.
4. In the principal section, search by copied Object ID. Click Next.
5. Click Review + Create.
6. Repeat steps 2 to 5 to add access policy for the user account used to authorize the connection.

#### c. Configurations in Microsoft Sentinel

1. In Microsoft Sentinel, the analytical rule should be configured to trigger an incident based on data ingested from Vectra. Incident should have Entity mapping with `detection_id` populated in Custom Details.
2. To manually run the playbook on a particular incident, follow the steps below:
   * Go to Microsoft Sentinel → *your workspace* → Incidents.
   * Select an incident.
   * In the right pane, click on **Actions**, and from the dropdown select the **Run Playbook** option.
   * Click on the **Run** button beside this playbook.

#### d. Note

1. In Microsoft Sentinel Incident, the comment should be in the following structure only to be able to extract values from it.
   * **note: [note_content]** (Do not use quotes for note content)
   * **note: {note_content}** (Do not use quotes for note content)
   * Single note value is supported from the comment. For multiple note values, use the adaptive card option instead.
2. If both `TeamsGroupId` and `TeamsChannelId` are left empty at deployment, the playbook will exit with **Succeeded** status when no structured comment is found, instead of prompting via Teams.
3. Notes are appended to each detection — existing notes are never removed. Duplicate notes (identical content) are not added to prevent redundancy.
