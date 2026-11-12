# AWS Unified Connector onboarding

[Overview](../README.md) | [GCP onboarding](../GCP/README.md)

Choose one template to set up AWS access for the connector. All four create a
new IAM collection role. The right choice depends on your existing log pipeline
and OIDC identity provider.

## Choose a template

1. **Check your log pipeline.** To reuse it, you need CloudTrail logs in an S3
   bucket and working object-created notifications reaching an SQS queue.
   Otherwise, choose a template that creates a new pipeline.
2. **Check the identity provider.** In **IAM > Identity providers**, look for
   `https://sts.windows.net/33e01921-4d64-4f8c-a055-5bdaffd5e33d/`.
   If it exists, confirm its audience includes
   `api://1462b192-27f7-4cb9-8523-0f4ecb54b47e`.

| Your current AWS setup | Which template to use | Why |
| --- | --- | --- |
| You need a new log pipeline and do not have the OIDC provider above | [provision-with-identity-provider.json](provision-with-identity-provider.json) | Creates the pipeline, OIDC provider, and collection role. |
| You need a new log pipeline and already have the matching OIDC provider | [provision.json](provision.json) | Creates the pipeline and collection role. Reuses your OIDC provider. |
| Your log pipeline works, but you do not have the OIDC provider above | [existing-resources-with-identity-provider.json](existing-resources-with-identity-provider.json) | Creates the OIDC provider and collection role. Uses your existing bucket and queue. |
| Your log pipeline works and you already have the matching OIDC provider | [existing-resources.json](existing-resources.json) | Creates only the collection role. Uses your existing provider, bucket, and queue. |

The `provision*` templates create a new multi-region CloudTrail trail, S3 bucket,
SNS topic, SQS queue, SNS subscription, and resource policies. They do not reuse
an existing bucket or queue.

The `existing-resources*` templates do not create or repair the log pipeline.
Have the existing **bucket name** and **SQS queue ARN** ready.

AWS allows only one OIDC provider per issuer URL in an account. If the provider
exists but its audience does not match, have its owner review the configuration
before deploying. Do not create a duplicate or delete a shared provider.

## Prerequisites

- An approved provisioning identity permitted to create the requested IAM and,
  for provision variants, CloudTrail/S3/SNS/SQS resources and resource policies.
  Acknowledge `CAPABILITY_NAMED_IAM`; an existing role with the selected name can
  conflict with stack creation.
- AWS CLI for the CLI example below, or the AWS CloudFormation console.
- Existing-resource variants require an already working CloudTrail-to-S3
  notification pipeline feeding the supplied SQS queue. They do not create or
  repair that pipeline.
- An existing OIDC provider, when required, must trust the issuer and audience in
  the selected template. Review existing consumers before changing shared trust.
- Check organization policies, quotas, naming rules, and encryption policies.
  These templates do not add customer-managed KMS decryption permissions.

## Parameters

| Parameter | Used by | Meaning / default |
| --- | --- | --- |
| `TenantId` | All | Required customer Microsoft Entra tenant UUID; no default |
| `UCCLogCollectionRoleName` | All | New role name; `UCC-LogCollection` |
| `UCCLogCollectionCloudTrailName` | Provision | New trail name; `ucc-lc-cloudtrail` |
| `UCCLogCollectionS3BucketName` | Provision | Bucket suffix; `ucc-lc-s3-bucket`; resulting name includes account and region |
| `UCCLogCollectionSqsQueueName` | Provision | New queue name; `ucc-lc-sqs-queue` |
| `ExistingS3BucketName` | Existing resources | Required existing bucket name, not an ARN |
| `ExistingSqsQueueArn` | Existing resources | Required existing queue ARN, not its URL |

Choose valid, unused names. The bucket name must satisfy S3 lowercase naming
requirements even though the template parameter pattern permits uppercase.

## Deployment steps

1. Select the AWS account and region for the source logs.
2. Open the template selected above and choose **Download raw file** in GitHub.
   Deploy only that template, not all four.
3. In **CloudFormation > Stacks**, choose **Create stack > With new resources
   (standard)**. Choose **Upload a template file** and upload the JSON.
4. Enter a stack name, your customer Microsoft Entra `TenantId`, and an unused
   `UCCLogCollectionRoleName`.
5. Fill in the remaining parameters for your template:
   - **New pipeline:** choose names for the trail and queue, and a bucket suffix.
     The bucket name combines your AWS account ID, region, and suffix.
   - **Existing pipeline:** enter `ExistingS3BucketName` and `ExistingSqsQueueArn`.
     Use the queue ARN here, not its URL.
6. Review the resources and permissions. Acknowledge creation of IAM resources
   with custom names, then submit the stack.
7. Wait for `CREATE_COMPLETE`. Open **Outputs** and use the values described
   below to finish connector setup.

Alternatively, after filling in your values, run this example from this folder
for an existing-resource deployment with an existing OIDC provider:

```bash
aws cloudformation create-stack \
  --stack-name '<new-stack-name>' \
  --region '<source-region>' \
  --capabilities CAPABILITY_NAMED_IAM \
  --template-body file://existing-resources.json \
  --parameters \
    ParameterKey=TenantId,ParameterValue='<customer-entra-tenant-id>' \
    ParameterKey=ExistingS3BucketName,ParameterValue='<existing-bucket-name>' \
    ParameterKey=ExistingSqsQueueArn,ParameterValue='<existing-queue-arn>'
```

For provision variants, supply the provision parameters instead of the two
`Existing*` parameters. Do not deploy multiple variants for the same resources.

## Outputs and connector configuration

- **AWS account ID / S3 region:** the source account and region.
- **IAM role ARN:** `UCCLogsReaderRoleArn` from stack outputs.
- **SQS queue URL:** `CloudTrailSQSQueueUrl` for provision variants; for existing
  resources, obtain the queue URL from AWS separately. Do not paste its ARN into
  a portal field asking for a URL.
- Provision variants also output `CloudTrailS3BucketArn`.

Enter these values in the AWS S3 Unified Connector setup in the Microsoft
Defender portal, then check connector health and recent log ingestion.

## Permissions and resource reuse

The role reads the selected bucket and receives/deletes messages from the
selected queue. Historical lookup uses `cloudtrail:LookupEvents` with
`Resource: "*"`. The trust policy fixes Microsoft's commercial issuer/audience
and restricts the requested session name using `TenantId`; do not change these
service constants or substitute a customer tenant as the issuer.

Provisioning changes IAM and starts CloudTrail logging. Review the
service-to-service policies, trust conditions, encryption, and logging scope.
Role session-name filtering alone is not a signed customer-tenant boundary.

## Troubleshooting

These templates do not declare explicit retention/deletion protection for the
new log resources. A nonempty bucket can prevent stack deletion. Inspect stack
events after failure and plan recovery; do not blindly delete a shared OIDC
provider or replace existing policies.
