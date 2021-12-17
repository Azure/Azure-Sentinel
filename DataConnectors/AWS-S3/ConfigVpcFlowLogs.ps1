# Include helper scripts
. ".\Utils\HelperFunctions.ps1"
. ".\Utils\AwsSentinelTag.ps1"

# Validate AWS configuration
Test-AwsConfiguration

Write-Output `n`n'Setting up your AWS environment'
Write-Output `n'This script enables additional VPC Flow Logs if you have already set up the required resources Bucket S3, SQS etc.'

Write-Output `n`n'S3 Bucket definition'

$bucketName = Read-ValidatedHost 'S3 bucket name'
Write-Output "Using S3 Bucket name: $bucketName"

Write-Output `n"Listing your available VPCs"
aws ec2 --output text --query 'Vpcs[*].{VpcId:VpcId}' describe-vpcs

Write-Output `n'Enabling Flow Logs (default format), please enter VPC Resource Id[s]'
$vpcResourceId = Read-ValidatedHost 'Vpc Resource Id[s] (space separated)'

do
{
    try
    {
    [ValidateSet("ALL","ACCEPT","REJECT")]$vpcTrafficType = Read-Host 'Please enter traffic type (ALL, ACCEPT, REJECT)'
    }
catch {}
} until ($?)

$vpcName = Read-ValidatedHost 'Vpc Name:'
Write-Output " Using Vpc name: $vpcname"

$vpcTagSpecifications = "ResourceType=vpc-flow-log,Tags=[{Key=Name,Value=$vpcName}, {Key=$(Get-SentinelTagKey),Value=$(Get-SentinelTagValue)}]"

# creating the VPC Flow logs with specified info
aws ec2 create-flow-logs --resource-type VPC --resource-ids $vpcResourceId.Split(' ') --traffic-type $vpcTrafficType.ToUpper() --log-destination-type s3 --log-destination arn:aws:s3:::$bucketName --tag-specifications $vpcTagSpecifications | Out-Null
