Write-Output `n`n'Setting up your AWS environment'
Write-Output `n'The script enables additional VPC Flow Logs (if you have already set up the required resources Bucket S3, SQS etc.)'
aws configure

Write-Output `n`n'S3 Bucket Definition'
$bucketName = Read-Host 'S3 Bucket Name'

Write-Output `n"Listing your account's availble VPCs"
aws ec2 --output text --query 'Vpcs[*].{VpcId:VpcId}' describe-vpcs

Write-Output `n'Enabling Flow Logs(default format), please enter VPC Resource Id[s]'
$vpcResourceId = Read-Host 'Vpc Resource Id[s](space separated)'
$vpcTrafficType = Read-Host 'Traffic Type(ALL,ACCEPT,REJECT - default ALL)'
if($vpcTrafficType -ne "ALL" -And $vpcTrafficType -ne "ACCEPT" -And $vpcTrafficType -ne "REJECT") {$vpcTrafficType = "ALL"}
$vpcName = Read-Host 'Vpc Name'
$vpcTagSpecifications = "ResourceType=vpc-flow-log,Tags=[{Key=Name,Value=${vpcName}}]"
aws ec2 create-flow-logs --resource-type VPC --resource-ids $vpcResourceId.Split(' ') --traffic-type $vpcTrafficType --log-destination-type s3 --log-destination arn:aws:s3:::$bucketName --tag-specifications $vpcTagSpecifications | Out-Null
