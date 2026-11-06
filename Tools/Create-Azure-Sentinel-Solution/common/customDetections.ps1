function Get-CustomDetectionParserNames {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SolutionPath
    )

    $parserPath = Join-Path $SolutionPath 'Parsers'
    if (-not (Test-Path -LiteralPath $parserPath -PathType Container)) {
        return
    }
    $names = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($file in (Get-ChildItem -LiteralPath $parserPath -Recurse -File |
            Where-Object { $_.Extension -in '.yaml', '.yml' } | Sort-Object FullName)) {
        $document = Get-Content -LiteralPath $file.FullName -Raw |
            ConvertFrom-Yaml -ErrorAction Stop
        if ($document -isnot [System.Collections.IDictionary]) {
            throw "Parser must contain a YAML object: $($file.FullName)"
        }
        if ($null -eq $document['FunctionName'] -and $null -eq $document['FunctionAlias']) {
            throw "Parser must declare FunctionName or FunctionAlias: $($file.FullName)"
        }
        foreach ($field in @('FunctionName', 'FunctionAlias')) {
            if ($null -ne $document[$field]) {
                if ($document[$field] -isnot [string] -or [string]::IsNullOrWhiteSpace($document[$field])) {
                    throw "Parser $field must be a nonempty string: $($file.FullName)"
                }
                [void]$names.Add($document[$field].Trim())
            }
        }
    }
    return @($names | Sort-Object -CaseSensitive)
}

function Set-CustomDetectionParserBindings {
    param(
        [Parameter(Mandatory = $true)]
        [psobject]$DetectionDocument,
        [string[]]$ParserNames = @()
    )

    if ($ParserNames.Count -eq 0) {
        return
    }
    $helper = Join-Path $PSScriptRoot '..\..\SentinelToXDRMigration\kql\rename-parser-bindings.cjs'
    $node = Get-Command node -CommandType Application -ErrorAction SilentlyContinue
    if ($null -eq $node) {
        throw 'Node.js is required for scope-aware KQL parser binding normalization.'
    }
    $dependency = Join-Path (Split-Path $helper) 'node_modules\@kusto\language-service-next'
    if (-not (Test-Path -LiteralPath $dependency -PathType Container)) {
        throw "KQL dependency is missing; run npm ci --prefix `"$(Split-Path $helper)`""
    }
    $inputJson = @{
        query = [string]$DetectionDocument.properties.queryCondition.queryText
        reservedNames = @($ParserNames)
    } | ConvertTo-Json -Depth 10 -Compress
    $outputJson = $inputJson | & $node.Source $helper 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Custom Detection parser binding normalization failed: $($outputJson -join [Environment]::NewLine)"
    }
    $result = ($outputJson -join [Environment]::NewLine) | ConvertFrom-Json -ErrorAction Stop
    $DetectionDocument.properties.queryCondition.queryText = $result.query
    foreach ($rename in $result.renames) {
        Write-Warning "Renamed local parser binding $($rename.from) to $($rename.to) to avoid a saved parser collision."
    }
}

function Get-CustomDetectionDataProperty {
    param(
        [Parameter(Mandatory = $true)]
        [psobject]$ContentToImport
    )

    return $ContentToImport.PSObject.Properties |
        Where-Object { $_.Name -ieq 'XDR Detections' -or $_.Name -ieq 'Custom Detections' } |
        Select-Object -First 1
}

function Resolve-CustomDetectionPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepositoryRoot,
        [Parameter(Mandatory = $true)]
        [string]$SolutionName,
        [Parameter(Mandatory = $true)]
        [string]$ConfiguredPath
    )

    $normalizedPath = $ConfiguredPath.Replace('\', '/').TrimStart('/')
    $solutionPrefix = "Solutions/$SolutionName/"
    if ($normalizedPath.StartsWith($solutionPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        $normalizedPath = $normalizedPath.Substring($solutionPrefix.Length)
    }
    elseif ($normalizedPath.StartsWith("$SolutionName/", [System.StringComparison]::OrdinalIgnoreCase)) {
        $normalizedPath = $normalizedPath.Substring($SolutionName.Length + 1)
    }

    return Join-Path -Path (Join-Path -Path $RepositoryRoot -ChildPath "Solutions/$SolutionName") -ChildPath $normalizedPath
}

function Get-CustomDetectionDeploymentName {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SolutionName,
        [Parameter(Mandatory = $true)]
        [string]$DetectionId
    )

    $name = (($SolutionName -replace '[^A-Za-z0-9]', '') + '-CD-' + $DetectionId)
    if ($name.Length -le 64) {
        return $name
    }

    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hashBytes = $sha256.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($name))
        $digest = ([System.BitConverter]::ToString($hashBytes) -replace '-', '').Substring(0, 8).ToLowerInvariant()
    }
    finally {
        $sha256.Dispose()
    }

    $prefixLength = 64 - $digest.Length - 1
    return $name.Substring(0, $prefixLength).TrimEnd('-') + '-' + $digest
}

function Copy-CustomDetectionObject {
    param(
        [Parameter(Mandatory = $true)]
        [object]$InputObject
    )

    return $InputObject | ConvertTo-Json -Depth 100 | ConvertFrom-Json
}

function ConvertTo-CustomDetectionArmLiteral {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    $escapedValue = $Value.Replace("'", "''")
    return "[if(true(), '$escapedValue', '$escapedValue')]"
}

function Set-CustomDetectionArmIdentifiers {
    param(
        [Parameter(Mandatory = $true)]
        [psobject]$DetectionResource
    )

    $DetectionResource.properties.id = ConvertTo-CustomDetectionArmLiteral -Value ([string]$DetectionResource.properties.id)
    foreach ($mappingGroup in $DetectionResource.properties.detectionAction.alertTemplate.entityMappings.PSObject.Properties) {
        foreach ($mapping in @($mappingGroup.Value)) {
            if (-not [string]::IsNullOrWhiteSpace([string]$mapping.id)) {
                $mapping.id = ConvertTo-CustomDetectionArmLiteral -Value ([string]$mapping.id)
            }
        }
    }
    foreach ($detail in $DetectionResource.properties.detectionAction.alertTemplate.customDetails.PSObject.Properties) {
        if ($detail.Name -like '*id' -and $detail.Value -is [string]) {
            $detail.Value = ConvertTo-CustomDetectionArmLiteral -Value $detail.Value
        }
    }
    $DetectionResource.properties.contentProvenance.packageId = ConvertTo-CustomDetectionArmLiteral -Value (
        [string]$DetectionResource.properties.contentProvenance.packageId
    )
}

function ConvertTo-CustomDetectionTemplateJson {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Json
    )

    # ARM-TTK's Resolve-JSONContent counts '{' and '}' inside JSON strings;
    # Unicode escapes for braces preserve decoded KQL/ARM strings while keeping
    # literal '[' and ']' intact for ARM-TTK's raw-text expression regexes.
    return [regex]::Replace($Json, '"(?:\\.|[^"\\])*"', [System.Text.RegularExpressions.MatchEvaluator]{
        param($Match)
        return $Match.Value.Replace('{', '\u007b').Replace('}', '\u007d')
    })
}

function ConvertTo-V31CustomDetectionId {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DetectionId,
        [Parameter(Mandatory = $true)]
        [string]$SourceId,
        [Parameter(Mandatory = $true)]
        [bool]$SentinelDerived,
        [Parameter(Mandatory = $true)]
        [string]$ContentPath
    )

    $guidPattern = '\A[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\z'
    $prefixedPattern = '\Axdr-([0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12})\z'
    $normalized = $DetectionId
    if ($SentinelDerived) {
        if ($SourceId -cnotmatch $guidPattern) {
            throw "Sentinel-derived Custom Detection '$ContentPath' has an invalid originating Sentinel template GUID '$SourceId'."
        }
        if ($DetectionId -cmatch $guidPattern) {
            if ($DetectionId -ine $SourceId) {
                throw "Sentinel-derived Custom Detection '$ContentPath' ID '$DetectionId' conflicts with originating Sentinel GUID '$SourceId'; no identity was changed."
            }
            $normalized = "xdr-$SourceId"
        }
        elseif ($DetectionId -match $prefixedPattern) {
            if ($Matches[1] -ine $SourceId) {
                throw "Sentinel-derived Custom Detection '$ContentPath' ID '$DetectionId' conflicts with originating Sentinel GUID '$SourceId'; no identity was changed."
            }
            $normalized = "xdr-$SourceId"
        }
        else {
            throw "Sentinel-derived Custom Detection '$ContentPath' ID '$DetectionId' must be the originating GUID or its canonical xdr-<GUID> form; arbitrary custom IDs are not overwritten."
        }
    }
    elseif ($DetectionId -cmatch $guidPattern) {
        $normalized = "xdr-$DetectionId"
    }
    elseif ($DetectionId -match $prefixedPattern) {
        $normalized = "xdr-$($Matches[1])"
    }
    elseif ($DetectionId -cnotmatch '\A[A-Za-z][A-Za-z0-9_-]{0,99}\z') {
        throw "Custom Detection '$ContentPath' ID '$DetectionId' is invalid for Microsoft Graph; use a letter followed by at most 99 letters, digits, dashes, or underscores."
    }

    if ($normalized -cnotmatch '\A[A-Za-z][A-Za-z0-9_-]{0,99}\z') {
        throw "Normalized Custom Detection ID '$normalized' for '$ContentPath' is invalid for Microsoft Graph."
    }
    return [pscustomobject]@{
        id      = $normalized
        changed = $normalized -cne $DetectionId
    }
}

function Set-V31CustomDetectionTactics {
    param([psobject]$DetectionResource, [string]$DetectionId)
    $alertTemplate = $DetectionResource.properties.detectionAction.alertTemplate
    if ($null -eq $alertTemplate.PSObject.Properties['tactics']) {
        $projection = [ordered]@{
            detectionId     = $DetectionId
            authoredTactics = @()
            packagedTactics = @()
            omittedTactics  = @()
        }
        Write-Host "V3.1 TACTIC PROJECTION: $($projection | ConvertTo-Json -Depth 10 -Compress)"
        return
    }
    $tactics = $alertTemplate.tactics
    if ($tactics -isnot [array] -or $tactics.Count -eq 0) {
        throw "Custom Detection '$DetectionId' tactics must be a nonempty array when supplied."
    }
    foreach ($tactic in $tactics) {
        if ($tactic -isnot [pscustomobject] -or $tactic.tactic -isnot [string] -or
            [string]::IsNullOrWhiteSpace($tactic.tactic)) {
            throw "Custom Detection '$DetectionId' tactics must contain objects with a nonempty tactic name."
        }
        if ($null -ne $tactic.PSObject.Properties['techniques']) {
            if ($tactic.techniques -isnot [array]) {
                throw "Custom Detection '$DetectionId' tactic techniques must be an array."
            }
            foreach ($technique in $tactic.techniques) {
                if ($technique -isnot [pscustomobject] -or $technique.technique -isnot [string] -or
                    [string]::IsNullOrWhiteSpace($technique.technique)) {
                    throw "Custom Detection '$DetectionId' techniques must contain objects with a nonempty technique name."
                }
                if ($null -ne $technique.PSObject.Properties['subTechniques'] -and (
                    $technique.subTechniques -isnot [array] -or
                    @($technique.subTechniques | Where-Object {
                        $_ -isnot [string] -or [string]::IsNullOrWhiteSpace($_)
                    }).Count -gt 0)) {
                    throw "Custom Detection '$DetectionId' subTechniques must be an array of nonempty strings."
                }
            }
        }
    }
    if ($tactics.Count -gt 1) {
        $omittedTactics = @($tactics | Select-Object -Skip 1 | ForEach-Object { [string]$_.tactic })
        $alertTemplate.tactics = @($tactics[0])
    }
    else {
        $omittedTactics = @()
    }
    $projection = [ordered]@{
        detectionId     = $DetectionId
        authoredTactics = @($tactics | ForEach-Object { [string]$_.tactic })
        packagedTactics = @([string]$tactics[0].tactic)
        omittedTactics  = $omittedTactics
    }
    Write-Host "V3.1 TACTIC PROJECTION: $($projection | ConvertTo-Json -Depth 10 -Compress)"
    if ($omittedTactics.Count -gt 0) {
        $dropped = $omittedTactics -join ', '
        Write-Host "INFORMATION: V3.1 TACTIC SELECTION: Custom Detection '$DetectionId' ARM install and registration package the first authored tactic '$($tactics[0].tactic)' and its techniques; omitted tactics: $dropped. Source order is preserved; this is an API payload restriction, not a recommended classification or full tactic coverage. Authored YAML and provenance are unchanged."
    }
}

function Get-AnalyticRuleContentTemplateIndex {
    param(
        [Parameter(Mandatory = $true)]
        [psobject]$Template
    )

    $index = @{}
    foreach ($variableProperty in $Template.variables.PSObject.Properties) {
        $variableValue = $variableProperty.Value
        if ($null -eq $variableValue -or $null -eq $variableValue.PSObject) {
            continue
        }

        foreach ($contentIdProperty in $variableValue.PSObject.Properties) {
            if ($contentIdProperty.Name -like '_analyticRulecontentId*' -and
                -not [string]::IsNullOrWhiteSpace([string]$contentIdProperty.Value)) {
                $index[[string]$contentIdProperty.Value] = $variableProperty.Name
            }
        }
    }

    return $index
}

function Set-AnalyticRuleE5Condition {
    param(
        [Parameter(Mandatory = $true)]
        [psobject]$Template,
        [Parameter(Mandatory = $true)]
        [string]$SourceId,
        [Parameter(Mandatory = $true)]
        [hashtable]$AnalyticRuleIndex
    )

    $variableName = $AnalyticRuleIndex[$SourceId]
    if ([string]::IsNullOrWhiteSpace($variableName)) {
        throw "No AnalyticsRule variable was found for Custom Detection source id '$SourceId'."
    }

    $matched = $false
    $variableReference = "variables('$variableName')"
    foreach ($resource in $Template.resources) {
        if ($resource.properties.contentKind -ne 'AnalyticsRule' -or
            -not ([string]$resource.name).Contains($variableReference)) {
            continue
        }

        if ($null -ne $resource.condition -and $resource.condition -ne "[not(parameters('E5Flavor'))]") {
            $existingCondition = ([string]$resource.condition).Trim('[', ']')
            $resource.condition = "[and(not(parameters('E5Flavor')), $existingCondition)]"
        }
        else {
            $resource | Add-Member -MemberType NoteProperty -Name condition -Value "[not(parameters('E5Flavor'))]" -Force
        }
        $matched = $true
    }

    if (-not $matched) {
        throw "No AnalyticsRule content template resource was found for Custom Detection source id '$SourceId'."
    }
}

function New-CustomDetectionInstallDeployment {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DeploymentName,
        [Parameter(Mandatory = $true)]
        [psobject]$DetectionResource,
        [Parameter(Mandatory = $true)]
        [string]$ExtensionVersion
    )

    if ($null -eq $DetectionResource.properties.contentProvenance) {
        throw 'Custom Detection installation requires resolved content provenance.'
    }
    $deploymentDetection = Copy-CustomDetectionObject -InputObject $DetectionResource
    Set-CustomDetectionArmIdentifiers -DetectionResource $deploymentDetection

    return [pscustomobject]@{
        type       = 'Microsoft.Resources/deployments'
        apiVersion = '2025-04-01'
        name       = $DeploymentName
        condition  = "[parameters('DeployCustomDetection')]"
        dependsOn  = @(
            "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/contentPackages', variables('_solutionId'))]"
        )
        properties = [pscustomobject]@{
            mode                        = 'Incremental'
            expressionEvaluationOptions = [pscustomobject]@{ scope = 'inner' }
            template                    = [pscustomobject]@{
                '$schema'       = 'https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#'
                languageVersion = '2.0'
                contentVersion  = '1.0.0.0'
                imports         = [pscustomobject]@{
                    MicrosoftSecurity = [pscustomobject]@{
                        provider = 'MicrosoftSecurity'
                        version  = $ExtensionVersion
                    }
                }
                resources       = [pscustomobject]@{ detectionRule = $deploymentDetection }
            }
        }
    }
}

function New-CustomDetectionRegistration {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DeploymentName,
        [Parameter(Mandatory = $true)]
        [psobject]$DetectionResource,
        [Parameter(Mandatory = $true)]
        [psobject]$DetectionDocument,
        [Parameter(Mandatory = $true)]
        [string]$ContentVersion,
        [Parameter(Mandatory = $true)]
        [string]$ExtensionVersion
    )

    $contentId = [string]$DetectionResource.properties.id
    $escapedContentId = $contentId.Replace("'", "''")
    $escapedVersion = $ContentVersion.Replace("'", "''")
    $productId = "[concat(take(variables('_solutionId'),50),'-','cd','-', uniqueString(concat(variables('_solutionId'),'-','CustomDetection','-','$escapedContentId','-','$escapedVersion')))]"
    $registrationDetection = Copy-CustomDetectionObject -InputObject $DetectionResource
    Set-CustomDetectionArmIdentifiers -DetectionResource $registrationDetection
    $alertTemplate = $DetectionResource.properties.detectionAction.alertTemplate

    $properties = [ordered]@{
        description          = [string]$alertTemplate.description
        mainTemplate         = [pscustomobject]@{
            '$schema'       = 'https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#'
            languageVersion = '2.0'
            contentVersion  = '1.0.0'
            imports         = [pscustomobject]@{
                MicrosoftSecurity = [pscustomobject]@{
                    provider = 'MicrosoftSecurity'
                    version  = $ExtensionVersion
                }
            }
            resources       = [pscustomobject]@{ detectionRule = $registrationDetection }
        }
        packageKind          = 'Solution'
        packageVersion       = "[variables('_solutionVersion')]"
        packageName          = "[variables('_solutionName')]"
        packageId            = "[variables('_solutionId')]"
        contentSchemaVersion = '3.0.0'
        contentId            = $contentId
        contentKind          = 'CustomDetection'
        displayName          = [string]$DetectionResource.properties.displayName
        contentProductId     = $productId
        id                   = $productId
        version              = $ContentVersion
    }

    $fullProvenance = Copy-CustomDetectionObject -InputObject $DetectionResource.properties.contentProvenance
    $fullProvenance | Add-Member -NotePropertyName requiredWorkloads -NotePropertyValue @($DetectionDocument.contentProvenance.requiredWorkloads)
    $fullProvenance | Add-Member -NotePropertyName requiredDataConnectors -NotePropertyValue @($DetectionDocument.contentProvenance.requiredDataConnectors)
    $fullProvenance.packageId = ConvertTo-CustomDetectionArmLiteral -Value ([string]$fullProvenance.packageId)
    $properties['contentProvenance'] = $fullProvenance

    return [pscustomobject]@{
        type       = 'Microsoft.OperationalInsights/workspaces/providers/contentTemplates'
        apiVersion = '2023-04-01-preview'
        name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat(parameters('workspace'),'-cd-',uniquestring('$escapedContentId')))]"
        location   = "[parameters('workspace-location')]"
        condition  = "[parameters('DeployCustomDetection')]"
        dependsOn  = @(
            "[resourceId('Microsoft.Resources/deployments', '$DeploymentName')]",
            "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/contentPackages', variables('_solutionId'))]"
        )
        properties = [pscustomobject]$properties
    }
}

function Set-XdrCustomDetectionDependencyCriteria {
    param(
        [Parameter(Mandatory = $true)]
        [psobject]$Template,
        [Parameter(Mandatory = $true)]
        [object[]]$Criteria
    )

    $contentPackages = @($Template.resources | Where-Object {
        ([string]$_.type) -ieq 'Microsoft.OperationalInsights/workspaces/providers/contentPackages'
    })
    if ($contentPackages.Count -ne 1) {
        throw "Expected exactly one solution contentPackages resource while adding Custom Detection dependencies; found $($contentPackages.Count)."
    }

    $dependencies = $contentPackages[0].properties.dependencies
    if ($null -eq $dependencies -or $null -eq $dependencies.PSObject.Properties['criteria']) {
        throw 'The solution contentPackages resource has no dependency criteria to extend with Custom Detections.'
    }

    $sentinelCriteria = @($dependencies.criteria | Where-Object {
        ([string]$_.kind) -ine 'CustomDetection'
    })
    $dependencies.criteria = @($sentinelCriteria) + @($Criteria)
}

function Add-XdrCustomDetectionsToSolution {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SolutionName,
        [Parameter(Mandatory = $true)]
        [psobject]$ContentToImport,
        [Parameter(Mandatory = $true)]
        [psobject]$Template
    )

    $detectionProperty = Get-CustomDetectionDataProperty -ContentToImport $ContentToImport
    if ($null -eq $detectionProperty -or @($detectionProperty.Value).Count -eq 0) {
        return 0
    }

    if ($null -eq (Get-Command ConvertFrom-Yaml -ErrorAction SilentlyContinue)) {
        Import-Module powershell-yaml -ErrorAction Stop
    }

    $registrationProperty = $ContentToImport.PSObject.Properties |
        Where-Object { $_.Name -ieq 'Include XDR Content Registration' } |
        Select-Object -First 1
    if ($null -ne $registrationProperty) {
        Write-Warning 'V3.1 CONTENT SELECTION: Include XDR Content Registration is deprecated and ignored (including false). Installation and registration are both emitted under DeployCustomDetection; live provider registration support remains unverified.'
    }
    else {
        Write-Warning 'V3.1 CONTENT SELECTION: Custom Detection installation and registration are both emitted under DeployCustomDetection; live provider registration support remains unverified.'
    }

    $extensionVersion = '1.0.0'
    $extensionVersionProperty = $ContentToImport.PSObject.Properties |
        Where-Object { $_.Name -ieq 'XDR Extension Version' } |
        Select-Object -First 1
    if ($null -ne $extensionVersionProperty -and -not [string]::IsNullOrWhiteSpace([string]$extensionVersionProperty.Value)) {
        $extensionVersion = [string]$extensionVersionProperty.Value
    }

    $defaultContentVersion = [string]$ContentToImport.Version
    $contentVersionProperty = $ContentToImport.PSObject.Properties |
        Where-Object { $_.Name -ieq 'XDR Detection Version' } |
        Select-Object -First 1
    if ($null -ne $contentVersionProperty -and -not [string]::IsNullOrWhiteSpace([string]$contentVersionProperty.Value)) {
        $defaultContentVersion = [string]$contentVersionProperty.Value
    }

    $repoRoot = git rev-parse --show-toplevel
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($repoRoot)) {
        throw 'Unable to resolve the repository root while packaging Custom Detections.'
    }

    $analyticRuleIndex = Get-AnalyticRuleContentTemplateIndex -Template $Template
    $parserNames = @(Get-CustomDetectionParserNames -SolutionPath (Join-Path $repoRoot "Solutions/$SolutionName"))
    $seenIds = @{}
    $dependencyCriteria = @()
    $count = 0
    foreach ($configuredPath in @($detectionProperty.Value)) {
        $detectionPath = Resolve-CustomDetectionPath -RepositoryRoot $repoRoot -SolutionName $SolutionName -ConfiguredPath ([string]$configuredPath)
        if (-not (Test-Path -LiteralPath $detectionPath -PathType Leaf)) {
            throw "Custom Detection file not found: $detectionPath"
        }

        $detectionDocument = Get-Content -LiteralPath $detectionPath -Raw |
            ConvertFrom-Yaml -ErrorAction Stop |
            ConvertTo-Json -Depth 100 |
            ConvertFrom-Json

        if ($detectionDocument.kind -ne 'CustomDetection' -or
            $detectionDocument.resourceType -ne 'Microsoft.Security/detectionRules') {
            throw "Custom Detection '$configuredPath' must declare kind CustomDetection and resourceType Microsoft.Security/detectionRules."
        }

        $sourceId = [string]$detectionDocument.contentProvenance.source.id
        $detectionId = [string]$detectionDocument.properties.id
        if ([string]::IsNullOrWhiteSpace($sourceId) -or [string]::IsNullOrWhiteSpace($detectionId)) {
            throw "Custom Detection '$configuredPath' must contain contentProvenance.source.id and properties.id."
        }
        $sentinelDerived = (
            ($detectionDocument.contentProvenance.source.platform -ceq 'Microsoft Sentinel' -and
             $detectionDocument.contentProvenance.source.kind -ceq 'AnalyticsRule') -or
            $detectionDocument.contentProvenance.conversion.tool -ceq 'sentinel-to-xdr-migration'
        )
        if ($sentinelDerived -and (
                $sourceId -cnotmatch '\A[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\z' -or
                [string]::IsNullOrWhiteSpace($detectionId))) {
            throw "Sentinel-derived Custom Detection '$configuredPath' must contain its full originating Sentinel template GUID in contentProvenance.source.id and a nonempty properties.id."
        }
        $identity = ConvertTo-V31CustomDetectionId -DetectionId $detectionId `
            -SourceId $sourceId -SentinelDerived $sentinelDerived -ContentPath $configuredPath
        $inputDetectionId = $detectionId
        $detectionId = [string]$identity.id
        if ($seenIds.ContainsKey($detectionId)) {
            throw "Duplicate Custom Detection id '$detectionId' after canonical ID normalization. Bare-GUID and xdr-prefixed copies of the same rule cannot be packaged together."
        }
        $seenIds[$detectionId] = $true
        $detectionDocument.properties.id = $detectionId
        $identityEvidence = [ordered]@{
            sourceId   = $sourceId
            inputId    = $inputDetectionId
            packagedId = $detectionId
            changed    = [bool]$identity.changed
            scope      = 'package-projection-only'
        }
        Write-Host "V3.1 ID PROJECTION: $($identityEvidence | ConvertTo-Json -Depth 10 -Compress)"
        if ($identity.changed) {
            Write-Host "INFORMATION: V3.1 ID NORMALIZATION: Custom Detection '$inputDetectionId' is emitted as '$detectionId' for Microsoft Graph compatibility; source/provenance IDs and YAML remain unchanged. This package projection does not update or migrate deployed rules; verify existing identities before any separately approved deployment."
        }

        if ([string]::IsNullOrWhiteSpace([string]$detectionDocument.properties.queryCondition.queryText)) {
            throw "Custom Detection '$detectionId' has no queryCondition.queryText."
        }
        if (-not $v31VersionPolicy -and @($detectionDocument.properties.detectionAction.alertTemplate.tactics).Count -gt 1) {
            throw "Custom Detection '$detectionId' contains more than one tactic; the service supports exactly one."
        }
        if ($null -eq $detectionDocument.properties.detectionAction.alertTemplate.entityMappings) {
            throw "Custom Detection '$detectionId' has no entity mappings."
        }

        $detectionDocument.properties.status = 'disabled'
        if ($null -ne $detectionDocument.properties.schedule -and
            [string]$detectionDocument.properties.schedule.frequency -ceq 'NRT') {
            $detectionDocument.properties.schedule.frequency = 'PT0S'
        }
        Set-CustomDetectionParserBindings -DetectionDocument $detectionDocument -ParserNames $parserNames
        $resourceType = "$($detectionDocument.resourceType)@$($detectionDocument.apiVersion)"
        $detectionResource = [pscustomobject]@{
            import     = 'MicrosoftSecurity'
            type       = $resourceType
            properties = Copy-CustomDetectionObject -InputObject $detectionDocument.properties
        }
        if ($v31VersionPolicy) {
            Set-V31CustomDetectionTactics -DetectionResource $detectionResource -DetectionId $detectionId
        }

        $variableName = $analyticRuleIndex[$sourceId]
        $matches = @($Template.resources | Where-Object {
            $_.properties.contentKind -eq 'AnalyticsRule' -and
            $variableName -and ([string]$_.name).Contains("variables('$variableName')")
        })
        if ($matches.Count -ne 1) {
            throw "Expected exactly one AnalyticsRule content template for Custom Detection source id '$sourceId'; found $($matches.Count)."
        }

        $contentVersion = [string]$detectionDocument.version
        if ($v31VersionPolicy) {
            Assert-V31ReleaseVersion -Version $contentVersion -ContentKind CustomDetection -ContentPath $configuredPath
        }
        elseif ($null -eq $detectionDocument.PSObject.Properties['version']) {
            # Retain old-document compatibility only outside the V3.1 entry point.
            $contentVersion = [string]$detectionDocument.contentProvenance.source.version
            if ([string]::IsNullOrWhiteSpace($contentVersion)) {
                $contentVersion = $defaultContentVersion
            }
        }
        $workloads = @('mde', 'mdo', 'mdi', 'mda', 'mdc', 'entraid', 'purview', 'appgovernance', 'sentinel', 'mtp')
        foreach ($field in @('requiredWorkloads', 'requiredDataConnectors')) {
            $fieldValue = $detectionDocument.contentProvenance.PSObject.Properties[$field]
            if ($null -eq $fieldValue -or $fieldValue.Value -isnot [System.Array]) {
                throw "Custom Detection '$detectionId' requires contentProvenance.$field as an array."
            }
            $identityField = if ($field -eq 'requiredWorkloads') { 'workload' } else { 'connectorId' }
            foreach ($record in $fieldValue.Value) {
                if ($null -eq $record -or $record.$identityField -isnot [string] -or
                    [string]::IsNullOrWhiteSpace($record.$identityField) -or
                    $record.dataTypes -isnot [System.Array]) {
                    throw "Custom Detection '$detectionId' has malformed contentProvenance.$field."
                }
                if ($field -eq 'requiredWorkloads' -and $record.workload -cnotin $workloads) {
                    throw "Custom Detection '$detectionId' has unknown workload '$($record.workload)'."
                }
                foreach ($dataType in $record.dataTypes) {
                    if ($dataType -isnot [string] -or [string]::IsNullOrWhiteSpace($dataType)) {
                        throw "Custom Detection '$detectionId' has invalid dependency dataTypes."
                    }
                }
            }
        }
        if ($detectionDocument.contentProvenance.dependencyReviewRequired -eq $true) {
            throw "Custom Detection '$detectionId' has unresolved dependency provenance."
        }
        $packageId = [string]$Template.variables.solutionId
        $packageVersion = [string]$Template.variables._solutionVersion
        if ([string]::IsNullOrWhiteSpace($packageId) -or $packageId.StartsWith('[') -or
            [string]::IsNullOrWhiteSpace($packageVersion) -or $packageVersion.StartsWith('[') -or
            [string]::IsNullOrWhiteSpace($contentVersion)) {
            throw "Custom Detection '$detectionId' requires resolved package and content identity/version."
        }
        $detectionResource.properties | Add-Member -NotePropertyName contentProvenance -NotePropertyValue ([pscustomobject]@{
            packageId = $packageId
            packageVersion = $packageVersion
            contentId = $detectionId
            contentVersion = $contentVersion
        }) -Force
        $deploymentName = Get-CustomDetectionDeploymentName -SolutionName $SolutionName -DetectionId $detectionId
        $Template.resources += New-CustomDetectionInstallDeployment -DeploymentName $deploymentName -DetectionResource $detectionResource -ExtensionVersion $extensionVersion
        $registration = New-CustomDetectionRegistration -DeploymentName $deploymentName -DetectionResource $detectionResource -DetectionDocument $detectionDocument -ContentVersion $contentVersion -ExtensionVersion $extensionVersion
        $Template.resources += $registration
        $dependencyCriteria += [pscustomobject]@{
            kind      = 'CustomDetection'
            contentId = [string]$registration.properties.contentId
            version   = [string]$registration.properties.version
        }
        $count++
    }

    Set-XdrCustomDetectionDependencyCriteria -Template $Template -Criteria $dependencyCriteria
    Write-Host "Added $count XDR Custom Detection(s) to the hybrid solution template."
    return $count
}
