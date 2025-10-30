# ***********       Main Flow       ***********

# Validate AWS configuration
Test-AwsConfiguration

Write-Log -Message "Starting data connector configuration script" -LogFileName $LogFileName -Severity Verbose
Write-Log -Message "This script creates an Assume Role with minimal permissions to grant Azure Sentinel access to your logs in a designated S3 bucket & SQS of your choice, enable S3 bucket, SQS Queue, and S3 notifications." -LogFileName $LogFileName -LinePadding 2
Write-ScriptNotes

# Add an Identity Provider
New-OidcProvider
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
$s3RequiredPolicy = Get-RoleS3Policy -RoleArn $roleArn -BucketName $bucketName
Update-S3Policy -RequiredPolicy $s3RequiredPolicy -CustomMessage $customMessage

$logsPath = Read-ValidatedHost -Prompt "Please enter S3 objects full path"
$eventNotificationPrefix = Enable-S3EventNotification -DefaultEventNotificationPrefix $logsPath -IsCustomLog $true 
 
# Output information needed to configure Sentinel data connector
Write-RequiredConnectorDefinitionInfo

Write-Log -Message "please make sure that logs are being exported to the S3 bucket $bucketName into $logsPath" -LogFileName $LogFileName -LinePadding 2

