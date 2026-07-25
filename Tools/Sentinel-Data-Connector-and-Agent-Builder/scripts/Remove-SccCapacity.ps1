<#
.SYNOPSIS
    Deletes a Security Copilot SCU capacity to stop the ~ $4/SCU/hour billing.

.DESCRIPTION
    The agent calls this at the END of the Phase 5A run-confirmation
    step (after the developer (a) replies "agent works", (b) runs the agent
    2-3 times for SCU-usage measurement, and (c) captures Partner-Center
    screenshots). Failing to delete leaves the capacity running 24/7 — on an
    ISV Success Program developer tenant this can exhaust the monthly Azure
    credit grant in days.

    Flow:
      1. Resolve the capacity to delete:
           - Explicit -CapacityName + -ResourceGroupName, OR
           - phases.5_agent_build.sccCapacity.{name, resourceGroup} from
             progress.json (the default path written by Ensure-SccCapacity.ps1).
      2. Show the capacity details + cumulative cost estimate based on
         createdAt.
      3. Require -Confirm to delete (idempotent — already-deleted returns OK).
      4. Strip phases.5_agent_build.sccCapacity from progress.json.

.PARAMETER SubscriptionId
    Defaults to phases.5_agent_build.sccCapacity.id (parsed) or
    phases.2_data_lake_onboarding.subscriptionId or `az account show`.

.PARAMETER ResourceGroupName
    Defaults to the RG segment of phases.5_agent_build.sccCapacity.id.

.PARAMETER CapacityName
    Defaults to phases.5_agent_build.sccCapacity.name.

.PARAMETER ProgressJsonPath
    Default 'config/progress.json'.

.PARAMETER Confirm
    Required for delete. The agent chat MUST obtain explicit
    DOUBLE developer consent before calling with -Confirm (see Phase 5A
    Step 6 in .github/copilot-instructions.md).

.OUTPUTS
    Hashtable: @{
        CapacityId   = '...'
        Deleted      = $true|$false
        AlreadyGone  = $true|$false
        EstimatedRuntimeHours = <number or $null>
        EstimatedCostUsd      = <number or $null>
    }
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)] [string]$SubscriptionId,
    [Parameter(Mandatory=$false)] [string]$ResourceGroupName,
    [Parameter(Mandatory=$false)] [string]$CapacityName,
    [Parameter(Mandatory=$false)] [string]$ProgressJsonPath = 'config/progress.json',
    [Parameter(Mandatory=$false)] [switch]$Confirm,
    [Parameter(Mandatory=$false)] [switch]$NukeResourceGroup
)

$ErrorActionPreference = 'Stop'

function Write-Step($m) { Write-Host "`n=== $m ===" -ForegroundColor Cyan }
function Write-Ok  ($m) { Write-Host "✅ $m" -ForegroundColor Green }
function Write-Info($m) { Write-Host "   $m" }
function Write-Warn2($m){ Write-Host "⚠️  $m" -ForegroundColor Yellow }
function Write-Err2 ($m){ Write-Host "❌ $m" -ForegroundColor Red }

# -------- 1. Resolve target from progress.json -------------------------------
$progress = $null
if (Test-Path $ProgressJsonPath) {
    try { $progress = Get-Content $ProgressJsonPath -Raw | ConvertFrom-Json } catch { $progress = $null }
}
$scc = $progress.phases.'5_agent_build'.sccCapacity

if ((-not $CapacityName -or -not $ResourceGroupName -or -not $SubscriptionId) -and $scc.id) {
    if ($scc.id -match '/subscriptions/([^/]+)/resourceGroups/([^/]+)/providers/[^/]+/[^/]+/([^/]+)$') {
        if (-not $SubscriptionId)    { $SubscriptionId    = $Matches[1] }
        if (-not $ResourceGroupName) { $ResourceGroupName = $Matches[2] }
        if (-not $CapacityName)      { $CapacityName      = $Matches[3] }
    }
}
if (-not $SubscriptionId) { $SubscriptionId = $progress.phases.'2_data_lake_onboarding'.subscriptionId }
if (-not $SubscriptionId) { $SubscriptionId = az account show --query id -o tsv }

if (-not $CapacityName -or -not $ResourceGroupName -or -not $SubscriptionId) {
    throw "Could not resolve capacity target. Pass -SubscriptionId / -ResourceGroupName / -CapacityName explicitly."
}

Write-Step "SCU capacity delete"
Write-Info "Subscription:  $SubscriptionId"
Write-Info "Resource group: $ResourceGroupName"
Write-Info "Capacity name: $CapacityName"

az account set --subscription $SubscriptionId | Out-Null

# -------- 2. Cost estimate based on createdAt (WHOLE-HOUR ceiling) ----------
# SCU billing is NOT prorated: any partial hour bills as a full hour at $4/SCU.
# 1 min alive = $4. 61 min alive = $8.
$estHours      = $null   # elapsed real hours (for transparency)
$billedHours   = $null   # whole-hour ceiling used for cost math
$estCost       = $null
$units = if ($scc.units) { [int]$scc.units } else { 1 }
if ($scc.createdAt) {
    try {
        $start = [datetime]::Parse($scc.createdAt).ToUniversalTime()
        $elapsed = ((Get-Date).ToUniversalTime() - $start).TotalHours
        if ($elapsed -lt 0) { $elapsed = 0 }
        $estHours    = [math]::Round($elapsed, 2)
        $billedHours = [math]::Max(1, [int][math]::Ceiling($elapsed))
        $estCost     = $billedHours * $units * 4
        Write-Info "Created at:    $($scc.createdAt) UTC  (elapsed ${estHours} h)"
        Write-Info "Billed hours:  $billedHours  (SCU is whole-hour billed, not prorated)"
        Write-Info "Cost so far:   \$$estCost USD  ($billedHours h x $units SCU x \$4/SCU/hr)"
    } catch { }
}

# -------- 2b. Cancel any pending auto-delete (prevent race) -----------------
if ($scc.autoDelete -and ($scc.autoDelete.deletionMode -eq 'server')) {
    # SERVER mode: cancel the Logic App reaper run so it doesn't fire later.
    # (The RG delete below is idempotent, but cancelling avoids a duplicate/late run.)
    $runId     = "$($scc.autoDelete.automationRunId)".Trim()
    $logicAppId = "$($scc.autoDelete.logicAppId)".Trim()
    if ($runId -and $logicAppId) {
        try {
            az rest --method post `
                --uri "$logicAppId/runs/$runId/cancel?api-version=2016-06-01" `
                --output none 2>$null
            Write-Info "Cancelled server-side auto-delete (Logic App run $runId)."
        } catch {
            Write-Info "Could not cancel Logic App run $runId (it may have already completed); proceeding with delete."
        }
    }
} elseif ($scc.autoDelete -and $scc.autoDelete.pid) {
    # LOCAL mode: kill the nohup sleep timer.
    $autoPid = "$($scc.autoDelete.pid)".Trim()
    if ($autoPid) {
        try {
            if ($IsWindows) {
                Stop-Process -Id $autoPid -Force -ErrorAction SilentlyContinue
            } else {
                & bash -c "kill -0 $autoPid 2>/dev/null && kill $autoPid 2>/dev/null" | Out-Null
            }
            Write-Info "Cancelled pending auto-delete timer (PID $autoPid)."
        } catch { }
    }
}

# -------- 3. Existence check -------------------------------------------------
$capId = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.SecurityCopilot/capacities/$CapacityName"
$exists = az resource show --ids $capId --output json 2>$null
$alreadyGone = -not [bool]$exists
if ($alreadyGone) {
    Write-Ok "Capacity does not exist (already deleted or never created)."
}

# -------- 4. Delete (gated on -Confirm) -------------------------------------
$deleted = $false
if (-not $alreadyGone) {
    if (-not $Confirm) {
        Write-Warn2 "DELETE requires -Confirm. Re-run with:"
        Write-Host "  ./scripts/Remove-SccCapacity.ps1 -Confirm" -ForegroundColor Gray
        exit 4
    }
    Write-Info "Deleting capacity..."
    $delOut = az resource delete --ids $capId --output json 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Err2 "Capacity delete failed."
        Write-Host $delOut -ForegroundColor Red
        throw "Capacity delete failed."
    }
    $deleted = $true
    Write-Ok "Capacity deleted. Billing for '$CapacityName' has stopped."
}

# -------- 4b. Nuke the dedicated RG (belt-and-suspenders) -------------------
# Only delete the RG when (a) the caller explicitly asked, OR (b) progress.json
# marks the RG as dedicated (i.e., Ensure-SccCapacity.ps1 created it).
$rgNuked = $false
$shouldNukeRg = $NukeResourceGroup -or ($scc.dedicatedRg -eq $true)
if ($shouldNukeRg -and ($deleted -or $alreadyGone)) {
    $rgExists = az group exists --name $ResourceGroupName --subscription $SubscriptionId
    if ($rgExists -eq 'true') {
        Write-Info "Nuking dedicated resource group '$ResourceGroupName' (--no-wait)..."
        az group delete --name $ResourceGroupName --subscription $SubscriptionId --yes --no-wait | Out-Null
        $rgNuked = $true
        Write-Ok "Resource group delete initiated (runs async in Azure)."
    }
}

# -------- 5. Strip from progress.json ---------------------------------------
if (($deleted -or $alreadyGone) -and (Test-Path $ProgressJsonPath)) {
    try {
        $j = Get-Content $ProgressJsonPath -Raw | ConvertFrom-Json
        if ($j.phases.'5_agent_build'.sccCapacity) {
            $j.phases.'5_agent_build'.PSObject.Properties.Remove('sccCapacity') | Out-Null
            $j | ConvertTo-Json -Depth 32 | Set-Content $ProgressJsonPath -Encoding UTF8
            Write-Ok "Removed phases.5_agent_build.sccCapacity from $ProgressJsonPath."
        }
    } catch {
        Write-Warn2 "Could not update $ProgressJsonPath (non-fatal): $($_.Exception.Message)"
    }
}

return @{
    CapacityId            = $capId
    Deleted               = $deleted
    AlreadyGone           = $alreadyGone
    ResourceGroupNuked    = $rgNuked
    ElapsedHours          = $estHours
    BilledHours           = $billedHours
    EstimatedCostUsd      = $estCost
}
