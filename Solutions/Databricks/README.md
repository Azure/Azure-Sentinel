# Databricks audit logs for Microsoft Sentinel

Ingests the account and workspace audit logs that Databricks on AWS delivers to an Amazon S3 bucket into the custom table `DatabricksAudit_CL`, using the Codeless Connector Framework and Microsoft Sentinel's Amazon S3 poller. Nothing runs in your subscription; no AWS keys are stored.

Azure Databricks is not covered by this solution. It writes to Log Analytics through diagnostic settings.

## What is in the solution

| Item | Purpose |
|---|---|
| Data connector `DatabricksAuditLogs_CCF` | Gallery tile, "Add new collector" form, S3 poller, data collection rule with transform, and the `DatabricksAudit_CL` table |
| `Data Connectors/CloudFormationTemplates/` | Two templates for the AWS side: the OpenID Connect provider for Microsoft Sentinel, and the IAM role, SQS queue, dead-letter queue and queue policy |
| Analytic rules (4) | Failed logins from one IP, admin privilege granted, IP access list changed, long-lived token created |
| Hunting queries (3) | Secret reads outside business hours, notebook exports and result downloads, new source IP per user |

## Setup

See `Data Connectors/README.md`. In short:

1. Databricks: enable audit log delivery to S3 (Premium or Enterprise tier), output format JSON, with a delivery path prefix.
2. AWS: deploy `OIDCWebIdProvider.json` (once per account) and `DatabricksAuditLogsResources.json` with your Workspace ID, bucket and prefix. Add an ObjectCreated notification on the bucket to the queue, filtered on the prefix, if the bucket already exists.
3. Microsoft Sentinel: install the solution, open the connector page, click **Add new collector**, paste the Role ARN and Queue URL.

Rows appear within 5 to 15 minutes of the next Databricks file landing in S3. Objects that were already in the bucket are not read.

## Table

`DatabricksAudit_CL` has one row per audit event. `EventTime` is the Databricks timestamp. `TimeGenerated` equals `EventTime` when the event is less than 47 hours old at ingestion, otherwise the ingestion time (Log Analytics does not accept older `TimeGenerated` values on custom tables). Query on `EventTime` for historical analysis.

| Column | From |
|---|---|
| ServiceName, ActionName | `serviceName`, `actionName` |
| UserEmail, UserSubjectName, UserIdentity | `userIdentity.email`, `userIdentity.subjectName`, `userIdentity` |
| SourceIPAddress, UserAgent, SessionId, RequestId | same names |
| WorkspaceId, OrgId, AccountId, ShardName, AuditLevel, SchemaVersion | `workspaceId` (or `orgId` when empty), `orgId`, `accountId`, `shardName`, `auditLevel`, `version` |
| RequestParams, ResponseStatusCode, ResponseErrorMessage, ResponseResult | `requestParams`, `response.statusCode`, `response.errorMessage`, `response.result` |

## Validation

The table schema, transform and the AWS trust pattern were verified against a live Microsoft Sentinel workspace and AWS account with Databricks-shaped data (410 events, historical and live) on 7 October 2026, using the companion package at the author's repository, which also contains an Azure Function alternative, pre-flight and diagnostics scripts, and an automated test harness.

## Support

Community supported. Open an issue in this repository and mention `Solutions/Databricks`. Author: David Broggy, LevelBlue (david.broggy@levelblue.com).
