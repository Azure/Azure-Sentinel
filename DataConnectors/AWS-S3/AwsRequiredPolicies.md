
# AWS S3 connector permissions policies

These are the policies required for deploying the AWS S3 data connector.

Be sure to replace the *${placeholder}* values in the policies.

##  Common policies
These policies are required for all S3 connectors, regardless of AWS service.

### SQS policy
 - Allows your S3 bucket to send data to the queue
 - Enables the AWS Sentinel account's assumed role to read, delete and change messages visibilities in the queue
 - Placeholders:
   - {roleArn} is the *assumed role* ARN you have created for the AWS Sentinel account.
   - {sqsArn} is the ARN of the SQS queue you created, to which this policy will apply.
   - {bucketName} is the name of the S3 bucket you are giving send permissions to.

```JSON
{
  "Version": "2008-10-17",
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Sid": "allow s3 to send notification messages to SQS queue",
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "SQS:SendMessage",
      "Resource": "${sqsArn}",
      "Condition": {
        "ArnLike": {
          "aws:SourceArn": "arn:aws:s3:*:*:${bucketName}"
        }
      }
    },
    {
      "Sid": "allow specific role to read/delete/change visibility of SQS messages and get queue url",
      "Effect": "Allow",
      "Principal": {
        "AWS": "${roleArn}"
      },
      "Action": [
        "SQS:ChangeMessageVisibility",
        "SQS:DeleteMessage",
        "SQS:ReceiveMessage",
        "SQS:GetQueueUrl"
      ],
      "Resource": "${sqsArn}"
    }
  ]
}
```

### S3 policy
 - Allows the AWS Sentinel account's assumed role to read the date from the S3 bucket.
 - Placeholders:
   - {roleArn} is the *assumed role* ARN you have created for the AWS Sentinel account.
   - {bucketName} is the name of the S3 bucket.

```JSON
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Sid": "Allow Arn read access S3 bucket",
      "Effect": "Allow",
      "Principal": {
        "AWS": "${roleArn}"
      },
      "Action": [
        "s3:Get*",
        "s3:List*"
      ],
      "Resource": "arn:aws:s3:::${bucketName}/*"
    }
  ]
}
```

<br />

## GuardDuty policies

Apply the following policies if you are ingesting GuardDuty findings.

### KMS policy
- Allows GuardDuty to (read encrypted data in the logs it sends to S3?).
- Placeholders:
   - {roleArn}

```JSON
{
  "Statement": [
    {
      "Sid": "Allow GuardDuty to use the key",
      "Effect": "Allow",
      "Principal": {
        "Service": "guardduty.amazonaws.com"
      },
      "Action": "kms:GenerateDataKey",
      "Resource": "*"
    },
    {
      "Sid": "Allow use of the key",
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "${roleArn}"
        ]
      },
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ],
      "Resource": "*"
    }
  ]
}
```

### S3 policies
-	Additional policies to allow GuardDuty to send logs to S3 and read the data using KMS
- Placeholders:
   - {roleArn}
   - {bucketName}
   - {kmsArn} (what is this?)

```JSON
{
  "Statement": [
    {
      "Sid": "Allow GuardDuty to use the getBucketLocation operation",
      "Effect": "Allow",
      "Principal": {
        "Service": "guardduty.amazonaws.com"
      },
      "Action": "s3:GetBucketLocation",
      "Resource": "arn:aws:s3:::${bucketName}"
    },
    {
      "Sid": "Allow GuardDuty to upload objects to the bucket",
      "Effect": "Allow",
      "Principal": {
        "Service": "guardduty.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::${bucketName}/*"
    },
    {
      "Sid": "Deny unencrypted object uploads. This is optional",
      "Effect": "Deny",
      "Principal": {
        "Service": "guardduty.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::${bucketName}/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "aws:kms"
        }
      }
    },
    {
      "Sid": "Deny incorrect encryption header. This is optional",
      "Effect": "Deny",
      "Principal": {
        "Service": "guardduty.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::${bucketName}/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption-aws-kms-key-id": "${kmsArn}"
        }
      }
    },
    {
      "Sid": "Deny non-HTTPS access",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": "arn:aws:s3:::${bucketName}/*",
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
```

<br />

## CloudTrail

Apply the following policies if you are ingesting CloudTrail logs.

### KMS policy (optional) 
- Allows CloudTrail to encrypt the logs it sends to S3.
- Placeholders:
   - {roleArn}

```JSON
{
  "Statement": [
    {
      "Sid": "Allow CloudTrail to encrypt logs",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "kms:GenerateDataKey*",
      "Resource": "*"
    },
    {
      "Sid": "Allow use of the key",
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "${roleArn}"
        ]
      },
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ],
      "Resource": "*"
    }
  ]
}
```

### S3 policies
Additional S3 policies for CloudTrail. Apply any relevant S3 policies from this section
- Placeholders: (descriptions?)
   - {roleArn}
   - {bucketName}
   - {callerAccount}
   - {organizationId}
   - {kmsArn}

**Allow CloudTrail to send logs to S3**

```JSON
{
  "Statement": [
    {
      "Sid": "AWSCloudTrailAclCheck20150319",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "s3:GetBucketAcl",
      "Resource": "arn:aws:s3:::${bucketName}"
    },
    {
      "Sid": "AWSCloudTrailWrite20150319",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::${bucketName}/AWSLogs/${callerAccount}/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": "bucket-owner-full-control"
        }
      }
    }
  ]
}
```

**Allow logs for cross organization**
```JSON
{
  "Statement": [
    {
      "Sid": "AWSCloudTrailWrite20150319",
      "Effect": "Allow",
      "Principal": {
        "Service": [
          "cloudtrail.amazonaws.com"
        ]
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::${bucketName}/AWSLogs/${organizationId}/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": "bucket-owner-full-control"
        }
      }
    }
  ]
}
```

**Allow S3 to use KMS for the logs**
```JSON
{
  "Statement": [
    {
      "Sid": "Deny unencrypted object uploads. This is optional",
      "Effect": "Deny",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::${bucketName}/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "aws:kms"
        }
      }
    },
    {
      "Sid": "Deny incorrect encryption header. This is optional",
      "Effect": "Deny",
      "Principal": {
        "Service": "cloudtrail.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::${bucketName}/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption-aws-kms-key-id": "${kmsArn}"
        }
      }
    }
  ]
}
```
