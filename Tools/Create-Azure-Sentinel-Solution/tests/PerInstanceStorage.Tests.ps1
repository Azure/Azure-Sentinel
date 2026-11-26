#Requires -Version 7.0
<#
.SYNOPSIS
Offline regressions for opt-in per-instance storage connections.
.DESCRIPTION
Run: pwsh -NoProfile -File Tools/Create-Azure-Sentinel-Solution/tests/PerInstanceStorage.Tests.ps1
Uses synthetic sources in a temporary directory, not parent-owned solution files.
Checks generated expressions, source preservation and the installed field/type
validators. Does not deploy, evaluate ARM resource references or execute KQL.
#>
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\common\commonFunctions.ps1')
. (Join-Path $PSScriptRoot '..\common\get-ccp-details.ps1')
. (Join-Path $PSScriptRoot '..\common\createCCPConnector.ps1')
. (Join-Path $PSScriptRoot '..\common\storageAccountDeploymentTemplate.ps1')
. (Join-Path $PSScriptRoot '..\common\eventGridManagedIdentityDeploymentTemplate.ps1')
. (Join-Path $PSScriptRoot '..\common\perInstanceStorageDeploymentTemplate.ps1')

function Assert-Equal($Actual, $Expected) {
    $actualJson = ConvertTo-Json -InputObject $Actual -Depth 100 -Compress
    $expectedJson = ConvertTo-Json -InputObject $Expected -Depth 100 -Compress
    if ($actualJson -cne $expectedJson) { throw "Expected: $expectedJson`nActual:   $actualJson" }
}

function Assert-Throws([scriptblock]$Action, [string]$Message) {
    try { & $Action }
    catch {
        if (-not $_.Exception.Message.Contains($Message)) { throw "Expected error containing '$Message'; got: $($_.Exception.Message)" }
        return
    }
    throw "Expected error containing '$Message'."
}

function Copy-TestObject($Value) {
    return ConvertFrom-Json -InputObject (ConvertTo-Json -InputObject $Value -Depth 100) -Depth 100
}

function Get-OnlyResource($Template, [string]$Type) {
    $resources = @($Template.resources | Where-Object type -eq $Type)
    Assert-Equal $resources.Count 1
    return $resources[0]
}

function New-TestInput([string]$Name, [switch]$Optional) {
    return [pscustomobject]@{
        type = 'Textbox'
        parameters = [pscustomobject]@{
            name = $Name
            label = $Name
            validations = [pscustomobject]@{ required = -not $Optional }
        }
    }
}

function Save-TestSources($Fixture) {
    foreach ($name in @('Definition', 'Poller', 'Table', 'Dcr')) {
        ConvertTo-Json -InputObject $Fixture.$name -Depth 100 |
            Set-Content -LiteralPath $Fixture.Paths[$name] -Encoding utf8
    }
}

function New-TestFixture([string]$Root) {
    $folder = Join-Path $Root 'Solutions\Fixture\Data Connectors\Fixture'
    $null = New-Item -ItemType Directory -Path $folder -Force
    $identity = @('CloudflareAccountId', 'StorageAccountSubscription', 'StorageAccountResourceGroupName', 'StorageAccountName', 'ContainerName')
    $fixture = @{
        Root = $Root
        Paths = @{
            Definition = Join-Path $folder 'ConnectorDefinition.json'
            Poller = Join-Path $folder 'Poller.json'
            Table = Join-Path $folder 'Table.json'
            Dcr = Join-Path $folder 'DCR.json'
        }
        Definition = [pscustomobject]@{
            name = 'CloudflareDefinition'
            type = 'Microsoft.SecurityInsights/dataConnectorDefinitions'
            kind = 'Customizable'
            properties = [pscustomobject]@{
                connectorUiConfig = [pscustomobject]@{
                    id = 'CloudflareDefinition'
                    title = 'Synthetic storage collector (not its definition ID)'
                    publisher = 'Toolkit tests'
                    instructionSteps = @(
                        [pscustomobject]@{
                            title = 'Accounts'
                            instructions = @((New-TestInput 'CloudflareAccountId'), (New-TestInput 'CloudflareAccountName'))
                        },
                        [pscustomobject]@{
                            title = 'Storage'
                            instructions = @([pscustomobject]@{
                                type = 'ContextPane'
                                parameters = [pscustomobject]@{
                                    instructionSteps = @([pscustomobject]@{
                                        instructions = @(
                                            foreach ($name in @('StorageAccountSubscription', 'StorageAccountResourceGroupName', 'StorageAccountName', 'ContainerName', 'StorageAccountLocation')) {
                                                New-TestInput $name
                                            }
                                            [pscustomobject]@{
                                                type = 'ServicePrincipalIDTextBox_test'
                                                parameters = [pscustomobject]@{ name = 'principalId' }
                                            }
                                        )
                                    })
                                }
                            })
                        },
                        [pscustomobject]@{
                            title = 'Options'
                            instructions = @([pscustomobject]@{
                                type = 'ContextPane'
                                parameters = [pscustomobject]@{
                                    instructionSteps = @([pscustomobject]@{
                                        instructions = @(
                                            (New-TestInput 'TableName' -Optional)
                                            (New-TestInput 'EGSystemTopicName' -Optional)
                                            (New-TestInput 'blobFolderName' -Optional)
                                            [pscustomobject]@{
                                                type = 'Radio'
                                                parameters = [pscustomobject]@{
                                                    name = 'eventGridRbacMode'
                                                    options = @(
                                                        [pscustomobject]@{ value = 'CreateRoleAssignment' },
                                                        [pscustomobject]@{ value = 'UseExistingRoleAssignment' }
                                                    )
                                                }
                                            }
                                        )
                                    })
                                }
                            })
                        }
                    )
                }
            }
        }
        Poller = [pscustomobject]@{
            type = 'Microsoft.SecurityInsights/dataConnectors'
            apiVersion = '2024-09-01'
            name = 'Fixture'
            kind = 'StorageAccountBlobContainer'
            UseRandomGuid = $false
            eventGridUseManagedIdentity = $true
            eventGridAdvancedFilters = @([pscustomobject]@{ operatorType = 'StringNotContains'; key = 'subject'; values = @('/_check') })
            connectionDeployment = [pscustomobject]@{
                mode = 'PerInstance'
                resourcePrefix = 'cloudflare'
                queuePrefix = 'cf'
                tableName = 'CloudflareV2_CL'
                identityParameters = $identity
                enableDcrLogErrors = $true
                attributionColumns = [pscustomobject]@{ CloudflareAccountId = 'CloudflareAccountId'; CloudflareAccountName = 'CloudflareAccountName' }
            }
            properties = [pscustomobject]@{
                auth = [pscustomobject]@{ type = 'ManagedServicePrincipal' }
                connectorDefinitionName = 'CloudflareDefinition'
                dataType = "[[variables('tableName')]"
                dcrConfig = [pscustomobject]@{
                    streamName = 'Custom-Fixture'
                    dataCollectionEndpoint = '{{dataCollectionEndpoint}}'
                    dataCollectionRuleImmutableId = '{{dataCollectionRuleImmutableId}}'
                }
                request = [pscustomobject]@{
                    requestStorageAccountSubscriptionId = '{{StorageAccountSubscription}}'
                    requestStorageAccountResourceGroupName = '{{StorageAccountResourceGroupName}}'
                }
                response = [pscustomobject]@{ eventsJsonPaths = @('$'); format = 'json'; isGzipCompressed = $true }
                addOnAttributes = [pscustomobject]@{
                    account = [pscustomobject]@{ id = '{{CloudflareAccountId}}'; label = '{{CloudflareAccountName}}' }
                    values = @([pscustomobject]@{ value = '{{CloudflareAccountId}}/{{CloudflareAccountName}}'; empty = @() })
                    mixed = @($false, 7, $null, 'fixed')
                    nestedArrays = ConvertFrom-Json -InputObject '[[1],[2,3],[]]' -NoEnumerate
                }
            }
        }
        Table = [pscustomobject]@{
            type = 'Microsoft.OperationalInsights/workspaces/tables'
            apiVersion = '2022-10-01'
            name = 'CloudflareV2_CL'
            properties = [pscustomobject]@{
                retentionInDays = 30
                schema = [pscustomobject]@{
                    name = 'CloudflareV2_CL'
                    columns = @(
                        [pscustomobject]@{ name = 'TimeGenerated'; type = 'datetime'; description = 'Synthetic timestamp' },
                        [pscustomobject]@{ name = 'Message'; type = 'string'; description = 'Synthetic message' },
                        [pscustomobject]@{ name = 'CloudflareAccountId'; type = 'string'; description = 'Configured account ID' },
                        [pscustomobject]@{ name = 'CloudflareAccountName'; type = 'string'; description = 'Configured account label' }
                    )
                }
            }
        }
        Dcr = [pscustomobject]@{
            type = 'Microsoft.Insights/dataCollectionRules'
            apiVersion = '2022-06-01'
            name = 'FixtureDCR-{{workspace}}'
            tags = [pscustomobject]@{ SourceTag = 'preserved' }
            properties = [pscustomobject]@{
                description = 'Authoritative synthetic schema'
                dataSources = [pscustomobject]@{}
                streamDeclarations = [pscustomobject]@{
                    'Custom-Fixture' = [pscustomobject]@{
                        columns = @(
                            [pscustomobject]@{ name = 'TimeGenerated'; type = 'datetime' },
                            [pscustomobject]@{ name = 'Message'; type = 'string' }
                        )
                    }
                }
                destinations = [pscustomobject]@{
                    logAnalytics = @([pscustomobject]@{ name = 'workspace'; workspaceResourceId = '{{workspaceResourceId}}' })
                }
                dataFlows = @([pscustomobject]@{
                    streams = @('Custom-Fixture')
                    destinations = @('workspace')
                    outputStream = 'Custom-CloudflareV2_CL'
                    transformKql = "source`n| where isnotempty(Message)`n| extend CloudflareAccountId = '', CloudflareAccountName = ''`n| project TimeGenerated, Message, CloudflareAccountId, CloudflareAccountName"
                })
            }
        }
    }
    Save-TestSources $fixture
    return $fixture
}

function Invoke-TestGenerator($Fixture) {
    Save-TestSources $Fixture
    . (Join-Path $PSScriptRoot '..\common\commonFunctions.ps1')
    $data = [pscustomobject]@{
        Name = 'Fixture'; Author = 'Toolkit tests - maintainer@example.invalid'; Version = '3.0.0'
        'Data Connectors' = @('Data Connectors/Fixture/ConnectorDefinition.json')
    }
    $metadata = [pscustomobject]@{ publisherId = 'test'; offerId = 'fixture'; support = [pscustomobject]@{ name = 'Toolkit tests'; tier = 'Community' } }
    $base = (Join-Path $Fixture.Root 'Solutions') + [IO.Path]::DirectorySeparatorChar
    $dict = @(Get-CCP-Dict -dataFileMetadata $data -baseFolderPath $base -solutionName 'Fixture' -DCFolderName 'Data Connectors')
    Assert-Equal $dict.Count 1
    createCCPConnectorResources -contentResourceDetails (returnContentResources $data.Version) `
        -dataFileMetadata $data -solutionFileMetadata $metadata -dcFolderName 'Data Connectors' `
        -ccpDict $dict -solutionBasePath $base -solutionName 'Fixture' -ccpTables @() -ccpTablesCounter 1
    # Same serialization depth as V3; fail instead of truncating nested metadata.
    return $global:baseMainTemplate | ConvertTo-Json -Depth 50 -WarningAction Stop | ConvertFrom-Json -AsHashtable -Depth 100
}

function Invoke-TestHelper($Fixture, [scriptblock]$ChangeParameters = {}) {
    Save-TestSources $Fixture
    $definition = Copy-TestObject $Fixture.Definition
    $definition.type = 'Microsoft.OperationalInsights/workspaces/providers/dataConnectorDefinitions'
    $parameters = Get-ConnectionsTemplateParameters @($definition)
    & $ChangeParameters $parameters
    $connection = [pscustomobject]@{ properties = [pscustomobject]@{
        mainTemplate = [pscustomobject]@{ parameters = [pscustomobject]@{}; variables = [pscustomobject]@{}; resources = @() }
    } }
    $poller = Copy-TestObject $Fixture.Poller
    $item = [pscustomobject]@{ DCDefinitionId = 'CloudflareDefinition'; DCRFilePath = $Fixture.Paths.Dcr; TableFilePath = $Fixture.Paths.Table }
    CreatePerInstanceStorageAccountBlobContainerResourceProperties -ArmResource $poller `
        -TemplateContentConnections $connection -DeploymentConfig $poller.connectionDeployment `
        -CcpItem $item -InstructionParameters $parameters
    return $connection.properties.mainTemplate
}

function Get-Connections($Package) {
    $connections = @($Package.resources | Where-Object { $_.properties.contentKind -eq 'ResourcesDataConnector' })
    Assert-Equal $connections.Count 1
    return $connections[0].properties.mainTemplate
}

function Convert-TestConnectionExpressions($Value) {
    # ARM removes one leading escape bracket when the outer solution installs
    # the content template. Test that runtime template, not the inert [[ strings.
    if ($Value -is [string] -and $Value.StartsWith('[[')) { return $Value.Substring(1) }
    if ($Value -is [PSCustomObject]) {
        foreach ($property in @($Value.PSObject.Properties)) {
            $property.Value = Convert-TestConnectionExpressions $property.Value
        }
    }
    elseif ($Value -is [array]) {
        for ($i = 0; $i -lt $Value.Count; $i++) { $Value[$i] = Convert-TestConnectionExpressions $Value[$i] }
    }
    return ,$Value
}

function Expand-TestAttribution([string]$Expression, [hashtable]$Parameters, [System.Collections.IDictionary]$Variables = @{}) {
    # Deliberately limited interpreter for the emitted concat/string/base64/substring
    # expression, not an ARM/KQL evaluator and never Invoke-Expression.
    if (-not $Expression.StartsWith('[[concat(') -or -not $Expression.EndsWith(')]')) { throw 'Not an attribution concat expression.' }
    $body = $Expression.Substring(9, $Expression.Length - 11)
    $pattern = "\G\s*(?:'(?<literal>(?:[^']|'')*)'|base64\(parameters\('(?<parameter>[A-Za-z_][A-Za-z0-9_]*)'\)\)|substring\(variables\('(?<variable>[A-Za-z_][A-Za-z0-9_]*)'\), (?<start>\d+), (?<length>\d+)\))\s*(?:,|$)"
    $parser = [regex]::new($pattern, [Text.RegularExpressions.RegexOptions]::None, [timespan]::FromSeconds(2))
    $result = [Text.StringBuilder]::new()
    $cursor = 0
    while ($cursor -lt $body.Length) {
        # \G anchors at the requested start, not at a previously matched prefix.
        $match = $parser.Match($body, $cursor)
        if (-not $match.Success) { throw "Unsupported attribution expression at $cursor." }
        if ($match.Groups['parameter'].Success) {
            $name = $match.Groups['parameter'].Value
            if (-not $Parameters.ContainsKey($name)) { throw "Missing test value '$name'." }
            $null = $result.Append([Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Parameters[$name])))
        }
        elseif ($match.Groups['variable'].Success) {
            $name = $match.Groups['variable'].Value
            if (-not $Variables.Contains($name)) { throw "Missing test variable '$name'." }
            $null = $result.Append($Variables[$name].Substring([int]$match.Groups['start'].Value, [int]$match.Groups['length'].Value))
        }
        else { $null = $result.Append($match.Groups['literal'].Value.Replace("''", "'")) }
        $cursor += $match.Length
    }
    return $result.ToString()
}

$tests = [ordered]@{
    'Discovery and dispatcher emit per-instance topology only at connection time' = {
        $package = Invoke-TestGenerator $fixture
        $connection = Get-Connections $package
        $connector = Get-OnlyResource $connection 'Microsoft.OperationalInsights/workspaces/providers/dataConnectors'
        Assert-Equal $connector.properties.connectorDefinitionName 'CloudflareDefinition'
        Assert-Equal $connector.properties.auth.type 'ManagedServicePrincipal'
        Assert-Equal $connector.properties.dataType "[[variables('tableName')]"
        Assert-Equal $connector.apiVersion '2024-09-01'
        foreach ($name in @('connectionDeployment', 'eventGridUseManagedIdentity', 'eventGridAdvancedFilters', 'UseRandomGuid')) {
            Assert-Equal $connector.Contains($name) $false
        }
        foreach ($name in @('guidValue', 'dcrConfig', 'forceUpdateTag')) { Assert-Equal $connection.parameters.Contains($name) $false }
        foreach ($type in @('Microsoft.Insights/dataCollectionRules', 'Microsoft.Insights/dataCollectionEndpoints', 'Microsoft.OperationalInsights/workspaces/tables', 'Microsoft.Insights/diagnosticSettings', 'Microsoft.Resources/deployments')) {
            $null = Get-OnlyResource $connection $type
        }
        Assert-Equal @($connection.resources | Where-Object type -eq 'Microsoft.Resources/deploymentScripts').Count 0
        $definitionTemplate = @($package.resources | Where-Object { $_.properties.contentKind -eq 'DataConnector' })[0].properties.mainTemplate
        Assert-Equal @($definitionTemplate.resources | Where-Object type -eq 'Microsoft.Insights/dataCollectionRules').Count 0
        Assert-Equal $connector.dependsOn @("[[variables('dcrResourceId')]", "[[variables('dceResourceId')]", "[[variables('nestedDeploymentId')]")
    }
    'All three UI steps, twelve inputs and optional defaults survive merging' = {
        $package = Invoke-TestGenerator $fixture
        $connection = Get-Connections $package
        $definition = Get-OnlyResource $package 'Microsoft.OperationalInsights/workspaces/providers/dataConnectorDefinitions'
        Assert-Equal $definition.properties.connectorUiConfig $fixture.Definition.properties.connectorUiConfig
        foreach ($name in @('CloudflareAccountId', 'CloudflareAccountName', 'StorageAccountSubscription', 'StorageAccountResourceGroupName', 'StorageAccountName', 'ContainerName', 'StorageAccountLocation', 'principalId', 'TableName', 'EGSystemTopicName', 'blobFolderName', 'eventGridRbacMode')) {
            Assert-Equal $connection.parameters[$name].type 'securestring'
        }
        foreach ($name in @('TableName', 'EGSystemTopicName', 'blobFolderName')) {
            Assert-Equal $connection.parameters[$name].defaultValue ''
            Assert-Equal $connection.parameters[$name].Contains('minLength') $false
        }
        Assert-Equal $connection.parameters.eventGridRbacMode.allowedValues @('CreateRoleAssignment', 'UseExistingRoleAssignment')
        Assert-Equal $connection.parameters.eventGridRbacMode.defaultValue 'CreateRoleAssignment'
        Assert-Equal $connection.variables.tableName "[[if(empty(trim(parameters('TableName'))), variables('tableNameDefault'), trim(parameters('TableName')))]"
    }
    'Nested attributes, arrays, scalar types and request scope placeholders are preserved' = {
        $connection = Get-Connections (Invoke-TestGenerator $fixture)
        $connector = Get-OnlyResource $connection 'Microsoft.OperationalInsights/workspaces/providers/dataConnectors'
        $attributes = $connector.properties.addOnAttributes
        Assert-Equal $attributes.account.id "[[parameters('CloudflareAccountId')]"
        Assert-Equal $attributes.account.label "[[parameters('CloudflareAccountName')]"
        Assert-Equal $attributes.values.Count 1
        Assert-Equal $attributes.values[0].value "[[concat(parameters('CloudflareAccountId'),'/',parameters('CloudflareAccountName'))]"
        Assert-Equal $attributes.values[0].empty @()
        Assert-Equal $attributes.mixed @($false, 7, $null, 'fixed')
        Assert-Equal $attributes.nestedArrays $fixture.Poller.properties.addOnAttributes.nestedArrays
        Assert-Equal $connector.properties.response $fixture.Poller.properties.response
        Assert-Equal $connector.properties.request.requestStorageAccountSubscriptionId "[[parameters('StorageAccountSubscription')]"
        Assert-Equal $connector.properties.request.requestStorageAccountResourceGroupName "[[parameters('StorageAccountResourceGroupName')]"
    }
    'Shared AddOnAttributes processing also preserves nested objects and arrays' = {
        $templateContentConnections = [pscustomobject]@{ properties = [pscustomobject]@{
            mainTemplate = [pscustomobject]@{ parameters = [pscustomobject]@{} }
        } }
        $global:commaSeparatedTextFieldName = ''
        $armResource = Copy-TestObject $fixture.Poller
        AddOnAttributes $armResource
        Assert-Equal $armResource.properties.addOnAttributes.account.label "[[parameters('CloudflareAccountName')]"
        Assert-Equal $armResource.properties.addOnAttributes.mixed $fixture.Poller.properties.addOnAttributes.mixed
        Assert-Equal $armResource.properties.addOnAttributes.nestedArrays $fixture.Poller.properties.addOnAttributes.nestedArrays
        Assert-Equal $armResource.properties.addOnAttributes.values[0].empty @()
    }
    'PR14792 identity order, normalization and name formulas are unchanged' = {
        $connection = Invoke-TestHelper $fixture
        $vars = $connection.variables
        Assert-Equal $vars.instanceKey "[[uniqueString(toLower(trim(parameters('CloudflareAccountId'))), toLower(trim(parameters('StorageAccountSubscription'))), toLower(trim(parameters('StorageAccountResourceGroupName'))), toLower(trim(parameters('StorageAccountName'))), toLower(trim(parameters('ContainerName'))), toLower(variables('workspaceResourceId')))]"
        Assert-Equal $vars.workspaceResourceId "[[resourceId('Microsoft.OperationalInsights/workspaces', parameters('innerWorkspace'))]"
        foreach ($name in @('connectorName', 'dcrName', 'dceName')) {
            Assert-Equal $vars[$name] "[[format('{0}-{1}', variables('resourcePrefix'), variables('instanceKey'))]"
        }
        Assert-Equal $vars.queueName "[[format('{0}-{1}-notification', variables('queuePrefix'), variables('instanceKey'))]"
        Assert-Equal $vars.dlqName "[[format('{0}-{1}-dlq', variables('queuePrefix'), variables('instanceKey'))]"
        Assert-Equal $vars.EgSubscriptionName "[[format('{0}-{1}-blobcreated', variables('resourcePrefix'), variables('instanceKey'))]"
        Assert-Equal $vars.nestedDeploymentName "[[format('{0}-{1}-storage', variables('resourcePrefix'), variables('instanceKey'))]"
        Assert-Equal $vars.EGSystemTopicDefaultName "[[format('sentinel-{0}-{1}', variables('resourcePrefix'), uniqueString(toLower(trim(parameters('StorageAccountSubscription'))), toLower(trim(parameters('StorageAccountResourceGroupName'))), variables('storageAccountName')))]"
        Assert-Equal $vars.EGSystemTopicName "[[if(empty(parameters('EGSystemTopicName')), variables('EGSystemTopicDefaultName'), parameters('EGSystemTopicName'))]"
        Assert-Equal $vars.instanceKey.Contains('CloudflareAccountName') $false
        Assert-Equal $vars.instanceKey.Contains('TableName') $false
        # The exact old expression above is the migration invariant. These checks
        # exercise its ordered, normalized hash inputs, not a substitute hash.
        $values = @(' Account-A ', '00000000-0000-0000-0000-000000000001', 'Storage-RG', 'storagefixture', 'logs')
        $workspace = '/subscriptions/00000000-0000-0000-0000-000000000002/resourceGroups/workspace-rg/providers/Microsoft.OperationalInsights/workspaces/fixture'
        $seed = @($values | ForEach-Object { $_.Trim().ToLowerInvariant() }) + $workspace.ToLowerInvariant()
        $repeat = @($values | ForEach-Object { $_.ToUpperInvariant().Trim().ToLowerInvariant() }) + $workspace.ToLowerInvariant()
        Assert-Equal $seed $repeat
        for ($i = 0; $i -lt $seed.Count; $i++) {
            $changed = @($seed)
            $changed[$i] += '-different'
            Assert-Equal (($changed -join '|') -ceq ($seed -join '|')) $false
        }
    }
    'Current MI helper, source guard, identity preservation and sender-only opt-out are reused' = {
        $connection = Invoke-TestHelper $fixture
        $deployment = Get-OnlyResource $connection 'Microsoft.Resources/deployments'
        $inner = $deployment.properties.template
        Assert-Equal $deployment.properties.expressionEvaluationOptions.scope 'inner'
        Assert-Equal $deployment.subscriptionId "[[trim(parameters('StorageAccountSubscription'))]"
        Assert-Equal $deployment.resourceGroup "[[trim(parameters('StorageAccountResourceGroupName'))]"
        $children = @($inner.resources | Where-Object type -eq 'Microsoft.Resources/deployments')
        Assert-Equal $children (Get-EventGridManagedIdentityDeployments)
        Assert-Equal $inner.parameters.existingSystemTopicMatchesStorageAccount.allowedValues @($true)
        Assert-Equal $deployment.properties.parameters.existingSystemTopic.value "[[if(empty(parameters('EGSystemTopicName')), createObject(), reference(variables('EGTopicResourceId'), '2025-02-15', 'Full'))]"
        $roles = @($inner.resources | Where-Object type -like '*/providers/roleAssignments')
        Assert-Equal $roles.Count 3
        foreach ($role in $roles) { Assert-Equal $role.Contains('condition') $false }
        $blob = @($roles | Where-Object type -like '*/blobServices/*')[0]
        Assert-Equal $blob.properties.roleDefinitionId "[[variables('storageBlobReaderRoleId')]"
        Assert-Equal $connection.variables.blobRaGuid "[[guid(variables('blobContainerResourceId'), parameters('principalId'), variables('storageBlobReaderRoleId'))]"
        Assert-Equal $connection.variables.notificationQueueRaGuid "[[guid(variables('notificationQueueResourceId'), parameters('principalId'), variables('storageQueueContributorRoleId'))]"
        Assert-Equal $connection.variables.dlqRaGuid "[[guid(variables('dlqResourceId'), parameters('principalId'), variables('storageQueueContributorRoleId'))]"
        $event = Get-OnlyResource $inner 'Microsoft.EventGrid/systemTopics/eventSubscriptions'
        Assert-Equal $event.properties.filter.advancedFilters $fixture.Poller.eventGridAdvancedFilters
        Assert-Equal $event.properties.filter.subjectBeginsWith "[[format('{0}/{1}/blobs/{2}', '/blobServices/default/containers', variables('blobContainerName'), if(empty(parameters('blobFolderName')), '', concat(parameters('blobFolderName'),'/')))]"
        Assert-Equal $event.dependsOn @(
            "[[if(equals(parameters('eventGridRbacMode'), 'CreateRoleAssignment'), variables('eventGridQueueSenderDeploymentId'), variables('eventGridTopicDeploymentId'))]",
            "[[variables('notificationQueueResourceId')]"
        )
        foreach ($name in @('storageAccountId', 'blobContainerResourceId', 'notificationQueueResourceId', 'dlqResourceId', 'EGTopicResourceId', 'EgSubscriptionResourceId', 'nestedDeploymentId')) {
            Assert-Equal $connection.variables[$name].StartsWith("[[resourceId(trim(parameters('StorageAccountSubscription')), trim(parameters('StorageAccountResourceGroupName')),") $true
        }
    }
    'Source schema descriptions, added fields, tags and transform body are authoritative' = {
        $fixture.Table.properties.schema.columns += [pscustomobject]@{ name = 'ExtraField'; type = 'string'; description = "An author's new column" }
        $fixture.Dcr.properties.streamDeclarations.'Custom-Fixture'.columns += [pscustomobject]@{ name = 'ExtraField'; type = 'string' }
        $fixture.Dcr.properties.dataFlows[0].transformKql += ', ExtraField'
        $connection = Invoke-TestHelper $fixture
        $table = Get-OnlyResource $connection 'Microsoft.OperationalInsights/workspaces/tables'
        $dcr = Get-OnlyResource $connection 'Microsoft.Insights/dataCollectionRules'
        Assert-Equal $table.properties.schema.columns $fixture.Table.properties.schema.columns
        Assert-Equal $dcr.properties.streamDeclarations $fixture.Dcr.properties.streamDeclarations
        Assert-Equal $dcr.properties.dataSources $fixture.Dcr.properties.dataSources
        Assert-Equal $dcr.tags $fixture.Dcr.tags
        Assert-Equal $dcr.properties.dataFlows[0].outputStream "[[variables('outputStreamName')]"
        Assert-Equal $dcr.properties.destinations.logAnalytics[0].workspaceResourceId "[[variables('workspaceResourceId')]"
        Assert-Equal $dcr.properties.dataCollectionEndpointId "[[variables('dceResourceId')]"
    }
    'Authoring preview APIs are replaced by deployable APIs without changing source schemas or transforms' = {
        $fixture.Table.apiVersion = '2021-03-01-privatepreview'
        $fixture.Dcr.apiVersion = '2021-09-01-preview'
        $connection = Get-Connections (Invoke-TestGenerator $fixture)
        $table = Get-OnlyResource $connection 'Microsoft.OperationalInsights/workspaces/tables'
        $dcr = Get-OnlyResource $connection 'Microsoft.Insights/dataCollectionRules'
        $dce = Get-OnlyResource $connection 'Microsoft.Insights/dataCollectionEndpoints'
        Assert-Equal ([ordered]@{ table = $table.apiVersion; dcr = $dcr.apiVersion; dce = $dce.apiVersion }) `
            ([ordered]@{ table = '2022-10-01'; dcr = '2022-06-01'; dce = '2022-06-01' })

        $schema = Copy-TestObject $fixture.Table.properties.schema
        $schema.name = "[[variables('tableName')]"
        Assert-Equal $table.properties.schema $schema
        Assert-Equal $table.properties.retentionInDays $fixture.Table.properties.retentionInDays
        Assert-Equal $dcr.properties.streamDeclarations $fixture.Dcr.properties.streamDeclarations
        Assert-Equal $dcr.properties.dataSources $fixture.Dcr.properties.dataSources
        Assert-Equal $dcr.tags $fixture.Dcr.tags
        $sourceTransform = $fixture.Dcr.properties.dataFlows[0].transformKql
        Assert-Equal $connection.variables.perInstanceSourceTransform0 $sourceTransform
        $values = @{ CloudflareAccountId = 'account-a'; CloudflareAccountName = "O'Brian\Lab" }
        $expected = $sourceTransform
        foreach ($name in @('CloudflareAccountId', 'CloudflareAccountName')) {
            $encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($values[$name]))
            $expected = $expected.Replace("$name = ''", "$name = base64_decodestring('$encoded')")
        }
        Assert-Equal (Expand-TestAttribution $dcr.properties.dataFlows[0].transformKql $values $connection.variables) $expected
        # Version normalization applies to generated resources, never source files.
        Assert-Equal (Get-Content -LiteralPath $fixture.Paths.Table -Raw | ConvertFrom-Json -Depth 100) $fixture.Table
        Assert-Equal (Get-Content -LiteralPath $fixture.Paths.Dcr -Raw | ConvertFrom-Json -Depth 100) $fixture.Dcr
    }
    'Attribution preserves quotes, backslashes, Unicode and hostile-looking values without KQL injection' = {
        $transform = $fixture.Dcr.properties.dataFlows[0].transformKql
        # Property order must not be a hidden ordering requirement on source KQL.
        $mapping = [pscustomobject]@{ CloudflareAccountName = 'CloudflareAccountName'; CloudflareAccountId = 'CloudflareAccountId' }
        $expression = Get-PerInstanceAttributionTransform -Transform $transform -Attribution $mapping
        foreach ($label in @("O'Brian\Lab", "é東京`nnew`rline`tlabel", "'); project Injected='yes'; //\tail")) {
            $values = @{ CloudflareAccountId = 'account-a'; CloudflareAccountName = $label }
            $expanded = Expand-TestAttribution $expression $values
            $expected = $transform
            foreach ($name in @('CloudflareAccountId', 'CloudflareAccountName')) {
                $encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($values[$name]))
                $expected = $expected.Replace("$name = ''", "$name = base64_decodestring('$encoded')")
            }
            Assert-Equal $expanded $expected
            $encodedLabels = [regex]::Matches($expanded, "base64_decodestring\('([A-Za-z0-9+/=]*)'\)")
            Assert-Equal $encodedLabels.Count 2
            Assert-Equal ([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($encodedLabels[1].Groups[1].Value))) $label
        }
    }
    'Large source transforms stay intact without exceeding the ARM expression length limit' = {
        $fixture.Dcr.properties.dataFlows[0].transformKql = (
            '// A long authoritative transformation must remain data, not a huge ARM expression.' + "`n"
        ) * 800 + $fixture.Dcr.properties.dataFlows[0].transformKql
        $source = $fixture.Dcr.properties.dataFlows[0].transformKql
        Assert-Equal ($source.Length -gt 24576) $true
        $connection = Invoke-TestHelper $fixture
        $dcr = Get-OnlyResource $connection 'Microsoft.Insights/dataCollectionRules'
        Assert-Equal $connection.variables.perInstanceSourceTransform0 $source
        Assert-Equal ($dcr.properties.dataFlows[0].transformKql.Length -lt 4096) $true
        $values = @{ CloudflareAccountId = 'account-a'; CloudflareAccountName = "O'Brian\Lab" }
        $expanded = Expand-TestAttribution $dcr.properties.dataFlows[0].transformKql $values $connection.variables
        $expected = $source
        foreach ($name in @('CloudflareAccountId', 'CloudflareAccountName')) {
            $encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($values[$name]))
            $expected = $expected.Replace("$name = ''", "$name = base64_decodestring('$encoded')")
        }
        Assert-Equal $expanded $expected
    }
    'Missing, ambiguous or invalid attribution metadata fails explicitly' = {
        $mapping = $fixture.Poller.connectionDeployment.attributionColumns
        Assert-Throws { Get-PerInstanceAttributionTransform -Transform 'source | project Message' -Attribution $mapping } 'requires exactly one empty-string assignment'
        Assert-Throws { Get-PerInstanceAttributionTransform -Transform "source | extend CloudflareAccountId = '', CloudflareAccountId = ''" -Attribution $mapping } 'requires exactly one empty-string assignment'
        Assert-Throws { Get-PerInstanceAttributionTransform -Transform "source | extend A = ''" -Attribution ([pscustomobject]@{ A = "bad'); expression" }) } 'must map KQL column identifiers'
        $fixture.Table.properties.schema.columns = @($fixture.Table.properties.schema.columns | Where-Object name -ne 'CloudflareAccountName')
        Assert-Throws { Invoke-TestHelper $fixture } "Attribution column 'CloudflareAccountName' must be declared once as a string"
    }
    'Config booleans, unknown options and naming constraints fail closed' = {
        $original = Copy-TestObject $fixture.Poller.connectionDeployment
        foreach ($case in @(
            @{ Name = 'mode'; Value = 'Unknown'; Error = "mode 'PerInstance'" },
            @{ Name = 'enableDcrLogErrors'; Value = 'false'; Error = 'enableDcrLogErrors must be a boolean' },
            @{ Name = 'queuePrefix'; Value = 'bad--queue'; Error = 'queuePrefix must be' },
            @{ Name = 'resourcePrefix'; Value = "bad'prefix"; Error = 'resourcePrefix must be' },
            @{ Name = 'tableName'; Value = 'Invalid-Table'; Error = 'tableName must be' },
            @{ Name = 'rolePropagationDelaySeconds'; Value = 90; Error = "Unsupported connectionDeployment option 'rolePropagationDelaySeconds'" }
        )) {
            $fixture.Poller.connectionDeployment = Copy-TestObject $original
            $fixture.Poller.connectionDeployment | Add-Member -NotePropertyName $case.Name -NotePropertyValue $case.Value -Force
            Assert-Throws { Invoke-TestHelper $fixture } $case.Error
        }
    }
    'Immutable identity inputs must exist, be scalar, required and unique' = {
        $original = @($fixture.Poller.connectionDeployment.identityParameters)
        Assert-Throws { Invoke-TestHelper $fixture { param($p) $p.PSObject.Properties.Remove('CloudflareAccountId') } } "parameter 'CloudflareAccountId' must be declared"
        Assert-Throws { Invoke-TestHelper $fixture { param($p) $p.CloudflareAccountId.type = 'array' } } "parameter 'CloudflareAccountId' must be declared"
        Assert-Throws { Invoke-TestHelper $fixture { param($p) $p.eventGridRbacMode.type = 'array' } } "Optional per-instance parameter 'eventGridRbacMode' must be a scalar input"
        Assert-Throws { Invoke-TestHelper $fixture { param($p) $p.CloudflareAccountId.PSObject.Properties.Remove('minLength') } } "Immutable identity parameter 'CloudflareAccountId' must be a required"
        $fixture.Poller.connectionDeployment.identityParameters = $original + 'cloudflareaccountid'
        Assert-Throws { Invoke-TestHelper $fixture } 'must contain unique parameter identifiers'
        $fixture.Poller.connectionDeployment.identityParameters = $original + 'TableName'
        Assert-Throws { Invoke-TestHelper $fixture } "Mutable setting 'TableName' cannot be"
        $fixture.Poller.connectionDeployment.identityParameters = @($original | Where-Object { $_ -ne 'StorageAccountSubscription' })
        Assert-Throws { Invoke-TestHelper $fixture } "identityParameters must include 'StorageAccountSubscription'"
    }
    'First-party auth, MI boolean and literal backend definition ID are enforced' = {
        foreach ($value in @($false, 'true')) {
            $fixture.Poller.eventGridUseManagedIdentity = $value
            Assert-Throws { Invoke-TestHelper $fixture } 'requires eventGridUseManagedIdentity: true'
        }
        $fixture.Poller.eventGridUseManagedIdentity = $true
        $fixture.Poller.properties.auth.type = 'ServicePrincipal'
        Assert-Throws { Invoke-TestHelper $fixture } 'requires ManagedServicePrincipal'
        $fixture.Poller.properties.auth.type = 'ManagedServicePrincipal'
        $fixture.Poller.properties.connectorDefinitionName = "[[parameters('connectorDefinitionName')]"
        Assert-Throws { Invoke-TestHelper $fixture } 'must be the literal connector definition ID'
    }
    'Unsupported table and DCR routing does not silently fall back' = {
        $fixture.Dcr.properties.dataFlows[0].outputStream = 'Custom-Other_CL'
        Assert-Throws { Invoke-TestHelper $fixture } 'Every per-instance DCR data flow must route'
        $fixture.Dcr.properties.dataFlows[0].outputStream = 'Custom-CloudflareV2_CL'
        $fixture.Dcr.properties.destinations.logAnalytics += [pscustomobject]@{ name = 'another'; workspaceResourceId = 'unused' }
        Assert-Throws { Invoke-TestHelper $fixture } 'must declare one Log Analytics destination'
        $fixture.Dcr.properties.destinations.logAnalytics = @($fixture.Dcr.properties.destinations.logAnalytics[0])
        $fixture.Poller.properties.dcrConfig.streamName = 'Custom-Undeclared'
        Assert-Throws { Invoke-TestHelper $fixture } 'streamName must name an input stream declared and routed'
    }
    'Authoritative table rejects a top-level false condition' = {
        $fixture.Table | Add-Member -NotePropertyName 'condition' -NotePropertyValue $false
        Assert-Throws { Invoke-TestHelper $fixture } "Per-instance table source does not support top-level 'condition'."
    }
    'Authoritative table rejects a top-level copy loop' = {
        $fixture.Table | Add-Member -NotePropertyName 'copy' -NotePropertyValue ([pscustomobject]@{ name = 'tableCopies'; count = 2 })
        Assert-Throws { Invoke-TestHelper $fixture } "Per-instance table source does not support top-level 'copy'."
    }
    'Authoritative DCR rejects a top-level false condition' = {
        $fixture.Dcr | Add-Member -NotePropertyName 'condition' -NotePropertyValue $false
        Assert-Throws { Invoke-TestHelper $fixture } "Per-instance DCR source does not support top-level 'condition'."
    }
    'Authoritative DCR rejects a top-level copy loop' = {
        $fixture.Dcr | Add-Member -NotePropertyName 'copy' -NotePropertyValue ([pscustomobject]@{ name = 'dcrCopies'; count = 2 })
        Assert-Throws { Invoke-TestHelper $fixture } "Per-instance DCR source does not support top-level 'copy'."
    }
    'Diagnostics and attribution are independently optional' = {
        $fixture.Poller.connectionDeployment.enableDcrLogErrors = $false
        $fixture.Poller.connectionDeployment.PSObject.Properties.Remove('attributionColumns')
        $connection = Invoke-TestHelper $fixture
        Assert-Equal @($connection.resources | Where-Object type -eq 'Microsoft.Insights/diagnosticSettings').Count 0
        $dcr = Get-OnlyResource $connection 'Microsoft.Insights/dataCollectionRules'
        Assert-Equal $dcr.properties.dataFlows[0].transformKql $fixture.Dcr.properties.dataFlows[0].transformKql
    }
    'No opt-in keeps shared storage routing and legacy ROLE plus GUID behavior' = {
        $fixture.Poller.PSObject.Properties.Remove('connectionDeployment')
        $fixture.Poller.PSObject.Properties.Remove('eventGridUseManagedIdentity')
        $fixture.Poller.properties.auth.type = 'ServicePrincipal'
        $fixture.Poller.properties.dataType = 'CloudflareV2_CL'
        $fixture.Definition.properties.connectorUiConfig.instructionSteps[0].instructions += New-TestInput 'blobContainerUri'
        $connection = Get-Connections (Invoke-TestGenerator $fixture)
        Assert-Equal @($connection.resources | Where-Object type -eq 'Microsoft.Insights/dataCollectionRules').Count 0
        Assert-Equal $connection.variables.connectorName 'sentinel-connector'
        Assert-Equal $connection.variables.nestedDeploymentName 'CreateDataFlowResources'
        Assert-Equal $connection.variables.blobRaGuid "[[guid(variables('storageAccountName'), variables('blobContainerName'))]"
        Assert-Equal $connection.variables.storageBlobContributorRoleId "[[subscriptionResourceId(parameters('StorageAccountSubscription'), 'Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')]"
        $inner = (Get-OnlyResource $connection 'Microsoft.Resources/deployments').properties.template
        Assert-Equal $inner.resources.Count 7
        Assert-Equal @($inner.resources | Where-Object type -eq 'Microsoft.Resources/deployments').Count 0
    }
    'Installed connection field-type validator accepts output and rejects a string regression' = {
        $package = Invoke-TestGenerator $fixture
        $solutionRoot = Join-Path $fixture.Root 'Solutions\Fixture'
        $packageFolder = Join-Path $solutionRoot 'Package'
        $null = New-Item -ItemType Directory -Path $packageFolder
        $path = Join-Path $packageFolder 'mainTemplate.json'
        $repoRoot = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
        $validator = Join-Path $repoRoot '.script\package-automation\validateFieldTypes.ps1'
        foreach ($expected in @(0, 1)) {
            if ($expected -eq 1) { (Get-Connections $package).parameters.StorageAccountLocation.type = 'string' }
            ConvertTo-Json -InputObject $package -Depth 100 | Set-Content -LiteralPath $path
            $output = & pwsh -NoProfile -File $validator -baseFolderPath $fixture.Root -SolutionPath $solutionRoot 2>&1
            if ($LASTEXITCODE -ne $expected) { throw "Field validator expected exit $expected, got ${LASTEXITCODE}: $($output -join "`n")" }
        }
    }
    'Queue and dead-letter URIs use uri construction and pass the installed ARM-TTK URI check' = {
        $package = Invoke-TestGenerator $fixture
        $connector = Get-OnlyResource (Get-Connections $package) 'Microsoft.OperationalInsights/workspaces/providers/dataConnectors'
        foreach ($entry in @(@('QueueUri', 'queueName'), @('DlqUri', 'dlqName'))) {
            Assert-Equal $connector.properties.request[$entry[0]] `
                "[[uri(concat('https://', variables('storageAccountName'), '.queue.', environment().suffixes.storage, '/'), variables('$($entry[1])'))]"
        }

        $connection = Convert-TestConnectionExpressions (Copy-TestObject (Get-Connections $package))
        $path = Join-Path $fixture.Root 'mainTemplate.json'
        Import-Module (Join-Path $PSScriptRoot '..\tmp\arm-ttk\arm-ttk.psd1') -Scope Local
        # Check both the packaged form that failed integration and the runtime
        # connection template after ARM removes its outer escape bracket.
        foreach ($template in @($package, $connection)) {
            ConvertTo-Json -InputObject $template -Depth 100 | Set-Content -LiteralPath $path
            $errors = @()
            $results = @(Test-AzTemplate -TemplatePath $path -Test 'URIs Should Be Properly Constructed' -ErrorVariable +errors -ErrorAction Continue)
            if ($results.Count -eq 0 -or @($results | Where-Object { -not $_.Passed }).Count -gt 0 -or $errors.Count -gt 0) {
                throw "URI validation failed: $($errors -join "`n")`n$($results | Format-List Name,Passed,Errors | Out-String)"
            }
            Assert-Equal (@($results | Where-Object Name -eq 'URIs Should Be Properly Constructed').Count -gt 0) $true
        }

        # Reproduce the integration defect independently for each property.
        # Keep errors enabled so ARM-TTK can classify the intentional failures.
        $request = (Get-OnlyResource $connection 'Microsoft.OperationalInsights/workspaces/providers/dataConnectors').properties.request
        foreach ($entry in @(@('QueueUri', 'queueName'), @('DlqUri', 'dlqName'))) {
            $valid = $request.($entry[0])
            $request.($entry[0]) = "[concat('https://', variables('storageAccountName'), '.queue.', environment().suffixes.storage, '/', variables('$($entry[1])'))]"
            ConvertTo-Json -InputObject $connection -Depth 100 | Set-Content -LiteralPath $path
            $invalidErrors = @()
            $invalid = @(Test-AzTemplate -TemplatePath $path -Test 'URIs Should Be Properly Constructed' -ErrorVariable +invalidErrors -ErrorAction Continue)
            $uriFailures = @($invalid | Where-Object { -not $_.Passed })
            Assert-Equal (@($uriFailures.Errors | Where-Object {
                $_.FullyQualifiedErrorId -like 'URI.Improperly.Constructed*' -and
                $_.Exception.Message.Contains("Function 'concat' found within '$($entry[0])'")
            }).Count -gt 0) $true
            $request.($entry[0]) = $valid
        }
    }
    'Installed ARM-TTK accepts nested parameter types and inner secure-parameter forwarding' = {
        $package = Invoke-TestGenerator $fixture
        $connection = Convert-TestConnectionExpressions (Copy-TestObject (Get-Connections $package))
        $path = Join-Path $fixture.Root 'mainTemplate.json'
        ConvertTo-Json -InputObject $connection -Depth 100 | Set-Content -LiteralPath $path
        Import-Module (Join-Path $PSScriptRoot '..\tmp\arm-ttk\arm-ttk.psd1')
        $errors = @()
        $results = @(Test-AzTemplate -TemplatePath $path -Test @('Parameter Types Should Be Consistent', 'Secure Params In Nested Deployments') -ErrorVariable +errors -ErrorAction Continue)
        if ($results.Count -eq 0 -or @($results | Where-Object { -not $_.Passed }).Count -gt 0 -or $errors.Count -gt 0) {
            throw "Nested parameter validation failed: $($errors -join "`n")`n$($results | Format-List Name,Passed,Errors | Out-String)"
        }
        Assert-Equal (@($results | Where-Object Name -eq 'Parameter Types Should Be Consistent').Count -gt 0) $true
        # Prove this is checking the real parent/child boundary rather than
        # returning a vacuous pass for the content-template wrapper.
        $storage = Get-OnlyResource $connection 'Microsoft.Resources/deployments'
        $storage.properties.template.parameters.StorageAccountLocation.type = 'string'
        ConvertTo-Json -InputObject $connection -Depth 100 | Set-Content -LiteralPath $path
        # ARM-TTK classifies captured error-stream records. SilentlyContinue
        # suppresses that stream before its harness can classify a failure.
        $invalidErrors = @()
        $invalid = @(Test-AzTemplate -TemplatePath $path -Test 'Parameter Types Should Be Consistent' -ErrorVariable +invalidErrors -ErrorAction Continue)
        $typeFailures = @($invalid | Where-Object { -not $_.Passed })
        if ($typeFailures.Count -eq 0) {
            throw "ARM-TTK did not reject the intentional StorageAccountLocation type mismatch: $($invalid | Format-List Name,Passed,Errors | Out-String)"
        }
        Assert-Equal (@($typeFailures.Errors | Where-Object { $_.FullyQualifiedErrorId -like 'Inconsistent.Parameter*' -and $_.Exception.Message.Contains('StorageAccountLocation') }).Count -gt 0) $true
    }
}

$root = Join-Path ([IO.Path]::GetTempPath()) ('sentinel-per-instance-tests-' + [guid]::NewGuid().ToString('N'))
$failures = 0
$index = 0
try {
    foreach ($test in $tests.GetEnumerator()) {
        $fixture = New-TestFixture (Join-Path $root "case-$index")
        try {
            & $test.Value
            Write-Host "PASS: $($test.Key)"
        }
        catch {
            $failures++
            Write-Host "FAIL: $($test.Key)`n$($_.Exception.Message)`n$($_.ScriptStackTrace)"
        }
        $index++
    }
}
finally {
    if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force }
}
Write-Host "$($tests.Count - $failures)/$($tests.Count) per-instance tests passed."
if ($failures) { throw "$failures per-instance storage regression test(s) failed." }
