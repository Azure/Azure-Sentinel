# Workday Email Activity - custom CCF connector

Connector version **1.0.1**. This community-supported connector collects completed
Email ID Change events from a Workday Report-as-a-Service (RaaS) custom report into
the standard `ASimAuditEventLogs` table. It is separate from the Microsoft Workday
User Activity connector. It does **not** support WQL endpoints.

## ARM deliverable

Deploy [PollerConnector.json](./PollerConnector.json) as a resource-group ARM
template in the resource group of an existing Microsoft Sentinel workspace.
[PollerConnector.parameters.json](./PollerConnector.parameters.json) is a
credential-free example parameter file; replace the workspace name and region
before use. Use Azure Portal **Deploy a custom template > Build your own template
in the editor**, load the installer, and review its resources before deployment.
Deployment is an environment write and requires the environment owner's approval.

| Parameter | Meaning |
|---|---|
| `workspace` | Existing workspace **resource name**, not its workspace/customer GUID. Must be in the deployment resource group. |
| `workspace-location` | Actual workspace region. Defaults to the resource group region; override when they differ. |
| `existingDataCollectionEndpointResourceId` | Optional DCE resource ID in the workspace region. Empty creates a dedicated DCE with public network access. This is not a logs ingestion URL. |
| `dataCollectionRuleName` | Optional dedicated DCR name for Sentinel to create during connection. Empty selects a stable workspace-specific name. |

The installer registers the connector definition, metadata, connection templates,
and custom content package. It creates a DCE unless an existing DCE is supplied.
It does **not** deploy an authenticated poller, accept Workday credentials, or
perform token exchange during installation.

After installation, open **Microsoft Sentinel > Data connectors > Workday Email
Activity (via Codeless Connector Framework)**. Supply the endpoints and OAuth
credentials and complete Workday consent. Sentinel uses the definition template
to create the DCR and the connection template to create the poller. Installation
success is not connection or ingestion success.

This is a custom ARM installation, not a Marketplace submission or a generated
Content Hub ZIP. The connector is version 1.0.1; the content-package envelope is
version 3.0.1 to satisfy the CCF solution-envelope version convention.

## Prerequisites

- An existing Microsoft Sentinel-enabled Log Analytics workspace and access to
  the standard `ASimAuditEventLogs` ingestion destination. This connector does not
  redefine the standard table schema, its plan, or its retention.
- Workspace read/write/delete permissions; permission to manage Sentinel
  definitions, metadata, content templates, and content packages; and
  `Microsoft.Insights/dataCollectionEndpoints/write` and
  `Microsoft.Insights/dataCollectionRules/write` in the relevant resource group.
- If reusing a DCE, its region must match the workspace and its network policy
  must allow CCF ingestion. Do not select a private-only DCE without validating
  the supported network path.
- A Workday OAuth API client configured for **Authorization Code Grant** and
  **Bearer** access tokens, with functional-area permissions for the report.
- An authorizing Workday user permitted to execute the report. Verify that
  Workday's token lifecycle permits continued unattended access by CCF.
- A web-service-enabled RaaS report returning the exact contract below.

## Workday report contract

Configure the actual report URL using Workday's web-service URL for the custom
report. It typically has this path:

`https://<services-host>/ccx/service/customreport2/<tenant>/<report-owner>/<report-name>`

Enter the URL **without query parameters**. The connector supplies:

| Query parameter | Value |
|---|---|
| `format` | `json` |
| `After_Date_Time` | CCF query-window start time |
| `Before_Date_Time` | CCF query-window end time |

The report must honor both prompts and return **all** matching rows in a single
`Report_Entry` array. The owner confirmed this endpoint is unpaginated; no
`limit`, `offset`, or invented page-size parameters are sent. Windows are five
minutes. Define nonoverlapping prompt boundaries in the report and confirm empty
windows return an empty array, not HTML or a login page. If Workday truncates a
response, reduce volume or redesign the report before using the connector.

Expected response shape (synthetic example):

```json
{
  "Report_Entry": [
    {
      "DateTimeStamp": "2026-10-30T14:00:00Z",
      "EmailIDBefore": "previous@example.invalid",
      "EmailIDAfter": "current@example.invalid",
      "Employee_ID": "EXAMPLE-001",
      "Login_ID": "example-user",
      "TargetID": "example-event-001",
      "Worker": "Example Worker"
    }
  ]
}
```

All seven source fields are strings. `DateTimeStamp` must parse as an ISO 8601
timestamp with a timezone; no ingestion-time fallback hides malformed timestamps.
This contract represents completed changes, so the existing `EventResult=Success`
mapping is retained. If the report includes failed attempts, nested objects, or
different columns, update the source contract and DCR before connecting.

| Source field | ASIM destination |
|---|---|
| `DateTimeStamp` | `TimeGenerated`, `EventStartTime`, `EventEndTime` |
| `EmailIDBefore` / `EmailIDAfter` | `OldValue` / `NewValue` |
| `Employee_ID` | `ActorUserId` |
| `Login_ID` | `ActorUsername` |
| `TargetID` | `EventOriginalUid` |
| `Worker` | `Object` |

The original identity mappings are preserved. Confirm with the report owner that
`Employee_ID` and `Login_ID` identify the actor, not just the employee whose email
changed, and that `TargetID` is an event identifier before relying on these
columns for identity-based detections or deduplication.

The DCR explicitly projects only supported standard-table columns. It does not
send the former extra columns `DateTimeStamp`, `EventSchema`, or `Dvc` to the
standard table. The input stream is `Custom-WorkdayEmailActivity`, and the output
stream is `Microsoft-ASimAuditEventLogs`. Queries retain
`EventProduct == "Workday"` and `Operation == "Email Activity"`.

## OAuth setup and connection

1. Enable OAuth 2.0 clients in Workday tenant security settings.
2. Register the API client with the grant type and report permissions above.
3. Register exactly this redirect URI:
   `https://portal.azure.com/TokenAuthorize/ExtensionName/Microsoft_Azure_Security_Insights`
4. Retrieve the **token** and **authorization** endpoints from **View API
   Clients** in the same Workday tenant. The authorization host can differ from
   the services host; do not construct either from an example.
5. In the connector page, enter the token URL, authorization URL without query
   parameters, and RaaS report URL without query parameters. The connector adds
   `redirect=n` once to the authorization request.
6. Supply an OAuth scope only if the Workday administrator confirms an explicit
   scope string is required. Microsoft CCF's generic OAuth reference marks Scope
   required, while the published Workday connector omits it. This connector
   exposes Scope with an empty default to preserve that Workday behavior; verify
   tenant compatibility rather than guessing `System`, `openid`, or
   `offline_access`. Workday functional-area selection is not automatically an
   OAuth scope string.
7. Enter the client ID and secret in the OAuth form, click **Connect once**, and
   complete Workday authorization. Do not submit a second connection while the
   first is pending. A code is single-use; every new attempt needs fresh consent
   and a newly issued code.

Credentials use `securestring` parameters in stored connection templates and
are not embedded in labels or Terraform configuration. Do not log or commit
tokens, authorization codes, or secrets. Rotate any genuine secret previously
placed in the standalone definition's form labels; source removal does not erase
repository history, deployed metadata, or copies.

`retryCount: 3` remains a data-request setting. It does not prove that CCF retries
OAuth token redemption three times. If token acquisition still fails, correlate
the first Workday token response with the Azure deployment operation and UTC
timestamp; a browser HAR alone does not capture backend-to-Workday exchanges.

## Source files and consistency

| File | Purpose |
|---|---|
| [PollerConnector.json](./PollerConnector.json) | Self-contained ARM installer and embedded CCF templates. Deploy this file. |
| [DataConnectorDefination.json](./DataConnectorDefination.json) | Standalone UI definition. Original filename retained for compatibility. |
| [PollingConfig.json](./PollingConfig.json) | Standalone CCF polling component with CCF placeholders. Not a standalone deployment template. |
| [DataConnectionRules.json](./DataConnectionRules.json) | Standalone DCR component with CCF placeholders. Not a standalone deployment template. |
| [connection-template.json](./connection-template.json) | Unescaped ARM equivalent of the poller for reviewing the portal connection contract. Not the installer or an unattended Terraform entry point. |

The standalone components and installer must stay synchronized. The polling
component uses the short SecurityInsights resource type; the ARM installer uses
the workspace-qualified ARM resource type and resource name. CCF component
placeholders such as `{{clientSecret}}` become secure parameter references in the
ARM connection template. ARM expressions
inside stored connection templates are escaped with `[[` so credentials and
endpoints resolve at connection time, not installer deployment time.

## Terraform

The Terraform module now wraps only the installer. It reads the existing resource
group and workspace to obtain the actual workspace region. It does **not** read
Key Vault secrets, redeem authorization codes, directly create DCRs or pollers,
or ignore installer-template changes.

Use the existing environment backend and environment variables for your own
approved workflow. Required input: `subscription_id`. Set `workspace` and
`resource_group_name` explicitly when computed names do not match your resources.
Optional DCE reuse is supported through
`existing_data_collection_endpoint_resource_id`, or
`data_collection_endpoint_name` for a DCE in the workspace resource group, but
not both. Empty selects a new dedicated DCE.

Removed inputs: `connectors`, `deploy_connections`,
`create_data_collection_resources`, `key_vault_name`, and
`key_vault_resource_group`. Remove these from pipeline variable arguments and
external tfvars too. Workday endpoints and credentials now belong exclusively
to the portal connection. Removed direct-connection outputs must not be used by
pipeline consumers; use the installer outputs and `next_step` instead.

### Existing deployment migration - do not apply blindly

Removing the former DCR and poller resources from configuration can make Terraform
plan their destruction. Before using this version on an existing state:

1. Back up state securely and inventory actual resources and Terraform addresses.
   Old state may contain Workday credentials; protect the backup accordingly.
2. Obtain environment-owner approval for the migration and any state changes.
3. Decide whether to retain or retire each old DCR and poller. If retaining them,
   an operator must detach the exact legacy managed-resource addresses from state
   without deleting Azure resources, following the organization's reviewed state
   migration procedure. Relevant former blocks are
   `azurerm_monitor_data_collection_rule.workday_email` and
   `azurerm_resource_group_template_deployment.workday_email_connection`.
   Do not assume deleting an ARM deployment record deletes its child poller.
4. The new installer preserves its Terraform deployment address, but the canonical
   definition is now `WorkdayEmailCCPDefinition`. The old long
   `WorkdayEmailTemplateConnectorDefinition` and old `WorkdayEmail` or
   `WorkdayEmailPoller-*` pollers are not automatically deleted by an incremental
   deployment. Disable/disconnect legacy polling under approval before activating
   the replacement to avoid duplicate ingestion and authorization activity.
5. Keep existing DCRs independent or explicitly transfer ownership before
   reusing a name. The default new DCR name differs from the old static names.
   Do not let both Terraform and Sentinel manage the same DCR.
6. Review the plan. Stop if it proposes unexpected deletion or changes to shared
   resources. Complete portal OAuth only after the approved installation.

This repository change does not perform any state migration, Azure deployment,
resource cleanup, OAuth connection, or credential rotation.

## Repairing "content template not found"

The initial 1.0.1 installer used abbreviated `contentProductId` hash inputs.
These differed from the identifiers in Microsoft's CCF ARM example and the
published Workday connector, even though `contentId` and connector metadata
appeared to match. The corrected installer uses the canonical hash input:

`<solutionId>-<contentKind>-<contentId>-<contentVersion>`

The definition uses `DataConnector` and the connector version; the connection
uses `ResourcesDataConnector` and the connector version; the package uses
`Solution` and the solution version. The two content templates' `version` fields
also follow the example's solution-envelope version, while metadata dependency
versions remain at the connector version. Matching `contentId` alone is not
sufficient to establish correct template registration.

To apply this correction, obtain approval and redeploy the updated
[PollerConnector.json](./PollerConnector.json) in **Incremental** mode to the
same workspace and resource group, with the same parameter values. The resource
names and versions are unchanged, so the existing template resources are updated
rather than renamed. Do not delete the workspace, connector, DCR, or DCE.
Confirm the installer deployment succeeds, close and reopen the connector page,
then enter the actual RaaS endpoint and complete a fresh OAuth connection.

This corrects a source-level registration mismatch consistent with the reported
error. Successful template lookup in the deployed workspace still requires a
live check. If the error persists, inspect both deployed content templates and
the connector metadata, including `contentId`, `contentProductId`, `contentKind`,
`version`, `packageId`, `packageVersion`, and the target workspace.

## Verification

Run the repository build-and-validation entry point in validation-only mode for
this custom ARM deliverable. This folder does not contain Marketplace solution
data for V3 ZIP packaging.

After an approved deployment, verify definition visibility, successful fresh
OAuth authorization, DCR stream alignment, empty and populated query windows,
token renewal, and actual rows in `ASimAuditEventLogs`. Query
`EventProduct == "Workday"` and `Operation == "Email Activity"`. The
`HasDataConnectors` gallery criterion indicates connector-resource presence,
not proof that report data has arrived.

Static checks cannot prove Workday credentials, token endpoint reachability,
refresh behavior, source-field semantics, or the absence of backend OAuth
retries. Those require a separately approved live test.

### Local validation limitations (30 October 2026)

- The CCF multi-file validation tool reports one cross-file error: it expects a
  manual UX parameter named `authorizationCode`. This connector uses
  `OAuthForm`, which supplies that code through the OAuth redirect flow instead.
  The tool also warns that the authorization endpoint UI input is unused,
  although it is referenced by `auth.AuthorizationEndpoint`. Do not add a
  manual code textbox or remove the endpoint to suppress these diagnostics.
  The validator needs maintainer review for this OAuthForm configuration.
- The required repository runner was invoked with `-SkipPackaging` and the
  approved patch bump. It exited with code 2 before validation:
  `Data folder not found: Solutions\Workday_Email_CCF\Data`. It did not emit a
  complete build report. Supporting custom ARM-only folders in that runner
  requires a separate maintainer change; no tooling was modified here.
- Terraform CLI is not installed in this environment, so Terraform formatting
  and provider validation have not been executed.
- No Azure template validation, deployment, Workday authentication, ingestion,
  or token-renewal test has been performed. Treat this deliverable as authored
  content pending those checks, not a fully qualified production connector.

## References

- [Create a pull CCF connector](https://learn.microsoft.com/azure/sentinel/isv/create-codeless-connector)
- [CCF authentication and polling reference](https://learn.microsoft.com/azure/sentinel/data-connector-connection-rules-reference)
- [CCF UI reference](https://learn.microsoft.com/azure/sentinel/data-connector-ui-definitions-reference)
- [ASimAuditEventLogs table schema](https://learn.microsoft.com/azure/azure-monitor/reference/tables/asimauditeventlogs)

## Version history

| Version | Date | Changes |
|---|---|---|
| 1.0.1 | 30-10-2026 | ARM-first installation and portal-only OAuth activation; secure credential parameters; consistent connector identity; unpaginated RaaS polling; standard-table projection; Terraform migration guidance; corrected CCF content-product hash inputs and template-envelope versions for template discovery. |
