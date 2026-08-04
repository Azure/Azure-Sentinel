# Amazon Web Services Config Microsoft Sentinel Connector

## Introduction

The AWS Config Microsoft Sentinel connector ingests AWS Config configuration item notifications into Microsoft Sentinel by using the Codeless Connector Framework (CCF).

The connector uses an AWS-hosted HTTPS API that is deployed with the included AWS CloudFormation template. Microsoft Sentinel polls this API over HTTPS and authenticates by using an API key in the `x-api-key` header.

The connector stores data in the following custom table:

```text
AWSConfig_CL
```

## End-to-end data flow

```text
AWS Config
-> SNS Topic
-> Lambda Ingest Function
-> DynamoDB Table
-> API Gateway /logs Endpoint
-> Microsoft Sentinel CCF RestApiPoller
-> Data Collection Rule
-> AWSConfig_CL
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

## Key limitations

### The solution is regional

AWS Config is a regional service. Therefore, this solution is deployed per AWS account and per AWS region.

For London, use:

```text
Region: eu-west-2
```

Example:

```text
AWS Account 123456789 / eu-west-2 = 1 CloudFormation deployment
AWS Account 123456789 / eu-west-1 = 1 CloudFormation deployment
```

For multi-account or multi-region environments, deploy the CloudFormation template in each required account and region, or use AWS StackSets.

### The AWS Config S3 bucket must be preserved

AWS Config normally already has a delivery channel with an S3 bucket.

The S3 bucket may have an auto-generated name, for example:

```text
config-bucket-123456789
```

This is expected.

Do not replace or manually change the S3 bucket name unless AWS Config is intentionally being reconfigured.

The correct approach is:

```text
Keep the existing AWS Config S3 bucket.
Add the SNS topic created by the CloudFormation stack.
```

### SNS topic is mandatory

AWS Config must be configured with both:

```text
S3 bucket
SNS topic
```

If AWS Config has only S3 configured, logs may be delivered to S3, but the Lambda function will not be triggered.

Bad configuration:

```json
{
  "name": "default",
  "s3BucketName": "config-bucket-123456789"
}
```

Correct configuration:

```json
{
  "name": "default",
  "s3BucketName": "config-bucket-123456789",
  "snsTopicARN": "arn:aws:sns:eu-west-2:123456789:sentinel-config-notifications"
}
```

### The API endpoint must include `/logs`

The Microsoft Sentinel connector must use the API Gateway `/logs` endpoint.

Correct:

```text
https://xxxx.execute-api.eu-west-2.amazonaws.com/prod/logs
```

Incorrect:

```text
https://xxxx.execute-api.eu-west-2.amazonaws.com/prod
```

### Sentinel authenticates with an API key

The connector does not use AWS AssumeRole.

Microsoft Sentinel polls the API Gateway endpoint using:

```text
Header name: x-api-key
Header value: API key
```

The API key entered in Sentinel must match the API key configured in AWS API Gateway.

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

## Required values for troubleshooting

Before starting troubleshooting, confirm these values:

- AWS Region
- CloudFormation Stack Name
- AWS Account ID
- AWS Config S3 Bucket
- SNS Topic ARN
- API Endpoint
- API Key
- Microsoft Sentinel Workspace
- Microsoft Sentinel Table

Example values:

```text
AWS Region: eu-west-2
Stack Name: AWS-rnd-config
AWS Account ID: 123456789
S3 Bucket: config-bucket-123456789
SNS Topic: arn:aws:sns:eu-west-2:123456789:sentinel-config-notifications
API Endpoint: https://xxxx.execute-api.eu-west-2.amazonaws.com/prod/logs
Sentinel Table: AWSConfig_CL
```

## AWS validation and troubleshooting

### Step 1 - Set variables

Run this in AWS CloudShell:

```bash
REGION="eu-west-2"
STACK_NAME="AWS-rnd-config"

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "REGION=$REGION"
echo "STACK_NAME=$STACK_NAME"
echo "ACCOUNT_ID=$ACCOUNT_ID"
```

Expected output example:

```text
REGION=eu-west-2
STACK_NAME=AWS-rnd-config
ACCOUNT_ID=123456789
```

### Step 2 - Check AWS Config recorder status

```bash
aws configservice describe-configuration-recorder-status \
  --region $REGION
```

Expected values:

```text
"recording": true
"lastStatus": "SUCCESS"
```

If the recorder is not running, start it:

```bash
aws configservice start-configuration-recorder \
  --region $REGION \
  --configuration-recorder-name default
```

### Step 3 - Check AWS Config delivery channel

```bash
aws configservice describe-delivery-channels \
  --region $REGION
```

If the output has only `s3BucketName`, then SNS is missing.

Example of missing SNS:

```json
{
  "DeliveryChannels": [
    {
      "name": "default",
      "s3BucketName": "config-bucket-123456789"
    }
  ]
}
```

Expected output must include both:

```json
{
  "DeliveryChannels": [
    {
      "name": "default",
      "s3BucketName": "config-bucket-123456789",
      "snsTopicARN": "arn:aws:sns:eu-west-2:123456789:sentinel-config-notifications"
    }
  ]
}
```

### Step 4 - Save the existing AWS Config S3 bucket

Do not type the bucket name manually. Read it directly from AWS Config:

```bash
CONFIG_BUCKET=$(aws configservice describe-delivery-channels \
  --region $REGION \
  --query "DeliveryChannels[0].s3BucketName" \
  --output text)

echo "CONFIG_BUCKET=$CONFIG_BUCKET"
```

Expected example:

```text
CONFIG_BUCKET=config-bucket-123456789
```

This bucket must be preserved.

### Step 5 - Get the SNS topic from CloudFormation

```bash
TOPIC_ARN=$(aws cloudformation describe-stacks \
  --region $REGION \
  --stack-name $STACK_NAME \
  --query "Stacks[0].Outputs[?OutputKey=='ConfigNotificationTopicArn'].OutputValue | [0]" \
  --output text)

echo "TOPIC_ARN=$TOPIC_ARN"
```

Expected example:

```text
TOPIC_ARN=arn:aws:sns:eu-west-2:123456789:sentinel-config-notifications
```

If the output is empty or `None`, list all CloudFormation outputs:

```bash
aws cloudformation describe-stacks \
  --region $REGION \
  --stack-name $STACK_NAME \
  --query "Stacks[0].Outputs[*].[OutputKey,OutputValue]" \
  --output table
```

### Step 6 - Add SNS to the AWS Config delivery channel

This is the most important post-deployment step.

```bash
aws configservice put-delivery-channel \
  --region $REGION \
  --delivery-channel name=default,s3BucketName=$CONFIG_BUCKET,snsTopicARN=$TOPIC_ARN
```

Validate again:

```bash
aws configservice describe-delivery-channels \
  --region $REGION
```

Expected result must include:

```text
s3BucketName
snsTopicARN
```

### Step 7 - Confirm SNS subscription to Lambda

```bash
aws sns list-subscriptions-by-topic \
  --region $REGION \
  --topic-arn $TOPIC_ARN
```

Expected result:

```text
Protocol: lambda
Endpoint: arn:aws:lambda:eu-west-2:123456789:function:sentinel-config-ingest
```

If the subscription is missing, create it:

```bash
aws sns subscribe \
  --region $REGION \
  --topic-arn $TOPIC_ARN \
  --protocol lambda \
  --notification-endpoint arn:aws:lambda:$REGION:$ACCOUNT_ID:function:sentinel-config-ingest
```

Then allow SNS to invoke the Lambda function:

```bash
aws lambda add-permission \
  --region $REGION \
  --function-name sentinel-config-ingest \
  --statement-id AllowExecutionFromSNSConfigTopic \
  --action lambda:InvokeFunction \
  --principal sns.amazonaws.com \
  --source-arn $TOPIC_ARN
```

If this error appears, it is acceptable:

```text
ResourceConflictException: The statement id already exists
```

It means the permission already exists.

## End-to-end test

### Step 1 - Trigger a simple AWS Config change

This test adds a tag to the default Security Group.

```bash
SG_ID=$(aws ec2 describe-security-groups \
  --region $REGION \
  --filters Name=group-name,Values=default \
  --query "SecurityGroups[0].GroupId" \
  --output text)

echo "Testing with Security Group: $SG_ID"

aws ec2 create-tags \
  --region $REGION \
  --resources $SG_ID \
  --tags Key=SentinelAWSConfigTest,Value=$(date -u +%Y%m%dT%H%M%SZ)
```

Wait 2-5 minutes.

### Step 2 - Check ingest Lambda logs

```bash
aws logs tail /aws/lambda/sentinel-config-ingest \
  --region $REGION \
  --since 15m
```

Expected result:

```text
New Lambda invocation logs should appear.
```

If no logs appear, check:

- AWS Config delivery channel includes `snsTopicARN`.
- SNS topic has Lambda subscription.
- Lambda invoke permission exists.
- The test was performed in the correct region.
- AWS Config recorder is running.

### Step 3 - Check DynamoDB

```bash
aws dynamodb scan \
  --region $REGION \
  --table-name SentinelConfigLogs \
  --select COUNT
```

Expected result:

```text
The count should increase after the test event.
```

If the count does not increase but Lambda logs exist, check Lambda errors and DynamoDB permissions.

### Step 4 - Get the API endpoint

Use this command to get the API URL from the CloudFormation stack output:

```bash
API_URL=$(aws cloudformation describe-stacks \
  --region $REGION \
  --stack-name $STACK_NAME \
  --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue | [0]" \
  --output text)

echo $API_URL
```

Expected format:

```text
https://xxxx.execute-api.eu-west-2.amazonaws.com/prod/logs
```

If the command returns `None`, list all stack outputs:

```bash
aws cloudformation describe-stacks \
  --region $REGION \
  --stack-name $STACK_NAME \
  --query "Stacks[0].Outputs[*].[OutputKey,OutputValue]" \
  --output table
```

If `/logs` is missing, add it manually when configuring the Sentinel connector.

### Step 5 - Set the API key

If the API key is already known:

```bash
API_KEY="<paste-api-key-here>"
```

If the API key must be retrieved from AWS:

```bash
aws apigateway get-api-keys \
  --region $REGION \
  --include-values \
  --query "items[].[name,value]" \
  --output table
```

Then set:

```bash
API_KEY="<retrieved-api-key-value>"
```

### Step 6 - Test the API directly

```bash
START=$(date -u -d '30 minutes ago' '+%Y-%m-%dT%H:%M:%SZ')
END=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

curl -sS -H "x-api-key: $API_KEY" \
"$API_URL?startTime=$START&endTime=$END" | jq '.events | length'
```

Expected result:

```text
1
```

or more.

If the result is `0`, try a wider time window:

```bash
START=$(date -u -d '2 hours ago' '+%Y-%m-%dT%H:%M:%SZ')
END=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

curl -sS -H "x-api-key: $API_KEY" \
"$API_URL?startTime=$START&endTime=$END" | jq '.events | length'
```

Common API errors:

| Error | Meaning |
|---|---|
| `Forbidden` | Wrong API key or API key is not attached to the usage plan. |
| `Missing Authentication Token` | Wrong endpoint, usually missing `/logs`. |

### Step 7 - Check query Lambda logs

```bash
aws logs tail /aws/lambda/sentinel-config-query \
  --region $REGION \
  --since 30m
```

If logs appear, the API is being called.

The calls may come from either:

- Manual `curl` testing.
- Microsoft Sentinel CCF polling.

## Microsoft Sentinel validation

### Step 1 - Check Sentinel connector configuration

Run this in Azure Cloud Shell:

```bash
SUB="<azure-subscription-id>"
RG="<azure-resource-group>"
WS="<log-analytics-workspace>"

az account set --subscription "$SUB"

az rest --method get \
  --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.OperationalInsights/workspaces/$WS/providers/Microsoft.SecurityInsights/dataConnectors?api-version=2023-11-01-preview" \
  --query "value[].{name:name,kind:kind,isActive:properties.isActive,dataType:properties.dataType,apiEndpoint:properties.request.apiEndpoint,streamName:properties.dcrConfig.streamName}" \
  -o table
```

Expected values:

```text
Kind: RestApiPoller
IsActive: true
DataType: AWSConfig_CL
ApiEndpoint: https://xxxx.execute-api.eu-west-2.amazonaws.com/prod/logs
StreamName: Custom-AWSConfig_CL
```

If the endpoint is incorrect, disconnect and reconnect the connector with the correct `/logs` endpoint.

### Step 2 - Check the Sentinel table

Run in Log Analytics:

```kql
AWSConfig_CL
| where TimeGenerated > ago(4h)
| sort by TimeGenerated desc
```

Summary view:

```kql
AWSConfig_CL
| where TimeGenerated > ago(4h)
| summarize Count=count(), LastSeen=max(TimeGenerated) by AwsAccountId, AwsRegion, ResourceType
| sort by LastSeen desc
```

If unsure whether data landed in another table:

```kql
search *
| where TimeGenerated > ago(4h)
| where $table has "AWS" or $table has "Config"
| summarize Count=count(), Last=max(TimeGenerated) by $table
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

## Troubleshooting decision guide

### Scenario 1 - AWS Config has only S3 and no SNS

Symptom:

```json
{
  "s3BucketName": "config-bucket-123456789"
}
```

Cause:

```text
AWS Config is not notifying the Lambda function.
```

Fix:

```bash
aws configservice put-delivery-channel \
  --region $REGION \
  --delivery-channel name=default,s3BucketName=$CONFIG_BUCKET,snsTopicARN=$TOPIC_ARN
```

### Scenario 2 - No ingest Lambda logs

Check:

```bash
aws logs tail /aws/lambda/sentinel-config-ingest \
  --region $REGION \
  --since 15m
```

Likely causes:

- SNS is not configured in AWS Config delivery channel.
- SNS topic has no Lambda subscription.
- Lambda permission for SNS is missing.
- Wrong AWS region.
- No new AWS Config event was generated.

### Scenario 3 - Lambda logs exist but DynamoDB count does not increase

Check:

```bash
aws dynamodb scan \
  --region $REGION \
  --table-name SentinelConfigLogs \
  --select COUNT
```

Likely causes:

- Lambda processing error.
- DynamoDB permission issue.
- Unexpected AWS Config message format.

### Scenario 4 - DynamoDB count increases but API returns 0

Check API with a wider time window:

```bash
START=$(date -u -d '2 hours ago' '+%Y-%m-%dT%H:%M:%SZ')
END=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

curl -sS -H "x-api-key: $API_KEY" \
"$API_URL?startTime=$START&endTime=$END" | jq '.events | length'
```

Likely causes:

- Wrong time window.
- Event is older than the connector polling window.
- Query Lambda filtering issue.

### Scenario 5 - API returns events but Sentinel has no logs

Likely causes:

- Sentinel connector is not connected.
- Wrong API endpoint in Sentinel.
- Wrong API key in Sentinel.
- DCR or table mapping issue.
- CCF polling issue.

Check Sentinel connector:

```bash
az rest --method get \
  --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.OperationalInsights/workspaces/$WS/providers/Microsoft.SecurityInsights/dataConnectors?api-version=2023-11-01-preview" \
  --query "value[].{name:name,kind:kind,isActive:properties.isActive,dataType:properties.dataType,apiEndpoint:properties.request.apiEndpoint,streamName:properties.dcrConfig.streamName}" \
  -o table
```

## Final operational checklist

Before confirming the connector is operational, verify:

- [ ] AWS Config recorder is running.
- [ ] AWS Config delivery channel has the existing S3 bucket.
- [ ] AWS Config delivery channel also has `snsTopicARN`.
- [ ] `snsTopicARN` points to `sentinel-config-notifications`.
- [ ] SNS topic has Lambda subscription to `sentinel-config-ingest`.
- [ ] Lambda permission allows SNS invocation.
- [ ] A new AWS Config change triggers ingest Lambda logs.
- [ ] DynamoDB count increases after the test event.
- [ ] API endpoint includes `/prod/logs`.
- [ ] API key works with `curl`.
- [ ] API returns one or more events.
- [ ] Sentinel connector is active.
- [ ] Sentinel connector uses the correct API endpoint.
- [ ] Sentinel connector uses the correct API key.
- [ ] `AWSConfig_CL` receives logs.

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

## Client summary

The connector is operational when a test AWS Config change is successfully processed through the full pipeline:

```text
AWS Config change
-> SNS notification
-> Lambda ingest function
-> DynamoDB
-> API Gateway /logs
-> Microsoft Sentinel CCF
-> AWSConfig_CL
```

The most important post-deployment requirement is:

```text
Preserve the existing AWS Config S3 bucket and add the CloudFormation-created SNS topic to the AWS Config delivery channel.
```
