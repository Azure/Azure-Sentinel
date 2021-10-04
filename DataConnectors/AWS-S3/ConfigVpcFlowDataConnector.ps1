
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

function Get-S3PolicyForRole{
	 $s3PolicyForArn = "{
            'Sid': 'Allow Arn read access S3 bucket',
            'Effect': 'Allow',
            'Principal': {
                'AWS': '${roleArn}'
            },
            'Action': ['s3:Get*','s3:List*'],
            'Resource': 'arn:aws:s3:::${bucketName}/*'
        }"	
	return $s3PolicyForArn.Replace("'",'"')
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
Write-Output 'VPC Flow logs to VPCs of your choice, S3 bucket, SQS Queue, and S3 notifications.'
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



Write-Output `n"Listing your account's available VPCs"
aws ec2 --output text --query 'Vpcs[*].{VpcId:VpcId}' describe-vpcs


Write-Output `n'Enabling Flow Logs(default format)'
Retry-Action({
	$vpcResourceIds = Read-Host 'Please insert Vpc Resource Id[s](space separated)'
	$vpcTrafficType = Read-Host 'Please insert Traffic Type(ALL,ACCEPT,REJECT - default ALL)'
	if($vpcTrafficType -ne "ALL" -And $vpcTrafficType -ne "ACCEPT" -And $vpcTrafficType -ne "REJECT") {$vpcTrafficType = "ALL"}
	$vpcName = Read-Host 'Please insert Vpc Name'
	$vpcTagSpecifications = "ResourceType=vpc-flow-log,Tags=[{Key=Name,Value=${vpcName}}]"
	$tempForOutput = aws ec2 create-flow-logs --resource-type VPC --resource-ids $vpcResourceIds.Split(' ') --traffic-type $vpcTrafficType --log-destination-type s3 --log-destination arn:aws:s3:::$bucketName --tag-specifications $vpcTagSpecifications 2>&1
})

Write-Output `n'Creating SQS queue'
 Retry-Action({
	$script:sqsName = Read-Host 'Please insert Sqs Name'
	$tempForOutput = aws sqs create-queue --queue-name $sqsName 2>&1
 })
$sqsUrl = ((aws sqs get-queue-url --queue-name $sqsName) | ConvertFrom-Json).QueueUrl
$sqsArn =  ((aws sqs get-queue-attributes --queue-url $sqsUrl --attribute-names QueueArn )| ConvertFrom-Json).Attributes.QueueArn


Write-Output `n"Updating the SQS policy to allow S3 notifications, and arn to read/delete/change visibility of SQS messages and get queue url"
Write-Output "Changes S3: SQS SendMessage permission to '${bucketName}' s3 bucket"
Write-Output "Changes Role arn: SQS ChangeMessageVisibility, DeleteMessage, ReceiveMessage and GetQueueUrl permissions to '${roleName}' rule"
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


Write-Output `n"Attaching S3 read policy to Sentinel's Role."
Write-Output "Changes Role arn: S3 Get and List permissions to '${roleName}' rule"
$s3RequiredPolicy = Get-S3PolicyForRole
$currentBucketPolicy = aws s3api get-bucket-policy --bucket $bucketName 2>&1
$isBucketPolicyExist = $lastexitcode -eq 0
if($isBucketPolicyExist)
{	
	$s3RequiredPolicyObject = $s3RequiredPolicy | ConvertFrom-Json 
	$currentBucketPolicyObject = $currentBucketPolicy | ConvertFrom-Json 	
	$currentBucketPolicies = ($currentBucketPolicyObject.Policy) | ConvertFrom-Json 
	 
	$s3RequiredPolicyThatNotExistInCurrentPolicy =  $s3RequiredPolicyObject | Where-Object { ($_ | ConvertTo-Json -Depth 5) -notin ($currentBucketPolicies.Statement | ForEach-Object { $_ | ConvertTo-Json -Depth 5}  )}
	if($s3RequiredPolicyThatNotExistInCurrentPolicy -ne $null)
	{
		$currentBucketPolicies.Statement += $s3RequiredPolicyThatNotExistInCurrentPolicy
		$UpdatedS3Policy = (@{Statement = $currentBucketPolicies.Statement} | ConvertTo-Json -Depth 16).Replace('"','\"')
		aws s3api put-bucket-policy --bucket $bucketName --policy $UpdatedS3Policy | Out-Null
	}
}
else
{
	$s3RequiredPolicyObject = $s3RequiredPolicy | ConvertFrom-Json
	$newS3Policy = (@{Statement = @($s3RequiredPolicyObject)} | ConvertTo-Json -Depth 16).Replace('"','\"')
	aws s3api put-bucket-policy --bucket $bucketName --policy $newS3Policy | Out-Null
}



Write-Output `n'Enabling S3 Event Notifications (for *.gz file)'
Retry-Action({
	$eventNotificationName = Read-Host 'Please insert Vpc Event Notifications Name'
	$eventNotificationPrefix =  "AWSLogs/${callerAccount}/vpcflowlogs/"
	$prefixOverrideConfirm = Read-Host "The Default prefix is '${eventNotificationPrefix}'. `nDo you want to override the event notification prefix? [y/n](n by default)"
	if($prefixOverrideConfirm -eq 'y')
	{
		$eventNotificationPrefix = Read-Host 'Please insert Vpc Event Notifications Prefix'
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

Write-Output `n`n'Please use the below values to setup the Amazon Web Service S3 Connector in the Data Connectors portal.'
Write-Output "Role arn: ${roleArn}"
Write-Output "Sqs Url: ${sqsUrl}"

Write-Host -NoNewLine `n`n'Press any key to continue...';
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');

