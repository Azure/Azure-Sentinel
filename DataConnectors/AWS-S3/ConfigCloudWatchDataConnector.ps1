function Get-RoleAndCloudWatchS3Policy
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
        $BucketName
    )
    $regionConfiguration = aws configure get region  
    $s3PolicyForRoleAndCloudWatch = "{
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
            'Sid': 'Allow CloudWatch to upload objects to the bucket',
            'Effect': 'Allow',
            'Principal': { 
                'Service': 'logs.$regionConfiguration.amazonaws.com'
            },
            'Action': 's3:PutObject',
            'Resource': 'arn:aws:s3:::$BucketName/*'
        },
		{
            'Sid': 'AWSCloudWatchAclCheck',
            'Effect': 'Allow',
            'Principal': {
                'Service': 'logs.$regionConfiguration.amazonaws.com'
            },
            'Action': 's3:GetBucketAcl',
            'Resource': 'arn:aws:s3:::${bucketName}'
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
	return $s3PolicyForRoleAndCloudWatch.Replace("'",'"')
}

# ***********       Main Flow       ***********

# Validate AWS configuration
Test-AwsConfiguration

Write-Log -Message "Starting data connector configuration script" -LogFileName $LogFileName -Severity Verbose
Write-Log -Message "This script creates an Assume Role with minimal permissions to grant Azure Sentinel access to your logs in a designated S3 bucket & SQS of your choice, enable S3 bucket, SQS Queue, and S3 notifications." -LogFileName $LogFileName -LinePadding 2
Write-ScriptNotes

New-ArnRole
Write-Log -Message "Executing: aws iam get-role --role-name $roleName" -LogFileName $LogFileName -Severity Verbose
$roleArnObject = aws iam get-role --role-name $roleName
$roleArn = ($roleArnObject | ConvertFrom-Json ).Role.Arn
Write-Log -Message $roleArn -LogFileName $LogFileName -Severity Verbose

# Create S3 bucket for storing logs
New-S3Bucket

New-SQSQueue
Write-Log -Message "Executing: ((aws sqs get-queue-url --queue-name $sqsName) | ConvertFrom-Json).QueueUrl" -LogFileName $LogFileName -Severity Verbose
$sqsUrl = ((aws sqs get-queue-url --queue-name $sqsName) | ConvertFrom-Json).QueueUrl
Write-Log -Message "Executing: ((aws sqs get-queue-attributes --queue-url $sqsUrl --attribute-names QueueArn )| ConvertFrom-Json).Attributes.QueueArn" -LogFileName $LogFileName -Severity Verbose
$sqsArn =  ((aws sqs get-queue-attributes --queue-url $sqsUrl --attribute-names QueueArn )| ConvertFrom-Json).Attributes.QueueArn
Write-Log -Message "sqsUrl: $sqsUrl sqsArn: $sqsArn" -LogFileName $LogFileName -Severity Verbose

Update-SQSPolicy

$customMessage = "Changes S3: Set notifications"
$s3RequiredPolicy = Get-RoleAndCloudWatchS3Policy -RoleArn $roleArn -BucketName $bucketName
Update-S3Policy -RequiredPolicy $s3RequiredPolicy -CustomMessage $customMessage

$logsPath = Read-ValidatedHost -Prompt "Please enter S3 objects full path"
$eventNotificationPrefix = Enable-S3EventNotification -DefaultEventNotificationPrefix $logsPath
 
# Output information needed to configure Sentinel data connector
Write-RequiredConnectorDefinitionInfo

Write-Log -Message "please make sure that CloudWatch logs are being exported to the S3 bucket $bucketName into $logsPath folder" -LogFileName $LogFileName -LinePadding 2

