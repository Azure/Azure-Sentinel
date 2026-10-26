<#
.SYNOPSIS
    Quick launcher for Invoke-SapAgentlessBackfill.ps1 with your saved settings.

.DESCRIPTION
    Fill in the SETTINGS block once, then start backfills without retyping connection details:

        .\Trigger-Run.ps1 -DryRun                                                # preview the default range
        .\Trigger-Run.ps1                                                        # run the default range
        .\Trigger-Run.ps1 -StartTimeUtc '2026-10-20T00:00' -EndTimeUtc '2026-10-20T06:00'
        .\Trigger-Run.ps1 -GapCsvPath .\gaps.csv
        .\Trigger-Run.ps1 -LastHours 6                                           # now-6h .. now

    Values can also come from environment variables, which take precedence over the SETTINGS
    block. This keeps tenant details out of the file:
        SAP_BACKFILL_CPI_ENDPOINT, SAP_BACKFILL_TOKEN_URL, SAP_BACKFILL_CLIENT_ID,
        SAP_BACKFILL_RFC_DESTINATION, SAP_BACKFILL_CLIENT_SECRET

    The client secret is never stored in this file. It is read from SAP_BACKFILL_CLIENT_SECRET
    if set, otherwise you are prompted once per run.

    Read the sizing guidance in README.md before running large loads.
#>
[CmdletBinding(DefaultParameterSetName = 'Default')]
param(
    [Parameter(ParameterSetName = 'Range', Mandatory = $true)][string]$StartTimeUtc,
    [Parameter(ParameterSetName = 'Range', Mandatory = $true)][string]$EndTimeUtc,
    [Parameter(ParameterSetName = 'Csv', Mandatory = $true)][string]$GapCsvPath,
    [Parameter(ParameterSetName = 'LastHours', Mandatory = $true)][ValidateRange(1, 8760)][int]$LastHours,
    [int]$SliceMinutes,
    [int]$PauseSeconds,
    [int]$MaxRuntimeMinutes,
    [switch]$DryRun,
    [switch]$Force
)

# ============================== SETTINGS (edit once) ==============================
$settings = @{
    CpiEndpoint        = 'https://azure-private.it-cpi023-rt.cfapps.eu20-001.hana.ondemand.com'
    TokenUrl           = 'https://azure-private.authentication.eu20.hana.ondemand.com/oauth/token'
    ClientId           = 'sb-626b08fa-b229-437b-8f5b-c1084582958c!b3750|it-rt-azure-private!b18631'
    RfcDestinationName = 'PM4-SENTINEL_CPI-RFC2'
}

# Default range used when neither -StartTimeUtc/-EndTimeUtc, -GapCsvPath nor -LastHours is given.
$defaultStartTimeUtc = '2026-10-20T00:00:00'
$defaultEndTimeUtc = '2026-10-20T06:00:00'

# Load tuning - start conservative, see README "Sizing and load protection".
$tuning = @{
    SliceMinutes      = 5
    PauseSeconds      = 10
    MaxRuntimeMinutes = 120
}
# ==================================================================================

$ErrorActionPreference = 'Stop'

$envMap = @{
    CpiEndpoint        = 'SAP_BACKFILL_CPI_ENDPOINT'
    TokenUrl           = 'SAP_BACKFILL_TOKEN_URL'
    ClientId           = 'SAP_BACKFILL_CLIENT_ID'
    RfcDestinationName = 'SAP_BACKFILL_RFC_DESTINATION'
}
foreach ($key in $envMap.Keys) {
    $envValue = [Environment]::GetEnvironmentVariable($envMap[$key])
    if (-not [string]::IsNullOrWhiteSpace($envValue)) { $settings[$key] = $envValue }
}

if ($PSBoundParameters.ContainsKey('SliceMinutes')) { $tuning.SliceMinutes = $SliceMinutes }
if ($PSBoundParameters.ContainsKey('PauseSeconds')) { $tuning.PauseSeconds = $PauseSeconds }
if ($PSBoundParameters.ContainsKey('MaxRuntimeMinutes')) { $tuning.MaxRuntimeMinutes = $MaxRuntimeMinutes }

$backfillArgs = @{} + $tuning

switch ($PSCmdlet.ParameterSetName) {
    'Range' { $backfillArgs.StartTimeUtc = $StartTimeUtc; $backfillArgs.EndTimeUtc = $EndTimeUtc }
    'Csv' { $backfillArgs.GapCsvPath = (Resolve-Path -LiteralPath $GapCsvPath).Path }
    'LastHours' {
        $now = (Get-Date).ToUniversalTime()
        $backfillArgs.StartTimeUtc = $now.AddHours(-$LastHours).ToString('yyyy-MM-ddTHH:mm:00')
        $backfillArgs.EndTimeUtc = $now.ToString('yyyy-MM-ddTHH:mm:00')
    }
    default { $backfillArgs.StartTimeUtc = $defaultStartTimeUtc; $backfillArgs.EndTimeUtc = $defaultEndTimeUtc }
}

if ($DryRun) { $backfillArgs.DryRun = $true }
if ($Force) { $backfillArgs.Force = $true }

if (-not $DryRun) {
    $placeholders = @($settings.Keys | Where-Object { [string]::IsNullOrWhiteSpace($settings[$_]) -or $settings[$_] -match '<[^>]+>' })
    if ($placeholders.Count -gt 0) {
        throw "Fill in the SETTINGS block in Trigger-Run.ps1 (or set the matching SAP_BACKFILL_* environment variables) for: $($placeholders -join ', ')"
    }
    $backfillArgs += $settings

    $secretFromEnv = $env:SAP_BACKFILL_CLIENT_SECRET
    if (-not [string]::IsNullOrEmpty($secretFromEnv)) {
        $backfillArgs.ClientSecret = ConvertTo-SecureString -String $secretFromEnv -AsPlainText -Force
    }

    $runsFolder = Join-Path $PSScriptRoot 'runs'
    New-Item -ItemType Directory -Path $runsFolder -Force | Out-Null
    $safeDestination = $settings.RfcDestinationName -replace '[^\w\-]', '_'
    $backfillArgs.LogFile = Join-Path $runsFolder "SapBackfill_${safeDestination}_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
}

& (Join-Path $PSScriptRoot 'Invoke-SapAgentlessBackfill.ps1') @backfillArgs
if ($?) {
    exit 0
}
exit 1
