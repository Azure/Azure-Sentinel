Get-AwsConfig

New-ArnRole
$roleArnObject = aws iam get-role --role-name $roleName
$roleArn = ($roleArnObject | ConvertFrom-Json ).Role.Arn

New-S3Bucket
$callerAccount = (aws sts get-caller-identity | ConvertFrom-Json).Account

Write-Output `n"Listing your account's available VPCs"
aws ec2 --output text --query 'Vpcs[*].{VpcId:VpcId}' describe-vpcs

Write-Output `n'Enabling Flow Logs(default format)'
New-RetryAction({
	$vpcResourceIds = Read-Host 'Please enter Vpc Resource Id[s] (space separated)'
	$vpcTrafficType = Read-Host 'Please enter Traffic Type (ALL, ACCEPT, REJECT - default ALL)'
	if ($vpcTrafficType -ne "ALL" -And $vpcTrafficType -ne "ACCEPT" -And $vpcTrafficType -ne "REJECT") {$vpcTrafficType = "ALL"}
	$vpcName = Read-Host 'Please enter Vpc Name'
	$vpcTagSpecifications = "ResourceType=vpc-flow-log,Tags=[{Key=Name,Value=${vpcName}}]"
	$tempForOutput = aws ec2 create-flow-logs --resource-type VPC --resource-ids $vpcResourceIds.Split(' ') --traffic-type $vpcTrafficType --log-destination-type s3 --log-destination arn:aws:s3:::$bucketName --tag-specifications $vpcTagSpecifications 2>&1
})

New-SQSQueue
$sqsUrl = ((aws sqs get-queue-url --queue-name $sqsName) | ConvertFrom-Json).QueueUrl
$sqsArn =  ((aws sqs get-queue-attributes --queue-url $sqsUrl --attribute-names QueueArn )| ConvertFrom-Json).Attributes.QueueArn

Update-SQSPolicy

Write-Output `n"Attaching S3 read policy to Sentinel's Role."
Write-Output "Changes Role arn: S3 Get and List permissions to '${roleName}' rule"
$s3RequiredPolicy = Get-S3PolicyForRole
Update-S3Policy -RequiredPolicy $s3RequiredPolicy

Enable-S3EventNotification -DefaultEvenNotificationPrefix "AWSLogs/${callerAccount}/vpcflowlogs/"

Write-TheRequiredDataForTheConnectorDefinition