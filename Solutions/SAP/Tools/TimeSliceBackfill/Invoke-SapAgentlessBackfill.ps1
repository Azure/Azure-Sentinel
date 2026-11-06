<#
.SYNOPSIS
    Loads selected historic time slices for the Microsoft Sentinel agentless SAP connector.

.DESCRIPTION
    The agentless SAP data connector (SAPCC) starts polling at "now". This script calls the SAP
    Integration Suite (CPI) iFlow endpoint /http/microsoft/sentinel/sap-log-trigger directly for
    past time windows. For each window, the iFlow reads the SAP logs and pushes them to the
    configured Data Collection Endpoint/Rule, the same way a regular connector poll does.

    Use it to:
      - perform an initial load of historic SAP logs.
      - fill gaps caused by intermittent failures or log pipeline downtime.

    Slices run one at a time, with a configurable pause between calls, to protect SAP
    Integration Suite, SAP Cloud Connector and the SAP ERP backend. Read the sizing section of
    README.md BEFORE you run large loads alongside live connector traffic.

    Error handling:
      - If a request reaches -TimeoutSeconds, the script stops (exit code 1) and prints a
        resume hint.
      - Any other error is logged (Status=Error in the results CSV) and the script continues.
        To re-run failed slices, filter the results CSV and pass it back via -GapCsvPath.

.PARAMETER CpiEndpoint
    CPI runtime URL, e.g. https://<tenant>.it-cpi023-rt.cfapps.eu20-001.hana.ondemand.com

.PARAMETER TokenUrl
    OAuth token URL from the Process Integration Runtime service key, e.g.
    https://<subdomain>.authentication.eu20.hana.ondemand.com/oauth/token

.PARAMETER ClientId
    Client id from the Process Integration Runtime service key.

.PARAMETER ClientSecret
    Client secret as a SecureString. You are prompted for it if it is omitted.

.PARAMETER RfcDestinationName
    The BTP/RFC destination name of the SAP system. Use the same value that is configured on
    the connector.

.PARAMETER ApiPath
    Path of the trigger iFlow. Default /http/microsoft/sentinel/sap-log-trigger.

.PARAMETER StartTimeUtc
    Start of the range to load (UTC). Use with -EndTimeUtc.

.PARAMETER EndTimeUtc
    End of the range to load (UTC, exclusive). The value is clamped to now minus
    -SafetyLagMinutes.

.PARAMETER GapCsvPath
    CSV with columns StartTimeUTC,EndTimeUTC. The StartTime,EndTime columns of this script's
    results CSV are also accepted. Each row is split into slices.

.PARAMETER SliceMinutes
    Size of each request window in minutes. Default 1.

.PARAMETER PauseSeconds
    Pause between two requests in seconds. Default 5.

.PARAMETER TimeoutSeconds
    Timeout per request. Default 180, the same as the connector. The script exits when a
    request reaches it.

.PARAMETER MaxRuntimeMinutes
    Maximum runtime. When reached, the script stops cleanly and prints a resume hint.
    0 = unlimited. Default 0.

.PARAMETER SafetyLagMinutes
    Windows that end later than now minus this lag are not requested. Default 5.

.PARAMETER LargeRunSliceThreshold
    The script refuses to run more slices than this unless -Force is set. Default 1440
    (1 day of 1-minute slices).

.PARAMETER TimeFormat
    Format of startTimeUTC/endTimeUTC. Default yyyy-MM-ddTHH:mm:ss.

.PARAMETER LogFile
    Results CSV. One row per slice is appended.

.PARAMETER Force
    Allows runs above -LargeRunSliceThreshold.

.PARAMETER DryRun
    Lists the planned slices only. No authentication and no requests.

.EXAMPLE
    .\Invoke-SapAgentlessBackfill.ps1 -StartTimeUtc '2026-10-20T00:00:00' -EndTimeUtc '2026-10-20T02:00:00' -DryRun

.EXAMPLE
    .\Invoke-SapAgentlessBackfill.ps1 -CpiEndpoint $cpi -TokenUrl $tok -ClientId $id -RfcDestinationName 'S4H_100' `
        -StartTimeUtc '2026-10-20T00:00:00' -EndTimeUtc '2026-10-20T06:00:00' -SliceMinutes 5 -PauseSeconds 10

.EXAMPLE
    .\Invoke-SapAgentlessBackfill.ps1 -CpiEndpoint $cpi -TokenUrl $tok -ClientId $id -RfcDestinationName 'S4H_100' `
        -GapCsvPath .\gaps.csv

.NOTES
    Provided as-is as a sample. Test in a non-production landscape first.
#>
[CmdletBinding(DefaultParameterSetName = 'Range')]
param(
    [string]$CpiEndpoint,
    [string]$TokenUrl,
    [string]$ClientId,
    [System.Security.SecureString]$ClientSecret,
    [string]$RfcDestinationName,
    [string]$ApiPath = '/http/microsoft/sentinel/sap-log-trigger',

    [Parameter(Mandatory = $true, ParameterSetName = 'Range')]
    [string]$StartTimeUtc,
    [Parameter(Mandatory = $true, ParameterSetName = 'Range')]
    [string]$EndTimeUtc,

    [Parameter(Mandatory = $true, ParameterSetName = 'Csv')]
    [string]$GapCsvPath,

    [ValidateRange(1, 1440)]
    [int]$SliceMinutes = 1,
    [ValidateRange(0, 3600)]
    [int]$PauseSeconds = 5,
    [ValidateRange(10, 600)]
    [int]$TimeoutSeconds = 180,
    [ValidateRange(0, 100000)]
    [int]$MaxRuntimeMinutes = 0,
    [ValidateRange(0, 1440)]
    [int]$SafetyLagMinutes = 5,
    [ValidateRange(1, [int]::MaxValue)]
    [int]$LargeRunSliceThreshold = 1440,
    [string]$TimeFormat = 'yyyy-MM-ddTHH:mm:ss',
    [string]$LogFile = ".\SapBackfill_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv",
    [int]$TokenRefreshBufferSeconds = 300,
    [switch]$Force,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$script:parameterSetName = $PSCmdlet.ParameterSetName

function ConvertTo-UtcDateTime {
    param([Parameter(Mandatory = $true)][string]$Value, [string]$Name = 'value')
    $styles = [System.Globalization.DateTimeStyles]::AssumeUniversal -bor [System.Globalization.DateTimeStyles]::AdjustToUniversal
    $parsed = [datetime]::MinValue
    if (-not [datetime]::TryParse($Value, [System.Globalization.CultureInfo]::InvariantCulture, $styles, [ref]$parsed)) {
        throw "Cannot parse $Name '$Value' as a date/time. Use ISO 8601, e.g. 2026-10-20T00:00:00 (interpreted as UTC)."
    }
    return [datetime]::SpecifyKind($parsed, [System.DateTimeKind]::Utc)
}

function Get-TimeSlice {
    param([datetime]$From, [datetime]$To, [int]$Minutes)
    $list = New-Object System.Collections.Generic.List[object]
    $cursor = $From
    while ($cursor -lt $To) {
        $next = $cursor.AddMinutes($Minutes)
        if ($next -gt $To) { $next = $To }
        $list.Add([PSCustomObject]@{ Start = $cursor; End = $next })
        $cursor = $next
    }
    return , $list
}

function Get-OAuthToken {
    $pair = "{0}:{1}" -f $ClientId, $script:plainSecret
    $basic = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($pair))
    $authHeaders = @{ 'Authorization' = "Basic $basic"; 'Accept' = 'application/json' }
    $tokenResponse = Invoke-RestMethod -Uri "$($TokenUrl)?grant_type=client_credentials" -Method Post -Headers $authHeaders -TimeoutSec 60
    $script:token = $tokenResponse.access_token
    $script:tokenExpiresIn = [int]$tokenResponse.expires_in
    $script:tokenObtainedAt = Get-Date
    Write-Host "Token obtained. Expires in $($script:tokenExpiresIn) seconds ($([math]::Round($script:tokenExpiresIn / 60, 1)) minutes)" -ForegroundColor Green
}

function Write-ResumeHint {
    param([datetime]$ResumeFrom, [datetime]$WindowEnd)
    Write-Host ""
    Write-Host "Resume from the interrupted slice with:" -ForegroundColor Cyan
    if ($script:parameterSetName -eq 'Range') {
        Write-Host "  -StartTimeUtc '$($ResumeFrom.ToString('yyyy-MM-ddTHH:mm:ss'))' -EndTimeUtc '$($WindowEnd.ToString('yyyy-MM-ddTHH:mm:ss'))'" -ForegroundColor Cyan
    }
    else {
        Write-Host "  a gap CSV containing the remaining windows of '$GapCsvPath', starting at $($ResumeFrom.ToString('yyyy-MM-ddTHH:mm:ss')) UTC." -ForegroundColor Cyan
    }
}

function Get-ColumnSum {
    param($Items, [string]$Property)
    $sum = ($Items | Where-Object { "$($_.$Property)" -match '^\d+$' } | ForEach-Object { [long]$_.$Property } | Measure-Object -Sum).Sum
    if ($null -eq $sum) { return 0 }
    return $sum
}

# ---------------------------------------------------------------------------------------------
# Build the list of windows and slices
# ---------------------------------------------------------------------------------------------
$nowUtc = (Get-Date).ToUniversalTime()
$latestAllowedEnd = $nowUtc.AddMinutes(-$SafetyLagMinutes)
$latestAllowedEnd = [datetime]::SpecifyKind($latestAllowedEnd.AddTicks(-($latestAllowedEnd.Ticks % [TimeSpan]::TicksPerMinute)), [System.DateTimeKind]::Utc)
$windows = New-Object System.Collections.Generic.List[object]

if ($script:parameterSetName -eq 'Range') {
    $windows.Add([PSCustomObject]@{
            Start = ConvertTo-UtcDateTime -Value $StartTimeUtc -Name 'StartTimeUtc'
            End   = ConvertTo-UtcDateTime -Value $EndTimeUtc -Name 'EndTimeUtc'
        })
}
else {
    if (-not (Test-Path -LiteralPath $GapCsvPath)) { throw "Gap CSV '$GapCsvPath' not found." }
    $rows = @(Import-Csv -LiteralPath $GapCsvPath)
    if ($rows.Count -eq 0) { throw "Gap CSV '$GapCsvPath' contains no rows." }
    $columns = $rows[0].PSObject.Properties.Name
    if ($columns -contains 'StartTimeUTC' -and $columns -contains 'EndTimeUTC') { $startCol = 'StartTimeUTC'; $endCol = 'EndTimeUTC' }
    elseif ($columns -contains 'StartTime' -and $columns -contains 'EndTime') { $startCol = 'StartTime'; $endCol = 'EndTime' }
    else { throw "Gap CSV must contain columns StartTimeUTC,EndTimeUTC (or StartTime,EndTime)." }
    $lineNumber = 1
    foreach ($row in $rows) {
        $lineNumber++
        $windows.Add([PSCustomObject]@{
                Start = ConvertTo-UtcDateTime -Value $row.$startCol -Name "$startCol (line $lineNumber)"
                End   = ConvertTo-UtcDateTime -Value $row.$endCol -Name "$endCol (line $lineNumber)"
            })
    }
}

$slices = New-Object System.Collections.Generic.List[object]
foreach ($window in ($windows | Sort-Object Start)) {
    if ($window.Start -ge $window.End) { throw "Invalid window: start $($window.Start.ToString($TimeFormat)) is not before end $($window.End.ToString($TimeFormat))." }
    if ($window.Start -ge $latestAllowedEnd) {
        Write-Warning "Skipping window starting $($window.Start.ToString($TimeFormat)) UTC: not older than now minus $SafetyLagMinutes minute(s). The live connector covers it."
        continue
    }
    $windowEnd = $window.End
    if ($windowEnd -gt $latestAllowedEnd) {
        Write-Warning "Window end $($windowEnd.ToString($TimeFormat)) UTC clamped to $($latestAllowedEnd.ToString($TimeFormat)) UTC (now minus $SafetyLagMinutes minute(s))."
        $windowEnd = $latestAllowedEnd
    }
    foreach ($s in (Get-TimeSlice -From $window.Start -To $windowEnd -Minutes $SliceMinutes)) {
        if ($slices.Count -gt 0 -and $s.Start -lt $slices[$slices.Count - 1].End) {
            Write-Warning "Slice $($s.Start.ToString($TimeFormat)) overlaps the previous window. Overlapping windows ingest duplicates."
        }
        $slices.Add($s)
    }
}

if ($slices.Count -eq 0) { Write-Host "Nothing to load." -ForegroundColor Yellow; return }

$coveredMinutes = [math]::Round((($slices | ForEach-Object { ($_.End - $_.Start).TotalMinutes }) | Measure-Object -Sum).Sum, 1)
$minimumPauseMinutes = [math]::Round((($slices.Count - 1) * $PauseSeconds) / 60, 1)
Write-Host "Planned: $($slices.Count) slice(s) of up to $SliceMinutes minute(s), covering $coveredMinutes minute(s) of SAP logs."
Write-Host "First slice starts: $($slices[0].Start.ToString($TimeFormat)) UTC, last slice ends: $($slices[$slices.Count - 1].End.ToString($TimeFormat)) UTC"
Write-Host "Pause between calls: $PauseSeconds s (adds at least $minimumPauseMinutes minute(s) of runtime). Timeout per request: $TimeoutSeconds s."

if ($DryRun) {
    $slices | Select-Object @{ n = 'StartTimeUTC'; e = { $_.Start.ToString($TimeFormat) } }, @{ n = 'EndTimeUTC'; e = { $_.End.ToString($TimeFormat) } } | Format-Table -AutoSize
    Write-Host "Dry run - no requests sent." -ForegroundColor Yellow
    return
}

if ($slices.Count -gt $LargeRunSliceThreshold -and -not $Force) {
    throw "The run has $($slices.Count) slices, which exceeds -LargeRunSliceThreshold ($LargeRunSliceThreshold). Review the sizing guidance in README.md, then re-run with -Force or split the load."
}

# ---------------------------------------------------------------------------------------------
# Validate connection parameters and authenticate
# ---------------------------------------------------------------------------------------------
foreach ($required in 'CpiEndpoint', 'TokenUrl', 'ClientId', 'RfcDestinationName') {
    if ([string]::IsNullOrWhiteSpace((Get-Variable -Name $required -ValueOnly))) { throw "Parameter -$required is required unless -DryRun is used." }
}
if (-not $ClientSecret) { $ClientSecret = Read-Host -Prompt 'Client secret' -AsSecureString }
$script:plainSecret = (New-Object System.Net.NetworkCredential('', $ClientSecret)).Password
$CpiEndpoint = $CpiEndpoint.TrimEnd('/')
if (-not $ApiPath.StartsWith('/')) { $ApiPath = "/$ApiPath" }

Get-OAuthToken

# ---------------------------------------------------------------------------------------------
# Process slices sequentially
# ---------------------------------------------------------------------------------------------
$results = New-Object System.Collections.Generic.List[object]
$runStart = Get-Date
$okCount = 0
$errorCount = 0
$lastWindowEnd = $slices[$slices.Count - 1].End

Write-Host "Writing results to $LogFile"

for ($i = 0; $i -lt $slices.Count; $i++) {
    $slice = $slices[$i]

    if ($MaxRuntimeMinutes -gt 0 -and ((Get-Date) - $runStart).TotalMinutes -ge $MaxRuntimeMinutes) {
        Write-Host "Max runtime of $MaxRuntimeMinutes minute(s) reached. Stopping cleanly." -ForegroundColor Yellow
        Write-ResumeHint -ResumeFrom $slice.Start -WindowEnd $lastWindowEnd
        break
    }

    $tokenAge = ((Get-Date) - $script:tokenObtainedAt).TotalSeconds
    if ($tokenAge -ge ($script:tokenExpiresIn - $TokenRefreshBufferSeconds)) {
        Write-Host "Token expiring soon (age: $([math]::Round($tokenAge))s, expires: $($script:tokenExpiresIn)s). Refreshing..." -ForegroundColor Yellow
        Get-OAuthToken
    }

    $startText = $slice.Start.ToString($TimeFormat)
    $endText = $slice.End.ToString($TimeFormat)
    $query = "?startTimeUTC=$([uri]::EscapeDataString($startText))&endTimeUTC=$([uri]::EscapeDataString($endText))"
    $headers = @{
        'Authorization'      = "Bearer $($script:token)"
        'Accept'             = 'application/json'
        'RfcDestinationName' = $RfcDestinationName
    }

    $resultObject = [PSCustomObject]@{
        StartTime   = $startText
        EndTime     = $endText
        Status      = ''
        ElapsedTime = $null
        AuditLog    = $null
        Users       = $null
        ChangeDoc   = $null
        Roles       = $null
        MPLLogID    = $null
        RunId       = $null
        Error       = $null
    }

    $requestStart = Get-Date
    try {
        $response = Invoke-WebRequest -Uri "$CpiEndpoint$ApiPath$query" -Method Get -Headers $headers -TimeoutSec $TimeoutSeconds -UseBasicParsing
        $elapsedTime = [math]::Round(((Get-Date) - $requestStart).TotalSeconds, 2)
        $resultObject.ElapsedTime = $elapsedTime

        if ($elapsedTime -ge $TimeoutSeconds) {
            $resultObject.Status = 'Timeout'
            $resultObject | Export-Csv -Path $LogFile -Append -NoTypeInformation
            Write-Host "FATAL: Request took $elapsedTime seconds (>= $TimeoutSeconds). Exiting." -ForegroundColor Red
            Write-ResumeHint -ResumeFrom $slice.Start -WindowEnd $lastWindowEnd
            exit 1
        }

        if ($response.Content -is [byte[]]) { $jsonContent = [System.Text.Encoding]::UTF8.GetString($response.Content) }
        else { $jsonContent = $response.Content }
        $extended = ($jsonContent | ConvertFrom-Json).properties.ExtendedProperties

        $resultObject.Status = 'OK'
        $resultObject.AuditLog = $extended.ABAPAuditLog
        $resultObject.Users = $extended.ABAPUserDetails
        $resultObject.ChangeDoc = $extended.ABAPChangeDocsLog
        $resultObject.Roles = $extended.ABAPAuthorizationDetails
        $resultObject.MPLLogID = $extended.SAP_MessageProcessingLogID
        $resultObject.RunId = $extended.SAP_RunId
        $okCount++
    }
    catch {
        $catchElapsed = [math]::Round(((Get-Date) - $requestStart).TotalSeconds, 2)
        $resultObject.ElapsedTime = $catchElapsed
        $resultObject.Error = "$_"
        if ($catchElapsed -ge $TimeoutSeconds) {
            $resultObject.Status = 'Timeout'
            $resultObject | Export-Csv -Path $LogFile -Append -NoTypeInformation
            Write-Host "FATAL: Request timed out after $catchElapsed seconds (>= $TimeoutSeconds). Exiting." -ForegroundColor Red
            Write-ResumeHint -ResumeFrom $slice.Start -WindowEnd $lastWindowEnd
            exit 1
        }
        $resultObject.Status = 'Error'
        $errorCount++
    }

    $results.Add($resultObject)
    $resultObject | Export-Csv -Path $LogFile -Append -NoTypeInformation

    try { Clear-Host } catch { Write-Verbose 'Console cannot be cleared (non-interactive host).' }
    Write-Host "Slice $($i + 1) of $($slices.Count) | OK: $okCount | Errors: $errorCount | Runtime: $([math]::Round(((Get-Date) - $runStart).TotalMinutes, 1)) min"
    $results | Select-Object -Last 20 | Format-Table StartTime, EndTime, Status, ElapsedTime, AuditLog, Users, ChangeDoc, Roles, RunId -AutoSize
    if ($resultObject.Status -eq 'Error') { Write-Host "Error: $($resultObject.Error)" -ForegroundColor Yellow }

    if ($i -lt $slices.Count - 1 -and $PauseSeconds -gt 0) { Start-Sleep -Seconds $PauseSeconds }
}

# ---------------------------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------------------------
Write-Host ""
Write-Host "Summary" -ForegroundColor Green
Write-Host "  Slices processed : $($results.Count) of $($slices.Count) (OK: $okCount, Errors: $errorCount)"
Write-Host "  ABAPAuditLog     : $(Get-ColumnSum $results 'AuditLog')"
Write-Host "  ABAPUserDetails  : $(Get-ColumnSum $results 'Users')"
Write-Host "  ABAPChangeDocsLog: $(Get-ColumnSum $results 'ChangeDoc')"
Write-Host "  ABAPAuthDetails  : $(Get-ColumnSum $results 'Roles')"
Write-Host "  Runtime          : $([math]::Round(((Get-Date) - $runStart).TotalMinutes, 1)) minute(s)"
Write-Host "  Results CSV      : $LogFile"
if ($errorCount -gt 0) {
    Write-Host ""
    Write-Host "Re-run failed slices with:" -ForegroundColor Yellow
    Write-Host "  Import-Csv '$LogFile' | Where-Object Status -eq 'Error' | Export-Csv .\retry.csv -NoTypeInformation" -ForegroundColor Yellow
    Write-Host "  .\Invoke-SapAgentlessBackfill.ps1 <connection parameters> -GapCsvPath .\retry.csv" -ForegroundColor Yellow
}
