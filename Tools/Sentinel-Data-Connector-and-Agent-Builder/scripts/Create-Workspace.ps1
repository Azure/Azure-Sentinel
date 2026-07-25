<#
.SYNOPSIS
    Creates a Log Analytics workspace and attaches Microsoft Sentinel.
.DESCRIPTION
    Provisions a new LA workspace in the recommended region (East US 2 default),
    then enables Microsoft Sentinel (SecurityInsights) solution on it.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory=$true)]
    [string]$WorkspaceName,

    [Parameter(Mandatory=$false)]
    [string]$Location = "eastus2",

    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId
)

$ErrorActionPreference = "Stop"

if ($SubscriptionId) {
    az account set --subscription $SubscriptionId
}

# Supported data lake regions
$supportedRegions = @(
    "centralus", "eastus", "eastus2", "southcentralus", "westus2",
    "canadacentral", "northeurope", "westeurope", "francecentral",
    "italynorth", "switzerlandnorth", "uksouth", "southeastasia",
    "centralindia", "israelcentral", "japaneast", "australiaeast"
)

if ($Location -notin $supportedRegions) {
    Write-Host "❌ Region '$Location' is not supported for Sentinel Data Lake."
    Write-Host "Supported regions: $($supportedRegions -join ', ')"
    exit 1
}

if ($Location -in @("eastus", "westus2", "westeurope")) {
    Write-Host "⚠️  Region '$Location' is capacity-restricted. May take additional time."
    Write-Host "   For East US, submit AppAssure Intake form: https://aka.ms/intakeform"
}

# 1. Create Resource Group
Write-Host "`n=== Creating Resource Group ===`n"
$rgExists = az group exists --name $ResourceGroupName
if ($rgExists -eq "true") {
    Write-Host "✅ Resource group '$ResourceGroupName' already exists."
} else {
    az group create --name $ResourceGroupName --location $Location --output none
    Write-Host "✅ Resource group '$ResourceGroupName' created in $Location."
}

# 2. Create Log Analytics Workspace
Write-Host "`n=== Creating Log Analytics Workspace ===`n"
$wsExists = az monitor log-analytics workspace show `
    --resource-group $ResourceGroupName `
    --workspace-name $WorkspaceName `
    --output json 2>$null

if ($wsExists) {
    $ws = $wsExists | ConvertFrom-Json
    Write-Host "✅ Workspace '$WorkspaceName' already exists."
} else {
    az monitor log-analytics workspace create `
        --resource-group $ResourceGroupName `
        --workspace-name $WorkspaceName `
        --location $Location `
        --retention-time 90 `
        --output none
    Write-Host "✅ Workspace '$WorkspaceName' created."
    $ws = az monitor log-analytics workspace show `
        --resource-group $ResourceGroupName `
        --workspace-name $WorkspaceName `
        --output json | ConvertFrom-Json
}

$workspaceId = $ws.customerId
$resourceId = $ws.id

Write-Host "   Workspace ID: $workspaceId"
Write-Host "   Resource ID: $resourceId"

# 3. Enable Microsoft Sentinel
Write-Host "`n=== Enabling Microsoft Sentinel ===`n"
$sentinelCheck = az sentinel onboarding-state show `
    --resource-group $ResourceGroupName `
    --workspace-name $WorkspaceName `
    --name "default" `
    --output json 2>$null

if ($sentinelCheck) {
    Write-Host "✅ Microsoft Sentinel already enabled."
} else {
    az sentinel onboarding-state create `
        --resource-group $ResourceGroupName `
        --workspace-name $WorkspaceName `
        --name "default" `
        --output none
    Write-Host "✅ Microsoft Sentinel enabled on workspace."
}

# 4. Output workspace config
Write-Host "`n=== Workspace Configuration ===`n"
Write-Host "Resource Group: $ResourceGroupName"
Write-Host "Workspace Name: $WorkspaceName"
Write-Host "Location: $Location"
Write-Host "Workspace ID: $workspaceId"
Write-Host "Resource ID: $resourceId"
Write-Host "`nNext step: Run Setup-DataIngestion.ps1 to create custom tables and DCR.`n"

# Return workspace info for pipeline use
return @{
    ResourceGroup = $ResourceGroupName
    WorkspaceName = $WorkspaceName
    WorkspaceId = $workspaceId
    ResourceId = $resourceId
    Location = $Location
}
