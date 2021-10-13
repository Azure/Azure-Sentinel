function Get-AwsConfig
{
    Write-Output `n`n'Setting up your AWS environment'
    Write-Output `n'This script creates an Assume Role with minimal permissions to grant Azure Sentinel access to your logs in a designated S3 bucket & SQS of your choice, enable'
    write-Output "${LogsName} Logs, S3 bucket, SQS Queue, and S3 notifications."
    Write-Output `n`n'Please enter AWS configuration:'
    aws configure
}

function Write-TheRequiredDataForTheConnectorDefinition
{
    Write-Output `n`n'Use the values below to configure the Amazon Web Service S3 data connector in the Azure Sentinel portal.'
    Write-Output "Role arn: ${roleArn}"
    Write-Output "Sqs Url: ${sqsUrl}"
}

function New-RetryAction
{
	param(
        [Parameter(Mandatory=$true)][Action]$action
        )
        
    $retryCount = 0
	$numberOfRetries = 3
    do {
            $retryCount++
            $action.Invoke();

            if ($lastexitcode -ne 0)
            {
                Write-Host $Error[0] -ForegroundColor red
				if ($retryCount -lt $numberOfRetries)
				{
					Write-Host `n"please try again"
				}
            }

       } while (($retryCount -lt $numberOfRetries) -and ($lastexitcode -ne 0) )

    if ($lastexitcode -ne 0)
    {
       Write-Host `n`n"The maximum number of retries reached. Please execute the script again" -ForegroundColor red
       exit
    }
}