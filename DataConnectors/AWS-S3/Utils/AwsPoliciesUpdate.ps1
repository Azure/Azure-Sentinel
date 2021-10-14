function Update-SQSPolicy{
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
}

function Update-S3Policy{
    Param
    (
         [Parameter(Mandatory=$true)][string]$RequiredPolicy,
         [Parameter(Mandatory=$false)][string]$CustomMessage
    )
    Write-Output `n"Updating the S3 policy to allow Sentinel read the date."
    Write-Output "Changes: S3 Get and List permissions to '${roleName}' rule"
    if($CustomMessage -ne $null)
    {
        Write-Output $CustomMessage
    }
        
    $currentBucketPolicy = aws s3api get-bucket-policy --bucket $bucketName 2>&1
    $isBucketPolicyExist = $lastexitcode -eq 0
    if($isBucketPolicyExist)
    {	
        $s3RequiredPolicyObject = $s3RequiredPolicy | ConvertFrom-Json 
        $currentBucketPolicyObject = $currentBucketPolicy | ConvertFrom-Json 	
        $currentBucketPolicies = ($currentBucketPolicyObject.Policy) | ConvertFrom-Json 
        
        $s3RequiredPolicyThatNotExistInCurrentPolicy = $s3RequiredPolicyObject.Statement | Where-Object { ($_ | ConvertTo-Json -Depth 5) -notin ($currentBucketPolicies.Statement | ForEach-Object { $_ | ConvertTo-Json  -Depth 5}  )}
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
        $newS3Policy = ($s3RequiredPolicyObject | ConvertTo-Json -Depth 16).Replace('"','\"')
        aws s3api put-bucket-policy --bucket $bucketName --policy $newS3Policy | Out-Null
    }
}

function Update-KmsPolicy{
    Param
    (
         [Parameter(Mandatory=$true)][string]$RequiredPolicy,
         [Parameter(Mandatory=$false)][string]$CustomMessage
    )
    Write-Output `n"Updating the KMS policy to allow Sentinel read the date."
    Write-Output "Changes Role: Kms Encrypt, Decrypt, ReEncrypt*, GenerateDataKey* and DescribeKey  permissions to '${roleName}' rule"
    if($CustomMessage -ne $null)
    {
        Write-Output $CustomMessage
    }

    $currentKmsPolicy = aws kms get-key-policy --policy-name default --key-id $kmsKeyId
    if($currentKmsPolicy -ne $null)
    {
        $kmsRequiredPoliciesObject = $RequiredPolicy | ConvertFrom-Json 
        $currentKmsPolicyObject = $currentKmsPolicy | ConvertFrom-Json 	
        $currentKmsPolicies = ($currentKmsPolicyObject.Policy) | ConvertFrom-Json
        
        $kmsRequiredPoliciesThatNotExistInCurrentPolicy =  $kmsRequiredPoliciesObject.Statement | Where-Object { ($_ | ConvertTo-Json -Depth 5) -notin ($currentKmsPolicies.Statement | ForEach-Object { $_ | ConvertTo-Json -Depth 5}  )}
        if($kmsRequiredPoliciesThatNotExistInCurrentPolicy -ne $null)
        {
            $currentKmsPolicies.Statement += $kmsRequiredPoliciesThatNotExistInCurrentPolicy

            $UpdatedKmsPolicyObject = ($currentKmsPolicies | ConvertTo-Json -Depth 16).Replace('"','\"')
            aws kms put-key-policy --policy-name default --key-id $kmsKeyId --policy $UpdatedKmsPolicyObject | Out-Null
        }
    }
    else
    {
        $newKmsPolicyObject = ($RequiredPolicy | ConvertFrom-Json |  ConvertTo-Json -Depth 16).Replace('"','\"')
        aws kms put-key-policy --policy-name default --key-id $kmsKeyId --policy $newKmsPolicyObject | Out-Null
    }
}