function Test-AwsConfiguration
{
    <#
    .SYNOPSIS
        This function executes "aws configure" to ensure it is connected for subsequent commands.
    #>

    Write-Log -Message "Checking AWS CLI configuration..." -LogFileName $LogFileName -Severity Information -LinePadding 1

    # validate aws configuration. in case of invalid region\credentials the following command will trow exception
     aws ec2 describe-regions 2>&1 | Out-Null

     if ($lastExitCode -ne 0 )
     {
        Write-Log -Message $error[0] -LogFileName $LogFileName -Severity Error
        Write-Log -Message "Please execute again 'aws configure' and verify that AWS configuration is correct." -LogFileName $LogFileName -Severity Error
        Write-Log -Message "For more details please see AWS doc https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html" -LogFileName $LogFileName -Severity Error               
        exit
     }
}

function Write-RequiredConnectorDefinitionInfo
{
    <#
    .SYNOPSIS
        Write data needed to configure the Azure Sentinel Data Connector for user.
    .PARAMETER DestinationTable
        Specifies the connector destination table
    #>
    param(
        [Parameter(Mandatory=$false,Position=0)][string]$DestinationTable
    )
    Write-Log -Message "Use the values below to configure the Amazon Web Service S3 data connector in the Azure Sentinel portal." -LogFileName $LogFileName -Severity Information -LinePadding 3
    Write-Log -Message "Role Arn: $roleArn" -LogFileName $LogFileName -Severity Information -LinePadding 1
    Write-Log -Message "Sqs Url: $sqsUrl" -LogFileName $LogFileName -Severity Information
    if ($DestinationTable -ne "")
    {
        Write-Log -Message "Destination Table: $DestinationTable" -LogFileName $LogFileName -Severity Information
    }
}

function Write-ScriptNotes
{
    Write-Log -Message "Notes:" -LogFileName $LogFileName -Severity Information -LinePadding 1 -Indent 2 -Color DarkYellow
    Write-Log -Message "* You can find more information about the script in https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/AWS-S3/README.md" -LogFileName $LogFileName -Severity Information -Indent 2 -Color DarkYellow
    Write-Log -Message "* If a resource name(like: S3, Sqs, Kms) already exists, the script will use the available one and not create a new resource" -LogFileName $LogFileName -Severity Information -Indent 2 -Color DarkYellow
}

function Set-RetryAction
{
	<#
    .SYNOPSIS
        Main worker function to try and retry configuration steps
        
    .PARAMETER Action
        Specifies the action to execute
    
    .PARAMETER MaxRetries
        Specifies the maximum number of times to retry the action. The default is 3.
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
					Start-Sleep 5
                    Write-Log -Message "Retrying..." -LogFileName $LogFileName -Severity Information
				}
            }

       } while (($retryCount -lt $MaxRetries) -and ($lastExitCode -ne 0) )

    if ($lastExitCode -ne 0)
    {
       Write-Log -Message "Action was unsuccessful after $MaxRetries attempts. Please review the errors and try again." -LogFileName $LogFileName -Severity Error
       exit
    }
}

function Read-ValidatedHost
{
<#
.SYNOPSIS
    Gets validated user input and ensures that it is not empty. It will continue to prompt until valid text is provided.
    Th 
.PARAMETER Prompt
    Text that will be displayed to user
.PARAMETER ValidationType
    Specify 'NotNull' to check for a non-null response and 'Confirm' to make sure the response is Y/Yes or N/No.
.PARAMETER MinLength
    Specifies the minimum number of characters the input value can be. The default is 1.
.PARAMETER MaxLength
    Specifies the maximum number of characters the input value can be. The default is 1024.
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
    $MinLength = 1,
    $MaxLength = 1024
)
    # Add a blank line before the prompt
    Write-Host ""
    $returnString = ""
    if ($ValidationType -eq "NotNull")
    {

        do
        {
            $returnString = Read-Host -Prompt $Prompt

        } while (($returnString -eq "") -or ($returnString.Length -lt $MinLength) -or ($returnString.Length -gt $MaxLength))
             
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
        Write-Log is used to write information to a log file and to the console. It provides basic formatting capabilities.
        
    
    .PARAMETER Severity
        Specifies the severity of the log message. Values can be: Information, Warning, Error, Verbose, or LogOnly. 
    .PARAMETER Padding
        Specifies the number of empty rows to add before message in the console. This does not apply to the log on disk.
    .PARAMETER Indent
        Specified the number of characters to indent the message in the console. This does not apply to the log on disk.
    .PARAMETER Color
        Specified the color of the text for information severity.

    .EXAMPLE
        Write-Log -Message "Starting script" -LogFileName C:\temp\TestLog1.csv -Severity Information
        Basic usage to write a message to the log and to the console.
    .EXAMPLE
        Write-Log -Message "Starting script" -LogFileName C:\temp\TestLog1.csv -Severity Information -LinePadding 2
        Write a message to the log and two blank lines before writing it to the console.
    .EXAMPLE
        Write-Log -Message "Starting script" -LogFileName C:\temp\TestLog1.csv -Severity Information -Indent 2
        Write a message to the log and the indenting the provided message two spaces on the console.
    .EXAMPLE
        Write-Log -Message "Error $Error[0]" -LogFileName C:\temp\TestLog1.csv -Severity Error -Indent 2
        Write the last error message to the log and to the error output channel.
    .EXAMPLE
        Write-Log -Message "Detailed debugging text that most people do not want to see in the console" -LogFileName C:\temp\TestLog1.csv -Severity Verbose -Indent 2
        Write the message to the verbose channel and to the log. Users would only see this in the console if they have enabled Verbose messaging.
    .EXAMPLE
        Write-Log -Message "Text to only send to the log" -LogFileName C:\temp\TestLog1.csv -Severity Verbose -Indent 2
        Write the text only to the log and not to the console.    
    #>

    [OutputType([System.Void])]
    [CmdletBinding()]
    param(
        [parameter(Mandatory=$true,Position=0)]
        $Message,
        [parameter(Mandatory=$true,Position=1)]
        [string]$LogFileName,
         [parameter(Mandatory=$false)]
        [ValidateSet('Information', 'Warning', 'Error', 'Verbose','LogOnly')]
        [string]$Severity = 'Information',
        [parameter(Mandatory=$false)]
        [int]$LinePadding = 0,
        [parameter(Mandatory=$false)]
        [int]$Indent = 0,
        [parameter(Mandatory=$false)]
        [ConsoleColor]$Color = "White"
    )

    # If data is passed in that is not a string, instead of generating an error, just convert it to string.
    $Message = "$Message"

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
        } | Export-Csv -Path $LogFileName -Append -NoTypeInformation -Force
    }
    catch 
    {
        Write-Error "An error occurred writing log to disk"		
    }    

    # Add specified indentation to the message before it is displayed
    if ($Indent -gt 0)
    {
        for ($i = 0; $i -lt $Indent; $i++) {
            $Message = " $Message"
        }
    }

    # Write the message to the correct output channel											  
    switch ($Severity) {
        "Information" { Write-Host $Message -ForegroundColor $Color }
        "Warning" { Write-Warning $Message }
        "Error" { Write-Host $Message -ForegroundColor Red }
        "Verbose" {Write-Verbose $Message }
        "LogOnly" {} # No console output
        default {}
    }
}