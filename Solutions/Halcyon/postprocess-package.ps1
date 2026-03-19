#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Post-processing script for the Halcyon Sentinel solution package.

.DESCRIPTION
    Run this after createSolutionV3.ps1 to:
      1. Promote the DCR and HalcyonEvents_CL table to top-level ARM resources so they
         update automatically on every solution upgrade via Content Hub, without requiring
         the user to re-click the "Deploy" button.

    Use -SkipInfraDeployment to omit the DCE/DCR nested deployment (table is still
    promoted). Useful for testing whether the Deploy button is greyed out after upgrade.

    The DCR and DCE are wrapped in a Microsoft.Resources/deployments nested deployment
    because ARM does not allow reference() in top-level resource names. The nested
    deployment receives the workspace customerId as a plain parameter so the inner
    template can name the resources correctly.

    The "Deploy" button remains necessary for first-time setup because it handles:
      - Entra app registration creation
      - Monitoring Metrics Publisher role assignment on the DCR
      - Push dataConnector resource creation (links Entra app + DCR)

.PARAMETER SolutionPath
    Path to the Halcyon solution directory. Defaults to the directory containing this script.

.EXAMPLE
    ./postprocess-package.ps1
    ./postprocess-package.ps1 -SolutionPath /path/to/Solutions/Halcyon
#>
param(
    [string]$SolutionPath = $PSScriptRoot,
    [switch]$SkipInfraDeployment
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$mainTemplatePath = Join-Path $SolutionPath "Package/mainTemplate.json"

if (-not (Test-Path $mainTemplatePath)) {
    Write-Error "mainTemplate.json not found at: $mainTemplatePath"
    exit 1
}

Write-Host "Reading $mainTemplatePath ..."
$templateRaw = Get-Content -Raw $mainTemplatePath
$template = $templateRaw | ConvertFrom-Json

# ── Locate the connectorDefinition contentTemplate ─────────────────────────
$connectorTemplate = $template.resources | Where-Object {
    $_.type -eq "Microsoft.OperationalInsights/workspaces/providers/contentTemplates" -and
    $_.properties.contentKind -eq "DataConnector"
} | Select-Object -First 1

if ($null -eq $connectorTemplate) {
    Write-Error "Could not find DataConnector contentTemplate in mainTemplate.json"
    exit 1
}

$nestedResources = $connectorTemplate.properties.mainTemplate.resources

if (-not $SkipInfraDeployment) {
    # ── Locate nested DCR (source for top-level deployment) ─────────────────────
    $nestedDcr = $nestedResources | Where-Object {
        $_.type -eq "Microsoft.Insights/dataCollectionRules"
    } | Select-Object -First 1

    if ($null -eq $nestedDcr) {
        Write-Error "Could not find Microsoft.Insights/dataCollectionRules in nested mainTemplate"
        exit 1
    }

    # ── Extract DCR properties for the top-level deployment ─────────────────────
    $dcrInner = $nestedDcr | ConvertTo-Json -Depth 50 | ConvertFrom-Json

    # Set name using parameters (no reference()) — ARM allows parameters() in resource names
    $dcrInner.name = "[concat('Microsoft-Sentinel-HalcyonDCR-', substring(parameters('workspaceCustomerId'), 0, 12))]"
    $dcrInner.location = "[parameters('workspaceLocation')]"

    # Fix dataCollectionEndpointId for the inner (nested deployment) context
    $dcrInner.properties.dataCollectionEndpointId = "[concat('/subscriptions/',parameters('subscription'),'/resourceGroups/',parameters('resourceGroupName'),'/providers/Microsoft.Insights/dataCollectionEndpoints/ASI-', parameters('workspaceCustomerId'))]"

    # Fix workspaceResourceId — inner template has its own parameters
    $dcrInner.properties.destinations.logAnalytics | ForEach-Object {
        $_.workspaceResourceId = "[parameters('workspaceResourceId')]"
    }

    # Remove kind — "[variables('blanks')]" (empty string) fails top-level ARM validation
    if ($dcrInner.PSObject.Properties['kind']) {
        $dcrInner.PSObject.Properties.Remove('kind')
    }

    # Add dependsOn DCE within inner template
    $dcrInnerDependsOn = @(
        "[resourceId('Microsoft.Insights/dataCollectionEndpoints', concat('ASI-', parameters('workspaceCustomerId')))]"
    )
    if ($null -eq $dcrInner.PSObject.Properties['dependsOn']) {
        $dcrInner | Add-Member -MemberType NoteProperty -Name 'dependsOn' -Value $dcrInnerDependsOn
    } else {
        $dcrInner.dependsOn = $dcrInnerDependsOn
    }

    Write-Host "DCR inner resource ready"

    # ── Build the nested deployment containing DCE + DCR ────────────────────────
    # reference() is not allowed in top-level resource names, so we pass the workspace
    # customerId via properties.parameters (where reference() IS allowed) and use it
    # as a plain parameters() call inside the inner template.
    $dceInner = [PSCustomObject]@{
        type       = "Microsoft.Insights/dataCollectionEndpoints"
        apiVersion = "2022-06-01"
        name       = "[concat('ASI-', parameters('workspaceCustomerId'))]"
        location   = "[parameters('workspaceLocation')]"
        properties = [PSCustomObject]@{}
    }

    $innerTemplate = [PSCustomObject]@{
        '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#"
        contentVersion = "1.0.0.0"
        parameters     = [PSCustomObject]@{
            workspaceCustomerId = [PSCustomObject]@{ type = "string" }
            workspaceLocation   = [PSCustomObject]@{ type = "string" }
            workspaceResourceId = [PSCustomObject]@{ type = "string" }
            subscription        = [PSCustomObject]@{ type = "string" }
            resourceGroupName   = [PSCustomObject]@{ type = "string" }
        }
        resources = @($dceInner, $dcrInner)
    }

    $infraDeployment = [PSCustomObject]@{
        type       = "Microsoft.Resources/deployments"
        apiVersion = "2022-09-01"
        name       = "HalcyonInfrastructureDeployment"
        dependsOn  = @(
            "[resourceId('Microsoft.OperationalInsights/workspaces/tables', parameters('workspace'), 'HalcyonEvents_CL')]"
        )
        properties = [PSCustomObject]@{
            mode = "Incremental"
            expressionEvaluationOptions = [PSCustomObject]@{ scope = "inner" }
            parameters = [PSCustomObject]@{
                workspaceCustomerId = [PSCustomObject]@{
                    value = "[reference(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), '2022-10-01').customerId]"
                }
                workspaceLocation = [PSCustomObject]@{
                    value = "[parameters('workspace-location')]"
                }
                workspaceResourceId = [PSCustomObject]@{
                    value = "[resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace'))]"
                }
                subscription = [PSCustomObject]@{
                    value = "[parameters('subscription')]"
                }
                resourceGroupName = [PSCustomObject]@{
                    value = "[parameters('resourceGroupName')]"
                }
            }
            template = $innerTemplate
        }
    }

    Write-Host "Built HalcyonInfrastructureDeployment (nested deployment wrapping DCE + DCR)"
}

# ── Extract table resource(s) ────────────────────────────────────────────────
$tableResources = @($nestedResources | Where-Object {
    $_.type -eq "Microsoft.OperationalInsights/workspaces/tables"
})
Write-Host "Found $($tableResources.Count) table resource(s)"

$tableTopLevel = @()
foreach ($table in $tableResources) {
    $t = $table | ConvertTo-Json -Depth 50 | ConvertFrom-Json
    $originalName = $t.name
    if ($originalName -notmatch '^\[') {
        $t.name = "[concat(parameters('workspace'), '/$originalName')]"
        Write-Host "Fixed table name: $originalName -> $($t.name)"
    }
    if ($t.PSObject.Properties['kind'] -and $null -eq $t.kind) {
        $t.PSObject.Properties.Remove('kind')
    }
    $tableTopLevel += $t
}

# ── Remove any stale top-level DCE / DCR / infra deployment resources ────────
# createSolutionV3 does not add these, but a previous postprocess run might have.
$resourcesToRemove = @(
    "Microsoft.Insights/dataCollectionEndpoints",
    "Microsoft.Insights/dataCollectionRules"
)
$template.resources = @($template.resources | Where-Object {
    $_.type -notin $resourcesToRemove -and
    -not ($_.type -eq "Microsoft.Resources/deployments" -and $_.name -eq "HalcyonInfrastructureDeployment")
})

# ── Add infrastructure deployment (unless skipped) ───────────────────────────
if (-not $SkipInfraDeployment) {
    $template.resources += $infraDeployment
    Write-Host "Added HalcyonInfrastructureDeployment to top-level resources"
} else {
    Write-Host "Skipping HalcyonInfrastructureDeployment (-SkipInfraDeployment)"
}

# ── Add table(s) at top level ─────────────────────────────────────────────────
$alreadyHasTables = $template.resources | Where-Object {
    $_.type -eq "Microsoft.OperationalInsights/workspaces/tables"
}

if ($alreadyHasTables) {
    Write-Host "Table(s) already present at top level — skipping"
} else {
    foreach ($t in $tableTopLevel) {
        $template.resources += $t
        Write-Host "Added table '$($t.name)' to top-level resources"
    }
}

# ── Save mainTemplate.json ───────────────────────────────────────────────────
Write-Host "Writing updated mainTemplate.json ..."
$template | ConvertTo-Json -Depth 100 | Set-Content -Path $mainTemplatePath -Encoding UTF8
Write-Host "Saved."

# ── Update zip ───────────────────────────────────────────────────────────────
$zipPath = Get-ChildItem (Join-Path $SolutionPath "Package") -Filter "*.zip" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1 -ExpandProperty FullName

if ($zipPath) {
    Write-Host "Updating zip: $zipPath ..."
    Compress-Archive -Path $mainTemplatePath -DestinationPath $zipPath -Update
    Write-Host "Zip updated."
} else {
    Write-Warning "No zip file found in Package/ — skipping zip update"
}

Write-Host ""
Write-Host "Done."
if ($SkipInfraDeployment) {
    Write-Host "  - HalcyonInfrastructureDeployment SKIPPED (-SkipInfraDeployment)"
} else {
    Write-Host "  - HalcyonInfrastructureDeployment added (DCE + DCR auto-update on upgrade)"
}
Write-Host "  - HalcyonEvents_CL table added as top-level resource (schema auto-updates)"
