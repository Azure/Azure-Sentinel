function Get-KmsPolicyForCloudTrail
{
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

function Get-S3PolicyForOrganizationCloudTrail
{	
	$s3PolicyForRoleOrganizationCloudTrail = "{
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

	return $s3PolicyForRoleOrganizationCloudTrail.Replace("'",'"')
}

function Get-S3PolicyForKMS
{	
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

function Get-S3PolicyForRoleAndCloudTrail
{
	 $s3PolicyForRoleAndCloudTrail = "{
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
	return $s3PolicyForRoleAndCloudTrail.Replace("'",'"')
}

function BuildCloudTrailS3Policy
{
	$s3RequiredPolicy = Get-S3PolicyForRoleAndCloudTrail
	$s3RequiredPolicyObject = $s3RequiredPolicy | ConvertFrom-Json 
	if ($organizationCloudTrailConfirmation -ne 'n')
	{
		$s3RequiredPolicyObject.Statement += (Get-S3PolicyForOrganizationCloudTrail | ConvertFrom-Json)
	}
	if ($kmsConfirmation -eq 'y')
	{
		$s3RequiredPolicyObject.Statement += (Get-S3PolicyForKMS | ConvertFrom-Json)
	}

	return $s3RequiredPolicyObject | ConvertTo-Json -Depth 5
}

function Get-EventNotificationPrefix
{
	if ($organizationCloudTrailConfirmation -ne 'n')
	{
		return "AWSLogs/${organizationId}/"
	}
	else
	{
		return  "AWSLogs/${callerAccount}/CloudTrail/"
	}	
}

function Set-CloudTrailDataEventConfig
{
	$DataEventsConfirmation = Read-Host `n'Do you want to enable the CloudTrail data events? [y/n](n by default)'
	if ($DataEventsConfirmation -eq 'y')
	{
		aws cloudtrail put-event-selectors --trail-name $cloudTrailName --event-selectors '[{\"DataResources\": [{\"Type\":\"AWS::S3::Object\", \"Values\": [\"arn:aws:s3:::\"]}]}]' | Out-Null
	}
}
function Set-MultiRegionTrailConfig
{
	$regionConfirmation = Read-Host 'Do you want to define the Trail as multi region? [y/n](n by default)'
	if ($regionConfirmation -eq 'y')
	{
		aws cloudtrail update-trail --name $cloudTrailName --is-multi-region-trail | Out-Null 
	}
	else
	{
		aws cloudtrail update-trail --name $cloudTrailName --no-is-multi-region-trail | Out-Null 
	}
}

function Set-OrganizationTrailConfig
{
	if ($organizationCloudTrailConfirmation -ne 'n')
	{	
		aws cloudtrail update-trail --name $cloudTrailName --is-organization-trail | Out-Null
	}
	else
	{
		aws cloudtrail update-trail --name $cloudTrailName --no-is-organization-trail | Out-Null
	}
}

# ***********       Main Flow       ***********

Get-AwsConfig

New-ArnRole
$roleArnObject = aws iam get-role --role-name $roleName
$roleArn = ($roleArnObject | ConvertFrom-Json ).Role.Arn

New-S3Bucket
$callerAccount = (aws sts get-caller-identity | ConvertFrom-Json).Account
$organizationId = ((aws organizations describe-account --account-id $callerAccount) | ConvertFrom-Json).Account.Arn.Split('/')[1]

New-SQSQueue
$sqsUrl = ((aws sqs get-queue-url --queue-name $sqsName) | ConvertFrom-Json).QueueUrl
$sqsArn =  ((aws sqs get-queue-attributes --queue-url $sqsUrl --attribute-names QueueArn )| ConvertFrom-Json).Attributes.QueueArn


$kmsConfirmation = Read-Host `n`n'Do you want to enable KMS for cloudTrail? [y/n](n by default)'
if ($kmsConfirmation -eq 'y')
{
	DefineKMS
	$kmsArn = ($kmsKeyDescription | ConvertFrom-Json).KeyMetadata.Arn 
	$kmsKeyId = ($kmsKeyDescription | ConvertFrom-Json).KeyMetadata.KeyId
	
	$customMessage = "Changes CloudTrail: Kms GenerateDataKey to CloudTrail"
    $kmsRequiredPolicies = Get-KmsPolicyForCloudTrail
    Update-KmsPolicy -RequiredPolicy $kmsRequiredPolicies -CustomMessage $customMessage
}

Update-SQSPolicy

$organizationCloudTrailConfirmation = Read-Host `n'Do you want to enable the Trail and CloudTrail S3 Policy for all accounts in your organization? [y/n](y by default)'
$s3RequiredPolicy = BuildCloudTrailS3Policy
$customMessage = "Changes: S3 Get CloudTrail notifications"
Update-S3Policy -RequiredPolicy $s3RequiredPolicy -CustomMessage $customMessage

$eventNotificationPrefix = Get-EventNotificationPrefix
Enable-S3EventNotification -DefaultEvenNotificationPrefix $eventNotificationPrefix

Write-Output `n`n'CloudTrail Definition'
 New-RetryAction({
	$script:cloudTrailName = Read-Host 'Please enter CloudTrail name'
	aws cloudtrail get-trail --name $cloudTrailName 2>&1| Out-Null
	$isCloudTrailNotExist = $lastexitcode -ne 0
	if ($isCloudTrailNotExist)
	{
		if ($kmsConfirmation -eq 'y')
		{
			$tempForOutput = aws cloudtrail create-trail --name $cloudTrailName --s3-bucket-name $bucketName --kms-key-id $kmsKeyId 2>&1
		}
		else
		{
			$tempForOutput = aws cloudtrail create-trail --name $cloudTrailName --s3-bucket-name $bucketName 2>&1
		}
		if($lastexitcode -eq 0)
		{
			Write-Host  "${cloudTrailName} trail created successfully"
		}
	}
	else
	{
		$cloudTrailBucketConfirmation = Read-Host "Trail '${cloudTrailName}' is already configured. Do you want to override the bucket destination? [y/n]"
		
		if ($cloudTrailBucketConfirmation -eq 'y')
		{
			if ($kmsConfirmation -eq 'y')
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
			Write-Output `n'CloudTrail setup was not completed. You must manually updated the CloudTrail destination bucket'
		}
	}
 })


Set-CloudTrailDataEventConfig
Set-MultiRegionTrailConfig
Set-OrganizationTrailConfig

aws cloudtrail start-logging  --name $cloudTrailName

Write-TheRequiredDataForTheConnectorDefinition

