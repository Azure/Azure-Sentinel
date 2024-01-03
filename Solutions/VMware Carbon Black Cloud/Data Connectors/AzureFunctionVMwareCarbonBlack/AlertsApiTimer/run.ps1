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

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"
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
    $OrgKey = $env:CarbonBlackOrgKey
    $s3BucketName = $env:s3BucketName
    $EventprefixFolder = $env:EventPrefixFolderName
    $AlertprefixFolder = $env:AlertPrefixFolderName
    $AWSAccessKeyId = $env:AWSAccessKeyId
    $AWSSecretAccessKey = $env:AWSSecretAccessKey
    $Severity = $env:Severity

    $startTime = [System.DateTime]::UtcNow.AddMinutes( - $($time))
    $now = [System.DateTime]::UtcNow

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
    $headers = @{
        "X-Auth-Token" = "$($SIEMapiKey)/$($SIEMapiId)";
    };
    $body = '{ "criteria" : { "minimum_severity": {min}}, "type": [ ], "policy_name": [ "ALL_POLICIES" ] }, "exclusions": { }, "sort": [ { "field": "severity", "order": "DESC" } ] }'
    $body = $body.Replace('{min}', $Severity)
    $authHeaders = @{"X-Auth-Token" = "$($SIEMapiKey)/$($SIEMapiId)" }
    $v7uri = ([System.Uri]::new("$($hostName)/api/alerts/v7/orgs/$($OrgKey)/alerts/_search"))
            
    $notifications = Invoke-WebRequest -Body $body -Uri $v7uri -Method $method -ContentType $contentType -Headers $headers -UseBasicParsing
    if ($notifications.success -eq $true) {
        $NotifLogJson = $notifications.notifications | ConvertTo-Json -Depth 5
        if (-not([string]::IsNullOrWhiteSpace($NotifLogJson))) {
            $responseObj = (ConvertFrom-Json $NotifLogJson)
            $status = Post-LogAnalyticsData -customerId $workspaceId -sharedKey $workspaceSharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($NotifLogJson)) -logType $NotificationTable;
            Write-Host("$($responseObj.count) new Carbon Black Notifications as of $([DateTime]::UtcNow). Pushed data to Azure sentinel Status code:$($status)")
        }
        else {
            Write-Host "No new Carbon Black Notifications as of $([DateTime]::UtcNow)"
        }
    }
    else {
        Write-Host "Notifications API status failed , Please check."
    }
}
try {
    CarbonBlackAPI
}
catch {
    Write-Error "Failed at CarbonBlackAlertsAPI with error message: $($_.Exception.Message)" -ErrorAction SilentlyContinue
}

