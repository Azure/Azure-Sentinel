<#
.SYNOPSIS
Ingest local CSV files into a Microsoft Sentinel / Log Analytics workspace.

.DESCRIPTION
Standalone utility that reads CSV files from local folders and ingests them into
Log Analytics using the same pipeline as the Sentinel Training Lab.

Place your CSV files in:
  - Custom/   folder (next to this script) for custom table ingestion
  - BuildIn/  folder (next to this script) for built-in table ingestion

The script downloads IngestCSV.ps1 from GitHub at runtime, then passes your
local CSV folders to it.

.PARAMETER SubscriptionId
Azure subscription ID. If omitted, uses the current Az context.

.PARAMETER ResourceGroupName
Resource group containing the Log Analytics workspace.

.PARAMETER WorkspaceName
Log Analytics workspace name.

.PARAMETER IngestScriptUrl
URL to download IngestCSV.ps1 from. Defaults to the official repo.

.PARAMETER SkipCustom
Skip ingestion of custom table CSVs (Custom/ folder).

.PARAMETER SkipBuiltIn
Skip ingestion of built-in table CSVs (BuildIn/ folder).

.EXAMPLE
# Place CSVs in Custom/ and BuildIn/ folders next to this script, then:
.\Ingest-LocalCSV.ps1 -SubscriptionId "xxxx" -ResourceGroupName "rg-sentinel" -WorkspaceName "law-sentinel"

.EXAMPLE
# Ingest only custom tables:
.\Ingest-LocalCSV.ps1 -ResourceGroupName "rg-sentinel" -WorkspaceName "law-sentinel" -SkipBuiltIn
#>
param(
    [string]$SubscriptionId,

    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory = $true)]
    [string]$WorkspaceName,

    [string]$IngestScriptUrl = "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Tools/Microsoft-Sentinel-Training-Lab/Artifacts/Scripts/IngestCSV.ps1",

    [switch]$SkipCustom,

    [switch]$SkipBuiltIn
)

$ErrorActionPreference = "Stop"

# ── Resolve paths relative to script location ────────────────────────────────
$scriptDir        = $PSScriptRoot
$customCsvPath    = Join-Path $scriptDir "Custom"
$builtInCsvPath   = Join-Path $scriptDir "BuildIn"
$templatesPath    = Join-Path $scriptDir "DCRTemplates"
$ingestScriptPath = Join-Path $scriptDir "IngestCSV.ps1"

# ── Validate CSV folders ─────────────────────────────────────────────────────
$hasCustom  = (-not $SkipCustom)  -and (Test-Path $customCsvPath)  -and ((Get-ChildItem $customCsvPath -Filter "*.csv" -File).Count -gt 0)
$hasBuiltIn = (-not $SkipBuiltIn) -and (Test-Path $builtInCsvPath) -and ((Get-ChildItem $builtInCsvPath -Filter "*.csv" -File).Count -gt 0)

if (-not $hasCustom -and -not $hasBuiltIn) {
    $msg = "No CSV files found. Place .csv files in:`n"
    $msg += "  Custom/  folder (next to this script) for custom tables`n"
    $msg += "  BuildIn/ folder (next to this script) for built-in tables"
    throw $msg
}

if ($hasCustom) {
    $customCount = (Get-ChildItem $customCsvPath -Filter "*.csv" -File).Count
    Write-Output "Found $customCount custom CSV(s) in: $customCsvPath"
} else {
    Write-Output "Skipping custom table ingestion (no CSVs or -SkipCustom)."
}

if ($hasBuiltIn) {
    $builtInCount = (Get-ChildItem $builtInCsvPath -Filter "*.csv" -File).Count
    Write-Output "Found $builtInCount built-in CSV(s) in: $builtInCsvPath"
} else {
    Write-Output "Skipping built-in table ingestion (no CSVs or -SkipBuiltIn)."
}

# ── Ensure templates output folder exists ────────────────────────────────────
if (-not (Test-Path $templatesPath)) {
    New-Item -ItemType Directory -Path $templatesPath -Force | Out-Null
}

# ── Connect to Azure ─────────────────────────────────────────────────────────
Import-Module Az.Accounts -ErrorAction Stop

$ctx = Get-AzContext
if (-not $ctx) {
    Write-Output "No active Azure session. Running Connect-AzAccount..."
    Connect-AzAccount | Out-Null
    $ctx = Get-AzContext
}

if (-not $SubscriptionId) {
    $SubscriptionId = $ctx.Subscription.Id
    Write-Output "Using current subscription: $SubscriptionId"
}

if ($ctx.Subscription.Id -ne $SubscriptionId) {
    Set-AzContext -SubscriptionId $SubscriptionId | Out-Null
}

# ── Download IngestCSV.ps1 ───────────────────────────────────────────────────
Write-Output "Downloading IngestCSV.ps1..."
$maxAttempts = 3
for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
    try {
        Invoke-WebRequest -Uri $IngestScriptUrl -OutFile $ingestScriptPath -UseBasicParsing
        break
    } catch {
        if ($attempt -eq $maxAttempts) {
            throw "Failed to download IngestCSV.ps1 after $maxAttempts attempts: $_"
        }
        Write-Warning "Download attempt $attempt failed. Retrying..."
        Start-Sleep -Seconds ([math]::Pow(2, $attempt))
    }
}

# ── Run ingestion ────────────────────────────────────────────────────────────
$ingestArgs = @{
    SubscriptionId      = $SubscriptionId
    ResourceGroupName   = $ResourceGroupName
    WorkspaceName       = $WorkspaceName
    TemplatesOutputPath = $templatesPath
    Deploy              = $true
    Ingest              = $true
}

if ($hasCustom) {
    $ingestArgs.TelemetryPath = $customCsvPath
}

if ($hasBuiltIn) {
    $ingestArgs.BuiltInTelemetryPath = $builtInCsvPath
    $ingestArgs.DeployBuiltInDcr     = $true
}

Write-Output "`n=========================================="
Write-Output " Starting ingestion"
Write-Output "=========================================="
Write-Output "Subscription:   $SubscriptionId"
Write-Output "Resource Group: $ResourceGroupName"
Write-Output "Workspace:      $WorkspaceName"
if ($hasCustom)  { Write-Output "Custom CSVs:    $customCount file(s)" }
if ($hasBuiltIn) { Write-Output "Built-in CSVs:  $builtInCount file(s)" }
Write-Output "==========================================`n"

& $ingestScriptPath @ingestArgs
