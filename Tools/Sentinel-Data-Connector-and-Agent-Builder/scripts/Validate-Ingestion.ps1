<#
.SYNOPSIS
    Validates that data has actually been ingested into Sentinel tables.
.DESCRIPTION
    Run this AFTER completing data ingestion via the DCR + Logs Ingestion API path
    (orchestrated by Invoke-AttackScenarioIngestion.ps1).
    Queries each target table to confirm rows exist and reports row counts, latest
    TimeGenerated, and ingestion freshness. Accounts for ingestion latency (~5-10 min
    after the last POST to the Logs Ingestion API).

    Tables in the Analytics tier (*_CL or native tables like SigninLogs) are queried
    via `az monitor log-analytics query`.

.PARAMETER SubscriptionId
    Azure subscription containing the Log Analytics workspace.
.PARAMETER ResourceGroupName
    Resource group containing the workspace.
.PARAMETER WorkspaceName
    Log Analytics workspace name.
.PARAMETER Tables
    Array of table names to validate (custom *_CL tables and/or native tables).
.PARAMETER LookbackHours
    How far back to look for ingested rows. Default: 24.
.PARAMETER MinRows
    Minimum row count required to consider a table 'ingested'. Default: 1.

.EXAMPLE
    # Validate DCR-ingested custom table
    ./Validate-Ingestion.ps1 -SubscriptionId "<subscription-id>" -ResourceGroupName "<resource-group>" `
        -WorkspaceName "<workspace>" -Tables @("ISVProductLogs_CL")

.EXAMPLE
    # Validate a mix of ISV custom table + native-table shadow_CL + native table
    ./Validate-Ingestion.ps1 -SubscriptionId "<subscription-id>" -ResourceGroupName "<resource-group>" `
        -WorkspaceName "<workspace>" `
        -Tables @("ISVProductLogs_CL", "SigninLogs_CL", "SecurityAlert")
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SubscriptionId,

    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory=$true)]
    [string]$WorkspaceName,

    [Parameter(Mandatory=$true)]
    [string[]]$Tables,

    [Parameter(Mandatory=$false)]
    [int]$LookbackHours = 24,

    [Parameter(Mandatory=$false)]
    [int]$MinRows = 1,

    [Parameter(Mandatory=$false)]
    [string]$ScenarioPath
)

$ErrorActionPreference = "Stop"

function Write-Status($msg, $status) {
    $icon = if ($status -eq "pass") { "✅" } elseif ($status -eq "fail") { "❌" } else { "⚠️" }
    Write-Host "$icon $msg"
}

Write-Host "`n=== Validating Data Ingestion ===`n"
Write-Host "Workspace : $WorkspaceName"
Write-Host "Lookback  : Last $LookbackHours hour(s)"
Write-Host "Tables    : $($Tables -join ', ')`n"

az account set --subscription $SubscriptionId 2>$null | Out-Null

# Get workspace customerId (for Data Lake KQL API db name) and resourceId
$ws = az monitor log-analytics workspace show `
    --resource-group $ResourceGroupName `
    --workspace-name $WorkspaceName `
    --output json 2>$null | ConvertFrom-Json

if (-not $ws) {
    Write-Status "Workspace '$WorkspaceName' not found in '$ResourceGroupName'" "fail"
    exit 1
}

$workspaceId = $ws.customerId
Write-Status "Workspace resolved: customerId = $workspaceId" "pass"

# Track results
$results = @()

foreach ($table in $Tables) {
    Write-Host "`n--- Validating: $table ---"

    $kql = "$table | where TimeGenerated > ago(${LookbackHours}h) | summarize Rows=count(), Latest=max(TimeGenerated)"

    # Query via Log Analytics (Analytics tier covers all custom *_CL and native tables)
    Write-Host "Tier: Analytics (querying via Log Analytics)"

    try {
        $qr = az monitor log-analytics query `
            --workspace $workspaceId `
            --analytics-query $kql `
            --output json 2>$null | ConvertFrom-Json

        if ($qr -and $qr.Count -gt 0) {
            $rows = [int]$qr[0].Rows
            $latest = $qr[0].Latest
        } else {
            $rows = 0; $latest = $null
        }
    } catch {
        Write-Status "Log Analytics query failed (table may not exist yet): $($_.Exception.Message)" "fail"
        $results += [pscustomobject]@{ Table=$table; Tier="Analytics"; Rows=0; Latest=$null; Status="fail"; Reason="query-error" }
        continue
    }

    # Evaluate
    if ($rows -ge $MinRows) {
        Write-Status "$table → $rows rows (latest: $latest)" "pass"
        $results += [pscustomobject]@{ Table=$table; Tier="Analytics"; Rows=$rows; Latest=$latest; Status="pass"; Reason="" }
    } else {
        Write-Status "$table → 0 rows in last $LookbackHours h" "warn"
        $results += [pscustomobject]@{ Table=$table; Tier="Analytics"; Rows=0; Latest=$null; Status="warn"; Reason="no-data" }
    }
}

# Summary
Write-Host "`n=== Ingestion Validation Summary ===`n"
$results | Format-Table -AutoSize

$failed = @($results | Where-Object { $_.Status -ne "pass" })
$passed = @($results | Where-Object { $_.Status -eq "pass" })

Write-Host "Passed : $($passed.Count) / $($results.Count)"
Write-Host "Failed : $($failed.Count) / $($results.Count)"

if ($failed.Count -gt 0) {
    Write-Host "`n--- Troubleshooting Empty Tables ---`n"
    Write-Host "Common causes when a table has 0 rows (DCR / Logs Ingestion API path):"
    Write-Host ""
    Write-Host "  1. Ingestion latency: data takes 5-10 minutes to appear after POST."
    Write-Host "     → Wait 10 minutes, then re-run this script."
    Write-Host "  2. DCR transform KQL dropped all rows."
    Write-Host "     → Inspect DCR's 'transformKql' for filters that exclude your sample data."
    Write-Host "  3. Schema mismatch between DCR streamDeclaration and target table."
    Write-Host "     → Verify column names/types align (TimeGenerated must be present)."
    Write-Host "  4. Identity sending data lacks 'Monitoring Metrics Publisher' role on DCR."
    Write-Host "     → az role assignment create --assignee <sp> --role 'Monitoring Metrics Publisher' --scope <dcr-id>"
    Write-Host "  5. Wrong DCE region or DCR streamName mismatch ('Custom-<name>' must match DCR)."
    Write-Host "  6. For native tables (e.g., SigninLogs, SecurityAlert): the Logs Ingestion API cannot"
    Write-Host "     write to first-party tables. Use a shadow *_CL table (e.g., SigninLogs_CL) for"
    Write-Host "     dev/test, mirror the native schema, and reference the *_CL name in agent instructions."
    Write-Host ""
    exit 1
}

Write-Host "`n✅ All tables have ingested data. Ingestion validated end-to-end.`n"

# -----------------------------------------------------------------------------
# Phase 3: Detection-scenario coverage assertions (optional)
# -----------------------------------------------------------------------------
if ($ScenarioPath) {
    if (-not (Test-Path $ScenarioPath)) {
        Write-Status "Scenario file not found: $ScenarioPath" "fail"
        exit 1
    }

    Write-Host "`n=== Detection-Scenario Coverage ===`n"
    Write-Host "Scenario file : $ScenarioPath`n"

    $scenarioJson = Get-Content $ScenarioPath -Raw | ConvertFrom-Json
    $coverage = $scenarioJson.scenarioCoverage
    if (-not $coverage) {
        Write-Status "scenarioCoverage[] missing from $ScenarioPath" "fail"
        exit 1
    }

    $scenarioResults = @()
    foreach ($sc in $coverage) {
        Write-Host "--- Scenario $($sc.id): $($sc.name) ---"
        Write-Host "Tables : $($sc.tables -join ', ')"
        Write-Host "Min    : $($sc.expectedMinHits)"

        try {
            $qr = az monitor log-analytics query `
                --workspace $workspaceId `
                --analytics-query $sc.kqlAssertion `
                --output json 2>$null | ConvertFrom-Json

            $count = 0
            if ($qr -and $qr.Count -gt 0) {
                # `| count` returns single row with single 'Count' column
                $row = $qr[0]
                foreach ($prop in $row.PSObject.Properties) {
                    if ($prop.Name -match '^(Count|Count_)$') { $count = [int]$prop.Value; break }
                }
                if ($count -eq 0) {
                    # fallback: first numeric property
                    foreach ($prop in $row.PSObject.Properties) {
                        if ($prop.Value -is [int] -or $prop.Value -is [long]) { $count = [int]$prop.Value; break }
                    }
                }
            }

            if ($count -ge $sc.expectedMinHits) {
                Write-Status "Scenario $($sc.id) → $count hits (>= $($sc.expectedMinHits))" "pass"
                $scenarioResults += [pscustomobject]@{ Id=$sc.id; Name=$sc.name; Hits=$count; Min=$sc.expectedMinHits; Status="pass" }
            } else {
                Write-Status "Scenario $($sc.id) → $count hits (< $($sc.expectedMinHits))" "fail"
                $scenarioResults += [pscustomobject]@{ Id=$sc.id; Name=$sc.name; Hits=$count; Min=$sc.expectedMinHits; Status="fail" }
            }
        } catch {
            Write-Status "Scenario $($sc.id) query failed: $($_.Exception.Message)" "fail"
            $scenarioResults += [pscustomobject]@{ Id=$sc.id; Name=$sc.name; Hits=0; Min=$sc.expectedMinHits; Status="fail" }
        }
        Write-Host ""
    }

    Write-Host "=== Scenario Coverage Summary ===`n"
    $scenarioResults | Format-Table -AutoSize

    $scFailed = @($scenarioResults | Where-Object { $_.Status -ne "pass" })
    $scPassed = @($scenarioResults | Where-Object { $_.Status -eq "pass" })
    Write-Host "Scenarios passed : $($scPassed.Count) / $($scenarioResults.Count)"
    Write-Host "Scenarios failed : $($scFailed.Count) / $($scenarioResults.Count)"

    if ($scFailed.Count -gt 0) {
        Write-Host "`n❌ One or more detection scenarios failed coverage assertion." -ForegroundColor Red
        Write-Host "   Likely causes: ingestion latency, missing correlation keys, or schema mismatch.`n"
        exit 1
    }

    Write-Host "`n✅ All $($scenarioResults.Count) detection scenarios satisfied.`n"
}

exit 0
