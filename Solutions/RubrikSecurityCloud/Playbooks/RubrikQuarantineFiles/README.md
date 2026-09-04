# Rubrik Quarantine Files

## Summary

This is a child (HTTP Request-triggered) playbook that quarantines a batch of files reported in a Rubrik DSPM violation. The caller (RubrikViolationRemediation) passes the whole files array in a single call, and this playbook iterates internally and routes on objectType: OneDrive/O365 files are moved to a quarantine folder via Microsoft Graph, and Windows file-share (NTFS) files are quarantined on their host via Microsoft Defender for Endpoint. It returns a per-file result set to the caller.

### Prerequisites

1. A single Azure AD app registration used for BOTH Microsoft Graph and Microsoft Defender for Endpoint (MDE). It needs Microsoft Graph **application** permissions `Files.ReadWrite.All`, `Sites.ReadWrite.All`, `User.Read.All` AND WindowsDefenderATP (MDE) **application** permissions `Machine.ReadWrite.All` (or `Machine.StopAndQuarantine`) and `AdvancedQuery.Read.All`, all admin-consented.
2. Store the app registration credentials in Key Vault and obtain the keyvault name.
    a. Create a Key Vault with a unique name.
    b. Go to KeyVault -> secrets -> Generate/import and create the secrets named by GraphClientIdSecretName ('Graph-App-ClientId') & GraphClientSecretSecretName ('Graph-App-ClientSecret') for storing the app registration client_id and client_secret respectively (these same credentials authenticate both Graph and MDE).
3. Obtain the Teams group id and channel id where the folder-name Adaptive Card will be posted (used by the OneDrive branch only).
4. For NTFS quarantine, the target file shares must be hosted on devices onboarded to Microsoft Defender for Endpoint, reachable by their physicalHost / computerDnsName.

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * PlaybookName: Enter the playbook name here. Must match the RubrikQuarantineFilesPlaybookName parameter on the caller (RubrikViolationRemediation).
    * TeamsGroupId: Id of the Teams Group where the folder-name Adaptive Card is posted.
    * TeamsChannelId: Id of the Teams Channel where the folder-name Adaptive Card is posted.
    * KeyVaultName: Name of the keyvault where the app registration credentials are stored.
    * TenantId: Azure AD tenant ID used for the Microsoft Graph / MDE OAuth2 token endpoint.
    * GraphClientIdSecretName: Key Vault secret name holding the app registration client id (default 'Graph-App-ClientId').
    * GraphClientSecretSecretName: Key Vault secret name holding the app registration client secret (default 'Graph-App-ClientSecret').
    * SearchRegion: ISO 3166-1 region code required by Microsoft Graph /search/query for app-only permissions; must match the tenant's data location (e.g. NAM, EUR, GBR, APC, AUS, CAN, IND, JPN).

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikQuarantineFiles%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikQuarantineFiles%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection like teams, keyvault.

1. Click the connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections

#### b. Assign role to access Key Vault secrets

Assign a role to this playbook's managed identity.

1. Go to the Key Vault named by KeyVaultName → Access Control (IAM) → Add
2. Add role assignment
3. Assignment type: Job function roles -> Add 'Key Vault Secrets User' as a Role (or add an access policy with Get on secrets)
4. Members: select managed identity for assigned access to and add your logic app as member
5. Click on review+assign

#### c. Grant the app registration API permissions

1. Create/point ONE app registration used for both Microsoft services and store its client id/secret in Key Vault under GraphClientIdSecretName / GraphClientSecretSecretName.
2. Grant it Microsoft Graph application permissions `Files.ReadWrite.All`, `Sites.ReadWrite.All`, `User.Read.All` AND WindowsDefenderATP application permissions `Machine.ReadWrite.All` (or `Machine.StopAndQuarantine`) and `AdvancedQuery.Read.All`, all admin-consented.
3. For NTFS quarantine, ensure the file-share hosts are onboarded to Microsoft Defender for Endpoint and resolvable by their physicalHost / computerDnsName.

#### d. Wire up the caller

This playbook has an HTTP Request trigger and does not run on its own. The caller RubrikViolationRemediation references it by the RubrikQuarantineFilesPlaybookName parameter and must be deployed in the same resource group. Ensure the PlaybookName here matches that value.
