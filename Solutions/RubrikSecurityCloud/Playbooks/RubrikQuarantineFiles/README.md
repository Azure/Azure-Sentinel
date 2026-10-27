# Rubrik Quarantine Files

## Summary

This is a child (HTTP Request-triggered) playbook that quarantines a batch of files reported in a Rubrik DSPM violation. The caller (RubrikDSPMViolationRemediation) passes the whole files array in a single call, and this playbook iterates internally and routes on `objectType`: OneDrive / SharePoint files are moved to a quarantine folder via Microsoft Graph, and Windows file-share (NTFS) files are quarantined on their host via Microsoft Defender for Endpoint. It returns a per-file result set to the caller.

Template version: **3.2.0** (`hidden-SentinelTemplateVersion`).

### Request and response contract

The caller sends the whole batch in one call:

```json
{
  "objectType": "O365_ONEDRIVE",
  "files": [
    {
      "filename":      "OrgwideFile.json",
      "filePath":      "/Documents/CrestTesting/OrgwideFile.json",
      "nativePath":    "/Documents/CrestTesting/OrgwideFile.json",
      "directory":     "/Documents/CrestTesting",
      "ownerUpn":      "admin@contoso.com",
      "objectType":    "O365",
      "physicalHost":  "fileserver01.contoso.com",
      "driveOwnerUpn": "alex.carter@contoso.com",
      "siteUrl":       "https://contoso.sharepoint.com/sites/Finance"
    }
  ]
}
```

The response carries the overall status, the per-file results and a top-level error summary:

```json
{
  "status": "success",
  "results": [
    { "filename": "OrgwideFile.json", "status": "Success",
      "newLocation": "https://contoso.sharepoint.com/.../Quarantine/OrgwideFile.json",
      "error": "" }
  ],
  "error": ""
}
```

`status` is `success` only when no per-file result is `Failed`. The caller uses exactly this value to decide whether the violation may be marked `REMEDIATED`.

### Routing on objectType

`objectType` is taken from the request body, falling back to the first file's own `objectType`, and is upper-cased before matching. Raw RSC object types are accepted directly — there is no need for the caller to normalise them:

| Routed to | Matches |
|-----------|---------|
| OneDrive / SharePoint (Graph) | anything containing `ONEDRIVE`, plus `O365_SITE`, `O365_ONEDRIVE`, `O365_MAILBOX`, `O365_SHAREPOINT_DRIVE` |
| NTFS (Defender for Endpoint) | anything containing `WINDOWS_FILESET`, `WINDOWS_FILESHARE` or `NTFS` |
| Unsupported | anything else — reported as an unknown object type, nothing is modified |

### How O365 files are located (v3.2.0)

Each O365 file is resolved **directly by drive and path** — never by a tenant-wide search:

1. The target drive comes from the RSC snappable identity supplied by the caller:
   * `driveOwnerUpn` (from `O365Onedrive.userPrincipalName`) -> `GET /v1.0/users/{upn}/drive`
   * `siteUrl` (from `O365Site.url`) -> `GET /v1.0/sites/{host}:{path}` -> `GET /v1.0/sites/{siteId}/drives`
2. The item comes from `filePath` (RSC `nativePath`). RSC may prefix this with the
   document-library name (e.g. `/Documents/CrestTesting/report.csv`), but Graph's
   `root:` **is** that library — so the playbook strips a leading segment matching the
   resolved drive's own `name` before the lookup:
   `GET /v1.0/drives/{driveId}/root:/{path}`

   The strip uses the actual drive name, so it works for any library name, is a no-op
   for unprefixed paths, and will not remove a genuine folder that merely looks similar.

Backslashes in `filePath` are normalised to forward slashes and any leading slash is removed before the lookup.

#### Sites with multiple document libraries

A SharePoint site can host more than the default `Documents` library, and the library
can vary **file by file within a single violation** (e.g. one violation containing both
`/Documents/report.csv` and `/TestLibrary2/hr-records.csv`).

The playbook therefore enumerates **all** libraries for the site once per file batch via
`GET /v1.0/sites/{siteId}/drives`, then for each file matches the leading segment of
`filePath` against each library's `name` — and, as a fallback, the last segment of its
`webUrl` (these differ for renamed libraries, e.g. display name `Documents` vs URL
segment `Shared Documents`). The matched library supplies the `driveId` used for the
lookup, and the leading segment is then stripped from the path.

If no library matches the leading segment, the playbook falls back to the site's default
library and treats the whole path as drive-relative — the original behavior, which is
correct for single-library sites and for paths that carry no library prefix.

This is a per-file match against one already-fetched list, not a per-library probe: there
is exactly one extra-cost-free Graph call per site (`/drives` replaces `/drive`), and no
retry loop. The quarantine folder and the moved copy are created in the **same** library
as the source file, because every downstream call derives its drive from the resolved
item's own `parentReference.driveId`.

If the file cannot be resolved at that exact drive and path, it is reported as `Failed` and **nothing is
modified**. There is deliberately no fallback to a filename search: a search cannot see files in a user's
private OneDrive under application permissions, and where the same filename exists elsewhere in the tenant
it can return — and act on — the wrong copy.

> Requires the caller to send `driveOwnerUpn` / `siteUrl`. See RubrikDSPMViolationRemediation, which
> resolves them once per violation from the RSC `SnappableIdentity` (`hierarchyObject`) query and stamps
> them onto every file record.

#### How the move is performed

The file is **copied server-side and then deleted** — the bytes never pass through the Logic App:

1. `POST /v1.0/drives/{sourceDriveId}/items/{sourceItemId}/copy` with the quarantine folder as `parentReference`. Graph returns `202 Accepted` and a `Location` header.
2. The monitor URL is polled every 3 seconds until the copy leaves `inProgress` / `notStarted`.
3. The new item is read back to capture its `webUrl`, which is returned as `newLocation`.
4. `DELETE /v1.0/drives/{sourceDriveId}/items/{sourceItemId}` completes the move.

Because there is no download/upload step, there is no 250 MB simple-upload limit and no upload-session handling.

> If the copy succeeds but the delete fails, the file is reported as **`Failed`** with
> "Uploaded to quarantine but failed to delete the source; delete manually." The copy in quarantine is
> left in place — this is a deliberate fail-safe, not a silent success.

Files with the same name are renamed by Graph rather than overwritten.

### How NTFS files are quarantined

Windows file-share files are quarantined on their host through Microsoft Defender for Endpoint:

1. `GET /api/machines?$filter=computerDnsName eq '{physicalHost}'` resolves the device.
2. An advanced hunting query over `DeviceFileEvents`, matched on `DeviceId`, `FileName` and `FolderPath`, obtains the file's SHA1 — MDE addresses files by hash, not by path.
3. `POST /api/machines/{machineId}/StopAndQuarantineFile` submits the action.
4. `GET /api/machineactions/{actionId}` is polled every 15 seconds until a terminal state is reached. Only `Succeeded` is reported as a success.

> NTFS quarantine depends on `physicalHost`, which RSC populates only on **SecurityViolation** events.
> Classification events never carry it, so NTFS quarantine is not available on the caller's reduced flow.

### Prerequisites

1. A single Azure AD app registration used for BOTH Microsoft Graph and Microsoft Defender for Endpoint (MDE). It needs Microsoft Graph **application** permissions `Files.ReadWrite.All`, `Sites.ReadWrite.All`, `User.Read.All` AND WindowsDefenderATP (MDE) **application** permissions `Machine.ReadWrite.All` (or `Machine.StopAndQuarantine`) and `AdvancedQuery.Read.All`, all admin-consented.

   The same client id/secret is used to request two separate tokens via the client-credentials grant, one per scope: `https://graph.microsoft.com/.default` and `https://api.securitycenter.microsoft.com/.default`.
2. Store the app registration credentials in Key Vault and obtain the keyvault name.
    a. Create a Key Vault with a unique name.
    b. Go to KeyVault -> secrets -> Generate/import and create TWO secrets using **exactly** these names — they are fixed in the playbook and are **not** deployment parameters:
        * `Graph-App-ClientId` — the app registration's Application (client) ID
        * `Graph-App-ClientSecret` — the app registration's client secret VALUE

      The same credentials authenticate both Microsoft Graph and MDE.
3. Obtain the Teams group id and channel id where the quarantine-folder Adaptive Card will be posted (used by the OneDrive/SharePoint branch only).
4. For NTFS quarantine, the target file shares must be hosted on devices onboarded to Microsoft Defender for Endpoint, reachable by their physicalHost / computerDnsName.

### Deployment instructions

1. To deploy the Playbook, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    * PlaybookName: Enter the playbook name here. Must match the RubrikQuarantineFilesPlaybookName parameter on the caller (RubrikDSPMViolationRemediation).
    * TeamsGroupId: Id of the Teams Group where the quarantine-folder Adaptive Card is posted.
    * TeamsChannelId: Id of the Teams Channel where the quarantine-folder Adaptive Card is posted.
    * KeyVaultName: Name of the keyvault where the app registration credentials are stored.
    * TenantId: Azure AD tenant ID used for the Microsoft Graph / MDE OAuth2 token endpoint.

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

1. Create/point ONE app registration used for both Microsoft services and store its client id/secret in Key Vault under the fixed secret names `Graph-App-ClientId` and `Graph-App-ClientSecret`.
2. Grant it Microsoft Graph application permissions `Files.ReadWrite.All`, `Sites.ReadWrite.All`, `User.Read.All` AND WindowsDefenderATP application permissions `Machine.ReadWrite.All` (or `Machine.StopAndQuarantine`) and `AdvancedQuery.Read.All`, all admin-consented.
3. For NTFS quarantine, ensure the file-share hosts are onboarded to Microsoft Defender for Endpoint and resolvable by their physicalHost / computerDnsName.

#### d. Wire up the caller

This playbook has an HTTP Request trigger and does not run on its own. The caller RubrikDSPMViolationRemediation references it by the RubrikQuarantineFilesPlaybookName parameter and must be deployed in the same resource group. Ensure the PlaybookName here matches that value.

#### e. Operator action at run time

The OneDrive/SharePoint branch posts an Adaptive Card to the configured Teams channel and **waits** for a reply before touching any file. The operator pastes a share link to the destination quarantine folder (create the folder first, then use Share / Copy link). All files in the batch are moved into that single folder, whichever drive each file came from.

If the share link cannot be resolved, the whole batch is reported as failed and **no file is modified**.

### Error handling

| Failure point | Behaviour |
|---------------|-----------|
| Graph or MDE authentication | Return a failed response to the caller and terminate |
| Quarantine folder share link not resolved | Whole batch reported failed; no file is touched |
| Missing both `driveOwnerUpn` and `siteUrl` | File reported `Failed` with "No drive owner UPN or site URL was supplied" |
| Missing `filePath` | File reported `Failed` |
| Drive or site unresolved | File reported `Failed` |
| Item not found at the exact drive + path | File reported `Failed`; nothing is modified, no search fallback |
| Copy not accepted or did not complete | File reported `Failed`; the source file is **not** deleted |
| Copy succeeded but delete failed | File reported `Failed`; quarantine copy left in place, delete the source manually |
| NTFS: no `physicalHost`, device not found, or SHA1 not found | File reported `Failed` with the specific reason |
| NTFS: machine action did not reach `Succeeded` | File reported `Failed` with the terminal state as the reason |
