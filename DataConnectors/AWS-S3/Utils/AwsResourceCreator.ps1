function Set-ArnRole{
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
}

function Set-S3Bucket{
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
}

function Set-SQSQueue{
    Write-Output `n'Creating SQS queue'
    Retry-Action({
        $script:sqsName = Read-Host 'Please insert Sqs Name'
        $tempForOutput = aws sqs create-queue --queue-name $sqsName 2>&1
    })
}

function Enable-S3EventNotification{
    Param([Parameter(Mandatory=$true)][string]$DefaultEvenNotificationPrefix)
    Write-Output `n'Enabling S3 Event Notifications (for *.gz file)'
    Retry-Action({
        $eventNotificationName = Read-Host 'Please insert the Event Notifications Name'
        $eventNotificationPrefix = $DefaultEvenNotificationPrefix
        $prefixOverrideConfirm = Read-Host "The Default prefix is '${eventNotificationPrefix}'. `nDo you want to override the event notification prefix? [y/n](n by default)"
        if($prefixOverrideConfirm -eq 'y')
        {
            $eventNotificationPrefix = Read-Host 'Please insert the Event Notifications Prefix'
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
}

function Set-KMS{
    Write-Output `n`n'Kms Definition.'
    Retry-Action({
        $script:kmaAliasName = Read-Host 'Please insert KMS alias Name'
        $script:kmsKeyDescription = aws kms describe-key --key-id alias/$kmaAliasName 2>&1
        $isKmsNotExist = $lastexitcode -ne 0
        if($isKmsNotExist)
        {
            $script:kmsKeyDescription = aws kms create-key
            $kmsKeyId = ($script:kmsKeyDescription | ConvertFrom-Json).KeyMetadata.KeyId
            $tempForOutput = aws kms create-alias --alias-name alias/$kmaAliasName --target-key-id $kmsKeyId 2>&1
            if($lastexitcode -eq 0)
            {
                Write-Host  "${kmaAliasName} Kms was successful created"
            }
        }
    })
}