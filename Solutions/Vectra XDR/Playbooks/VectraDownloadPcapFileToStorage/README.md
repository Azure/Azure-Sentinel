# Vectra Download Pcap File To Storage

## Summary

This playbook enables users to download pcap files of detections associated with a Vectra Entity to the default file share of a storage account. Users can provide detection IDs via Microsoft Teams Adaptive Card.

### Prerequisites

1. Obtain Key Vault name and Tenant ID where client credentials are stored for access token generation.
   - Create a Key Vault with a unique name.
   - Go to Key Vaults → *your Key Vault* → Overview and copy Directory ID (Tenant ID).
   - **NOTE:** Ensure the Permission model in the Access Configuration of Key Vault is set to **'Vault access policy'**.
2. Obtain Teams GroupId and ChannelId.
   - Create a Team with a public channel.
   - Click on the three dots (...) next to your newly created Teams channel and select **Get link to channel**.
   - Copy the text from the link between `/channel` and `/`, decode it using an online URL decoder, and copy it to use as Channel ID.
   - Copy the text of the GroupId parameter from the link to use as GroupId.
3. Obtain Storage Account Name where pcap files will be downloaded.
4. Ensure the VectraGenerateAccessToken playbook is deployed before deploying VectaDownloadPcapFileToStorage playbook.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   - PlaybookName: Enter the playbook name here.
   - KeyVaultName: Name of the Key Vault where secrets are stored.
   - TenantId: Tenant ID where the Key Vault is located.
   - BaseURL: Enter the base URL of your Vectra account.
   - TeamsGroupId: Enter Id of the Teams Group where the adaptive card will be posted.
   - TeamsChannelId: Enter Id of the Teams Channel where the adaptive card will be posted.
   - StorageAccountName: Name of the storage account where pcap files will be downloaded.
   - GenerateAccessCredPlaybookName: Playbook name which is deployed as part of prerequisites.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectaDownloadPcapFileToStorage%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectaDownloadPcapFileToStorage%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select keyvault connection resource.
2. Go to General → Edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.
6. Repeat steps for other connections.

**To authorize the Storage Account API connection, you will need the access key:**
1. Go to Azure Portal → Storage Accounts → *your storage account*.
2. In the left pane, select **Access keys** under **Security + networking**.
3. Copy the value of **key1** or **key2**.
4. Go to your logic app → API connections → Select the storage account connection resource.
5. Go to General → Edit API connection.
6. Paste the copied access key in the required field.
7. Click Save.

#### b. Add Access Policy in Key Vault

Add access policy for the playbook's managed identity and authorized user to read and write secrets of the Key Vault.
1. Go to Logic App → *your Logic App* → Identity → System assigned Managed identity and copy Object (principal) ID.
2. Go to Key Vaults → *your Key Vault* → Access policies → Create.
3. Select all keys & secrets permissions. Click Next.
4. In the principal section, search by copied Object ID. Click Next.
5. Click Review + Create.
6. Repeat steps 2 to 5 to add access policy for the user account used to authorize the connection.

#### c. Assign Role to update incident

After authorizing each connection, assign role to this playbook.
1. Go to Log Analytics Workspace → *your workspace* → Access Control → Add.
2. Add role assignment.
3. Assignment type: Job function roles.
4. Role: Microsoft Sentinel Contributor.
5. Members: select managed identity for assigned access to and add your logic app as member.
6. Click on review+assign.

#### d. Configurations in Microsoft Sentinel

1. In Microsoft Sentinel, the analytical rule should be configured to trigger an incident based on data ingested from Vectra. Incident should have Entity mapping.
2. To manually run the playbook on a particular incident, follow the steps below:
   - Go to Microsoft Sentinel → *your workspace* → Incidents.
   - Select an incident.
   - In the right pane, click on **Actions**, and from the dropdown select the **Run Playbook** option.
   - Click on the **Run** button beside this playbook.

#### e. Note

1. In Microsoft Sentinel Incident, users can provide detection IDs via the Adaptive Card option in Teams. The playbook will download the corresponding pcap files to the configured storage account's file share.