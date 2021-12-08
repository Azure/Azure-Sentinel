# Validate AWS configuration
Test-AwsConfiguration

Write-Log -Message "Starting Vpc flow data connector configuration script" -LogFileName $LogFileName -Severity Verbose
Write-Log -Message "This script creates an Assume Role with minimal permissions to grant Azure Sentinel access to your logs in a designated S3 bucket & SQS of your choice, enable VPCFlow Logs, S3 bucket, SQS Queue, and S3 notifications." -LogFileName $LogFileName
Write-ScriptNotes

# Create new Arn Role
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

Write-Log -Message "Listing your available VPC IDs" -LogFileName $LogFileName -Severity Information -LinePadding 1
Write-Log -Message "Executing: aws ec2 --output text --query 'Vpcs[*].{VpcId:VpcId}' describe-vpcs" -LogFileName $LogFileName -Severity Verbose
aws ec2 --output text --query 'Vpcs[*].{VpcId:VpcId}' describe-vpcs

Write-Log 'Enabling VPC flow Logs (default format)' -LogFileName $LogFileName -Severity Information -LinePadding 1

Set-RetryAction({
	
	$vpcResourceIds = Read-ValidatedHost 'Please enter VPC Resource Id[s] from the above list (space separated)'
	Write-Log -Message "Using Vpc Resource Ids: $vpcResourceIds" -LogFileName $LogFileName -Severity Information -Indent 2
	
	do
	{
    	try
		{
			[ValidateSet("ALL","ACCEPT","REJECT")]$vpcTrafficType = Read-Host 'Please enter traffic type (ALL, ACCEPT, REJECT)'
		}
		catch {}

	} until ($?)

	$vpcName = Read-ValidatedHost 'Please enter Vpc flow logs name'
	Write-Log "Using Vpc name: $vpcName" -LogFileName $LogFileName -Indent 2

	$vpcTagSpecifications = "ResourceType=vpc-flow-log,Tags=[{Key=Name,Value=${vpcName}}, {Key=$(Get-SentinelTagKey),Value=$(Get-SentinelTagValue)}]"
	Write-Log -Message "Vpc tag specification: $vpcTagSpecifications" -LogFileName $LogFileName

	Write-Log -Message "Executing: aws ec2 create-flow-logs --resource-type VPC --resource-ids $vpcResourceIds.Split(' ') --traffic-type $vpcTrafficType --log-destination-type s3 --log-destination arn:aws:s3:::$bucketName --tag-specifications $vpcTagSpecifications 2>&1" -LogFileName $LogFileName -Severity Verbose
	$tempForOutput = aws ec2 create-flow-logs --resource-type VPC --resource-ids $vpcResourceIds.Split(' ') --traffic-type $vpcTrafficType.ToUpper() --log-destination-type s3 --log-destination arn:aws:s3:::$bucketName --tag-specifications $vpcTagSpecifications 2>&1
	Write-Log $tempForOutput -LogFileName $LogFileName -Severity Verbose

})

New-SQSQueue

Write-Log "Executing: ((aws sqs get-queue-url --queue-name $sqsName) | ConvertFrom-Json).QueueUrl" -LogFileName $LogFileName -Severity Verbose
$sqsUrl = ((aws sqs get-queue-url --queue-name $sqsName) | ConvertFrom-Json).QueueUrl
Write-Log $sqsUrl.ToString() -LogFileName $LogFileName -Severity Verbose

Write-Log "Executing: ((aws sqs get-queue-attributes --queue-url $sqsUrl --attribute-names QueueArn )| ConvertFrom-Json).Attributes.QueueArn" -LogFileName $LogFileName -Severity Verbose
$sqsArn =  ((aws sqs get-queue-attributes --queue-url $sqsUrl --attribute-names QueueArn )| ConvertFrom-Json).Attributes.QueueArn
Write-Log $sqsArn.ToString() -LogFileName $LogFileName -Severity Verbose

Update-SQSPolicy

Write-Log -Message "Attaching S3 read policy to Sentinel role." -LogFileName $LogFileName -LinePadding 1
Write-Log -Message "Changes Role arn: S3 Get and List permissions to '${roleName}' rule" -LogFileName $LogFileName -LinePadding 1

$s3RequiredPolicy = Get-RoleS3Policy -RoleArn $roleArn -BucketName $bucketName
Update-S3Policy -RequiredPolicy $s3RequiredPolicy

Enable-S3EventNotification -DefaultEventNotificationPrefix "AWSLogs/${callerAccount}/vpcflowlogs/"

# Output information needed to configure Sentinel data connector
Write-RequiredConnectorDefinitionInfo -DestinationTable AWSVPCFlow