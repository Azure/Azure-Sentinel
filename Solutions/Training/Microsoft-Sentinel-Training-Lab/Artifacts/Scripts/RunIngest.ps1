param(
    [string]$SubscriptionId,

    [string]$ResourceGroupName,

    [string]$WorkspaceName,

    [string]$RepoBaseUrl = "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/Training/Microsoft-Sentinel-Training-Lab/Artifacts"
)

$ErrorActionPreference = "Stop"

Import-Module Az.Accounts -ErrorAction Stop
Connect-AzAccount -Identity | Out-Null

function Get-OptionalAutomationVariableValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    try {
        return Get-AutomationVariable -Name $Name
    }
    catch {
        return $null
    }
}

function ConvertTo-RunbookStringValue {
    param(
        [AllowNull()]
        [string]$Value
    )

    if ($null -eq $Value) {
        return $null
    }

    $trimmed = $Value.Trim()
    return $trimmed.Trim('"')
}

if (-not $SubscriptionId) {
    $SubscriptionId = Get-OptionalAutomationVariableValue -Name 'SentinelTrainingSubscriptionId'
}
if (-not $ResourceGroupName) {
    $ResourceGroupName = Get-OptionalAutomationVariableValue -Name 'SentinelTrainingResourceGroupName'
}
if (-not $WorkspaceName) {
    $WorkspaceName = Get-OptionalAutomationVariableValue -Name 'SentinelTrainingWorkspaceName'
}

if (-not $SubscriptionId) {
    $context = Get-AzContext
    if ($context -and $context.Subscription -and $context.Subscription.Id) {
        $SubscriptionId = $context.Subscription.Id
    }
}

$SubscriptionId = ConvertTo-RunbookStringValue -Value $SubscriptionId
$ResourceGroupName = ConvertTo-RunbookStringValue -Value $ResourceGroupName
$WorkspaceName = ConvertTo-RunbookStringValue -Value $WorkspaceName

if (-not $SubscriptionId -or -not $ResourceGroupName -or -not $WorkspaceName) {
    throw "Missing required runbook parameters. Provide SubscriptionId/ResourceGroupName/WorkspaceName via jobSchedule parameters or set Automation variables: SentinelTrainingSubscriptionId, SentinelTrainingResourceGroupName, SentinelTrainingWorkspaceName."
}

# ── Derive GitHub API URL from raw content URL ──────────────────────────────
# raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}
# -> api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}
if ($RepoBaseUrl -match '^https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.+)$') {
    $apiOwner  = $Matches[1]
    $apiRepo   = $Matches[2]
    $apiBranch = $Matches[3]
    $apiPath   = $Matches[4]
    $apiBase   = "https://api.github.com/repos/$apiOwner/$apiRepo/contents/$apiPath"
    $apiQuery  = "?ref=$apiBranch"
} else {
    throw "RepoBaseUrl must be a raw.githubusercontent.com URL. Got: $RepoBaseUrl"
}

function Get-CsvFileList {
    param([string]$SubFolder)
    $url = "$apiBase/$SubFolder$apiQuery"
    $headers = @{ "User-Agent" = "SentinelTrainingLab"; "Accept" = "application/vnd.github.v3+json" }
    $response = Invoke-RestMethod -Uri $url -Headers $headers -UseBasicParsing
    return @($response | Where-Object { $_.name -like "*.csv" } | ForEach-Object { $_.name })
}

Write-Output "Discovering CSV files from repo..."
$customCsvFiles  = Get-CsvFileList -SubFolder "Telemetry/Custom"
$builtInCsvFiles = Get-CsvFileList -SubFolder "Telemetry/BuildIn"
Write-Output "Found $($customCsvFiles.Count) custom and $($builtInCsvFiles.Count) built-in CSVs."

# ── Create local folder structure ────────────────────────────────────────────
$workdir              = Join-Path -Path $env:TEMP -ChildPath "sentinel-training-demo"
$scriptsDir           = Join-Path -Path $workdir -ChildPath "Scripts"
$customTelemetryPath  = Join-Path -Path $workdir -ChildPath "Telemetry/Custom"
$builtInTelemetryPath = Join-Path -Path $workdir -ChildPath "Telemetry/BuildIn"
$templatesPath        = Join-Path -Path $workdir -ChildPath "DCRTemplates"

foreach ($dir in @($scriptsDir, $customTelemetryPath, $builtInTelemetryPath, $templatesPath)) {
    if (-not (Test-Path -Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# ── Download helper with retry ───────────────────────────────────────────────
function Get-FileFromRepo {
    param([string]$Url, [string]$OutFile)
    $maxAttempts = 4
    for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
        try {
            Invoke-WebRequest -Uri $Url -OutFile $OutFile -UseBasicParsing
            return
        } catch {
            if ($attempt -eq $maxAttempts) {
                throw "Failed to download $Url after $maxAttempts attempts. Last error: $_"
            }
            $delay = [math]::Min(30, [math]::Pow(2, $attempt))
            Write-Warning "Download attempt $attempt for $Url failed: $($_.Exception.Message). Retrying in ${delay}s..."
            Start-Sleep -Seconds $delay
        }
    }
}

# ── Download files from repo ─────────────────────────────────────────────────
$scriptPath = Join-Path -Path $scriptsDir -ChildPath "IngestCSV.ps1"
Write-Output "Downloading IngestCSV.ps1..."
Get-FileFromRepo -Url "$RepoBaseUrl/Scripts/IngestCSV.ps1" -OutFile $scriptPath

Write-Output "Downloading $($customCsvFiles.Count) custom telemetry CSVs..."
foreach ($csv in $customCsvFiles) {
    Get-FileFromRepo -Url "$RepoBaseUrl/Telemetry/Custom/$csv" -OutFile (Join-Path $customTelemetryPath $csv)
}

Write-Output "Downloading $($builtInCsvFiles.Count) built-in telemetry CSVs..."
foreach ($csv in $builtInCsvFiles) {
    Get-FileFromRepo -Url "$RepoBaseUrl/Telemetry/BuildIn/$csv" -OutFile (Join-Path $builtInTelemetryPath $csv)
}

# ── Run ingestion ────────────────────────────────────────────────────────────
$ingestArgs = @{
    SubscriptionId       = $SubscriptionId
    ResourceGroupName    = $ResourceGroupName
    WorkspaceName        = $WorkspaceName
    TelemetryPath        = $customTelemetryPath
    BuiltInTelemetryPath = $builtInTelemetryPath
    TemplatesOutputPath  = $templatesPath
    DeployBuiltInDcr     = $true
    Deploy               = $true
    Ingest               = $true
}

& $scriptPath @ingestArgs
