function New-OidcProvider
{
    <#
    .SYNOPSIS
        Checks if an OIDC provider already exists, gets a list of the approved client IDs, and adds a new client ID if it's not already there.
        if the OIDC provider doesn't exists creates an IAM entity to describe an identity provider (IdP) that supports OpenID Connect (OIDC) provider for Sentinel Application.
    #>

    Write-Log -Message "Checking existing OIDC provider" -LogFileName $LogFileName -Severity Information -LinePadding 2
    Write-Log -Message "Executing Set-RetryAction" -LogFileName $LogFileName -Severity Verbose

    Set-RetryAction({
        
        Write-Log -Message "Executing: aws sts get-caller-identity --query 'Account' --output text" -LogFileName $LogFileName -Severity Verbose
        $CustomerAWSAccountId = aws sts get-caller-identity --query "Account" --output text
        Write-Log -Message $CustomerAWSAccountId -LogFileName $LogFileName -Severity Verbose
         
        Write-Log -Message "Executing: aws iam get-open-id-connect-provider --open-id-connect-provider-arn '$($AwsCloudResource):iam::$($CustomerAWSAccountId):oidc-provider/sts.windows.net/$($SentinelTenantId)/' 2>&1" -LogFileName $LogFileName -Severity Verbose
        $providerInfo = aws iam get-open-id-connect-provider --open-id-connect-provider-arn "$($AwsCloudResource):iam::$($CustomerAWSAccountId):oidc-provider/sts.windows.net/$($SentinelTenantId)/" 2>&1
        Write-Log -Message $providerInfo -LogFileName $LogFileName -Severity Verbose

        # If the provider was retrieved then the provider already exists
        $OIDCProviderExists = $lastexitcode -eq 0
        if ($OIDCProviderExists)
        {
            Write-Log -Message "OIDC provider already exists" -LogFileName $LogFileName -Severity Information -Indent 2

            # Get the list of client IDs
            $clientIds = $providerInfo | ConvertFrom-Json | Select-Object -ExpandProperty ClientIDList
            Write-Log -Message "Approved client IDs: $clientIds" -LogFileName $LogFileName -Severity Information -Indent 2
            # Check if the new client ID is already in the list
            if ($clientIds -contains $SentinelClientId)
            {
                Write-Log -Message "Client ID $SentinelClientId is already approved" -LogFileName $LogFileName -Severity Information -Indent 2
            }
            else
            {
                Write-Log -Message "Adding new client ID $SentinelClientId" -LogFileName $LogFileName -Severity Information -Indent 2
                Write-Log -Message "Executing: aws iam add-client-id-to-open-id-connect-provider --open-id-connect-provider-arn '$($AwsCloudResource):iam::$($CustomerAWSAccountId):oidc-provider/sts.windows.net/$($SentinelTenantId)/' --client-id $SentinelClientId 2>&1" -LogFileName $LogFileName -Severity Verbose
                aws iam add-client-id-to-open-id-connect-provider --open-id-connect-provider-arn "$($AwsCloudResource):iam::$($CustomerAWSAccountId):oidc-provider/sts.windows.net/$($SentinelTenantId)/" --client-id $SentinelClientId 2>&1

                # If the client ID was added then the operation was successful
                if ($lastexitcode -eq 0)
                {
                    Write-Log -Message "Client ID $SentinelClientId added successfully" -LogFileName $LogFileName -Severity Information -Indent 2
                }
            }
        }
        # If the provider doesn't exist
        else
        {
            Write-Log -Message "Creating OpenID Connect provider" -LogFileName $LogFileName -Severity Information -LinePadding 2
            Write-Log -Message "Executing Set-RetryAction" -LogFileName $LogFileName -Severity Verbose
        
            Set-RetryAction({
        
                Write-Log -Message "Executing: aws iam create-open-id-connect-provider --url 'https://sts.windows.net/$($SentinelTenantId)/' --ThumbprintList '626d44e704d1ceabe3bf0d53397464ac8080142c' --client-id-list $SentinelClientId 2>&1" -LogFileName $LogFileName -Severity Verbose
                $tempForOutput = aws iam create-open-id-connect-provider --url "https://sts.windows.net/$($SentinelTenantId)/" --thumbprint-list "626d44e704d1ceabe3bf0d53397464ac8080142c"  --client-id-list $SentinelClientId 2>&1
                Write-Log -Message $tempForOutput -LogFileName $LogFileName -Severity Verbose
        
                # If the provider was created then the operation was successful
                if ($lastexitcode -eq 0)
                {
                    Write-Log -Message "OpenID Connect provider created successfully" -LogFileName $LogFileName -Severity Information -Indent 2
                }
            })
        }
    })
}

function New-ArnRole
{
   <#
   .SYNOPSIS
        Creates a new role
   #>
   Write-Log -Message "Assume role definition" -LogFileName $LogFileName -Severity Information -LinePadding 2
   Write-Log -Message "Executing Set-RetryAction" -LogFileName $LogFileName -Severity Verbose
    
   Set-RetryAction({

        $script:roleName = Read-ValidatedHost -Prompt 'Please enter role name. If you have already configured an assume role for Azure Sentinel, use the same role name'
        
        # Determine if this role already exists before continuing
        Write-Log "Executing: aws iam get-role --role-name $roleName 2>&1| Out-Null" -LogFileName $LogFileName -Severity Verbose
        aws iam get-role --role-name $roleName 2>&1| Out-Null

        # If there was an error the role does not already exist, so it must be created.
        $isRuleNotExist = $lastexitcode -ne 0
        if ($isRuleNotExist)
        {
            $script:roleName = "OIDC_$roleName"
            Write-Log -Message "Using role name: $roleName with OIDC prefix because OpenID Connect authentication is being used." -LogFileName $LogFileName -Severity Information -Indent 2

            Write-Output "`n`n"
            Write-Log "You must specify the the Azure Sentinel Workspace ID. This is found in the Azure Sentinel portal." -LogFileName $LogFileName -Severity Information -LinePadding 1
            
            $workspaceId = Read-ValidatedHost -Prompt "Please enter your Azure Sentinel External ID (Workspace ID)"
            Write-Log "Using Azure Sentinel Workspace ID: $workspaceId" -LogFileName $LogFileName -Severity Information -Indent 2

            $CustomerAWSAccountId = aws sts get-caller-identity --query "Account" --output text
            $rolePolicy = Get-OIDCRoleArnPolicy -WorkspaceId $workspaceId -CustomerAWSAccountId $CustomerAWSAccountId
            # $rolePolicy = Get-RoleArnPolicy -WorkspaceId $workspaceId
            
            Write-Log "Executing: aws iam create-role --role-name $roleName --assume-role-policy-document $rolePolicy --tags $(Get-SentinelTagInJsonFormat) 2>&1" -LogFileName $LogFileName -Severity Verbose
            $tempForOutput = aws iam create-role --role-name $roleName --assume-role-policy-document $rolePolicy --tags [$(Get-SentinelTagInJsonFormat)] 2>&1
            Write-Log -Message $tempForOutput -LogFileName $LogFileName -Severity Verbose
            
            # If the role was retrieved then the role was created successfully
            if ($lastexitcode -eq 0)
            {
                Write-Log -Message "$roleName role created successfully" -LogFileName $LogFileName -Severity Information -Indent 2
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
        
        # Get s3 bucket name from user and clean up based on naming rules see https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-s3-bucket-naming-requirements.html
        
        $script:bucketName = (Read-ValidatedHost -Prompt "Please enter S3 bucket name (between 3 and 63 characters long)" -MaxLength 64 -MinLength 3)

        Write-Log -Message "Using S3 Bucket name: $bucketname" -LogFileName $LogFileName -Indent 2
        
        $regionConfiguration = aws configure get region
        Write-Log -Message "current region configuration: $regionConfiguration" -LogFileName $LogFileName -Severity Verbose

        Write-Log -Message "Executing: aws s3api head-bucket --bucket $bucketName 2>&1" -LogFileName $LogFileName -Severity Verbose
        $headBucketOutput = aws s3api head-bucket --bucket $bucketName 2>&1
        # If there was an error the bucket does not already exist or no permissions.
        Write-Log -Message "output $headBucketOutput 2>&1" -LogFileName $LogFileName -Severity Verbose
        Write-Log -Message "error code $lastexitcode 2>&1" -LogFileName $LogFileName -Severity Verbose
            
        $isBucketNotExist = $lastexitcode -ne 0
        if ($isBucketNotExist)
        {
            $bucketCreationConfirm = Read-ValidatedHost -Prompt "Bucket doesn't exist or you don't have permission to access it, would you like to create a new bucket ? [y/n]" -ValidationType Confirm
            Write-Log -Message "Creating new bucket: $bucketCreationConfirm " -LogFileName $LogFileName -Indent 2 
            
            if ($bucketCreationConfirm -eq 'y')
            {     
                if ($regionConfiguration -eq "us-east-1") # see aws doc https://docs.aws.amazon.com/cli/latest/reference/s3api/create-bucket.html
                {
                    Write-Log -Message "Executing: aws s3api create-bucket --bucket $bucketName 2>&1" -LogFileName $LogFileName -Severity Verbose
                    $tempForOutput = aws s3api create-bucket --bucket $bucketName 2>&1
                    Write-Log -Message $tempForOutput -LogFileName $LogFileName -Severity Verbose
                }
                else
                {
                    Write-Log "Executing: aws s3api create-bucket --bucket $bucketName --create-bucket-configuration LocationConstraint=$regionConfiguration 2>&1" -LogFileName $LogFileName -Severity Verbose
                    $tempForOutput = aws s3api create-bucket --bucket $bucketName --create-bucket-configuration LocationConstraint=$regionConfiguration 2>&1
                    Write-Log -Message $tempForOutput -LogFileName $LogFileName -Severity Verbose
                }
                    
                if ($lastexitcode -eq 0)
                {
                    Write-Log "S3 Bucket $bucketName created successfully" -LogFileName $LogFileName -Indent 2
                    Write-Log "Executing: aws s3api put-bucket-tagging --bucket $bucketName --tagging  ""{\""TagSet\"":[$(Get-SentinelTagInJsonFormat)]}""" -LogFileName $LogFileName -Severity Verbose
                    aws s3api put-bucket-tagging --bucket $bucketName --tagging  "{\""TagSet\"":[$(Get-SentinelTagInJsonFormat)]}"
                }
                elseif($error[0] -Match "InvalidBucketName")
                {
                        Write-Log -Message "Please see AWS bucket name documentation https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-s3-bucket-naming-requirements.html" -LogFileName $LogFileName -Severity Error
                }
            }
            else
            {
                exit
            }
        }
    })
    
    Write-Log -Message "Executing: (aws sts get-caller-identity | ConvertFrom-Json).Account" -LogFileName $LogFileName -Severity Verbose
    $callerAccount = (aws sts get-caller-identity | ConvertFrom-Json).Account
    Write-Log -Message $callerAccount -LogFileName $LogFileName -Severity Verbose

}

function New-SQSQueue
{
   <#
   .SYNOPSIS
        Creates a SQS Queue
   #>
    Write-Log -Message "Creating SQS queue:" -LogFileName $LogFileName -LinePadding 2
    Set-RetryAction({

        $script:sqsName = Read-ValidatedHost -Prompt "Please enter Sqs Name"
        Write-Log -Message "Using Sqs name: $sqsName" -LogFileName $LogFileName -Indent 2

        $sentinelTags =  "{\""$(Get-SentinelTagKey)\"": \""$(Get-SentinelTagValue)\""}"
        Write-Log -Message "Executing: aws sqs create-queue --queue-name $sqsName --tags $sentinelTags 2>&1" -LogFileName $LogFileName -Severity Verbose
        $tempForOutput = aws sqs create-queue --queue-name $sqsName --tags $sentinelTags 2>&1
        Write-Log -Message $tempForOutput -LogFileName $LogFileName -Severity Verbose

        if ($lastexitcode -ne 0 -and $error[0] -Match "QueueAlreadyExists")
        {
            Write-Log -Message "Executing: aws sqs create-queue --queue-name $sqsName 2>&1" -LogFileName $LogFileName -Severity Verbose
            $tempForOutput = aws sqs create-queue --queue-name $sqsName 2>&1
            Write-Log -Message $tempForOutput -LogFileName $LogFileName -Severity Verbose
        }
    })
}

function Enable-S3EventNotification 
{
    <#
   .SYNOPSIS
        Enables S3 event notifications. User may override the default prefix

    .PARAMETER DefaultEventNotificationPrefix
        Specifies the default prefix. The user may override this prefix and specify a new one
   #>
    param(
        [Parameter(Mandatory=$true)][string]$DefaultEventNotificationPrefix,
        [Parameter()][bool]$IsCustomLog
        )
        if($IsCustomLog -eq $true)
        {
            Write-Log -Message "Enabling S3 event notifications" -LogFileName $LogFileName -LinePadding 2
        }
        else
        {
            Write-Log -Message "Enabling S3 event notifications (for *.gz file)" -LogFileName $LogFileName -LinePadding 2
        }

    
    Set-RetryAction({
        $eventNotificationName = ""
        while ($eventNotificationName -eq "")
        {
            $eventNotificationName = Read-ValidatedHost -Prompt 'Please enter the event notifications name'
            Write-Log -Message "Using event notification name: $eventNotificationName" -LogFileName $LogFileName -Indent 2
        }

        $eventNotificationPrefix = $DefaultEventNotificationPrefix

        if($IsCustomLog -ne $true)
        {
            Write-Log -Message "Event notificaion prefix definition, to Limit the notifications to objects with key starting with specified characters." -LogFileName $LogFileName     
            $prefixOverrideConfirm = Read-ValidatedHost -Prompt "The default prefix is '$eventNotificationPrefix'. `n  Do you want to override the event notification prefix? [y/n]" -ValidationType Confirm
            if ($prefixOverrideConfirm -eq 'y')
            {
                $eventNotificationPrefix = Read-ValidatedHost 'Please enter the event notifications prefix'
                Write-Log -Message "Using event notification prefix: $eventNotificationPrefix" -LogFileName $LogFileName -Indent 2
            }
        }


        $newEventConfig = Get-SqsEventNotificationConfig -EventNotificationName $eventNotificationName -EventNotificationPrefix $eventNotificationPrefix -SqsArn $sqsArn -IsCustomLog $IsCustomLog

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
        if ($null -ne $tempForOutput)
        {
            Write-Log -Message $tempForOutput -LogFileName $LogFileName -Severity Verbose
        }
    })

}

function New-KMS
{
    <#
    .SYNOPSIS
        Creates a new Kms
    #>
    Write-Log -Message "Kms definition." -LogFileName $LogFileName -LinePadding 2
    Set-RetryAction({
        $script:kmsAliasName = Read-ValidatedHost -Prompt "Please enter the KMS alias name"
        Write-Log -Message "Using Kms alias name: $kmsAliasName" -LogFileName $LogFileName -Indent 2
        Write-Log -Message "Executing: aws kms describe-key --key-id alias/$kmsAliasName 2>&1" -LogFileName $LogFileName -Severity Verbose
        $script:kmsKeyDescription = aws kms describe-key --key-id alias/$kmsAliasName 2>&1
        Write-Log -Message $kmsKeyDescription -LogFileName $LogFileName -Severity Verbose

        $isKmsNotExist = $lastexitcode -ne 0
        if ($isKmsNotExist)
        {
            $sentinelTag = "{\""TagKey\"": \""$(Get-SentinelTagKey)\"", \""TagValue\"": \""$(Get-SentinelTagValue)\""}"
            Write-Log -Message "Executing: aws kms create-key --tags $sentinelTag" -LogFileName $LogFileName -Severity Verbose    
            $script:kmsKeyDescription = aws kms create-key --tags $sentinelTag          
            Write-Log -Message $kmsKeyDescription -LogFileName $LogFileName -Severity Verbose
            $kmsKeyId = ($script:kmsKeyDescription | ConvertFrom-Json).KeyMetadata.KeyId

            Write-Log -Message "Executing: ws kms create-alias --alias-name alias/$kmsAliasName --target-key-id $kmsKeyId 2>&1" -LogFileName $LogFileName -Severity Verbose
            $tempForOutput = aws kms create-alias --alias-name alias/$kmsAliasName --target-key-id $kmsKeyId 2>&1
            Write-Log -Message "$tempForOutput" -LogFileName $LogFileName -Severity Verbose
            
            if ($lastexitcode -eq 0)
            {

                Write-Log -Message "$kmsAliasName created successfully" -LogFileName $LogFileName -Indent 2
            }
        }
    })
}