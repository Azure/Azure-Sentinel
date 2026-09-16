#Requires -Version 7.0
<#
.SYNOPSIS
Tests the Event Grid managed-identity ARM template generator without deploying Azure resources.
.DESCRIPTION
Run with:
pwsh -NoProfile -File Tools\Create-Azure-Sentinel-Solution\tests\EventGridManagedIdentity.Tests.ps1

These dependency-free tests assert generated ARM expressions and resource wiring.
They do not evaluate ARM expressions or verify Azure identity/RBAC runtime behavior.
#>
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\common\storageAccountDeploymentTemplate.ps1')
. (Join-Path $PSScriptRoot '..\common\eventGridManagedIdentityDeploymentTemplate.ps1')

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

function Get-TestFixture([bool]$ManagedIdentity, $AdvancedFilters = $null) {
    # Set-ResourceVariables uses its caller's template and variables, as in production.
    $variables = [ordered]@{}
    $templateContentConnections = [pscustomobject]@{
        properties = [pscustomobject]@{
            mainTemplate = [pscustomobject]@{ variables = $variables }
        }
    }
    Set-ResourceVariables -eventGridUseManagedIdentity $ManagedIdentity
    $deployment = Get-StorageAccountDeploymentTemplate `
        -eventGridUseManagedIdentity $ManagedIdentity `
        -resourceVariables $templateContentConnections.properties.mainTemplate.variables `
        -eventGridAdvancedFilters $AdvancedFilters
    # Check the serialized contract, not PowerShell dictionary implementation details.
    return ($deployment | ConvertTo-Json -Depth 100 | ConvertFrom-Json -AsHashtable)
}

function Get-OnlyResource($Template, [string]$Type) {
    $matches = @($Template.resources | Where-Object { $_.type -eq $Type })
    Assert-Equal $matches.Count 1
    return $matches[0]
}

$tests = [ordered]@{
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
        foreach ($name in $inner.parameters.Keys) {
            Assert-Equal $managed.properties.parameters[$name].value "[[parameters('$name')]"
        }
        Assert-Equal $managed.subscriptionId "[[parameters('StorageAccountSubscription')]"
        Assert-Equal $managed.resourceGroup "[[parameters('StorageAccountResourceGroupName')]"
    }
    'Existing topic is read before the inner update; new topic skips reference' = {
        Assert-Equal $topicDeployment.properties.parameters.existingTopic.value "[[if(empty(parameters('EGSystemTopicName')), createObject(), reference(resourceId(parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'), 'Microsoft.EventGrid/systemTopics', variables('EGSystemTopicName')), '2025-02-15', 'Full'))]"
        Assert-Equal $topic.ContainsKey('condition') $false
        Assert-Equal $inner.variables.EGSystemTopicName "[[if(empty(parameters('EGSystemTopicName')), variables('EGSystemTopicDefaultName'), parameters('EGSystemTopicName'))]"
        Assert-Equal $topic.name "[[parameters('topicName')]"
    }
    'Identity expressions handle missing/null identities and retain user-assigned identities' = {
        Assert-Equal $topicTemplate.variables.existingIdentity "[[if(contains(parameters('existingTopic'), 'identity'), coalesce(parameters('existingTopic').identity, createObject()), createObject())]"
        Assert-Equal $topicTemplate.variables.userAssignedIdentities "[[if(contains(variables('existingIdentity'), 'userAssignedIdentities'), coalesce(variables('existingIdentity').userAssignedIdentities, createObject()), createObject())]"
        Assert-Equal $topicTemplate.variables.topicIdentity "[[if(empty(variables('userAssignedIdentities')), createObject('type', 'SystemAssigned'), createObject('type', 'SystemAssigned, UserAssigned', 'userAssignedIdentities', variables('userAssignedIdentities')))]"
        Assert-Equal $topic.identity "[[variables('topicIdentity')]"
    }
    'Topic update retains supplied tags and storage source' = {
        Assert-Equal $topic.tags "[[if(contains(parameters('existingTopic'), 'tags'), coalesce(parameters('existingTopic').tags, createObject()), createObject())]"
        Assert-Equal $topic.properties.source "[[parameters('sourceId')]"
        Assert-Equal $topic.properties.topicType 'microsoft.storage.storageaccounts'
        Assert-Equal $topicDeployment.properties.parameters.sourceId.value $storageId
    }
    'Sender deployment consumes the completed topic deployment principal output' = {
        Assert-Equal $topicTemplate.outputs.principalId.value "[[reference(resourceId('Microsoft.EventGrid/systemTopics', parameters('topicName')), '2025-02-15', 'Full').identity.principalId]"
        Assert-Equal $senderDeployment.properties.parameters.principalId.value "[[reference(variables('eventGridTopicDeploymentId'), '2025-04-01').outputs.principalId.value]"
        Assert-Equal $senderDeployment.dependsOn @(
            "[[variables('eventGridTopicDeploymentId')]",
            "[[resourceId(parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts/queueServices/queues', variables('storageAccountName'), 'default', variables('queueName'))]"
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
            Assert-Equal $inner.variables["${prefix}DeploymentId"] "[[resourceId(parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'), 'Microsoft.Resources/deployments', variables('${prefix}DeploymentName'))]"
        }
        Assert-Equal $topicDeployment.name "[[variables('eventGridTopicDeploymentName')]"
        Assert-Equal $senderDeployment.name "[[variables('eventGridQueueSenderDeploymentName')]"
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
            Assert-Equal $event.properties.filter.subjectBeginsWith "[[format('{0}/{1}', '/blobServices/default/containers', variables('blobContainerName'))]"
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
        $incomplete.Remove('eventGridTopicDeploymentId')
        Assert-Throws { Get-StorageAccountDeploymentTemplate -eventGridUseManagedIdentity $true -resourceVariables $incomplete } `
            "Missing storage variable 'eventGridTopicDeploymentId' for managed-identity Event Grid delivery."
    }
}

$managed = Get-TestFixture $true
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
$storageId = "[[resourceId(parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts', variables('storageAccountName'))]"
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
