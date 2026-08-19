<#
.SYNOPSIS
    Reliably detects whether the current tenant is onboarded to Microsoft Sentinel Data Lake
    and (optionally) drives remediation for Stale / NotOnboarded states.

.DESCRIPTION
    Phase 2 pre-flight for the Sentinel Data Connector and Agent Builder. Replaces the prior single-RG check
    for "msg-resources-<guid>" + Microsoft.SentinelPlatformServices/sentinelplatformservices,
    which was unreliable because:
      - The platform resource and its RG persist after the data lake is offboarded.
      - The linked Sentinel workspace can be deleted/stale while the resource still reports
        provisioningState=Succeeded.
      - The data lake is tenant-level; scanning one RG can never confirm tenant state.

    Reliable detection uses a combined signal:
      1. Tenant-wide ARM scan (Azure Resource Graph) for any
         Microsoft.SentinelPlatformServices/sentinelplatformservices resource.
      2. Verification that at least one Sentinel-enabled workspace exists by GETting
         Microsoft.SecurityInsights/onboardingStates/default (api-version 2025-09-01)
         on each Log Analytics workspace found via Resource Graph.

    Classification:
      - Onboarded   : platform resource exists AND >=1 workspace has onboardingStates/default
      - Stale       : platform resource exists but no live Sentinel-enabled workspace found
      - NotOnboarded: no platform resource found

    Remediation (when -Remediate is supplied):
      - Onboarded   : short-circuit, report primary workspace candidates.
      - Stale       : surface KB Issue #3 cleanup guidance.
      - NotOnboarded + >=1 Sentinel workspace: list, prompt for pick, print Defender portal steps.
      - NotOnboarded + 0 Sentinel workspaces : create RG + LAW + onboard Sentinel via az CLI,
        then print Defender portal data-lake setup steps.

.PARAMETER SubscriptionId
    Optional. If supplied, scoping for any auto-created resources (NotOnboarded branch).
    Detection always runs tenant-wide.

.PARAMETER ResourceGroupName
    Optional. Used only when auto-creating a workspace in the NotOnboarded branch.

.PARAMETER WorkspaceName
    Optional. Used only when auto-creating a workspace in the NotOnboarded branch.

.PARAMETER Location
    Optional. Azure region for any auto-created workspace. Defaults to eastus2
    (KB Issue #2 — known capacity-friendly region).

.PARAMETER Remediate
    Switch. When set, prompts the user and executes the matching remediation branch.
    Without this, the script only detects and reports.

.NOTES
    Required roles to fully drive remediation:
      - Microsoft Entra Security Administrator (or higher)
      - AND (Subscription Owner OR (User Access Administrator at subscription + Sentinel Contributor))
    Region is locked to the primary workspace once the tenant is onboarded; only same-region
    workspaces auto-attach to the data lake afterward.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$SubscriptionId,

    [Parameter(Mandatory = $false)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory = $false)]
    [string]$WorkspaceName,

    [Parameter(Mandatory = $false)]
    [string]$Location = "eastus2",

    [Parameter(Mandatory = $false)]
    [switch]$Remediate
)

$ErrorActionPreference = "Stop"
$SentinelOnboardingApi = "2025-09-01"
$PlatformResourceType  = "Microsoft.SentinelPlatformServices/sentinelplatformservices"

function Write-Section($Title) {
    Write-Host ""
    Write-Host "=== $Title ===" -ForegroundColor Cyan
}

function Invoke-AzRestJson {
    param([string]$Method = "GET", [string]$Uri)
    try {
        $raw = az rest --method $Method --url $Uri --only-show-errors 2>$null
        if (-not $raw) { return $null }
        return ($raw | ConvertFrom-Json)
    } catch {
        return $null
    }
}

function Ensure-AzCli {
    try { az account show --only-show-errors --output none 2>$null } catch {
        throw "Azure CLI is not signed in. Run 'az login' (and 'az login --tenant <tenantId>' if needed) before re-running."
    }
}

function Get-PlatformResources {
    # Tenant-wide via Azure Resource Graph; falls back to per-subscription scan if graph extension missing.
    $kql = "resources | where type =~ '$PlatformResourceType' | project id, name, location, subscriptionId, resourceGroup, properties"
    $rgResult = az graph query -q $kql --output json --only-show-errors 2>$null
    if ($LASTEXITCODE -eq 0 -and $rgResult) {
        $parsed = $rgResult | ConvertFrom-Json
        return @($parsed.data)
    }

    Write-Host "  resource-graph extension not available; falling back to per-subscription scan..." -ForegroundColor DarkGray
    $found = @()
    $subs = az account list --query "[?state=='Enabled'].id" -o tsv --only-show-errors
    foreach ($s in $subs) {
        $list = az resource list --subscription $s --resource-type $PlatformResourceType -o json --only-show-errors 2>$null
        if ($list) {
            $parsed = $list | ConvertFrom-Json
            foreach ($r in $parsed) { $found += $r }
        }
    }
    return $found
}

function Get-AllLogAnalyticsWorkspaces {
    $kql = "resources | where type =~ 'Microsoft.OperationalInsights/workspaces' | project id, name, location, subscriptionId, resourceGroup"
    $rgResult = az graph query -q $kql --output json --only-show-errors 2>$null
    if ($LASTEXITCODE -eq 0 -and $rgResult) {
        $parsed = $rgResult | ConvertFrom-Json
        return @($parsed.data)
    }

    $found = @()
    $subs = az account list --query "[?state=='Enabled'].id" -o tsv --only-show-errors
    foreach ($s in $subs) {
        $list = az monitor log-analytics workspace list --subscription $s -o json --only-show-errors 2>$null
        if ($list) {
            $parsed = $list | ConvertFrom-Json
            foreach ($w in $parsed) {
                $found += [pscustomobject]@{
                    id             = $w.id
                    name           = $w.name
                    location       = $w.location
                    subscriptionId = $s
                    resourceGroup  = ($w.id -split "/")[4]
                }
            }
        }
    }
    return $found
}

function Test-SentinelEnabled {
    param([string]$WorkspaceResourceId)
    $uri = "https://management.azure.com$WorkspaceResourceId/providers/Microsoft.SecurityInsights/onboardingStates/default?api-version=$SentinelOnboardingApi"
    $result = Invoke-AzRestJson -Method GET -Uri $uri
    return ($null -ne $result -and $null -ne $result.id)
}

function Get-SentinelWorkspaces {
    param([array]$Workspaces)
    $sentinel = @()
    foreach ($w in $Workspaces) {
        if (Test-SentinelEnabled -WorkspaceResourceId $w.id) {
            $sentinel += $w
        }
    }
    return $sentinel
}

function Show-DefenderPortalSteps {
    param([string]$WorkspaceName, [string]$Region)
    Write-Host ""
    Write-Host "Defender portal — manual steps required (data-lake onboarding is portal-driven):" -ForegroundColor Yellow
    Write-Host "  1. Open https://security.microsoft.com" -ForegroundColor White
    Write-Host "  2. Settings -> Microsoft Sentinel -> SIEM workspaces" -ForegroundColor White
    if ($WorkspaceName) {
        Write-Host "  3. Connect workspace: $WorkspaceName  (region: $Region)" -ForegroundColor White
    } else {
        Write-Host "  3. Connect the Sentinel workspace you want to use as primary" -ForegroundColor White
    }
    Write-Host "  4. Set the workspace as Primary" -ForegroundColor White
    Write-Host "  5. Data lake -> Start setup -> select subscription and resource group" -ForegroundColor White
    Write-Host "  6. Wait up to 60 minutes for provisioning to complete" -ForegroundColor White
    Write-Host ""
    Write-Host "Note: The data lake region is locked to the primary workspace's region." -ForegroundColor DarkYellow
    Write-Host "Only same-region workspaces will auto-attach after onboarding." -ForegroundColor DarkYellow
}

function Show-KBIssue3 {
    Write-Host ""
    Write-Host "KB Issue #3 — 'Something went wrong' during onboarding:" -ForegroundColor Yellow
    Write-Host "  - Verify the resource group and subscription tied to the platform resource still exist." -ForegroundColor White
    Write-Host "  - If the linked Sentinel workspace was deleted, the platform resource is stale." -ForegroundColor White
    Write-Host "  - Remove the stale Microsoft.SentinelPlatformServices/sentinelplatformservices resource(s)," -ForegroundColor White
    Write-Host "    then re-run onboarding from the Defender portal." -ForegroundColor White
    Write-Host ""
    Write-Host "Escalation:" -ForegroundColor DarkYellow
    Write-Host "  - Customers: open a Microsoft Defender support case." -ForegroundColor White
    Write-Host "  - ISVs/partners: https://aka.ms/intakeform (App Assure)." -ForegroundColor White
}

function Invoke-CreateWorkspaceFlow {
    param([string]$SubId, [string]$Rg, [string]$Wsn, [string]$Loc)

    if (-not $SubId) { $SubId = (az account show --query id -o tsv) }
    if (-not $Rg)    { $Rg    = Read-Host "Resource group name to create (or existing)" }
    if (-not $Wsn)   { $Wsn   = Read-Host "Log Analytics workspace name to create" }
    if (-not $Loc)   { $Loc   = "eastus2" }

    Write-Host ""
    Write-Host "Plan:" -ForegroundColor Cyan
    Write-Host "  Subscription : $SubId" -ForegroundColor White
    Write-Host "  Resource grp : $Rg ($Loc)" -ForegroundColor White
    Write-Host "  Workspace    : $Wsn ($Loc)" -ForegroundColor White
    $confirm = Read-Host "Proceed with create + Sentinel onboarding? [y/N]"
    if ($confirm -notmatch '^(y|yes)$') {
        Write-Host "Aborted by user." -ForegroundColor Yellow
        return $null
    }

    Write-Host "Creating resource group..." -ForegroundColor DarkGray
    az group create --subscription $SubId --name $Rg --location $Loc --only-show-errors --output none

    Write-Host "Creating Log Analytics workspace..." -ForegroundColor DarkGray
    az monitor log-analytics workspace create `
        --subscription $SubId --resource-group $Rg `
        --workspace-name $Wsn --location $Loc `
        --only-show-errors --output none

    $wsId = az monitor log-analytics workspace show --subscription $SubId -g $Rg -n $Wsn --query id -o tsv

    Write-Host "Onboarding workspace to Microsoft Sentinel..." -ForegroundColor DarkGray
    $onboardUri = "https://management.azure.com$wsId/providers/Microsoft.SecurityInsights/onboardingStates/default?api-version=$SentinelOnboardingApi"
    az rest --method PUT --url $onboardUri --body '{\"properties\":{}}' --only-show-errors --output none

    Write-Host "Sentinel onboarding submitted for $Wsn." -ForegroundColor Green
    return [pscustomobject]@{ Id = $wsId; Name = $Wsn; Location = $Loc; SubscriptionId = $SubId; ResourceGroup = $Rg }
}

# ------------------- Main -------------------

Ensure-AzCli

Write-Section "Sentinel Data Lake — Tenant Detection"

Write-Host "Scanning tenant for Sentinel platform resources..." -ForegroundColor DarkGray
$platformResources = Get-PlatformResources

Write-Host "Scanning tenant for Log Analytics workspaces..." -ForegroundColor DarkGray
$workspaces = Get-AllLogAnalyticsWorkspaces

Write-Host "Probing $($workspaces.Count) workspace(s) for Sentinel onboarding state..." -ForegroundColor DarkGray
$sentinelWorkspaces = Get-SentinelWorkspaces -Workspaces $workspaces

# Classify
$state = "NotOnboarded"
if ($platformResources.Count -gt 0 -and $sentinelWorkspaces.Count -gt 0) {
    $state = "Onboarded"
} elseif ($platformResources.Count -gt 0 -and $sentinelWorkspaces.Count -eq 0) {
    $state = "Stale"
}

Write-Section "Detection Result: $state"
Write-Host "  Platform resources found    : $($platformResources.Count)" -ForegroundColor White
Write-Host "  Sentinel-enabled workspaces : $($sentinelWorkspaces.Count)" -ForegroundColor White

switch ($state) {
    "Onboarded" {
        Write-Host ""
        Write-Host "Tenant is onboarded to Sentinel Data Lake." -ForegroundColor Green
        Write-Host "Candidate primary workspace(s):" -ForegroundColor Cyan
        foreach ($w in $sentinelWorkspaces) {
            Write-Host "  - $($w.name)  [$($w.location)]  sub=$($w.subscriptionId)  rg=$($w.resourceGroup)" -ForegroundColor White
        }
        exit 0
    }

    "Stale" {
        Write-Host ""
        Write-Host "Tenant has Sentinel platform resource(s) but NO live Sentinel-enabled workspace." -ForegroundColor Yellow
        Write-Host "This typically means the originally onboarded workspace was deleted." -ForegroundColor Yellow
        foreach ($r in $platformResources) {
            Write-Host "  Stale platform resource: $($r.id)" -ForegroundColor DarkYellow
        }
        Show-KBIssue3
        exit 2
    }

    "NotOnboarded" {
        Write-Host ""
        Write-Host "Tenant is NOT onboarded to Sentinel Data Lake." -ForegroundColor Yellow

        if (-not $Remediate) {
            Write-Host ""
            Write-Host "Re-run with -Remediate to drive onboarding interactively." -ForegroundColor DarkGray
            exit 1
        }

        if ($sentinelWorkspaces.Count -gt 0) {
            Write-Host ""
            Write-Host "Existing Sentinel workspaces detected — pick one to use as primary:" -ForegroundColor Cyan
            $i = 0
            foreach ($w in $sentinelWorkspaces) {
                Write-Host "  [$i] $($w.name)  [$($w.location)]  sub=$($w.subscriptionId)  rg=$($w.resourceGroup)" -ForegroundColor White
                $i++
            }
            $pick = Read-Host "Index of workspace to set as primary"
            if ($pick -notmatch '^\d+$' -or [int]$pick -ge $sentinelWorkspaces.Count) {
                Write-Host "Invalid selection." -ForegroundColor Red
                exit 1
            }
            $chosen = $sentinelWorkspaces[[int]$pick]
            Show-DefenderPortalSteps -WorkspaceName $chosen.name -Region $chosen.location
            exit 0
        }

        Write-Host ""
        Write-Host "No Sentinel-enabled workspaces found anywhere in the tenant." -ForegroundColor Yellow
        Write-Host "Proceeding to auto-create resource group + Log Analytics workspace + Sentinel onboarding." -ForegroundColor Cyan
        $created = Invoke-CreateWorkspaceFlow -SubId $SubscriptionId -Rg $ResourceGroupName -Wsn $WorkspaceName -Loc $Location
        if ($created) {
            Show-DefenderPortalSteps -WorkspaceName $created.Name -Region $created.Location
        }
        exit 0
    }
}
