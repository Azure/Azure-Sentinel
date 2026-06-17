# AWS Config Microsoft Sentinel Connector

## Introduction

The AWS Config Microsoft Sentinel connector ingests AWS Config configuration item notifications into Microsoft Sentinel by using the Codeless Connector Framework (CCF).

The connector uses an AWS-hosted HTTPS API that is deployed with the included AWS CloudFormation template. Microsoft Sentinel polls this API over HTTPS and authenticates by using an API key in the `x-api-key` header.

The connector stores data in the following custom table:

```text
AWSConfig_CL
```

## Configuration process

The CloudFormation template can be used to automatically configure the required AWS resources.

At a high level, the template does the following:

1. Creates a DynamoDB table to buffer AWS Config notification events.
2. Creates a new SNS topic for AWS Config notifications, or uses an existing SNS topic.
3. Creates an ingest Lambda function that receives AWS Config notifications from SNS.
4. Stores normalized AWS Config items in DynamoDB.
5. Creates a query Lambda function that returns events by time window.
6. Creates an Amazon API Gateway REST API with a `GET /logs` endpoint.
7. Creates an API Gateway API key and usage plan.
8. Creates CloudWatch log groups for the Lambda functions.

When the deployment is complete, the CloudFormation stack outputs the API endpoint that must be entered in the Microsoft Sentinel data connector page.

## Template prerequisites

You must have the following before using the template:

- AWS CLI installed and configured.
- Permissions to deploy CloudFormation stacks.
- Permissions to create or update IAM roles, Lambda functions, DynamoDB tables, SNS topics or subscriptions, API Gateway resources, and CloudWatch log groups.
- AWS Config enabled in the AWS account and region that you want to monitor.
- A Microsoft Sentinel workspace where the AWS Config data connector has been deployed.

Run the following command to confirm that the AWS CLI is configured:

```bash
aws sts get-caller-identity
```

## Using the template

Download the CloudFormation template to your computer:

```text
template_1_AWS_Config_v2.yaml
```

Generate an API key value. The same value must be used later in the Microsoft Sentinel connector page.

```bash
API_KEY_VALUE="$(openssl rand -hex 32)"
AWS_ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
```

Deploy the CloudFormation stack:

```bash
aws cloudformation deploy \
  --template-file template_1_AWS_Config_v2.yaml \
  --stack-name sentinel-aws-config-ccf \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    AwsAccountId="$AWS_ACCOUNT_ID" \
    ApiKeyValue="$API_KEY_VALUE" \
    CreateSnsTopic="true"
```

> IMPORTANT: The deployment requires `CAPABILITY_NAMED_IAM` because the template creates a named IAM role for the Lambda functions.

## Configure AWS Config notifications

After the stack deployment completes, retrieve the SNS topic ARN:

```bash
aws cloudformation describe-stacks \
  --stack-name sentinel-aws-config-ccf \
  --query "Stacks[0].Outputs[?OutputKey=='ConfigNotificationTopicArn'].OutputValue" \
  --output text
```

Configure AWS Config to publish notifications to this SNS topic.

If AWS Config already publishes notifications to an existing SNS topic, use the existing SNS topic deployment option below instead.

## Using an existing SNS topic

If AWS Config already publishes notifications to an existing SNS topic, deploy the template with `CreateSnsTopic=false` and provide the topic ARN:

```bash
aws cloudformation deploy \
  --template-file template_1_AWS_Config_v2.yaml \
  --stack-name sentinel-aws-config-ccf \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    AwsAccountId="$AWS_ACCOUNT_ID" \
    ApiKeyValue="$API_KEY_VALUE" \
    CreateSnsTopic="false" \
    ExistingSnsTopicArn="arn:aws:sns:<region>:<account-id>:<topic-name>"
```

The template subscribes the ingest Lambda function to the existing SNS topic.

## Get the API endpoint

Retrieve the API endpoint from the CloudFormation stack outputs:

```bash
API_ENDPOINT="$(aws cloudformation describe-stacks \
  --stack-name sentinel-aws-config-ccf \
  --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" \
  --output text)"

echo "$API_ENDPOINT"
```

The output already includes the `/logs` path.

## Test the API endpoint

Use a recent time window to test the endpoint before configuring Microsoft Sentinel:

```bash
START_TIME="$(date -u -d '10 minutes ago' '+%Y-%m-%dT%H:%M:%SZ')"
END_TIME="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

curl -sS \
  -H "x-api-key: $API_KEY_VALUE" \
  -H "Accept: application/json" \
  "$API_ENDPOINT?startTime=$START_TIME&endTime=$END_TIME"
```

Expected response format:

```json
{
  "events": [
    {
      "CaptureTime": "2026-06-09T12:00:00Z",
      "AwsAccountId": "123456789012",
      "AwsRegion": "eu-west-2",
      "ResourceType": "AWS::EC2::Instance",
      "ResourceId": "i-0123456789abcdef0",
      "ConfigItemStatus": "OK",
      "MessageType": "ConfigurationItemChangeNotification"
    }
  ],
  "nextToken": "optional-next-page-token"
}
```

The Microsoft Sentinel connector expects:

| Setting | Value |
|---|---|
| HTTP method | `GET` |
| API key header | `x-api-key` |
| Start time query parameter | `startTime` |
| End time query parameter | `endTime` |
| Paging query parameter | `nextToken` |
| Events JSON path | `$.events` |

## Configure Microsoft Sentinel

In the Azure portal, open the Microsoft Sentinel data connector page.

```text
Microsoft Sentinel
-> Data connectors
-> AWS Config
-> Open connector page
```

Enter the following values:

```text
API endpoint: <ApiEndpoint CloudFormation output>
API key:      <API_KEY_VALUE used during CloudFormation deployment>
```

Then select **Connect**.

## Validate data in Microsoft Sentinel

Allow several polling intervals for data to appear, then run:

```kql
AWSConfig_CL
| sort by TimeGenerated desc
| take 20
```

To check ingestion health:

```kql
AWSConfig_CL
| summarize Count=count(), LastEvent=max(TimeGenerated), LastIngestion=max(ingestion_time())
```

To summarize by AWS account, region, and resource type:

```kql
AWSConfig_CL
| summarize Count=count() by AwsAccountId, AwsRegion, ResourceType
| sort by Count desc
```

## Troubleshooting

### No data appears in Microsoft Sentinel

Check the following:

1. AWS Config is enabled in the target account and region.
2. AWS Config is publishing notifications to the SNS topic used by the stack.
3. The ingest Lambda function has recent invocations in CloudWatch Logs.
4. The DynamoDB table contains recent items.
5. The API endpoint returns `HTTP 200` when called with the correct `x-api-key`.
6. The API response contains an `events` array.
7. `CaptureTime` values are inside the requested time window.
8. The API endpoint configured in Microsoft Sentinel exactly matches the `ApiEndpoint` stack output.

### API returns 403

A `403` response usually means the API key is missing or incorrect.

Confirm that the Sentinel connector uses the same value provided to the CloudFormation `ApiKeyValue` parameter, and confirm that the header name is:

```text
x-api-key
```

### API returns 400

A `400` response usually means `startTime` or `endTime` is missing or malformed.

Use UTC ISO 8601 format:

```text
yyyy-MM-ddTHH:mm:ssZ
```

Example:

```text
2026-06-09T12:00:00Z
```

### SNS topic exists but no events arrive

If `CreateSnsTopic=true`, the template creates the SNS topic and subscribes the ingest Lambda function. AWS Config must still be configured to publish notifications to that topic.

If `CreateSnsTopic=false`, confirm that AWS Config is already publishing to the existing SNS topic provided in `ExistingSnsTopicArn`.

## Advanced usage

The CloudFormation template supports the following parameters:

| Parameter | Description |
|---|---|
| `AwsAccountId` | The 12-digit AWS account ID. The template validates that it matches the deployment account. |
| `DynamoDBTableName` | Name of the DynamoDB table used to buffer AWS Config events. |
| `LambdaExecutionRoleName` | Name of the IAM role shared by the ingest and query Lambda functions. |
| `IngestFunctionName` | Name of the Lambda function that receives SNS notifications. |
| `QueryFunctionName` | Name of the Lambda function used by API Gateway. |
| `CreateSnsTopic` | Set to `true` to create a new SNS topic, or `false` to use an existing SNS topic. |
| `SnsTopicName` | Name of the SNS topic to create when `CreateSnsTopic=true`. |
| `ExistingSnsTopicArn` | ARN of an existing SNS topic when `CreateSnsTopic=false`. |
| `ApiName` | Name of the API Gateway REST API. |
| `ApiStageName` | API Gateway stage name. |
| `ApiKeyName` | Name of the API Gateway API key. |
| `ApiKeyValue` | API key value sent by Microsoft Sentinel in the `x-api-key` header. |
| `ThrottleRateLimit` | API Gateway steady-state request rate limit. |
| `ThrottleBurstLimit` | API Gateway burst request limit. |
| `DailyQuota` | API Gateway daily request quota. |
| `TtlDays` | Number of days to retain buffered events in DynamoDB. |
| `LambdaMemory` | Memory size for the Lambda functions. |
| `LambdaTimeout` | Timeout for the Lambda functions. |
| `LogRetentionDays` | CloudWatch Logs retention for the Lambda log groups. |

## Cleanup

To remove the AWS resources created by the template, run:

```bash
aws cloudformation delete-stack \
  --stack-name sentinel-aws-config-ccf
```

If the stack created the SNS topic and AWS Config was configured to use it, update the AWS Config delivery channel as needed before or after deleting the stack.
