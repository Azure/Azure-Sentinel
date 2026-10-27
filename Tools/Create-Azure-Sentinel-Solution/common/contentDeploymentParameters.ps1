$script:contentDeploymentContract = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'contentDeploymentParameters.json') -Raw | ConvertFrom-Json
$script:solutionResourceKinds = [System.Collections.Generic.Dictionary[object,string]]::new([System.Collections.Generic.ReferenceEqualityComparer]::Instance)
$script:solutionRequiredResources = [System.Collections.Generic.HashSet[object]]::new([System.Collections.Generic.ReferenceEqualityComparer]::Instance)

function Register-SolutionRequiredResources {
    param([object[]]$Resources)
    foreach ($resource in $Resources) {
        [void]$script:solutionRequiredResources.Add($resource)
    }
}

function Register-SolutionResourceKind {
    param([object[]]$Resources, [string]$Kind)
    foreach ($resource in $Resources) {
        $script:solutionResourceKinds[$resource] = $Kind
    }
}

function Get-SolutionResourceSelection {
    param([psobject]$Resource)

    if ($script:solutionRequiredResources.Contains($Resource)) { return $null }
    $kind = [string]$Resource.properties.contentKind
    if (-not $kind -and $Resource.type -eq 'Microsoft.OperationalInsights/workspaces/providers/metadata') {
        $kind = [string]$Resource.properties.kind
    }
    if (-not $kind) {
        $kind = $script:solutionResourceKinds[$Resource]
    }
    if (-not $kind) {
        $kind = switch ($Resource.type) {
            'Microsoft.OperationalInsights/workspaces/providers/dataConnectors' { 'DataConnector' }
            'Microsoft.OperationalInsights/workspaces/providers/dataConnectorDefinitions' { 'DataConnector' }
            'Microsoft.OperationalInsights/workspaces/providers/alertRules' { 'AnalyticsRule' }
            'Microsoft.OperationalInsights/workspaces/providers/watchlists' { 'Watchlist' }
            'Microsoft.OperationalInsights/workspaces/summaryLogs' { 'SummaryRule' }
            'Microsoft.Insights/workbooks' { 'Workbook' }
        }
    }
    if ($kind) {
        foreach ($entry in $script:contentDeploymentContract.PSObject.Properties) {
            if ($kind -in $entry.Value.kinds) { return $entry.Name }
        }
        if ($kind -eq 'Solution' -and $Resource.type -in @(
            'Microsoft.OperationalInsights/workspaces/providers/contentPackages',
            'Microsoft.OperationalInsights/workspaces/providers/metadata'
        )) { return $null }
    }
    elseif ($Resource.type -eq 'Microsoft.Resources/deployments') {
        # Only the generated XDR install wrapper is classified by its typed inner resource.
        $inner = $Resource.properties.template
        $detection = $inner.resources.detectionRule
        if ($inner.languageVersion -eq '2.0' -and
            $inner.imports.MicrosoftSecurity.provider -eq 'MicrosoftSecurity' -and
            $detection.import -eq 'MicrosoftSecurity' -and
            $detection.type -like 'Microsoft.Security/detectionRules@*' -and
            @($inner.resources.PSObject.Properties).Count -eq 1) {
            return 'DeployCustomDetection'
        }
    }
    elseif ($Resource.type -eq 'Microsoft.OperationalInsights/workspaces' -and
        $null -ne $Resource.resources) {
        # The legacy query container is shared infrastructure; its children select independently.
        return $null
    }
    throw "Unclassified V3.1 content resource '$($Resource.name)' (type '$($Resource.type)', kind '$kind'). Add an explicit content-family mapping before packaging."
}

function Set-SolutionSelectionCondition {
    param([psobject]$Resource, [string]$Parameter)
    $selection = "parameters('$Parameter')"
    $condition = "[$selection]"
    if ($null -ne $Resource.condition -and
        ($Resource.condition -isnot [string] -or $Resource.condition -cne $condition)) {
        if ($Resource.condition -is [bool]) {
            $existing = ([string]$Resource.condition).ToLowerInvariant() + '()'
        }
        elseif ($Resource.condition -is [string] -and
            $Resource.condition.StartsWith('[') -and $Resource.condition.EndsWith(']') -and
            -not $Resource.condition.StartsWith('[[')) {
            $existing = $Resource.condition.Substring(1, $Resource.condition.Length - 2)
        }
        else {
            throw "Invalid existing ARM condition on '$($Resource.name)': $($Resource.condition)"
        }
        $condition = "[and($selection, $existing)]"
    }
    $Resource | Add-Member -NotePropertyName condition -NotePropertyValue $condition -Force
}

function Add-SolutionContentDeploymentParameters {
    param([psobject]$Template, [psobject]$UiDefinition)
    $used = [System.Collections.Generic.HashSet[string]]::new()
    function Set-ResourceSelection($Resources, [string]$ParentSelection) {
        foreach ($resource in $Resources) {
            $selection = if ($ParentSelection) { $ParentSelection } else { Get-SolutionResourceSelection -Resource $resource }
            if ($selection) {
                [void]$used.Add($selection)
                Set-SolutionSelectionCondition -Resource $resource -Parameter $selection
            }
            # ARM child resources share the outer scope; stored templates and deployment
            # templates do not. Never inject outer parameter references into their bodies.
            if ($null -ne $resource.resources) {
                Set-ResourceSelection -Resources $resource.resources -ParentSelection $selection
            }
        }
    }
    Set-ResourceSelection -Resources $Template.resources

    $elements = @()
    foreach ($entry in $script:contentDeploymentContract.PSObject.Properties) {
        if (-not $used.Contains($entry.Name)) { continue }
        if ($null -ne $Template.parameters.PSObject.Properties[$entry.Name]) {
            throw "V3.1 reserved selection parameter '$($entry.Name)' is already declared."
        }
        $Template.parameters | Add-Member -NotePropertyName $entry.Name -NotePropertyValue ([pscustomobject]@{
            type = 'bool'
            defaultValue = $entry.Value.defaultValue
            metadata = [pscustomobject]@{ description = $entry.Value.description }
        })
        $elements += [pscustomobject]@{
            name = $entry.Name
            type = 'Microsoft.Common.CheckBox'
            label = $entry.Name
            defaultValue = $entry.Value.defaultValue
            toolTip = $entry.Value.description
        }
        $UiDefinition.parameters.outputs | Add-Member -NotePropertyName $entry.Name -NotePropertyValue "[steps('contentSelection').$($entry.Name)]"
    }
    if ($elements.Count -gt 0) {
        $UiDefinition.parameters.steps += [pscustomobject]@{
            name = 'contentSelection'
            label = 'Content selection'
            elements = $elements
        }
    }
}
