<#
.SYNOPSIS
    Phase 3 sample-data orchestrator. Reads scenarios/tier0-attacker-investigation.json
    + config/entities.json + schemas/*.json, synthesises ~51 correlated records that
    satisfy the 7 detection scenarios in config/use-case-brief.md, and calls the per-table
    ingestion engine (Invoke-SampleDataIngestion.ps1) for each table in dependency order.

.DESCRIPTION
    Resolves a small DSL embedded in the scenario JSON:
      @entities.<dotted.path>            -> object/array from config/entities.json
      @entities.<path>[N]                -> indexed access
      @entities.<path>[*]                -> fan-out (array expansion); valid in `from`
      @now                               -> ISO-8601 anchor (t0)
      @now-Nh / @now-Nm / @now-Nd / @now-Ns  -> offset from t0 (e.g. @now-1h, @now-30m)
      @now-1h57m+4s                      -> compound + leftover-seconds offset
      $.field                            -> projection from iteration context
      ${FieldName}                       -> in-string interpolation from already-resolved fields
      "$.x | fallback($.y)"              -> pipe fallback (left if non-null/non-empty else right)

    Source modes per table entry:
      "source":"directProjection" + "from":"@entities.X[, @entities.Y[*]]" + "fieldMap":{...}
        -> iterates over the union of resolved sources and applies fieldMap per item
      "source":"explicit" + "records":[...]
        -> each record is resolved through the DSL as-is

    Extensibility verbs (-Verb parameter):
      generate_baseline   (default) -> deploy + ingest the full scenario
      extend_scenario     -> append N records to a named table (requires -ExtendTable + -ExtendCount)
      add_table           -> placeholder; requires the developer to add the table entry to the
                              scenario JSON + a schema file first; orchestrator then deploys + ingests it
      validate_coverage   -> dry-run: resolve + write records JSON without ingesting

.PARAMETER ScenarioPath
    Path to scenarios JSON. Default: scenarios/tier0-attacker-investigation.json

.PARAMETER EntitiesPath
    Path to entities JSON. Default: config/entities.json

.PARAMETER SchemasDir
    Directory containing <Table>.json column manifests. Default: schemas/

.PARAMETER SubscriptionId
    Azure subscription. If not specified, loaded from config/workspace.json (Phase 2 onboarding).

.PARAMETER ResourceGroup
    Workspace RG. If not specified, loaded from config/workspace.json.

.PARAMETER WorkspaceName
    Log Analytics workspace. If not specified, loaded from config/workspace.json.

.PARAMETER Location
    Azure region for DCE/DCRs. If not specified, loaded from config/workspace.json.

.PARAMETER DceName
    Shared DCE name. Default: dce-saa-shared.

.PARAMETER Verb
    Orchestration verb (see DESCRIPTION). Default: generate_baseline.

.PARAMETER ExtendTable
    Required for verb=extend_scenario; e.g. "LightningIOEResults_CL".

.PARAMETER ExtendCount
    Required for verb=extend_scenario; integer number of additional records to synthesise.

.PARAMETER OnlyTable
    Optional. If set, only this single table is processed (debug / partial run).

.PARAMETER OutputDir
    Where intermediate per-table records JSON files are written. Default: artifacts/records/.

.PARAMETER SkipIngestion
    If set, resolves and writes records JSON but does NOT call the engine.

.EXAMPLE
    pwsh ./scripts/Invoke-AttackScenarioIngestion.ps1

.EXAMPLE
    pwsh ./scripts/Invoke-AttackScenarioIngestion.ps1 -Verb validate_coverage

.EXAMPLE
    pwsh ./scripts/Invoke-AttackScenarioIngestion.ps1 -Verb extend_scenario `
         -ExtendTable LightningIOEResults_CL -ExtendCount 10
#>

[CmdletBinding()]
param(
    [string]$ScenarioPath  = "$PSScriptRoot/../scenarios/tier0-attacker-investigation.json",
    [string]$EntitiesPath  = "$PSScriptRoot/../config/entities.json",
    [string]$SchemasDir    = "$PSScriptRoot/../schemas",
    [string]$SubscriptionId,
    [string]$ResourceGroup,
    [string]$WorkspaceName,
    [string]$Location,
    [string]$DceName        = "dce-saa-shared",
    [ValidateSet('generate_baseline','extend_scenario','add_table','validate_coverage')]
    [string]$Verb           = 'generate_baseline',
    [string]$ExtendTable,
    [int]   $ExtendCount,
    [string]$OnlyTable,
    [string]$OutputDir      = "$PSScriptRoot/../artifacts/records",
    [switch]$SkipIngestion
)

$ErrorActionPreference = 'Stop'
$script:T0 = $null  # anchor; set after loading scenario

# ---------------- workspace context loader -----------------
# Per Phase 2 onboarding: env-discovery values (sub/rg/workspace/region) are persisted
# in config/workspace.json. Resolve any unset params from there. Explicit -Param values win.
$workspaceConfigPath = Join-Path $PSScriptRoot "../config/workspace.json"
if (Test-Path $workspaceConfigPath) {
    $wsCfg = Get-Content $workspaceConfigPath -Raw | ConvertFrom-Json
    if (-not $SubscriptionId) { $SubscriptionId = $wsCfg.subscriptionId }
    if (-not $ResourceGroup)  { $ResourceGroup  = $wsCfg.resourceGroup }
    if (-not $WorkspaceName)  { $WorkspaceName  = $wsCfg.workspaceName }
    if (-not $Location)       { $Location       = $wsCfg.region }
}
foreach ($req in @('SubscriptionId','ResourceGroup','WorkspaceName','Location')) {
    if (-not (Get-Variable $req -ValueOnly -ErrorAction SilentlyContinue)) {
        throw "Required value '$req' is not set. Pass it explicitly or populate config/workspace.json (Phase 2 onboarding)."
    }
}

# ---------------- helpers -----------------
function Write-Step($m) { Write-Host "`n=== $m ===" -ForegroundColor Cyan }
function Write-Ok  ($m) { Write-Host "✅ $m" -ForegroundColor Green }
function Write-Info($m) { Write-Host "ℹ  $m" -ForegroundColor Gray }
function Write-Warn2($m){ Write-Host "⚠  $m" -ForegroundColor Yellow }

function ConvertTo-Hashtable {
    # Recursively convert PSCustomObject (from ConvertFrom-Json) to ordered hashtable so we can
    # mutate field-by-field without fighting the read-only NoteProperty cells.
    param($obj)
    if ($null -eq $obj) { return $null }
    if ($obj -is [System.Collections.IDictionary]) {
        $h = [ordered]@{}
        foreach ($k in $obj.Keys) { $h[$k] = ConvertTo-Hashtable $obj[$k] }
        return $h
    }
    if ($obj -is [System.Collections.IEnumerable] -and -not ($obj -is [string])) {
        $a = @()
        foreach ($i in $obj) { $a += ,(ConvertTo-Hashtable $i) }
        return ,$a
    }
    if ($obj -is [psobject] -and $obj.PSObject.Properties.Count -gt 0) {
        $h = [ordered]@{}
        foreach ($p in $obj.PSObject.Properties) { $h[$p.Name] = ConvertTo-Hashtable $p.Value }
        return $h
    }
    return $obj
}

# ---------------- DSL: entity path resolver ----------------
function Resolve-EntityPath {
    param([string]$Expr, $Root)
    # Expr is something like "subjects.primary" or "tier0Nodes[2]" or "subjects.alternates[*]"
    # Returns the resolved value (object/array/scalar). [*] yields an array.
    $node = $Root
    foreach ($tok in ($Expr -split '\.')) {
        if ($null -eq $node) { return $null }
        # Split on [...] segments
        $m = [regex]::Match($tok, '^([A-Za-z0-9_]+)((?:\[[^\]]+\])*)$')
        if (-not $m.Success) {
            throw "Resolve-EntityPath: invalid token '$tok' in expression '$Expr'"
        }
        $name = $m.Groups[1].Value
        if ($node -is [System.Collections.IDictionary]) { $node = $node[$name] }
        else { $node = $node.$name }
        # Apply each [index] suffix
        foreach ($idx in [regex]::Matches($m.Groups[2].Value, '\[([^\]]+)\]')) {
            $key = $idx.Groups[1].Value
            if ($key -eq '*') { continue }   # wildcard handled by caller (fan-out)
            if ($key -match '^\d+$') { $node = $node[[int]$key] }
            else { if ($node -is [System.Collections.IDictionary]) { $node = $node[$key] } else { $node = $node.$key } }
            if ($null -eq $node) { return $null }
        }
    }
    return $node
}

function Test-IsWildcardPath { param([string]$Expr) return ($Expr -match '\[\*\]') }

function Resolve-FanoutSource {
    # Resolves a 'from' string which can be comma-separated multiple entity paths,
    # each optionally ending in [*]. Returns flat array of items.
    param([string]$From, $Entities)
    $items = @()
    foreach ($part in ($From -split ',\s*')) {
        if ($part -notmatch '^@entities\.') { throw "Resolve-FanoutSource: 'from' part must start with @entities. (got '$part')" }
        $expr = $part.Substring('@entities.'.Length)
        if ($expr -match '\[\*\]$') {
            $base = $expr -replace '\[\*\]$',''
            $arr  = Resolve-EntityPath -Expr $base -Root $Entities
            if ($null -eq $arr) { continue }
            foreach ($it in $arr) { $items += ,$it }
        } else {
            $v = Resolve-EntityPath -Expr $expr -Root $Entities
            if ($null -ne $v) {
                if ($v -is [System.Collections.IEnumerable] -and -not ($v -is [string]) -and -not ($v -is [System.Collections.IDictionary])) {
                    foreach ($it in $v) { $items += ,$it }
                } else {
                    $items += ,$v
                }
            }
        }
    }
    return ,$items
}

# ---------------- DSL: time offset resolver ----------------
function Resolve-Time {
    # Accepts:  @now , @now-2h , @now-1h57m , @now-2h+5s , @now-1h52m+6s , @now-30m , @now-7d
    param([string]$Expr, [datetime]$T0)
    if ($Expr -eq '@now' -or $Expr -eq 'now') { return $T0.ToString('yyyy-MM-ddTHH:mm:ssZ') }
    if ($Expr -notmatch '^@?now') { throw "Resolve-Time: not a time expression: $Expr" }
    $rest = $Expr -replace '^@?now',''
    $t = $T0
    foreach ($m in [regex]::Matches($rest, '([+\-])(\d+)([smhd])')) {
        $sign = if ($m.Groups[1].Value -eq '-') { -1 } else { 1 }
        $num  = [int]$m.Groups[2].Value * $sign
        switch ($m.Groups[3].Value) {
            's' { $t = $t.AddSeconds($num) }
            'm' { $t = $t.AddMinutes($num) }
            'h' { $t = $t.AddHours($num) }
            'd' { $t = $t.AddDays($num) }
        }
    }
    return $t.ToString('yyyy-MM-ddTHH:mm:ssZ')
}

# ---------------- DSL: value resolver (recursive) ----------------
function Resolve-Value {
    <#
      $Value      : raw value (string / number / bool / hashtable / array)
      $Context    : iteration item for $.field projection (hashtable or PSCustomObject) — may be $null
      $Entities   : root entities hashtable
      $Resolved   : already-resolved sibling fields (hashtable) for ${Field} interpolation
    #>
    param($Value, $Context, $Entities, $Resolved)

    if ($null -eq $Value) { return $null }

    # Dictionaries: recurse
    if ($Value -is [System.Collections.IDictionary]) {
        $out = [ordered]@{}
        foreach ($k in $Value.Keys) {
            $out[$k] = Resolve-Value -Value $Value[$k] -Context $Context -Entities $Entities -Resolved $out
        }
        return $out
    }

    # Arrays: recurse element-wise (return non-null result as plain array)
    if ($Value -is [System.Collections.IEnumerable] -and -not ($Value -is [string])) {
        $out = @()
        foreach ($el in $Value) {
            $out += ,(Resolve-Value -Value $el -Context $Context -Entities $Entities -Resolved $Resolved)
        }
        return ,$out
    }

    # Strings: apply DSL
    if ($Value -is [string]) {
        return Resolve-StringExpression -Expr $Value -Context $Context -Entities $Entities -Resolved $Resolved
    }

    # Scalars (int, bool, double): pass through
    return $Value
}

function Resolve-StringExpression {
    param([string]$Expr, $Context, $Entities, $Resolved)

    # Pipe fallback: "X | fallback(Y)"
    if ($Expr -match '^\s*(.+?)\s*\|\s*fallback\(\s*(.+?)\s*\)\s*$') {
        $left  = Resolve-StringExpression -Expr $Matches[1] -Context $Context -Entities $Entities -Resolved $Resolved
        if ($null -ne $left -and -not ([string]::IsNullOrWhiteSpace([string]$left))) { return $left }
        return  Resolve-StringExpression -Expr $Matches[2] -Context $Context -Entities $Entities -Resolved $Resolved
    }

    # @entities.<path>
    if ($Expr -match '^@entities\.(.+)$') {
        return Resolve-EntityPath -Expr $Matches[1] -Root $Entities
    }

    # @now... time offsets
    if ($Expr -match '^@?now($|[+\-])') {
        return Resolve-Time -Expr $Expr -T0 $script:T0
    }

    # $.field direct projection from iteration context
    if ($Expr -match '^\$\.(.+)$') {
        if ($null -eq $Context) { return $null }
        $field = $Matches[1]
        if ($Context -is [System.Collections.IDictionary]) { return $Context[$field] }
        return $Context.$field
    }

    # ${field} sibling interpolation (replace each occurrence with already-resolved sibling)
    if ($Expr -match '\$\{[A-Za-z0-9_]+\}') {
        $result = $Expr
        foreach ($m in [regex]::Matches($Expr, '\$\{([A-Za-z0-9_]+)\}')) {
            $name = $m.Groups[1].Value
            $repl = $null
            if ($null -ne $Resolved -and $Resolved.Contains($name)) { $repl = [string]$Resolved[$name] }
            elseif ($null -ne $Context) {
                if ($Context -is [System.Collections.IDictionary] -and $Context.Contains($name)) { $repl = [string]$Context[$name] }
                elseif ($Context.PSObject -and $Context.PSObject.Properties[$name]) { $repl = [string]$Context.$name }
            }
            $result = $result.Replace($m.Value, [string]$repl)
        }
        return $result
    }

    # Plain string literal
    return $Expr
}

# ---------------- Record synthesis ----------------
function New-RecordsFromDirectProjection {
    param($Table, $Entities)
    $items = Resolve-FanoutSource -From $Table.from -Entities $Entities
    $out = @()
    foreach ($item in $items) {
        $rec = [ordered]@{}
        foreach ($k in $Table.fieldMap.Keys) {
            $rec[$k] = Resolve-Value -Value $Table.fieldMap[$k] -Context $item -Entities $Entities -Resolved $rec
        }
        $out += ,$rec
    }
    return ,$out
}

function New-RecordsFromExplicit {
    param($Table, $Entities)
    $out = @()
    foreach ($rec in $Table.records) {
        $resolved = Resolve-Value -Value $rec -Context $null -Entities $Entities -Resolved $null
        $out += ,$resolved
    }
    return ,$out
}

function New-ExtendedRecords {
    # Synthesise N additional explicit-style records by cloning the last record of the table,
    # nudging TimeGenerated by -1m per clone, and tagging with a suffix to keep IDs unique.
    param($Table, $Entities, [int]$Count)
    if ($Table.source -ne 'explicit') {
        throw "extend_scenario currently supports only explicit-source tables. Table '$($Table.name)' is '$($Table.source)'."
    }
    $template = $Table.records[-1]
    $resolvedTemplate = Resolve-Value -Value $template -Context $null -Entities $Entities -Resolved $null
    $out = @()
    for ($i = 1; $i -le $Count; $i++) {
        $clone = [ordered]@{}
        foreach ($k in $resolvedTemplate.Keys) { $clone[$k] = $resolvedTemplate[$k] }
        if ($clone.Contains('TimeGenerated')) {
            try {
                $tg = [datetime]::Parse($clone['TimeGenerated'])
                $clone['TimeGenerated'] = $tg.AddMinutes(-1 * $i).ToString('yyyy-MM-ddTHH:mm:ssZ')
            } catch { Write-Warn2 "extend_scenario: could not parse TimeGenerated on clone $i; leaving as-is." }
        }
        # Append disambiguating suffix to first *Id-like field we find
        foreach ($k in @('ResultId','ExecutionId','SystemAlertId','LogonId','PathId','ReportId')) {
            if ($clone.Contains($k)) { $clone[$k] = "$($clone[$k])-ext$i"; break }
        }
        $out += ,$clone
    }
    return ,$out
}

# ---------------- main ----------------
Write-Step "Load scenario + entities"
if (-not (Test-Path $ScenarioPath)) { throw "Scenario file not found: $ScenarioPath" }
if (-not (Test-Path $EntitiesPath)) { throw "Entities file not found: $EntitiesPath" }
$rawScenario = Get-Content -Raw $ScenarioPath | ConvertFrom-Json
$rawEntities = Get-Content -Raw $EntitiesPath | ConvertFrom-Json
$scenario = ConvertTo-Hashtable $rawScenario
$entities = ConvertTo-Hashtable $rawEntities
Write-Ok  "Scenario: $($scenario.scenarioId) v$($scenario.version)"
Write-Info "Tables in order: $($scenario.ingestionOrder -join ', ')"

# Anchor t0
$baseUtc = $entities.timing.baseTimeUtc
if ([string]::IsNullOrWhiteSpace($baseUtc)) {
    $script:T0 = (Get-Date).ToUniversalTime().AddHours(-2)
    Write-Info "Anchor t0 (default): $($script:T0.ToString('o'))"
} else {
    $script:T0 = [datetime]::Parse($baseUtc).ToUniversalTime()
    Write-Info "Anchor t0 (from entities): $($script:T0.ToString('o'))"
}

# Ensure output dir
$null = New-Item -ItemType Directory -Force -Path $OutputDir
Write-Info "Records output dir: $OutputDir"

# Pin az CLI context to the target subscription so the engine (which relies on
# the current az context for ARM calls) targets the right tenant/subscription.
if ($SubscriptionId) {
    $null = az account set --subscription $SubscriptionId 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Failed to set az subscription context to '$SubscriptionId'. Run 'az login' first." }
    Write-Info "az subscription context: $SubscriptionId"
}

# Step 0 — RBAC pre-grant at RG scope.
# Granting 'Monitoring Metrics Publisher' once at the resource-group scope
# (instead of per-DCR after each DCR is created) avoids the Azure data-plane
# cold-start negative-cache that produces a 15+ minute 403 storm on freshly
# minted DCRs. Every per-table call below passes -SkipRbac since we've
# already established the grant here.
if (-not $SkipIngestion) {
    Write-Step "Pre-granting 'Monitoring Metrics Publisher' at RG scope"
    & "$PSScriptRoot/Grant-IngestionRbac.ps1" -ResourceGroupName $ResourceGroup | Out-Null
}

# Verb dispatch ----------------
if ($Verb -eq 'extend_scenario') {
    if (-not $ExtendTable) { throw "-ExtendTable is required for verb=extend_scenario" }
    if (-not $ExtendCount -or $ExtendCount -le 0) { throw "-ExtendCount must be a positive integer" }
    $tbl = $scenario.tables | Where-Object { $_.name -eq $ExtendTable }
    if (-not $tbl) { throw "ExtendTable '$ExtendTable' not found in scenario.tables[]" }
    $records = New-ExtendedRecords -Table $tbl -Entities $entities -Count $ExtendCount
    $outFile = Join-Path $OutputDir "$ExtendTable.ext.json"
    $records | ConvertTo-Json -Depth 30 | Set-Content -Path $outFile -Encoding UTF8
    Write-Ok "Wrote $ExtendCount extended records -> $outFile"
    if (-not $SkipIngestion) {
        $schemaFile = Join-Path $SchemasDir "$ExtendTable.json"
        & "$PSScriptRoot/Invoke-SampleDataIngestion.ps1" `
            -SchemaPath $schemaFile -RecordsJsonPath $outFile `
            -ResourceGroupName $ResourceGroup -WorkspaceName $WorkspaceName `
            -Location $Location -DceName $DceName -SkipRbac
    }
    return
}

# generate_baseline | validate_coverage | add_table fall through to full-loop
$dryRun = $SkipIngestion -or ($Verb -eq 'validate_coverage')
if ($dryRun) { Write-Warn2 "Dry-run mode: records will be resolved + written but NOT ingested." }

$summary = @()
$totalRecords = 0
foreach ($tableName in $scenario.ingestionOrder) {
    if ($OnlyTable -and $OnlyTable -ne $tableName) { continue }
    Write-Step "Process table: $tableName"
    $tbl = $scenario.tables | Where-Object { $_.name -eq $tableName }
    if (-not $tbl) { throw "Table '$tableName' is in ingestionOrder but not in tables[]" }

    if     ($tbl.source -eq 'directProjection') { $records = New-RecordsFromDirectProjection -Table $tbl -Entities $entities }
    elseif ($tbl.source -eq 'explicit')         { $records = New-RecordsFromExplicit         -Table $tbl -Entities $entities }
    else { throw "Unknown source '$($tbl.source)' on table '$tableName'" }

    if ($tbl.recordCount -and $records.Count -ne $tbl.recordCount) {
        Write-Warn2 "Record count mismatch on '$tableName': expected $($tbl.recordCount), got $($records.Count)"
    }

    # Sanity: every record must have TimeGenerated populated.
    foreach ($r in $records) {
        if (-not ($r.Contains('TimeGenerated')) -or [string]::IsNullOrWhiteSpace([string]$r['TimeGenerated'])) {
            throw "Record on '$tableName' is missing TimeGenerated after DSL resolution."
        }
    }

    $outFile = Join-Path $OutputDir "$tableName.json"
    $records | ConvertTo-Json -Depth 30 | Set-Content -Path $outFile -Encoding UTF8
    Write-Ok "Wrote $($records.Count) records -> $outFile"
    $totalRecords += $records.Count

    if (-not $dryRun) {
        $schemaFile = Join-Path $SchemasDir "$tableName.json"
        if (-not (Test-Path $schemaFile)) { throw "Schema file not found for '$tableName': $schemaFile" }
        & "$PSScriptRoot/Invoke-SampleDataIngestion.ps1" `
            -SchemaPath $schemaFile -RecordsJsonPath $outFile `
            -ResourceGroupName $ResourceGroup -WorkspaceName $WorkspaceName `
            -Location $Location -DceName $DceName -SkipRbac
    }

    $summary += [pscustomobject]@{ Table = $tableName; Records = $records.Count; OutputFile = $outFile }
}

Write-Step "Summary"
$summary | Format-Table -AutoSize | Out-Host
Write-Ok "Total records resolved: $totalRecords (expected ~$($scenario.validation.totalRecordsExpected))"
if ($dryRun) {
    Write-Info "Dry-run complete. Re-run without -SkipIngestion / with -Verb generate_baseline to ingest."
} else {
    Write-Ok "All tables processed. Wait 5-10 min then run scripts/Validate-Ingestion.ps1."
}

return [pscustomobject]@{
    ScenarioId   = $scenario.scenarioId
    Anchor       = $script:T0.ToString('o')
    TotalRecords = $totalRecords
    Tables       = $summary
    DryRun       = $dryRun
    Verb         = $Verb
}
