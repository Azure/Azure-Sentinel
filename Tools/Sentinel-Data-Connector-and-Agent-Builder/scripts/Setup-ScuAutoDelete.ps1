<#
.SYNOPSIS
    One-time per-subscription deploy of the server-side SCU auto-delete engine
    (Phase 5A Option 1). After this runs once, every `create scu` that chooses
    server-side teardown just POSTs a one-shot start request to the deployed
    Logic App — no per-session infrastructure, no client dependency.

.DESCRIPTION
    Deploys infra/scu-autodelete/scu-autodelete.bicep into a dedicated
    automation resource group:
      - Consumption Logic App (the "reaper") with a system-assigned managed identity
      - Azure Communication Services + Email service + Azure-managed sender domain
      - Role assignment letting the Logic App MI send mail through ACS

    Then records the automation's resource IDs to config/scu-automation.json so
    Ensure-SccCapacity.ps1 (server mode) can find it. The Logic App trigger
    callback URL is a secret and is NOT stored — Ensure-SccCapacity.ps1 fetches
    it fresh each session via `az rest`.

    The per-session RG-delete permission for the MI is NOT granted here (RGs are
    created per session); Ensure-SccCapacity.ps1 grants the MI Contributor on
    each `<isvSlug>-scu-rg` at create time (least-privilege).

.PARAMETER SubscriptionId
    Target subscription. Defaults to phases.2_data_lake_onboarding.subscriptionId
    or `az account show`.

.PARAMETER AutomationResourceGroup
    RG to hold the automation. Default 'scu-automation-rg'. Created if missing.

.PARAMETER Location
    Region for the Logic App. Default 'eastus2'.

.PARAMETER AcsDataLocation
    ACS data residency: 'United States' | 'Europe' | 'UK' | 'Australia'.
    Default 'United States'.

.PARAMETER NamePrefix
    Resource-name prefix (3-16 lowercase alphanumerics). Default 'scuauto'.

.PARAMETER ProgressJsonPath
    Default 'config/progress.json' (for subscription hydration only).

.PARAMETER AutomationConfigPath
    Where to write the automation record. Default 'config/scu-automation.json'.

.PARAMETER Confirm
    Required to actually deploy.

.OUTPUTS
    Hashtable mirroring config/scu-automation.json.

.NOTES
    Not live deploy-tested from the dev workstation — run once in-tenant.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)] [string]$SubscriptionId,
    [Parameter(Mandatory=$false)] [string]$AutomationResourceGroup = 'scu-automation-rg',
    [Parameter(Mandatory=$false)] [string]$Location = 'eastus2',
    [Parameter(Mandatory=$false)]
    [ValidateSet('United States','Europe','UK','Australia')]
    [string]$AcsDataLocation = 'United States',
    [Parameter(Mandatory=$false)]
    [ValidatePattern('^[a-z0-9]{3,16}$')]
    [string]$NamePrefix = 'scuauto',
    [Parameter(Mandatory=$false)] [string]$ProgressJsonPath = 'config/progress.json',
    [Parameter(Mandatory=$false)] [string]$AutomationConfigPath = 'config/scu-automation.json',
    [Parameter(Mandatory=$false)] [switch]$Confirm
)

$ErrorActionPreference = 'Stop'

function Write-Step($m) { Write-Host "`n=== $m ===" -ForegroundColor Cyan }
function Write-Ok  ($m) { Write-Host "✅ $m" -ForegroundColor Green }
function Write-Info($m) { Write-Host "   $m" }
function Write-Warn2($m){ Write-Host "⚠️  $m" -ForegroundColor Yellow }
function Write-Err2 ($m){ Write-Host "❌ $m" -ForegroundColor Red }

# -------- 1. Resolve subscription -------------------------------------------
$progress = $null
if (Test-Path $ProgressJsonPath) {
    try { $progress = Get-Content $ProgressJsonPath -Raw | ConvertFrom-Json } catch { $progress = $null }
}
if (-not $SubscriptionId) { $SubscriptionId = $progress.phases.'2_data_lake_onboarding'.subscriptionId }
if (-not $SubscriptionId) { $SubscriptionId = az account show --query id -o tsv }
if (-not $SubscriptionId) { throw "Could not resolve a subscription. Pass -SubscriptionId." }

az account set --subscription $SubscriptionId | Out-Null

Write-Step "SCU auto-delete engine — one-time setup"
Write-Info "Subscription:      $SubscriptionId"
Write-Info "Automation RG:     $AutomationResourceGroup"
Write-Info "Region:            $Location"
Write-Info "ACS data location: $AcsDataLocation"
Write-Info "Name prefix:       $NamePrefix"

# -------- 2. Role pre-flight ------------------------------------------------
# The Bicep creates a role assignment (MI -> ACS), so the deployer needs role-
# write rights. Owner or User Access Administrator at subscription scope.
$signedInId = az ad signed-in-user show --query id -o tsv 2>$null
$subScope = "/subscriptions/$SubscriptionId"
$rolesJson = az role assignment list --assignee $signedInId --scope $subScope --include-inherited -o json 2>$null
$roles = @()
if ($rolesJson) { try { $roles = ($rolesJson | ConvertFrom-Json).roleDefinitionName } catch {} }
$canAssign = ($roles -contains 'Owner') -or ($roles -contains 'User Access Administrator')
if (-not $canAssign) {
    Write-Warn2 "You need 'Owner' or 'User Access Administrator' at subscription scope to create the MI->ACS role assignment in this template."
    Write-Info  "Grant it, then re-run. CLI:"
    Write-Host  "  az role assignment create --assignee-object-id $signedInId --assignee-principal-type User --role 'User Access Administrator' --scope $subScope" -ForegroundColor Gray
    exit 3
}

if (-not $Confirm) {
    Write-Warn2 "This deploys a Logic App + Azure Communication Services (one-time, ~`$0.05/month at ~300 sessions)."
    Write-Host  "Re-run with -Confirm to deploy:" -ForegroundColor Yellow
    Write-Host  "  ./scripts/Setup-ScuAutoDelete.ps1 -Confirm" -ForegroundColor Gray
    exit 4
}

# -------- 3. Ensure automation RG + deploy Bicep ----------------------------
$rgExists = az group exists --name $AutomationResourceGroup --subscription $SubscriptionId
if ($rgExists -ne 'true') {
    Write-Info "Creating automation RG '$AutomationResourceGroup' in '$Location'..."
    az group create --name $AutomationResourceGroup --location $Location --subscription $SubscriptionId --output none
    Write-Ok "Automation RG created."
}

$bicepPath = Join-Path (Split-Path $PSScriptRoot -Parent) 'infra/scu-autodelete/scu-autodelete.bicep'
if (-not (Test-Path $bicepPath)) { throw "Bicep template not found at $bicepPath" }

$deployName = "scu-autodelete-$((Get-Date).ToString('yyyyMMddHHmmss'))"
Write-Info "Deploying '$deployName' (this can take a few minutes — ACS managed domain provisioning is slow)..."
# Redirect az's stderr (WARNING lines, bicep-build notices) to a temp file so it never
# pollutes the JSON on stdout — otherwise ConvertFrom-Json chokes on a leading "WARNING:".
$errFile = [System.IO.Path]::GetTempFileName()
try {
    $deployOut = az deployment group create `
        --name $deployName `
        --resource-group $AutomationResourceGroup `
        --subscription $SubscriptionId `
        --template-file $bicepPath `
        --parameters location=$Location namePrefix=$NamePrefix "acsDataLocation=$AcsDataLocation" `
        --query properties.outputs `
        --output json 2>$errFile
    $deployErr = if (Test-Path $errFile) { (Get-Content $errFile -Raw) } else { '' }
} finally {
    Remove-Item $errFile -ErrorAction SilentlyContinue
}
if ($LASTEXITCODE -ne 0) {
    Write-Err2 "Deployment failed."
    if ($deployErr)  { Write-Host $deployErr -ForegroundColor Red }
    if ($deployOut)  { Write-Host ($deployOut | Out-String) -ForegroundColor Red }
    throw "Setup deployment failed."
}
$deployOutStr = ($deployOut | Out-String).Trim()
if ([string]::IsNullOrWhiteSpace($deployOutStr)) {
    throw "Deployment reported success but returned no outputs. az stderr was:`n$deployErr"
}
$outputs = $deployOutStr | ConvertFrom-Json
Write-Ok "Deployment succeeded."

# -------- 4. Persist automation record --------------------------------------
$record = [ordered]@{
    subscriptionId = $SubscriptionId
    automationResourceGroup = $AutomationResourceGroup
    region         = $outputs.region.value
    logicAppId     = $outputs.workflowId.value
    workflowName   = $outputs.workflowName.value
    miPrincipalId  = $outputs.miPrincipalId.value
    acsEndpoint    = $outputs.acsEndpoint.value
    senderAddress  = $outputs.senderAddress.value
    deployedAt     = (Get-Date).ToUniversalTime().ToString('o')
}
$cfgDir = Split-Path $AutomationConfigPath -Parent
if ($cfgDir -and -not (Test-Path $cfgDir)) { New-Item -ItemType Directory -Force -Path $cfgDir | Out-Null }
$record | ConvertTo-Json -Depth 8 | Set-Content $AutomationConfigPath -Encoding UTF8
Write-Ok "Wrote automation record to $AutomationConfigPath"

Write-Host ""
Write-Host "Setup complete. Server-side SCU auto-delete is now available." -ForegroundColor Green
Write-Info "Logic App:      $($record.logicAppId)"
Write-Info "MI principal:   $($record.miPrincipalId)"
Write-Info "ACS sender:     $($record.senderAddress)"
Write-Host ""
Write-Host "From now on, `create scu` can choose server-side teardown:" -ForegroundColor Yellow
Write-Host "  ./scripts/Ensure-SccCapacity.ps1 -Confirm -DeletionMode server -NotifyEmail you@example.com" -ForegroundColor Gray

return $record
