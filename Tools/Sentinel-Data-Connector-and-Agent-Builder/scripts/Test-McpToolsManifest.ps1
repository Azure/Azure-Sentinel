<#
.SYNOPSIS
    Validates a Custom MCP Tools manifest (config/mcp-tools/<slug>/tools.json)
    before it is published to the Sentinel Platform Services AI Primitives API.

.DESCRIPTION
    Sibling of Test-AgentInstructions.ps1 for the Custom MCP Tools track.
    Runs the static checks locked in plan.md section K6 / section K9 and knowledge/custom-mcp-tools-guide.md section 8:

      1. JSON parses; top-level is an array.
      2. Every entry has required keys: displayName, description, mcpToolType=="Kqs",
         queryFormat, arguments, defaultArgumentValues.
      3. displayName is unique and matches ^[a-z][a-z0-9-]{1,62}[a-z0-9]$.
      4. Every {{token}} in queryFormat is declared in arguments.properties.
      5. Every name in arguments.required is either used in queryFormat OR is workspaceId.
      6. workspaceId rule (K4): present in arguments.properties (type=="string"),
         in arguments.required, and a non-empty GUID-looking value in defaultArgumentValues.
      7. Banned-terms lint (K9): "headless client" / "headless_client" / "headless-client"
         must not appear anywhere in any string value (case-insensitive).
      8. -Render: substitute defaultArgumentValues into queryFormat and print the rendered
         KQL per tool, for visual sanity check before publication.
      9. -JsonOutput: emit a structured pass/fail JSON document to stdout (CI-friendly).

    Optional cross-check: if config/mcp-tools/<slug>/validated-tool-queries.json exists
    (the Phase 4 → Phase 5B bridge artifact from K1), every tool in the manifest must
    have a matching entry by displayName and the queryFormat must match the bridge
    entry's queryFormatTemplate after canonicalisation.

    Exit codes: 0 = clean, 1 = validation failures, 2 = file unreadable / bad input.

.PARAMETER ManifestPath
    Path to the tools.json manifest. Required.

.PARAMETER Render
    Switch. When present, print rendered KQL (defaults substituted) per tool to stdout.

.PARAMETER JsonOutput
    Switch. When present, emit structured pass/fail JSON to stdout instead of
    human-readable lines. Errors still go to stderr.

.EXAMPLE
    pwsh ./scripts/Test-McpToolsManifest.ps1 -ManifestPath config/mcp-tools/<slug>/tools.json

.EXAMPLE
    pwsh ./scripts/Test-McpToolsManifest.ps1 -ManifestPath config/mcp-tools/<slug>/tools.json -Render

.EXAMPLE
    pwsh ./scripts/Test-McpToolsManifest.ps1 -ManifestPath config/mcp-tools/<slug>/tools.json -JsonOutput
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $ManifestPath,

    [switch] $Render,

    [switch] $JsonOutput
)

$ErrorActionPreference = 'Stop'

trap {
    Write-Error "Unhandled exception in Test-McpToolsManifest: $($_.Exception.Message)"
    Write-Error $_.ScriptStackTrace
    exit 1
}

# ---------- helpers ----------

$script:Findings = New-Object System.Collections.Generic.List[object]
$script:Rendered = New-Object System.Collections.Generic.List[object]

function Add-Finding {
    param(
        [Parameter(Mandatory)] [ValidateSet('error', 'warning')] [string] $Severity,
        [Parameter(Mandatory)] [string] $Check,
        [Parameter(Mandatory)] [string] $Message,
        [string] $ToolName = ''
    )
    $script:Findings.Add([pscustomobject]@{
        severity = $Severity
        check    = $Check
        tool     = $ToolName
        message  = $Message
    }) | Out-Null
}

function Test-DisplayNameFormat {
    param([string] $Name)
    return $Name -match '^[a-z][a-z0-9-]{1,62}[a-z0-9]$'
}

function Test-GuidLike {
    param([string] $Value)
    if ([string]::IsNullOrWhiteSpace($Value)) { return $false }
    return $Value -match '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
}

function Get-PlaceholdersFromQuery {
    param([string] $QueryFormat)
    $names = New-Object System.Collections.Generic.HashSet[string]
    if ([string]::IsNullOrWhiteSpace($QueryFormat)) { return ,$names }
    $regex = [regex]'\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}'
    foreach ($m in $regex.Matches($QueryFormat)) {
        [void] $names.Add($m.Groups[1].Value)
    }
    return ,$names
}

function Get-AllStringValues {
    param($Node)
    $out = New-Object System.Collections.Generic.List[string]
    $stack = New-Object System.Collections.Generic.Stack[object]
    $stack.Push($Node)
    while ($stack.Count -gt 0) {
        $cur = $stack.Pop()
        if ($null -eq $cur) { continue }
        if ($cur -is [string]) { $out.Add($cur) | Out-Null; continue }
        if ($cur -is [System.Collections.IDictionary]) {
            foreach ($v in $cur.Values) { $stack.Push($v) }
            continue
        }
        if ($cur -is [pscustomobject]) {
            foreach ($p in $cur.PSObject.Properties) { $stack.Push($p.Value) }
            continue
        }
        if ($cur -is [System.Collections.IEnumerable] -and -not ($cur -is [string])) {
            foreach ($e in $cur) { $stack.Push($e) }
            continue
        }
    }
    return ,$out
}

function Get-PropertyNames {
    param($Obj)
    $names = New-Object System.Collections.Generic.HashSet[string]
    if ($null -eq $Obj) { return ,$names }
    if ($Obj -is [pscustomobject]) {
        foreach ($p in $Obj.PSObject.Properties) { [void] $names.Add($p.Name) }
    } elseif ($Obj -is [System.Collections.IDictionary]) {
        foreach ($k in $Obj.Keys) { [void] $names.Add([string] $k) }
    }
    return ,$names
}

function Get-PropertyValue {
    param($Obj, [string] $Name)
    if ($null -eq $Obj) { return $null }
    if ($Obj -is [pscustomobject]) {
        $p = $Obj.PSObject.Properties[$Name]
        if ($p) { return $p.Value }
        return $null
    }
    if ($Obj -is [System.Collections.IDictionary]) {
        if ($Obj.Contains($Name)) { return $Obj[$Name] }
        return $null
    }
    return $null
}

# ---------- load manifest ----------

if (-not (Test-Path -LiteralPath $ManifestPath)) {
    Write-Error "Manifest file not found: $ManifestPath"
    exit 2
}

try {
    $raw = Get-Content -LiteralPath $ManifestPath -Raw -ErrorAction Stop
} catch {
    Write-Error "Cannot read manifest: $_"
    exit 2
}

try {
    $manifest = $raw | ConvertFrom-Json -ErrorAction Stop
} catch {
    Write-Error "Manifest is not valid JSON: $_"
    exit 2
}

# Check 1: top-level array
if ($manifest -isnot [System.Collections.IEnumerable] -or $manifest -is [string]) {
    Add-Finding -Severity error -Check 'shape' -Message 'Top-level JSON must be an array of tool definitions.'
}

# ---------- banned-terms lint (K9) over RAW text ----------

$bannedPatterns = @('headless client', 'headless_client', 'headless-client')
foreach ($pat in $bannedPatterns) {
    if ($raw -match [regex]::Escape($pat)) {
        Add-Finding -Severity error -Check 'K9-banned-terms' -Message "Banned term '$pat' found in manifest. Use 'the consuming agent' instead."
    }
}

# ---------- per-tool validation ----------

$requiredKeys = @('displayName', 'description', 'mcpToolType', 'queryFormat', 'arguments', 'defaultArgumentValues')
$seenNames = New-Object System.Collections.Generic.HashSet[string]
$toolIndex = -1

if ($manifest -is [System.Collections.IEnumerable] -and $manifest -isnot [string]) {

    foreach ($tool in $manifest) {
        $toolIndex++
        try {
            $displayName = Get-PropertyValue -Obj $tool -Name 'displayName'
            $toolLabel = if ($displayName) { [string] $displayName } else { "<index $toolIndex>" }

            # Check 2: required keys
            $present = Get-PropertyNames -Obj $tool
            foreach ($k in $requiredKeys) {
                if (-not $present.Contains($k)) {
                    Add-Finding -Severity error -Check 'required-keys' -ToolName $toolLabel `
                        -Message "Missing required key '$k'."
                }
            }

            # mcpToolType must be exactly 'Kqs'
            $mcpType = Get-PropertyValue -Obj $tool -Name 'mcpToolType'
            if ($mcpType -and $mcpType -ne 'Kqs') {
                Add-Finding -Severity error -Check 'mcpToolType' -ToolName $toolLabel `
                    -Message "mcpToolType must be 'Kqs' (got '$mcpType')."
            }

            # Check 3: displayName format + uniqueness
            if ($displayName) {
                if (-not (Test-DisplayNameFormat -Name $displayName)) {
                    Add-Finding -Severity error -Check 'displayName-format' -ToolName $toolLabel `
                        -Message "displayName '$displayName' must match ^[a-z][a-z0-9-]{1,62}[a-z0-9]$ (kebab-case, 3-64 chars)."
                }
                if (-not $seenNames.Add([string] $displayName)) {
                    Add-Finding -Severity error -Check 'displayName-unique' -ToolName $toolLabel `
                        -Message "Duplicate displayName '$displayName' in manifest."
                }
            }

            # Skip remaining structural checks if shape is broken
            $queryFormat = Get-PropertyValue -Obj $tool -Name 'queryFormat'
            $argsObj = Get-PropertyValue -Obj $tool -Name 'arguments'
            $defaultsObj = Get-PropertyValue -Obj $tool -Name 'defaultArgumentValues'

            if (-not $queryFormat -or -not $argsObj) {
                continue
            }

            $props = Get-PropertyValue -Obj $argsObj -Name 'properties'
            $required = Get-PropertyValue -Obj $argsObj -Name 'required'

            $propNames = Get-PropertyNames -Obj $props
            $requiredNames = New-Object System.Collections.Generic.HashSet[string]
            if ($required -is [System.Collections.IEnumerable] -and $required -isnot [string]) {
                foreach ($r in $required) { [void] $requiredNames.Add([string] $r) }
            }

            $placeholders = Get-PlaceholdersFromQuery -QueryFormat ([string] $queryFormat)

            # Check 4: every placeholder declared in arguments.properties
            foreach ($p in $placeholders) {
                if (-not $propNames.Contains($p)) {
                    Add-Finding -Severity error -Check 'placeholder-undeclared' -ToolName $toolLabel `
                        -Message "queryFormat references {{$p}} but it is not declared in arguments.properties."
                }
            }

            # Check 5: every required arg used in queryFormat OR is workspaceId
            foreach ($r in $requiredNames) {
                if ($r -eq 'workspaceId') { continue }
                if (-not $placeholders.Contains($r)) {
                    Add-Finding -Severity error -Check 'required-unused' -ToolName $toolLabel `
                        -Message "arguments.required includes '$r' but {{$r}} does not appear in queryFormat."
                }
            }

            # Check 6: workspaceId rule (K4)
            if (-not $propNames.Contains('workspaceId')) {
                Add-Finding -Severity error -Check 'K4-workspaceId-property' -ToolName $toolLabel `
                    -Message "arguments.properties.workspaceId is required (K4)."
            } else {
                $wsProp = Get-PropertyValue -Obj $props -Name 'workspaceId'
                $wsType = Get-PropertyValue -Obj $wsProp -Name 'type'
                if ($wsType -ne 'string') {
                    Add-Finding -Severity error -Check 'K4-workspaceId-type' -ToolName $toolLabel `
                        -Message "arguments.properties.workspaceId.type must be 'string' (K4, got '$wsType')."
                }
            }
            if (-not $requiredNames.Contains('workspaceId')) {
                Add-Finding -Severity error -Check 'K4-workspaceId-required' -ToolName $toolLabel `
                    -Message "'workspaceId' must appear in arguments.required (K4)."
            }
            $wsDefault = Get-PropertyValue -Obj $defaultsObj -Name 'workspaceId'
            if (-not $wsDefault) {
                Add-Finding -Severity error -Check 'K4-workspaceId-default' -ToolName $toolLabel `
                    -Message "defaultArgumentValues.workspaceId is required (K4)."
            } elseif (-not (Test-GuidLike -Value ([string] $wsDefault))) {
                Add-Finding -Severity warning -Check 'K4-workspaceId-default-shape' -ToolName $toolLabel `
                    -Message "defaultArgumentValues.workspaceId '$wsDefault' does not look like a workspace GUID; confirm it matches progress.json phase2.workspace.customerId."
            }

            # -Render: substitute defaults and stash
            if ($Render -and $queryFormat) {
                $renderedKql = [string] $queryFormat
                foreach ($name in $propNames) {
                    $val = Get-PropertyValue -Obj $defaultsObj -Name $name
                    if ($null -ne $val) {
                        $renderedKql = $renderedKql.Replace("{{$name}}", [string] $val)
                        $renderedKql = $renderedKql.Replace("{{ $name }}", [string] $val)
                    }
                }
                $script:Rendered.Add([pscustomobject]@{
                    tool     = $toolLabel
                    rendered = $renderedKql
                }) | Out-Null
            }
        } catch {
            $errLabel = if ($displayName) { [string] $displayName } else { "<index $toolIndex>" }
            Add-Finding -Severity error -Check 'tool-check-exception' -ToolName $errLabel `
                -Message "Internal error while validating tool: $($_.Exception.Message)"
        }
    }
}

# ---------- optional cross-check vs validated-tool-queries.json (K1 bridge) ----------

try {
    $manifestDir = Split-Path -Path $ManifestPath -Parent
    if ([string]::IsNullOrEmpty($manifestDir)) { $manifestDir = '.' }
    $bridgePath = Join-Path $manifestDir 'validated-tool-queries.json'
    if (Test-Path -LiteralPath $bridgePath) {
        $bridge = Get-Content -LiteralPath $bridgePath -Raw | ConvertFrom-Json
        $bridgeByName = @{}
        foreach ($b in $bridge) {
            $bn = Get-PropertyValue -Obj $b -Name 'toolName'
            if ($bn) { $bridgeByName[[string] $bn] = $b }
        }
        if ($manifest -is [System.Collections.IEnumerable] -and $manifest -isnot [string]) {
            foreach ($tool in $manifest) {
                $dn = Get-PropertyValue -Obj $tool -Name 'displayName'
                if (-not $dn) { continue }
                if (-not $bridgeByName.ContainsKey([string] $dn)) {
                    Add-Finding -Severity warning -Check 'K1-bridge-missing' -ToolName ([string] $dn) `
                        -Message "No entry in validated-tool-queries.json for '$dn'. Phase 4 -> Phase 5B bridge artifact is incomplete."
                }
            }
        }
    }
} catch {
    Add-Finding -Severity warning -Check 'K1-bridge-read' `
        -Message "Could not cross-check validated-tool-queries.json: $($_.Exception.Message)"
}

# ---------- emit results ----------

$errorCount = ($script:Findings | Where-Object { $_.severity -eq 'error' }).Count
$warningCount = ($script:Findings | Where-Object { $_.severity -eq 'warning' }).Count

if ($JsonOutput) {
    $payload = [ordered]@{
        manifestPath = (Resolve-Path -LiteralPath $ManifestPath).Path
        status       = if ($errorCount -gt 0) { 'fail' } else { 'pass' }
        errorCount   = $errorCount
        warningCount = $warningCount
        findings     = $script:Findings
    }
    if ($Render) {
        $payload['rendered'] = $script:Rendered
    }
    $payload | ConvertTo-Json -Depth 8
} else {
    if ($script:Findings.Count -eq 0) {
        Write-Host "OK: $ManifestPath passes all checks." -ForegroundColor Green
    } else {
        foreach ($f in $script:Findings) {
            $tag = if ($f.severity -eq 'error') { 'ERROR' } else { 'WARN ' }
            $line = "[$tag] [$($f.check)]"
            if ($f.tool) { $line += " ($($f.tool))" }
            $line += " $($f.message)"
            if ($f.severity -eq 'error') {
                Write-Host $line -ForegroundColor Red
            } else {
                Write-Host $line -ForegroundColor Yellow
            }
        }
        Write-Host ""
        $summaryColor = if ($errorCount -gt 0) { 'Red' } else { 'Yellow' }
        Write-Host "Summary: $errorCount error(s), $warningCount warning(s)" -ForegroundColor $summaryColor
    }
    if ($Render -and $script:Rendered.Count -gt 0) {
        Write-Host ""
        Write-Host "-- Rendered KQL (defaults substituted) --" -ForegroundColor Cyan
        foreach ($r in $script:Rendered) {
            Write-Host ""
            Write-Host "### $($r.tool)" -ForegroundColor Cyan
            Write-Host $r.rendered
        }
    }
}

if ($errorCount -gt 0) { exit 1 } else { exit 0 }
