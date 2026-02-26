# Input bindings are passed in via param block.
param($Timer)
#Requires -Modules @{ModuleName='AWS.Tools.Common';ModuleVersion='4.1.14'}
#Requires -Modules @{ModuleName='AWS.Tools.S3';ModuleVersion='4.1.14'}
# Get the current universal time in the default string format
$currentUTCtime = (Get-Date).ToUniversalTime()

# The 'IsPastDue' porperty is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}
[int]$maxdurationminutes=10
$script_start_time=([System.DateTime]::UtcNow)
# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"
<#
.SYNOPSIS
#

.DESCRIPTION
Long description

.EXAMPLE
An example

.NOTES
General notes
#>
function getCheckpoint()
{
$azstoragestring = $Env:WEBSITE_CONTENTAZUREFILECONNECTIONSTRING
$Context = New-AzStorageContext -ConnectionString $azstoragestring
if((Get-AzStorageContainer -Context $Context).Name -contains "lastalertlog"){
    #Set Container
    $Blob = Get-AzStorageBlob -Context $Context -Container (Get-AzStorageContainer -Name "lastalertlog" -Context $Context).Name -Blob "lastalertlog.log"
    $lastlogTime = $blob.ICloudBlob.DownloadText()
    $startTime = $lastlogTime | Get-Date -Format yyyy-MM-ddTHH:mm:ss
    return $startTime
}

}
<#
.SYNOPSIS
Short description

.DESCRIPTION
Long description

.EXAMPLE
An example

.NOTES
General notes
#>
function GenerateDate()
{
    
    $time= [int]$Env:timeInterval
    $startTime=getCheckpoint
    if($null -ne $startTime)
    {
       $startTime = Get-Date -Date $startTime
       #$startTime=$startTime.ToUniversalTime()
    }

    if($null -ne $startTime)
    {
        Write-Host "The last start time in file share is" $startTime
    }
    else {
        $startTime = [System.DateTime]::UtcNow.AddMinutes(-$($time))
    }

    $now = [System.DateTime]::UtcNow
    #$Duration = New-TimeSpan -Start $startTime -End $now()
    if($startTime -le $now)
    {
        [int]$noofmins = $($now-$startTime).TotalMinutes
    }
    else {
        Write-Host "Start time is greater than current time,Please check the start time and correct it."
    }
    if($noofmins -gt $time)
    {
        if($null -ne $startTime)
        {
          $now=$startTime.AddMinutes($time)
        }
        Write-Host "The no of mins b/w start and end time is greater than $time"
    }
    Write-Host "The now time is" $now

    return $startTime, $now
}
function CarbonBlackAPI() {
    $workspaceId = $env:workspaceId
    $workspaceSharedKey = $env:workspaceKey
    $hostName = $env:uri
    $apiSecretKey = $env:apiKey
    $logType = $env:CarbonBlackLogTypes
    $apiId = $env:apiId
    $SIEMapiKey = $env:SIEMapiKey
    $SIEMapiId = $env:SIEMapiId
    $time = $env:timeInterval
    $AuditLogTable = "CarbonBlackAuditLogs"
    $EventLogTable = "CarbonBlackEvents"
    $NotificationTable = "CarbonBlackNotifications"
    $AlertsTable="CarbonBlackAlerts"
    $OrgKey = $env:CarbonBlackOrgKey
    $s3BucketName = $env:s3BucketName
    $EventprefixFolder = $env:EventPrefixFolderName
    $AlertprefixFolder = $env:AlertPrefixFolderName
    $AWSAccessKeyId = $env:AWSAccessKeyId
    $AWSSecretAccessKey = $env:AWSSecretAccessKey
    $Severity = $env:Severity


    # Remove if addition slash or space added in hostName
    $hostName = $hostName.Trim() -replace "[.*/]$", ""

    if ([string]::IsNullOrEmpty($logAnalyticsUri)) {
        $logAnalyticsUri = "https://" + $workspaceId + ".ods.opinsights.azure.com"
    }

    # Returning if the Log Analytics Uri is in incorrect format.
    # Sample format supported: https://" + $customerId + ".ods.opinsights.azure.com
    if ($logAnalyticsUri -notmatch 'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$') {
        throw "VMware Carbon Black: Invalid Log Analytics Uri."
    }

    $authHeaders = @{
        "X-Auth-Token" = "$($apiSecretKey)/$($apiId)"
    }
    
    #Converting LogType to array
    if ([string]::IsNullOrWhiteSpace($logType)) {
        if ($SIEMapiKey -eq '<Optional>' -or $SIEMapiId -eq '<Optional>' -or [string]::IsNullOrWhitespace($SIEMapiKey) -or [string]::IsNullOrWhitespace($SIEMapiId)) {
            $LogTypeArr = @("event", "audit")
        }
        else {
            $LogTypeArr = @("event", "audit", "alertSIEMAPI")
        }
    }
    else {
        if ($logType -like "``[*``]") {
            $logType = $logType.Substring(1, $logType.Length - 2)
        }
        $logType = $logType -replace """", ""
        $LogTypeArr = $logType -split ','
    }
    if ($LogTypeArr -contains "alertSIEMAPI" -or $LogTypeArr -contains "alertAWSS3") {
        if (-not([string]::IsNullOrWhiteSpace($SIEMapiKey)) -and -not([string]::IsNullOrWhiteSpace($SIEMapiId))) {
           CarbonBlackAlertsAPI 
        }
        else {
            Write-Warning "No SIEM API ID and/or Key or S3Bucket value was defined, therefore alert logs will not to ingested to workspace."
        }
    }
    else {
        Write-Warning "'Alert' was not selected as a LogType, therefore alert logs will not be ingested to the workspace."
    } 
}

# Create the function to create the authorization signature
function Build-Signature ($customerId, $sharedKey, $date, $contentLength, $method, $contentType, $resource) {
    $xHeaders = "x-ms-date:" + $date;
    $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $resource;
    $bytesToHash = [Text.Encoding]::UTF8.GetBytes($stringToHash);
    $keyBytes = [Convert]::FromBase64String($sharedKey);
    $sha256 = New-Object System.Security.Cryptography.HMACSHA256;
    $sha256.Key = $keyBytes;
    $calculatedHash = $sha256.ComputeHash($bytesToHash);
    $encodedHash = [Convert]::ToBase64String($calculatedHash);
    $authorization = 'SharedKey {0}:{1}' -f $customerId, $encodedHash;
    return $authorization;
}

# Create the function to create and post the request
function Post-LogAnalyticsData($customerId, $sharedKey, $body, $logType) {
    $TimeStampField = "eventTime"
    $method = "POST";
    $contentType = "application/json";
    $resource = "/api/logs";
    $rfc1123date = [DateTime]::UtcNow.ToString("r");
    $contentLength = $body.Length;
    $signature = Build-Signature -customerId $customerId -sharedKey $sharedKey -date $rfc1123date -contentLength $contentLength -method $method -contentType $contentType -resource $resource;
    $logAnalyticsUri = $logAnalyticsUri + $resource + "?api-version=2016-04-01"
    $headers = @{
        "Authorization"        = $signature;
        "Log-Type"             = $logType;
        "x-ms-date"            = $rfc1123date;
        "time-generated-field" = $TimeStampField;
    };
    $response = Invoke-WebRequest -Body $body -Uri $logAnalyticsUri -Method $method -ContentType $contentType -Headers $headers -UseBasicParsing
    return $response.StatusCode
}
<#
.SYNOPSIS
##

.DESCRIPTION
Long description

.PARAMETER percentage
Parameter description

.PARAMETER script_start_time
Parameter description

.EXAMPLE
An example

.NOTES
General notes
#>
function check_if_script_runs_too_long($percentage, $script_start_time)
{
 [int]$seconds=(60)
 [int]$duration = $(([System.DateTime]::UtcNow - $script_start_time).Seconds)
 [int]$temp=$maxdurationminutes * $seconds 
 [double]$maxduration= $temp * 0.8
 return $duration -gt $maxduration
}
<#
.SYNOPSIS
Short description

.DESCRIPTION
Long description

.EXAMPLE
An example

.NOTES
General notes
#>
function CarbonBlackAlertsAPI() {
    if (-not([string]::IsNullOrWhiteSpace($Severity))) {
        $Severity = [int]$Severity
        if ($Severity -ge 1 && $Severity -le 10) {
            ##Do nothing
                
        }
        else {
                    
            throw "Severity should be between 1 and 10."
        }

    }
    else {
        ##Defaulted to 1
        $Severity = 1
    }
    $method = "POST";
    $contentType = "application/json";
    
    $body = '{ "time_range": {
                  "start": "{starttime}",
                  "end": "{endtime}"
      }, "criteria" : { "minimum_severity": {min}, "type": [ ], "policy_name": [ "ALL_POLICIES" ] }, "exclusions": { }, "sort": [ { "field": "severity", "order": "DESC" } ] }'
    $body = $body.Replace('{min}', $Severity)
    $body= $body.Replace('{starttime}', $startTime)
    $body=$body.Replace('{endtime}',$now)

    $headers = @{
        "X-Auth-Token" = "$($SIEMapiKey)/$($SIEMapiId)";
    };
    $authHeaders = @{"X-Auth-Token" = "$($SIEMapiKey)/$($SIEMapiId)" }
    $v7uri = ([System.Uri]::new("$($hostName)/api/alerts/v7/orgs/$($OrgKey)/alerts/_search"))
            
    $notifications = Invoke-WebRequest -Body $body -Uri $v7uri -Method $method -ContentType $contentType -Headers $headers -UseBasicParsing
    if($notifications.RawContentLength -ge 10)
    {
     $notificationsresults = $notifications | ConvertFrom-Json
     $TotalCount=0
    foreach ($item in $notificationsresults.results) {
<# $currentItemName is the current item #>
    $NotifLogJson = $item | ConvertTo-Json -Depth 5
   if (-not([string]::IsNullOrWhiteSpace($NotifLogJson)))
   {
     $responseObj = (ConvertFrom-Json $NotifLogJson)
     $status = Post-LogAnalyticsData -customerId $workspaceId -sharedKey $workspaceSharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($NotifLogJson)) -logType $AlertsTable;
     $TotalCount=$TotalCount+$responseObj.count
     Write-Host("$($responseObj.count) new Carbon Black Notifications as of $([DateTime]::UtcNow). Pushed data to Azure sentinel Status code:$($status)")
   }
   else
   {
    Write-Host "No new Carbon Black Notifications as of $([DateTime]::UtcNow)"
   }
   if((check_if_script_runs_too_long -percentage 0.8 -script_start_time $script_start_time))
   {
       Write-Host "Script is running long"
       break
   }

   }
   Write-Host("Total $($TotalCount) new Carbon Black Notifications as of $([DateTime]::UtcNow). Pushed data to Azure sentinel")
    }
    else
    {
        Write-Host "Notifications API status failed , Please check."
    }
}
try {

    $azstoragestring = $Env:WEBSITE_CONTENTAZUREFILECONNECTIONSTRING
    $Context = New-AzStorageContext -ConnectionString $azstoragestring
    $startTime,$now=GenerateDate
    $startTime=$startTime | Get-Date -Format yyyy-MM-ddTHH:mm:ss.000K
    if($startTime.Contains("Z"))
    {
            ## Do Nothing
    }
    else {
        $startTime=$startTime+"Z"
    }
    $now= $now | Get-Date -Format yyyy-MM-ddTHH:mm:ss.000K
    if($now.Contains("Z"))
    {
            ## Do Nothing
    }
    else {
        $now=$now+"Z"
    }
    CarbonBlackAPI
    if((Get-AzStorageContainer -Context $Context).Name -contains "lastalertlog"){
        #Set Container
        $now | Out-File "$env:TEMP\lastalertlog.log"
        Set-AzStorageBlobContent -file "$env:TEMP\lastalertlog.log" -Container (Get-AzStorageContainer -Name "lastalertlog" -Context $Context).Name -Context $Context -Force
    }
    else {
    $blob=(Get-AzStorageContainer -Context $Context).Name -contains "lastalertlog"
    if(-not $blob)
    {
    $azStorageContainer = New-AzStorageContainer -Name "lastalertlog" -Context $Context
    $now | Out-File "$env:TEMP\lastalertlog.log"
    Set-AzStorageBlobContent -file "$env:TEMP\lastalertlog.log" -Container $azStorageContainer.name -Context $Context -Force
    }
    }
}
catch {
    Write-Error "Failed at CarbonBlackAlertsAPI with error message: $($_.Exception.Message)" -ErrorAction SilentlyContinue
}

