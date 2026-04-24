<#
.SYNOPSIS
    Exports, sanitises, and optionally deploys Microsoft Sentinel playbooks as portable ARM templates.

.DESCRIPTION
    One script to rule them all, one script to find them,
    one script to bring them all, and in the SOC bind them.

    Invoke-SentinelPlaybookManager discovers Logic App playbooks and their API connections
    in a source resource group, exports each as a sanitised ARM template with full
    parameterisation, and optionally deploys them to any target environment.

    Sanitisation includes:
    - Replaces all hardcoded subscription, resource group, location, and tenant references
    - Normalises managed API connector names (lowercase, strips designer suffixes)
    - Configures managed identity authentication only on supported APIs
    - Deduplicates connection resources and workflow connection parameters
    - Fixes ARM expression escaping (STIX patterns, encodeURIComponent, semicolons)
    - Enforces Azure connection name length limits (80 characters)
    - Sanitises PlaybookName for valid ARM resource name characters
    - Parameterises tag values for cross-environment portability
    - Auto-detects and wires workflow-level parameters with ARM passthrough
    - Populates ARM template metadata (title, trigger type, entities, timestamps)
    - Upgrades resource API versions to latest stable releases
    - Generates environment.parameters.json for customer configuration
    - Integrated deployment with -Deploy flag

    Requires PowerShell 7+ and the Az PowerShell module.
    Optionally uses Microsoft.PowerShell.ConsoleGuiTools for interactive playbook selection.

.PARAMETER ResourceGroupName
    Source Azure resource group containing the Sentinel playbooks to export.

.PARAMETER OutputPath
    Directory to write the exported templates. Created if it doesn't exist.
    Defaults to ./Exported relative to the script location.

.PARAMETER Interactive
    When set, presents a GUI grid view for selecting which playbooks to export.
    Requires the Microsoft.PowerShell.ConsoleGuiTools module (install with:
    Install-Module Microsoft.PowerShell.ConsoleGuiTools -Scope CurrentUser).
    If the module is not installed, falls back to exporting all playbooks.

.PARAMETER PlaybookFilter
    Wildcard filter applied to playbook names. Ignored when -Interactive is used.
    Defaults to '*' (all playbooks).

.PARAMETER SkipParameterFiles
    When set, only exports azuredeploy.json templates without generating
    azuredeploy.parameters.json or environment.parameters.json files.
    Useful when exporting templates for a gallery or repository where
    parameter files will be generated separately at deploy time.

.PARAMETER Deploy
    When set, deploys the exported templates to -TargetResourceGroupName after export.
    Requires -TargetResourceGroupName and optionally -EnvironmentFile.

.PARAMETER TargetResourceGroupName
    Target Azure resource group for deployment. Required when -Deploy is used.

.PARAMETER EnvironmentFile
    Path to an environment.parameters.json with values for the target environment.
    When omitted with -Deploy, uses the auto-generated file from the export.

.EXAMPLE
    .\Invoke-SentinelPlaybookManager.ps1 -ResourceGroupName "rg-prd-sentinel"
    Exports all playbooks from the resource group.

.EXAMPLE
    .\Invoke-SentinelPlaybookManager.ps1 -ResourceGroupName "rg-prd-sentinel" -Interactive
    Opens a console grid view to interactively pick which playbooks to export.

.EXAMPLE
    .\Invoke-SentinelPlaybookManager.ps1 -ResourceGroupName "rg-prd-sentinel" -PlaybookFilter "CSOC-*"
    Exports only playbooks matching the CSOC-* wildcard pattern.

.EXAMPLE
    .\Invoke-SentinelPlaybookManager.ps1 -ResourceGroupName "rg-source" -Deploy -TargetResourceGroupName "rg-target" -EnvironmentFile "./env.json"
    Exports from source, sanitises, and deploys to a different resource group in one command.

.EXAMPLE
    .\Invoke-SentinelPlaybookManager.ps1 -ResourceGroupName "rg-source" -PlaybookFilter "Incident-*" -Deploy -TargetResourceGroupName "rg-target"
    Exports filtered playbooks and deploys using the auto-generated environment file.

.EXAMPLE
    .\Invoke-SentinelPlaybookManager.ps1 -ResourceGroupName "rg-prd-sentinel" -SkipParameterFiles
    Exports only the ARM templates without parameter files (for gallery/repo publishing).

.NOTES
    Version : 0.1.1
    Author  : Toby G
    Date    : April 2026

.LINK
    https://learn.microsoft.com/en-us/azure/sentinel/automate-responses-with-playbooks
#>

#Requires -Version 7.0
#Requires -Modules Az.Accounts, Az.Resources, Az.LogicApp

[CmdletBinding(DefaultParameterSetName = 'Filter')]
param(
    [Parameter(Mandatory, Position = 0)]
    [string]$ResourceGroupName,

    [Parameter()]
    [string]$OutputPath = (Join-Path $PSScriptRoot '..' 'Playbooks' 'Exported'),

    [Parameter(ParameterSetName = 'Interactive')]
    [switch]$Interactive,

    [Parameter(ParameterSetName = 'Filter')]
    [string]$PlaybookFilter = '*',

    [Parameter()]
    [switch]$SkipParameterFiles,

    [Parameter()]
    [switch]$Deploy,

    [Parameter()]
    [string]$TargetResourceGroupName,

    [Parameter()]
    [string]$EnvironmentFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region ── Configuration ──────────────────────────────────────────────────────────

# Latest stable ARM API versions (verified against Azure resource providers April 2026)
$Script:LogicAppApiVersion  = '2019-05-01'
$Script:ConnectionApiVersion = '2016-06-01'

# Managed APIs that support managed identity (parameterValueType: Alternative)
$Script:MISupportedApis = @('azuresentinel', 'keyvault')

# Tag keys to parameterise — maps source tag name to ARM parameter name
$Script:TagParamMap = [ordered]@{
    'Cost Centre'  = 'TagCostCentre'
    'CostCentre'   = 'TagCostCentre'
    'Owner'        = 'TagOwner'
    'CostOwner'    = 'TagCostOwner'
    'ServiceOwner' = 'TagServiceOwner'
    'ServiceName'  = 'TagServiceName'
    'BusinessUnit' = 'TagBusinessUnit'
    'Department'   = 'TagDepartment'
}

# Known workflow-level parameters that need ARM-to-Logic-Apps passthrough
$Script:WorkflowLevelParams = @(
    'NotificationEmailAddress', 'SenderEmailAddress', 'TenantId',
    'ClientId', 'TeamsChannelId', 'SensitivityLabelId', 'KeyVaultSecretName'
)

# Entity path-to-type mapping for metadata population
$Script:EntityPathMap = @{
    '/entities/ip'       = 'IP'
    '/entities/url'      = 'URL'
    '/entities/account'  = 'Account'
    '/entities/host'     = 'Host'
    '/entities/filehash' = 'FileHash'
    '/entities/file'     = 'File'
    '/entities/process'  = 'Process'
    '/entities/dns'      = 'DNS'
    '/entities/mailbox'  = 'Mailbox'
}

#endregion

#region ── Prerequisites Check ────────────────────────────────────────────────────

Write-Host ""
Write-Host "     S E N T I N E L   P L A Y B O O K" -ForegroundColor Yellow
Write-Host "             M A N A G E R" -ForegroundColor Yellow
Write-Host ""
Write-Host "       Three scripts for the Elven-devs" -ForegroundColor DarkGray
Write-Host "         under one cloud," -ForegroundColor DarkGray
Write-Host "       Seven for the SOC-lords in their" -ForegroundColor DarkGray
Write-Host "         halls of logs," -ForegroundColor DarkGray
Write-Host "       Nine for the Mortal analysts" -ForegroundColor DarkGray
Write-Host "         doomed to on-call," -ForegroundColor DarkGray
Write-Host ""
Write-Host "       One Script to rule them all," -ForegroundColor Yellow
Write-Host "       One Script to find them," -ForegroundColor Yellow
Write-Host "       One Script to bring them all," -ForegroundColor Yellow
Write-Host "       And in the SOC bind them." -ForegroundColor Yellow
Write-Host ""
Write-Host "  v0.1.1 | Author: Toby G | April 2026" -ForegroundColor DarkGray
Write-Host ""

# Verify Azure connection
try {
    $ctx = Get-AzContext
    if (-not $ctx.Subscription) { throw 'No active subscription' }
    Write-Host "  Subscription : $($ctx.Subscription.Name)" -ForegroundColor White
    Write-Host "  Tenant       : $($ctx.Tenant.Id)" -ForegroundColor White
}
catch {
    Write-Host "  ERROR: Not connected to Azure. Run Connect-AzAccount first." -ForegroundColor Red
    exit 1
}

# Verify resource group
try {
    $rg = Get-AzResourceGroup -Name $ResourceGroupName -ErrorAction Stop
    Write-Host "  Source RG    : $($rg.ResourceGroupName) ($($rg.Location))" -ForegroundColor White
}
catch {
    Write-Host "  ERROR: Resource group '$ResourceGroupName' not found." -ForegroundColor Red
    exit 1
}

# Check for GUI tools if -Interactive requested
if ($Interactive) {
    $guiModule = Get-Module -ListAvailable -Name 'Microsoft.PowerShell.ConsoleGuiTools'
    if (-not $guiModule) {
        Write-Host "  Microsoft.PowerShell.ConsoleGuiTools not found." -ForegroundColor Yellow
        Write-Host "  Install with: Install-Module Microsoft.PowerShell.ConsoleGuiTools -Scope CurrentUser" -ForegroundColor Yellow
        Write-Host "  Falling back to exporting all playbooks.`n" -ForegroundColor Yellow
        $Interactive = $false
    }
}

$subId    = $ctx.Subscription.Id
$tenantId = $ctx.Tenant.Id
$location = $rg.Location

#endregion

#region ── Discover & Select Playbooks ────────────────────────────────────────────

Write-Host "`n  Discovering playbooks..." -ForegroundColor Cyan

$allLogicApps = Get-AzResource -ResourceGroupName $ResourceGroupName `
    -ResourceType 'Microsoft.Logic/workflows' | Sort-Object Name

$allConnections = Get-AzResource -ResourceGroupName $ResourceGroupName `
    -ResourceType 'Microsoft.Web/connections'

Write-Host "  Found $($allLogicApps.Count) playbooks, $($allConnections.Count) API connections" -ForegroundColor White

if ($Interactive) {
    Import-Module Microsoft.PowerShell.ConsoleGuiTools -ErrorAction Stop
    $selectedPlaybooks = $allLogicApps |
        Select-Object Name, @{N='Tags';E={ ($_.Tags.Keys -join ', ') }} |
        Out-ConsoleGridView -Title 'Select playbooks to export (Space to select, Enter to confirm)' -OutputMode Multiple

    if (-not $selectedPlaybooks -or $selectedPlaybooks.Count -eq 0) {
        Write-Host "  No playbooks selected. Exiting." -ForegroundColor Yellow
        exit 0
    }

    $logicApps = $allLogicApps | Where-Object { $_.Name -in $selectedPlaybooks.Name }
    Write-Host "  Selected $($logicApps.Count) playbooks" -ForegroundColor Green
}
else {
    $logicApps = @($allLogicApps | Where-Object { $_.Name -like $PlaybookFilter })
    Write-Host "  Matched $($logicApps.Count) playbooks (filter: $PlaybookFilter)" -ForegroundColor White
}

if (-not (Test-Path $OutputPath)) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
}
$OutputPath = (Resolve-Path $OutputPath).Path

Write-Host "  Output       : $OutputPath" -ForegroundColor White
Write-Host "  API versions : Logic Apps $Script:LogicAppApiVersion | Connections $Script:ConnectionApiVersion" -ForegroundColor DarkGray
Write-Host ""

#endregion

#region ── Sanitisation Functions ─────────────────────────────────────────────────

function Get-PlaybookMetadata {
    param([PSCustomObject]$Template, [string]$PlaybookName)

    $logicApp = $Template.resources |
        Where-Object { $_.type -eq 'Microsoft.Logic/workflows' } | Select-Object -First 1
    if (-not $logicApp) { return $null }

    # Detect trigger type
    $triggerType = 'Incident'
    if ($logicApp.properties.definition.triggers) {
        $trigger = $logicApp.properties.definition.triggers.PSObject.Properties | Select-Object -First 1
        if ($trigger) {
            $path = ''
            if ($trigger.Value.PSObject.Properties['inputs'] -and
                $trigger.Value.inputs -and
                $trigger.Value.inputs.PSObject.Properties['path']) {
                $path = $trigger.Value.inputs.path
            }
            if ($path -match 'incident') { $triggerType = 'Incident' }
            elseif ($path -match 'alert') { $triggerType = 'Alert' }
            elseif ($trigger.Value.type -eq 'Recurrence') { $triggerType = 'Scheduled' }
            elseif ($trigger.Value.type -match 'Manual|Http') { $triggerType = 'Entity' }
        }
    }

    # Detect entities
    $entities = [System.Collections.Generic.List[string]]::new()
    if ($logicApp.properties.definition.actions) {
        foreach ($act in $logicApp.properties.definition.actions.PSObject.Properties) {
            $actPath = if ($act.Value.PSObject.Properties['inputs'] -and $act.Value.inputs -and $act.Value.inputs.PSObject.Properties['path']) { $act.Value.inputs.path } else { $null }
            if ($actPath) {
                foreach ($ep in $Script:EntityPathMap.GetEnumerator()) {
                    if ($actPath -eq $ep.Key -and $ep.Value -notin $entities) {
                        $entities.Add($ep.Value)
                    }
                }
            }
        }
    }

    # Detect connectors
    $connectors = [System.Collections.Generic.List[string]]::new()
    foreach ($res in $Template.resources) {
        if ($res.type -eq 'Microsoft.Web/connections' -and
            $res.properties.PSObject.Properties['api'] -and
            $res.properties.api.PSObject.Properties['id']) {
            $tag = ''
            if ($res.properties.api.id -match '/managedApis/([a-zA-Z]+)') { $tag = $Matches[1] }
            elseif ($res.properties.api.id -match '/customApis/([a-zA-Z]+)') { $tag = "custom:$($Matches[1])" }
            if ($tag -and $tag -notin $connectors) { $connectors.Add($tag) }
        }
    }

    # Extract from Sentinel tags
    $existingTags = if ($logicApp.PSObject.Properties['tags']) { $logicApp.tags } else { $null }
    $playbookType = if ($existingTags -and $existingTags.PSObject.Properties['PlaybookType']) { $existingTags.PlaybookType } else { '' }
    $templateName = if ($existingTags -and $existingTags.PSObject.Properties['hidden-SentinelTemplateName']) { $existingTags.'hidden-SentinelTemplateName' } else { $PlaybookName }
    $templateVersion = if ($existingTags -and $existingTags.PSObject.Properties['hidden-SentinelTemplateVersion']) { $existingTags.'hidden-SentinelTemplateVersion' } else { '1.0' }

    # Build prerequisites
    $prereqs = [System.Collections.Generic.List[string]]::new()
    $prereqs.Add('An active Azure subscription with Microsoft Sentinel enabled.')
    $customApis = $Template.resources | Where-Object { $_.type -eq 'Microsoft.Web/connections' -and $_.properties.api.id -match '/customApis/' }
    if ($customApis) {
        $names = ($customApis | ForEach-Object { if ($_.properties.api.id -match '/customApis/(\w+)') { $Matches[1] } }) -join ', '
        $prereqs.Add("Custom API connector(s) must be deployed first: $names.")
    }
    if ($Template.resources | Where-Object { $_.type -eq 'Microsoft.Web/connections' -and $_.properties.PSObject.Properties['parameterValueType'] -and $_.properties.parameterValueType -eq 'Alternative' }) {
        $prereqs.Add('A User Assigned Managed Identity with appropriate role assignments.')
    }

    return [PSCustomObject]@{
        title           = $PlaybookName
        description     = "Sentinel SOAR playbook: $PlaybookName. Trigger: $triggerType.$(if ($playbookType) {" Type: $playbookType."}) Connectors: $($connectors -join ', ')."
        prerequisites   = ($prereqs -join ' ')
        postDeployment  = @('Configure API connections and assign managed identity permissions after deployment.')
        lastUpdateTime  = (Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')
        entities        = @($entities)
        tags            = @($connectors | ForEach-Object { $_.ToLower() })
        triggerType     = $triggerType
        templateName    = $templateName
        templateVersion = $templateVersion
    }
}

function Invoke-TemplateSanitise {
    param([PSCustomObject]$Template, [string]$PlaybookName)

    $logicApp = $Template.resources |
        Where-Object { $_.type -eq 'Microsoft.Logic/workflows' } | Select-Object -First 1
    if (-not $logicApp) { return }

    # ── Metadata ──
    $meta = Get-PlaybookMetadata -Template $Template -PlaybookName $PlaybookName
    if ($meta) {
        $Template | Add-Member -NotePropertyName 'metadata' -NotePropertyValue ([PSCustomObject]@{
            title                          = $meta.title
            description                    = $meta.description
            prerequisites                  = $meta.prerequisites
            postDeployment                 = $meta.postDeployment
            prerequisitesDeployTemplateFile = ''
            lastUpdateTime                 = $meta.lastUpdateTime
            entities                       = $meta.entities
            tags                           = $meta.tags
            support                        = [PSCustomObject]@{ tier = 'community'; armtemplate = 'Generated by Invoke-SentinelPlaybookManager.ps1' }
            author                         = [PSCustomObject]@{ name = '' }
        }) -Force
    }

    # ── Parameters ──
    if (-not $Template.parameters) {
        $Template | Add-Member -NotePropertyName 'parameters' -NotePropertyValue ([PSCustomObject]@{}) -Force
    }

    $safeName = $PlaybookName -replace '[^A-Za-z0-9\-_.]', ''
    $Template.parameters | Add-Member -NotePropertyName 'PlaybookName' -NotePropertyValue ([PSCustomObject]@{
        defaultValue = $safeName
        type         = 'string'
        metadata     = [PSCustomObject]@{ description = 'Name for the Logic App playbook resource.' }
    }) -Force

    $logicApp.name = "[parameters('PlaybookName')]"

    # ── API Versions ──
    $logicApp.apiVersion = $Script:LogicAppApiVersion
    foreach ($res in $Template.resources) {
        if ($res.type -eq 'Microsoft.Web/connections') { $res.apiVersion = $Script:ConnectionApiVersion }
    }

    # ── Location ──
    foreach ($res in $Template.resources) {
        if ($res.PSObject.Properties['location']) { $res.location = "[resourceGroup().location]" }
    }

    # ── Tags ──
    if ($logicApp.PSObject.Properties['tags'] -and $logicApp.tags) {
        # Update Sentinel hidden tags
        if ($meta -and $logicApp.tags.PSObject.Properties['hidden-SentinelTemplateName']) {
            $logicApp.tags.'hidden-SentinelTemplateName' = $meta.templateName
        }
        # Parameterise known tag values
        foreach ($tp in @($logicApp.tags.PSObject.Properties)) {
            if ($tp.Name.StartsWith('hidden-')) { continue }
            $pName = $Script:TagParamMap[$tp.Name]
            if ($pName) {
                $tp.Value = "[parameters('$pName')]"
                if (-not $Template.parameters.PSObject.Properties[$pName]) {
                    $def = if ($pName -eq 'TagServiceName') { 'Sentinel' } else { '' }
                    $Template.parameters | Add-Member -NotePropertyName $pName -NotePropertyValue ([PSCustomObject]@{
                        type = 'string'; defaultValue = $def
                        metadata = [PSCustomObject]@{ description = "$($tp.Name) tag value." }
                    }) -Force
                }
            }
        }
    }

    # ── Connection Resources ──
    $connVars = [ordered]@{}
    $seenApis = @{}

    foreach ($res in @($Template.resources)) {
        if ($res.type -ne 'Microsoft.Web/connections') { continue }

        $apiName = ''; $isCustom = $false
        $apiId = if ($res.properties.PSObject.Properties['api'] -and $res.properties.api.PSObject.Properties['id']) { $res.properties.api.id } else { '' }
        if ($apiId -match '/managedApis/([a-zA-Z0-9]+)') { $apiName = $Matches[1].ToLower() }
        elseif ($apiId -match '/customApis/(\w+)') { $apiName = $Matches[1].ToLower(); $isCustom = $true }

        # Normalise API id
        if ($apiName -and -not $isCustom) {
            $res.properties.api.id = "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Web/locations/', resourceGroup().location, '/managedApis/$apiName')]"
        } elseif ($isCustom) {
            $res.properties.api.id = "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Web/locations/', resourceGroup().location, '/customApis/$($Matches[1])')]"
        }

        # MI handling
        if ($apiName -in $Script:MISupportedApis -and -not $isCustom) {
            $res.properties | Add-Member -NotePropertyName 'parameterValueType' -NotePropertyValue 'Alternative' -Force
        } elseif ($res.properties.PSObject.Properties['parameterValueType']) {
            $res.properties.PSObject.Properties.Remove('parameterValueType')
            if ($res.properties.PSObject.Properties['connectionProperties']) { $res.properties.PSObject.Properties.Remove('connectionProperties') }
        }

        if ($res.properties.PSObject.Properties['provisioningState']) { $res.properties.PSObject.Properties.Remove('provisioningState') }

        # Dedup by API
        $apiKey = if ($isCustom) { "custom_$apiName" } else { $apiName }
        if ($seenApis[$apiKey]) { $res | Add-Member -NotePropertyName '_remove' -NotePropertyValue $true -Force; continue }
        $seenApis[$apiKey] = $true

        # Variable
        $varBase = (Get-Culture).TextInfo.ToTitleCase($apiName)
        $varName = "${varBase}ConnectionName"
        $prefix = "$varBase-"
        if (($prefix.Length + $safeName.Length) -gt 80) { $prefix = $prefix.Substring(0, [Math]::Max(1, 80 - $safeName.Length)) }
        $connVars[$varName] = "[concat('$prefix', parameters('PlaybookName'))]"
        $res.name = "[variables('$varName')]"
        if ($res.properties.PSObject.Properties['displayName']) { $res.properties.displayName = "[variables('$varName')]" }
    }

    $Template.resources = @($Template.resources | Where-Object { -not ($_.PSObject.Properties['_remove'] -and $_._remove) })
    $Template.variables = [PSCustomObject]$connVars

    # ── $connections ──
    if ($logicApp.properties.parameters -and $logicApp.properties.parameters.PSObject.Properties['$connections']) {
        $conns = $logicApp.properties.parameters.'$connections'.value
        $seenKeys = @{}; $removeKeys = [System.Collections.Generic.List[string]]::new()

        foreach ($cp in @($conns.PSObject.Properties)) {
            $conn = $cp.Value; $apiName = ''; $isCustom = $false
            if ($conn.id -match '/managedApis/([a-zA-Z0-9]+)') {
                $apiName = $Matches[1].ToLower()
                $conn.id = "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Web/locations/', resourceGroup().location, '/managedApis/$apiName')]"
            } elseif ($conn.id -match '/customApis/(\w+)') {
                $apiName = $Matches[1].ToLower(); $isCustom = $true
                $conn.id = "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Web/locations/', resourceGroup().location, '/customApis/$($Matches[1])')]"
            }

            if ($apiName -notin $Script:MISupportedApis -and $conn.PSObject.Properties['connectionProperties']) { $conn.PSObject.Properties.Remove('connectionProperties') }
            if ($conn.PSObject.Properties['connectionProperties'] -and
                $conn.connectionProperties.PSObject.Properties['authentication'] -and
                $conn.connectionProperties.authentication.PSObject.Properties['identity']) {
                $conn.connectionProperties.authentication.identity = "[concat('/subscriptions/', parameters('SubscriptionId'), '/resourceGroups/', parameters('ResourceGroupName'), '/providers/Microsoft.ManagedIdentity/userAssignedIdentities/', parameters('ManagedIdentityName'))]"
                foreach ($pn in @('SubscriptionId','ResourceGroupName','ManagedIdentityName')) {
                    if (-not $Template.parameters.PSObject.Properties[$pn]) {
                        $pd = switch ($pn) {
                            'SubscriptionId'     { @{type='string';defaultValue='[subscription().subscriptionId]';metadata=@{description='Azure Subscription ID.'}} }
                            'ResourceGroupName'  { @{type='string';defaultValue='[resourceGroup().name]';metadata=@{description='Resource group name.'}} }
                            'ManagedIdentityName' { @{type='string';metadata=@{description='User Assigned Managed Identity name for SOAR playbooks.'}} }
                        }
                        $Template.parameters | Add-Member -NotePropertyName $pn -NotePropertyValue ([PSCustomObject]$pd) -Force
                    }
                }
            }

            $apiKey = if ($isCustom) { "custom_$apiName" } else { $apiName }
            if ($seenKeys[$apiKey]) { $removeKeys.Add($cp.Name); continue }
            $seenKeys[$apiKey] = $cp.Name

            $varBase = (Get-Culture).TextInfo.ToTitleCase($apiName); $varName = "${varBase}ConnectionName"
            if ($connVars.Contains($varName)) {
                $conn.connectionId = "[resourceId('Microsoft.Web/connections', variables('$varName'))]"
                $conn.connectionName = "[variables('$varName')]"
            }
        }
        foreach ($k in $removeKeys) { $conns.PSObject.Properties.Remove($k) }
    }

    # ── dependsOn ──
    $deps = @($Template.resources | Where-Object { $_.type -eq 'Microsoft.Web/connections' } | ForEach-Object {
        $n = $_.name; if ($n -match '^\[') { "[resourceId('Microsoft.Web/connections', $($n.TrimStart('[').TrimEnd(']')))]" } else { "[resourceId('Microsoft.Web/connections', '$n')]" }
    })
    $logicApp | Add-Member -NotePropertyName 'dependsOn' -NotePropertyValue $deps -Force

    # ── Workflow Parameters ──
    $defJson = $logicApp.properties.definition | ConvertTo-Json -Depth 100
    $wfParams = [System.Collections.Generic.HashSet[string]]::new()
    foreach ($m in [regex]::Matches($defJson, "@parameters\('([^']+)'\)")) { if ($m.Groups[1].Value -ne '$connections') { [void]$wfParams.Add($m.Groups[1].Value) } }
    foreach ($m in [regex]::Matches($defJson, "\[parameters\('($($Script:WorkflowLevelParams -join '|'))'\)\]")) { [void]$wfParams.Add($m.Groups[1].Value) }

    foreach ($wp in $wfParams) {
        if (-not $logicApp.properties.definition.parameters.PSObject.Properties[$wp]) {
            $logicApp.properties.definition.parameters | Add-Member -NotePropertyName $wp -NotePropertyValue ([PSCustomObject]@{defaultValue='';type='String'}) -Force
        }
        if (-not $logicApp.properties.parameters.PSObject.Properties[$wp]) {
            $logicApp.properties.parameters | Add-Member -NotePropertyName $wp -NotePropertyValue ([PSCustomObject]@{value="[parameters('$wp')]"}) -Force
        }
        if (-not $Template.parameters.PSObject.Properties[$wp]) {
            $Template.parameters | Add-Member -NotePropertyName $wp -NotePropertyValue ([PSCustomObject]@{type='string';metadata=[PSCustomObject]@{description="Value for $wp."}}) -Force
        }
    }
}

function Invoke-TextLevelFixes {
    param([string]$Json, [string]$SubId, [string]$TenantId, [string]$Location, [string]$RGName)

    # Hardcoded subscription IDs — in quotes and inside URL paths
    $Json = $Json.Replace("`"$SubId`"", '"[subscription().subscriptionId]"')
    $Json = $Json.Replace("/subscriptions/$SubId/", "/subscriptions/', subscription().subscriptionId, '/")

    # Hardcoded tenant IDs — in quotes and inside URL paths
    if ($TenantId) {
        $Json = $Json.Replace("`"$TenantId`"", '"[subscription().tenantId]"')
        $Json = $Json.Replace("/$TenantId/", "/', subscription().tenantId, '/")
    }

    # Hardcoded locations in API paths
    $Json = $Json.Replace("/locations/$Location/", "/locations/', resourceGroup().location, '/")

    # Hardcoded resource group names in paths
    $Json = $Json.Replace("/resourceGroups/$RGName/", "/resourceGroups/', resourceGroup().name, '/")

    $stix = 'ipv4-addr|ipv6-addr|domain-name|url|file|email-addr|network-traffic|windows-registry-key|process|software|user-account|mac-addr|autonomous-system|directory'
    $Json = [regex]::Replace($Json, "`"(\[(?:$stix)[^`"]*\])`"", '"[$1"')
    $Json = [regex]::Replace($Json, "encodeURIComponent\('@parameters\('([^']+)'\)'\)", "encodeURIComponent(parameters('`$1'))")
    $Json = [regex]::Replace($Json, "@\{encodeURIComponent\('\[([^\]]+)\]'\)\}", '@{encodeURIComponent($1)}')
    $Json = [regex]::Replace($Json, '"(@parameters\([^)]+\)[^"]*;[^"]*)"', { param($m); $v = [regex]::Replace($m.Groups[1].Value, '@parameters\(([^)]+)\)', '@{parameters($1)}'); "`"$v`"" })

    $Json = [regex]::Replace($Json, 'managedApis/([A-Za-z][A-Za-z0-9]*)-\d+', 'managedApis/$1')
    $Json = $Json.Replace('managedApis/Microsoftsentinel', 'managedApis/azuresentinel').Replace('managedApis/microsoftsentinel', 'managedApis/azuresentinel').Replace('managedApis/Mdcalert', 'managedApis/ascalert')
    $Json = [regex]::Replace($Json, 'managedApis/([A-Za-z][A-Za-z0-9]*)', { param($m); "managedApis/$($m.Groups[1].Value.ToLower())" })
    $Json = [regex]::Replace($Json, "variables\('([A-Za-z][A-Za-z0-9]*)-\d+(ConnectionName)'\)", "variables('`$1`$2')")

    return $Json
}

function New-ParameterFile {
    param([PSCustomObject]$Template)
    $values = [ordered]@{}
    foreach ($p in $Template.parameters.PSObject.Properties) {
        $d = if ($p.Value.PSObject.Properties['defaultValue']) { $p.Value.defaultValue } else { $null }
        if ($null -ne $d -and $d -is [string] -and $d -match '^\[.*\]$') { continue }
        $values[$p.Name] = [PSCustomObject]@{ value = $(if ($null -ne $d) { $d } else { '' }) }
    }
    return [PSCustomObject][ordered]@{
        '$schema'='https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#'
        'contentVersion'='1.0.0.0'
        'parameters'=[PSCustomObject]$values
    }
}

#endregion

#region ── Export Loop ─────────────────────────────────────────────────────────────

$results   = [System.Collections.Generic.List[object]]::new()
$allParams = [System.Collections.Generic.HashSet[string]]::new()
$total     = @($logicApps).Count
$current   = 0

foreach ($la in $logicApps) {
    $current++; $pbName = $la.Name
    Write-Host "  [$current/$total] $pbName..." -ForegroundColor Cyan -NoNewline

    try {
        $pbConns   = $allConnections | Where-Object { $_.Name -match [regex]::Escape($pbName) }
        $exportIds = @($la.ResourceId) + @($pbConns | ForEach-Object { $_.ResourceId })

        $tmpFile = Join-Path ([System.IO.Path]::GetTempPath()) "sentinel-export-$($pbName -replace '[^A-Za-z0-9]','-').json"
        Export-AzResourceGroup -ResourceGroupName $ResourceGroupName -Resource $exportIds `
            -SkipAllParameterization -Force -Path $tmpFile -ErrorAction Stop | Out-Null

        $rawJson = Get-Content $tmpFile -Raw
        if (-not $rawJson -or $rawJson.Length -lt 10) { throw 'Export produced empty template.' }
        Remove-Item $tmpFile -Force -ErrorAction SilentlyContinue

        $template = $rawJson | ConvertFrom-Json -Depth 100
        Invoke-TemplateSanitise -Template $template -PlaybookName $pbName
        $output = $template | ConvertTo-Json -Depth 100
        $output = Invoke-TextLevelFixes -Json $output -SubId $subId -TenantId $tenantId -Location $location -RGName $ResourceGroupName

        $final = $output | ConvertFrom-Json -Depth 100
        foreach ($p in $final.parameters.PSObject.Properties) { [void]$allParams.Add($p.Name) }

        $outDir = Join-Path $OutputPath $pbName
        if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir -Force | Out-Null }
        [System.IO.File]::WriteAllText((Join-Path $outDir 'azuredeploy.json'), $output, [System.Text.Encoding]::UTF8)
        if (-not $SkipParameterFiles) {
            [System.IO.File]::WriteAllText((Join-Path $outDir 'azuredeploy.parameters.json'), ((New-ParameterFile -Template $final) | ConvertTo-Json -Depth 100), [System.Text.Encoding]::UTF8)
        }

        $results.Add([PSCustomObject]@{ Name=$pbName; Status='OK'; Error='' })
        Write-Host " OK" -ForegroundColor Green
    }
    catch {
        $msg = $_.Exception.Message; if ($msg.Length -gt 200) { $msg = $msg.Substring(0,200) + '...' }
        $results.Add([PSCustomObject]@{ Name=$pbName; Status='FAILED'; Error=$msg })
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host "    $msg" -ForegroundColor DarkRed
    }
}

#endregion

#region ── Generate Environment File ──────────────────────────────────────────────

if (-not $SkipParameterFiles) {
    $envParams = [ordered]@{ '_readme' = 'Fill in the values below for your target environment, then use Deploy-Playbooks.ps1 to deploy.' }
    foreach ($pn in ($allParams | Sort-Object)) {
        if ($pn -in @('PlaybookName','SubscriptionId','ResourceGroupName','TenantId')) { continue }
        $envParams[$pn] = $(if ($pn -eq 'TagServiceName') { 'Sentinel' } else { '' })
        $envParams["_$pn"] = "Value for $pn."
    }
    [System.IO.File]::WriteAllText((Join-Path $OutputPath 'environment.parameters.json'), ([PSCustomObject]$envParams | ConvertTo-Json -Depth 5), [System.Text.Encoding]::UTF8)
}

#endregion

#region ── Summary ────────────────────────────────────────────────────────────────

$ok = @($results | Where-Object Status -eq 'OK').Count
$fail = @($results | Where-Object Status -eq 'FAILED').Count

Write-Host "`n=============================================" -ForegroundColor Cyan
Write-Host "  Export Complete" -ForegroundColor Cyan
Write-Host "  Success : $ok" -ForegroundColor Green
Write-Host "  Failed  : $fail" -ForegroundColor $(if ($fail -gt 0) {'Red'} else {'Green'})
Write-Host "  Total   : $total" -ForegroundColor White
Write-Host "  Output  : $OutputPath" -ForegroundColor White
Write-Host "=============================================`n" -ForegroundColor Cyan

if ($fail -gt 0) {
    Write-Host "  Failed:" -ForegroundColor Red
    $results | Where-Object Status -eq 'FAILED' | ForEach-Object { Write-Host "    $($_.Name): $($_.Error)" -ForegroundColor Red }
    Write-Host ""
}

if (-not $Deploy) {
    Write-Host "  Next steps:" -ForegroundColor Yellow
    Write-Host "    1. Fill in: $OutputPath/environment.parameters.json" -ForegroundColor White
    Write-Host "    2. Run again with -Deploy -TargetResourceGroupName <rg> to deploy.`n" -ForegroundColor DarkGray
}

#endregion

#region ── Deploy (optional) ──────────────────────────────────────────────────────

if ($Deploy) {
    if (-not $TargetResourceGroupName) {
        Write-Host "  ERROR: -TargetResourceGroupName is required when using -Deploy." -ForegroundColor Red
        exit 1
    }

    try {
        $targetRg = Get-AzResourceGroup -Name $TargetResourceGroupName -ErrorAction Stop
        Write-Host "  Target RG    : $($targetRg.ResourceGroupName) ($($targetRg.Location))" -ForegroundColor White
    }
    catch {
        Write-Host "  ERROR: Target resource group '$TargetResourceGroupName' not found." -ForegroundColor Red
        exit 1
    }

    # Load environment values
    $envFile = if ($EnvironmentFile) { $EnvironmentFile } else { Join-Path $OutputPath 'environment.parameters.json' }
    $envValues = @{}
    if (Test-Path $envFile) {
        $ej = Get-Content $envFile -Raw | ConvertFrom-Json
        foreach ($p in $ej.PSObject.Properties) {
            if (-not $p.Name.StartsWith('_') -and $p.Value -ne '' -and $null -ne $p.Value) {
                $envValues[$p.Name] = $p.Value
            }
        }
        Write-Host "  Env values   : $($envValues.Count) loaded from $(Split-Path $envFile -Leaf)" -ForegroundColor White
    }
    else {
        Write-Host "  WARNING: No environment file found. Parameters will use template defaults." -ForegroundColor Yellow
    }

    Write-Host ""

    $exportedDirs = Get-ChildItem $OutputPath -Directory |
        Where-Object { Test-Path (Join-Path $_.FullName 'azuredeploy.json') } | Sort-Object Name

    $deployResults = [System.Collections.Generic.List[object]]::new()
    $dTotal = @($exportedDirs).Count
    $dCurrent = 0

    foreach ($dir in $exportedDirs) {
        $dCurrent++
        $tplFile = Join-Path $dir.FullName 'azuredeploy.json'

        Write-Host "  [$dCurrent/$dTotal] Deploying: $($dir.Name)..." -ForegroundColor Cyan -NoNewline

        try {
            # Build parameter file from template + env values
            $tpl = Get-Content $tplFile -Raw | ConvertFrom-Json -Depth 100
            $pValues = [ordered]@{}
            foreach ($prop in $tpl.parameters.PSObject.Properties) {
                $d = if ($prop.Value.PSObject.Properties['defaultValue']) { $prop.Value.defaultValue } else { $null }
                if ($null -ne $d -and $d -is [string] -and $d -match '^\[.*\]$') { continue }
                if ($envValues.ContainsKey($prop.Name)) { $pValues[$prop.Name] = [PSCustomObject]@{ value = $envValues[$prop.Name] } }
                elseif ($null -ne $d) { $pValues[$prop.Name] = [PSCustomObject]@{ value = $d } }
                else { $pValues[$prop.Name] = [PSCustomObject]@{ value = '' } }
            }

            $pFile = Join-Path $dir.FullName 'azuredeploy.parameters.json'
            $pObj = [PSCustomObject][ordered]@{
                '$schema'='https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#'
                'contentVersion'='1.0.0.0'
                'parameters'=[PSCustomObject]$pValues
            }
            [System.IO.File]::WriteAllText($pFile, ($pObj | ConvertTo-Json -Depth 100), [System.Text.Encoding]::UTF8)

            $deployName = "$($dir.Name.Substring(0, [Math]::Min(50, $dir.Name.Length)))-$(Get-Date -Format 'HHmmss')" -replace '[^A-Za-z0-9\-_.]', ''

            New-AzResourceGroupDeployment -ResourceGroupName $TargetResourceGroupName `
                -TemplateFile $tplFile -TemplateParameterFile $pFile `
                -Name $deployName -ErrorAction Stop | Out-Null

            $deployResults.Add([PSCustomObject]@{ Name=$dir.Name; Status='OK'; Error='' })
            Write-Host " OK" -ForegroundColor Green
        }
        catch {
            $msg = $_.Exception.Message; if ($msg.Length -gt 200) { $msg = $msg.Substring(0,200) + '...' }
            $deployResults.Add([PSCustomObject]@{ Name=$dir.Name; Status='FAILED'; Error=$msg })
            Write-Host " FAILED" -ForegroundColor Red
            Write-Host "    $msg" -ForegroundColor DarkRed
        }
    }

    $dOk = @($deployResults | Where-Object Status -eq 'OK').Count
    $dFail = @($deployResults | Where-Object Status -eq 'FAILED').Count

    Write-Host "`n=============================================" -ForegroundColor Cyan
    Write-Host "  Deployment Results" -ForegroundColor Cyan
    Write-Host "  Success : $dOk" -ForegroundColor Green
    Write-Host "  Failed  : $dFail" -ForegroundColor $(if ($dFail -gt 0) {'Red'} else {'Green'})
    Write-Host "  Total   : $dTotal" -ForegroundColor White
    Write-Host "=============================================`n" -ForegroundColor Cyan

    if ($dFail -gt 0) {
        Write-Host "  Failed deployments:" -ForegroundColor Red
        $deployResults | Where-Object Status -eq 'FAILED' | ForEach-Object { Write-Host "    $($_.Name): $($_.Error)" -ForegroundColor Red }
    }
}

$results
