function New-ArnRole
{
   <#
   .SYNOPSIS
        Creates a new role
   #>
   Write-Output "`n`n" 
   Write-Log -Message "Assume role definition" -LogFileName $LogFileName -Severity Information

   Write-Log -Message "Executing Set-RetryAction" -LogFileName $LogFileName -Severity Verbose
    
   Set-RetryAction({

        $script:roleName = Read-ValidatedHost -Prompt 'Please enter role name. If you have already configured an assume role for Azure Sentinel, use the same role name'
        Write-Log " Using role name: $roleName" -LogFileName $LogFileName
        
        # Determine if this role already exists before continuing
        Write-Log "Executing: aws iam get-role --role-name $roleName 2>&1| Out-Null" -LogFileName $LogFileName -Severity Verbose
        aws iam get-role --role-name $roleName 2>&1| Out-Null

        # If there was an error the role does not already exist, so it must be created.
        $isRuleNotExist = $lastexitcode -ne 0
        if ($isRuleNotExist)
        {
            Write-Output "`n`n"
            Write-Log "You must specify the the Azure Sentinel Workspace ID. This is found in the Azure Sentinel portal." -LogFileName $LogFileName
            
            $workspaceId = Read-ValidatedHost -Prompt 'Please enter your Azure Sentinel Workspace ID (External Id)'
            Write-Log " Using Azure Sentinel Workspace ID: $workspaceId" -LogFileName $LogFileName
            Write-Output "`n`n"

            $rolePolicy = Get-RoleArnPolicy -WorkspaceId $workspaceId
            Write-Log "Executing: aws iam create-role --role-name $roleName --assume-role-policy-document $rolePolicy 2>&1" -LogFileName $LogFileName -Severity Verbose
            $tempForOutput = aws iam create-role --role-name $roleName --assume-role-policy-document $rolePolicy 2>&1
            
            # If the role was retrieved then the role was created successfully
            if ($lastexitcode -eq 0)
            {
                Write-Log -Message "${roleName} role created successfully" -LogFileName $LogFileName
            }
        }
    })
}

function New-S3Bucket
{
    <#
   .SYNOPSIS
        Creates a new S3 Bucket
   #>
   
    Write-Output `n`n'S3 bucket definition.'
    Set-RetryAction(
        {

        $script:bucketName = Read-ValidatedHost -Prompt 'Please enter S3 bucket name'
        Write-Log " Using S3 Bucket name: $bucketname" -LogFileName $LogFileName
            
        Write-Log "Executing: aws s3api head-bucket --bucket $bucketName 2>&1" -LogFileName $LogFileName -Severity Verbose
        $headBucketOutput = aws s3api head-bucket --bucket $bucketName 2>&1
            
        $isBucketNotExist = $null -ne $headBucketOutput
        if ($isBucketNotExist)
        {
            while ($bucketRegion -eq "")
            {
                $bucketRegion = Read-Host 'Please enter bucket region'
            }
                
            if ($bucketRegion -eq "us-east-1") # see aws doc https://docs.aws.amazon.com/cli/latest/reference/s3api/create-bucket.html
            {
                $tempForOutput = aws s3api create-bucket --bucket $bucketName 2>&1
            }
            else
            {
                $tempForOutput = aws s3api create-bucket --bucket $bucketName --create-bucket-configuration LocationConstraint=$bucketRegion 2>&1
            }
                
            if ($lastexitcode -eq 0)
            {
                Write-Log "${bucketName} Bucket created successfully" -LogFileName $LogFileName
            }
        }
    })
    Write-Log -Message "Executing: (aws sts get-caller-identity | ConvertFrom-Json).Account" -LogFileName $LogFileName -Severity Verbose
    $callerAccount = (aws sts get-caller-identity | ConvertFrom-Json).Account
    Write-Log -Message $callerAccount -LogFileName $LogFileName -Severity Verbose

}

function New-SQSQueue
{
    Write-Output `n'Creating SQS queue'
    Set-RetryAction({

        $script:sqsName = Read-ValidatedHost 'Please enter Sqs Name'
        Write-Log -Message "Sqs name: $sqsName was entered" -LogFileName $LogFileName -Indent 2
        Write-Log -Message "Executing: aws sqs create-queue --queue-name $sqsName 2>&1" -LogFileName $LogFileName -Severity Verbose
        $tempForOutput = aws sqs create-queue --queue-name $sqsName 2>&1
        Write-Log $tempForOutput -LogFileName $LogFileName -Severity Verbose
    })
}

function Enable-S3EventNotification 
{
    param(
        [Parameter(Mandatory=$true)][string]$DefaultEvenNotificationPrefix
        )
        Write-Log -Message "Enabling S3 event notifications (for *.gz file)" -LogFileName $LogFileName -LinePadding 2
    
    Set-RetryAction({
        $eventNotificationName = ""
        while ($eventNotificationName -eq "")
        {
            $eventNotificationName = Read-ValidatedHost -Prompt 'Please enter the event notifications name'
            Write-Log -Message "Event notification name $eventNotificationName was entered" -LogFileName $LogFileName -Indent 2
        }

        $eventNotificationPrefix = $DefaultEvenNotificationPrefix
      
        $prefixOverrideConfirm = Read-ValidatedHost -Prompt "The default prefix is '${eventNotificationPrefix}'. `nDo you want to override the event notification prefix? [y/n]" -ValidationType Confirm
        if ($prefixOverrideConfirm -eq 'y')
        {
            $eventNotificationPrefix = Read-ValidatedHost 'Please enter the event notifications prefix'
            Write-Log -Message "Event notification prefix $eventNotificationPrefix was entered" -LogFileName $LogFileName -Indent 2
        }

        $newEventConfig = Get-SqsEventNotificationConfig -EventNotificationName $eventNotificationName -EventNotificationPrefix $eventNotificationPrefix -SqsArn $sqsArn

        Write-Log -Message "Executing: aws s3api get-bucket-notification-configuration --bucket $bucketName" -LogFileName $LogFileName -Severity Verbose
        $existingEventConfig = aws s3api get-bucket-notification-configuration --bucket $bucketName

        if ($null -ne $existingEventConfig)
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
        Write-Log -Message "Executing: aws s3api put-bucket-notification-configuration --bucket $bucketName --notification-configuration $updatedEventConfigs 2>&1" -LogFileName $LogFileName -Severity Verbose
        $tempForOutput = aws s3api put-bucket-notification-configuration --bucket $bucketName --notification-configuration $updatedEventConfigs 2>&1
        Write-Log -Message $tempForOutput -LogFileName $LogFileName -Severity Verbose
    })
}

function New-KMS
{
    Write-Log -Message "Kms Definition." -LogFileName $LogFileName -LinePadding 2
    Set-RetryAction({
        $script:kmsAliasName = Read-ValidatedHost -Prompt "Please enter KMS alias name"
        Write-Log -Message "Kms alias name $kmsAliasName was entered" -LogFileName $LogFileName -Indent 2
        Write-Log -Message "Executing: aws kms describe-key --key-id alias/$kmsAliasName 2>&1" -LogFileName $LogFileName -Severity Verbose
        $script:kmsKeyDescription = aws kms describe-key --key-id alias/$kmsAliasName 2>&1
        Write-Log -Message $kmsKeyDescription -LogFileName $LogFileName -Severity Verbose

        $isKmsNotExist = $lastexitcode -ne 0
        if ($isKmsNotExist)
        {
            Write-Log -Message "Executing: aws kms create-key" -LogFileName $LogFileName -Severity Verbose
            $script:kmsKeyDescription = aws kms create-key
            Write-Log -Message $kmsKeyDescription -LogFileName $LogFileName -Severity Verbose
            $kmsKeyId = ($script:kmsKeyDescription | ConvertFrom-Json).KeyMetadata.KeyId
            Write-Log -Message "Executing: ws kms create-alias --alias-name alias/$kmsAliasName --target-key-id $kmsKeyId 2>&1" -LogFileName $LogFileName -Severity Verbose
            $tempForOutput = aws kms create-alias --alias-name alias/$kmsAliasName --target-key-id $kmsKeyId 2>&1
            Write-Log -Message $tempForOutput -LogFileName $LogFileName -Severity Verbose
            
            if ($lastexitcode -eq 0)
            {
                Write-Log -Message "$kmsAliasName created successfully" -LogFileName $LogFileName -Indent 2
            }
        }
    })
}