# Rubrik DSPM Violation Remediation

## Summary

This is an incident-triggered playbook that remediates Rubrik Security Cloud (RSC) DSPM violations raised as Microsoft Sentinel incidents. It branches on the incident's `eventType`. For a `SecurityViolation` it retrieves the violation, exports the violation-files CSV and the remediation-actions log (create -> poll the Download Bar -> download the bytes -> upload to a blob container -> generate a read-only SAS link), lists the violation file hits, quarantines each file by calling the RubrikQuarantineFiles sub-playbook, notifies the file owner in Microsoft Teams, and marks the violation `REMEDIATED` only when every quarantine succeeded. For `ClassificationResultsAvailable` (no DSPM license) it runs a reduced flow: list file hits -> quarantine -> notify. Both flows write a final comment back to the Sentinel incident.

### Prerequisites

1. The Rubrik Security Cloud data connector should be configured to send appropriate events to Microsoft Sentinel.
2. The Rubrik Security Cloud solution should be configured to [connect to Rubrik Security Cloud API end points using a Service Account](https://docs.rubrik.com/en-us/saas/saas/polaris_api_access_with_service_accounts.html); the service account should be assigned a role that includes the privileges necessary to read and update policy violations (see [Roles and Permissions](https://docs.rubrik.com/en-us/saas/saas/common/roles_and_permissions.html) in the Rubrik Security Cloud user guide).
3. Deploy the Rubrik custom connector (`Microsoft.Web/customApis`) first, in the same resource group and region. This playbook uses its `Authentication` (`/api/client_token`) operation to obtain the RSC bearer token.
4. Deploy the RubrikQuarantineFiles sub-playbook (HTTP Request-triggered) before this playbook; it is called once per file to quarantine and must return `{ status, newLocation }`.
5. Store Service account credentials in Key Vault and obtain the keyvault name.
    a. Create a Key Vault with a unique name.
    b. Go to KeyVault -> secrets -> Generate/import and create 'Rubrik-AS-Int-ClientId' & 'Rubrik-AS-Int-ClientSecret' for storing client_id and client_secret respectively.
6. An Azure Storage account and an EXISTING blob container for the exported CSV/log files (SecurityViolation flow only).
7. Obtain the Teams group id and channel id where the owner-notification card will be posted.
8. An analytics rule that maps the Rubrik event fields into incident Custom Details (eventType, objectId, objectName, objectType, seriesId, eventName, snapshotId).

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * PlaybookName: Enter the playbook name here.
    * API Hostname: Hostname of the Rubrik Security Cloud instance (e.g. customer.my.rubrik.com), without scheme or trailing slash.
    * Rubrik Connector name: Name of the Rubrik Custom Connector deployed previously.
    * KeyVaultName: Name of the keyvault where the RSC service-account secrets ('Rubrik-AS-Int-ClientId' and 'Rubrik-AS-Int-ClientSecret') are stored.
    * RubrikQuarantineFilesPlaybookName: Logic App name of the RubrikQuarantineFiles sub-playbook. It must exist in the same resource group and expose an HTTP Request trigger.
    * StorageAccountName: Azure Storage account name used to persist the exported CSV/log.
    * StorageContainerName: Name of an EXISTING blob container in StorageAccountName where the violation-files export is written.
    * SasTokenTtlHours: Validity window (hours) for the read-only SAS link added to the incident comment.
    * TeamsGroupId: Id of the Teams Group where the owner-notification card is posted.
    * TeamsChannelId: Id of the Teams Channel where the owner-notification card is posted.
    * DownloadPollIntervalSec: Seconds to wait between Download Bar polls.
    * DownloadPollMaxAttempts: Maximum Download Bar poll attempts before giving up on an export.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikDSPMViolationRemediation%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikDSPMViolationRemediation%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection like Rubrik custom connector, teams, keyvault, azure blob storage.

1. Click the connection resource
2. Click edit API connection
3. Click Authorize
4. Sign in
5. Click Save
6. Repeat steps for other connections

The Azure Blob Storage connection's account must have write access to StorageContainerName; it is used to upload the CSV/log and to create the read-only SAS link.

#### b. Assign roles to the playbook

Assign roles to this playbook's managed identity.

1. Go to Log Analytics Workspace → <your workspace> → Access Control → Add
2. Add role assignment
3. Assignment type: Job function roles -> Add 'Microsoft Sentinel Responder' as a Role (to comment on and update incidents)
4. Members: select managed identity for assigned access to and add your logic app as member
5. Click on review+assign
6. Grant the playbook's managed identity the 'Key Vault Secrets User' role (or a get-secret access policy) on the Key Vault named by the KeyVaultName parameter.

#### c. Wire up the sub-playbook

This playbook calls the RubrikQuarantineFiles sub-playbook once per file. Deploy that sub-playbook first (same resource group) and set RubrikQuarantineFilesPlaybookName to its Logic App name; it must expose an HTTP Request trigger returning `{ status, newLocation }`.

#### d. Configurations in Microsoft Sentinel

1. In Microsoft Sentinel, analytical rules should be configured to trigger an incident. The incident should carry the DSPM Custom Details (eventType, objectId, objectName, objectType, seriesId, eventName, snapshotId) obtained from the corresponding fields in Rubrik DSPM event logs. Check the [documentation](https://docs.microsoft.com/azure/sentinel/surface-custom-details-in-alerts) to learn more about adding custom details to incidents.
2. Configure the automation rules to trigger this playbook on the relevant DSPM incidents (playbooks do not auto-attach).
