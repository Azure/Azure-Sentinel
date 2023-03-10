function Update-SQSPolicy
{
    <#
    .SYNOPSIS 
       Update the SQS policy 
    #>
    Write-Log -Message "Updating the SQS policy to allow S3 notifications, and ARN to read/delete/change visibility of SQS messages and get queue url" -LogFileName $LogFileName -LinePadding 2
    Write-Log -Message "Changes S3: SQS SendMessage permission to '${bucketName}' s3 bucket" -LogFileName $LogFileName -Indent 2
    Write-Log -Message "Changes Role ARN: SQS ChangeMessageVisibility, DeleteMessage, ReceiveMessage and GetQueueUrl permissions to '${roleName}' rule" -LogFileName $LogFileName -Indent 2

    $sqsRequiredPolicies = Get-S3AndRuleSQSPolicies -RoleArn $roleArn -SqsArn $sqsArn -BucketName $bucketName
    Write-Log -Message "Executing: aws sqs get-queue-attributes --queue-url $sqsUrl --attribute-names Policy" -LogFileName $LogFileName -Severity Verbose
    $currentSqsPolicy = aws sqs get-queue-attributes --queue-url $sqsUrl --attribute-names Policy

    if ($null -ne $currentSqsPolicy)
    {
        Write-Log -Message $currentSqsPolicy -LogFileName $LogFileName -Severity Verbose
        $sqsRequiredPoliciesObject = $sqsRequiredPolicies | ConvertFrom-Json 
        $currentSqsPolicyObject = $currentSqsPolicy | ConvertFrom-Json 	
        $currentSqsPolicies = ($currentSqsPolicyObject.Attributes.Policy) | ConvertFrom-Json 
        
        $sqsRequiredPoliciesThatNotExistInCurrentPolicy =  $sqsRequiredPoliciesObject.Statement | Where-Object { ($_ | ConvertTo-Json -Depth 5) -notin ($currentSqsPolicies.Statement | ForEach-Object { $_ | ConvertTo-Json -Depth 5}  )}
        if ($null -ne $sqsRequiredPoliciesThatNotExistInCurrentPolicy)
        {
            $currentSqsPolicies.Statement += $sqsRequiredPoliciesThatNotExistInCurrentPolicy

            $UpdatedPolicyValue = ($currentSqsPolicies | ConvertTo-Json -Depth 16  -Compress).Replace('"','\\\"')
            $UpdatedSqsPolicy = ("{'Policy':'${UpdatedPolicyValue}'}").Replace("'",'\"')
            aws sqs set-queue-attributes --queue-url $sqsUrl  --attributes $UpdatedSqsPolicy | Out-Null
        }
    }
    else
    {
        Write-Log -Message "No results returned from: aws sqs get-queue-attributes --queue-url $sqsUrl --attribute-names Policy " -LogFileName $LogFileName -Severity Verbose
        $newSqsPolicyValue = ($sqsRequiredPolicies | ConvertFrom-Json |  ConvertTo-Json -Depth 16  -Compress).Replace('"','\\\"')
        $newSqsPolicyObject = ("{'Policy':'${newSqsPolicyValue}'}").Replace("'",'\"')
        aws sqs set-queue-attributes --queue-url $sqsUrl  --attributes $newSqsPolicyObject | Out-Null
    }
}

function Update-S3Policy
{
    <#
    .SYNOPSIS
        Updates S3 policy to allow Sentinel access to read data.
    
    .PARAMETER RequiredPolicy
        Specifies the policy to customize
    .PARAMETER CustomMessage
        Specifies the message to include in customized policy
    
    #>
    
    param
    (
         [Parameter(Mandatory=$true)][string]$RequiredPolicy,
         [Parameter(Mandatory=$false)][string]$CustomMessage
    )
    Write-Log -Message "Updating the S3 policy to allow Sentinel to read the data." -LogFileName $LogFileName -LinePadding 2
    Write-Log -Message "Changes: S3 Get and List permissions to '${roleName}' rule" -LogFileName $LogFileName

    if ($CustomMessage -ne $null)
    {
        Write-Output $CustomMessage
    }
    
    Write-Log -Message "Executing: aws s3api get-bucket-policy --bucket $bucketName 2>&1" -LogFileName $LogFileName -Severity Verbose
    $currentBucketPolicy = aws s3api get-bucket-policy --bucket $bucketName 2>&1
    $isBucketPolicyExist = $lastexitcode -eq 0
    if ($isBucketPolicyExist)
    {	
        $s3RequiredPolicyObject = $s3RequiredPolicy | ConvertFrom-Json 
        $currentBucketPolicyObject = $currentBucketPolicy | ConvertFrom-Json 	
        $currentBucketPolicies = ($currentBucketPolicyObject.Policy) | ConvertFrom-Json 
        
        $s3RequiredPolicyThatNotExistInCurrentPolicy = $s3RequiredPolicyObject.Statement | Where-Object { ($_ | ConvertTo-Json -Depth 5) -notin ($currentBucketPolicies.Statement | ForEach-Object { $_ | ConvertTo-Json  -Depth 5}  )}
        if ($null -ne $s3RequiredPolicyThatNotExistInCurrentPolicy)
        {
            $currentBucketPolicies.Statement += $s3RequiredPolicyThatNotExistInCurrentPolicy
            $UpdatedS3Policy = (@{Statement = $currentBucketPolicies.Statement} | ConvertTo-Json -Depth 16).Replace('"','\"')
            Write-Log -Message "Executing: aws s3api put-bucket-policy --bucket $bucketName --policy $UpdatedS3Policy | Out-Null" -LogFileName $LogFileName -Severity Verbose
            aws s3api put-bucket-policy --bucket $bucketName --policy $UpdatedS3Policy | Out-Null
        }
    }
    else
    {
        $s3RequiredPolicyObject = $s3RequiredPolicy | ConvertFrom-Json
        $newS3Policy = ($s3RequiredPolicyObject | ConvertTo-Json -Depth 16).Replace('"','\"')
        Write-Log -Message "Executing: aws s3api put-bucket-policy --bucket $bucketName --policy $newS3Policy | Out-Null" -LogFileName $LogFileName -Severity Verbose
        aws s3api put-bucket-policy --bucket $bucketName --policy $newS3Policy | Out-Null
    }
}

function Update-KmsPolicy
{
    <#
    .SYNOPSIS
        Updates Kms policy to allow Sentinel access to read data.
    
    .PARAMETER RequiredPolicy
        Specifies the policy to customize
    .PARAMETER CustomMessage
        Specifies the message to include in customized policy
    
    #>
    param
    (
         [Parameter(Mandatory=$true)][string]$RequiredPolicy,
         [Parameter(Mandatory=$false)][string]$CustomMessage
    )
    Write-Log -Message "Updating KMS policy to allow Sentinel read the data." -LogFileName $LogFileName -LinePadding 1
    Write-Log -Message "Changes Role: Kms Encrypt, Decrypt, ReEncrypt*, GenerateDataKey* and DescribeKey  permissions to '${roleName}' rule" -LogFileName $LogFileName -Indent 2
    
    if ($CustomMessage -ne $null)
    {
        Write-Log -Message $CustomMessage -LogFileName $LogFileName -LinePadding 1
    }

    Write-Log -Message "Executing: aws kms get-key-policy --policy-name default --key-id $kmsKeyId" -LogFileName $LogFileName -Severity Verbose
    $currentKmsPolicy = aws kms get-key-policy --policy-name default --key-id $kmsKeyId
    if ($null -ne $currentKmsPolicy)
    {
        $kmsRequiredPoliciesObject = $RequiredPolicy | ConvertFrom-Json 
        $currentKmsPolicyObject = $currentKmsPolicy | ConvertFrom-Json 	
        $currentKmsPolicies = ($currentKmsPolicyObject.Policy) | ConvertFrom-Json
        
        $kmsRequiredPoliciesThatNotExistInCurrentPolicy =  $kmsRequiredPoliciesObject.Statement | Where-Object { ($_ | ConvertTo-Json -Depth 5) -notin ($currentKmsPolicies.Statement | ForEach-Object { $_ | ConvertTo-Json -Depth 5}  )}
        if ($null -ne $kmsRequiredPoliciesThatNotExistInCurrentPolicy)
        {
            $currentKmsPolicies.Statement += $kmsRequiredPoliciesThatNotExistInCurrentPolicy

            $UpdatedKmsPolicyObject = ($currentKmsPolicies | ConvertTo-Json -Depth 16).Replace('"','\"')
            Write-Log -Message "Executing: aws kms put-key-policy --policy-name default --key-id $kmsKeyId --policy $UpdatedKmsPolicyObject | Out-Null" -LogFileName $LogFileName -Severity Verbose
            aws kms put-key-policy --policy-name default --key-id $kmsKeyId --policy $UpdatedKmsPolicyObject | Out-Null
        }
    }
    else
    {
        $newKmsPolicyObject = ($RequiredPolicy | ConvertFrom-Json |  ConvertTo-Json -Depth 16).Replace('"','\"')
        Write-Log -Message "Executing: aws kms put-key-policy --policy-name default --key-id $kmsKeyId --policy $newKmsPolicyObject | Out-Null" -LogFileName $LogFileName -Severity Verbose
        aws kms put-key-policy --policy-name default --key-id $kmsKeyId --policy $newKmsPolicyObject | Out-Null
    }
}