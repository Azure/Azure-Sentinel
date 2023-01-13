function Get-RoleArnPolicy
{
   <#
	.SYNOPSIS
		Returns a customized Arn policy using the Sentinel Workspace Id
	.PARAMETER WorkspaceId
		Specifies the Azure Sentinel workspace id 
   #>
[OutputType([string])]
[CmdletBinding()]
param (
	[Parameter(position=0)]
	[ValidateNotNullOrEmpty()]
	[string]
	$WorkspaceId
)  
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
                            'sts:ExternalId': '$WorkspaceId'
                        }
                    }
                }
            ]
        }"
	return $arnRolePolicy.Replace("'",'\"')
}

function Get-S3AndRuleSQSPolicies
{
   	<#
	.SYNOPSIS
		Returns a customized Sqs rule policy using the specified S3 bucket name, the Sqs ARN, and role ARN.
	.PARAMETER EventNotificationName
		Specifies the event notification name
	.PARAMETER EventNotificationPrefix
		Specifies the event notification prefix
	.PARAMETER SqsArn
		Specifies the Sqs ARN
   #>
   [OutputType([string])]
   [CmdletBinding()]
   param (
	   [ValidateNotNullOrEmpty()][string]
	   $RoleArn,
	   [ValidateNotNullOrEmpty()][string]
	   $BucketName,
	   [ValidateNotNullOrEmpty()][string]
	   $SqsArn
   )  

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
			  'Resource': '$SqsArn',
			  'Condition': {
				'ArnLike': {
				  'aws:SourceArn': 'arn:aws:s3:*:*:$BucketName'
				}
			  }
		  },
		  {
		  'Sid': 'allow specific role to read/delete/change visibility of SQS messages and get queue url',
		  'Effect': 'Allow',
		  'Principal': {
			'AWS': '$RoleArn'
		  },
		  'Action': [
			'SQS:ChangeMessageVisibility',
			'SQS:DeleteMessage',
			'SQS:ReceiveMessage',
            'SQS:GetQueueUrl'
		  ],
		  'Resource': '$SqsArn'
		}
	  ]
	}"

	return $sqsPolicyForS3.Replace("'",'"')
}

function Get-SqsEventNotificationConfig
{ 
   	<#
	.SYNOPSIS
		Returns a customized Sqs event notification config policy using the specified event notification name, the Sqs ARN, and notification prefix.
	.PARAMETER EventNotificationName
		Specifies the event notification name
	.PARAMETER EventNotificationPrefix
		Specifies the event notification prefix
	.PARAMETER SqsArn
		Specifies the Sqs ARN
   #>
[OutputType([string])]
[CmdletBinding()]
param (
	[Parameter(position=0)]
	[ValidateNotNullOrEmpty()]
	[string]
	$EventNotificationName,
	[Parameter(position=1)]
	[ValidateNotNullOrEmpty()]
	[string]
	$EventNotificationPrefix,
	[Parameter(position=2)]
	[ValidateNotNullOrEmpty()]
	[string]
	$SqsArn,
	[Parameter()]
	[bool]
	$IsCustomLog
)  
	$SqsSuffix = ""

	if($true -ne $IsCustomLog)
	{
		$SqsSuffix = ",{
						'Name': 'suffix',
						'Value': '.gz'
						}"
	}


	$sqsEventConfig = "
	{
		'QueueConfigurations': [
				{
				'Id':'$EventNotificationName',
				'QueueArn': '$SqsArn',
				'Events': ['s3:ObjectCreated:*'],
				'Filter': {
					'Key': {
					'FilterRules': [
						{
						'Name': 'prefix',
						'Value': '$EventNotificationPrefix'
						}
						$SqsSuffix
					]
					}
				}
				}
			]
	}"

	return $sqsEventConfig.Replace("'",'"')
}

function Get-RoleS3Policy
{
	<#
	.SYNOPSIS
		Returns a customized Arn policy using the specified role ARN and bucket name
	.PARAMETER RoleArn
		Specifies the Role ARN
	.PARAMETER BucketName
		Specifies the S3 Bucket
   #>
[OutputType([string])]
[CmdletBinding()]
param (
	[Parameter(position=0)]
	[ValidateNotNullOrEmpty()][string]
	$RoleArn,
	[Parameter(position=1)]
	[ValidateNotNullOrEmpty()][string]
	$BucketName
)  
	
	$s3PolicyForArn = "{
	 'Statement': [{
            'Sid': 'Allow Arn read access S3 bucket',
            'Effect': 'Allow',
            'Principal': {
                'AWS': '$RoleArn'
            },
            'Action': ['s3:GetObject'],
            'Resource': 'arn:aws:s3:::$BucketName/*'
        }]}"
			
	return $s3PolicyForArn.Replace("'",'"')
}
