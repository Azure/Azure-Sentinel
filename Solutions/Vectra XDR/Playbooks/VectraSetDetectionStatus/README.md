# Vectra Set Detection Status

## Summary

This playbook automatically updates the status of all detections listed in an incident's custom details based on the current incident status. When an incident is marked as Active, detections are set to 'acknowledged'. When an incident is Closed, detections are closed with a reason derived from the incident classification (True Positive → remediated; Benign Positive / False Positive / Undetermined → benign).

### Prerequisites

1. The Vectra XDR data connector should be configured to create alerts and generate an incident based on entity data in Microsoft Sentinel.
2. Obtain Key Vault name and Tenant ID where client credentials are stored and using which access token will be generated.
   * Create a Key Vault with a unique name.
   * Go to Key Vaults → *your Key Vault* → Overview and copy Directory ID, which will be used as the tenant ID.
   **NOTE:** Ensure the Permission model in the Access Configuration of Key Vault is set to **'Vault access policy'**.
3. Ensure the VectraGenerateAccessToken playbook is deployed before deploying VectraSetDetectionStatus playbook.
4. The analytical rule must include Custom Details with at minimum 'detection_id' field mapped from Vectra alert data.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   * PlaybookName: Enter the playbook name here.
   * KeyVaultName: Name of the Key Vault where secrets are stored.
   * TenantId: Tenant ID where the Key Vault is located.
   * BaseURL: Enter the base URL of your Vectra account.
   * GenerateAccessCredPlaybookName: Playbook name which is deployed as part of prerequisites.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraSetDetectionStatus%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraSetDetectionStatus%2Fazuredeploy.json)

### Post-Deployment Instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection.
1. Go to your logic app → API connections → Select keyvault connection resource.
2. Go to General → Edit API connection.
3. Click Authorize.
4. Sign in.
5. Click Save.

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

1. In Microsoft Sentinel, the analytical rule should be configured to trigger an incident based on data ingested from Vectra. Incident should have Entity mapping with `detection_id` populated in Custom Details.
2. To manually run the playbook on a particular incident, follow the steps below:
   * Go to Microsoft Sentinel → *your workspace* → Incidents.
   * Select an incident.
   * In the right pane, click on **Actions**, and from the dropdown select the **Run Playbook** option.
   * Click on the **Run** button beside this playbook.

#### e. Status and Classification Mapping

The playbook uses the following mappings to update detection status:

| Incident Status | Detection Status | Close Reason (if Closed) |
|---|---|---|
| Active | acknowledged | N/A |
| Closed (True Positive) | closed | remediated |
| Closed (Benign Positive) | closed | benign |
| Closed (False Positive) | closed | benign |
| Closed (Undetermined) | closed | benign |

#### f. Note

1. The playbook executes automatically when triggered by an incident creation/update event in Microsoft Sentinel.
2. A comment is automatically added to the incident documenting the status update operation, including the detection IDs affected.
3. The playbook requires the 'detection_id' field to be present in the incident's Custom Details. If missing, the playbook will terminate with a failure status.
