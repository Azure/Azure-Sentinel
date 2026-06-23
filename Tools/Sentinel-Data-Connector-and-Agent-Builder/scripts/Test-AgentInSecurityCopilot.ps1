<#
.SYNOPSIS
    Phase 5 gate: pre-flight check + test runbook printer for validating an
    agent inside a real Security Copilot workspace before Phase 6 (packaging)
    is allowed to begin.

.DESCRIPTION
    1. Detects whether the current Azure subscription/tenant already has at least
       one Security Compute Unit (SCU) capacity provisioned
       (resource type: Microsoft.SecurityCopilot/capacities) via Azure Resource Graph.
    2. If no SCU is found → prints onboarding URL + Lab-05 step pointer and exits 2.
    3. If at least one SCU is found → prints the capacity inventory, the
       workspace-check hint, and a per-scenario test runbook generated from
       scenarios/<slug>.json.scenarioCoverage[]. Exits 0.
    4. Optionally writes a sidecar JSON capture of the run so the developer can
       paste the populated `securityCopilotValidation` block back into
       config/progress.json once the agent test passes.

.PARAMETER ScenarioPath
    Path to the scenario file with scenarioCoverage[] entries. Required.

.PARAMETER ProgressPath
    Path to config/progress.json. Used only to seed the sidecar template with
    the workspace customerId and the Phase 5 agent name. Defaults to
    config/progress.json.

.PARAMETER SidecarOut
    Path to write the sidecar securityCopilotValidation JSON capture.
    Defaults to .out/security-copilot-validation.json. Pass empty string to skip.

.PARAMETER GuideUrl
    Public URL for the Security Copilot onboarding home.
    Default: https://securitycopilot.microsoft.com/

.EXAMPLE
    ./scripts/Test-AgentInSecurityCopilot.ps1 -ScenarioPath scenarios/<slug>.json
        Runs pre-flight + prints runbook.

.EXAMPLE
    ./scripts/Test-AgentInSecurityCopilot.ps1 -ScenarioPath scenarios/<slug>.json -SidecarOut ''
        Skip writing the sidecar JSON.

.NOTES
    Exit codes:
      0 = SCU capacity present, runbook printed, ready for manual validation
      2 = SCU capacity missing, onboarding required (developer must provision SCU)
      1 = unexpected error (az not logged in, scenario file missing, etc.)
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string] $ScenarioPath,
    [string] $ProgressPath = 'config/progress.json',
    [string] $SidecarOut  = '.out/security-copilot-validation.json',
    [string] $GuideUrl    = 'https://securitycopilot.microsoft.com/'
)

$ErrorActionPreference = 'Stop'
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')

function Resolve-RepoPath([string] $p) {
    if ([System.IO.Path]::IsPathRooted($p)) { return $p }
    return (Join-Path $repoRoot $p)
}

function Write-Section($title) {
    Write-Host ''
    Write-Host ('═' * 72) -ForegroundColor DarkCyan
    Write-Host (" $title") -ForegroundColor Cyan
    Write-Host ('═' * 72) -ForegroundColor DarkCyan
}

function Get-AzAccountContext {
    try {
        $ctx = az account show --only-show-errors 2>$null | ConvertFrom-Json
        if (-not $ctx) { throw "az account show returned nothing." }
        return $ctx
    } catch {
        Write-Host "ERROR: 'az' CLI is not logged in. Run 'az login' first." -ForegroundColor Red
        exit 1
    }
}

function Query-ScuCapacities([string] $subscriptionId) {
    $kql = "resources | where type =~ 'microsoft.securitycopilot/capacities' | project id, name, resourceGroup, location, sku=tostring(sku.name), capacityUnits=tostring(properties.numberOfUnits), provisioningState=tostring(properties.provisioningState)"
    $argRaw = az graph query -q $kql --subscriptions $subscriptionId --only-show-errors 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $argRaw) { return @() }
    $arg = $argRaw | ConvertFrom-Json
    if ($null -eq $arg.data) { return @() }
    return @($arg.data)
}

function Load-Json([string] $path) {
    $full = Resolve-RepoPath $path
    if (-not (Test-Path $full)) {
        Write-Host "ERROR: file not found → $full" -ForegroundColor Red
        exit 1
    }
    return (Get-Content -Raw -Path $full | ConvertFrom-Json)
}

# -----------------------------------------------------------------------------
# 0. Load scenario + progress context
# -----------------------------------------------------------------------------
$scenario = Load-Json $ScenarioPath
$progress = $null
if (Test-Path (Resolve-RepoPath $ProgressPath)) {
    $progress = Load-Json $ProgressPath
}

$agentName        = $scenario.advisorName
if (-not $agentName) { $agentName = '<Agent Name>' }
$primaryInputName = if ($scenario.primaryInput.name)        { $scenario.primaryInput.name }        else { '<inputName>' }
$primaryInputDesc = if ($scenario.primaryInput.description) { $scenario.primaryInput.description } else { 'The primary input value to investigate (see scenarios/<slug>.json.primaryInput.description).' }
$primaryInputEg   = if ($scenario.primaryInput.example)     { $scenario.primaryInput.example }     else { '<example-value-from-entities.json>' }
$workspaceName    = if ($progress) { $progress.phases.'2_data_lake_onboarding'.workspaceName } else { '<workspace-name>' }
$workspaceCustId  = if ($progress) { $progress.phases.'2_data_lake_onboarding'.workspaceCustomerId } else { $null }
$instructionsPath = if ($progress) { $progress.phases.'5_agent_build'.instructionsPath } else { 'config/agent-instructions/<slug>.md' }

# -----------------------------------------------------------------------------
# 1. SCU capacity pre-flight via ARG
# -----------------------------------------------------------------------------
Write-Section "Phase 5 Security Copilot validation — pre-flight"

$ctx = Get-AzAccountContext
Write-Host ("Subscription : {0}" -f $ctx.id)
Write-Host ("Tenant       : {0}" -f $ctx.tenantId)
Write-Host ("Signed-in as : {0}" -f $ctx.user.name)
Write-Host ("Agent        : {0}" -f $agentName)
Write-Host ("Workspace    : {0} ({1})" -f $workspaceName, $workspaceCustId)
Write-Host ("Instructions : {0}" -f $instructionsPath)
Write-Host ''

Write-Host "Querying Azure Resource Graph for SCU capacities..." -ForegroundColor Yellow
$capacities = Query-ScuCapacities -subscriptionId $ctx.id

# -----------------------------------------------------------------------------
# 2. Branch: onboarding required OR ready-to-test
# -----------------------------------------------------------------------------
if ($capacities.Count -eq 0) {
    Write-Section "Result: NO SCU capacity detected — onboarding required"
    Write-Host "No 'Microsoft.SecurityCopilot/capacities' resource was found in subscription $($ctx.id)." -ForegroundColor Red
    Write-Host ''
    Write-Host "What you need to do (one-time per tenant):" -ForegroundColor Yellow
    Write-Host "  1. Open: $GuideUrl"
    Write-Host "  2. Sign in with an account that has the 'Security Administrator' role."
    Write-Host "  3. Provision a Security Compute Unit (SCU) capacity. 1 SCU is enough for testing."
    Write-Host "     Pick the same region as your data lake-attached workspace ($workspaceName)."
    Write-Host "  4. After provisioning completes (5-10 min), Security Copilot will auto-create"
    Write-Host "     a default workspace and land you in the onboarding wizard."
    Write-Host "  5. When the role-assignment dialog appears, choose 'No one. Add them later'"
    Write-Host "     unless you already know which users will operate the agent."
    Write-Host ''
    Write-Host "Reference walkthrough (with screenshots):"
    Write-Host "  https://github.com/suchandanreddy/Microsoft-Sentinel-Labs/blob/main/05-Building-an-Agent-in-Security-Copilot.md"
    Write-Host "  knowledge/security-copilot-agent-guide.md   (this repo)"
    Write-Host ''
    Write-Host "Re-run this script after SCU provisioning completes." -ForegroundColor Yellow
    exit 2
}

Write-Section "Result: SCU capacity detected — ready for agent validation"
foreach ($cap in $capacities) {
    Write-Host ("  • {0,-30}  RG: {1,-25}  Region: {2,-12}  SKU: {3}  Units: {4}  State: {5}" -f `
        $cap.name, $cap.resourceGroup, $cap.location, $cap.sku, $cap.capacityUnits, $cap.provisioningState)
}
Write-Host ''
Write-Host "Workspace check: Security Copilot does not expose its workspace via ARM." -ForegroundColor Yellow
Write-Host "  → Browse to $GuideUrl."
Write-Host "  → If you land on the home / chat experience, you have a workspace."
Write-Host "  → If you land on an onboarding wizard, complete it (no SCU action needed)."

# -----------------------------------------------------------------------------
# 3. Print agent-build steps + per-scenario runbook (driven by scenarioCoverage[])
# -----------------------------------------------------------------------------
Write-Section "Step A — Build the agent in Security Copilot"
@"
  1. Open  $GuideUrl  →  Build (left rail)  →  + Create  →  Start from scratch
  2. Name        :  $agentName
  3. Description :  (paste the 1-line summary from $ScenarioPath → "summary")
  4. Inputs      :
       • Name        : $primaryInputName
       • Type        : string
       • Description : $primaryInputDesc
       • Required    : yes
  5. Instructions:  copy/paste the ENTIRE contents of
                    $instructionsPath
                    into the Instructions textarea. Do NOT trim sections.
  6. Tools       :  Add Microsoft Sentinel plugin (built-in) and enable:
                    • list_sentinel_workspaces
                    • search_tables
                    • query_lake (or query_sentinel — whichever is exposed in your tenant)
                    • $agentName  (the agent itself — required so the orchestrator can invoke its KQL skills)
  7. Workspaces  :  bind to '$workspaceName' (customerId: $workspaceCustId).
  8. Save        :  Publish scope = 'Me'  (private to you during validation).
                    Promote to 'Workspace' only after every scenario passes.
"@ | Write-Host

Write-Section "Step B — Execute the per-scenario test runbook"
Write-Host "Run each prompt below in the agent's test pane. For each row, capture the verdict the agent emits and tick PASS / FAIL." -ForegroundColor Yellow
Write-Host ''

$scenarios = $scenario.scenarioCoverage

foreach ($s in $scenarios) {
    $entityValue     = if ($s.entityValue)     { $s.entityValue }     else { $primaryInputEg }
    $expectedVerdict = if ($s.expectedVerdict) { $s.expectedVerdict } else { '(see scenarioCoverage[].expectedVerdict)' }
    $keySignals      = if ($s.keySignals)      { $s.keySignals -join '; ' } else { '' }
    $rationale       = if ($s.rationale)       { $s.rationale }       else { '' }
    $tablesList      = if ($s.tables)          { ($s.tables -join ', ') } else { '' }
    $promptText      = "Triage ${primaryInputName}: $entityValue. Investigate within the last 24h."

    Write-Host ("Scenario {0}: {1}" -f $s.id, $s.name) -ForegroundColor White
    if ($tablesList)      { Write-Host ("  Tables expected : {0}" -f $tablesList) }
    if ($s.expectedMinHits) { Write-Host ("  Min hits        : {0}" -f $s.expectedMinHits) }
    Write-Host ("  Expected verdict: {0}" -f $expectedVerdict)
    Write-Host  "  Prompt          : " -NoNewline
    Write-Host  $promptText -ForegroundColor Gray
    if ($keySignals) { Write-Host ("  Key signals     : {0}" -f $keySignals) -ForegroundColor DarkGray }
    if ($rationale)  { Write-Host ("  Rationale       : {0}" -f $rationale)  -ForegroundColor DarkGray }
    Write-Host  "  Pass criteria   : (a) 24h time filter applied, (b) all expected tables touched, (c) verdict matches expected, (d) no hallucinated columns or tables." -ForegroundColor DarkGray
    Write-Host ''
}

Write-Section "Step C — Record the outcome in config/progress.json"
$scenariosJsonBlock = ($scenarios | ForEach-Object {
    '        {"id": ' + $_.id + ', "name": "' + $_.name + '", "result": "pass"}'
}) -join ",`n"

@"
  After every scenario passes, update phases.5_agent_build.securityCopilotValidation
  in config/progress.json:

    "securityCopilotValidation": {
      "status": "validated",
      "scuCapacityId": "$($capacities[0].id)",
      "scuCapacityResourceGroup": "$($capacities[0].resourceGroup)",
      "scuRegion": "$($capacities[0].location)",
      "workspaceConfirmed": true,
      "scenariosPassed": [
$scenariosJsonBlock
      ],
      "validatedAt": "<ISO-8601 UTC timestamp>",
      "validatedBy": "$($ctx.user.name)"
    }

  Phase 6 (packaging) is BLOCKED until securityCopilotValidation.status == 'validated'.
"@ | Write-Host

# -----------------------------------------------------------------------------
# 4. Sidecar JSON capture (optional)
# -----------------------------------------------------------------------------
if ($SidecarOut) {
    $sidecarFull = Resolve-RepoPath $SidecarOut
    $sidecarDir  = Split-Path $sidecarFull -Parent
    if ($sidecarDir -and -not (Test-Path $sidecarDir)) { New-Item -ItemType Directory -Force -Path $sidecarDir | Out-Null }

    $scenariosTemplate = @()
    foreach ($s in $scenarios) {
        $scenariosTemplate += [pscustomobject]@{ id = [int]$s.id; name = [string]$s.name; result = $null }
    }

    $payload = [pscustomobject]@{
        status                   = 'pending'
        scuCapacityId            = $capacities[0].id
        scuCapacityResourceGroup = $capacities[0].resourceGroup
        scuRegion                = $capacities[0].location
        workspaceConfirmed       = $false
        scenariosPassed          = $scenariosTemplate
        validatedAt              = $null
        validatedBy              = $ctx.user.name
        generatedAt              = (Get-Date).ToUniversalTime().ToString("o")
        scriptVersion            = '1.0'
    }
    $payload | ConvertTo-Json -Depth 6 | Set-Content -Path $sidecarFull -Encoding UTF8
    Write-Section "Sidecar capture written"
    Write-Host "  $sidecarFull" -ForegroundColor Green
    Write-Host "  Edit this file as you complete each scenario, then merge into config/progress.json."
}

Write-Host ''
Write-Host "Done. Pre-flight = READY. Proceed with Step B in Security Copilot." -ForegroundColor Green
exit 0
