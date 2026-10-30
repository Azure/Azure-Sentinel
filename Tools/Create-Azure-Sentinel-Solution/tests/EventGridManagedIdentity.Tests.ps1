#Requires -Version 7.0
<#
.SYNOPSIS
Tests the Event Grid managed-identity ARM template generator without deploying Azure resources.
.DESCRIPTION
Run with:
pwsh -NoProfile -File Tools\Create-Azure-Sentinel-Solution\tests\EventGridManagedIdentity.Tests.ps1

These dependency-free tests assert generated ARM expressions and resource wiring.
They do not evaluate ARM expressions or verify Azure identity/RBAC runtime behavior.
Optional -ConnectorDirectory and -ReferenceTemplatePath inputs accept the generated
GitHubAuditBlobConnector source files and expected mainTemplate.json for comparison.
#>
param(
    [string]$ReferenceTemplatePath,
    [string]$ConnectorDirectory
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\common\storageAccountDeploymentTemplate.ps1')
. (Join-Path $PSScriptRoot '..\common\eventGridManagedIdentityDeploymentTemplate.ps1')
. (Join-Path $PSScriptRoot '..\common\commonFunctions.ps1')

function Assert-Equal($Actual, $Expected) {
    $actualJson = ConvertTo-Json -InputObject $Actual -Depth 100 -Compress
    $expectedJson = ConvertTo-Json -InputObject $Expected -Depth 100 -Compress
    if ($actualJson -cne $expectedJson) {
        throw "Expected: $expectedJson`nActual:   $actualJson"
    }
}

function Assert-Throws([scriptblock]$Action, [string]$Message) {
    try { & $Action }
    catch {
        Assert-Equal $_.Exception.Message $Message
        return
    }
    throw "Expected exception: $Message"
}

function Assert-Equivalent($Actual, $Expected, [string]$Path = '$') {
    try {
        if ($Expected -is [System.Collections.IDictionary]) {
            Assert-Equal @($Actual.Keys | Sort-Object) @($Expected.Keys | Sort-Object)
            foreach ($key in $Expected.Keys) {
                Assert-Equivalent $Actual[$key] $Expected[$key] "$Path.$key"
            }
        }
        elseif ($Expected -is [array]) {
            Assert-Equal $Actual.Count $Expected.Count
            for ($i = 0; $i -lt $Expected.Count; $i++) {
                Assert-Equivalent $Actual[$i] $Expected[$i] "$Path[$i]"
            }
        }
        else {
            Assert-Equal $Actual $Expected
        }
    }
    catch { throw "${Path}: $($_.Exception.Message)" }
}

function Get-TestFixture([bool]$ManagedIdentity, $AdvancedFilters = $null, [bool]$ManagedCollector = $false) {
    # Set-ResourceVariables uses its caller's template and variables, as in production.
    $variables = [ordered]@{}
    $templateContentConnections = [pscustomobject]@{
        properties = [pscustomobject]@{
            mainTemplate = [pscustomobject]@{ variables = $variables }
        }
    }
    Set-ResourceVariables -eventGridUseManagedIdentity $ManagedIdentity -isManagedServicePrincipal $ManagedCollector
    $deployment = Get-StorageAccountDeploymentTemplate `
        -eventGridUseManagedIdentity $ManagedIdentity `
        -resourceVariables $templateContentConnections.properties.mainTemplate.variables `
        -eventGridAdvancedFilters $AdvancedFilters `
        -isManagedServicePrincipal $ManagedCollector
    # Check the serialized contract, not PowerShell dictionary implementation details.
    return ($deployment | ConvertTo-Json -Depth 100 | ConvertFrom-Json -AsHashtable)
}

function Get-OnlyResource($Template, [string]$Type) {
    $matches = @($Template.resources | Where-Object { $_.type -eq $Type })
    Assert-Equal $matches.Count 1
    return $matches[0]
}

function Remove-CollectorRbac($Deployment) {
    $copy = $Deployment | ConvertTo-Json -Depth 100 | ConvertFrom-Json -AsHashtable -Depth 100
    $collectorRoleTypes = @(
        'Microsoft.Storage/storageAccounts/blobServices/containers/providers/roleAssignments',
        'Microsoft.Storage/storageAccounts/queueServices/queues/providers/roleAssignments'
    )
    $copy.properties.template.resources = @(
        $copy.properties.template.resources |
            Where-Object { $_.type -notin $collectorRoleTypes }
    )
    foreach ($name in @(
        'principalId', 'storageBlobReaderRoleId', 'storageQueueContributorRoleId',
        'blobRaGuid', 'notificationQueueRaGuid', 'dlqRaGuid', 'dlqResourceId'
    )) {
        $copy.properties.parameters.Remove($name)
        $copy.properties.template.parameters.Remove($name)
        $copy.properties.template.variables.Remove($name)
    }
    return $copy
}

$tests = [ordered]@{
    'Solution content paths accept existing solution-prefixed references' = {
        $root = Join-Path ([System.IO.Path]::GetTempPath()) "sentinel-solution-path-test-$([guid]::NewGuid().ToString('N'))"
        $solutionRoot = Join-Path $root 'Cloudflare'
        $connector = Join-Path $solutionRoot 'Data Connectors\connector.json'
        try {
            New-Item -ItemType Directory -Path (Split-Path $connector -Parent) -Force | Out-Null
            Set-Content -LiteralPath $connector -Value '{}' -NoNewline
            foreach ($path in @(
                'Data Connectors/connector.json',
                'Cloudflare/Data Connectors/connector.json',
                'Solutions/Cloudflare/Data Connectors/connector.json'
            )) {
                $resolved = Resolve-SolutionContentPath `
                    -SolutionRoot $solutionRoot `
                    -SolutionName 'Cloudflare' `
                    -ContentPath $path `
                    -RequireFile
                Assert-Equal $resolved.RelativePath 'Data Connectors/connector.json'
            }
        }
        finally {
            if (Test-Path $root) {
                Remove-Item -LiteralPath $root -Recurse -Force
            }
        }
    }
    'GitHub polling configuration generates managed-identity delivery with its audit filter' = {
        $repoRoot = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
        $pollingPath = Join-Path $repoRoot 'Solutions\GitHub\Data Connectors\GitHubAuditLogs_AzStorage\PollingConfig.json'
        $polling = Get-Content -LiteralPath $pollingPath -Raw | ConvertFrom-Json -AsHashtable
        Assert-Equal $polling.kind 'StorageAccountBlobContainer'
        Assert-Equal $polling.eventGridUseManagedIdentity $true
        $github = Get-TestFixture $polling.eventGridUseManagedIdentity $polling.eventGridAdvancedFilters
        $event = Get-OnlyResource $github.properties.template 'Microsoft.EventGrid/systemTopics/eventSubscriptions'
        Assert-Equal $event.properties.deliveryWithResourceIdentity.identity.type 'SystemAssigned'
        Assert-Equal $event.properties.filter.advancedFilters $polling.eventGridAdvancedFilters
        Assert-Equal $polling.eventGridAdvancedFilters @(
            [ordered]@{ operatorType = 'StringNotContains'; key = 'subject'; values = @('/_check') }
        )
    }
    'Nested templates evaluate parameters in their own scope' = {
        Assert-Equal $managed.properties.expressionEvaluationOptions.scope 'inner'
        foreach ($child in $children) {
            Assert-Equal $child.properties.expressionEvaluationOptions.scope 'inner'
            Assert-Equal $child.properties.mode 'Incremental'
        }
        foreach ($name in @('StorageAccountLocation', 'blobFolderName', 'eventGridRbacMode')) {
            Assert-Equal $managed.properties.parameters[$name].value "[[parameters('$name')]"
        }
        foreach ($name in @('storageAccountName', 'storageAccountId', 'blobContainerName', 'queueName', 'dlqName', 'EGSystemTopicName', 'EGTopicResourceId', 'EgSubscriptionName')) {
            Assert-Equal $managed.properties.parameters[$name].value "[[variables('$name')]"
            Assert-Equal $inner.variables[$name] "[[parameters('$name')]"
        }
        Assert-Equal $managed.subscriptionId "[[parameters('StorageAccountSubscription')]"
        Assert-Equal $managed.resourceGroup "[[parameters('StorageAccountResourceGroupName')]"
    }
    'Existing topic is read before the inner update; new topic skips reference' = {
        Assert-Equal $managed.properties.parameters.existingSystemTopic.value "[[if(empty(parameters('EGSystemTopicName')), createObject(), reference(variables('EGTopicResourceId'), '2025-02-15', 'Full'))]"
        Assert-Equal $topicDeployment.properties.parameters.existingSystemTopic.value "[[parameters('existingSystemTopic')]"
        Assert-Equal $topic.ContainsKey('condition') $false
        Assert-Equal $topic.name "[[parameters('topicName')]"
    }
    'Existing topic source must match before its identity is updated' = {
        Assert-Equal $managed.properties.parameters.existingSystemTopicMatchesStorageAccount.value "[[if(empty(parameters('EGSystemTopicName')), true(), equals(toLower(reference(variables('EGTopicResourceId'), '2025-02-15', 'Full').properties.source), toLower(variables('storageAccountId'))))]"
        Assert-Equal $inner.parameters.existingSystemTopicMatchesStorageAccount.type 'bool'
        Assert-Equal $inner.parameters.existingSystemTopicMatchesStorageAccount.allowedValues @($true)
        Assert-Equal $topicDeployment.condition "[[parameters('existingSystemTopicMatchesStorageAccount')]"
    }
    'Identity expressions handle missing/null identities and retain user-assigned identities' = {
        Assert-Equal $topicTemplate.variables.existingTopicIdentity "[[if(contains(parameters('existingSystemTopic'), 'identity'), coalesce(parameters('existingSystemTopic').identity, createObject()), createObject())]"
        Assert-Equal $topicTemplate.variables.existingUserAssignedIdentities "[[if(contains(variables('existingTopicIdentity'), 'userAssignedIdentities'), coalesce(variables('existingTopicIdentity').userAssignedIdentities, createObject()), createObject())]"
        Assert-Equal $topicTemplate.variables.topicIdentity "[[if(empty(variables('existingUserAssignedIdentities')), createObject('type', 'SystemAssigned'), createObject('type', 'SystemAssigned, UserAssigned', 'userAssignedIdentities', variables('existingUserAssignedIdentities')))]"
        Assert-Equal $topic.identity "[[variables('topicIdentity')]"
    }
    'Topic update retains supplied tags and storage source' = {
        Assert-Equal $topic.tags "[[if(contains(parameters('existingSystemTopic'), 'tags'), coalesce(parameters('existingSystemTopic').tags, createObject()), createObject())]"
        Assert-Equal $topic.location "[[if(empty(parameters('existingSystemTopic')), parameters('StorageAccountLocation'), parameters('existingSystemTopic').location)]"
        Assert-Equal $topic.properties.source "[[if(empty(parameters('existingSystemTopic')), parameters('sourceId'), parameters('existingSystemTopic').properties.source)]"
        Assert-Equal $topic.properties.topicType "[[if(empty(parameters('existingSystemTopic')), 'microsoft.storage.storageaccounts', parameters('existingSystemTopic').properties.topicType)]"
        Assert-Equal $topicDeployment.properties.parameters.sourceId.value $storageId
    }
    'Sender deployment consumes the completed topic deployment principal output' = {
        Assert-Equal $topicTemplate.outputs.principalId.value "[[reference(resourceId('Microsoft.EventGrid/systemTopics', parameters('topicName')), '2025-02-15', 'Full').identity.principalId]"
        Assert-Equal $senderDeployment.properties.parameters.principalId.value "[[if(equals(parameters('eventGridRbacMode'), 'CreateRoleAssignment'), reference(variables('eventGridTopicDeploymentId'), '2025-04-01').outputs.principalId.value, '')]"
        Assert-Equal $senderDeployment.dependsOn @(
            "[[variables('eventGridTopicDeploymentId')]",
            "[[variables('notificationQueueResourceId')]"
        )
        Assert-Equal $sender.properties.principalId "[[parameters('principalId')]"
    }
    'Sender role is account-scoped and uniquely keyed by scope, principal and role' = {
        Assert-Equal $senderDeployment.properties.parameters.storageAccountResourceId.value $storageId
        Assert-Equal $sender.scope "[[parameters('storageAccountResourceId')]"
        Assert-Equal $sender.properties.principalType 'ServicePrincipal'
        Assert-Equal $senderTemplate.variables.queueMessageSenderRoleId "[[subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'c6a89b2d-59bc-44d0-9896-0f6e12d7b80a')]"
        Assert-Equal $sender.properties.roleDefinitionId "[[variables('queueMessageSenderRoleId')]"
        Assert-Equal $sender.name "[[guid(toLower(parameters('storageAccountResourceId')), toLower(parameters('principalId')), toLower(variables('queueMessageSenderRoleId')))]"
    }
    'RBAC mode allows both choices and defaults only at the outer boundary' = {
        $outerParameter = Get-EventGridRbacModeParameter -IncludeDefault
        Assert-Equal $outerParameter.allowedValues @('CreateRoleAssignment', 'UseExistingRoleAssignment')
        Assert-Equal $outerParameter.defaultValue 'CreateRoleAssignment'
        Assert-Equal $inner.parameters.eventGridRbacMode.allowedValues $outerParameter.allowedValues
        Assert-Equal $inner.parameters.eventGridRbacMode.ContainsKey('defaultValue') $false
        Assert-Equal $senderDeployment.condition "[[equals(parameters('eventGridRbacMode'), 'CreateRoleAssignment')]"
    }
    'Subscription waits for sender creation or topic preparation according to RBAC mode' = {
        Assert-Equal $subscription.dependsOn @(
            "[[if(equals(parameters('eventGridRbacMode'), 'CreateRoleAssignment'), variables('eventGridQueueSenderDeploymentId'), variables('eventGridTopicDeploymentId'))]",
            "[[variables('notificationQueueResourceId')]"
        )
        foreach ($prefix in @('eventGridTopic', 'eventGridQueueSender')) {
            Assert-Equal $inner.variables["${prefix}DeploymentId"] "[[resourceId('Microsoft.Resources/deployments', variables('${prefix}DeploymentName'))]"
        }
        Assert-Equal $topicDeployment.name "[[variables('eventGridTopicDeploymentName')]"
        Assert-Equal $senderDeployment.name "[[variables('eventGridQueueSenderDeploymentName')]"
    }
    'Folder filtering is optional and uses a complete container/blob prefix' = {
        Assert-Equal $managed.properties.parameters.blobFolderName.value "[[parameters('blobFolderName')]"
        Assert-Equal $inner.parameters.blobFolderName.defaultValue ''
        Assert-Equal $subscription.properties.filter.subjectBeginsWith "[[format('{0}/{1}/blobs/{2}', '/blobServices/default/containers', variables('blobContainerName'), if(empty(parameters('blobFolderName')), '', concat(parameters('blobFolderName'),'/')))]"
    }
    'Both collector modes receive least-privilege grants with compatible assignment names' = {
        foreach ($enabled in @($false, $true)) {
            $managedCollector = Get-TestFixture $enabled $null $true
            $servicePrincipalCollector = Get-TestFixture $enabled
            foreach ($fixture in @($managedCollector, $servicePrincipalCollector)) {
                $assignments = @($fixture.properties.template.resources | Where-Object type -like '*/providers/roleAssignments')
                Assert-Equal $assignments.Count 3
                $blobAssignment = @($assignments | Where-Object type -like '*/blobServices/containers/providers/roleAssignments')[0]
                Assert-Equal $blobAssignment.properties.roleDefinitionId "[[variables('storageBlobReaderRoleId')]"
                Assert-Equal $blobAssignment.properties.principalId "[[parameters('principalId')]"
            }
            if ($enabled) {
                foreach ($fixture in @($managedCollector, $servicePrincipalCollector)) {
                    Assert-Equal $fixture.properties.parameters.principalId.value "[[parameters('principalId')]"
                    Assert-Equal $fixture.properties.template.parameters.principalId.type 'securestring'
                    Assert-Equal $fixture.properties.template.variables.blobRaGuid "[[parameters('blobRaGuid')]"
                    Assert-Equal $fixture.properties.parameters.blobRaGuid.value "[[variables('blobRaGuid')]"
                    Assert-Equal $fixture.properties.template.variables.notificationQueueRaGuid "[[parameters('notificationQueueRaGuid')]"
                }
            }
        }
        $variables = [ordered]@{}
        $templateContentConnections = [pscustomobject]@{
            properties = [pscustomobject]@{ mainTemplate = [pscustomobject]@{ variables = $variables } }
        }
        Set-ResourceVariables -eventGridUseManagedIdentity $true -isManagedServicePrincipal $true
        Assert-Equal $variables.storageBlobReaderRoleId `
            "[[subscriptionResourceId(parameters('StorageAccountSubscription'), 'Microsoft.Authorization/roleDefinitions', '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1')]"
        Assert-Equal $variables.blobRaGuid `
            "[[guid(toLower(variables('storageAccountId')), toLower(variables('blobContainerName')), toLower(parameters('principalId')), toLower(variables('storageBlobReaderRoleId')))]"
        Assert-Equal $variables.notificationQueueRaGuid `
            "[[guid(toLower(variables('notificationQueueResourceId')), toLower(parameters('principalId')), toLower(variables('storageQueueContributorRoleId')))]"
        Assert-Equal $variables.dlqRaGuid `
            "[[guid(toLower(variables('dlqResourceId')), toLower(parameters('principalId')), toLower(variables('storageQueueContributorRoleId')))]"
        $variables = [ordered]@{}
        $templateContentConnections = [pscustomobject]@{
            properties = [pscustomobject]@{ mainTemplate = [pscustomobject]@{ variables = $variables } }
        }
        Set-ResourceVariables -eventGridUseManagedIdentity $true
        Assert-Equal $variables.blobRaGuid `
            "[[guid(variables('storageAccountName'), variables('blobContainerName'))]"
        Assert-Equal $variables.notificationQueueRaGuid `
            "[[guid(variables('storageAccountName'), variables('queueName'))]"
        Assert-Equal $variables.dlqRaGuid `
            "[[guid(variables('storageAccountName'), variables('dlqName'))]"
        Assert-Equal $inner.resources.Count 8
        Assert-Equal $inner.parameters.ContainsKey('principalId') $true
    }
    'Subscription uses managed-identity delivery, not the legacy destination property' = {
        Assert-Equal $subscription.properties.ContainsKey('destination') $false
        Assert-Equal $subscription.properties.deliveryWithResourceIdentity.identity.type 'SystemAssigned'
        Assert-Equal $subscription.properties.deliveryWithResourceIdentity.destination.endpointType 'StorageQueue'
        Assert-Equal $subscription.properties.deliveryWithResourceIdentity.destination.properties.resourceId $storageId
        Assert-Equal $subscription.properties.deliveryWithResourceIdentity.destination.properties.queueName "[[variables('queueName')]"
        Assert-Equal $subscription.properties.eventDeliverySchema 'EventGridSchema'
        Assert-Equal @($inner.resources | Where-Object type -eq 'Microsoft.EventGrid/systemTopics').Count 0
        Assert-Equal $children.Count 2
    }
    'Advanced filters survive managed-identity conversion and remain optional' = {
        foreach ($enabled in @($false, $true)) {
            $filtered = Get-TestFixture $enabled $filters
            $event = Get-OnlyResource $filtered.properties.template 'Microsoft.EventGrid/systemTopics/eventSubscriptions'
            Assert-Equal $event.properties.filter.advancedFilters $filters
            Assert-Equal $event.properties.filter.includedEventTypes @('Microsoft.Storage.BlobCreated')
            if (-not $enabled) {
                Assert-Equal $event.properties.filter.subjectBeginsWith "[[format('{0}/{1}', '/blobServices/default/containers', variables('blobContainerName'))]"
            }
            foreach ($emptyFilters in @($null, @())) {
                $unfiltered = Get-TestFixture $enabled $emptyFilters
                $event = Get-OnlyResource $unfiltered.properties.template 'Microsoft.EventGrid/systemTopics/eventSubscriptions'
                Assert-Equal $event.properties.filter.ContainsKey('advancedFilters') $false
            }
        }
    }
    'Disabled feature retains legacy topic and delivery without new deployments or parameters' = {
        $legacy = Get-TestFixture $false
        $legacyTemplate = $legacy.properties.template
        Assert-Equal $legacyTemplate.resources.Count 7
        Assert-Equal @($legacyTemplate.resources | Where-Object type -eq 'Microsoft.Resources/deployments').Count 0
        Assert-Equal $legacy.properties.ContainsKey('expressionEvaluationOptions') $false
        Assert-Equal $legacyTemplate.ContainsKey('parameters') $false
        $legacyTopic = Get-OnlyResource $legacyTemplate 'Microsoft.EventGrid/systemTopics'
        Assert-Equal $legacyTopic.condition "[[empty(parameters('EGSystemTopicName'))]"
        Assert-Equal $legacyTopic.ContainsKey('identity') $false
        $legacyEvent = Get-OnlyResource $legacyTemplate 'Microsoft.EventGrid/systemTopics/eventSubscriptions'
        Assert-Equal $legacyEvent.properties.ContainsKey('deliveryWithResourceIdentity') $false
        Assert-Equal $legacyEvent.properties.destination.properties.resourceId "[[variables('storageAccountId')]"
        Assert-Equal $legacyEvent.dependsOn @("[[format('Microsoft.EventGrid/systemTopics/{0}', variables('EGSystemTopicName'))]")
        $default = Get-StorageAccountDeploymentTemplate | ConvertTo-Json -Depth 100 | ConvertFrom-Json -AsHashtable
        Assert-Equal $default $legacy
    }
    'Missing managed-identity variables fail explicitly' = {
        Assert-Throws { Get-StorageAccountDeploymentTemplate -eventGridUseManagedIdentity $true } `
            'Storage variables are required for managed-identity Event Grid delivery.'
        $incomplete = [ordered]@{}
        foreach ($key in $inner.variables.Keys) { $incomplete[$key] = $inner.variables[$key] }
        $incomplete.Remove('EGTopicResourceId')
        Assert-Throws { Get-StorageAccountDeploymentTemplate -eventGridUseManagedIdentity $true -resourceVariables $incomplete } `
            "Missing storage variable 'EGTopicResourceId' for managed-identity Event Grid delivery."
    }
    'Managed-identity outer resource IDs explicitly select the storage subscription and resource group' = {
        $variables = [ordered]@{}
        $templateContentConnections = [pscustomobject]@{
            properties = [pscustomobject]@{ mainTemplate = [pscustomobject]@{ variables = $variables } }
        }
        Set-ResourceVariables -eventGridUseManagedIdentity $true
        foreach ($name in @('storageAccountId', 'notificationQueueResourceId', 'dlqResourceId', 'EGTopicResourceId', 'EgSubscriptionResourceId', 'nestedDeploymentId')) {
            Assert-Equal $variables[$name].StartsWith("[[resourceId(parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'),") $true
        }
    }
}

if ($ReferenceTemplatePath) {
    $tests['Generated storage deployment matches the supplied GitHub reference'] = {
        $reference = Get-Content -LiteralPath $ReferenceTemplatePath -Raw | ConvertFrom-Json -AsHashtable -Depth 100
        $connections = @($reference.resources | Where-Object { $_.properties.contentKind -eq 'ResourcesDataConnector' })
        Assert-Equal $connections.Count 1
        $referenceDeployment = Get-OnlyResource $connections[0].properties.mainTemplate 'Microsoft.Resources/deployments'
        $referenceSubscription = Get-OnlyResource $referenceDeployment.properties.template 'Microsoft.EventGrid/systemTopics/eventSubscriptions'
        $actual = Get-TestFixture $true $referenceSubscription.properties.filter.advancedFilters $true
        Assert-Equivalent (Remove-CollectorRbac $actual) $referenceDeployment
    }
}

$tests['CCF packaging preserves source content, optional parameters and both collector authentication modes'] = {
    $repoRoot = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
    $sourceDirectory = if ($ConnectorDirectory) { $ConnectorDirectory } else {
        Join-Path $repoRoot 'Solutions\GitHub\Data Connectors\GitHubAuditLogs_AzStorage'
    }
    $fixtureRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("sentinel-blob-packaging-test-" + [guid]::NewGuid().ToString('N'))
    $fixtureSolution = Join-Path $fixtureRoot 'Solutions\GitHub'
    $fixtureConnector = Join-Path $fixtureSolution 'Data Connectors\GitHubAuditLogs_AzStorage'
    try {
        $null = New-Item -ItemType Directory -Path $fixtureConnector
        foreach ($name in @('ConnectorDefinition.json', 'PollingConfig.json', 'DCR.json')) {
            Copy-Item -LiteralPath (Join-Path $sourceDirectory $name) -Destination $fixtureConnector
        }
        Copy-Item -LiteralPath (Join-Path $repoRoot 'Solutions\GitHub\Data Connectors\GitHubAuditLogs_AzStorage\table_GitHubAuditLogsV3.json') -Destination $fixtureConnector
        $sourceDefinition = Get-Content -LiteralPath (Join-Path $fixtureConnector 'ConnectorDefinition.json') -Raw | ConvertFrom-Json -AsHashtable -Depth 100
        $sourceDcr = Get-Content -LiteralPath (Join-Path $fixtureConnector 'DCR.json') -Raw | ConvertFrom-Json -AsHashtable -Depth 100
        if ($ConnectorDirectory) {
            Assert-Equal (($sourceDefinition | ConvertTo-Json -Depth 100 -Compress).Contains('7ae5462d-d9d1-42f6-93ca-198d7b0ca997')) $true
        }
        $pollingPath = Join-Path $fixtureConnector 'PollingConfig.json'
        $polling = Get-Content -LiteralPath $pollingPath -Raw | ConvertFrom-Json -Depth 100
        foreach ($authType in @('ManagedServicePrincipal', 'ServicePrincipal')) {
            $polling.properties.auth.type = $authType
            $polling | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $pollingPath
            . (Join-Path $PSScriptRoot '..\common\commonFunctions.ps1')
            . (Join-Path $PSScriptRoot '..\common\get-ccp-details.ps1')
            . (Join-Path $PSScriptRoot '..\common\createCCPConnector.ps1')
            $data = Get-Content -LiteralPath (Join-Path $repoRoot 'Solutions\GitHub\data\Solution_GitHub.json') -Raw | ConvertFrom-Json
            $data.'Data Connectors' = @('Data Connectors/GitHubAuditLogs_AzStorage/ConnectorDefinition.json')
            $metadata = Get-Content -LiteralPath (Join-Path $repoRoot 'Solutions\GitHub\SolutionMetadata.json') -Raw | ConvertFrom-Json
            $solutionBase = (Join-Path $fixtureRoot 'Solutions') + [System.IO.Path]::DirectorySeparatorChar
            $dict = @(Get-CCP-Dict -dataFileMetadata $data -baseFolderPath $solutionBase -solutionName 'GitHub' -DCFolderName 'Data Connectors')
            Assert-Equal $dict.Count 1
            $tables = @(GetCCPTableFilePaths -existingCCPDict $dict -baseFolderPath $solutionBase -solutionName 'GitHub' -DCFolderName 'Data Connectors')
            createCCPConnectorResources -contentResourceDetails (returnContentResources $data.Version) `
                -dataFileMetadata $data -solutionFileMetadata $metadata -dcFolderName 'Data Connectors' `
                -ccpDict $dict -solutionBasePath $solutionBase -solutionName 'GitHub' -ccpTables $tables -ccpTablesCounter 1
            # Use the V3 serializer's depth to catch nested-template truncation as well as parameter merging.
            $packaged = $global:baseMainTemplate | ConvertTo-Json -Depth 50 -WarningAction Stop | ConvertFrom-Json -AsHashtable -Depth 100
            $connections = @($packaged.resources | Where-Object { $_.properties.contentKind -eq 'ResourcesDataConnector' })
            Assert-Equal $connections.Count 1
            $connectionTemplate = $connections[0].properties.mainTemplate
            $connector = Get-OnlyResource $connectionTemplate 'Microsoft.OperationalInsights/workspaces/providers/dataConnectors'
            Assert-Equal $connector.properties.auth.type $authType
            if ($authType -eq 'ManagedServicePrincipal') {
                Assert-Equal $connector.properties.connectorDefinitionName "[[parameters('connectorDefinitionName')]"
            }
            Assert-Equal $connector.ContainsKey('eventGridUseManagedIdentity') $false
            Assert-Equal $connector.ContainsKey('eventGridAdvancedFilters') $false
            Assert-Equal $connector.properties.response.isGzipCompressed $true
            Assert-Equal $connectionTemplate.parameters.blobFolderName.defaultValue ''
            Assert-Equal $connectionTemplate.parameters.blobFolderName.ContainsKey('minLength') $false
            Assert-Equal $connectionTemplate.parameters.eventGridRbacMode.allowedValues @('CreateRoleAssignment', 'UseExistingRoleAssignment')
            Assert-Equal $connectionTemplate.parameters.eventGridRbacMode.defaultValue 'CreateRoleAssignment'
            Assert-Equal $connectionTemplate.parameters.EGSystemTopicName.defaultValue ''
            Assert-Equal $connectionTemplate.parameters.EGSystemTopicName.ContainsKey('minLength') $false
            $definition = Get-OnlyResource $packaged 'Microsoft.OperationalInsights/workspaces/providers/dataConnectorDefinitions'
            Assert-Equivalent $definition.properties.connectorUiConfig $sourceDefinition.properties.connectorUiConfig
            $definitionTemplate = @($packaged.resources | Where-Object { $_.properties.contentKind -eq 'DataConnector' })[0].properties.mainTemplate
            $dcr = Get-OnlyResource $definitionTemplate 'Microsoft.Insights/dataCollectionRules'
            Assert-Equivalent $dcr.properties.streamDeclarations $sourceDcr.properties.streamDeclarations
            Assert-Equivalent $dcr.properties.dataFlows $sourceDcr.properties.dataFlows
            $deployment = Get-OnlyResource $connectionTemplate 'Microsoft.Resources/deployments'
            Assert-Equal @($deployment.properties.template.resources | Where-Object type -like '*/providers/roleAssignments').Count 3
            if ($ReferenceTemplatePath -and $authType -eq 'ManagedServicePrincipal') {
                $reference = Get-Content -LiteralPath $ReferenceTemplatePath -Raw | ConvertFrom-Json -AsHashtable -Depth 100
                $referenceConnections = @($reference.resources | Where-Object { $_.properties.contentKind -eq 'ResourcesDataConnector' })[0].properties.mainTemplate
                Assert-Equivalent (Remove-CollectorRbac $deployment) (Get-OnlyResource $referenceConnections 'Microsoft.Resources/deployments')
            }
        }
    }
    finally {
        if (Test-Path -LiteralPath $fixtureRoot) { Remove-Item -LiteralPath $fixtureRoot -Recurse -Force }
    }
}

$managed = Get-TestFixture $true $null $true
$inner = $managed.properties.template
$children = @($inner.resources | Where-Object type -eq 'Microsoft.Resources/deployments')
$topicDeployment = @($children | Where-Object name -eq "[[variables('eventGridTopicDeploymentName')]")
$senderDeployment = @($children | Where-Object name -eq "[[variables('eventGridQueueSenderDeploymentName')]")
Assert-Equal $topicDeployment.Count 1
Assert-Equal $senderDeployment.Count 1
$topicDeployment = $topicDeployment[0]
$senderDeployment = $senderDeployment[0]
$topicTemplate = $topicDeployment.properties.template
$senderTemplate = $senderDeployment.properties.template
$topic = Get-OnlyResource $topicTemplate 'Microsoft.EventGrid/systemTopics'
$sender = Get-OnlyResource $senderTemplate 'Microsoft.Authorization/roleAssignments'
$subscription = Get-OnlyResource $inner 'Microsoft.EventGrid/systemTopics/eventSubscriptions'
$storageId = "[[variables('storageAccountId')]"
$filters = @(
    [ordered]@{ operatorType = 'StringEndsWith'; key = 'subject'; values = @('.json.gz') },
    [ordered]@{ operatorType = 'StringIn'; key = 'data.api'; values = @('PutBlob', 'FlushWithClose') }
)
$failures = 0
foreach ($test in $tests.GetEnumerator()) {
    try {
        & $test.Value
        Write-Host "PASS: $($test.Key)"
    }
    catch {
        $failures++
        Write-Host "FAIL: $($test.Key)`n$($_.Exception.Message)"
    }
}
Write-Host "$($tests.Count - $failures)/$($tests.Count) tests passed."
if ($failures) { throw "$failures Event Grid managed-identity regression test(s) failed." }
