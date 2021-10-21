function Get-AwsConfig
{
    <#
    .SYNOPSIS
        This function executes "aws configure" to ensure it is connected for subsequent commands.
    #>

    Write-Log -Message "Setting up your AWS CLI environment..." -LogFileName $LogFileName -Severity Information
    Write-Output `n`n'Please ensure that the AWS CLI is connected:'
    Write-Log -Message "Executing aws configure" -LogFileName $LogFileName -Severity Verbose

    aws configure
}

function Write-RequiredConnectorDefinitionInfo
{
    Write-Log -Message "Use the values below to configure the Amazon Web Service S3 data connector in the Azure Sentinel portal." -LogFileName $LogFileName -Severity Information
    Write-Log -Message "Role arn: ${roleArn}" -LogFileName $LogFileName -Severity Information
    Write-Log -Message "Sqs Url: ${sqsUrl}" -LogFileName $LogFileName -Severity Information
}

function Set-RetryAction
{
	<#
    .SYNOPSIS
        Main worker function to try and retry configuration steps 
    #>
    param(
        [Parameter(Mandatory=$true,Position=0)][Action]$Action,
        [Parameter(Mandatory=$false)][int]$MaxRetries = 3

        )
        
    $retryCount = 0
	
    do {
            $retryCount++
            $Action.Invoke();

            if ($lastExitCode -ne 0)
            {
                Write-Log -Message $error[0] -LogFileName $LogFileName -Severity Error
				if ($retryCount -lt $maxRetries)
				{
					Start-Sleep 10
                    Write-Log -Message "Retrying..." -LogFileName $LogFileName -Severity Information
				}
            }

       } while (($retryCount -lt $MaxRetries) -and ($lastExitCode -ne 0) )

    if ($lastExitCode -ne 0)
    {
       Write-Log -Message "We have tried the maximum number of times ($MaxRetries). Please review the errors and try again. " -LogFileName $LogFileName -Severity Error
       exit
    }
}


function Read-ValidatedHost
{
<#
.SYNOPSIS
    Gets validated user input and ensures that it is not empty. It will continue to prompt until non-empty text is provided
.PARAMETER Prompt
    Text that will be displayed to user
.PARAMETER ValidationType
    Specify whether to ensure a non-null response of that the response is Yes or No.
    
#>
[OutputType([string])]
[CmdletBinding()]
param (
    [Parameter(Mandatory=$true,Position=0)]
    [string]
    $Prompt,
    [ValidateSet("NotNull","Confirm")]
    [Parameter(Mandatory=$false,Position=1)]
    [string]
    $ValidationType="NotNull",
    [Parameter(Mandatory=$false)]
    [string()]
    $ValidationSet
)

    if ($ValidationType -eq "NotNull")
    {
        do
        {
            try
            {
                [ValidateNotNullOrEmpty]$returnString = Read-Host -Prompt $Prompt
            } 
            catch {}
        } until ($?)

        return $returnString
    }
    elseif ($ValidationType -eq "Confirm")
    {
        do
        {
            try
            {
                [ValidateSet("Y","Yes","N","No")]$returnString = Read-Host -Prompt $Prompt
            } 
            catch {}
        } until ($?)

        if (($returnString -eq "Yes") -or ($returnString -eq "Y"))
        {
            $returnString = "y"
        }
        else
        {
            $returnString = "n"
        } 
        
        return $returnString

    }
    else{
        return ""
    
    }
}

function Write-Log 
{
    <#
    .DESCRIPTION 
    Write-Log is used to write information to a log file and to the console. This provides basic formatting capabilities.
    
    .PARAMETER Severity
        Specifies the severity of the log message. Values can be: Information, Warning, Error, Verbose, or LogOnly. 
    .PARAMETER Padding
        Specifies the number of empty rows to add before message on screen. This does not apply to the log on disk.
    .PARAMETER Indent
        Specified the number of characters to indent the message on screen. This does not apply to the log on disk.
    #>

    [OutputType([System.Void])]
    [CmdletBinding()]
    param(
        [parameter(Mandatory=$true,Position=0)]
        [ValidateNotNullOrEmpty()]
        [string]$Message,
        [parameter(Mandatory=$true,Position=1)]
        [string]$LogFileName,
         [parameter(Mandatory=$false,Position=2)]
        [ValidateNotNullOrEmpty()]
        [ValidateSet('Information', 'Warning', 'Error', 'Verbose','LogOnly')]
        [string]$Severity = 'Information',
        [parameter(Mandatory=$false)]
        [int]$LinePadding = 0,
        [parameter(Mandatory=$false)]
        [int]$Indent = 0
    )

    # Write the appropriate number of empty lines to the screen
    if ($LinePadding -gt 0)
    {
        for ($i = 0; $i -lt $LinePadding; $i++)
        {
            Write-Host ""
        }
    }
											  
    try 
    {
        [PSCustomObject]@{
            Time     = (Get-Date -f g)
            Message  = $Message
            Severity = $Severity
        } | Export-Csv -Path "$PSScriptRoot\$LogFileName" -Append -NoTypeInformation -Force
    }
    catch 
    {
        Write-Error "An error occurred writing log to disk"		
    }    

    # Add specified indentation to the message before it is displayed
    if ($Indent -gt 0)
    {
        for ($i = 0; $i -lt $padding; $i++) {
            $Message = " $Message"
        }
    }

    # Write the message out to the correct channel											  
    switch ($Severity) {
        "Information" { Write-Output $Message }
        "Warning" { Write-Warning $Message }
        "Error" { Write-Error $Message }
        "Verbose" {Write-Verbose $Message }
    } 

}