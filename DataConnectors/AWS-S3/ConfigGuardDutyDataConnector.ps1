function Get-RoleAndGuardDutyS3Policy
{
	<#
    .SYNOPSIS 
        Creates a S3 Policy for GuardDuty based on specified bucket name, role ARN, and Kms ARN

    .PARAMETER RoleArn
		Specifies the Role ARN
	.PARAMETER BucketName
		Specifies the S3 Bucket
    .PARAMETER KmsArn
        Specifies the KMS ARN
    #>
    [OutputType([string])]
    [CmdletBinding()]
    param (
        [Parameter(position=0)]
        [ValidateNotNullOrEmpty()][string]
        $RoleArn,
        [Parameter(position=1)]
        [ValidateNotNullOrEmpty()][string]
        $BucketName,
        [Parameter(position=2)]
        [ValidateNotNullOrEmpty()][string]
        $KmsArn
    )  
    $s3PolicyForRoleAndGuardDuty = "{
	 'Statement': [
		{
            'Sid': 'Allow Arn read access S3 bucket',
            'Effect': 'Allow',
            'Principal': {
                'AWS': '$RoleArn'
            },
            'Action': ['s3:GetObject'],
            'Resource': 'arn:aws:s3:::$BucketName/*'
        },
		{
            'Sid': 'Allow GuardDuty to use the getBucketLocation operation',
            'Effect': 'Allow',
            'Principal': {
                'Service': 'guardduty.amazonaws.com'
            },
            'Action': 's3:GetBucketLocation',
            'Resource': 'arn:aws:s3:::$BucketName'
        },
        {
            'Sid': 'Allow GuardDuty to upload objects to the bucket',
            'Effect': 'Allow',
            'Principal': {
                'Service': 'guardduty.amazonaws.com'
            },
            'Action': 's3:PutObject',
            'Resource': 'arn:aws:s3:::$BucketName/*'
        },
        {
            'Sid': 'Deny unencrypted object uploads. This is optional',
            'Effect': 'Deny',
            'Principal': {
                'Service': 'guardduty.amazonaws.com'
            },
            'Action': 's3:PutObject',
            'Resource': 'arn:aws:s3:::$BucketName/*',
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
            'Resource': 'arn:aws:s3:::$BucketName/*',
            'Condition': {
                'StringNotEquals': {
                    's3:x-amz-server-side-encryption-aws-kms-key-id': '$KmsArn'
                }
            }
        },
        {
            'Sid': 'Deny non-HTTPS access',
            'Effect': 'Deny',
            'Principal': '*',
            'Action': 's3:*',
            'Resource': 'arn:aws:s3:::$BucketName/*',
            'Condition': {
                'Bool': {
                    'aws:SecureTransport': 'false'
                }
            }
	 }]}"	
	return $s3PolicyForRoleAndGuardDuty.Replace("'",'"')
}

function Get-GuardDutyAndRoleKmsPolicy
{
	<#
    .SYNOPSIS 
        Creates a customized KMS Policy for GuardDuty based on specified role ARN
    .PARAMETER RoleArn
		Specifies the Role ARN
    #>
    [OutputType([string])]
    [CmdletBinding()]
    param (
        [Parameter(position=0)]
        [ValidateNotNullOrEmpty()][string]
        $RoleArn
    )

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
                'AWS': ['$RoleArn']
            },
            'Action': [
                'kms:Decrypt'
            ],
            'Resource': '*'
        }
    ]}"
	
	return $kmsPolicy.Replace("'",'"')
}

function Enable-GuardDuty-ForRegion
{
    <#
    .SYNOPSIS 
        Enables GuardDuty based on specified configuration
    .PARAMETER Region
		Specifies the region
    #>

    param (
        [Parameter()]
        [ValidateNotNullOrEmpty()][string]
        $Region
    )

    Write-Log -Message "Enabling GuardDuty for region $region" -LogFileName $LogFileName -LinePadding 1
    Set-RetryAction({
        Write-Log -Message "Executing: aws guardduty create-detector --enable --finding-publishing-frequency FIFTEEN_MINUTES 2>&1" -LogFileName $LogFileName -Severity Verbose
        $newGuarduty = aws --region $region guardduty create-detector --enable --finding-publishing-frequency FIFTEEN_MINUTES 2>&1
        
        $isGuardutyEnabled = $lastexitcode -ne 0
        if ($isGuardutyEnabled)
        {
            Write-Output `n
            Write-Log -Message 'A detector already exists for the current account.' -LogFileName $LogFileName
            Write-Log -Message "Executing: aws guardduty list-detectors" -LogFileName $LogFileName -Severity Verbose

            $script:detectorId = (aws --region $region guardduty list-detectors | ConvertFrom-Json)."DetectorIds"  -join ', '
            Write-Log -Message "Detector Id: $detectorId" -LogFileName $LogFileName
        }
        else
        {
            $script:detectorId = ($newGuarduty | ConvertFrom-Json).DetectorId
        }
        
        Write-Log -Message "Executing: aws guardduty list-publishing-destinations --detector-id $detectorId 2>&1" -LogFileName $LogFileName -Severity Verbose
        $script:currentDestinations = aws --region $region guardduty list-publishing-destinations --detector-id $detectorId 2>&1
        Write-Log $currentDestinations -LogFileName $LogFileName -Severity Verbose
    })
}

function Set-GuardDutyPublishDestinationBucket
{
    <#
    .SYNOPSIS 
        Configures GuardDuty to publish logs to destination bucket
    .PARAMETER Region
		Specifies the region
    #>

    param (
        [Parameter()]
        [ValidateNotNullOrEmpty()][string]
        $Region
    )

    $currentDestinationsObject = $currentDestinations | ConvertFrom-Json
    $currentS3Destinations = $currentDestinationsObject.Destinations | Where-Object DestinationType -eq S3
    if ($null -eq $currentS3Destinations)
    {
        Write-Log -Message "Executing: aws guardduty create-publishing-destination --detector-id $detectorId --destination-type S3 --destination-properties DestinationArn=arn:aws:s3:::$bucketName,KmsKeyArn=$kmsArn | Out-Null" -LogFileName $LogFileName -Severity Verbose
        aws --region $Region guardduty create-publishing-destination --detector-id $detectorId --destination-type S3 --destination-properties DestinationArn=arn:aws:s3:::$bucketName,KmsKeyArn=$kmsArn | Out-Null
    }
    else
    {
        Write-Log "Executing: aws guardduty describe-publishing-destination --detector-id $detectorId --destination-id $currentS3Destinations.DestinationId | ConvertFrom-Json" -LogFileName $LogFileName -Severity Verbose
        $destinationDescriptionObject = aws --region $Region guardduty describe-publishing-destination --detector-id $detectorId --destination-id $currentS3Destinations.DestinationId | ConvertFrom-Json
        $destinationArn = $destinationDescriptionObject.DestinationProperties.DestinationArn

        Write-Log -Message "GuardDuty is already configured for bucket arn '$destinationArn'" -LogFileName $LogFileName -LinePadding 2
        $guardDutyBucketConfirmation = Read-ValidatedHost -Prompt "Are you sure that you want to override the existing bucket destination? [y/n]"
        if ($guardDutyBucketConfirmation -eq 'y')
        {
            Write-Log -Message "Executing: aws guardduty update-publishing-destination --detector-id $detectorId --destination-id $currentS3Destinations.DestinationId --destination-properties DestinationArn=arn:aws:s3:::$bucketName,KmsKeyArn=$kmsArn | Out-Null" -LogFileName $LogFileName -Severity Verbose
            aws --region $Region guardduty update-publishing-destination --detector-id $detectorId --destination-id $currentS3Destinations.DestinationId --destination-properties DestinationArn=arn:aws:s3:::$bucketName,KmsKeyArn=$kmsArn | Out-Null
        }
        else
        {
            Write-Log -Message 'GuardDuty setup was not completed. You must manually update the GuardDuty destination bucket' -LogFileName $LogFileName -Severity Error -LinePadding 2
        }
    } 
}

function Enable-GuardDuty
{
    <#
    .SYNOPSIS 
        Enables GuardDuty based on specified configuration
    #>

    [String[]]$allRegionsArray =  (aws ec2 describe-regions | ConvertFrom-Json)."Regions".RegionName
    $regionConfirmation = Read-ValidatedHost 'Do you want enable guardduty for all regions? [y/n]' -ValidationType Confirm
    if ($regionConfirmation -eq 'y')
    {     
        for($i = 0; $i -lt $allRegionsArray.length; $i++)
        { 
            Enable-GuardDuty-ForRegion -Region $allRegionsArray[$i]
            Set-GuardDutyPublishDestinationBucket -Region $allRegionsArray[$i]
        }
    }
    else
    {
        [String[]]$selectedRegionsArray = Read-ValidatedHost -Prompt "Please enter list of regions seperated by space"
        $selectedRegionsArray = $selectedRegionsArray.Split(' ') | Select-Object -Unique

        for($i = 0; $i -lt $selectedRegionsArray.length; $i++)
        { 
            if (-not($allRegionsArray -contains $selectedRegionsArray[$i]))
            {
                $notValidRegion = $selectedRegionsArray[$i]
                $selectedRegionsArray = $selectedRegionsArray | ? {$_ -ne $notValidRegion}
                Write-Log -Message "Region $notValidRegion doesn't exist" -LogFileName $LogFileName -LinePadding 2
            }
        }
        for($i = 0; $i -lt $selectedRegionsArray.length; $i++)
        { 
            Enable-GuardDuty-ForRegion -Region $selectedRegionsArray[$i]
            Set-GuardDutyPublishDestinationBucket -Region $selectedRegionsArray[$i]
        }
    }
}




# ***********       Main Flow       ***********

# Validate AWS configuration
Test-AwsConfiguration

Write-Log -Message "Starting GuardDuty data connector configuration script" -LogFileName $LogFileName -Severity Verbose
Write-Log -Message "This script creates an Assume Role with minimal permissions to grant Azure Sentinel access to your logs in a designated S3 bucket & SQS of your choice, enable GuardDuty Logs, S3 bucket, SQS Queue, and S3 notifications." -LogFileName $LogFileName -LinePadding 2
Write-ScriptNotes

New-ArnRole
Write-Log -Message "Executing: aws iam get-role --role-name $roleName" -LogFileName $LogFileName -Severity Verbose
$roleArnObject = aws iam get-role --role-name $roleName
$roleArn = ($roleArnObject | ConvertFrom-Json ).Role.Arn
Write-Log -Message $roleArn -LogFileName $LogFileName -Severity Verbose

# Create S3 bucket for storing logs
New-S3Bucket

Write-Log -Message "Executing: (aws sts get-caller-identity | ConvertFrom-Json).Account" -LogFileName $LogFileName -Severity Verbose
$callerAccount = (aws sts get-caller-identity | ConvertFrom-Json).Account
Write-Log -Message $callerAccount -LogFileName $LogFileName -Severity Verbose

New-KMS
$kmsArn = ($kmsKeyDescription | ConvertFrom-Json).KeyMetadata.Arn 
$kmsKeyId = ($kmsKeyDescription | ConvertFrom-Json).KeyMetadata.KeyId
Write-Log -Message "kmsArn: $kmsArn kmsKeyId: $kmsKeyId" -LogFileName $LogFileName -Severity Verbose

New-SQSQueue
Write-Log -Message "Executing: ((aws sqs get-queue-url --queue-name $sqsName) | ConvertFrom-Json).QueueUrl" -LogFileName $LogFileName -Severity Verbose
$sqsUrl = ((aws sqs get-queue-url --queue-name $sqsName) | ConvertFrom-Json).QueueUrl
Write-Log -Message "Executing: ((aws sqs get-queue-attributes --queue-url $sqsUrl --attribute-names QueueArn )| ConvertFrom-Json).Attributes.QueueArn" -LogFileName $LogFileName -Severity Verbose
$sqsArn =  ((aws sqs get-queue-attributes --queue-url $sqsUrl --attribute-names QueueArn )| ConvertFrom-Json).Attributes.QueueArn
Write-Log -Message "sqsUrl: $sqsUrl sqsArn: $sqsArn" -LogFileName $LogFileName -Severity Verbose

$customMessage = "Changes GuardDuty: Kms GenerateDataKey to GuardDuty"
$kmsRequiredPolicies = Get-GuardDutyAndRoleKmsPolicy -RoleArn $roleArn
Update-KmsPolicy -RequiredPolicy $kmsRequiredPolicies -CustomMessage $customMessage

Update-SQSPolicy

$customMessage = "Changes S3: Get GuardDuty notifications"
$s3RequiredPolicy = Get-RoleAndGuardDutyS3Policy -RoleArn $roleArn -BucketName $bucketName -KmsArn $kmsArn
Update-S3Policy -RequiredPolicy $s3RequiredPolicy -CustomMessage $customMessage

Enable-S3EventNotification -DefaultEventNotificationPrefix "AWSLogs/${callerAccount}/GuardDuty/"

Enable-GuardDuty

 
# Output information needed to configure Sentinel data connector
Write-RequiredConnectorDefinitionInfo -DestinationTable AWSGuardDuty