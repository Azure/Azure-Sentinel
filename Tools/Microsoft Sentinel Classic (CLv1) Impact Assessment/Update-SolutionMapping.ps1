#!/usr/bin/env pwsh
#Requires -Version 7.0
<#
.SYNOPSIS
    Regenerates the static solution-mapping.json from upstream Azure-Sentinel CSVs.

.DESCRIPTION
    Downloads the latest Content Hub solution mapping CSVs from the
    Azure-Sentinel Solutions Analyzer and regenerates the static JSON
    lookup used by the PowerShell report and the web app solution matcher.

.EXAMPLE
    ./data/Update-SolutionMapping.ps1

.OUTPUTS
    data/solution-mapping.json          (this folder - used by the PS script)
    src/lib/data/solution-mapping.json  (web app - if the repo root is reachable)
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$ScriptDir   = $PSScriptRoot
$LocalOutput = Join-Path $ScriptDir 'solution-mapping-v2.json'
$WebAppOutput = Join-Path $ScriptDir '..' '..' '..' 'src' 'lib' 'data' 'solution-mapping-v2.json'

$BaseUrl = 'https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Tools/Solutions%20Analyzer'

# ── Helpers ──────────────────────────────────────────────────────────────────

function Get-UpstreamCsv {
    param([string]$FileName)
    $url = "$BaseUrl/$FileName"
    try {
        return Invoke-RestMethod -Uri $url -Method Get -ErrorAction Stop
    }
    catch {
        throw "Failed to fetch ${FileName}: $($_.Exception.Message)"
    }
}

function Split-CsvRow {
    param([string]$Row)
    $fields  = [System.Collections.Generic.List[string]]::new()
    $inQuote = $false
    $current = [System.Text.StringBuilder]::new()

    for ($i = 0; $i -lt $Row.Length; $i++) {
        $ch = $Row[$i]
        if ($ch -eq '"') {
            $inQuote = -not $inQuote
            continue
        }
        if ($ch -eq ',' -and -not $inQuote) {
            $fields.Add($current.ToString())
            [void]$current.Clear()
            continue
        }
        [void]$current.Append($ch)
    }
    $fields.Add($current.ToString())
    return , $fields.ToArray()
}

# ── Main ─────────────────────────────────────────────────────────────────────

Write-Output 'Fetching simplified mapping...'
$simplifiedRaw = Get-UpstreamCsv 'solutions_connectors_tables_mapping_simplified.csv'

Write-Output 'Fetching full mapping for solution metadata...'
$fullRaw = Get-UpstreamCsv 'solutions_connectors_tables_mapping.csv'

# Build table -> unique solution names from simplified CSV (case-sensitive keys to preserve casing like barracuda_CL vs Barracuda_CL)
$tablesToSolutions = [System.Collections.Specialized.OrderedDictionary]::new([StringComparer]::Ordinal)
$simplifiedLines = ($simplifiedRaw.Trim() -split "`n") | Select-Object -Skip 1

foreach ($line in $simplifiedLines) {
    if ($line -match '"([^"]*)","([^"]*)","([^"]*)"') {
        $solutionName = $Matches[1]
        $tableName    = $Matches[3]
        if (-not $tablesToSolutions.Contains($tableName)) {
            $tablesToSolutions[$tableName] = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
        }
        [void]$tablesToSolutions[$tableName].Add($solutionName)
    }
}

# Convert HashSets to sorted arrays (ordinal sort to match JS .sort() — uppercase before lowercase)
foreach ($key in @($tablesToSolutions.Keys)) {
    $sorted = [string[]]@($tablesToSolutions[$key])
    [Array]::Sort($sorted, [StringComparer]::Ordinal)
    $tablesToSolutions[$key] = $sorted
}

# Extract solution metadata from full CSV
$solutionMetadata = [ordered]@{}
$fullLines = ($fullRaw.Trim() -split "`n") | Select-Object -Skip 1

foreach ($line in $fullLines) {
    $fields = Split-CsvRow $line
    $solutionName = $fields[1]
    if (-not $solutionName -or $solutionMetadata.Contains($solutionName)) { continue }

    $meta = [ordered]@{}
    if ($fields[4]) { $meta['publisherId'] = $fields[4] }
    if ($fields[5]) { $meta['offerId']     = $fields[5] }
    if ($fields[3]) { $meta['githubUrl']   = $fields[3] }
    $solutionMetadata[$solutionName] = $meta
}

# Build output structure
$output = [ordered]@{
    generatedAt      = (Get-Date -Format 'yyyy-MM-dd')
    sourceUrl        = 'https://github.com/Azure/Azure-Sentinel/tree/master/Tools/Solutions%20Analyzer'
    tableCount       = $tablesToSolutions.Count
    solutionCount    = $solutionMetadata.Count
    tablesToSolutions = $tablesToSolutions
    solutionMetadata  = $solutionMetadata
}

$json = ($output | ConvertTo-Json -Depth 10) + "`n"

Set-Content -Path $LocalOutput -Value $json -Encoding UTF8 -NoNewline
Write-Output "`nWritten to $LocalOutput"

$webAppDir = Split-Path $WebAppOutput -Parent
if (Test-Path $webAppDir) {
    Set-Content -Path $WebAppOutput -Value $json -Encoding UTF8 -NoNewline
    Write-Output "Written to $WebAppOutput"
}
else {
    Write-Output "Skipped web app output ($webAppDir not found)"
}

Write-Output "  Tables:    $($output.tableCount)"
Write-Output "  Solutions: $($output.solutionCount)"
