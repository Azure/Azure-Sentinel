# MuleSoft CloudHub CCF connectors

## Application logs: push setup

The Logs CCF connector receives records in `MuleSoftCloudhubLogs_CL`; it does
not discover applications or call the CloudHub application/log APIs.
Deploying it creates receiving resources, not a MuleSoft sender.

1. Open the **MuleSoft CloudHub Logs** connector in Microsoft Sentinel and select
   **Deploy**. Copy the sender configuration values displayed after deployment.
   Verify the Entra application has **Monitoring Metrics Publisher** access on
   the DCR.
2. Select a custom asynchronous Log4j appender compatible with Azure Monitor
   Logs Ingestion, or an external collector that implements that API.
   No ready-made sender is supplied with this solution.
3. Configure each Mule application's `pom.xml` and
   `src/main/resources/log4j2.xml` using the appender's instructions.
   Follow the [CloudHub 1.0 guide](https://docs.mulesoft.com/cloudhub/custom-log-appender)
   or [CloudHub 2.0 guide](https://docs.mulesoft.com/cloudhub-2/ch2-integrate-log-system)
   for your deployment; their configurations are not interchangeable.
4. Use the connector's copied Entra tenant ID, client ID, protected secret,
   DCE URL, DCR immutable ID and stream name in the sender. It must implement
   token refresh, DCR field mapping, batching, retries and delivery monitoring.
   Use Entra credentials, not MuleSoft Connected App credentials; the DCE is an
   endpoint, not an authentication method. Do not hardcode secrets in
   `log4j2.xml`. A generic HTTP appender alone is insufficient. See the
   [Logs Ingestion API examples](https://learn.microsoft.com/azure/azure-monitor/logs/tutorial-logs-ingestion-code).
5. Send a uniquely identifiable test log and verify its message and application
   context in `MuleSoftCloudhubLogs_CL` before rolling out or disabling existing
   logging. The connector UI includes the ingestion request and schema guidance.

```kusto
MuleSoftCloudhubLogs_CL
| where TimeGenerated > ago(1h)
| project TimeGenerated, ApplicationDomainName, Level, Message
| take 10
```

If the test log is missing, inspect sender delivery errors: check the Entra token
for 401, DCR permissions for 403, and stream/schema mapping for 400.
Confirm network access to the DCE and token endpoint.

## Alerts

### Select the CloudHub platform

The **CloudHub deployment platform** radio selector displays the fields required
for CloudHub 1.0 or CloudHub 2.0. API version `v2` does not identify the deployment
platform. Customers using both can create separate connections in the same
connector; each connection selects one platform and environment.

| Selection | Authentication and fields | API and destination |
| --- | --- | --- |
| CloudHub 1.0 | Connected App client ID/secret; environment ID; optional application filter | `/cloudhub/api/v2/alerts` -> `MulesoftCloudhubAlerts_CL` |
| CloudHub 2.0 | Connected App client ID/secret; organization/business group ID; environment ID | `/amc/application-manager/api/v2/organizations/{organizationId}/environments/{environmentId}/alerts` -> `MulesoftCloudhubAlerts_CL` |

Both platforms write to **MulesoftCloudhubAlerts_CL**. The DCR assigns the
**CloudHubVersion** string column to `1.0` or `2.0` based on the input stream,
not a vendor-provided field. Two input streams are retained to identify the
source platform; both data flows target this one table.

```kusto
MulesoftCloudhubAlerts_CL
| where ingestion_time() > ago(1h)
| summarize Records = count() by CloudHubVersion
```

CloudHub 1.0 requires its product entitlement. CloudHub 2.0-only access cannot
enable the 1.0 API. Both paths collect **alert configuration snapshots**, not
fired-alert history or application logs. On-premises Runtime Manager alerts are
not supported. OAuth2 token issuance uses the same Anypoint Platform
`/accounts/api/v2/oauth2/token` endpoint for both platforms.

MuleSoft documents [CloudHub](https://docs.mulesoft.com/cloudhub/),
[CloudHub 2.0](https://docs.mulesoft.com/cloudhub-2/), and the
[CloudHub API](https://docs.mulesoft.com/cloudhub/cloudhub-api) separately.
The [AMC API reference](https://dev-portal.mulesoft.com/apis/amc-application-manager.html)
documents the CloudHub 2.0 organization/environment-scoped alerts API.

### Connect

1. Select **CloudHub 1.0** or **CloudHub 2.0** according to the deployment
   platform used by the source environment. Confirm the relevant access with
   your MuleSoft account owner. For 1.0, confirm CloudHub 1.0 entitlement.
2. Enter your regional Anypoint Platform URL, such as
   `https://anypoint.mulesoft.com` or `https://eu1.anypoint.mulesoft.com`.
   The connector resolves the alerts and token endpoint paths on this origin.
   Existing URLs ending in `/cloudhub/api` also work. Custom proxy paths are
   not supported.
3. Create a
   [Connected App](https://docs.mulesoft.com/access-management/creating-connected-apps-dev)
   that **acts on its own behalf (client credentials)**. Grant
   **Runtime Manager > Read Alerts** for the requested business group and
   environment. Use the **Connected App's** client ID and secret, not the
   environment's client credentials. Connected App OAuth2 is the only offered
   authentication method for both platforms; no authentication selector or
   Anypoint username/password fields are displayed.
4. For **1.0** only, optionally enter an application name to filter alert
   configurations. Leave it blank for no application restriction.
5. For **2.0**, enter the organization/business group ID that owns the environment.
   Supply the matching environment ID for either platform, then verify receipt
   in `MulesoftCloudhubAlerts_CL` using `ingestion_time()` and `CloudHubVersion`.

Existing connections are not updated automatically by changing these local files.
After publishing/deploying the updated package, select the intended platform
and enter Connected App credentials when creating a connection. Basic is no
longer offered for new connections. Installing this package does not delete
or convert existing Basic connections; replace them manually with OAuth2.
Before replacing an existing source connection, delete its old connection using
**DeleteConnector** in the connection grid, then create the replacement.
ARM deployment does not remove the old, differently named authentication branch;
keeping both active causes duplicate collection.
The same applies to a previously deployed separate `MulesoftCloudhub2Connector`:
its active connections are not moved or deleted by this unified definition.
Existing 1.0 connections can have a blank platform column until re-created.
Deploy the updated shared table schema and DCR before recreating connections.
Existing CloudHub 2.0 connections must be recreated to use the shared destination
configuration. Historical data in `MulesoftCloudhub2Alerts_CL` is not moved or
deleted; that table is no longer provisioned by this package. The `MuleSoftCloudhub`
parser still reads it alongside the shared table, legacy Function data and Push logs.
Older 1.0 rows have no `CloudHubVersion` value in the raw table. The parser labels
them `1.0` and historical rows from the former 2.0 table `2.0`; existing nonempty
platform values are preserved. Push logs have no inferred platform value.

### Recorded validation and remaining checks

Earlier CloudHub 2.0 testing recorded successful Connected App authentication,
an AMC alerts response, native connection creation and a matching ingested
configuration. Those results validate the earlier separate 2.0 path, not this
new unified UI/package. Neither this change nor the 2.0 results prove live
CloudHub 1.0 collection.

Token HTTP 200 confirms token issuance, not alert permissions or ingestion.
For API HTTP 403, read the vendor error: **"organization does not have Cloudhub
1.0 entitlement enabled"** requires a product entitlement change, not a credential
change. Other 403 errors can indicate missing access to the target environment.

If connection creation fails with an invalid `concat(workspace-name, ...)`
expression, the failure occurs during ARM template validation, before
authentication. Install the corrected package before retrying: both OAuth2 poller
names use the connection template's `innerWorkspace` parameter so the workspace
is resolved at connection deployment, not inserted as unquoted expression text.
Replacing the local ZIP alone does not update an installed connection template.

Before production use, verify OAuth2 for each intended platform in
the portal, including required-field visibility, connection creation, repeated
polls, pagination and token renewal. Validate additional control planes separately.
Do not retire the legacy Function based on content deployment alone.

### Repeated alert revisions

The endpoint is an alert-list API. No verified timestamp filter is configured.
The polling interval does **not** restrict results to new alerts. Pagination
retrieves the list but does not prevent repeat ingestion.

The connector provides an optional **Deduplicate repeated CloudHub alert revisions**
sample query:

```kusto
let alerts = MulesoftCloudhubAlerts_CL
    | where ingestion_time() > ago(24h)
    | extend CloudHubVersion = coalesce(tostring(column_ifexists('CloudHubVersion', '')), '1.0');
union
(alerts
 | where isnotempty(Id) and isnotnull(LastModified)
 | summarize arg_max(ingestion_time(), *) by CloudHubVersion, OrganizationId, EnvironmentId, Id,
     CreatedAt, LastModified, Name, Severity, ProductName, Enabled, IsSystem,
     _ConditionKey = tostring(Condition), _ActionsKey = tostring(Actions)
 | project-away _ConditionKey, _ActionsKey),
(alerts | where isempty(Id) or isnull(LastModified))
```

This keeps one collected copy of an identical alert revision in the queried period,
while retaining revisions with different timestamps or payload fields. Records
without an ID or last-modified timestamp pass through unchanged. Nested JSON
serialization differences can prevent duplicates from matching. Identical revisions
collected by multiple connections on the same platform are intentionally combined.
The `CloudHubVersion` key keeps the two platforms separate.

Use this query, or save it as a workspace function, in consumers that require
deduplicated alerts. The `MuleSoftCloudhub` parser also includes historical 2.0 data.
Deduplication does **not** remove stored rows, lower ingestion costs, or prove that
the source provides a complete history of alert occurrences.

## Migration scope

The old Azure Function polls alerts, discovers applications, and retrieves each
application's logs. The alerts CCF connector replaces only the alerts path.
The separate logs CCF connector is push-based: each application's log forwarding
must be configured and verified independently. Do not disable the Function until
the required alerts and application logs have been validated.
