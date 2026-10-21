# Databricks audit logs via Amazon S3: setup guide

This connector ingests the account and workspace audit logs that Databricks on AWS delivers to an Amazon S3 bucket into the `DatabricksAudit_CL` table. Microsoft Sentinel's S3 poller reads each new file. Nothing is hosted in your environment and no AWS access keys are used.

## How it works

1. Databricks writes audit events as JSON lines to `s3://<bucket>/<prefix>/workspaceId=<id>/date=<yyyy-mm-dd>/auditlogs_<id>.json`. Account-level events use `workspaceId=0`. Without a delivery path prefix the `workspaceId=` folders are at the top of the bucket.
2. S3 sends an `ObjectCreated` message for each new file under the prefix (or under `workspaceId=` when there is no prefix) to an SQS queue.
3. The Microsoft Sentinel S3 poller signs in to AWS with Microsoft Sentinel's own Entra ID identity and assumes an IAM role in your account through the IAM OpenID Connect provider.
4. It reads messages from the queue.
5. It downloads each file the messages name.
6. It sends the lines to the data collection endpoint.
7. The data collection rule reshapes each line and writes it to `DatabricksAudit_CL`.
8. It deletes the message. A file that keeps failing is retried, then moved to the dead-letter queue. Status is written to `SentinelHealth`.

## Steps

| Step | Where | Check before the next step |
|---|---|---|
| 1. Prerequisites and values | Databricks, AWS, Azure | `workspaceId=` folders exist in the bucket, under the prefix if there is one |
| 2. Install the solution | Microsoft Sentinel content hub | Connector listed in Data connectors; Workspace ID noted |
| 3. Role and queues | AWS CloudFormation console | Stack outputs: Role ARN, Queue URL, Queue ARN |
| 4. S3 event notification | S3 console | An `s3:TestEvent` message in the queue |
| 5. Add the collector | Connector page | Collector listed with your Role ARN and Queue URL |
| 6. Validate | Microsoft Sentinel Logs | `SentinelHealth` Success; rows in `DatabricksAudit_CL` |

If a check fails, fix it there. Later steps only fail with less specific errors.

## Step 1. Prerequisites and values

- **Databricks**: Premium or Enterprise tier, with [audit log delivery](https://docs.databricks.com/aws/en/admin/account-settings/audit-logs) to S3 configured: `log_type` AUDIT_LOGS, `output_format` JSON, and optionally a `delivery_path_prefix`.
- **AWS**: rights in the account that owns the bucket to deploy CloudFormation stacks that create IAM resources, and to add an S3 event notification.
- **Azure**: Microsoft Sentinel Contributor on the workspace and Contributor on its resource group.

| # | Value | Where to find it | Example |
|---|---|---|---|
| 1 | Workspace ID | Connector page (step 2), or the Log Analytics workspace Overview | `1a2b3c4d-1234-5678-9abc-def012345678` |
| 2 | Bucket name and region | S3 console | `acme-databricks-logs`, `us-east-1` |
| 3 | Delivery path prefix | The folder that holds the `workspaceId=` folders, no slashes. Empty if they are at the top of the bucket | `audit-logs`, or empty |
| 4 | KMS key ARN | Only if the bucket uses SSE-KMS | `arn:aws:kms:us-east-1:123456789012:key/...` |
| 5 | Role ARN | Stack output `SentinelRoleArn` (step 3) | `arn:aws:iam::123456789012:role/OIDC_MicrosoftSentinelDatabricksAudit` |
| 6 | Queue URL | Stack output `SentinelSQSQueueURL` (step 3) | `https://sqs.us-east-1.amazonaws.com/123456789012/MicrosoftSentinelDatabricksAuditSqs` |
| 7 | Queue ARN | Stack output `SentinelSQSQueueArn` (step 3) | `arn:aws:sqs:us-east-1:123456789012:MicrosoftSentinelDatabricksAuditSqs` |

The Workspace ID, tenant ID and subscription ID are all GUIDs. Only the Workspace ID is used here. Fixed values, the same in every installation: OpenID Connect provider `https://sts.windows.net/33e01921-4d64-4f8c-a055-5bdaffd5e33d/`, audience `api://1462b192-27f7-4cb9-8523-0f4ecb54b47e`.

## Step 2. Install the solution

1. Microsoft Sentinel, **Content hub**, search "Databricks", select the solution, **Install**.
2. Turn on health monitoring: Microsoft Sentinel settings, **Auditing and health monitoring**, **Enable**. Without it `SentinelHealth` stays empty.
3. Microsoft Sentinel, **Configuration**, **Data connectors**, search "Databricks", select **Databricks Audit Logs via Amazon S3 (via Codeless Connector Framework)**, **Open connector page**. Copy the **Workspace ID** (value 1).

## Step 3. Role and queues (AWS CloudFormation console)

Work in the bucket's region. The templates are in `Data Connectors/CloudFormationTemplates/`.

### 3a. Check for an existing identity provider

Open **IAM**, **Identity providers**. If `sts.windows.net/33e01921-4d64-4f8c-a055-5bdaffd5e33d/` is listed, another Microsoft Sentinel AWS connector already created it: check that its **Audiences** include `api://1462b192-27f7-4cb9-8523-0f4ecb54b47e` (add it if not) and skip 3b.

### 3b. Stack 1: OIDCWebIdProvider.json

1. **CloudFormation**, **Create stack**, **With new resources (standard)**, **Choose an existing template**, **Upload a template file**, `OIDCWebIdProvider.json`, **Next**.
2. Stack name `MicrosoftSentinel-OIDC`. The template has no parameters. **Next**, **Next**, **Submit**.
3. Wait for **CREATE_COMPLETE**.

### 3c. Stack 2: DatabricksAuditLogsResources.json

1. **Create stack**, **With new resources (standard)**, **Choose an existing template**, **Upload a template file**, `DatabricksAuditLogsResources.json`, **Next**.
2. Stack name `MicrosoftSentinel-DatabricksAudit`.

Fill in the first parameter group, **Enter your values**:

| Field | Enter |
|---|---|
| Microsoft Sentinel Workspace ID | Value 1 |
| Databricks S3 bucket name | Value 2, the name only (no `s3://`) |
| Databricks delivery path prefix (empty if none) | Value 3, no slashes; leave it empty if there is no prefix |
| KMS key ARN (SSE-KMS buckets only) | Value 4, or empty |

Leave the second group, **Keep the defaults**, as it is: IAM role name `OIDC_MicrosoftSentinelDatabricksAudit` (it must start with `OIDC_`), SQS queue name `MicrosoftSentinelDatabricksAuditSqs`, Create a new bucket `false`. The form rejects a Workspace ID that is not a GUID, a bucket written as `s3://...` and a prefix with a leading or trailing slash.

Then:

1. **Next**, **Next**. On **Review**, tick **I acknowledge that AWS CloudFormation might create IAM resources with custom names**, **Submit**.
2. Wait for **CREATE_COMPLETE**. On **ROLLBACK_COMPLETE**, the first **CREATE_FAILED** event on the **Events** tab gives the reason; delete the failed stack before trying again.
3. From the **Outputs** tab, record **SentinelRoleArn** (value 5), **SentinelSQSQueueURL** (value 6), **SentinelSQSQueueArn** (value 7) and **NotificationPrefix**.

| Event message | Cause | Fix |
|---|---|---|
| Stack 1: `already exists` | The identity provider exists | Delete the failed stack and skip 3b |
| Stack 2: `Invalid principal in policy` | The identity provider does not exist | Deploy stack 1, then stack 2 again |
| Stack 2: role or queue `already exists` | Names used by another stack | Delete the old stack, or change the names in the second group |
| `Requires capabilities: [CAPABILITY_NAMED_IAM]` | Acknowledgement not ticked | Create the stack again and tick it |

## Step 4. S3 event notification

CloudFormation cannot add a notification to a bucket it did not create.

1. S3, the bucket, **Properties**, **Event notifications**, **Create event notification**.
2. Name `databricks-audit-to-sentinel`. Prefix: the **NotificationPrefix** output, exactly as shown: value 3 with a trailing slash (for example `audit-logs/`), or `workspaceId%3D` if value 3 is empty. Type `%3D`, not `=`: S3 needs special characters in filter values URL-encoded, and a prefix written `workspaceId=` matches no file, so S3 sends nothing. The same applies to any character in value 3 other than letters, digits and `- _ . /`. Suffix: `.json`, or empty. Event types: **All object create events**.
3. Destination **SQS queue**, the queue from step 3 (or value 7). **Save changes**.

Check: in SQS, open the queue, **Send and receive messages**, **Poll for messages**. A message containing `s3:TestEvent` is there. S3 sends it whatever the prefix, so it shows the queue accepts messages from the bucket, not that the prefix matches the files. Polling is safe now; do not poll the queue in the console after step 5, because it hides messages from the collector and counts toward the five reads before a message moves to the dead-letter queue.

- **Unable to validate the following destination configurations**: the queue policy does not allow this bucket. The bucket name in stack 2 does not match.
- **Configurations overlap**: the bucket already sends object-create events for this prefix to another destination. S3 allows one destination per overlapping prefix and event type.

With the AWS CLI instead of the console (merge with any existing notifications; read them first with `get-bucket-notification-configuration`):

```bash
aws s3api put-bucket-notification-configuration --bucket <bucket> --notification-configuration '{
  "QueueConfigurations": [{
    "Id": "databricks-audit-to-sentinel",
    "QueueArn": "<SentinelSQSQueueArn>",
    "Events": ["s3:ObjectCreated:*"],
    "Filter": {"Key": {"FilterRules": [{"Name": "prefix", "Value": "<NotificationPrefix>"}, {"Name": "suffix", "Value": ".json"}]}}
  }]
}'
```

## Step 5. Add the collector

On the connector page, **Add new collector**. **Role ARN**: value 5. **Queue URL**: value 6 (the URL, not the ARN). **Connect**. The grid on the connector page lists the collector.

Files already in the bucket before step 4 are not read.

## Step 6. Validate

Rows arrive 5 to 15 minutes after the next Databricks file lands. Then run these in Microsoft Sentinel **Logs**:

```kusto
// Latest collector status: expect Success
SentinelHealth
| where TimeGenerated > ago(1d)
| where SentinelResourceKind == "AmazonWebServicesS3"
| summarize arg_max(TimeGenerated, Status, Description) by SentinelResourceName, OperationName
```

```kusto
// Polling failures: expect no rows
SentinelHealth
| where TimeGenerated > ago(1d)
| where SentinelResourceKind == "AmazonWebServicesS3" and OperationName == "Data fetch failure summary"
| mv-expand F = ExtendedProperties["FailureSummary"]
| project TimeGenerated, SentinelResourceName, StatusCode = tostring(F["StatusCode"]), StatusMessage = tostring(F["StatusMessage"])
```

```kusto
// Rows and field mapping: Rows > 0, the other counts 0
DatabricksAudit_CL
| where TimeGenerated > ago(1d)
| summarize Rows = count(), NoEventTime = countif(isnull(EventTime)), NoAction = countif(isempty(ActionName)), NoRequestId = countif(isempty(RequestId)), LastIngested = max(ingestion_time())
```

In AWS, the queue's **Monitoring** tab should show messages returning to 0, and the `-dlq` queue should stay at 0.

## Without CloudFormation

Create the same resources by hand, in the bucket's region and in this order. Replace `<account-id>`, `<region>`, `<workspace-id>`, `<bucket>` and `<prefix>` (no slashes) before pasting. If there is no prefix, use `arn:aws:s3:::<bucket>/workspaceId=*` for `s3:GetObject` and `workspaceId%3D` as the notification prefix.

1. **Identity provider** (skip if it exists, see 3a): IAM, **Identity providers**, **Add provider**, **OpenID Connect**, URL `https://sts.windows.net/33e01921-4d64-4f8c-a055-5bdaffd5e33d/`, audience `api://1462b192-27f7-4cb9-8523-0f4ecb54b47e`.
2. **Role**: IAM, **Roles**, **Create role**, **Custom trust policy**:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::<account-id>:oidc-provider/sts.windows.net/33e01921-4d64-4f8c-a055-5bdaffd5e33d/" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": { "StringEquals": {
      "sts.windows.net/33e01921-4d64-4f8c-a055-5bdaffd5e33d/:aud": "api://1462b192-27f7-4cb9-8523-0f4ecb54b47e",
      "sts:RoleSessionName": "MicrosoftSentinel_<workspace-id>"
    } }
  }]
}
```

   Name it `OIDC_MicrosoftSentinelDatabricksAudit` (it must start with `OIDC_`), then add this inline policy. If the bucket uses SSE-KMS, add a statement allowing `kms:Decrypt` on the key.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow",
      "Action": ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:ChangeMessageVisibility", "sqs:GetQueueAttributes", "sqs:GetQueueUrl"],
      "Resource": "arn:aws:sqs:<region>:<account-id>:MicrosoftSentinelDatabricksAuditSqs" },
    { "Effect": "Allow", "Action": "s3:GetObject", "Resource": "arn:aws:s3:::<bucket>/<prefix>/*" },
    { "Effect": "Allow", "Action": ["s3:ListBucket", "s3:GetBucketLocation"], "Resource": "arn:aws:s3:::<bucket>" }
  ]
}
```

3. **Dead-letter queue**: SQS, **Create queue**, Standard, `MicrosoftSentinelDatabricksAuditSqs-dlq`, retention 14 days.
4. **Queue**: Standard, `MicrosoftSentinelDatabricksAuditSqs`, visibility timeout 10 minutes, retention 4 days, dead-letter queue the `-dlq` queue with maximum receives 5, and this access policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Principal": { "Service": "s3.amazonaws.com" }, "Action": "sqs:SendMessage",
      "Resource": "arn:aws:sqs:<region>:<account-id>:MicrosoftSentinelDatabricksAuditSqs",
      "Condition": { "ArnLike": { "aws:SourceArn": "arn:aws:s3:*:*:<bucket>" }, "StringEquals": { "aws:SourceAccount": "<account-id>" } } },
    { "Effect": "Allow", "Principal": { "AWS": "arn:aws:iam::<account-id>:role/OIDC_MicrosoftSentinelDatabricksAudit" },
      "Action": ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:ChangeMessageVisibility", "sqs:GetQueueUrl"],
      "Resource": "arn:aws:sqs:<region>:<account-id>:MicrosoftSentinelDatabricksAuditSqs" }
  ]
}
```

5. Continue with step 4.

## Troubleshooting

| What you see | Cause | Fix |
|---|---|---|
| `SentinelHealth` mentions `AssumeRoleWithWebIdentity` or `AccessDenied` | Trust policy does not match | Role name starts with `OIDC_`; `sts:RoleSessionName` is `MicrosoftSentinel_` plus the Workspace ID (not the tenant or subscription ID); provider and audience as above |
| `InvalidIdentityToken` | Identity provider missing or without the audience | Step 3a |
| `NonExistentQueue` | Wrong Queue URL on the collector | Delete the collector and add it again with the stack output |
| `s3:GetObject` `AccessDenied` | Role cannot read the file | The stack's delivery prefix must be the folder holding the `workspaceId=` folders, or empty if they are at the top of the bucket |
| `kms:Decrypt` | Bucket uses SSE-KMS | Update stack 2 with the KMS key ARN |
| Queue stays at 0 | Notification missing or prefix wrong | Use the stack output `NotificationPrefix`: the folder holding the `workspaceId=` folders with a trailing slash, or `workspaceId%3D` if they are at the top of the bucket |
| Queue stays at 0 while Databricks writes files, prefix `workspaceId=` | S3 needs special characters in filter values URL-encoded; an unencoded `=` matches no file | Edit the notification: prefix `workspaceId%3D` |
| Messages deleted, no rows after 30 minutes | Rows rejected by the data collection rule | Enable diagnostic settings on `DatabricksAuditLogs-DCR` and check `DCRLogErrors` |
| Messages in the `-dlq` queue | A file failed five reads | Poll the `-dlq` queue to see the file; fix the cause, then **Start DLQ redrive** |

## Operations

- **Daily check**: the first validation query above; save it as a scheduled analytics rule if you want an alert.
- **Collector changes**: a collector cannot be edited. To change the Role ARN or Queue URL, delete it on the connector page and add it again.
- **Another bucket or Databricks account**: deploy `DatabricksAuditLogsResources.json` again with a different stack, role and queue name, add a notification on that bucket, and add a second collector.
- **Loading history**: only files created after the notification exists are read. Upload older files again under the prefix (or `workspaceId=`) with new names to ingest them.
- **Removal**: delete the collector, then the solution in the content hub, the S3 event notification, and the `MicrosoftSentinel-DatabricksAudit` stack. Keep the identity provider if other Microsoft Sentinel AWS connectors use it.

## Known limits

- `TimeGenerated` is the event time only when the event is under 47 hours old at ingestion; `EventTime` always carries the Databricks timestamp.
- SQS delivers at least once, so a few duplicate rows are possible. Deduplicate on `RequestId`.
- Databricks delivers plain JSON. If your pipeline gzips the objects, change `dataFormat.IsCompressed` to `true` and `compressType` to `Gzip` in the poller configuration.
