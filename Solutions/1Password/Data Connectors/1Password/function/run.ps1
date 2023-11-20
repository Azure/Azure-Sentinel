# Input bindings are passed in via param block.
param($Timer)

# Get the current universal time in the default string format.
$currentUTCtime = (Get-Date).ToUniversalTime()

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"

$currentStartTime = (Get-Date).AddDays(-30).ToString('yyyy-MM-ddTHH:mm:ss.fffZ')

try {
    Get-Variables
} catch {
    Write-Warning "Unable to load required module"
    exit
}
$results = @()
$lastRunTime = Get-TimeStamp @storagePayload

$endpoints = @('auditevents', 'signinattempts', 'itemusages')

foreach ($api in $endpoints) {
    try {
        $cursor = Get-Cursor @storagePayload -cursor $api -ErrorAction SilentlyContinue
        if ($cursor) {
            $results += Get-AuditLogs -cursor $cursor -api $api
        } else {
            $results += Get-AuditLogs -lastRunTime $currentStartTime -api $api
        }
    } catch {
        $results += Get-AuditLogs -lastRunTime $currentStartTime -api $api
    }

    if ($results.count -gt 1) {
        Send-Data -body ($results | ConvertTo-Json)
        $updateTime = $true
    } else {
        Write-Host "No new data was found"
    }
}

    if ($true -eq $updateTime) {
        $null = Set-TimeStamp @storagePayload -lastRun $currentUTCtime
    }

    #clear the temp folder
    Remove-Item $env:temp\* -Recurse -Force -ErrorAction SilentlyContinue
