# Include helper scripts
. ".\Utils\HelperFunctions.ps1"
. ".\Utils\AwsResourceCreator.ps1"
. ".\Utils\CommonAwsPolicies.ps1"
. ".\Utils\AwsPoliciesUpdate.ps1"

# Verify that the AWS CLI is available
if ($null -eq (Get-Command "aws" -ErrorAction SilentlyContinue)) 
{ 

    Write-Error "The AWS CLI is not available in the path!"
    Write-Output "Please install the latest AWS CLI from https://aws.amazon.com/cli/"
    Write-Output "If the CLI is already installed, make sure it is added to the path."
    exit
}

# Setup basic logging to capture
$TimeStamp = Get-Date -Format yyyyMMdd_HHmmss 
$LogFileName = '{0}_{1}.csv' -f "AWSS3Cfg", $TimeStamp
Write-Log -Message "Starting ConfigAwsConnector at: $(Get-Date)" -LogFileName $LogFileName -Severity Information -LinePadding 2
Write-Log -Message "Creating log $LogFileName" -LogFileName $LogFileName -Severity Information -Indent 2
Write-Log -Message "Starting ConfigAwsConnector at: $(Get-Date)" -LogFileName $LogFileName -Severity Information -LinePadding 1

# Choose which type of log to configure
do
{
    try{
        [ValidateSet("VPC","CloudTrail","GuardDuty")]$logsType = Read-Host 'Please enter the log type to configure (VPC, CloudTrail, GuardDuty)'
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