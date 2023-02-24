<#
  	THE SCRIPT IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SCRIPT OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.

.SYNOPSIS
    This script is used to start the configuration process for all supported AWS S3 logs sources. 

    Log sources currently supported are: VPC flows, CloudTrail, GuardDuty

.PARAMETER LogPath
    Specifies the path to save the script log. If not specified, the current path is used.

.PARAMETER AwsLogType
    Specifies the Aws log type to configure. Valid options are: "VPC", "CloudTrail", "GuardDuty", "CustomLog"

.EXAMPLE
    .\Config-AwsConnector.ps1
    Executes the script with defaults

#>
[CmdletBinding()]
param (
    [Parameter()]
    [string]
    $LogPath=(Join-Path (Get-Location).Path Logs),
    [Parameter()]
    [ValidateSet("VPC","CloudTrail","GuardDuty", "CloudWatch", "CustomLog")][string]$AwsLogType
)
# Include helper scripts
. ".\Utils\HelperFunctions.ps1"
. ".\Utils\AwsResourceCreator.ps1"
. ".\Utils\CommonAwsPolicies.ps1"
. ".\Utils\AwsPoliciesUpdate.ps1"
. ".\Utils\AwsSentinelTag.ps1"

# Verify that the AWS CLI is available
if ($null -eq (Get-Command "aws" -ErrorAction SilentlyContinue)) 
{ 

    Write-Error "The AWS CLI is not available in the path"
    Write-Output "`nPlease install the latest AWS CLI from https://aws.amazon.com/cli/"
    Write-Output "If the CLI is already installed, make sure it is added to the path.`n"
    exit
}

# Setup basic logging
New-Item -ItemType Directory -Force -Path $LogPath | Out-Null
$TimeStamp = Get-Date -Format MMddHHmm 
$LogFileName = '{0}-{1}.csv' -f "AwsS3", $TimeStamp
$LogFileName = Join-Path $LogPath $LogFileName

Write-Log -Message "Starting ConfigAwsConnector at: $(Get-Date)" -LogFileName $LogFileName -Severity Information -LinePadding 2
Write-Log -Message "Log created: $LogFileName" -LogFileName $LogFileName -Severity Information -Indent 2

Write-Log -Message "To begin you will choose the AWS logs to configure." -LogFileName $LogFileName -Severity Information -LinePadding 2

# If LogType parameter was not specified, prompt the user to choose.
if ($AwsLogType -eq "")
{

    do
    {
        try
        {
            [ValidateSet("VPC","CloudTrail","GuardDuty", "CloudWatch", "CustomLog")]$AwsLogType = Read-ValidatedHost -Prompt "Please enter the AWS log type to configure (VPC, CloudTrail, GuardDuty, CloudWatch, CustomLog)"
        }
        catch{}
    } until ($?)
}

switch ($AwsLogType)
{
    "VPC" {.\ConfigVpcFlowDataConnector.ps1; break}
    "CloudTrail" {.\ConfigCloudTrailDataConnector.ps1 ; break }
    "GuardDuty" {.\ConfigGuardDutyDataConnector.ps1 ; break }
    "CloudWatch" {.\ConfigCloudWatchDataConnector.ps1 ; break }
    "CustomLog" {.\ConfigCustomLogDataConnector.ps1 ; break }
    default {Write-Log -Message "Invalid log type" -LogFileName $LogFileName -Severity Error; exit}
}

Write-Host -NoNewLine `n`n'Press any key to continue...'
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')