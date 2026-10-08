# Databricks audit logs via Amazon S3: connector setup

## How it works

1. Databricks writes audit events as JSON lines to `s3://<bucket>/<prefix>/workspaceId=<id>/date=<yyyy-mm-dd>/auditlogs_<id>.json`. Account-level events use `workspaceId=0`.
2. S3 sends an ObjectCreated notification for each new object to an SQS queue.
3. Microsoft Sentinel assumes an IAM role in your account through OpenID Connect (no stored keys), reads the queue, fetches each object and pushes the rows through a data collection rule into `DatabricksAudit_CL`.

## Prerequisites

- Databricks account on the Premium or Enterprise tier with [audit log delivery](https://docs.databricks.com/aws/en/admin/account-settings/audit-logs) configured: `log_type` AUDIT_LOGS, `output_format` JSON, a `delivery_path_prefix` with no leading or trailing slash.
- AWS permissions to create an IAM role and OIDC provider, an SQS queue, and an S3 bucket notification.
- Microsoft Sentinel Contributor on the workspace and Contributor on its resource group.

## AWS setup with CloudFormation

### Template 1: OIDCWebIdProvider.json

Creates the OpenID Connect provider for Microsoft Sentinel (`sts.windows.net/33e01921-4d64-4f8c-a055-5bdaffd5e33d/`, audience `api://1462b192-27f7-4cb9-8523-0f4ecb54b47e`). Deploy it once per AWS account. If another Microsoft Sentinel AWS connector (CloudTrail, GuardDuty, VPC Flow Logs, Security Hub) already created it, skip this template.

### Template 2: DatabricksAuditLogsResources.json

| Parameter | Value |
|---|---|
| `SentinelWorkspaceId` | The Workspace ID shown on the connector page |
| `BucketName` | The bucket Databricks delivers to |
| `DeliveryPathPrefix` | The Databricks `delivery_path_prefix`, no slashes |
| `AwsRoleName` | Must start with `OIDC_` (default provided) |
| `KmsKeyArn` | Only if the bucket uses SSE-KMS |
| `CreateNewBucket` | `false` when the bucket exists (usual); `true` creates it with the notification |

Outputs: **SentinelRoleArn** and **SentinelSQSQueueURL** for the collector, **SentinelSQSQueueArn** and **NotificationPrefix** for the next step.

### S3 event notification on an existing bucket

CloudFormation cannot add a notification to a bucket it did not create. In the S3 console open the bucket, Properties, Event notifications, Create event notification: prefix `<DeliveryPathPrefix>/`, event type All object create events, destination SQS queue, the queue from the stack outputs. Or with the CLI:

```bash
aws s3api put-bucket-notification-configuration --bucket <bucket> --notification-configuration '{
  "QueueConfigurations": [{
    "Id": "databricks-audit-to-sentinel",
    "QueueArn": "<SentinelSQSQueueArn>",
    "Events": ["s3:ObjectCreated:*"],
    "Filter": {"Key": {"FilterRules": [{"Name": "prefix", "Value": "<DeliveryPathPrefix>/"}]}}
  }]
}'
```

If the bucket already has notifications, merge rather than replace: `get-bucket-notification-configuration` first and add the new entry.

### Trust policy rules

The role the collector uses must satisfy all of these or the connector shows `AssumeRole` or `AccessDenied` in `SentinelHealth`:

- Role name starts with `OIDC_`.
- Trust principal is the OIDC provider `sts.windows.net/33e01921-4d64-4f8c-a055-5bdaffd5e33d/` in your account.
- Conditions: `sts.windows.net/33e01921-4d64-4f8c-a055-5bdaffd5e33d/:aud` equals `api://1462b192-27f7-4cb9-8523-0f4ecb54b47e` and `sts:RoleSessionName` equals `MicrosoftSentinel_<Workspace ID>`.
- Permissions: receive and delete on the queue; `s3:GetObject` on `<bucket>/<prefix>/*`; `kms:Decrypt` on the key if SSE-KMS.

## Microsoft Sentinel

Install the solution from the content hub, open **Databricks Audit Logs via Amazon S3** in Data connectors, click **Add new collector**, paste the Role ARN and Queue URL, click Connect.

## Check it worked

```kusto
SentinelHealth
| where SentinelResourceKind == "AmazonWebServicesS3"
| summarize arg_max(TimeGenerated, *) by SentinelResourceName
| project TimeGenerated, SentinelResourceName, Status, Description
```

```kusto
DatabricksAudit_CL
| take 10
```

Queue depth and dead-letter queue depth should return to zero after each poll. A message in the dead-letter queue names an object the role could not read: usually a prefix mismatch or a missing `kms:Decrypt`.

## Known limits

- Objects already in the bucket when the collector is created are not ingested. To load history, copy them to a second prefix with its own notification and collector.
- `TimeGenerated` is set to the event time only when the event is under 47 hours old at ingestion; `EventTime` always carries the Databricks timestamp.
- Databricks delivers plain JSON. If your pipeline gzips the objects, change `dataFormat.IsCompressed` to `true` and `compressType` to `Gzip` in the poller configuration.
