# Rubrik DSPM Violation Remediation

## Summary

This is an incident-triggered playbook that remediates Rubrik Security Cloud (RSC) DSPM violations raised as Microsoft Sentinel incidents. It branches on the incident's `eventType`. For a `SecurityViolation` it retrieves the violation, validates it against the incident, marks it `IN_PROGRESS`, exports the violation-files CSV and the remediation-actions log (create -> poll the Download Bar -> download the bytes -> upload to a blob container -> generate a read-only SAS link), lists the violation file hits, quarantines each file by calling the RubrikQuarantineFiles sub-playbook, notifies the owner in Microsoft Teams, and marks the violation `REMEDIATED` only when every quarantine succeeded. For `ClassificationResultsAvailable` (no DSPM license) it runs a reduced flow: resolve the snappable identity -> list file hits -> quarantine -> notify. Both flows write a final comment back to the Sentinel incident.

Template version: **1.6.0** (`hidden-SentinelTemplateVersion`).

### Flow detail

**Initialize (both flows)**

* The newest alert on the incident is selected and its Custom Details parsed into variables: `eventType`, `objectId`, `objectName`, `objectType`, `seriesId` (-> violation id), `eventName`, `snapshotId`.
* The RSC service-account client id and secret are read from Key Vault and exchanged for a bearer token through the Rubrik custom connector. An authentication failure comments on the incident and terminates.
* `eventType` routes the run: `SecurityViolation` -> full flow, `Classification` -> reduced flow, anything else -> an "unknown event type" comment on the incident.

**SecurityViolation (full) flow**

1. **Get the violation** — `policyViolation` with `policyTypes: [POLICY_TYPE_DATAGOV]`. Supplies `status`, `violationSeverity`, `resourceId`, `details.snapshotId`, `policy.name` and from `resourceMetadata.metadata` the `platform` and `physicalHost`.
2. **Validate the identifiers** — `objectName`, `objectId` and `snapshotId` taken from the incident are compared against `resourceMetadata.metadata.name`, `resourceId` and `details.snapshotId` returned by RSC. On a mismatch the playbook comments and terminates; it never remediates against an object the incident did not describe.
3. **Resolve the snappable identity** — see below.
4. **Mark `IN_PROGRESS`** before any remediation work starts. A failure here comments and terminates.
5. **Export the violation-files CSV** — `downloadSnapshotResultsCsv`, then poll the Download Bar, download the bytes, upload to blob, create a read-only SAS link.
6. **Export the remediation-actions log** — `createViolationRemediation` with `REMEDIATION_TYPE_EXPORT_ACTIONS_LOG_TO_CSV`, then the same poll/download/upload/SAS sequence.
7. **List the file hits** — paginated 25 at a time, with `fileType: HITS` and `whitelistEnabled: true`.
8. **Quarantine** — the whole files array goes to RubrikQuarantineFiles in a single call.
9. **Notify and close out** — post the owner card to Teams, comment on the incident with the SAS links and per-file results, and set `REMEDIATED` only if every file was quarantined.

**ClassificationResultsAvailable (reduced) flow**

Used when the customer has no DSPM license. There is no violation object, so there is no `policyViolationId`; the `snapshotId` arrives on the incident as a Custom Detail. The flow resolves the snappable identity, lists the file hits (`filters.violationId` omitted), quarantines, notifies and comments. It does **not** export the CSV or log, and does **not** update any violation status.

### Where `siteUrl` / `driveOwnerUpn` come from

Both flows call the RSC `SnappableIdentity` query **once per violation**, not per file:

```graphql
query SnappableIdentity($fid: UUID!) {
  hierarchyObject(fid: $fid) {
    id name objectType
    ... on O365Site     { title url __typename }
    ... on O365Onedrive { userPrincipalName userName userID __typename }
    __typename
  }
}
```

Only one inline fragment is populated, depending on the object type: `O365Site.url` -> `siteUrl`, or `O365Onedrive.userPrincipalName` -> `driveOwnerUpn`. The resolved values are then stamped onto **every** file record sent to the sub-playbook, which uses them to address each file's exact drive instead of searching the tenant.

A failure of this query is **non-fatal** — the run continues, and the sub-playbook reports the affected O365 files as `Failed` rather than acting on the wrong file.

### Export polling

Each export is matched in the Download Bar on three conditions together: the download `type` (`SNAPSHOT_RESULTS_CSV` for the files export), a `filename` containing the object's name pattern, and a `createdAt` at or after the export start time stamped immediately before the export was triggered. This prevents an older export of the same object being picked up. If several downloads match, the newest is used and the ambiguity is recorded in the run's error messages.

Polling runs every `DownloadPollIntervalSec` seconds for at most `DownloadPollMaxAttempts` attempts. An export that fails or never becomes ready is **non-fatal**: the incident comment states that the export was unavailable and the rest of the flow proceeds.

Uploaded exports are written to `/{StorageContainerName}/dspm/{incidentName}/{violationId}/` and shared as read-only SAS links valid for `SasTokenTtlHours`.

### Prerequisites

1. The Rubrik Security Cloud data connector should be configured to send appropriate events to Microsoft Sentinel.
2. The Rubrik Security Cloud solution should be configured to [connect to Rubrik Security Cloud API end points using a Service Account](https://docs.rubrik.com/en-us/saas/saas/polaris_api_access_with_service_accounts.html); the service account should be assigned a role that includes the privileges necessary to read and update policy violations (see [Roles and Permissions](https://docs.rubrik.com/en-us/saas/saas/common/roles_and_permissions.html) in the Rubrik Security Cloud user guide).
3. Deploy the Rubrik custom connector (`Microsoft.Web/customApis`) first, in the same resource group and region. This playbook uses its `Authentication` (`/api/client_token`) operation to obtain the RSC bearer token.
4. Deploy the RubrikQuarantineFiles sub-playbook (HTTP Request-triggered) before this playbook; it is called once per incident with the whole files array and returns `{ status, results: [ { filename, status, newLocation, error } ], error }`.
5. **Version pairing (important):** this playbook sends `siteUrl` and `driveOwnerUpn` on every file record, taken from the RSC snappable identity, so that RubrikQuarantineFiles can resolve each O365 file by its exact drive and path instead of by a tenant-wide search. It must be deployed together with **RubrikQuarantineFiles v3.1.0 or later** (current: v3.2.0). An older sub-playbook ignores the two new fields (harmless); a v3.1.0+ sub-playbook paired with an older parent reports every O365 file as `Failed` with "No drive owner UPN or site URL was supplied", by design, rather than silently acting on the wrong file.
6. Store Service account credentials in Key Vault and obtain the keyvault name.
    a. Create a Key Vault with a unique name.
    b. Go to KeyVault -> secrets -> Generate/import and create 'Rubrik-AS-Int-ClientId' & 'Rubrik-AS-Int-ClientSecret' for storing client_id and client_secret respectively.
7. An Azure Storage account and an EXISTING blob container for the exported CSV/log files (SecurityViolation flow only).
8. Obtain the Teams group id and channel id where the owner-notification card will be posted.
9. An analytics rule that maps the Rubrik event fields into incident Custom Details (eventType, objectId, objectName, objectType, seriesId, eventName, snapshotId).

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
    * SasTokenTtlHours: Validity window (hours) for the read-only SAS link added to the incident comment. Default 72.
    * TeamsGroupId: Id of the Teams Group where the owner-notification card is posted.
    * TeamsChannelId: Id of the Teams Channel where the owner-notification card is posted.
    * DownloadPollIntervalSec: Seconds to wait between Download Bar polls. Default 15.
    * DownloadPollMaxAttempts: Maximum Download Bar poll attempts before giving up on an export. Default 20.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikDSPMViolationRemediation%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FRubrikSecurityCloud%2FPlaybooks%2FRubrikDSPMViolationRemediation%2Fazuredeploy.json)

### Post-Deployment instructions

#### a. Authorize connections

Once deployment is complete, authorize each connection: Rubrik custom connector, Microsoft Teams, Key Vault, Azure Blob Storage and Microsoft Sentinel.

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

This playbook calls the RubrikQuarantineFiles sub-playbook once per incident, passing the whole files array. Deploy that sub-playbook first (same resource group) and set RubrikQuarantineFilesPlaybookName to its Logic App name; it must expose an HTTP Request trigger returning `{ status, results: [ ... ], error }`.

Each file record sent to the sub-playbook carries `filename`, `filePath` (RSC `nativePath`), `nativePath`, `directory`, `ownerUpn` (`createdBy`, falling back to `modifiedBy`), `objectType`, `physicalHost` (NTFS) and `siteUrl` / `driveOwnerUpn` from the violation's RSC snappable identity. The last two let the sub-playbook address the file's drive directly; see the version-pairing note in the prerequisites.

#### d. Configurations in Microsoft Sentinel

1. In Microsoft Sentinel, analytical rules should be configured to trigger an incident. The incident should carry the DSPM Custom Details (eventType, objectId, objectName, objectType, seriesId, eventName, snapshotId) obtained from the corresponding fields in Rubrik DSPM event logs. Check the [documentation](https://docs.microsoft.com/azure/sentinel/surface-custom-details-in-alerts) to learn more about adding custom details to incidents.
2. Configure the automation rules to trigger this playbook on the relevant DSPM incidents (playbooks do not auto-attach).

### Error handling

Every RSC call checks both the HTTP status code and the presence of a non-empty `errors` key, because RSC returns GraphQL errors with HTTP 200. The checks run after `Succeeded`, `Failed` and `TimedOut` so a transport failure is handled rather than silently ending the run.

| Failure point | Behaviour |
|---------------|-----------|
| Authentication | Comment on incident, terminate |
| Get DSPM Violation | Comment on incident, terminate |
| Identifier validation mismatch | Comment on incident, terminate — no remediation is attempted |
| Set status `IN_PROGRESS` | Comment on incident, terminate |
| Get Snappable Identity | Non-fatal: record the error and continue; affected O365 files report `Failed` in the sub-playbook |
| CSV / remediation-log export or poll | Non-fatal: record the error; the incident comment states the export was unavailable |
| List file hits | Comment on incident, terminate |
| Quarantine partially failed | Violation is left `IN_PROGRESS`; per-file failures are listed in the incident comment |
| No file hits at all | Violation is marked `REMEDIATED`; the notification and comment record that no files required quarantine |
