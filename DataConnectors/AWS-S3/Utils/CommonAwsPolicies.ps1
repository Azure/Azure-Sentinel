function Get-RoleArnPolicy
{
   $arnRolePolicy = "{
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Effect': 'Allow',
                    'Principal': {
                        'AWS': 'arn:aws:iam::197857026523:root'
                    },
                    'Action': 'sts:AssumeRole',
                    'Condition': {
                        'StringEquals': {
                            'sts:ExternalId': '${workspaceId}'
                        }
                    }
                }
            ]
        }"
	return $arnRolePolicy.Replace("'",'\"')
}

function Get-SQSPoliciesForS3AndRule
{
	$sqsPolicyForS3 = "
    {
	  'Version': '2008-10-17',
	  'Id':'__default_policy_ID',
      'Statement': [
		  {
			  'Sid': 'allow s3 to send notification messages to SQS queue',
			  'Effect': 'Allow',
			  'Principal': {
				'Service': 's3.amazonaws.com'
			  },
			  'Action': 'SQS:SendMessage',
			  'Resource': '${sqsArn}',
			  'Condition': {
				'ArnLike': {
				  'aws:SourceArn': 'arn:aws:s3:*:*:${bucketName}'
				}
			  }
		  },
		  {
		  'Sid': 'allow specific role to read/delete/change visibility of SQS messages and get queue url',
		  'Effect': 'Allow',
		  'Principal': {
			'AWS': '${roleArn}'
		  },
		  'Action': [
			'SQS:ChangeMessageVisibility',
			'SQS:DeleteMessage',
			'SQS:ReceiveMessage',
            'SQS:GetQueueUrl'
		  ],
		  'Resource': '${sqsArn}'
		}
	  ]
	}"

	return $sqsPolicyForS3.Replace("'",'"')
}

function Get-SqsEventNotificationConfig
{
   $sqsEventConfig = "
   {
	   'QueueConfigurations': [
			{
			  'Id':'${eventNotificationName}',
			  'QueueArn': '${sqsArn}',
			  'Events': ['s3:ObjectCreated:*'],
			  'Filter': {
				'Key': {
				  'FilterRules': [
					{
					  'Name': 'prefix',
					  'Value': '${eventNotificationPrefix}'
					},
					{
					  'Name': 'suffix',
					  'Value': '.gz'
					}
				  ]
				}
			  }
			}
		]
	}"

	return $sqsEventConfig.Replace("'",'"')
}

function Get-S3PolicyForRole
{
	 $s3PolicyForArn = "{
	 'Statement': [{
            'Sid': 'Allow Arn read access S3 bucket',
            'Effect': 'Allow',
            'Principal': {
                'AWS': '${roleArn}'
            },
            'Action': ['s3:Get*','s3:List*'],
            'Resource': 'arn:aws:s3:::${bucketName}/*'
        }]}"
			
	return $s3PolicyForArn.Replace("'",'"')
}
