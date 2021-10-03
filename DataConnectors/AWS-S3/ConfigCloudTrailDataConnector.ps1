# ***********       Helper Functions       ***********
function Get-RoleArnPolicy{
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


function Get-SQSPoliciesForS3AndRule {
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

function Get-SqsEventNotificationConfig {
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

function Get-S3PolicyForOrganizationClousTrail{	
	$s3PolicyForRoleOrganizationClousTrail = "{
        'Sid': 'AWSCloudTrailWrite20150319',
        'Effect': 'Allow',
        'Principal': {
            'Service': [
                    'cloudtrail.amazonaws.com'
                ]
            },
        'Action': 's3:PutObject',
        'Resource': 'arn:aws:s3:::${bucketName}/AWSLogs/${organizationId}/*',
        'Condition': {
            'StringEquals': {
                's3:x-amz-acl': 'bucket-owner-full-control'
            }
        }
    }"

	return $s3PolicyForRoleOrganizationClousTrail.Replace("'",'"')
}

function Get-S3PolicyForKMS{	
	$s3PolicyForKms = "
	[	
		{
            'Sid': 'Deny unencrypted object uploads. This is optional',
            'Effect': 'Deny',
            'Principal': {
                'Service': 'cloudtrail.amazonaws.com'
            },
            'Action': 's3:PutObject',
            'Resource': 'arn:aws:s3:::${bucketName}/*',
            'Condition': {
                'StringNotEquals': {
                    's3:x-amz-server-side-encryption': 'aws:kms'
                }
            }
        },
        {
            'Sid': 'Deny incorrect encryption header. This is optional',
            'Effect': 'Deny',
            'Principal': {
                'Service': 'cloudtrail.amazonaws.com'
            },
            'Action': 's3:PutObject',
            'Resource': 'arn:aws:s3:::${bucketName}/*',
            'Condition': {
                'StringNotEquals': {
                    's3:x-amz-server-side-encryption-aws-kms-key-id': '${kmsArn}'
                }
            }
		}
    ]"

	return $s3PolicyForKms.Replace("'",'"')
}

function Get-S3PolicyForRoleAndClousTrail{
	 $s3PolicyForRoleAndClousTrail = "{
	 'Statement': [
		{
            'Sid': 'Allow Arn read access S3 bucket',
            'Effect': 'Allow',
            'Principal': {
                'AWS': '${roleArn}'
            },
            'Action': ['s3:Get*','s3:List*'],
            'Resource': 'arn:aws:s3:::${bucketName}/*'
        },
		{
            'Sid': 'AWSCloudTrailAclCheck20150319',
            'Effect': 'Allow',
            'Principal': {
                'Service': 'cloudtrail.amazonaws.com'
            },
            'Action': 's3:GetBucketAcl',
            'Resource': 'arn:aws:s3:::${bucketName}'
        },
        {
            'Sid': 'AWSCloudTrailWrite20150319',
            'Effect': 'Allow',
            'Principal': {
                'Service': 'cloudtrail.amazonaws.com'
            },
            'Action': 's3:PutObject',
            'Resource': 'arn:aws:s3:::${bucketName}/AWSLogs/${callerAccount}/*',
            'Condition': {
                'StringEquals': {
                    's3:x-amz-acl': 'bucket-owner-full-control'
                }
            }
        }]}"	
	return $s3PolicyForRoleAndClousTrail.Replace("'",'"')
}


function Get-KmsPolicyForCloudTrail{
	$kmsPolicy = "{
		'Statement': [
		{
			  'Sid': 'Allow CloudTrail to encrypt logs',
			  'Effect': 'Allow',
			  'Principal': {
				'Service': 'cloudtrail.amazonaws.com'
			  },
			  'Action': 'kms:GenerateDataKey*',
			  'Resource': '*'
		},
        {
            'Sid': 'Allow use of the key',
            'Effect': 'Allow',
            'Principal': {
                'AWS': ['${roleArn}']
            },
            'Action': [
                'kms:Encrypt',
                'kms:Decrypt',
                'kms:ReEncrypt*',
                'kms:GenerateDataKey*',
                'kms:DescribeKey'
            ],
            'Resource': '*'
        }
    ]}"
	
	return $kmsPolicy.Replace("'",'"')
}

function Retry-Action {
	Param([Parameter(Mandatory=$true)][Action]$action)
    $retryCount = 0
	$numberOfRetries = 3
    do {
            $retryCount++
            $action.Invoke();

            if($lastexitcode -ne 0)
            {
                Write-Host $Error[0] -ForegroundColor red
				if($retryCount -lt $numberOfRetries)
				{
					Write-Host `n"please try again"
				}
            }

       } while (($retryCount -lt $numberOfRetries) -and ($lastexitcode -ne 0) )

    if($lastexitcode -ne 0)
    {
       Write-Host `n`n"The number of retries reached. Please tey to execute the script again" -ForegroundColor red
       exit
    }
}

# ***********       Main Flow       ***********

Write-Output `n`n'Setting up your AWS environment'
Write-Output `n'The script creates an Assume Role with minimal permissions to grant Azure Sentinel access to your logs in a designated S3 bucket & SQS of your choice, enable'
Write-Output 'CloudTrail logs, Kms, S3 bucket, SQS Queue, and S3 notifications.'
Write-Output `n`n'Please insert AWS configuration:'
aws configure


Write-Output `n`n'Arn Role Defenition'
 Retry-Action({
	$script:roleName = Read-Host 'Please insert Role Name. If you have already configured an Assume Role for Azure Sentinel in the past, please type the name'
	aws iam get-role --role-name $roleName 2>&1| Out-Null
	$isRuleNotExist = $lastexitcode -ne 0
	if($isRuleNotExist)
	{
		$workspaceId = Read-Host 'Please insert Workspae Id (External Id)'
		$rolePolicy = Get-RoleArnPolicy
		$tempForOutput = aws iam create-role --role-name $roleName --assume-role-policy-document $rolePolicy 2>&1
		if($lastexitcode -eq 0)
		{
			Write-Host  "${roleName} Role was successful created"
		}
	}
})
 
$roleArnObject = aws iam get-role --role-name $roleName
$roleArn = ($roleArnObject | ConvertFrom-Json ).Role.Arn


Write-Output `n`n'S3 Bucket Definition.'
 Retry-Action({
	$script:bucketName = Read-Host 'Please insert S3 Bucket Name'
	$headBucketOutput = aws s3api head-bucket --bucket $bucketName 2>&1
	$isBucketNotExist = $headBucketOutput -ne $null
	if($isBucketNotExist)
	{
		$bucketRegion = Read-Host 'Please insert Bucket Region'
		if($bucketRegion -eq "us-east-1") # see aws doc https://docs.aws.amazon.com/cli/latest/reference/s3api/create-bucket.html
		{
			$tempForOutput = aws s3api create-bucket --bucket $bucketName 2>&1
		}
		else
		{
			$tempForOutput = aws s3api create-bucket --bucket $bucketName --create-bucket-configuration LocationConstraint=$bucketRegion 2>&1
		}
		
		if($lastexitcode -eq 0)
		{
			Write-Host  "${bucketName} Bucket was successful created"
		}
	}	
})
$callerAccount = (aws sts get-caller-identity | ConvertFrom-Json).Account
$organizationId = ((aws organizations describe-account --account-id $callerAccount) | ConvertFrom-Json).Account.Arn.Split('/')[1]



Write-Output `n'Creating SQS queue'
 Retry-Action({
	$script:sqsName = Read-Host 'Please insert Sqs Name'
	$tempForOutput = aws sqs create-queue --queue-name $sqsName 2>&1
 })
$sqsUrl = ((aws sqs get-queue-url --queue-name $sqsName) | ConvertFrom-Json).QueueUrl
$sqsArn =  ((aws sqs get-queue-attributes --queue-url $sqsUrl --attribute-names QueueArn )| ConvertFrom-Json).Attributes.QueueArn


$kmsCofirmation = Read-Host `n`n'Do you want to enable KMS for cloudTrail? [y/n](n by default)'
if($kmsCofirmation -eq 'y')
{
	Write-Output `n'Kms Definition.'
	Retry-Action({
		$kmaAliasName = Read-Host 'Please insert KMS alias Name'
		$script:kmsKeyDescription = aws kms describe-key --key-id alias/$kmaAliasName 2>&1
		$isKmsNotExist = $lastexitcode -ne 0
		if($isKmsNotExist)
		{
			$script:kmsKeyDescription = aws kms create-key
			$kmsKeyId = ($script:kmsKeyDescription | ConvertFrom-Json).KeyMetadata.KeyId
			$tempForOutput = aws kms create-alias --alias-name alias/$kmaAliasName --target-key-id $kmsKeyId 2>&1
			if($lastexitcode -eq 0)
			{
				Write-Host  "${kmaAliasName} Kms was successful created"
			}
		}
	})
	$kmsArn = ($kmsKeyDescription | ConvertFrom-Json).KeyMetadata.Arn 
	$kmsKeyId = ($kmsKeyDescription | ConvertFrom-Json).KeyMetadata.KeyId
	
	
	Write-Output `n"Updating the KMS policy to allow Sentinel read the date."
	Write-Output "Changes Role: Kms Encrypt, Decrypt, ReEncrypt*, GenerateDataKey* and DescribeKey  permissions to '${roleName}' rule"
	Write-Output "Changes CloudTrail: Kms GenerateDataKey to CloudTrail"
	$kmsRequiredPolicies = Get-KmsPolicyForCloudTrail
	$currentKmsPolicy = aws kms get-key-policy --policy-name default --key-id $kmsKeyId
	if($currentKmsPolicy -ne $null)
	{
		$kmsRequiredPoliciesObject = $kmsRequiredPolicies | ConvertFrom-Json 
		$currentKmsPolicyObject = $currentKmsPolicy | ConvertFrom-Json 	
		$currentKmsPolicies = ($currentKmsPolicyObject.Policy) | ConvertFrom-Json
		
		$kmsRequiredPoliciesThatNotExistInCurrentPolicy =  $kmsRequiredPoliciesObject.Statement | Where-Object { ($_ | ConvertTo-Json -Depth 5) -notin ($currentKmsPolicies.Statement | ForEach-Object { $_ | ConvertTo-Json -Depth 5}  )}
		if($kmsRequiredPoliciesThatNotExistInCurrentPolicy -ne $null)
		{
			$currentKmsPolicies.Statement += $kmsRequiredPoliciesThatNotExistInCurrentPolicy

			$UpdatedKmsPolicyObject = ($currentKmsPolicies | ConvertTo-Json -Depth 16).Replace('"','\"')
			aws kms put-key-policy --policy-name default --key-id $kmsKeyId --policy $UpdatedKmsPolicyObject | Out-Null
		}
	}
	else
	{
		$newKmsPolicyObject = ($kmsRequiredPolicies | ConvertFrom-Json |  ConvertTo-Json -Depth 16).Replace('"','\"')
		aws kms put-key-policy --policy-name default --key-id $kmsKeyId --policy $newKmsPolicyObject | Out-Null
	}
}


Write-Output `n"Updating the SQS policy to allow S3 notifications, and arn to read/delete/change visibility of SQS messages and get queue url"
Write-Output "Changes S3: SQS SendMessage permission to '${bucketName}' s3 bucket"
Write-Output "Changes ARN: SQS ChangeMessageVisibility, DeleteMessage, ReceiveMessage and GetQueueUrl permissions to '${roleName}' rule"
$sqsRequiredPolicies = Get-SQSPoliciesForS3AndRule
$currentSqsPolicy = aws sqs get-queue-attributes --queue-url $sqsUrl --attribute-names Policy
if($currentSqsPolicy -ne $null)
{
	$sqsRequiredPoliciesObject = $sqsRequiredPolicies | ConvertFrom-Json 
	$currentSqsPolicyObject = $currentSqsPolicy | ConvertFrom-Json 	
	$currentSqsPolicies = ($currentSqsPolicyObject.Attributes.Policy) | ConvertFrom-Json 
	
	$sqsRequiredPoliciesThatNotExistInCurrentPolicy =  $sqsRequiredPoliciesObject.Statement | Where-Object { ($_ | ConvertTo-Json -Depth 5) -notin ($currentSqsPolicies.Statement | ForEach-Object { $_ | ConvertTo-Json -Depth 5}  )}
	if($sqsRequiredPoliciesThatNotExistInCurrentPolicy -ne $null)
	{
		$currentSqsPolicies.Statement += $sqsRequiredPoliciesThatNotExistInCurrentPolicy

		$UpdatedPolicyValue = ($currentSqsPolicies | ConvertTo-Json -Depth 16  -Compress).Replace('"','\\\"')
		$UpdatedSqsPolicy = ("{'Policy':'${UpdatedPolicyValue}'}").Replace("'",'\"')
		aws sqs set-queue-attributes --queue-url $sqsUrl  --attributes $UpdatedSqsPolicy | Out-Null
	}
}
else
{
	$newSqsPolicyValue = ($sqsRequiredPolicies | ConvertFrom-Json |  ConvertTo-Json -Depth 16  -Compress).Replace('"','\\\"')
	$newSqsPolicyObject = ("{'Policy':'${newSqsPolicyValue}'}").Replace("'",'\"')
	aws sqs set-queue-attributes --queue-url $sqsUrl  --attributes $newSqsPolicyObject | Out-Null
}


Write-Output `n"Updating the S3 policy to allow Sentinel read the date."
$organizetionCloudTrailConfirmation = Read-Host `n'Do you want to enable the Trail and CloudTtail S3 Policy for all accounts in your organization? [y/n](y by default)'
Write-Output "Changes: S3 Get and List permissions to '${roleName}' rule"
Write-Output "Changes: S3 Get CloudTrail notifications"
$currentBucketPolicy = aws s3api get-bucket-policy --bucket $bucketName 2>&1
$s3RequiredPolicy = Get-S3PolicyForRoleAndClousTrail
$s3RequiredPolicyObject = $s3RequiredPolicy | ConvertFrom-Json 
if($organizetionCloudTrailConfirmation -ne 'n')
{
	$s3RequiredPolicyObject.Statement += (Get-S3PolicyForOrganizationClousTrail | ConvertFrom-Json)
}
if($kmsCofirmation -eq 'y')
{
	$s3RequiredPolicyObject.Statement += (Get-S3PolicyForKMS | ConvertFrom-Json)
}

$isBucketPolicyExist = $lastexitcode -eq 0
if($isBucketPolicyExist)
{	
	$currentBucketPolicyObject = $currentBucketPolicy | ConvertFrom-Json 	
	$currentBucketPolicies = ($currentBucketPolicyObject.Policy) | ConvertFrom-Json 
	 
    $sqsRequiredPolicyThatNotExistInCurrentPolicy = $s3RequiredPolicyObject.Statement | Where-Object { ($_ | ConvertTo-Json -Depth 5) -notin ($currentBucketPolicies.Statement | ForEach-Object { $_ | ConvertTo-Json -Depth 5}  )}
	if($sqsRequiredPolicyThatNotExistInCurrentPolicy -ne $null)
	{
		$currentBucketPolicies.Statement += $sqsRequiredPolicyThatNotExistInCurrentPolicy
		$UpdatedS3Policy = (@{Statement = $currentBucketPolicies.Statement} | ConvertTo-Json -Depth 16).Replace('"','\"')
		aws s3api put-bucket-policy --bucket $bucketName --policy $UpdatedS3Policy | Out-Null
	}
}
else
{
	$newS3Policy = ($s3RequiredPolicyObject | ConvertTo-Json -Depth 16).Replace('"','\"')
	aws s3api put-bucket-policy --bucket $bucketName --policy $newS3Policy | Out-Null
}



Write-Output `n'Enabling S3 Event Notifications (for *.gz file)'
Retry-Action({
	$eventNotificationName = Read-Host 'Please insert CloudTrail Event Notifications Name'
	if($organizetionCloudTrailConfirmation -ne 'n')
	{
		$eventNotificationPrefix =  "AWSLogs/${organizationId}/"
	}
	else
	{
		$eventNotificationPrefix =  "AWSLogs/${callerAccount}/CloudTrail/"
	}	
	$prefixOverrideConfirmation = Read-Host "The Default prefix is '${eventNotificationPrefix}'. `nDo you want to override the event notification prefix? [y/n](n by default)"
	if($prefixOverrideConfirmation -eq 'y')
	{
		$eventNotificationPrefix = Read-Host 'Please insert CloudTrail Event Notifications Prefix'
	}
	$newEventConfig = Get-SqsEventNotificationConfig
	$existingEventConfig = aws s3api get-bucket-notification-configuration --bucket $bucketName
	if($existingEventConfig -ne $null)
	{
		$newEventConfigObject = $newEventConfig | ConvertFrom-Json
		$existingEventConfigObject = $existingEventConfig | ConvertFrom-Json 
		
		$newEventConfigObject.QueueConfigurations += $existingEventConfigObject.QueueConfigurations
		$updatedEventConfigs = ($newEventConfigObject | ConvertTo-Json -Depth 6 ).Replace('"','\"')
	}
	else
	{
		$updatedEventConfigs = $newEventConfig.Replace('"','\"')
	}
	$tempForOutput = aws s3api put-bucket-notification-configuration --bucket $bucketName --notification-configuration $updatedEventConfigs 2>&1
})




Write-Output `n`n'CloudTrail Defenition'
 Retry-Action({
	$script:cloudTrailName = Read-Host 'Please insert cloudTrail name'
	aws cloudtrail get-trail --name $cloudTrailName 2>&1| Out-Null
	$isCloudTrailNotExist = $lastexitcode -ne 0
	if($isCloudTrailNotExist)
	{
		if($kmsCofirmation -eq 'y')
		{
			$tempForOutput = aws cloudtrail create-trail --name $cloudTrailName --s3-bucket-name $bucketName --kms-key-id $kmsKeyId 2>&1
		}
		else
		{
			$tempForOutput = aws cloudtrail create-trail --name $cloudTrailName --s3-bucket-name $bucketName 2>&1
		}
		if($lastexitcode -eq 0)
		{
			Write-Host  "${cloudTrailName} trail was successful created"
		}
	}
	else
	{
		$cloudtrailBucketConfirmation = Read-Host "Trail '${cloudTrailName}' is already config. Are you sure that you want to override the bucket destination? [y/n]"
		if($cloudtrailBucketConfirmation -eq 'y')
		{
			if($kmsCofirmation -eq 'y')
			{
				aws cloudtrail update-trail --name $cloudTrailName --s3-bucket-name $bucketName -kms-key-id $kmsKeyId | Out-Null
			}
			else
			{
				aws cloudtrail update-trail --name $cloudTrailName --s3-bucket-name $bucketName | Out-Null
			}
		}
		else
		{
			Write-Output `n'CloudTrail setup is not completed. Please update manually CloudTrail destination bucket'
		}
	}
 })


## CloudTrail configuration
$DataEventsConfirmation = Read-Host `n'Do you want to enable the CloudTtail data events? [y/n](n by default)'
if($DataEventsConfirmation -eq 'y')
{
	aws cloudtrail put-event-selectors --trail-name $cloudTrailName --event-selectors '[{\"DataResources\": [{\"Type\":\"AWS::S3::Object\", \"Values\": [\"arn:aws:s3:::\"]}]}]' | Out-Null
}

$regionCofirmation = Read-Host 'Do you want to define the Trail as multi region? [y/n](n by default)'
if($regionCofirmation -eq 'y')
{
	aws cloudtrail update-trail --name $cloudTrailName --is-multi-region-trail | Out-Null 
}
else
{
	aws cloudtrail update-trail --name $cloudTrailName --no-is-multi-region-trail | Out-Null 
}

if($organizetionCloudTrailConfirmation -ne 'n')
{	
	aws cloudtrail update-trail --name $cloudTrailName --is-organization-trail | Out-Null
}
else
{
	aws cloudtrail update-trail --name $cloudTrailName --no-is-organization-trail | Out-Null
}

aws cloudtrail start-logging  --name $cloudTrailName

Write-Output `n`n'Attached AWSCloudTrailReadOnlyAccess policy To ARN'
aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/AWSCloudTrailReadOnlyAccess --role-name $roleName


Write-Output `n`n'Please use the below values to setup the Amazon Web Service S3 Connector in the Data Connectors portal.'
Write-Output "Role arn: ${roleArn}"
Write-Output "Sqs Url: ${sqsUrl}"

Write-Host -NoNewLine `n`n'Press any key to continue...';
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');

