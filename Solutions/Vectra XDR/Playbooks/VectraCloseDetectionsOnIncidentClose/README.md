# Vectra Close Detections On Incident Close

## Summary

This playbook is triggered when a Microsoft Sentinel incident is closed. It reads Vectra detection_id values from the incident alert Custom Details, maps the Microsoft Sentinel close classification to a Vectra close reason (remediated or benign), and bulk-closes all detections via the Vectra `PATCH /api/v3.5/detections/close` endpoint. Authentication is handled via the VectraGenerateAccessToken playbook.

### Prerequisites

1. The Vectra XDR data connector should be configured to create alerts and generate an incident based on entity data in Microsoft Sentinel.
2. Obtain Key Vault name and Tenant ID where client credentials are stored using which access token will be generated.
   - Create a Key Vault with a unique name.
   - Go to Key Vaults → *your Key Vault* → Overview and copy Directory ID, which will be used as the tenant ID.
   - **NOTE:** Ensure the Permission model in the Access Configuration of Key Vault is set to **'Vault access policy'**.
3. Ensure the VectraGenerateAccessToken playbook is deployed before deploying VectraCloseDetectionsOnIncidentClose playbook.
4. The Sentinel Analytics Rule that creates incidents must populate alert Custom Details with the key **'detection_id'**.
5. A Sentinel Automation Rule configured to run this playbook when the incident status changes to Closed.

### Deployment Instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
   - PlaybookName: Enter the playbook name here.
   - KeyVaultName: Name of the Key Vault where secrets are stored.
   - TenantId: Tenant ID where the Key Vault is located.
   - BaseURL: Enter the base URL of your Vectra account.
   - GenerateAccessCredPlaybookName: Playbook name which is deployed as part of prerequisites.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraCloseDetectionsOnIncidentClose%2Fazuredeploy.json) [![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FVectraXDR%2FPlaybooks%2FVectraCloseDetectionsOnIncidentClose%2Fazuredeploy.json)

### Post-Deployment Instructions

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

#### c. Assign Role to update incident

After authorizing each connection, assign role to this playbook.
1. Go to Log Analytics Workspace → *your workspace* → Access Control → Add.
2. Add role assignment.
3. Assignment type: Job function roles.
4. Role: Microsoft Sentinel Responder.
5. Members: select managed identity for assigned access to and add your logic app as member.
6. Click on review+assign.

#### d. Configurations in Microsoft Sentinel

1. In Microsoft Sentinel, create an Automation Rule: Trigger = **'When an incident is updated'**, Condition = **'Status changed to Closed'**, Action = **'Run playbook'** and select this playbook.
2. The analytical rule that creates incidents must populate alert Custom Details with the key **'detection_id'**. Incident should have Entity mapping.

#### e. Note

1. The playbook reads Vectra `detection_id` values from the incident alert Custom Details (key **'detection_id'**) and closes all of the referenced detections when the incident is closed.
2. The playbook runs only when the incident status is **Closed**.
3. The Microsoft Sentinel close classification is mapped to the Vectra close reason as follows:
   * **TruePositive** → **remediated**
   * Any other classification (**BenignPositive**, **FalsePositive**, **Undetermined**, or none) → **benign** (default)
