function Get-AwsConfig
{
    <#
    .SYNOPSIS
        This function executes "aws configure" to ensure it is connected for subsequent commands.
    #>
    Write-Output `n`n'Setting up your AWS CLI environment...'
    Write-Output `n`n'Please ensure that the AWS CLI is connected:'
    aws configure
}

function Write-RequiredConnectorDefinitionInfo
{
    Write-Output `n`n'Use the values below to configure the Amazon Web Service S3 data connector in the Azure Sentinel portal.'
    Write-Output "Role arn: ${roleArn}"
    Write-Output "Sqs Url: ${sqsUrl}"
}

function Set-RetryAction
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