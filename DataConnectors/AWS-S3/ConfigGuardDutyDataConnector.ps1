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

function EnableGuardDuty{
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
}


function DefineGuardDutyPublishDestinationBucket{
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
}

# ***********       Main Flow       ***********

Get-AwsConfig

DefineArnRole
$roleArnObject = aws iam get-role --role-name $roleName
$roleArn = ($roleArnObject | ConvertFrom-Json ).Role.Arn

DefineS3Bucket
$callerAccount = (aws sts get-caller-identity | ConvertFrom-Json).Account

DefineKMS
$kmsArn = ($kmsKeyDescription | ConvertFrom-Json).KeyMetadata.Arn 
$kmsKeyId = ($kmsKeyDescription | ConvertFrom-Json).KeyMetadata.KeyId

CreatSQSQueue
$sqsUrl = ((aws sqs get-queue-url --queue-name $sqsName) | ConvertFrom-Json).QueueUrl
$sqsArn =  ((aws sqs get-queue-attributes --queue-url $sqsUrl --attribute-names QueueArn )| ConvertFrom-Json).Attributes.QueueArn


$customMessage = "Changes GuardDuty: Kms GenerateDataKey to GuardDuty"
$kmsRequiredPolicies = Get-KmsPolicyForGuardDutyAndRole
Update-KmsPolicy -RequiredPolicy $kmsRequiredPolicies -CustomMessage $customMessage

Update-SQSPolicy

$customMessage = "Changes: S3 Get GuardDuty notifications"
$s3RequiredPolicy = Get-S3PolicyForRoleAndGuardDuty
Update-S3Policy -RequiredPolicy $s3RequiredPolicy -CustomMessage $customMessage

Enable-S3EventNotification -DefaultEvenNotificationPrefix "AWSLogs/${callerAccount}/GuardDuty/"

EnableGuardDuty
DefineGuardDutyPublishDestinationBucket
 
Write-TheRequiredDataForTheConnectorDefinition