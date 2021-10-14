. ".\Utils\HelperFunctions.ps1"
. ".\Utils\AwsResourceCreator"
. ".\Utils\CommonAwsPolicies.ps1"
. ".\Utils\AwsPoliciesUpdate"

$logsType = Read-Host 'Please insert the logs type (VPC, CloudTrail, GuardDuty)'

switch ($logsType)
{
    "VPC" {.\ConfigVpcFlowDataConnector.ps1; Break}
    "CloudTrail" {.\ConfigCloudTrailDataConnector.ps1 ; Break }
    "GuardDuty" {.\ConfigGuardDutyDataConnector.ps1 ; Break }
    default {Write-Host "Invalid logs type" -ForegroundColor red; exit}
}

Write-Host -NoNewLine `n`n'Press any key to continue...';
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');