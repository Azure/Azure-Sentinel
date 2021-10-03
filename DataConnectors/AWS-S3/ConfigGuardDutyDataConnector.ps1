
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

function Get-S3PolicyForRoleAndGuardDuty{
	 $s3PolicyForRoleAndGuardDuty = "{
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
            'Sid': 'Allow GuardDuty to use the getBucketLocation operation',
            'Effect': 'Allow',
            'Principal': {
                'Service': 'guardduty.amazonaws.com'
            },
            'Action': 's3:GetBucketLocation',
            'Resource': 'arn:aws:s3:::${bucketName}'
        },
        {
            'Sid': 'Allow GuardDuty to upload objects to the bucket',
            'Effect': 'Allow',
            'Principal': {
                'Service': 'guardduty.amazonaws.com'
            },
            'Action': 's3:PutObject',
            'Resource': 'arn:aws:s3:::${bucketName}/*'
        },
        {
            'Sid': 'Deny unencrypted object uploads. This is optional',
            'Effect': 'Deny',
            'Principal': {
                'Service': 'guardduty.amazonaws.com'
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
                'Service': 'guardduty.amazonaws.com'
            },
            'Action': 's3:PutObject',
            'Resource': 'arn:aws:s3:::${bucketName}/*',
            'Condition': {
                'StringNotEquals': {
                    's3:x-amz-server-side-encryption-aws-kms-key-id': '${kmsArn}'
                }
            }
        },
        {
            'Sid': 'Deny non-HTTPS access',
            'Effect': 'Deny',
            'Principal': '*',
            'Action': 's3:*',
            'Resource': 'arn:aws:s3:::${bucketName}/*',
            'Condition': {
                'Bool': {
                    'aws:SecureTransport': 'false'
                }
            }
	 }]}"	
	return $s3PolicyForRoleAndGuardDuty.Replace("'",'"')
}

function Get-KmsPolicyForGuardDutyAndRole{
	$kmsPolicy = "{
		'Statement': [
        {
            'Sid': 'Allow GuardDuty to use the key',
            'Effect': 'Allow',
            'Principal': {
                'Service': 'guardduty.amazonaws.com'
            },
            'Action': 'kms:GenerateDataKey',
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
       Write-Host `n`n"The maximum number of retries reached. Please try to execute the script again" -ForegroundColor red
       exit
    }
}

# ***********       Main Flow       ***********

Write-Output `n`n'Setting up your AWS environment'
Write-Output `n'The script creates an Assume Role with minimal permissions to grant Azure Sentinel access to your logs in a designated S3 bucket & SQS of your choice, enable'
Write-Output 'GuardDuty logs, Kms, S3 bucket, SQS Queue, and S3 notifications.'
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



Write-Output `n`n'Kms Definition.'
Retry-Action({
	$script:kmaAliasName = Read-Host 'Please insert KMS alias Name'
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


Write-Output `n'Creating SQS queue'
 Retry-Action({
	$script:sqsName = Read-Host 'Please insert Sqs Name'
	$tempForOutput = aws sqs create-queue --queue-name $sqsName 2>&1
 })
$sqsUrl = ((aws sqs get-queue-url --queue-name $sqsName) | ConvertFrom-Json).QueueUrl
$sqsArn =  ((aws sqs get-queue-attributes --queue-url $sqsUrl --attribute-names QueueArn )| ConvertFrom-Json).Attributes.QueueArn


Write-Output `n"Updating the KMS policy to allow Sentinel read the date."
Write-Output "Changes Role: Kms Encrypt, Decrypt, ReEncrypt*, GenerateDataKey* and DescribeKey  permissions to '${roleName}' rule"
Write-Output "Changes GuardDuty: Kms GenerateDataKey to GuardDuty"
$kmsRequiredPolicies = Get-KmsPolicyForGuardDutyAndRole
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
Write-Output "Changes: S3 Get and List permissions to '${roleName}' rule"
Write-Output "Changes: S3 Get GuardDuty notifications"
$s3RequiredPolicy = Get-S3PolicyForRoleAndGuardDuty
$currentBucketPolicy = aws s3api get-bucket-policy --bucket $bucketName 2>&1
$isBucketPolicyExist = $lastexitcode -eq 0
if($isBucketPolicyExist)
{	
	$s3RequiredPolicyObject = $s3RequiredPolicy | ConvertFrom-Json 
	$currentBucketPolicyObject = $currentBucketPolicy | ConvertFrom-Json 	
	$currentBucketPolicies = ($currentBucketPolicyObject.Policy) | ConvertFrom-Json 
	 
    $sqsRequiredPolicyThatNotExistInCurrentPolicy = $s3RequiredPolicyObject.Statement | Where-Object { ($_ | ConvertTo-Json) -notin ($currentBucketPolicies.Statement | ForEach-Object { $_ | ConvertTo-Json}  )}
	if($sqsRequiredPolicyThatNotExistInCurrentPolicy -ne $null)
	{
		$currentBucketPolicies.Statement += $sqsRequiredPolicyThatNotExistInCurrentPolicy
		$UpdatedS3Policy = (@{Statement = $currentBucketPolicies.Statement} | ConvertTo-Json -Depth 16).Replace('"','\"')
		aws s3api put-bucket-policy --bucket $bucketName --policy $UpdatedS3Policy | Out-Null
	}
}
else
{
	$s3RequiredPolicyObject = $s3RequiredPolicy | ConvertFrom-Json
	$newS3Policy = ($s3RequiredPolicyObject | ConvertTo-Json -Depth 16).Replace('"','\"')
	aws s3api put-bucket-policy --bucket $bucketName --policy $newS3Policy | Out-Null
}



Write-Output `n'Enabling S3 Event Notifications (for *.gz file)'
Retry-Action({
	$eventNotificationName = Read-Host 'Please insert GaurdDuty Event Notifications Name'
	$eventNotificationPrefix =  "AWSLogs/${callerAccount}/GuardDuty/"
	$prefixOverrideConfirmation = Read-Host "The Default prefix is '${eventNotificationPrefix}'. `nDo you want to override the event notification prefix? [y/n](n by default)"
	if($prefixOverrideConfirmation -eq 'y')
	{
		$eventNotificationPrefix = Read-Host 'Please insert GaurdDuty Event Notifications Prefix'
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


Write-Output `n'Enabling GuardDuty'
 Retry-Action({
	$newGuarduty = aws guardduty create-detector --enable --finding-publishing-frequency FIFTEEN_MINUTES 2>&1
	$isGuardutyEnabled = $lastexitcode -ne 0
	if($isGuardutyEnabled)
	{
		Write-Output `n'A detector already exists for the current account.'
		Write-Output 'List of existing detectors:'
		aws guardduty list-detectors
		$script:detectorId = Read-Host 'Please insert Detector Id'
	}
	else
	{
		$script:detectorId = ($newGuarduty | ConvertFrom-Json).DetectorId
	}
	$script:currentDestinations = aws guardduty list-publishing-destinations --detector-id $detectorId 2>&1
 })
 
$currentDestinationsObject = $currentDestinations | ConvertFrom-Json
$currentS3Destinations = $currentDestinationsObject.Destinations | Where DestinationType -eq S3
if($currentS3Destinations -eq $null)
{
	aws guardduty create-publishing-destination --detector-id $detectorId --destination-type S3 --destination-properties DestinationArn=arn:aws:s3:::$bucketName,KmsKeyArn=$kmsArn | Out-Null
}
else
{
	$destinatioDescriptionObject = aws guardduty describe-publishing-destination --detector-id $detectorId --destination-id $currentS3Destinations.DestinationId | ConvertFrom-Json
	$destinationArn = $destinatioDescriptionObject.DestinationProperties.DestinationArn
	Write-Output `n"GaurdDuty is already config for bucket arn '${destinationArn}'"
	$guardDutyBucketConfirmation = Read-Host 'Are you sure that you want to override the bucket destination? [y/n]'
	if($guardDutyBucketConfirmation -eq 'y')
	{
		aws guardduty update-publishing-destination --detector-id $detectorId --destination-id $currentS3Destinations.DestinationId --destination-properties DestinationArn=arn:aws:s3:::$bucketName,KmsKeyArn=$kmsArn | Out-Null
	}
	else
	{
		Write-Output `n'GuardDuty setup is not completed. Please update manually GuardDuty destination bucket'
	}
} 
 
 
Write-Output `n`n'Please use the below values to setup the Amazon Web Service S3 Connector in the Data Connectors portal.'
Write-Output "Role arn: ${roleArn}"
Write-Output "Sqs Url: ${sqsUrl}"

Write-Host -NoNewLine `n`n'Press any key to continue...';
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');