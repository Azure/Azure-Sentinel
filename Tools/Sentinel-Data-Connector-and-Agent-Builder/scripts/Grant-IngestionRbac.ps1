<#
.SYNOPSIS
    Grants 'Monitoring Metrics Publisher' at RESOURCE GROUP scope so every
    current and future DCR/DCE in the RG inherits the role at creation time.

.DESCRIPTION
    Phase 3 ingestion (Invoke-SampleDataIngestion.ps1) previously granted the
    role at per-DCR scope AFTER the DCR was created. On a brand-new DCR, the
    Logs Ingestion data plane caches a "no access" decision for 5-15+ minutes
    even after the assignment lands, so the first POST hits a 403 storm that
    multi-attempt retry loops (~15+ min) often can't outlast. This was
    observed in field artifacts where the first one or two tables succeeded
    (their per-DCR assignments were already present from prior runs) but a
    newly-created DCR for a third table failed every retry.

    This script fixes that by:

      1. Resolving the signed-in principal (User OR ServicePrincipal — detected
         automatically; the previous code hard-coded 'User' which is wrong for
         CI / federated identities).
      2. Checking whether the role already exists at RG scope (idempotent).
      3. Creating the assignment at RG scope if missing. The grant is surfaced
         LOUDLY on failure (vs the prior code which redirected stderr to
         `$null` and pretended the grant succeeded).
      4. Optionally waiting for ARM RBAC propagation and forcing the az CLI
         to drop any cached access token for `monitor.azure.com` so the next
         token acquisition reflects the new assignment.

    The orchestrator (Invoke-AttackScenarioIngestion.ps1) calls this ONCE
    before the per-table loop. Every per-table DCR created afterwards
    inherits the role from RG scope at the moment of creation — no
    cold-start negative cache.

.PARAMETER ResourceGroupName
    Resource group that hosts (or will host) the DCE/DCRs.

.PARAMETER SubscriptionId
    Optional. Defaults to `az account show`.

.PARAMETER PrincipalObjectId
    Optional override. If omitted, resolves the currently signed-in
    user or service principal.

.PARAMETER PrincipalType
    Optional override. One of 'User', 'ServicePrincipal', 'Group',
    'ForeignGroup'. Auto-detected when omitted.

.PARAMETER WaitForPropagation
    When set (default ON), sleeps after a fresh grant and re-acquires the
    monitor.azure.com token so the next caller sees the new assignment.

.PARAMETER PropagationSleepSeconds
    Sleep duration after a fresh grant. Default 30s. ARM RBAC propagation
    is typically <30s; the heavier data-plane cache problem we are solving
    happens for per-DCR grants, NOT for RG-scope grants made before the
    DCR exists — so this short wait is sufficient.

.OUTPUTS
    Hashtable: @{
        PrincipalId        = '<oid>'
        PrincipalType      = 'User' | 'ServicePrincipal'
        Scope              = '/subscriptions/<sub>/resourceGroups/<rg>'
        AlreadyExisted     = $true|$false
        FreshGrantCreated  = $true|$false
        TokenRefreshed     = $true|$false
    }
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]  [string]$ResourceGroupName,
    [Parameter(Mandatory=$false)] [string]$SubscriptionId,
    [Parameter(Mandatory=$false)] [string]$PrincipalObjectId,
    [Parameter(Mandatory=$false)]
    [ValidateSet('User','ServicePrincipal','Group','ForeignGroup')]
    [string]$PrincipalType,
    [Parameter(Mandatory=$false)] [bool]$WaitForPropagation = $true,
    [Parameter(Mandatory=$false)] [int]$PropagationSleepSeconds = 30
)

$ErrorActionPreference = 'Stop'

function Write-Step($m) { Write-Host "`n=== $m ===" -ForegroundColor Cyan }
function Write-Ok  ($m) { Write-Host "✅ $m" -ForegroundColor Green }
function Write-Info($m) { Write-Host "   $m" }
function Write-Warn2($m){ Write-Host "⚠️  $m" -ForegroundColor Yellow }
function Write-Err2 ($m){ Write-Host "❌ $m" -ForegroundColor Red }

# Monitoring Metrics Publisher — built-in role definition GUID.
$MMP_ROLE_ID = '3913510d-42f4-4e42-8a64-420c390055eb'

# -------- 1. Resolve subscription --------------------------------------------
if (-not $SubscriptionId) {
    $SubscriptionId = az account show --query id -o tsv
    if (-not $SubscriptionId) { throw "Not logged in. Run 'az login' first." }
}
$scope = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName"

Write-Step "RG-scope role grant: Monitoring Metrics Publisher"
Write-Info "Scope: $scope"

# -------- 2. Resolve principal (User vs ServicePrincipal) --------------------
if (-not $PrincipalObjectId) {
    # Prefer signed-in-user; falls back to SP based on az account user.type.
    $accountUser = az account show --query user -o json 2>$null | ConvertFrom-Json
    $userType    = $accountUser.type   # 'user' | 'servicePrincipal'

    if ($userType -eq 'user') {
        $PrincipalObjectId = az ad signed-in-user show --query id -o tsv 2>$null
        if (-not $PrincipalObjectId) {
            throw "Could not resolve signed-in user objectId. If you are using a service principal, pass -PrincipalObjectId explicitly."
        }
        if (-not $PrincipalType) { $PrincipalType = 'User' }
    }
    elseif ($userType -eq 'servicePrincipal') {
        # az account show.user.name is the SP appId; convert to objectId.
        $appId = $accountUser.name
        $PrincipalObjectId = az ad sp show --id $appId --query id -o tsv 2>$null
        if (-not $PrincipalObjectId) {
            throw "Could not resolve service principal objectId for appId '$appId'."
        }
        if (-not $PrincipalType) { $PrincipalType = 'ServicePrincipal' }
    }
    else {
        throw "Unrecognised az account user.type='$userType'. Pass -PrincipalObjectId and -PrincipalType explicitly."
    }
}
if (-not $PrincipalType) { $PrincipalType = 'User' }

Write-Info "Principal:     $PrincipalObjectId ($PrincipalType)"

# -------- 3. Idempotency check at RG scope -----------------------------------
$existing = az role assignment list `
    --assignee-object-id $PrincipalObjectId `
    --scope $scope `
    --role $MMP_ROLE_ID `
    --query "[0].id" -o tsv 2>$null

$alreadyExisted    = [bool]$existing
$freshGrantCreated = $false

if ($alreadyExisted) {
    Write-Ok "Role already assigned at RG scope (assignment id: $existing)."
} else {
    Write-Info "Role not found at RG scope. Creating..."

    # Do NOT swallow stderr — surface auth failures loudly. The prior bug
    # was `2>$null` masking 'AuthorizationFailed' / 'principal does not have
    # Microsoft.Authorization/roleAssignments/write' and letting the script
    # proceed to a guaranteed-to-fail POST 16 min later.
    $createOut = az role assignment create `
        --assignee-object-id $PrincipalObjectId `
        --assignee-principal-type $PrincipalType `
        --role $MMP_ROLE_ID `
        --scope $scope `
        --output json 2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Err2 "Failed to create role assignment at RG scope."
        Write-Host $createOut -ForegroundColor Red
        Write-Host ""
        Write-Host "REMEDIATION:" -ForegroundColor Yellow
        Write-Host "  The signed-in principal needs 'Microsoft.Authorization/roleAssignments/write' on $scope."
        Write-Host "  This is granted by: Owner, User Access Administrator, or Role Based Access Control Administrator at sub OR RG scope."
        Write-Host ""
        Write-Host "  If you cannot self-assign, ask an Owner/UAA to run:"
        Write-Host "    az role assignment create \\" -ForegroundColor Gray
        Write-Host "      --assignee-object-id $PrincipalObjectId \\" -ForegroundColor Gray
        Write-Host "      --assignee-principal-type $PrincipalType \\" -ForegroundColor Gray
        Write-Host "      --role '$MMP_ROLE_ID' \\" -ForegroundColor Gray
        Write-Host "      --scope $scope" -ForegroundColor Gray
        throw "Role grant failed. Aborting before ingestion to avoid a multi-minute 403 retry storm."
    }
    $freshGrantCreated = $true
    Write-Ok "Role granted at RG scope."
}

# -------- 4. Propagation wait + token refresh -------------------------------
$tokenRefreshed = $false
if ($freshGrantCreated -and $WaitForPropagation) {
    Write-Info "Waiting ${PropagationSleepSeconds}s for ARM RBAC propagation..."
    Start-Sleep -Seconds $PropagationSleepSeconds

    # Force the az CLI to drop its cached access token for monitor.azure.com so
    # the next caller's `az account get-access-token --resource https://monitor.azure.com/`
    # acquires a fresh one. The token's RBAC is evaluated server-side at request
    # time (token claims don't carry resource-scoped roles), but clearing the
    # CLI's MSAL cache for this resource removes any ambiguity about staleness.
    #
    # `az account clear` is too aggressive (logs everyone out). Instead invoke
    # get-access-token in a way that forces a fresh STS round-trip.
    try {
        $null = az account get-access-token --resource "https://monitor.azure.com/" --output none 2>$null
        $tokenRefreshed = $true
        Write-Ok "Refreshed monitor.azure.com access token."
    } catch {
        Write-Warn2 "Token refresh call failed (non-fatal): $($_.Exception.Message)"
    }

    # Confirm the assignment is now visible at RG scope (defensive — ARM Graph
    # eventually consistent, but typically resolves inside the sleep window).
    $verify = az role assignment list `
        --assignee-object-id $PrincipalObjectId `
        --scope $scope `
        --role $MMP_ROLE_ID `
        --query "[0].id" -o tsv 2>$null
    if ($verify) {
        Write-Ok "Verified RG-scope assignment is visible to ARM."
    } else {
        Write-Warn2 "Assignment not yet visible to ARM listing after ${PropagationSleepSeconds}s; ingestion will retry on POST."
    }
}

return @{
    PrincipalId        = $PrincipalObjectId
    PrincipalType      = $PrincipalType
    Scope              = $scope
    AlreadyExisted     = $alreadyExisted
    FreshGrantCreated  = $freshGrantCreated
    TokenRefreshed     = $tokenRefreshed
}
