
# AWS require polices
The required policise for AWS S3 connectors. 
please note to replac the *{place holder}* values in the policies

##  common polices
These policies are required for all S3 connectors. 

### SQS
 - Allow S3 sending data to the queue
 - Enable Arn role to read, delete and change messages visibilities in the queue
 - {roleArn} is the assumed role ARN you have created for AWS Sentinel account
 - {roleArn} is the assumed role ARN you have created for AWS Sentinel account 
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

### S3
 - Allow Arn role to read the date from S3

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

## Guard Duty
### Kms
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
### S3
 -	Additional policies to allow Guard Duty send logs to S3, and read the data using KMS
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
## Tutorial

The following is a Terrifically Simple JSON document:
```JSON
{
 "name": "Martin",
 "bornOn": "1957-01-05",
 "bornIn": "http://www.scotland.org#"
}
```

