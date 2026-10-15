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

    $deploymentDetection = Copy-CustomDetectionObject -InputObject $DetectionResource
    $deploymentDetection.properties.id = ConvertTo-CustomDetectionArmLiteral -Value ([string]$deploymentDetection.properties.id)
    foreach ($mappingGroup in $deploymentDetection.properties.detectionAction.alertTemplate.entityMappings.PSObject.Properties) {
        foreach ($mapping in @($mappingGroup.Value)) {
            if (-not [string]::IsNullOrWhiteSpace([string]$mapping.id)) {
                $mapping.id = ConvertTo-CustomDetectionArmLiteral -Value ([string]$mapping.id)
            }
        }
    }

    return [pscustomobject]@{
        type       = 'Microsoft.Resources/deployments'
        apiVersion = '2025-04-01'
        name       = $DeploymentName
        condition  = "[parameters('E5Flavor')]"
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
    $registrationDetection.properties.id = ConvertTo-CustomDetectionArmLiteral -Value ([string]$registrationDetection.properties.id)
    foreach ($mappingGroup in $registrationDetection.properties.detectionAction.alertTemplate.entityMappings.PSObject.Properties) {
        foreach ($mapping in @($mappingGroup.Value)) {
            if (-not [string]::IsNullOrWhiteSpace([string]$mapping.id)) {
                $mapping.id = ConvertTo-CustomDetectionArmLiteral -Value ([string]$mapping.id)
            }
        }
    }
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

    $requiredWorkloads = @($DetectionDocument.contentProvenance.conversion.requiredWorkloads)
    if ($requiredWorkloads.Count -gt 0) {
        $properties['dependency'] = [pscustomobject]@{
            requiredWorkloads = $requiredWorkloads
        }
    }

    return [pscustomobject]@{
        type       = 'Microsoft.OperationalInsights/workspaces/providers/contentTemplates'
        apiVersion = '2023-04-01-preview'
        name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat(parameters('workspace'),'-cd-',uniquestring('$escapedContentId')))]"
        location   = "[parameters('workspace-location')]"
        condition  = "[and(parameters('E5Flavor'), parameters('RegisterE5Content'))]"
        dependsOn  = @(
            "[resourceId('Microsoft.Resources/deployments', '$DeploymentName')]",
            "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/contentPackages', variables('_solutionId'))]"
        )
        properties = [pscustomobject]$properties
    }
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

    if ($null -eq $Template.parameters.E5Flavor) {
        $Template.parameters | Add-Member -MemberType NoteProperty -Name E5Flavor -Value ([pscustomobject]@{
            type         = 'bool'
            defaultValue = $false
            metadata     = [pscustomobject]@{
                description = 'When true, install the E5 / XDR-native custom detections instead of the analytic rules they replace.'
            }
        })
    }
    $includeRegistration = $false
    $registrationProperty = $ContentToImport.PSObject.Properties |
        Where-Object { $_.Name -ieq 'Include XDR Content Registration' } |
        Select-Object -First 1
    if ($null -ne $registrationProperty) {
        $includeRegistration = [System.Convert]::ToBoolean($registrationProperty.Value)
    }
    if ($includeRegistration -and $null -eq $Template.parameters.RegisterE5Content) {
        $Template.parameters | Add-Member -MemberType NoteProperty -Name RegisterE5Content -Value ([pscustomobject]@{
            type         = 'bool'
            defaultValue = $false
            metadata     = [pscustomobject]@{
                description = 'Register each installed custom detection as Content Hub content. Leave false until CustomDetection content-template registration is supported by the live resource provider.'
            }
        })
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
        if ($seenIds.ContainsKey($detectionId)) {
            throw "Duplicate Custom Detection id '$detectionId'."
        }
        $seenIds[$detectionId] = $true

        if ([string]::IsNullOrWhiteSpace([string]$detectionDocument.properties.queryCondition.queryText)) {
            throw "Custom Detection '$detectionId' has no queryCondition.queryText."
        }
        if (@($detectionDocument.properties.detectionAction.alertTemplate.tactics).Count -gt 1) {
            throw "Custom Detection '$detectionId' contains more than one tactic; the service supports exactly one."
        }
        if ($null -eq $detectionDocument.properties.detectionAction.alertTemplate.entityMappings) {
            throw "Custom Detection '$detectionId' has no entity mappings."
        }

        $detectionDocument.properties.status = 'disabled'
        Set-CustomDetectionParserBindings -DetectionDocument $detectionDocument -ParserNames $parserNames
        $resourceType = "$($detectionDocument.resourceType)@$($detectionDocument.apiVersion)"
        $detectionResource = [pscustomobject]@{
            import     = 'MicrosoftSecurity'
            type       = $resourceType
            properties = Copy-CustomDetectionObject -InputObject $detectionDocument.properties
        }

        Set-AnalyticRuleE5Condition -Template $Template -SourceId $sourceId -AnalyticRuleIndex $analyticRuleIndex

        $deploymentName = Get-CustomDetectionDeploymentName -SolutionName $SolutionName -DetectionId $detectionId
        $Template.resources += New-CustomDetectionInstallDeployment -DeploymentName $deploymentName -DetectionResource $detectionResource -ExtensionVersion $extensionVersion

        $contentVersion = [string]$detectionDocument.contentProvenance.source.version
        if ([string]::IsNullOrWhiteSpace($contentVersion)) {
            $contentVersion = $defaultContentVersion
        }
        if ($includeRegistration) {
            $Template.resources += New-CustomDetectionRegistration -DeploymentName $deploymentName -DetectionResource $detectionResource -DetectionDocument $detectionDocument -ContentVersion $contentVersion -ExtensionVersion $extensionVersion
        }
        $count++
    }

    Write-Host "Added $count XDR Custom Detection(s) to the hybrid solution template."
    return $count
}
