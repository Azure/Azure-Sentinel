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

### Supported product

This alerts connector uses the **CloudHub 1.0** API at
`/cloudhub/api/v2/alerts`. API version `v2` does not mean CloudHub 2.0.
CloudHub 1.0 entitlement is required. CloudHub 2.0 and on-premises Runtime
Manager alerts are not supported by this connector.

MuleSoft documents [CloudHub](https://docs.mulesoft.com/cloudhub/),
[CloudHub 2.0](https://docs.mulesoft.com/cloudhub-2/), and the
[CloudHub API](https://docs.mulesoft.com/cloudhub/cloudhub-api) separately.

### Connect

1. Confirm CloudHub 1.0 entitlement under Access Management's subscription
   information or with your MuleSoft account owner.
2. Enter your regional Anypoint Platform URL, such as
   `https://anypoint.mulesoft.com` or `https://eu1.anypoint.mulesoft.com`.
   The connector resolves the alerts and token endpoint paths on this origin.
   Existing URLs ending in `/cloudhub/api` also work. Custom proxy paths are
   not supported.
3. Select **OAuth2** (recommended). Create a
   [Connected App](https://docs.mulesoft.com/access-management/creating-connected-apps-dev)
   that **acts on its own behalf (client credentials)**. Grant
   **Runtime Manager > Read Alerts** for the requested business group and
   environment. Use the **Connected App's** client ID and secret, not the
   environment's client credentials.
4. Alternatively, select **Basic** only if your Anypoint account supports
   Basic API authentication. Enter its username and password.
5. Supply the matching environment ID and, optionally, an application filter.
   Verify records arrive in `MulesoftCloudhubAlerts_CL`.

Existing connections are not updated automatically by changing these local files.
After publishing/deploying the updated package, select the intended authentication
method when creating a connection. Basic remains available. Before changing the
authentication method for an existing source, delete its old connection using
**DeleteConnector** in the connection grid, then create the replacement.
ARM deployment does not remove the old, differently named authentication branch;
keeping both active causes duplicate collection.

### Diagnose without ingestion

Open a standalone **PowerShell 7** or VS Code `pwsh` terminal, not PowerShell ISE.
From this directory, run:

```powershell
.\Test-MulesoftCloudHubAlerts.ps1 `
  -AuthType OAuth2 `
  -MulesoftBaseUrl 'https://anypoint.mulesoft.com' `
  -EnvironmentId '<environment-id>'
```

The script prompts for the Connected App ID and a masked secret, requests a token
at `/accounts/api/v2/oauth2/token`, then calls the alerts endpoint. Tokens and secrets
are not printed. No Azure resources are changed and no records are ingested.
Use `-AuthType Basic` to test username/password, and `-MaxPages 3` for bounded
pagination. `-ShowResponsePreview` displays vendor response bodies, which can
contain sensitive data; redact before sharing.

Token HTTP 200 confirms token issuance, not alert permissions or ingestion.
For API HTTP 403, read the vendor error: **"organization does not have Cloudhub
1.0 entitlement enabled"** requires a product entitlement change, not a credential
change. Other 403 errors can indicate missing access to the target environment.

### Repeated alert revisions

The endpoint is an alert-list API. No verified timestamp filter is configured.
The polling interval does **not** restrict results to new alerts. Pagination
retrieves the list but does not prevent repeat ingestion.

The connector provides an optional **Deduplicate repeated CloudHub alert revisions**
sample query:

```kusto
let alerts = MulesoftCloudhubAlerts_CL | where TimeGenerated > ago(24h);
union
(alerts
 | where isnotempty(Id) and isnotnull(LastModified)
 | summarize arg_max(TimeGenerated, *) by OrganizationId, EnvironmentId, Id,
     CreatedAt, LastModified, Name, Severity, ProductName, Enabled, IsSystem,
     _ConditionKey = tostring(Condition), _ActionsKey = tostring(Actions)
 | project-away _ConditionKey, _ActionsKey),
(alerts | where isempty(Id) or isnull(LastModified))
```

This keeps one collected copy of an identical alert revision in the queried period,
while retaining revisions with different timestamps or payload fields. Records
without an ID or last-modified timestamp pass through unchanged. Nested JSON
serialization differences can prevent duplicates from matching. Identical revisions
collected by multiple connections are intentionally combined.

Use this query, or save it as a workspace function, in consumers that require
deduplicated alerts. The existing `MuleSoftCloudhub` parser is unchanged.
Deduplication does **not** remove stored rows, lower ingestion costs, or prove that
the source provides a complete history of alert occurrences.

## Migration scope

The old Azure Function polls alerts, discovers applications, and retrieves each
application's logs. The alerts CCF connector replaces only the alerts path.
The separate logs CCF connector is push-based: each application's log forwarding
must be configured and verified independently. Do not disable the Function until
the required alerts and application logs have been validated.
