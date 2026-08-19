<#
.SYNOPSIS
    Validates prerequisites for the Sentinel Data Connector and Agent Builder workflow.
.DESCRIPTION
    Checks az CLI, login status, subscription access, required resource providers,
    and the two distinct permission sets the developer needs to complete in the
    Defender portal before the agent reaches Phase 2:

      Step A — Set Primary Sentinel Workspace
        (Entra Security Administrator or higher)
        AND (Subscription Owner OR (User Access Administrator + Microsoft Sentinel Contributor))

      Step B — Onboard / Setup Data Lake
        (Subscription Owner OR Contributor — for billing setup)
        AND (Entra Global Administrator OR Security Administrator)
.PARAMETER SubscriptionId
    Azure subscription ID to validate against.
.PARAMETER TenantId
    Entra tenant ID (optional if already logged in).
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$TenantId,

    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId
)

$ErrorActionPreference = "Stop"
$script:HasErrors = $false

function Write-Status($msg, $status) {
    $icon = if ($status -eq "pass") { "✅" } elseif ($status -eq "fail") { "❌"; $script:HasErrors = $true } else { "⚠️" }
    Write-Host "$icon $msg"
}

# 1. Check az CLI installed
Write-Host "`n=== Sentinel Data Connector and Agent Builder Prerequisites Validation ===`n"
Write-Host "Two prerequisite steps must be completed manually in the Defender portal:" -ForegroundColor Cyan
Write-Host "  Step A — Set Primary Sentinel Workspace" -ForegroundColor Cyan
Write-Host "  Step B — Onboard / Setup Data Lake" -ForegroundColor Cyan
Write-Host "This script verifies you have the roles required for both.`n" -ForegroundColor Cyan
try {
    $azVersion = az version --output json | ConvertFrom-Json
    Write-Status "Azure CLI installed (v$($azVersion.'azure-cli'))" "pass"
} catch {
    Write-Status "Azure CLI not installed. Install from https://aka.ms/installazurecli" "fail"
    exit 1
}

# 2. Check login status
try {
    $account = az account show --output json 2>$null | ConvertFrom-Json
    Write-Status "Logged in as: $($account.user.name)" "pass"
} catch {
    Write-Status "Not logged in. Running 'az login'..." "warn"
    if ($TenantId) { az login --tenant $TenantId } else { az login }
    $account = az account show --output json | ConvertFrom-Json
}

# 3. Verify tenant
if ($TenantId -and $account.tenantId -ne $TenantId) {
    Write-Status "Wrong tenant. Switching to $TenantId..." "warn"
    az login --tenant $TenantId
    $account = az account show --output json | ConvertFrom-Json
}
$TenantId = $account.tenantId
Write-Status "Tenant: $TenantId" "pass"

# 4. Set subscription
if ($SubscriptionId) {
    az account set --subscription $SubscriptionId
    Write-Status "Subscription set: $SubscriptionId" "pass"
} else {
    $SubscriptionId = $account.id
    Write-Status "Using default subscription: $SubscriptionId" "pass"
}

# 5. Check required resource providers
$requiredProviders = @(
    "Microsoft.OperationalInsights",
    "Microsoft.SecurityInsights",
    "Microsoft.Insights"
)

Write-Host "`n--- Resource Providers ---"
foreach ($provider in $requiredProviders) {
    $state = az provider show --namespace $provider --query "registrationState" -o tsv 2>$null
    if ($state -eq "Registered") {
        Write-Status "$provider registered" "pass"
    } else {
        Write-Status "$provider not registered. Registering..." "warn"
        az provider register --namespace $provider
    }
}

# ============================================================
# PERMISSION VALIDATION — gather Entra + Azure roles once
# ============================================================
# This script validates the two distinct permission sets the developer needs
# to complete BEFORE the agent reaches Phase 2:
#
#   STEP A — Set Primary Sentinel Workspace in the Defender portal
#     Requires: (Entra Security Administrator OR higher)
#               AND (Subscription Owner
#                    OR (User Access Administrator + Microsoft Sentinel Contributor))
#
#   STEP B — Onboard / Setup Data Lake in the Defender portal
#     Requires: (Subscription Owner OR Subscription Contributor — for billing setup)
#               AND (Entra Global Administrator OR Security Administrator)
#
# Both steps are performed manually in the Defender portal — the
# agent only checks that the developer has the right roles to do them.

Write-Host "`n--- Gathering role assignments ---"

# Resolve the signed-in user's object ID. Using --assignee with a UPN/email is
# unreliable for MSA / guest / B2B accounts (e.g., gmail signups) because the
# display email differs from the mangled guest UPN Entra stores. Object ID is
# the only stable identifier, and combining it with --include-inherited /
# --include-groups picks up roles granted via management groups or AAD groups.
$currentUserId = az ad signed-in-user show --query id -o tsv 2>$null
if (-not $currentUserId) {
    Write-Status "Could not resolve signed-in user object ID via 'az ad signed-in-user show'. Falling back to UPN-based lookup (may miss MSA / guest accounts)." "warn"
    $azureRoles = az role assignment list --assignee $account.user.name --subscription $SubscriptionId --include-inherited --include-groups --output json 2>$null | ConvertFrom-Json
} else {
    $azureRoles = az role assignment list --assignee-object-id $currentUserId --subscription $SubscriptionId --include-inherited --include-groups --output json 2>$null | ConvertFrom-Json
}

# Entra directory roles
$entraRoles = @()
if ($currentUserId) {
    $entraRoles = az rest --method GET `
        --url "https://graph.microsoft.com/v1.0/me/memberOf/microsoft.graph.directoryRole" `
        --query "value[].displayName" -o json 2>$null | ConvertFrom-Json
}

$hasSecurityAdmin   = [bool]($entraRoles | Where-Object { $_ -match "Security Administrator|Global Administrator" })
$hasGlobalAdmin     = [bool]($entraRoles | Where-Object { $_ -match "Global Administrator" })
$isOwner            = [bool]($azureRoles | Where-Object { $_.roleDefinitionName -eq "Owner" })
$isContributor      = [bool]($azureRoles | Where-Object { $_.roleDefinitionName -eq "Contributor" })
$hasUAA             = [bool]($azureRoles | Where-Object { $_.roleDefinitionName -eq "User Access Administrator" })
$hasSentinelContrib = [bool]($azureRoles | Where-Object { $_.roleDefinitionName -eq "Microsoft Sentinel Contributor" })

# ============================================================
# STEP A — Set Primary Sentinel Workspace (Defender portal)
# ============================================================
Write-Host "`n=== Step A: Set Primary Sentinel Workspace (Defender portal) ==="
Write-Host "Required: (Entra Security Administrator or higher) AND (Subscription Owner OR (User Access Administrator + Microsoft Sentinel Contributor))"

$stepA_entra = $hasSecurityAdmin
$stepA_azure = $isOwner -or ($hasUAA -and $hasSentinelContrib)

if ($stepA_entra) {
    Write-Status "Entra ID: Security Administrator (or higher) ✓" "pass"
} else {
    Write-Status "Entra ID: MISSING 'Security Administrator' (or higher) — required to set Primary Sentinel workspace" "fail"
    Write-Host "   Remediation: Ask your Entra ID admin to assign 'Security Administrator' role."
    Write-Host "   Navigate: Entra admin center → Roles and administrators → Security Administrator → Add assignment"
}

if ($isOwner) {
    Write-Status "Azure: Subscription Owner ✓ (covers UAA + Sentinel Contributor)" "pass"
} elseif ($hasUAA -and $hasSentinelContrib) {
    Write-Status "Azure: User Access Administrator + Microsoft Sentinel Contributor ✓" "pass"
} else {
    Write-Status "Azure: MISSING required Azure roles for Step A" "fail"
    if (-not $hasUAA) {
        Write-Host "   Missing: User Access Administrator"
        Write-Host "   Remediation: az role assignment create --assignee-object-id $currentUserId --assignee-principal-type User --role 'User Access Administrator' --scope /subscriptions/$SubscriptionId"
    }
    if (-not $hasSentinelContrib) {
        Write-Host "   Missing: Microsoft Sentinel Contributor"
        Write-Host "   Remediation: az role assignment create --assignee-object-id $currentUserId --assignee-principal-type User --role 'Microsoft Sentinel Contributor' --scope /subscriptions/$SubscriptionId"
    }
    Write-Host "   Note: Alternatively, get 'Owner' on the subscription which covers both."
}

if ($stepA_entra -and $stepA_azure) {
    Write-Host "✅ Step A ready — you can set the Primary Sentinel workspace in the Defender portal." -ForegroundColor Green
} else {
    Write-Host "❌ Step A blocked — resolve the missing roles above before setting Primary Sentinel workspace." -ForegroundColor Red
}

# ============================================================
# STEP B — Onboard / Setup Data Lake (Defender portal)
# ============================================================
Write-Host "`n=== Step B: Onboard / Setup Data Lake (Defender portal) ==="
Write-Host "Required: (Subscription Owner OR Contributor — for billing) AND (Entra Global Administrator OR Security Administrator)"

$stepB_azure = $isOwner -or $isContributor
$stepB_entra = $hasGlobalAdmin -or $hasSecurityAdmin

if ($isOwner) {
    Write-Status "Azure: Subscription Owner ✓ (billing setup)" "pass"
} elseif ($isContributor) {
    Write-Status "Azure: Subscription Contributor ✓ (billing setup)" "pass"
} else {
    Write-Status "Azure: MISSING 'Owner' or 'Contributor' on subscription — required for data lake billing setup" "fail"
    Write-Host "   Remediation: Ask the subscription owner to assign 'Contributor' (minimum) or 'Owner'."
}

if ($hasGlobalAdmin) {
    Write-Status "Entra ID: Global Administrator ✓" "pass"
} elseif ($hasSecurityAdmin) {
    Write-Status "Entra ID: Security Administrator ✓" "pass"
} else {
    Write-Status "Entra ID: MISSING 'Global Administrator' or 'Security Administrator' — required for data lake onboarding" "fail"
    Write-Host "   Remediation: Ask your Entra ID admin to assign 'Security Administrator' (minimum) or 'Global Administrator'."
}

if ($stepB_azure -and $stepB_entra) {
    Write-Host "✅ Step B ready — you can onboard / setup Data Lake in the Defender portal." -ForegroundColor Green
} else {
    Write-Host "❌ Step B blocked — resolve the missing roles above before data lake onboarding." -ForegroundColor Red
}

# ============================================================
# SUMMARY
# ============================================================
Write-Host "`n=== Prerequisite Check Complete ===`n"
Write-Host "Subscription: $SubscriptionId"
Write-Host "Tenant: $TenantId"
Write-Host "User: $($account.user.name)"

if ($script:HasErrors) {
    Write-Host "`n❌ BLOCKING ISSUES FOUND — resolve the above errors before proceeding.`n" -ForegroundColor Red
    exit 1
} else {
    Write-Host "`n✅ All prerequisites met — ready to proceed.`n" -ForegroundColor Green
    exit 0
}
