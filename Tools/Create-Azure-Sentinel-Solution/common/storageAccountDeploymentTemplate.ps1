
function Set-UriProperty {
    param (
        [string]$propertyName,
        [string]$queueVarName
    )
    $uriValue = "[[uri(concat('https://', variables('storageAccountName'), '.queue.core', '.windows.net', '/'), variables('$queueVarName'))]"

    # Ensure 'request' object exists inside 'properties'
    if (-not ($armResource.properties.PSObject.Properties.Name -contains 'request')) {
        $armResource.properties | Add-Member -MemberType NoteProperty -Name 'request' -Value ([PSCustomObject]@{})
    }
    
    $request = $armResource.properties.request

    # If the property already exists, remove it
    if ($request.PSObject.Properties.Name -contains $propertyName) {
        $request.PSObject.Properties.Remove($propertyName)
    }

    $request | Add-Member -NotePropertyName $propertyName -NotePropertyValue $uriValue -Force
}

function Set-ArmVariable {
    param (
        [hashtable]$variables,
        [string]$name,
        [string]$value
    )

    if (-not $variables.ContainsKey($name)) {
        $variables[$name] = $value
    }
}

function CreateStorageAccountBlobContainerResourceProperties($armResource, $templateContentConnections, $fileType, $instructionParameters = $null) {
    $isManagedServicePrincipal = $armResource.properties.auth.type -eq 'ManagedServicePrincipal'
    $eventGridUseManagedIdentity = $false
    if ($armResource.PSObject.Properties.Name -contains 'eventGridUseManagedIdentity') {
        if ($armResource.eventGridUseManagedIdentity -isnot [bool]) {
            throw 'eventGridUseManagedIdentity must be a boolean.'
        }
        $eventGridUseManagedIdentity = $armResource.eventGridUseManagedIdentity
        $armResource.PSObject.Properties.Remove('eventGridUseManagedIdentity')
    }
    try {
        $kindType = 'StorageAccountBlobContainer'
        $eventGridAdvancedFilters = $null
        $hasEventGridAdvancedFilters = [bool]($armResource.PSObject.Properties.Name -contains "eventGridAdvancedFilters")
        if ($hasEventGridAdvancedFilters) {
            $eventGridAdvancedFilters = $armResource.eventGridAdvancedFilters
            # This is generator metadata, not a valid data connector ARM property.
            $armResource.PSObject.Properties.Remove("eventGridAdvancedFilters")
        }

        ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties -propertyName 'dataType' -isInnerObject $false -innerObjectName $null -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

        ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $true -propertyObject $armResource.properties -propertyName 'auth' -isInnerObject $false -innerObjectName $null -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

        ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.auth -propertyName 'type' -isInnerObject $true -innerObjectName 'auth' -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

        ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $true -propertyObject $armResource.properties -propertyName 'dcrConfig' -isInnerObject $false -innerObjectName $null -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

        if ($isManagedServicePrincipal) {
            $armResource.properties.connectorDefinitionName = "[[parameters('connectorDefinitionName')]"
        }

        $hasDependsOn = [bool]($armResource.PSobject.Properties.name -match "dependsOn")
        if (!$hasDependsOn) {
            $armResource | Add-Member -NotePropertyName "dependsOn" -NotePropertyValue @( "[[variables('nestedDeploymentId')]")
        }

        Set-UriProperty -propertyName "QueueUri" -queueVarName "queueName"
        Set-UriProperty -propertyName "DlqUri" -queueVarName "dlqName"

        $hasVariables = [bool]($templateContentConnections.properties.mainTemplate.PSobject.Properties.name -match "variables")
        if (!$hasVariables) {
            $templateContentConnections.properties.mainTemplate | Add-Member -NotePropertyName "variables" -NotePropertyValue @{}
        }

        Set-ResourceVariables -eventGridUseManagedIdentity $eventGridUseManagedIdentity -isManagedServicePrincipal $isManagedServicePrincipal
        if ($eventGridUseManagedIdentity) {
            . (Join-Path $PSScriptRoot 'eventGridManagedIdentityDeploymentTemplate.ps1')
            # Keep UI-derived parameters in sync so the final merge cannot restore a required folder.
            foreach ($parameterSet in @($templateContentConnections.properties.mainTemplate.parameters, $instructionParameters)) {
                if ($null -eq $parameterSet) { continue }
                $parameterSet | Add-Member -NotePropertyName 'StorageAccountLocation' -NotePropertyValue ([PSCustomObject]@{
                    type = 'string'
                    defaultValue = 'StorageAccountLocation'
                }) -Force
                $parameterSet | Add-Member -NotePropertyName 'eventGridRbacMode' -NotePropertyValue (Get-EventGridRbacModeParameter -IncludeDefault) -Force
                $parameterSet | Add-Member -NotePropertyName 'blobFolderName' -NotePropertyValue ([PSCustomObject]@{
                    type = 'string'
                    defaultValue = ''
                }) -Force
            }
        }
        $templateContentConnections.properties.mainTemplate.resources += Get-StorageAccountDeploymentTemplate -eventGridAdvancedFilters $eventGridAdvancedFilters -eventGridUseManagedIdentity $eventGridUseManagedIdentity -resourceVariables $templateContentConnections.properties.mainTemplate.variables -isManagedServicePrincipal $isManagedServicePrincipal
    }
    catch {
        if ($eventGridUseManagedIdentity -or $isManagedServicePrincipal) { throw }
        Write-Host "Error in CreateStorageAccountBlobContainerResourceProperties function. Error Details $_"
    }
}

function Get-StorageAccountDeploymentTemplate {
    param (
        [object]$eventGridAdvancedFilters = $null,
        [bool]$eventGridUseManagedIdentity = $false,
        [System.Collections.IDictionary]$resourceVariables = $null,
        [bool]$isManagedServicePrincipal = $false
    )

        $storageDeploymentTemplate = [ordered]@{
            type           = "Microsoft.Resources/deployments"
            apiVersion     = "2021-04-01"
            name           = "[[variables('nestedDeploymentName')]"
            properties     = [ordered]@{
                mode     = "Incremental"
                template = [ordered]@{
                    '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#"
                    contentVersion = "1.0.0.0"
                    resources      = @(
                        [ordered]@{
                            type       = "Microsoft.Storage/storageAccounts/queueServices/queues"
                            apiVersion = "2021-04-01"
                            name       = "[[concat(variables('storageAccountName'), '/default/', variables('queueName'))]"
                            dependsOn  = @()
                            properties = @{}
                        },
                        [ordered]@{
                            type       = "Microsoft.Storage/storageAccounts/queueServices/queues"
                            apiVersion = "2021-04-01"
                            name       = "[[concat(variables('storageAccountName'), '/default/', variables('dlqName'))]"
                            dependsOn  = @()
                            properties = @{}
                        },
                        [ordered]@{
                            type       = "Microsoft.EventGrid/systemTopics"
                            apiVersion = "2022-06-15"
                            name       = "[[variables('EGSystemTopicName')]"
                            location   = "[[parameters('StorageAccountLocation')]"
                            properties = [ordered]@{
                                source            = "[[variables('storageAccountId')]"
                                topicType         = "microsoft.storage.storageaccounts"
                            }
                            condition  = "[[empty(parameters('EGSystemTopicName'))]"
                        },
                        [ordered]@{
                            type       = "Microsoft.EventGrid/systemTopics/eventSubscriptions"
                            apiVersion = "2023-12-15-preview"
                            name       = "[[format('{0}/{1}', variables('EGSystemTopicName'), variables('EgSubscriptionName'))]"
                            dependsOn  = @(
                                "[[format('Microsoft.EventGrid/systemTopics/{0}', variables('EGSystemTopicName'))]"
                            )
                            properties = @{
                                destination = [ordered]@{
                                    endpointType = "StorageQueue"
                                    properties   = [ordered]@{
                                        queueName  = "[[variables('queueName')]"
                                        resourceId = "[[variables('storageAccountId')]"
                                    }
                                }
                                filter      = [ordered]@{
                                    includedEventTypes = @("Microsoft.Storage.BlobCreated")
                                    subjectBeginsWith  = "[[format('{0}/{1}', '/blobServices/default/containers', variables('blobContainerName'))]"
                                }
                            }
                        },
                        [ordered]@{
                            type       = "Microsoft.Storage/storageAccounts/blobServices/containers/providers/roleAssignments"
                            apiVersion = "2018-01-01-preview"
                            name       = "[[concat(variables('storageAccountName'), '/default/', variables('blobContainerName'), '/Microsoft.Authorization/', variables('blobRaGuid'))]"
                            properties = [ordered]@{
                                roleDefinitionId = "[[variables('storageBlobReaderRoleId')]"
                                principalId      = "[[parameters('principalId')]"
                            }
                        },
                        [ordered]@{
                            type       = "Microsoft.Storage/storageAccounts/queueServices/queues/providers/roleAssignments"
                            apiVersion = "2018-01-01-preview"
                            name       = "[[concat(variables('storageAccountName'), '/default/', variables('queueName'), '/Microsoft.Authorization/',  variables('notificationQueueRaGuid'))]"
                            dependsOn  = @(
                                "[[variables('notificationQueueResourceId')]"
                            )
                            properties = [ordered]@{
                                roleDefinitionId = "[[variables('storageQueueContributorRoleId')]"
                                principalId      = "[[parameters('principalId')]"
                            }
                        },
                        [ordered]@{
                            type       = "Microsoft.Storage/storageAccounts/queueServices/queues/providers/roleAssignments"
                            apiVersion = "2018-01-01-preview"
                            name       = "[[concat(variables('storageAccountName'), '/default/', variables('dlqName'), '/Microsoft.Authorization/', variables('dlqRaGuid'))]"
                            dependsOn  = @(
                                "[[variables('dlqResourceId')]"
                            )
                            properties = [ordered]@{
                                roleDefinitionId = "[[variables('storageQueueContributorRoleId')]"
                                principalId      = "[[parameters('principalId')]"
                            }
                        }
                    )
                }
            }
            subscriptionId = "[[parameters('StorageAccountSubscription')]"
            resourceGroup  = "[[parameters('StorageAccountResourceGroupName')]"
        }

        $hasAdvancedFilters = $false
        if ($null -ne $eventGridAdvancedFilters) {
            if ($eventGridAdvancedFilters -is [System.Array]) {
                $hasAdvancedFilters = $eventGridAdvancedFilters.Count -gt 0
            }
            else {
                $hasAdvancedFilters = $true
            }
        }

        if ($hasAdvancedFilters) {
            $eventSubscriptionResource = $storageDeploymentTemplate.properties.template.resources |
                Where-Object { $_.type -eq "Microsoft.EventGrid/systemTopics/eventSubscriptions" } |
                Select-Object -First 1

            if ($null -ne $eventSubscriptionResource) {
                $eventSubscriptionResource.properties.filter["advancedFilters"] = $eventGridAdvancedFilters
            }
        }

        if ($eventGridUseManagedIdentity) {
            if ($null -eq $resourceVariables) {
                throw 'Storage variables are required for managed-identity Event Grid delivery.'
            }
            . (Join-Path $PSScriptRoot 'eventGridManagedIdentityDeploymentTemplate.ps1')
            $storageDeploymentTemplate.apiVersion = '2025-04-01'
            # An outer-evaluated template would evaluate the child deployments' parameter expressions too early.
            $storageDeploymentTemplate.properties['expressionEvaluationOptions'] = @{ scope = 'inner' }
            $storageDeploymentTemplate.properties['parameters'] = [ordered]@{}
            $storageDeploymentTemplate.properties.template['parameters'] = [ordered]@{}
            foreach ($parameterName in @('StorageAccountLocation', 'blobFolderName', 'eventGridRbacMode')) {
                $storageDeploymentTemplate.properties.parameters[$parameterName] = @{
                    value = "[[parameters('$parameterName')]"
                }
                $storageDeploymentTemplate.properties.template.parameters[$parameterName] = @{ type = 'string' }
            }
            $storageDeploymentTemplate.properties.template.parameters['blobFolderName']['defaultValue'] = ''
            $storageDeploymentTemplate.properties.template.parameters['eventGridRbacMode'] = Get-EventGridRbacModeParameter
            # Snapshot and validate the existing topic before any nested deployment updates it.
            $storageDeploymentTemplate.properties.parameters['existingSystemTopic'] = @{
                value = "[[if(empty(parameters('EGSystemTopicName')), createObject(), reference(variables('EGTopicResourceId'), '2025-02-15', 'Full'))]"
            }
            $storageDeploymentTemplate.properties.template.parameters['existingSystemTopic'] = @{ type = 'object' }
            $storageDeploymentTemplate.properties.parameters['existingSystemTopicMatchesStorageAccount'] = @{
                value = "[[if(empty(parameters('EGSystemTopicName')), true(), equals(toLower(reference(variables('EGTopicResourceId'), '2025-02-15', 'Full').properties.source), toLower(variables('storageAccountId'))))]"
            }
            $storageDeploymentTemplate.properties.template.parameters['existingSystemTopicMatchesStorageAccount'] = @{
                type = 'bool'
                allowedValues = @($true)
                metadata = @{
                    description = 'The existing Event Grid system topic must use the selected storage account as its source.'
                }
            }
            $storageDeploymentTemplate.properties.template['variables'] = [ordered]@{}
            $storageVariableNames = @(
                'storageAccountName', 'storageAccountId', 'blobContainerName',
                'queueName', 'dlqName', 'EGSystemTopicName', 'EGTopicResourceId', 'EgSubscriptionName',
                'storageBlobReaderRoleId', 'storageQueueContributorRoleId',
                'blobRaGuid', 'notificationQueueRaGuid', 'dlqRaGuid', 'dlqResourceId'
            )
            $storageDeploymentTemplate.properties.parameters['principalId'] = @{ value = "[[parameters('principalId')]" }
            $storageDeploymentTemplate.properties.template.parameters['principalId'] = @{ type = 'securestring' }
            foreach ($name in $storageVariableNames) {
                if (-not $resourceVariables.Contains($name)) {
                    throw "Missing storage variable '$name' for managed-identity Event Grid delivery."
                }
                $storageDeploymentTemplate.properties.parameters[$name] = @{ value = "[[variables('$name')]" }
                $storageDeploymentTemplate.properties.template.parameters[$name] = @{ type = 'string' }
                $storageDeploymentTemplate.properties.template.variables[$name] = "[[parameters('$name')]"
            }
            $storageDeploymentTemplate.properties.template.variables['notificationQueueResourceId'] = "[[resourceId('Microsoft.Storage/storageAccounts/queueServices/queues', variables('storageAccountName'), 'default', variables('queueName'))]"
            $storageDeploymentTemplate.properties.template.variables['eventGridTopicDeploymentName'] = "[[concat('PrepareEventGridTopic-', uniqueString(variables('EGTopicResourceId')))]"
            $storageDeploymentTemplate.properties.template.variables['eventGridTopicDeploymentId'] = "[[resourceId('Microsoft.Resources/deployments', variables('eventGridTopicDeploymentName'))]"
            $storageDeploymentTemplate.properties.template.variables['eventGridQueueSenderDeploymentName'] = "[[concat('EventGridQueueSender-', uniqueString(variables('EGTopicResourceId'), variables('queueName')))]"
            $storageDeploymentTemplate.properties.template.variables['eventGridQueueSenderDeploymentId'] = "[[resourceId('Microsoft.Resources/deployments', variables('eventGridQueueSenderDeploymentName'))]"
            $eventSubscriptionResource = $storageDeploymentTemplate.properties.template.resources |
                Where-Object { $_.type -eq 'Microsoft.EventGrid/systemTopics/eventSubscriptions' } |
                Select-Object -First 1
            $eventSubscriptionResource.apiVersion = '2025-02-15'
            $destination = $eventSubscriptionResource.properties.destination
            $destination.properties.resourceId = "[[variables('storageAccountId')]"
            $eventSubscriptionResource.properties.filter.subjectBeginsWith = "[[format('{0}/{1}/blobs/{2}', '/blobServices/default/containers', variables('blobContainerName'), if(empty(parameters('blobFolderName')), '', concat(parameters('blobFolderName'),'/')))]"
            $eventSubscriptionResource.properties = [ordered]@{
                deliveryWithResourceIdentity = [ordered]@{
                    identity = @{ type = 'SystemAssigned' }
                    destination = $destination
                }
                filter = $eventSubscriptionResource.properties.filter
                eventDeliverySchema = 'EventGridSchema'
            }
            $eventSubscriptionResource.dependsOn = @(
                "[[if(equals(parameters('eventGridRbacMode'), 'CreateRoleAssignment'), variables('eventGridQueueSenderDeploymentId'), variables('eventGridTopicDeploymentId'))]",
                "[[variables('notificationQueueResourceId')]"
            )
            $storageDeploymentTemplate.properties.template.resources = @(
                foreach ($resource in $storageDeploymentTemplate.properties.template.resources) {
                    if ($resource.type -eq 'Microsoft.EventGrid/systemTopics') {
                        Get-EventGridManagedIdentityDeployments
                    } else {
                        if ($resource.type -eq 'Microsoft.Storage/storageAccounts/queueServices/queues') {
                            $resource.apiVersion = '2025-06-01'
                        }
                        $resource
                    }
                }
            )
        }

        return $storageDeploymentTemplate
}

function Set-ResourceVariables {
    param(
        [bool]$eventGridUseManagedIdentity = $false,
        [bool]$isManagedServicePrincipal = $false
    )

    try {
        # Initialize variables hashtable if not already done
        if (-not $variables) { $variables = [ordered]@{} }

        $connectorName = "sentinel-connector"
        $variables["_dataConnectorContentIdConnections$global:connectorCounter"] = "[variables('_dataConnectorContentIdConnections$global:connectorCounter')]"
        $variables["connectorName"] = "$connectorName"
        $variables["blobContainerUriPart"] = "[concat('.blob.core', '.windows.net')]"
        $variables["storageAccountName"] = "[[split(split(parameters('blobContainerUri'), 'https://')[1], variables('blobContainerUriPart'))[0]]"
        $variables["blobContainerName"] = "[[split(split(parameters('blobContainerUri'), concat(variables('blobContainerUriPart'), '/'))[1], '/')[0]]"
        $variables["queueName"] = "[[concat(variables('connectorName'), '-notification')]"
        $variables["dlqName"] = "[[concat(variables('connectorName'), '-dlq')]"
        $variables["storageAccountId"] = "[[resourceId(parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts', variables('storageAccountName'))]"
        $variables["notificationQueueResourceId"] = "[[resourceId(parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts/queueServices/queues', variables('storageAccountName'), 'default', variables('queueName'))]"
        $variables["dlqResourceId"] = "[[resourceId(parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts/queueServices/queues', variables('storageAccountName'), 'default', variables('dlqName'))]"
        $variables["EGSystemTopicDefaultName"] = "[[format('eg-system-topic-{0}-{1}', variables('connectorName'), parameters('innerWorkspace'))]"
        $variables["EGSystemTopicName"] = "[[if(empty(parameters('EGSystemTopicName')), variables('EGSystemTopicDefaultName'), parameters('EGSystemTopicName'))]"
        $variables["EGTopicResourceId"] = "[[resourceId(parameters('StorageAccountResourceGroupName'), 'Microsoft.EventGrid/systemTopics', variables('EGSystemTopicName'))]"
        $variables["EgSubscriptionName"] = "[[format('{0}-{1}', variables('connectorName'), 'blobcreatedevents')]"
        $variables["EgSubscriptionResourceId"] = "[[resourceId(parameters('StorageAccountResourceGroupName'), 'Microsoft.EventGrid/systemTopics/eventSubscriptions', variables('EGSystemTopicName'), variables('EgSubscriptionName'))]"
        $variables["storageBlobReaderRoleId"] = "[[subscriptionResourceId(parameters('StorageAccountSubscription'), 'Microsoft.Authorization/roleDefinitions', '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1')]"
        $variables["storageQueueContributorRoleId"] = "[[subscriptionResourceId(parameters('StorageAccountSubscription'), 'Microsoft.Authorization/roleDefinitions', '974c5e8b-45b9-4653-ba55-5f855dd0fb88')]"
        if ($isManagedServicePrincipal) {
            $variables["blobRaGuid"] = "[[guid(toLower(variables('storageAccountId')), toLower(variables('blobContainerName')), toLower(parameters('principalId')), toLower(variables('storageBlobReaderRoleId')))]"
            $variables["notificationQueueRaGuid"] = "[[guid(toLower(variables('notificationQueueResourceId')), toLower(parameters('principalId')), toLower(variables('storageQueueContributorRoleId')))]"
            $variables["dlqRaGuid"] = "[[guid(toLower(variables('dlqResourceId')), toLower(parameters('principalId')), toLower(variables('storageQueueContributorRoleId')))]"
        }
        else {
            # Preserve existing assignment IDs for ServicePrincipal connectors.
            $variables["blobRaGuid"] = "[[guid(variables('storageAccountName'), variables('blobContainerName'))]"
            $variables["notificationQueueRaGuid"] = "[[guid(variables('storageAccountName'), variables('queueName'))]"
            $variables["dlqRaGuid"] = "[[guid(variables('storageAccountName'), variables('dlqName'))]"
        }
        $variables["blobRoleAssignmentResourceId"] = "[[resourceId(parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts/blobServices/containers/providers/roleAssignments', variables('storageAccountName'), 'default', variables('blobContainerName'), 'Microsoft.Authorization', variables('blobRaGuid'))]"
        $variables["notificationQueueRoleAssignmentResourceId"] = "[[resourceId(parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts/queueServices/queues/providers/roleAssignments', variables('storageAccountName'), 'default', variables('queueName'), 'Microsoft.Authorization', variables('notificationQueueRaGuid'))]"
        $variables["dlqRoleAssignmentResourceId"] = "[[resourceId(parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts/queueServices/queues/providers/roleAssignments', variables('storageAccountName'), 'default', variables('dlqName'), 'Microsoft.Authorization', variables('dlqRaGuid'))]"
        $variables["nestedDeploymentName"] = "CreateDataFlowResources"
        $variables["nestedDeploymentId"] = "[[resourceId(parameters('StorageAccountResourceGroupName'), 'Microsoft.Resources/deployments', variables('nestedDeploymentName'))]"

        if ($eventGridUseManagedIdentity) {
            $variables['storageAccountId'] = "[[resourceId(parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts', variables('storageAccountName'))]"
            $variables['notificationQueueResourceId'] = "[[resourceId(parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts/queueServices/queues', variables('storageAccountName'), 'default', variables('queueName'))]"
            $variables['dlqResourceId'] = "[[resourceId(parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts/queueServices/queues', variables('storageAccountName'), 'default', variables('dlqName'))]"
            $variables['EGTopicResourceId'] = "[[resourceId(parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'), 'Microsoft.EventGrid/systemTopics', variables('EGSystemTopicName'))]"
            $variables['EgSubscriptionResourceId'] = "[[resourceId(parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'), 'Microsoft.EventGrid/systemTopics/eventSubscriptions', variables('EGSystemTopicName'), variables('EgSubscriptionName'))]"
            $variables['nestedDeploymentId'] = "[[resourceId(parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'), 'Microsoft.Resources/deployments', variables('nestedDeploymentName'))]"
        }

        $templateContentConnections.properties.mainTemplate.variables = $variables
    }
    catch {
        Write-Host "Error in Set-ResourceVariables function: $_"
        exit 1
    }
}