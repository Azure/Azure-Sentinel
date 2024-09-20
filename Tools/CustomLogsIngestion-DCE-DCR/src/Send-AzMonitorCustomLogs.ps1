<#
  	THE SCRIPT IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SCRIPT OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.

    .SYNOPSIS
    Sends custom logs to a specific table in Azure Monitor.

    .DESCRIPTION
    Script to send data to a data collection endpoint which is a unique connection point for your subscription.
    The payload sent to Azure Monitor must be in JSON format. A data collection rule is needed in your Azure tenant that understands the format of the source data, potentially filters and transforms it for the target table, and then directs it to a specific table in a specific workspace.
    You can modify the target table and workspace by modifying the data collection rule without any change to the REST API call or source data.

    .PARAMETER LogPath
    Path to the log file or folder to read logs from and send them to Azure Monitor.

    .PARAMETER AADAppId
    Azure Active Directory application to authenticate against the API to send logs to Azure Monitor data collection endpoint.
    This script supports the Client Credential Grant Flow.

    .PARAMETER AADAppSecret
    Secret text to use with the Azure Active Directory application to authenticate against the API for the Client Credential Grant Flow.

    .PARAMETER TenantId
    ID of Tenant

    .PARAMETER DcrImmutableId
    Immutable ID of the data collection rule used to process events flowing to an Azure Monitor data table.

    .PARAMETER DceURI
    Uri of the data collection endpoint used to host the data collection rule.

    .PARAMETER StreamName
    Name of stream to send data to before being procesed and sent to an Azure Monitor data table.

    .EXAMPLE
    PS> Send-AzMonitorCustomLogs -LogPath C:\WinEvents.json -AADAppId 'XXXX' -AADAppSecret 'XXXXXX' -TenantId 'XXXXXX' -DcrImmutableId 'dcr-XXXX' -DceURI 'https://XXXX.westus2-1.ingest.monitor.azure.com' -StreamName 'Custom-WindowsEvent'

    .EXAMPLE
    PS> Send-AzMonitorCustomLogs -LogPath C:\WinEventsFolder\ -AADAppId 'XXXX' -AADAppSecret 'XXXXXX' -TenantId 'XXXXXX' -DcrImmutableId 'dcr-XXXX' -DceURI 'https://XXXX.westus2-1.ingest.monitor.azure.com' -StreamName 'Custom-WindowsEvent'

    .NOTES
    # Author: Roberto Rodriguez (@Cyb3rWard0g)
    # Modified: Sreedhar Ande
    # Last Edit: 5/1/2022
    # License: MIT

    # Reference:
    # https://docs.microsoft.com/azure/azure-monitor/logs/custom-logs-overview
    # https://docs.microsoft.com/azure/azure-monitor/logs/tutorial-custom-logs-api#send-sample-data
    # https://securitytidbits.wordpress.com/2017/04/14/powershell-and-gzip-compression/

    # Custom Logs Limit
    # Maximum size of API call: 1MB for both compressed and uncompressed data
    # Maximum data/minute per DCR: 1 GB for both compressed and uncompressed data. Retry after the duration listed in the Retry-After header in the response.
    # Maximum requests/minute per DCR: 6,000. Retry after the duration listed in the Retry-After header in the response.
#>

param(
    [Parameter(Mandatory=$true)]
        [ValidateScript({
            if( -Not ($_ | Test-Path) ){
                throw "File or folder does not exist"
            }
            return $true
        })]
        [string]$LogPath,

    [Parameter(Mandatory=$true)]
    [string]$TenantId,

    [Parameter(Mandatory=$true)]
    [string]$AADAppId,

    [Parameter(Mandatory=$true)]
    [string]$AADAppSecret,

    [Parameter(Mandatory=$true)]
    [string]$DcrImmutableId,

    [Parameter(Mandatory=$true)]
    [string]$DceURI,

    [Parameter(Mandatory=$true)]
    [string]$StreamName
)

#region HelperFunctions
Function Write-Log {
    <#
    .DESCRIPTION
    Write-Log is used to write information to a log file and to the console.

    .PARAMETER Severity
    parameter specifies the severity of the log message. Values can be: Information, Warning, or Error.
    #>

    [CmdletBinding()]
    param(
        [parameter()]
        [ValidateNotNullOrEmpty()]
        [string]$Message,
        [string]$LogFileName,

        [parameter()]
        [ValidateNotNullOrEmpty()]
        [ValidateSet('Information', 'Warning', 'Error')]
        [string]$Severity = 'Information'
    )
    # Write the message out to the correct channel
    switch ($Severity) {
        "Information" { Write-Host $Message -ForegroundColor Green }
        "Warning" { Write-Host $Message -ForegroundColor Yellow }
        "Error" { Write-Host $Message -ForegroundColor Red }
    }
    try {
        [PSCustomObject] [ordered] @{
            Time     = (Get-Date -f g)
            Message  = $Message
            Severity = $Severity
        } | Export-Csv -Path "$PSScriptRoot\$LogFileName" -Append -NoTypeInformation -Force
    }
    catch {
        Write-Error "An error occurred in Write-Log() method" -ErrorAction SilentlyContinue
    }
}

#endregion

#region MainFunction
Function Get-BearerToken {
    Try {
        Add-Type -AssemblyName System.Web
        Write-Log -Message "Obtaining Access Token" -LogFileName $LogFileName -Severity Information
        $scope = [System.Web.HttpUtility]::UrlEncode("https://monitor.azure.com//.default")
        $body = "client_id=$AADAppId&scope=$scope&client_secret=$AADAppSecret&grant_type=client_credentials";
        $headers = @{"Content-Type" = "application/x-www-form-urlencoded"};
        $uri = "https://login.microsoftonline.com/$TenantID/oauth2/v2.0/token"
        $bearerToken = (Invoke-RestMethod -Uri $uri -Method "POST" -Body $body -Headers $headers).access_token

        return $bearerToken
    }
    catch {
        Write-Log -Message "Error occured in Obtain-Token :$($_)" -LogFileName $LogFileName -Severity Error
        exit
    }
}

Function Send-DataToDCE {
    [CmdletBinding()]
    param (
        [parameter(Mandatory = $true)] $JsonPayload,
        [parameter(Mandatory = $true)] $AccessToken,
		[parameter(Mandatory = $true)] $DceURI,
        [parameter(Mandatory = $true)] $DcrImmutableId,
        [parameter(Mandatory = $true)] $StreamName,
		[parameter(Mandatory = $true)] $ApiVersion
    )

    # Initialize Headers and URI for POST request to the Data Collection Endpoint (DCE)
    $headers = @{"Authorization" = "Bearer $AccessToken"; "Content-Type" = "application/json"}
    $uri = "$DceURI/dataCollectionRules/$DcrImmutableId/streams/$StreamName`?api-version=$ApiVersion"

    Try {
        # Sending data to Data Collection Endpoint (DCE) -> Data Collection Rule (DCR) -> Azure Monitor table
        $IngestionStatus = Invoke-RestMethod -Uri $uri -Method "POST" -Body $JsonPayload -Headers $headers -verbose
        Write-Log -Message "Status : $IngestionStatus" -LogFileName $LogFileName -Severity Information
    }
    catch {
        Write-Log -Message "Error occured in Send-DataToDCE :$($_)" -LogFileName $LogFileName -Severity Error
    }
}
#endregion

#region DriverProgram

# Check Powershell version, needs to be 5 or higher
if ($host.Version.Major -lt 5) {
    Write-Log -Message "Supported PowerShell version for this script is 5 or above" -LogFileName $LogFileName -Severity Error
    exit
}

$ApiVersion = "2021-11-01-preview"

$TimeStamp = Get-Date -Format yyyyMMdd_HHmmss
$LogFileName = '{0}_{1}.csv' -f "CustomlogsIngestion", $TimeStamp


##################
### Step 1: Path to the log file or folder to read logs from and send them to Azure Monitor
##################

$all_datasets = @()
foreach ($file in $LogPath){
    if ((Get-Item $file) -is [system.io.fileinfo]){
        $all_datasets += (Resolve-Path -Path $file)
    }
    elseif ((Get-Item $file) -is [System.IO.DirectoryInfo]){
        $folderfiles = Get-ChildItem -Path $file -Recurse -Include *.json,*.csv
        $all_datasets += $folderfiles
    }
}

##################
### Step 2: Obtain a bearer token used later to authenticate against the DCE
##################
$bearerToken = Get-BearerToken

foreach ($dataset in $all_datasets){
    $extn = [IO.Path]::GetExtension($dataset)
    if ($extn -ieq ".csv") {
        $json_records = Get-Content $dataset | ConvertFrom-Csv | ConvertTo-Json
        $json_payload= $json_records | Convertfrom-json | ConvertTo-Json
    }
    else {
        $json_records = Get-Content $dataset
        $json_payload= $json_records | Convertfrom-json | ConvertTo-Json
    }

    $payload_size = ([System.Text.Encoding]::UTF8.GetBytes($json_payload).Length)
    If ($payload_size -le 1mb) {
        Write-Log -Message "Sending log events with size $dataset_size" -LogFileName $LogFileName -Severity Information
        Send-DataToDCE -JsonPayload $json_payload -AccessToken $bearerToken -DceURI $DceURI -DcrImmutableId $DcrImmutableId -StreamName $StreamName -ApiVersion $ApiVersion
    }
    else {
        # Maximum size of API call: 1MB for both compressed and uncompressed data
        Write-Log -Message "Log size is greater than APILimitBytes" -LogFileName $LogFileName -Severity Error
    }

}
#endregion