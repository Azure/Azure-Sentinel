<#
.SYNOPSIS
    Validates Security Copilot agent instructions by trial-running every embedded
    KQL query against the Sentinel data lake (KQL Queries REST API).

.DESCRIPTION
    The agent generates Security Copilot agent instructions from the lab-05
    template (https://github.com/suchandanreddy/Microsoft-Sentinel-Labs/blob/main/05-Building-an-Agent-in-Security-Copilot.md).
    Each "Per-table query" section embeds a sample KQL snippet that the SCC agent
    will execute at run-time. If any of those snippets has a schema mismatch,
    missing column, or syntax error, the published agent will fail in production.

    This script is the **mandatory pre-flight gate**: it extracts every fenced
    ```kql / ```kusto block from the draft instructions, substitutes the input
    placeholders (e.g. {{UserPrincipalName}}) with a synthetic test value, and
    POSTs each query to the data lake KQL Queries API:

        POST https://api.securityplatform.microsoft.com/lake/kql/v2/rest/query
        Body: { "csl": "<query>", "db": "<WorkspaceName>-<workspaceCustomerId>" }

    Docs: https://learn.microsoft.com/azure/sentinel/datalake/kql-queries-api

    Per-query result is reported as pass / fail / no_data. The agent must iterate
    on the draft and re-run this script until pass==true for every query before
    handing the instructions to the developer.

.PARAMETER InstructionsPath
    Path to the draft instructions markdown file. The script extracts every
    fenced ```kql or ```kusto code block.

.PARAMETER Queries
    Inline array of KQL query strings to validate. Mutually exclusive with
    -InstructionsPath.

.PARAMETER Substitutions
    See expanded description below (under PassOnEmpty).

.PARAMETER WorkspaceName
    Log Analytics workspace name (e.g., '<workspace-name>'). Required to build the `db` field.

.PARAMETER WorkspaceCustomerId
    Workspace customerId (GUID). If omitted, resolved via `az monitor log-analytics
    workspace show` when -ResourceGroup is provided, else read from progress.json.

.PARAMETER ResourceGroup
    Resource group containing the workspace. Optional — only used to resolve
    WorkspaceCustomerId via az cli.

.PARAMETER ProgressFile
    Path to config/progress.json. Used to auto-resolve WorkspaceName /
    WorkspaceCustomerId / ResourceGroup if not supplied. Default:
    <repoRoot>/config/progress.json.

.PARAMETER MaxRows
    Cap rows returned per query (we only care about success vs syntax error,
    not the data). Default 5. Append `| take <MaxRows>` if absent.

.PARAMETER PassOnEmpty
    Treat 0-row responses as pass (default). Schema validity is what we are
    checking — empty result usually means the synthetic input matched no real
    rows, which is fine. Set to $false to require at least one row.

    When ALL queries return HTTP 200 + 0 rows AND -Substitutions is non-empty,
    the script automatically fires a **stripped-filter probe**: it takes query
    #1, removes any line containing a substituted value literal, and re-POSTs
    against the same lake endpoint. The result drives the envelope `verdict`:
      - probe returns rows  → verdict = "substitution_mismatch" (exit 4) —
        the data IS in the lake; -Substitutions value doesn't match a seeded
        entity. Fix `primaryInput.exampleSource` in progress.json (or extend
        config/entities.json + re-ingest Phase 3) and re-run.
      - probe returns 0     → verdict = "lake_pending" (exit 0) — data
        genuinely not yet visible in the lake.
    This discriminator prevents the historical false-signal anti-pattern where
    PassOnEmpty masked a substitution bug as a fake "lake replication delay".

.PARAMETER Substitutions
    Hashtable of placeholder substitutions. Keys are the placeholder names
    (without braces), values are the synthetic test values. Example:
        @{ UserPrincipalName = 'test.user@contoso.com'; SubmissionId = 'b1a2c3d4-...' }
    Both '{{Key}}' and '{Key}' patterns are replaced.

    **Values MUST be sourced from `config/entities.json` via the JSON pointer
    in `progress.json.phases.5_agent_build.primaryInput.exampleSource`** — never
    synthetic/themed examples. Querying with an unseeded value returns 0 rows
    from every block, which the probe above will then correctly flag as
    substitution_mismatch (exit 4).

.PARAMETER TokenResource
    Audience for the access token. Default 'https://api.securityplatform.microsoft.com'.
    Falls back to 'https://purview.azure.net' on 401.

.PARAMETER JsonOutput
    Emit machine-readable JSON envelope on stdout. Human messages go to stderr.

.EXAMPLE
    pwsh ./scripts/Test-AgentInstructions.ps1 `
        -InstructionsPath ./config/agent-instructions/<slug>.md `
        -Substitutions @{ submissionId = 'b1a2c3d4-0001-0001-0001-000000000001' } `
        -JsonOutput

.EXAMPLE
    pwsh ./scripts/Test-AgentInstructions.ps1 `
        -Queries @('<IsvTable>_CL | where Severity <= 2 | summarize count()') `
        -JsonOutput

.NOTES
    Exit codes:
      0 — all queries passed
      1 — one or more queries failed (syntax / schema / runtime error)
      2 — bad input (no instructions or queries supplied, file unreadable)
      3 — auth failed
#>
[CmdletBinding(DefaultParameterSetName = 'FromFile')]
param(
    [Parameter(ParameterSetName = 'FromFile', Mandatory = $true)]
    [string]$InstructionsPath,

    [Parameter(ParameterSetName = 'Inline', Mandatory = $true)]
    [string[]]$Queries,

    [hashtable]$Substitutions = @{},

    [string]$WorkspaceName,
    [string]$WorkspaceCustomerId,
    [string]$ResourceGroup,
    [string]$ProgressFile,

    [int]$MaxRows = 5,
    [bool]$PassOnEmpty = $true,
    [string]$TokenResource = 'https://api.securityplatform.microsoft.com',
    [switch]$JsonOutput
)

$ErrorActionPreference = 'Stop'

function Write-Info($m) { if (-not $JsonOutput) { [Console]::Error.WriteLine("ℹ️  $m") } }
function Write-Ok($m)   { if (-not $JsonOutput) { [Console]::Error.WriteLine("✅ $m") } }
function Write-Warn2($m){ if (-not $JsonOutput) { [Console]::Error.WriteLine("⚠️  $m") } }
function Write-Err($m)  { if (-not $JsonOutput) { [Console]::Error.WriteLine("❌ $m") } }

function Emit-Json($obj) {
    if ($JsonOutput) { ($obj | ConvertTo-Json -Depth 10 -Compress) | Write-Output }
}

# --- Resolve workspace context ----------------------------------------------------
if (-not $ProgressFile) {
    $here = Split-Path -Parent $PSCommandPath
    $ProgressFile = Join-Path (Split-Path -Parent $here) 'config/progress.json'
}

if ((-not $WorkspaceName -or -not $WorkspaceCustomerId) -and (Test-Path $ProgressFile)) {
    try {
        $prog = Get-Content $ProgressFile -Raw | ConvertFrom-Json
        $p2 = $prog.phases.'2_data_lake_onboarding'
        # Support both shapes:
        #   (legacy/flat)  $p2.workspaceName, $p2.workspaceCustomerId, $p2.workspaceResourceGroup
        #   (nested)       $p2.workspace.name, $p2.workspace.customerId, $p2.workspace.resourceGroup
        if (-not $WorkspaceName) {
            if ($p2.workspaceName)          { $WorkspaceName = $p2.workspaceName }
            elseif ($p2.workspace -and $p2.workspace.name) { $WorkspaceName = $p2.workspace.name }
        }
        if (-not $ResourceGroup) {
            if ($p2.workspaceResourceGroup) { $ResourceGroup = $p2.workspaceResourceGroup }
            elseif ($p2.workspace -and $p2.workspace.resourceGroup) { $ResourceGroup = $p2.workspace.resourceGroup }
        }
        if (-not $WorkspaceCustomerId) {
            if ($p2.workspaceCustomerId)    { $WorkspaceCustomerId = $p2.workspaceCustomerId }
            elseif ($p2.workspace -and $p2.workspace.customerId) { $WorkspaceCustomerId = $p2.workspace.customerId }
        }
    } catch {
        Write-Warn2 "Could not parse progress file: $($_.Exception.Message)"
    }
}

if (-not $WorkspaceCustomerId -and $WorkspaceName -and $ResourceGroup) {
    Write-Info "Resolving workspaceCustomerId via az cli..."
    try {
        $cid = az monitor log-analytics workspace show `
            --workspace-name $WorkspaceName --resource-group $ResourceGroup `
            --query customerId -o tsv 2>$null
        if ($LASTEXITCODE -eq 0 -and $cid) { $WorkspaceCustomerId = $cid.Trim() }
    } catch { }
}

if (-not $WorkspaceName -or -not $WorkspaceCustomerId) {
    Write-Err "Need both -WorkspaceName and -WorkspaceCustomerId (or resolvable via -ResourceGroup or progress.json)."
    Emit-Json @{ pass = $false; error = 'missing_workspace_context' }
    exit 2
}

$db = "$WorkspaceName-$WorkspaceCustomerId"
Write-Info "Using db: $db"

# --- Collect queries --------------------------------------------------------------
$rawQueries = @()
$querySources = @()

if ($PSCmdlet.ParameterSetName -eq 'FromFile') {
    if (-not (Test-Path $InstructionsPath)) {
        Write-Err "InstructionsPath not found: $InstructionsPath"
        Emit-Json @{ pass = $false; error = 'instructions_not_found'; path = $InstructionsPath }
        exit 2
    }
    $md = Get-Content $InstructionsPath -Raw
    # Match ```kql ... ``` and ```kusto ... ``` (case-insensitive, multiline)
    $pattern = '(?ims)```\s*(kql|kusto)\s*\r?\n(.*?)\r?\n```'
    $matches = [regex]::Matches($md, $pattern)
    if ($matches.Count -eq 0) {
        Write-Warn2 "No fenced ```kql / ```kusto blocks found in $InstructionsPath"
        Emit-Json @{ pass = $false; error = 'no_kql_blocks'; path = $InstructionsPath }
        exit 2
    }
    $idx = 0
    foreach ($m in $matches) {
        $idx++
        $rawQueries += $m.Groups[2].Value
        $querySources += "block_$idx"
    }
    Write-Info "Extracted $($rawQueries.Count) KQL block(s) from $InstructionsPath"
} else {
    $idx = 0
    foreach ($q in $Queries) {
        $idx++
        $rawQueries += $q
        $querySources += "inline_$idx"
    }
}

# --- Substitute placeholders + cap rows -------------------------------------------
$preparedQueries = @()
foreach ($q in $rawQueries) {
    $cur = $q
    foreach ($k in $Substitutions.Keys) {
        $val = [string]$Substitutions[$k]
        $cur = $cur -replace ('\{\{\s*' + [regex]::Escape($k) + '\s*\}\}'), $val
        $cur = $cur -replace ('(?<!\{)\{\s*' + [regex]::Escape($k) + '\s*\}(?!\})'), $val
    }
    # Ensure we cap rows so we don't drag huge result sets back
    if ($cur -notmatch '\|\s*take\s+\d+' -and $cur -notmatch '\|\s*limit\s+\d+' -and $cur -notmatch '\|\s*top\s+\d+') {
        $cur = $cur.TrimEnd() + " | take $MaxRows"
    }
    $preparedQueries += $cur
}

# --- Detect unsubstituted placeholders --------------------------------------------
$placeholderPattern = '\{\{\s*\w+\s*\}\}'
for ($i = 0; $i -lt $preparedQueries.Count; $i++) {
    if ($preparedQueries[$i] -match $placeholderPattern) {
        $unfilled = ([regex]::Matches($preparedQueries[$i], $placeholderPattern) | ForEach-Object { $_.Value }) -join ', '
        Write-Warn2 "$($querySources[$i]): unsubstituted placeholder(s) detected: $unfilled — query will likely fail. Pass values via -Substitutions."
    }
}

# --- Response row-count extractor (handles v1 and v2 lake formats) ----------------
# The Sentinel Data Lake KQL endpoint returns Kusto v2 streaming JSON: an array of
# frames, each with FrameType / TableKind. The PrimaryResult frame carries Rows[].
# Older Log Analytics-style endpoints return { tables: [ { rows: [...] } ] }.
# Support both so the script works regardless of which endpoint the workspace
# routes to.
function Get-RowCountFromResponse($resp) {
    if ($null -eq $resp) { return 0 }
    # v2 streaming: array of frames
    try {
        $frames = @($resp)
        $primary = $frames | Where-Object {
            $_.FrameType -eq 'DataTable' -and $_.TableKind -eq 'PrimaryResult'
        } | Select-Object -First 1
        if ($primary -and $primary.Rows) { return @($primary.Rows).Count }
    } catch { }
    # v1 LA shape: { tables: [ { rows: [...] } ] }
    try {
        if ($resp.tables -and $resp.tables[0] -and $resp.tables[0].rows) {
            return @($resp.tables[0].rows).Count
        }
    } catch { }
    return 0
}

# --- Acquire token ----------------------------------------------------------------
function Get-Token($audience) {
    try {
        $t = az account get-access-token --resource $audience --query accessToken -o tsv 2>$null
        if ($LASTEXITCODE -eq 0 -and $t) { return $t.Trim() }
    } catch { }
    return $null
}

Write-Info "Acquiring access token (audience: $TokenResource)"
$token = Get-Token $TokenResource
if (-not $token -and $TokenResource -ne 'https://purview.azure.net') {
    Write-Warn2 "Token acquisition failed for '$TokenResource'. Falling back to 'https://purview.azure.net'."
    $token = Get-Token 'https://purview.azure.net'
    if ($token) { $TokenResource = 'https://purview.azure.net' }
}
if (-not $token) {
    Write-Err "Failed to acquire token. Try 'az login'."
    Emit-Json @{ pass = $false; error = 'auth_failed' }
    exit 3
}
Write-Ok "Token acquired (audience: $TokenResource)"

# --- Run each query ---------------------------------------------------------------
$uri = 'https://api.securityplatform.microsoft.com/lake/kql/v2/rest/query'
$results = @()
$anyFail = $false

for ($i = 0; $i -lt $preparedQueries.Count; $i++) {
    $src = $querySources[$i]
    $query = $preparedQueries[$i]
    $preview = $query.Substring(0, [Math]::Min(120, $query.Length)).Replace("`n", ' ').Replace("`r", '')
    Write-Info "[$src] running: $preview..."

    $body = @{ csl = $query; db = $db } | ConvertTo-Json -Compress
    $rowCount = 0
    $passed = $false
    $reason = ''
    $httpStatus = 0
    $resp = $null

    try {
        $resp = Invoke-RestMethod -Uri $uri -Method Post `
            -Headers @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' } `
            -Body $body -ErrorAction Stop
        $httpStatus = 200
    } catch {
        try { $httpStatus = [int]$_.Exception.Response.StatusCode } catch { }
        $errBody = ''
        try {
            $stream = $_.Exception.Response.GetResponseStream()
            if ($stream) {
                $reader = [System.IO.StreamReader]::new($stream)
                $errBody = $reader.ReadToEnd()
                $reader.Dispose()
            }
        } catch { }
        if (-not $errBody) { try { $errBody = $_.ErrorDetails.Message } catch { } }

        # 401 fallback
        if ($httpStatus -eq 401 -and $TokenResource -ne 'https://purview.azure.net') {
            Write-Warn2 "401 with audience '$TokenResource'. Retrying with 'https://purview.azure.net'..."
            $token2 = Get-Token 'https://purview.azure.net'
            if ($token2) {
                try {
                    $resp = Invoke-RestMethod -Uri $uri -Method Post `
                        -Headers @{ Authorization = "Bearer $token2"; 'Content-Type' = 'application/json' } `
                        -Body $body -ErrorAction Stop
                    $token = $token2
                    $TokenResource = 'https://purview.azure.net'
                    $httpStatus = 200
                } catch {
                    try { $httpStatus = [int]$_.Exception.Response.StatusCode } catch { $httpStatus = 0 }
                    $reason = "query_failed_after_fallback (HTTP $httpStatus): $($_.Exception.Message)"
                }
            } else {
                $reason = 'fallback_token_failed'
            }
        } else {
            $shortBody = $errBody
            if ($shortBody -and $shortBody.Length -gt 400) { $shortBody = $shortBody.Substring(0, 400) + '...' }
            $reason = "query_failed (HTTP $httpStatus): $($_.Exception.Message)"
            if ($shortBody) { $reason += " | body: $shortBody" }
        }
    }

    if ($resp) {
        try {
            $rowCount = Get-RowCountFromResponse $resp
        } catch {
            $reason = "parse_failed: $($_.Exception.Message)"
        }
    }

    if (-not $reason) {
        if ($rowCount -gt 0 -or $PassOnEmpty) {
            $passed = $true
            if ($rowCount -gt 0) { Write-Ok "[$src] passed ($rowCount row(s))" }
            else { Write-Ok "[$src] passed (0 rows; schema valid — synthetic input matched no data)" }
        } else {
            $reason = 'no_data_returned'
            Write-Err "[$src] failed: returned 0 rows and -PassOnEmpty:`$false"
        }
    } else {
        Write-Err "[$src] failed: $reason"
    }

    if (-not $passed) { $anyFail = $true }

    $results += [pscustomobject]@{
        source     = $src
        passed     = $passed
        rowCount   = $rowCount
        httpStatus = $httpStatus
        reason     = $reason
        query      = $query
    }
}

# --- Summarise --------------------------------------------------------------------
$passedCount = ($results | Where-Object { $_.passed }).Count
$failedCount = $results.Count - $passedCount

Write-Info "Summary: $passedCount/$($results.Count) queries passed; $failedCount failed."

# --- Lake-readiness probe ----------------------------------------------------------
# When every query returned HTTP 200 + 0 rows, we cannot distinguish "data not yet in
# the lake" from "substitution value doesn't match any seeded entity". Both look
# identical (0 rows everywhere) and -PassOnEmpty:$true masks them as pass — which
# led to the historical "data not yet visible in the Sentinel Data Lake" false-
# signal anti-pattern. The discriminator: take query #1, strip the line(s)
# containing any '<substituted-value>' literal, re-run. If the stripped query
# returns rows, the substitution is wrong (the data IS in the lake). If it also
# returns 0, the lake is genuinely empty for this scope.
$lakeReadinessProbe = $null
$allZero = (-not $anyFail) -and ($results.Count -gt 0) -and (($results | Where-Object { $_.rowCount -gt 0 }).Count -eq 0)
$hasSubstitutions = $Substitutions -and $Substitutions.Keys.Count -gt 0

if ($allZero -and $hasSubstitutions) {
    Write-Info "All queries returned HTTP 200 + 0 rows. Running stripped-filter probe to distinguish substitution_mismatch from lake_pending..."

    $stripValues = @()
    foreach ($k in $Substitutions.Keys) {
        $v = [string]$Substitutions[$k]
        if ($v) { $stripValues += $v }
    }

    $probeBase = $preparedQueries[0]
    $lines = $probeBase -split "`n"
    $kept = @()
    $dropped = @()
    foreach ($ln in $lines) {
        $hit = $false
        foreach ($v in $stripValues) {
            if ($ln.IndexOf("'$v'") -ge 0 -or $ln.IndexOf("`"$v`"") -ge 0) { $hit = $true; break }
        }
        if ($hit) { $dropped += $ln.Trim() } else { $kept += $ln }
    }
    $probeQuery = ($kept -join "`n").TrimEnd()
    if ($probeQuery -notmatch '\|\s*take\s+\d+' -and $probeQuery -notmatch '\|\s*limit\s+\d+' -and $probeQuery -notmatch '\|\s*top\s+\d+') {
        $probeQuery = $probeQuery + " | take $MaxRows"
    }

    $probeRowCount = 0
    $probeHttp = 0
    $probeError = ''
    $probeVerdict = 'lake_pending'

    if ($dropped.Count -eq 0) {
        # Couldn't find a line to strip — substitutions didn't appear in query #1.
        # Treat as inconclusive / lake_pending (we can't prove the data is present).
        $probeVerdict = 'lake_pending'
        $probeError = 'no_lines_matched_substitution_values'
    } else {
        $probeBody = @{ csl = $probeQuery; db = $db } | ConvertTo-Json -Compress
        try {
            $probeResp = Invoke-RestMethod -Uri $uri -Method Post `
                -Headers @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' } `
                -Body $probeBody -ErrorAction Stop
            $probeHttp = 200
            try {
                $probeRowCount = Get-RowCountFromResponse $probeResp
            } catch { }
        } catch {
            try { $probeHttp = [int]$_.Exception.Response.StatusCode } catch { }
            $probeError = $_.Exception.Message
        }

        if ($probeRowCount -gt 0) {
            $probeVerdict = 'substitution_mismatch'
            Write-Warn2 "PROBE: stripped-filter query returned $probeRowCount row(s) — data IS in the lake. Substitution value(s) ($($stripValues -join ', ')) don't match any seeded entity. Re-check primaryInput.exampleSource against config/entities.json + scenarios/<slug>.json."
        } else {
            Write-Info "PROBE: stripped-filter query returned 0 rows — data appears genuinely absent from the lake."
        }
    }

    $lakeReadinessProbe = [ordered]@{
        ran                = $true
        verdict            = $probeVerdict
        rowCount           = $probeRowCount
        httpStatus         = $probeHttp
        error              = $probeError
        droppedLines       = $dropped
        substitutionValues = $stripValues
        strippedQuery      = $probeQuery
    }
} elseif (-not $anyFail) {
    $lakeReadinessProbe = [ordered]@{
        ran     = $false
        verdict = 'pass'
        reason  = if (-not $hasSubstitutions) { 'no_substitutions_supplied' } else { 'at_least_one_query_returned_rows' }
    }
} else {
    $lakeReadinessProbe = [ordered]@{
        ran     = $false
        verdict = 'failed_with_errors'
        reason  = 'one_or_more_queries_returned_non_2xx_or_semantic_error'
    }
}

# --- Top-level verdict (drives exit code + agent UX) ------------------------------
$verdict = 'pass'
$exitCode = 0
if ($anyFail) {
    $verdict = 'failed_with_errors'
    $exitCode = 1
} elseif ($lakeReadinessProbe.verdict -eq 'substitution_mismatch') {
    $verdict = 'substitution_mismatch'
    $exitCode = 4
} elseif ($lakeReadinessProbe.verdict -eq 'lake_pending') {
    $verdict = 'lake_pending'
    $exitCode = 0   # pass-on-empty; agent uses verdict, not exit code, to decide messaging
}

$nextStep = switch ($verdict) {
    'pass'                  { 'instructions_validated_proceed_to_publish' }
    'substitution_mismatch' { 'fix_primaryInput_exampleSource_in_progress_json_and_rerun' }
    'lake_pending'          { 'wait_30min_then_rerun_Validate-Ingestion_and_revalidate' }
    'failed_with_errors'    { 'iterate_on_instructions_and_rerun' }
    default                 { 'iterate_on_instructions_and_rerun' }
}

$envelope = [ordered]@{
    pass               = (-not $anyFail)
    verdict            = $verdict
    totalQueries       = $results.Count
    passedCount        = $passedCount
    failedCount        = $failedCount
    workspace          = $WorkspaceName
    db                 = $db
    audience           = $TokenResource
    substitutions      = $Substitutions
    lakeReadinessProbe = $lakeReadinessProbe
    results            = $results
    nextStep           = $nextStep
}

Emit-Json $envelope

exit $exitCode
