<#
.SYNOPSIS
    Discovers or creates a Security Copilot SCU capacity
    (Microsoft.SecurityCopilot/capacities) so the Phase 5A developer can skip
    the portal SCU-creation step.

.DESCRIPTION
    Security Copilot capacity (Security Compute Units, "SCU") is a real ARM
    resource. The Security Copilot portal flow at
    https://securitycopilot.microsoft.com/ wraps the same ARM PUT we issue
    here. Automating the create means the developer's only remaining
    portal click is "create workspace" (no public API for that yet).

    Flow:
      1. Register the Microsoft.SecurityCopilot RP if not yet registered
         (idempotent no-op when already registered).
      2. Discover existing capacities in the subscription:
           - 0 found  -> require explicit -Confirm (cost gate) and create.
           - 1 found  -> reuse silently, surface name + units.
           - 2+ found -> list and ask the caller to pass -CapacityName.
      3. On create, write to ARM via `az resource create`.
      4. Persist the capacity id/name/region/units to
         config/progress.json.phases.5_agent_build.sccCapacity.

    COST WARNING — surfaced to the developer in the agent chat
    BEFORE this script runs. SCU capacity is billed hourly at roughly
    $4 USD per SCU per hour (~ $2900 USD per SCU per month if left
    running). ISV Success Program developer tenants can burn their
    monthly Azure credit grant in days if a capacity is left running.
    Always pair Ensure-SccCapacity.ps1 with Remove-SccCapacity.ps1 when
    the testing session ends.

.PARAMETER SubscriptionId
    Target subscription. Defaults to phases.2_data_lake_onboarding.subscriptionId
    in progress.json, then `az account show`.

.PARAMETER ResourceGroupName
    LOCKED to the dedicated SCU RG named '<CapacityName>-rg' (defaulting to
    '<isv-slug>-scu-rg'). This script does NOT accept a developer-provided RG.
    Rationale: the SCU lives in its OWN blast-radius — when
    Remove-SccCapacity.ps1 runs with -NukeResourceGroup, it deletes the SCU
    AND the RG, guaranteeing the secure compute unit is entirely cleaned up
    and nothing keeps billing after teardown. If the caller passes
    -ResourceGroupName and the value does not match '<CapacityName>-rg', the
    script exits with code 6 and tells the agent to refuse the
    override.

.PARAMETER AutoDeleteAfterMinutes
    LEGACY / power-user override. Default 0 = unused. Schedules the auto-delete
    timer using minutes-relative math (now + N min). When > 0, takes precedence
    over -HoursOfBudget. Prefer -HoursOfBudget for normal use because SCU is
    billed in WHOLE clock-hour blocks (not rolling 60-min windows) — a
    minutes-relative timer that crosses an hour boundary silently doubles the
    bill. The PID and scheduled deletion time are persisted to
    progress.json.phases.5_agent_build.sccCapacity.autoDelete so the agent
    can cancel the timer at deletion prompt time.

.PARAMETER HoursOfBudget
    Default 1. Number of CLOCK-HOUR blocks of paid SCU time the developer
    wants. Schedules the auto-delete timer to fire at
    startOfHour(createdAt) + (N hours) - DeleteBufferMinutes (default 12 ->
    :48; the 12-min cushion absorbs the SCU delete (a long-running operation) trailing ~10-min backend
    deprovisioning settlement before the next clock-hour rolls over and
    silently bills another $4). This is the cost-optimal default — testing
    started inside a clock-hour block always pays for that block; the timer
    ensures no second block is paid by accident. Set HoursOfBudget=2 for a
    2-block session, etc. Ignored when -AutoDeleteAfterMinutes > 0 (legacy
    override).
    See:
    https://learn.microsoft.com/en-us/copilot/security/security-compute-units-capacity#how-provisioned-and-overage-scus-are-billed

.PARAMETER DeleteBufferMinutes
    Default 12. Minutes before the next clock-hour boundary at which the
    clock-hour-aligned auto-delete fires (:48). SCU delete is an async long-running operation
    whose final billing settlement lands ~10 min after the request; a :55
    delete settles ~:05 of the next block and double-bills ($4 -> $8). The
    12-min cushion keeps that settlement inside the paid block. Raise toward
    15 (:45) for extra safety at the cost of a few testing minutes.

.PARAMETER NoAutoDelete
    Disables the auto-delete timer. Equivalent to -AutoDeleteAfterMinutes 0.
    Only set after the developer has explicitly opted out in chat.

.PARAMETER CapacityName
    Capacity name. Defaults to '<isv-slug>-scu' from progress.json.companyName.

.PARAMETER Location
    Azure region for the capacity resource. Defaults to
    phases.2_data_lake_onboarding.workspace.region (then 'eastus'). The script
    tries the requested region FIRST. If ARM rejects with
    LocationNotAvailableForResourceType, the script queries
    Microsoft.SecurityCopilot/capacities for the live allowlist (today:
    australiaeast, eastus, uksouth, westeurope), picks the nearest
    geo-affinity match, and exits with code 5 — the agent chat must
    then surface the suggestion to the developer and re-invoke with
    -AcceptRemappedRegion to proceed. -Geo is auto-derived from the final
    region unless the caller explicitly pins it.

.PARAMETER AcceptRemappedRegion
    Set ONLY after the developer has explicitly approved an alternate region
    (e.g., after the script returned exit 5). Re-runs the create against the
    Location passed on this invocation without re-prompting.

.PARAMETER Geo
    Capacity geo for prompt evaluation. One of 'US', 'EU', 'UK', 'AU'.
    Default 'US'.

.PARAMETER Units
    Number of SCUs. Default 1. Override to 2+ for richer parallelism.
    Each unit adds ~ $4/hr to the bill.

.PARAMETER ProgressJsonPath
    Path to config/progress.json. Default 'config/progress.json'.

.PARAMETER Confirm
    REQUIRED for any path that issues a fresh CREATE. The agent
    chat must obtain explicit developer consent (acknowledging the
    ~ $4/SCU/hour cost) before invoking the script with -Confirm. Without
    -Confirm, the script refuses to create and exits with code 4.

.PARAMETER SkipRoleCheck
    Skip the Entra + Azure RBAC pre-flight. Use only when the required
    roles (Security Administrator in Entra + Contributor on the subscription)
    are granted via a group membership the role-check API can't enumerate
    for the signed-in user. Otherwise leave it off — the pre-flight saves
    a failed ARM create round-trip and emits a structured remediation block
    the developer can hand to their Global Administrator.

.EXITCODES
    0  Capacity reused or created successfully.
    3  Role pre-flight failed (missing Entra and/or Azure roles). A structured
       remediation block is written to .scu-role-preflight.json containing the
       caller identity, missing roles, exact `az` grant commands, and the
       Azure portal click-paths a Global Administrator can use.
    4  -Confirm missing when a CREATE was required (cost gate).
    5  Region not available for Microsoft.SecurityCopilot/capacities in this
       subscription. Script prints the suggested fallback region; the
       agent must ask developer permission and re-invoke with -Location
       <approved> -AcceptRemappedRegion.
    6  Caller passed -ResourceGroupName that does not match the dedicated
       '<CapacityName>-rg' convention. The agent must refuse the
       override and explain the dedicated-RG-for-SCU benefit.
    Other non-zero  Underlying az / ARM failure (message surfaced).

.OUTPUTS
    Hashtable: @{
        CapacityId   = '/subscriptions/.../providers/Microsoft.SecurityCopilot/capacities/...'
        Name         = '...'
        Region       = '...'
        Geo          = '...'
        Units        = 1
        AlreadyExisted = $true|$false
        CreatedAt    = '<ISO-8601>' (only when freshly created)
    }
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)] [string]$SubscriptionId,
    [Parameter(Mandatory=$false)] [string]$ResourceGroupName,
    [Parameter(Mandatory=$false)] [string]$CapacityName,
    [Parameter(Mandatory=$false)] [string]$Location,
    [Parameter(Mandatory=$false)]
    [ValidateSet('US','EU','UK','AU')]
    [string]$Geo = 'US',
    [Parameter(Mandatory=$false)] [int]$Units = 1,
    [Parameter(Mandatory=$false)] [string]$ProgressJsonPath = 'config/progress.json',
    [Parameter(Mandatory=$false)] [switch]$Confirm,
    [Parameter(Mandatory=$false)] [switch]$SkipRoleCheck,
    [Parameter(Mandatory=$false)] [switch]$AcceptRemappedRegion,
    [Parameter(Mandatory=$false)] [int]$AutoDeleteAfterMinutes = 0,
    [Parameter(Mandatory=$false)] [int]$HoursOfBudget = 1,
    [Parameter(Mandatory=$false)] [int]$DeleteBufferMinutes = 12,
    [Parameter(Mandatory=$false)] [switch]$NoAutoDelete,
    [Parameter(Mandatory=$false)]
    [ValidateSet('local','server')]
    [string]$DeletionMode = 'local',
    [Parameter(Mandatory=$false)] [string]$NotifyEmail,
    [Parameter(Mandatory=$false)] [string]$AutomationConfigPath = 'config/scu-automation.json'
)

$ErrorActionPreference = 'Stop'

function Write-Step($m) { Write-Host "`n=== $m ===" -ForegroundColor Cyan }
function Write-Ok  ($m) { Write-Host "✅ $m" -ForegroundColor Green }
function Write-Info($m) { Write-Host "   $m" }
function Write-Warn2($m){ Write-Host "⚠️  $m" -ForegroundColor Yellow }
function Write-Err2 ($m){ Write-Host "❌ $m" -ForegroundColor Red }

# -------- 1. Hydrate defaults from progress.json -----------------------------
$progress = $null
if (Test-Path $ProgressJsonPath) {
    try { $progress = Get-Content $ProgressJsonPath -Raw | ConvertFrom-Json } catch { $progress = $null }
}
$phase2 = $progress.phases.'2_data_lake_onboarding'

if (-not $SubscriptionId)    { $SubscriptionId    = $phase2.subscriptionId }
if (-not $SubscriptionId)    { $SubscriptionId    = az account show --query id -o tsv }

# Dedicated-RG default: when the caller did NOT pass -ResourceGroupName, derive
# a dedicated RG name from the (about-to-be-resolved) CapacityName so the SCU
# lives in its own isolated RG. This makes Remove-SccCapacity.ps1
# -NukeResourceGroup safe to run: deleting the RG can only affect SCU-related
# resources because nothing else lives there.
$useDedicatedRg = -not $PSBoundParameters.ContainsKey('ResourceGroupName')

if (-not $Location)          { $Location          = $phase2.workspace.region }
if (-not $Location)          { $Location          = 'eastus' }

if (-not $CapacityName) {
    $slug = ($progress.companyName -replace '[^a-zA-Z0-9]','').ToLower()
    if (-not $slug) { $slug = 'isv' }
    $CapacityName = "$slug-scu"
}

if ($useDedicatedRg) {
    $ResourceGroupName = "$CapacityName-rg"
}
# Dedicated-RG guard. The script ALWAYS creates and uses the dedicated SCU RG.
# If the caller passed -ResourceGroupName and it doesn't match the dedicated
# convention, refuse the override and exit 6 — the agent surfaces the
# "clean teardown via RG delete" rationale to the developer.
if (-not $useDedicatedRg) {
    $expectedRg = "$CapacityName-rg"
    if ($ResourceGroupName -ne $expectedRg) {
        Write-Err2 "-ResourceGroupName override is not allowed. The SCU must live in its own dedicated RG ('$expectedRg')."
        Write-Host ""
        Write-Host "Why a dedicated RG?" -ForegroundColor Yellow
        Write-Host "  Putting the SCU in its own RG keeps deletion clean — Remove-SccCapacity.ps1" -ForegroundColor Yellow
        Write-Host "  deletes the RG when teardown runs, which guarantees the Secure Compute Unit" -ForegroundColor Yellow
        Write-Host "  is entirely removed and nothing keeps billing after the test session ends." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Re-run without -ResourceGroupName (the script will create '$expectedRg' for you)." -ForegroundColor Yellow
        exit 6
    }
}
if (-not $ResourceGroupName) { $ResourceGroupName = $phase2.workspace.resourceGroup }

if (-not $SubscriptionId)    { throw "SubscriptionId not resolved. Pass -SubscriptionId or run 'az login'." }
if (-not $ResourceGroupName) { throw "ResourceGroupName not resolved. Pass -ResourceGroupName or complete Phase 2." }

# -------- 1a. SCU-region helpers (used on ARM rejection, not upfront) --------
# Microsoft.SecurityCopilot/capacities is only deployable in a narrow allowlist
# (today: australiaeast, eastus, uksouth, westeurope). We DO NOT silently
# remap the developer's requested region — per the agent contract,
# we try what the developer asked for first, and on
# LocationNotAvailableForResourceType we exit with code 5 and a suggested
# fallback so the agent can prompt the developer for approval.
function Get-NearestSccRegion {
    param([string]$Requested, [string[]]$Supported)
    $r = $Requested.ToLower()
    $usRegions = @('eastus','eastus2','eastus3','centralus','northcentralus','southcentralus','westus','westus2','westus3','westcentralus','canadacentral','canadaeast','mexicocentral','brazilsouth')
    $euRegions = @('westeurope','northeurope','francecentral','francesouth','germanywestcentral','germanynorth','swedencentral','swedensouth','switzerlandnorth','switzerlandwest','norwayeast','norwaywest','polandcentral','italynorth','spaincentral')
    $ukRegions = @('uksouth','ukwest')
    $auRegions = @('australiaeast','australiasoutheast','australiacentral','australiacentral2','newzealandnorth')
    $asiaRegions = @('eastasia','southeastasia','japaneast','japanwest','koreacentral','koreasouth','centralindia','southindia','westindia','jioindiawest')
    $meRegions = @('uaenorth','uaecentral','qatarcentral','israelcentral','southafricanorth','southafricawest')
    if ($Supported -contains $r) { return $r }
    foreach ($pair in @(
        @{ Pool = $usRegions;   Pick = @('eastus','westeurope','uksouth','australiaeast') },
        @{ Pool = $euRegions;   Pick = @('westeurope','uksouth','eastus','australiaeast') },
        @{ Pool = $ukRegions;   Pick = @('uksouth','westeurope','eastus','australiaeast') },
        @{ Pool = $auRegions;   Pick = @('australiaeast','eastus','westeurope','uksouth') },
        @{ Pool = $asiaRegions; Pick = @('australiaeast','eastus','westeurope','uksouth') },
        @{ Pool = $meRegions;   Pick = @('westeurope','uksouth','eastus','australiaeast') }
    )) {
        if ($pair.Pool -contains $r) {
            foreach ($cand in $pair.Pick) { if ($Supported -contains $cand) { return $cand } }
        }
    }
    return ($Supported | Select-Object -First 1)
}

function Get-GeoForRegion {
    param([string]$Region)
    switch ($Region.ToLower()) {
        'eastus'         { 'US' }
        'westeurope'     { 'EU' }
        'uksouth'        { 'UK' }
        'australiaeast'  { 'AU' }
        default          { 'US' }
    }
}

function Get-SccSupportedRegions {
    # Static known-good allowlist (matches the ARM error message). Always
    # union with whatever the RP live-query returns so a degraded RP response
    # (partial registration / policy filter) never narrows our suggestion
    # list below the platform truth.
    $static = @('eastus','westeurope','uksouth','australiaeast')
    try {
        $rpJson = az provider show --namespace Microsoft.SecurityCopilot --query "resourceTypes[?resourceType=='capacities'].locations" -o json 2>$null
        if ($rpJson) {
            $rpLocs = ($rpJson | ConvertFrom-Json) | Select-Object -First 1
            if ($rpLocs) {
                $live = @($rpLocs | ForEach-Object { ($_ -replace '\s','').ToLower() })
                return @($static + $live | Sort-Object -Unique)
            }
        }
    } catch { }
    return $static
}

# Auto-derive Geo from the (possibly-to-be-remapped) location unless caller pinned it.
if (-not $PSBoundParameters.ContainsKey('Geo') -or [string]::IsNullOrWhiteSpace($Geo)) {
    $Geo = Get-GeoForRegion -Region $Location
}

# -------- 1a-strict. Force $Location into the SCU-supported allowlist --------
# Microsoft.SecurityCopilot/capacities deploys ONLY in
# { australiaeast, eastus, uksouth, westeurope }. The Sentinel workspace
# region (used as the default $Location) is almost never one of those four,
# so we remap up-front by geo proximity rather than letting ARM reject the
# create with LocationNotAvailableForResourceType. This is silent — no
# developer prompt — because (a) SCU pricing is uniform across the four
# regions, (b) the proximity choice is deterministic from the workspace
# region, and (c) the developer cannot influence which one is chosen
# without explicitly passing -Location anyway.
$sccSupported = Get-SccSupportedRegions
if ($sccSupported -notcontains $Location.ToLower()) {
    $originalLocation = $Location
    $Location = Get-NearestSccRegion -Requested $Location -Supported $sccSupported
    $Geo      = Get-GeoForRegion -Region $Location
    Write-Info "Region '$originalLocation' is not in the SCU allowlist — remapped to '$Location' (geo $Geo) by proximity. SCU-supported regions: $($sccSupported -join ', ')."
}

Write-Step "SCU capacity ensure"
Write-Info "Subscription:  $SubscriptionId"
Write-Info "Resource group: $ResourceGroupName"
Write-Info "Capacity name: $CapacityName"
Write-Info "Region:        $Location"
Write-Info "Geo:           $Geo"
Write-Info "Units:         $Units"

az account set --subscription $SubscriptionId | Out-Null

# -------- 1b. Role pre-flight (Entra + Azure) --------------------------------
# Creating an SCU capacity needs BOTH:
#   - Entra directory role: Security Administrator OR Global Administrator
#   - Azure RBAC at SUBSCRIPTION scope: Contributor OR Owner.
# Why subscription scope? The script creates a brand-new dedicated RG
# ('<CapacityName>-rg') before creating the SCU. Creating a new RG requires
# 'Microsoft.Resources/subscriptions/resourceGroups/write' which only exists
# at subscription scope; once the RG is created the same sub-scope role
# inherits down to satisfy the SCU create. A role granted directly on an
# existing RG cannot create new sibling RGs and so cannot satisfy the
# dedicated-RG flow.
# We surface BOTH checks even if one fails, so the developer sees the full
# missing-role list in one shot. The script also writes a structured
# remediation block to .scu-role-preflight.json so the agent chat
# can render a ready-to-paste request the developer hands to a Global
# Administrator (both `az` CLI grant commands AND Azure portal click-paths).
if (-not $SkipRoleCheck) {
    Write-Step "Role pre-flight"

    $signedInId  = az ad signed-in-user show --query id -o tsv 2>$null
    $signedInUpn = az ad signed-in-user show --query userPrincipalName -o tsv 2>$null
    $tenantId    = az account show --query tenantId -o tsv 2>$null
    if (-not $signedInId) {
        Write-Warn2 "Could not resolve the signed-in user (are you signed in as a service principal?). Skipping role checks. Pass -SkipRoleCheck to suppress this warning."
    } else {
        Write-Info "Signed-in user: $signedInUpn ($signedInId)"

        # --- Entra check ----------------------------------------------------
        # Security Administrator templateId: 194ae4cb-b126-40b2-bd5b-6091b380977d
        # Global Administrator   templateId: 62e90394-69f5-4237-9190-012177145e10
        $hasEntraRole = $false
        $entraRoleName = $null
        $assignmentsJson = az rest --method get `
            --uri "https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignments?`$filter=principalId eq '$signedInId'" `
            --headers "ConsistencyLevel=eventual" -o json 2>$null
        if ($assignmentsJson) {
            try {
                $assignments = ($assignmentsJson | ConvertFrom-Json).value
                foreach ($a in $assignments) {
                    if ($a.roleDefinitionId -eq '194ae4cb-b126-40b2-bd5b-6091b380977d') { $hasEntraRole = $true; $entraRoleName = 'Security Administrator'; break }
                    if ($a.roleDefinitionId -eq '62e90394-69f5-4237-9190-012177145e10') { $hasEntraRole = $true; $entraRoleName = 'Global Administrator';  break }
                }
            } catch { }
        }
        if ($hasEntraRole) {
            Write-Ok "Entra role granted: $entraRoleName"
        } else {
            Write-Err2 "Entra role MISSING: Security Administrator on tenant."
        }

        # --- Azure RBAC check (SUBSCRIPTION scope only) ---------------------
        $hasAzureRole = $false
        $azureRoleName = $null
        $subScope = "/subscriptions/$SubscriptionId"
        $subAssignsJson = az role assignment list --assignee $signedInId --scope $subScope --include-inherited -o json 2>$null
        try {
            $subRoles = if ($subAssignsJson) { ($subAssignsJson | ConvertFrom-Json).roleDefinitionName } else { @() }
            if     ($subRoles -contains 'Owner')       { $hasAzureRole = $true; $azureRoleName = "Owner on subscription" }
            elseif ($subRoles -contains 'Contributor') { $hasAzureRole = $true; $azureRoleName = "Contributor on subscription" }
        } catch { }
        if ($hasAzureRole) {
            Write-Ok "Azure RBAC granted: $azureRoleName"
        } else {
            Write-Err2 "Azure RBAC MISSING: Contributor on subscription '$SubscriptionId' (required to create the dedicated RG '$ResourceGroupName' and the SCU capacity inside it)."
        }

        if (-not ($hasEntraRole -and $hasAzureRole)) {
            # --- Build structured remediation block -------------------------
            $missingRoles = @()
            if (-not $hasEntraRole) {
                $missingRoles += [ordered]@{
                    name             = 'Security Administrator'
                    type             = 'entra'
                    scope            = "/ (tenant $tenantId)"
                    roleDefinitionId = '194ae4cb-b126-40b2-bd5b-6091b380977d'
                    grantCli         = "az rest --method post --uri 'https://graph.microsoft.com/v1.0/roleManagement/directory/roleAssignments' --headers 'Content-Type=application/json' --body '{`"principalId`":`"$signedInId`",`"roleDefinitionId`":`"194ae4cb-b126-40b2-bd5b-6091b380977d`",`"directoryScopeId`":`"/`"}'"
                    grantCallerNeeds = 'Privileged Role Administrator OR Global Administrator'
                    portalPath       = "Entra admin center (entra.microsoft.com) -> Roles & admins -> Search 'Security Administrator' -> Open -> + Add assignments -> Select members -> add '$signedInUpn' -> Next -> Assignment type 'Active', 'Permanently assigned' -> Assign"
                }
            }
            if (-not $hasAzureRole) {
                $missingRoles += [ordered]@{
                    name             = 'Contributor'
                    type             = 'azure'
                    scope            = $subScope
                    roleDefinitionId = 'b24988ac-6180-42a0-ab88-20f7382dd24c'
                    grantCli         = "az role assignment create --assignee-object-id $signedInId --assignee-principal-type User --role Contributor --scope $subScope"
                    grantCallerNeeds = 'Owner OR User Access Administrator on the subscription'
                    portalPath       = "Azure portal (portal.azure.com) -> Subscriptions -> Open '$SubscriptionId' -> Access control (IAM) -> + Add -> Add role assignment -> Role 'Contributor' -> Next -> Assign access to 'User, group, or service principal' -> + Select members -> add '$signedInUpn' -> Review + assign"
                }
            }

            $remediation = [ordered]@{
                verdict        = 'role_preflight_failed'
                signedIn       = [ordered]@{
                    upn            = $signedInUpn
                    objectId       = $signedInId
                    tenantId       = $tenantId
                    subscriptionId = $SubscriptionId
                }
                missingRoles   = $missingRoles
                propagationMin = 10
                postGrantSteps = @(
                    "Wait 5-10 min for the assignment(s) to propagate.",
                    "Run 'az logout' and 'az login --tenant $tenantId' to refresh the local token cache.",
                    "Re-run scripts/Ensure-SccCapacity.ps1 -Confirm to retry."
                )
                generatedAt    = (Get-Date).ToUniversalTime().ToString("o")
            }
            $remediationPath = Join-Path (Get-Location) '.scu-role-preflight.json'
            try {
                ($remediation | ConvertTo-Json -Depth 8) | Set-Content -Path $remediationPath -Encoding utf8
                Write-Host ""
                Write-Host "Structured remediation block written to: $remediationPath" -ForegroundColor Yellow
                Write-Host "The agent will render this as a ready-to-paste request you can send to your Global Administrator." -ForegroundColor Yellow
            } catch {
                Write-Warn2 "Could not write $remediationPath ($_). Surfacing missing roles to stdout only."
            }
            Write-Host ""
            Write-Host "Missing role(s) above must be granted before this script can create the SCU capacity." -ForegroundColor Yellow
            Write-Host "(Skip this pre-flight with -SkipRoleCheck if the roles are granted via a group membership the check can't see.)" -ForegroundColor DarkGray
            exit 3
        }
    }
}

# -------- 2. Provider registration (idempotent) ------------------------------
$rpState = az provider show --namespace Microsoft.SecurityCopilot --query registrationState -o tsv 2>$null
if ($rpState -ne 'Registered') {
    Write-Info "Registering Microsoft.SecurityCopilot RP (current state: '$rpState')..."
    az provider register --namespace Microsoft.SecurityCopilot --wait | Out-Null
    Write-Ok "Microsoft.SecurityCopilot RP registered."
} else {
    Write-Info "Microsoft.SecurityCopilot RP already registered."
}

# -------- 3. Discover existing capacities in this subscription ---------------
$existingJson = az resource list `
    --resource-type Microsoft.SecurityCopilot/capacities `
    --subscription $SubscriptionId `
    --output json 2>$null
$existing = @()
if ($existingJson) {
    try { $existing = $existingJson | ConvertFrom-Json } catch { $existing = @() }
}

# Direct hit on the requested name?
$match = $existing | Where-Object { $_.name -eq $CapacityName -and $_.resourceGroup -eq $ResourceGroupName }

if ($match) {
    Write-Ok "Capacity '$CapacityName' already exists in '$ResourceGroupName'."
    $existingUnits = $match.properties.numberOfUnits
    if ($existingUnits -and $existingUnits -ne $Units) {
        Write-Warn2 "Existing capacity has $existingUnits unit(s); requested $Units. NOT mutating an existing capacity. Adjust manually if needed."
    }
    $result = @{
        CapacityId     = $match.id
        Name           = $match.name
        Region         = $match.location
        Geo            = $match.properties.geo
        Units          = $existingUnits
        AlreadyExisted = $true
    }
} elseif ($existing.Count -ge 1) {
    Write-Warn2 "Found $($existing.Count) existing SCU capacity/ies in subscription, none matching name '$CapacityName':"
    foreach ($c in $existing) {
        Write-Info " - $($c.name)  rg=$($c.resourceGroup)  region=$($c.location)  units=$($c.properties.numberOfUnits)"
    }
    Write-Warn2 "Re-run with -CapacityName <one-of-the-above> to reuse, or with -Confirm to create '$CapacityName' anyway."
    if (-not $Confirm) { exit 4 }
    # fall through to create
    $match = $null
}

# -------- 4. Create when missing (gated on -Confirm) -------------------------
if (-not $match) {
    if (-not $Confirm) {
        Write-Err2 "No matching SCU capacity. CREATE requires -Confirm (developer cost-acknowledgement gate)."
        Write-Host ""
        Write-Host "COST WARNING:" -ForegroundColor Yellow
        Write-Host "  SCU capacity bills at ~ `$4 USD per SCU per hour while it exists."
        Write-Host "  $Units SCU = ~ `$$([math]::Round($Units * 4)) / hr = ~ `$$([math]::Round($Units * 4 * 24)) / day = ~ `$$([math]::Round($Units * 4 * 730)) / month."
        Write-Host "  Run Remove-SccCapacity.ps1 immediately when your testing session ends."
        Write-Host ""
        Write-Host "Re-run with -Confirm to proceed:" -ForegroundColor Yellow
        Write-Host "  ./scripts/Ensure-SccCapacity.ps1 -Confirm" -ForegroundColor Gray
        exit 4
    }

    # Ensure the RG exists.
    $rgExists = az group exists --name $ResourceGroupName --subscription $SubscriptionId
    if ($rgExists -ne 'true') {
        Write-Info "Resource group '$ResourceGroupName' missing. Creating in '$Location'..."
        az group create --name $ResourceGroupName --location $Location --subscription $SubscriptionId --output none
        Write-Ok "Resource group created."
    }

    Write-Info "Creating capacity '$CapacityName' in '$ResourceGroupName' (region $Location, geo $Geo, units $Units)..."
    $props = @{
        numberOfUnits       = $Units
        crossGeoCompute     = 'NotAllowed'
        geo                 = $Geo
    } | ConvertTo-Json -Compress

    $createOut = az resource create `
        --subscription $SubscriptionId `
        --resource-group $ResourceGroupName `
        --name $CapacityName `
        --resource-type Microsoft.SecurityCopilot/capacities `
        --location $Location `
        --properties $props `
        --output json 2>&1
    if ($LASTEXITCODE -ne 0) {
        $errText = ($createOut | Out-String)
        Write-Err2 "Capacity create failed."
        Write-Host $errText -ForegroundColor Red

        # Detect region-not-available — surface a suggestion and exit 5 so the
        # agent can ask the developer for permission to retry in an
        # alternate region instead of silently remapping.
        if ($errText -match 'LocationNotAvailableForResourceType' -or
            $errText -match "location '.*?' is not available for resource type") {

            $supported = Get-SccSupportedRegions
            $suggested = Get-NearestSccRegion -Requested $Location -Supported $supported
            $suggestedGeo = Get-GeoForRegion -Region $suggested

            Write-Host ""
            Write-Host "REGION NOT AVAILABLE FOR Microsoft.SecurityCopilot/capacities:" -ForegroundColor Yellow
            Write-Host "  Requested region : $Location"
            Write-Host "  Supported regions: $($supported -join ', ')"
            Write-Host "  Suggested fallback: $suggested  (geo $suggestedGeo)"
            Write-Host ""
            Write-Host "Next step (developer approval required):" -ForegroundColor Yellow
            Write-Host "  Re-run with the approved region:" -ForegroundColor Gray
            Write-Host "  ./scripts/Ensure-SccCapacity.ps1 -Confirm -AcceptRemappedRegion -Location $suggested" -ForegroundColor Gray
            exit 5
        }

        throw "Capacity create failed."
    }
    $created = $createOut | ConvertFrom-Json
    Write-Ok "Capacity created: $($created.id)"
    $result = @{
        CapacityId     = $created.id
        Name           = $created.name
        Region         = $created.location
        Geo            = $Geo
        Units          = $Units
        AlreadyExisted = $false
        CreatedAt      = (Get-Date).ToUniversalTime().ToString('o')
    }
}

# -------- 4b. Schedule auto-delete (clock-hour-aligned by default) -----------
# SCU is billed in WHOLE clock-hour blocks (NOT rolling 60-min windows). See:
# https://learn.microsoft.com/en-us/copilot/security/security-compute-units-capacity#how-provisioned-and-overage-scus-are-billed
# Default: align delete to :48 of the last paid clock hour (12-min cushion absorbs
# the SCU delete (a long-running operation) trailing ~10-min backend settlement before the next block bills).
# Legacy: -AutoDeleteAfterMinutes <n> preserves minutes-relative math for power users.
$autoDeleteInfo = $null
$shouldSchedule = (-not $result.AlreadyExisted) -and (-not $NoAutoDelete)
if ($shouldSchedule) {
    $createdAtUtc = (Get-Date).ToUniversalTime()

    if ($AutoDeleteAfterMinutes -gt 0) {
        # LEGACY minutes-relative path
        $scheduledForUtc = $createdAtUtc.AddMinutes($AutoDeleteAfterMinutes)
        $alignmentMode   = 'minutes-relative'
        $effectiveMinutes = $AutoDeleteAfterMinutes
        $effectiveHoursOfBudget = $null
        Write-Warn2 "Using LEGACY -AutoDeleteAfterMinutes math. Risk: if the window crosses a clock-hour boundary, you will be billed for TWO blocks. Prefer -HoursOfBudget for cost-optimal alignment."
    } else {
        # CLOCK-HOUR-ALIGNED default path
        $startOfHour     = $createdAtUtc.Date.AddHours($createdAtUtc.Hour)
        $scheduledForUtc = $startOfHour.AddHours($HoursOfBudget).AddMinutes(-$DeleteBufferMinutes)
        # Floor: if the proposed delete is in the past or too close to now,
        # push by one hour at a time until safe (>= now + 2 min).
        $minSafe = $createdAtUtc.AddMinutes(2)
        while ($scheduledForUtc -lt $minSafe) { $scheduledForUtc = $scheduledForUtc.AddHours(1) }
        $alignmentMode   = 'clock-hour'
        $effectiveMinutes = [int]($scheduledForUtc - $createdAtUtc).TotalMinutes
        $effectiveHoursOfBudget = $HoursOfBudget
    }
    $sleepSec     = [int]($scheduledForUtc - $createdAtUtc).TotalSeconds
    if ($sleepSec -lt 60) { $sleepSec = 60 }  # absolute floor
    $scheduledFor = $scheduledForUtc.ToString('o')
    # Warn 10 min before delete; floor at now+1min if the window is very short.
    $notifyForUtc = $scheduledForUtc.AddMinutes(-10)
    if ($notifyForUtc -lt $createdAtUtc.AddMinutes(1)) { $notifyForUtc = $createdAtUtc.AddMinutes(1) }
    $notifyFor    = $notifyForUtc.ToString('o')

    if ($DeletionMode -eq 'server') {
        # ---- SERVER-SIDE auto-delete via the one-time-deployed Logic App "reaper" ----
        # Reliable even if the developer's workstation powers off: the wait+delete run in Azure.
        if (-not (Test-Path $AutomationConfigPath)) {
            Write-Warn2 "DeletionMode=server but '$AutomationConfigPath' not found. Run Setup-ScuAutoDelete.ps1 once per subscription first. Falling back to LOCAL timer."
            $DeletionMode = 'local'
        }
    }

    if ($DeletionMode -eq 'server') {
        $auto = Get-Content $AutomationConfigPath -Raw | ConvertFrom-Json
        if ($auto.subscriptionId -and ($auto.subscriptionId -ne $SubscriptionId)) {
            Write-Warn2 "scu-automation.json is for subscription $($auto.subscriptionId) but this capacity is in $SubscriptionId. Re-run Setup-ScuAutoDelete.ps1 for this subscription. Falling back to LOCAL timer."
            $DeletionMode = 'local'
        }
        if (-not $NotifyEmail) {
            $signedInUpn = az account show --query user.name -o tsv 2>$null
            if ($signedInUpn) { $NotifyEmail = "$signedInUpn".Trim() }
        }
        if (-not $NotifyEmail) {
            Write-Warn2 "DeletionMode=server requires a notification email (could not resolve signed-in UPN). Falling back to LOCAL timer."
            $DeletionMode = 'local'
        }
    }

    if ($DeletionMode -eq 'server') {
        try {
            # Least-privilege: grant the reaper MI Contributor ONLY on this session's dedicated RG.
            # Cascades away when the RG is deleted. ACS Contributor was granted once at Setup time.
            $rgId = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName"
            Write-Info "Granting reaper MI Contributor on '$ResourceGroupName' (least-privilege, per-session)..."
            az role assignment create `
                --assignee-object-id $auto.miPrincipalId `
                --assignee-principal-type ServicePrincipal `
                --role Contributor `
                --scope $rgId --output none 2>$null
            # Role propagation can lag; the Logic App waits >=1 min before any ARM call so this is safe.

            # Callback URL is a SAS secret — fetch fresh each session, never persist it.
            $cbUrl = az rest --method post `
                --uri "$($auto.logicAppId)/triggers/Start/listCallbackUrl?api-version=2016-06-01" `
                --query value -o tsv
            if (-not $cbUrl) { throw "Could not obtain Logic App callback URL." }

            $payload = @{
                subscriptionId = $SubscriptionId
                resourceGroup  = $ResourceGroupName
                capacityName   = $result.Name
                deleteAt       = $scheduledFor
                notifyAt       = $notifyFor
                email          = $NotifyEmail
                acsEndpoint    = $auto.acsEndpoint
                senderAddress  = $auto.senderAddress
            } | ConvertTo-Json -Compress

            $resp = Invoke-WebRequest -Method Post -Uri $cbUrl -ContentType 'application/json' -Body $payload -UseBasicParsing
            $runId = $resp.Headers['x-ms-workflow-run-id']
            if ($runId -is [array]) { $runId = $runId[0] }

            $autoDeleteInfo = [pscustomobject]@{
                deletionMode        = 'server'
                scheduledAt         = $createdAtUtc.ToString('o')
                scheduledFor        = $scheduledFor
                notifyAt            = $notifyFor
                notifyEmail         = $NotifyEmail
                afterMinutes        = $effectiveMinutes
                hoursOfBudget       = $effectiveHoursOfBudget
                alignmentMode       = $alignmentMode
                logicAppId          = $auto.logicAppId
                automationRunId     = "$runId".Trim()
                nukeRg              = [bool]$useDedicatedRg
            }
            Write-Ok "Server-side auto-delete armed: Logic App run $runId will delete '$ResourceGroupName' at $($scheduledForUtc.ToString('HH:mm')) UTC (warning email to $NotifyEmail ~10 min prior). No client needs to stay running."
            Write-Info "To cancel: run Remove-SccCapacity.ps1 -Confirm (cancels the Logic App run and deletes now)."
        } catch {
            Write-Warn2 "Server-side arming failed ($($_.Exception.Message)). Falling back to LOCAL timer."
            $DeletionMode = 'local'
        }
    }

    if ($DeletionMode -eq 'local') {
        $logDir = Join-Path (Split-Path $PSScriptRoot -Parent) '.scu-autodelete'
        if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }
        $logPath = Join-Path $logDir "$($result.Name).log"
        $scriptPath = Join-Path $PSScriptRoot 'Remove-SccCapacity.ps1'

        $nukeFlag = if ($useDedicatedRg) { '-NukeResourceGroup' } else { '' }
        $cmd = "sleep $sleepSec; pwsh -NoProfile -File `"$scriptPath`" -SubscriptionId `"$SubscriptionId`" -ResourceGroupName `"$ResourceGroupName`" -CapacityName `"$($result.Name)`" -Confirm $nukeFlag >> `"$logPath`" 2>&1"

        if ($IsWindows) {
            $proc = Start-Process -FilePath 'pwsh' -ArgumentList @('-NoProfile','-Command', $cmd) -WindowStyle Hidden -PassThru
            $autoPid = $proc.Id
        } else {
            $autoPid = & bash -c "nohup bash -c '$cmd' > /dev/null 2>&1 & echo `$!"
            $autoPid = "$autoPid".Trim()
        }

        $autoDeleteInfo = [pscustomobject]@{
            deletionMode    = 'local'
            pid             = $autoPid
            scheduledAt     = $createdAtUtc.ToString('o')
            scheduledFor    = $scheduledFor
            afterMinutes    = $effectiveMinutes
            hoursOfBudget   = $effectiveHoursOfBudget
            alignmentMode   = $alignmentMode
            logPath         = $logPath
            nukeRg          = [bool]$useDedicatedRg
        }
        if ($alignmentMode -eq 'clock-hour') {
            Write-Ok "Auto-delete scheduled for $($scheduledForUtc.ToString('HH:mm')) UTC (:48 of the last paid clock hour; HoursOfBudget=$HoursOfBudget; PID $autoPid). Log: $logPath"
        } else {
            Write-Ok "Auto-delete scheduled in $effectiveMinutes min (PID $autoPid). Log: $logPath"
        }
        Write-Warn2 "LOCAL timer: if this workstation sleeps/powers off before $($scheduledForUtc.ToString('HH:mm')) UTC, the SCU will NOT be deleted and keeps billing. Use -DeletionMode server for workstation-independent teardown."
        Write-Info "To cancel: kill $autoPid    (or run Remove-SccCapacity.ps1 -Confirm)"
    }
} elseif ($NoAutoDelete -and -not $result.AlreadyExisted) {
    Write-Warn2 "Auto-delete DISABLED (-NoAutoDelete). You MUST run Remove-SccCapacity.ps1 when done — \$4/hr per SCU keeps accruing, billed in WHOLE clock-hour blocks."
}

# -------- 5. Persist to progress.json ----------------------------------------
if (Test-Path $ProgressJsonPath) {
    try {
        $j = Get-Content $ProgressJsonPath -Raw | ConvertFrom-Json
        if (-not $j.phases) { $j | Add-Member -NotePropertyName phases -NotePropertyValue ([pscustomobject]@{}) -Force }
        if (-not $j.phases.'5_agent_build') {
            $j.phases | Add-Member -NotePropertyName '5_agent_build' -NotePropertyValue ([pscustomobject]@{}) -Force
        }
        $j.phases.'5_agent_build' | Add-Member -NotePropertyName sccCapacity -NotePropertyValue ([pscustomobject]@{
            id           = $result.CapacityId
            name         = $result.Name
            region       = $result.Region
            geo          = $result.Geo
            units        = $result.Units
            createdAt    = if ($result.CreatedAt) { $result.CreatedAt } else { $null }
            dedicatedRg  = [bool]$useDedicatedRg
            resourceGroup = $ResourceGroupName
            autoDelete   = $autoDeleteInfo
            note         = "SCU is billed in WHOLE hours at \$4/SCU/hour (NOT prorated — 1 min alive = \$4)."
        }) -Force
        $j | ConvertTo-Json -Depth 32 | Set-Content $ProgressJsonPath -Encoding UTF8
        Write-Ok "Persisted phases.5_agent_build.sccCapacity to $ProgressJsonPath."
    } catch {
        Write-Warn2 "Could not update $ProgressJsonPath (non-fatal): $($_.Exception.Message)"
    }
}

Write-Host ""
Write-Host "Next step:" -ForegroundColor Yellow
Write-Host "  1. Open https://securitycopilot.microsoft.com/ in the same tenant."
Write-Host "  2. The capacity '$($result.Name)' will appear in the picker."
Write-Host "  3. Create a workspace bound to it (this step is still UI-only — no public API)."
Write-Host "  4. When you finish testing, run: ./scripts/Remove-SccCapacity.ps1" -ForegroundColor Yellow

return $result
