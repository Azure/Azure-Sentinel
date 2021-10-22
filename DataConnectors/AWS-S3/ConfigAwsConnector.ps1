<#
.SYNOPSIS
    This script is used to start the configuration process for all supported AWS S3 logs sources. 

    Log sources currently supported are: VPC flows, CloudTrail, GuardDuty

.PARAMETER LogPath
    Specifies the path to save the script log. If not specified, the current path is used.

.EXAMPLE
    .\Config-AwsConnector.ps1
    Executes the script with defaults

#>
[CmdletBinding()]
param (
    [Parameter()]
    [string]
    $LogPath=(Get-Location).Path
)
# Include helper scripts
. ".\Utils\HelperFunctions.ps1"
. ".\Utils\AwsResourceCreator.ps1"
. ".\Utils\CommonAwsPolicies.ps1"
. ".\Utils\AwsPoliciesUpdate.ps1"

# Verify that the AWS CLI is available
if ($null -eq (Get-Command "aws" -ErrorAction SilentlyContinue)) 
{ 

    Write-Error "The AWS CLI is not available in the path"
    Write-Output "`nPlease install the latest AWS CLI from https://aws.amazon.com/cli/"
    Write-Output "If the CLI is already installed, make sure it is added to the path.`n"
    exit
}

# Setup basic logging
$TimeStamp = Get-Date -Format MMddHHmm 
$LogFileName = '{0}-{1}.csv' -f "AwsS3", $TimeStamp
$LogFileName = Join-Path $LogPath $LogFileName

Write-Log -Message "Starting ConfigAwsConnector at: $(Get-Date)" -LogFileName $LogFileName -Severity Information -LinePadding 2
Write-Log -Message "Log created: $LogFileName" -LogFileName $LogFileName -Severity Information -Indent 2

Write-Log -Message "To begin you will choose the AWS logs to configure." -LogFileName $LogFileName -Severity Information -LinePadding 2
# Choose which type of log to configure
do
{
    try{
        [ValidateSet("VPC","CloudTrail","GuardDuty")]$logsType = Read-ValidatedHost -Prompt "Please enter the AWS log type to configure (VPC, CloudTrail, GuardDuty)"
    }
    catch{}
} until ($?)

switch ($logsType)
{
    "VPC" {.\ConfigVpcFlowDataConnector.ps1; break}
    "CloudTrail" {.\ConfigCloudTrailDataConnector.ps1 ; break }
    "GuardDuty" {.\ConfigGuardDutyDataConnector.ps1 ; break }
    default {Write-Host "Invalid log type" -ForegroundColor red; exit}
}

Write-Host -NoNewLine `n`n'Press any key to continue...'
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')