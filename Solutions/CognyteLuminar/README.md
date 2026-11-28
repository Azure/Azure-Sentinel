# Cognyte Luminar Threat Intelligence for Microsoft Sentinel

Version 3.2.2

This solution brings Cognyte Luminar threat intelligence into Microsoft Sentinel. An Azure Function pulls indicators of compromise and their threat context from Luminar and uploads them through the [Microsoft Sentinel threat intelligence upload API](https://learn.microsoft.com/azure/sentinel/stix-objects-api). The data lands in the `ThreatIntelIndicators` and `ThreatIntelObjects` tables. From there, threat intelligence analytics rules, the Threat intelligence page and your own queries can use it.

**What is ingested**

- **IOCs collection.** URL and IPv4 indicators, with Luminar's confidence score, labels and expiry date.
- **Cyber Feeds collection.** File-hash, IPv4 and domain indicators, the threat actors and targeted organisations around them, and the relationships between them. Indicators are tagged with related malware, actors and campaigns from Luminar reports.
- **Not ingested.** Expired indicators are skipped. Leaked Records are not sent, because that collection describes compromised accounts rather than indicators.

## Before you start

You need:

- A Log Analytics workspace with Microsoft Sentinel enabled.
- A Luminar API account. For access, contact luminar@cognyte.com.
- Permission to register an application in Microsoft Entra ID.
- **Owner**, **User Access Administrator** or **Role Based Access Control Administrator** on the workspace, to assign a role to that application. Contributor is not enough.
- **Contributor** on the resource group where the Function App will be created.

Steps 1 to 3 collect the values that the deployment template asks for in step 5. Note each one as you go:

| Value | Where you get it | Template parameter |
|---|---|---|
| Workspace ID | Step 1 | `WorkspaceID` |
| Workspace resource ID | Step 1 | `AppInsightsWorkspaceResourceID` |
| Directory (tenant) ID | Step 2 | `TenantID` |
| Application (client) ID | Step 2 | `ApplicationID` |
| Client secret value | Step 2 | `ClientSecret` |
| Luminar Account ID, Client ID and Client Secret | Cognyte | `LuminarAPIAccountID`, `LuminarAPIClientID`, `LuminarAPIClientSecret` |

## Step 1. Identify the Microsoft Sentinel workspace

1. In the Azure portal, open **Log Analytics workspaces** and select the workspace that Microsoft Sentinel uses.
2. On the **Overview** page, copy the **Workspace ID**. It is a GUID.
3. Still on the Overview page, select **JSON View** and copy the **Resource ID**. It starts with `/subscriptions/`.

## Step 2. Register a Microsoft Entra application

1. Open **Microsoft Entra ID > App registrations > New registration**.
2. Enter a name, for example `CognyteLuminar-Sentinel`. Keep the default account type, leave the redirect URI empty, and select **Register**.
3. On the application's **Overview** page, copy the **Application (client) ID** and the **Directory (tenant) ID**.
4. Open **Certificates & secrets > Client secrets > New client secret**, choose an expiry date, and select **Add**.
5. Copy the secret's **Value** immediately. It is shown only once. Do not copy the **Secret ID**, which is a different value.

The application needs no API permissions. Leave the **API permissions** page as it is.

Note the secret's expiry date. When it expires, create a new secret and update the `ClientSecret` setting of the Function App.

## Step 3. Grant the application access to the workspace

1. Open the workspace from step 1 and select **Access control (IAM) > Add > Add role assignment**.
2. On the **Role** tab, select **Microsoft Sentinel Contributor**, then **Next**.
3. On the **Members** tab, choose **User, group, or service principal** and select **Select members**.
4. Search for the application **by name**. Applications only appear after you type their name. Select it, then **Select**.
5. Select **Review + assign**.

Assign the role on the workspace itself, or on its resource group or subscription. Do not assign it to the Function App's managed identity. The connector signs in as the application from step 2. A new role assignment can take up to 10 minutes to take effect.

## Step 4. Install the solution from Content hub

1. In Microsoft Sentinel, open **Content management > Content hub**.
2. Search for **Luminar** and select **Luminar Threat Intelligence**.
3. Select **Install**, or **Update** if an earlier version is installed.
4. When it finishes, select **Manage**, then open the **Cognyte Luminar Threat Intelligence** data connector and select **Open connector page**.

## Step 5. Deploy the connector

1. On the connector page, select **Deploy to Azure** under one of the two options:
   - **Flex Consumption plan.** Pay per use. Recommended for most customers.
   - **Premium plan.** Always-on instances, for organisations that need them.
2. Select the subscription, the resource group and the region.
3. Fill in the parameters and select **Review + create**, then **Create**.

| Parameter | What to enter |
|---|---|
| `location` | Keep the default, which is the region of the resource group you selected |
| `FunctionName` | A short name for the Function App, up to 20 letters and digits. Three random characters are added to it. |
| `ApplicationID`, `TenantID` | From step 2 |
| `ClientSecret` | The secret **value** from step 2 |
| `WorkspaceID` | The workspace ID from step 1 |
| `LuminarAPIClientID`, `LuminarAPIAccountID`, `LuminarAPIClientSecret` | Your Luminar API credentials |
| `LuminarInitialFetchDate` | The date to start from on the first run, as `YYYY-MM-DD`. A date in the last few days keeps the first run short. |
| `LuminarBaseURL` | Keep `https://www.cyberluminar.com` unless Cognyte gives you another address |
| `LuminarCollections` | Keep `iocs,cyberfeeds` |
| `DefaultIndicatorValidityDays` | Expiry, in days, for indicators that Luminar publishes without one. Default `90`. |
| `DefaultConfidence` | Confidence, from 0 to 100, for indicators that Luminar publishes without one. Default `50`. Enter `none` to leave it empty. |
| `TLPLevel` | Traffic Light Protocol marking for all uploaded data. Default `green`. |
| `TimeInterval` | How often the connector runs. Keep `Every 60 min`. Luminar publishes IOCs in bursts every few hours, and hourly runs keep Microsoft Sentinel up to date. |
| `AppInsightsWorkspaceResourceID` | The workspace resource ID from step 1. The connector's logs are stored there. |
| `storageAccountType`, `functionAppPlanSku` | Premium plan only. Keep the defaults. |

## Step 6. Confirm that data is arriving

The connector runs at the start of each hour. To run it straight away, open the Function App, then **Functions > CognyteLuminar > Code + Test > Test/Run**, and select **Run**.

After a successful run, data appears within about 15 minutes. Run these queries in Microsoft Sentinel **Logs** or Defender **Advanced hunting**:

```kusto
// Luminar indicators by type
ThreatIntelIndicators
| where SourceSystem == 'Cognyte Luminar'
| summarize arg_max(TimeGenerated, *) by Id
| where IsDeleted == false
| summarize Indicators = count() by ObservableKey
```

```kusto
// Sign-ins from IP addresses flagged by Luminar
let LuminarIPs = ThreatIntelIndicators
    | where SourceSystem == 'Cognyte Luminar' and ObservableKey == 'ipv4-addr:value'
    | summarize arg_max(TimeGenerated, *) by Id
    | where IsDeleted == false and ValidUntil > now()
    | project IPAddress = ObservableValue, Confidence, Tags;
SigninLogs
| join kind=inner LuminarIPs on IPAddress
```

```kusto
// Threat actors and the organisations they target
let Actors = ThreatIntelObjects
    | where SourceSystem == 'Cognyte Luminar' and StixType == 'threat-actor'
    | extend ActorId = tostring(Data.id), Actor = tostring(Data.name);
let Links = ThreatIntelObjects
    | where SourceSystem == 'Cognyte Luminar' and StixType == 'relationship'
    | extend Src = tostring(Data.source_ref), Tgt = tostring(Data.target_ref), Relationship = tostring(Data.relationship_type);
let Targets = ThreatIntelObjects
    | where SourceSystem == 'Cognyte Luminar' and StixType == 'identity'
    | extend TargetId = tostring(Data.id), Target = tostring(Data.name);
Actors
| join kind=inner Links on $left.ActorId == $right.Src
| join kind=inner Targets on $left.Tgt == $right.TargetId
| project Actor, Relationship, Target
```

The data connector page also shows the connection status and when data was last received.

## Troubleshooting

The connector writes its log to the Function App. Open **Monitor** or **Log stream** to read it.

| Message in the log | Cause | Fix |
|---|---|---|
| `AADSTS700016: Application with identifier ... was not found` | `ApplicationID` or `TenantID` is wrong | Copy both again from the application's Overview page |
| `AADSTS7000215: Invalid client secret` | The Secret ID was entered instead of the Value, or the secret expired | Create a new secret and enter its **Value** in the `ClientSecret` setting |
| `Upload API HTTP 401 ... does not have required permission ... on the workspace` | The application has no Microsoft Sentinel Contributor role on this workspace | Repeat step 3 on the workspace whose ID is in `WorkspaceID`, then wait 10 minutes |
| `Upload API HTTP 404` | `WorkspaceID` is not the workspace ID | Enter the Workspace ID GUID from the workspace Overview page |
| `Failed to obtain Luminar access token` or `Luminar ... HTTP 401` | Luminar credentials or address are wrong | Check the three Luminar settings and `LuminarBaseURL` |
| `Configuration error: Missing required app setting` | A setting is empty | Add the named setting under the Function App's **Settings > Environment variables** |
| `time budget reached` | A large backlog is being processed | No action needed. The next run continues from where this one stopped. |

To change a setting after deployment, open the Function App, then **Settings > Environment variables**. Saving restarts the app and the new value takes effect on the next run.

## Upgrading from version 3.0.x

Version 3.0.x used the retired Microsoft Graph `tiIndicators` API and wrote to the legacy `ThreatIntelligenceIndicator` table, which no longer receives data. To upgrade:

1. Update the solution in Content hub, as in step 4.
2. Assign the **Microsoft Sentinel Contributor** role to your existing application, as in step 3. The old Microsoft Graph permission, `ThreatIndicators.ReadWrite.OwnedBy`, is no longer used and can be removed.
3. Deploy the connector again, as in step 5, with the new `WorkspaceID` parameter. Use the same resource group and Function App name to replace the existing app.
4. Move any queries, workbooks or rules that read `ThreatIntelligenceIndicator` to `ThreatIntelIndicators` and `ThreatIntelObjects`. Microsoft's [migration guidance](https://learn.microsoft.com/azure/sentinel/work-with-stix-objects-indicators) shows how.

Leaked credentials are no longer sent as indicators, because those accounts belong to victims, not attackers. The connector continues from the point the previous version reached.

## Support

Cognyte Luminar: luminar@cognyte.com, https://www.cognyte.com/contact/

See [ReleaseNotes.md](ReleaseNotes.md) for the version history.
