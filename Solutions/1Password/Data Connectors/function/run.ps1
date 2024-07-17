# Input bindings are passed in via param block.
param($Timer)

# Get the current universal time in the default string format.
$currentUTCtime = (Get-Date).ToUniversalTime()

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"

$global:currentStartTime = (Get-Date).AddDays(-30).ToString('yyyy-MM-ddTHH:mm:ss.fffZ')

try {
    Get-Variables
} catch {
    Write-Warning "Unable to load required module"
    exit
}
$results = @()

# Validate the Access Token
$headers = @{
    "Authorization" = "Bearer $env:APIKey"
    "ContentType"   = "application/json"
}

$uri = "$env:apiEndpoint/api/v2/auth/introspect"
$apiResponse = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get

if (!($apiResponse)) {
    Write-Output "Invalid API Key"

    $results += @{
        "log_source"  = "healthevents"
        "category"    = "credentials_failed"
        "action_type" = "API Key Invalid"
    }

    Send-Data -body ($results | ConvertTo-Json -AsArray)
    exit
}

$lastRunTime = Get-TimeStamp @storagePayload

$endpoints = @('auditevents', 'signinattempts', 'itemusages')

foreach ($api in $endpoints) {
    try {
        # continue if the cursor does not exist and proceed with the lastRunTime
        $cursor = Get-Cursor @storagePayload -cursor $api -ErrorAction SilentlyContinue
        if ($cursor -and $cursor -ne "none") {
            $results += Get-AuditLogs -cursor $cursor -api $api
        } else {
            $results += Get-AuditLogs -lastRunTime $lastRunTime -api $api
        }
    } catch {
        $results += Get-AuditLogs -lastRunTime $currentStartTime -api $api
    }
}

$results += @{
    "log_source" = "healthevents"
}

if ($results.count -gt 0) {
    Write-Host "Sending $($results.count) new records"
    Send-Data -body ($results | ConvertTo-Json -AsArray)
    $updateTime = $true
} else {
    Write-Host "No new data was found"
}

if ($true -eq $updateTime) {
    $null = Set-TimeStamp @storagePayload -lastRun $currentUTCtime
}

#clear the temp folder
Remove-Item $env:temp\* -Recurse -Force -ErrorAction SilentlyContinue
