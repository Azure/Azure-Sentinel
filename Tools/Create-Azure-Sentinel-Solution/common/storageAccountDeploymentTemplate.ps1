
function Set-UriProperty {
    param (
        [string]$propertyName,
        [string]$queueVarName
    )

    $uriValue = "[[concat('https://', variables('storageAccountName'), '.queue.core.windows.net/', variables('$queueVarName'))]"
    $props = $armResource.properties.request.PSObject.Properties

    if ($props.Name -contains $propertyName) {
        $props.Remove($propertyName)
    }

    $armResource.properties.request | Add-Member -NotePropertyName $propertyName -NotePropertyValue $uriValue -Force
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

function CreateStorageAccountBlobContainerResourceProperties($armResource, $templateContentConnections, $fileType) {
    $kindType = 'StorageAccountBlobContainer'
    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties -propertyName 'dataType' -isInnerObject $false -innerObjectName $null -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $true -propertyObject $armResource.properties -propertyName 'auth' -isInnerObject $false -innerObjectName $null -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $false -propertyObject $armResource.properties.auth -propertyName 'type' -isInnerObject $true -innerObjectName 'auth' -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

    ProcessPropertyPlaceholders -armResource $armResource -templateContentConnections $templateContentConnections -isOnlyObjectCheck $true -propertyObject $armResource.properties -propertyName 'dcrConfig' -isInnerObject $false -innerObjectName $null -kindType $kindType -isSecret $true -isRequired $true -fileType $fileType -minLength 3 -isCreateArray $false

    $hasDependsOn = [bool]($armResource.PSobject.Properties.name -match "dependsOn")
    if (!$hasDependsOn) {
        $armResource | Add-Member -NotePropertyName "dependsOn" -NotePropertyValue @( "[[variables('nestedDeploymentId')]")
    }

    Set-UriProperty -propertyName "QueueUri" -queueVarName "queueName"
    Set-UriProperty -propertyName "DlqUri" -queueVarName "dlqName"

    $templateContentConnections.properties.variables = Set-ResourceVariables 
}

function Get-StorageAccountDeploymentTemplate {
    try {
        return @{
            type           = "Microsoft.Resources/deployments"
            apiVersion     = "2021-04-01"
            name           = "[[variables('nestedDeploymentName')]"
            properties     = @{
                mode     = "Incremental"
                template = @{
                    '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#"
                    contentVersion = "1.0.0.0"
                    resources      = @(
                        @{
                            type       = "Microsoft.Storage/storageAccounts/queueServices/queues"
                            apiVersion = "2021-04-01"
                            name       = "[[concat(variables('storageAccountName'), '/default/', variables('queueName'))]"
                            dependsOn  = @()
                            properties = @{}
                        },
                        @{
                            type       = "Microsoft.Storage/storageAccounts/queueServices/queues"
                            apiVersion = "2021-04-01"
                            name       = "[[concat(variables('storageAccountName'), '/default/', variables('dlqName'))]"
                            dependsOn  = @()
                            properties = @{}
                        },
                        @{
                            type       = "Microsoft.EventGrid/systemTopics"
                            apiVersion = "2022-06-15"
                            name       = "[[variables('EGSystemTopicName')]"
                            location   = "[[parameters('StorageAccountLocation')]"
                            properties = @{
                                provisioningState = "Succeeded"
                                source            = "[[variables('storageAccountId')]"
                                topicType         = "microsoft.storage.storageaccounts"
                                metricResourceId  = "0cefe8d9-3269-4f68-a44e-46a4fc26e4a9"
                            }
                            condition  = "[[empty(parameters('EGSystemTopicName'))]"
                        },
                        @{
                            type       = "Microsoft.EventGrid/systemTopics/eventSubscriptions"
                            apiVersion = "2023-12-15-preview"
                            name       = "[[format('{0}/{1}', variables('EGSystemTopicName'), variables('EgSubscriptionName'))]"
                            dependsOn  = @(
                                "[[variables('EGTopicResourceId')]",
                                "[[variables('notificationQueueResourceId')]"
                            )
                            properties = @{
                                destination = @{
                                    endpointType = "StorageQueue"
                                    properties   = @{
                                        queueName  = "[[variables('queueName')]"
                                        resourceId = "[[variables('storageAccountId')]"
                                    }
                                }
                                filter      = @{
                                    includedEventTypes = @("Microsoft.Storage.BlobCreated")
                                    subjectBeginsWith  = "[[format('{0}/{1}', '/blobServices/default/containers', variables('blobContainerName'))]"
                                }
                            }
                        },
                        @{
                            type       = "Microsoft.Storage/storageAccounts/blobServices/containers/providers/roleAssignments"
                            apiVersion = "2018-01-01-preview"
                            name       = "[[concat(variables('storageAccountName'), '/default/', variables('blobContainerName'), '/Microsoft.Authorization/', variables('blobRaGuid'))]"
                            properties = @{
                                roleDefinitionId = "[[variables('storageBlobContributorRoleId')]"
                                principalId      = "[[parameters('principalId')]"
                            }
                        },
                        @{
                            type       = "Microsoft.Storage/storageAccounts/queueServices/queues/providers/roleAssignments"
                            apiVersion = "2018-01-01-preview"
                            name       = "[[concat(variables('storageAccountName'), '/default/', variables('queueName'), '/Microsoft.Authorization/',  variables('notificationQueueRaGuid'))]"
                            dependsOn  = @(
                                "[[variables('notificationQueueResourceId')]"
                            )
                            properties = @{
                                roleDefinitionId = "[[variables('storageQueueContributorRoleId')]"
                                principalId      = "[[parameters('principalId')]"
                            }
                        },
                        @{
                            type       = "Microsoft.Storage/storageAccounts/queueServices/queues/providers/roleAssignments"
                            apiVersion = "2018-01-01-preview"
                            name       = "[[concat(variables('storageAccountName'), '/default/', variables('dlqName'), '/Microsoft.Authorization/', variables('dlqRaGuid'))]"
                            dependsOn  = @(
                                "[[variables('dlqResourceId')]"
                            )
                            properties = @{
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
    }
    catch {
        Write-Error "Error in Get-StorageAccountBlobContainerDeploymentTemplate function: $_"
        exit 1
    }
}

function Set-ResourceVariables {
    try {
        # Initialize variables hashtable if not already done
        if (-not $variables) { $variables = @{} }

        Set-ArmVariable $variables "_dataConnectorContentIdConnections$global:connectorCounter" "[variables('_dataConnectorContentIdConnections')]"
        Set-ArmVariable $variables "connectorName" "blob-example-26-12"
        Set-ArmVariable $variables "storageAccountName" "[[split(split(parameters('blobContainerUri'), 'https://')[1], '.blob.core.windows.net')[0]]"
        Set-ArmVariable $variables "blobContainerName" "[[split(split(parameters('blobContainerUri'), '.blob.core.windows.net/')[1], '/')[0]]"
        Set-ArmVariable $variables "queueName" "[[concat(variables('connectorName'), '-notification')]]"
        Set-ArmVariable $variables "dlqName" "[[concat(variables('connectorName'), '-dlq')]]"
        Set-ArmVariable $variables "ResourcesIdPrefix" "[[format('/subscriptions/{0}/resourceGroups/{1}/providers', parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'))]]"
        Set-ArmVariable $variables "storageAccountId" "[[format('{0}/Microsoft.Storage/storageAccounts/{1}', variables('ResourcesIdPrefix'), variables('storageAccountName'))]]"
        Set-ArmVariable $variables "notificationQueueResourceId" "[[format('{0}/Microsoft.Storage/storageAccounts/{1}/queueServices//default/queues/{2}', variables('ResourcesIdPrefix'), variables('storageAccountName'), variables('queueName'))]]"
        Set-ArmVariable $variables "dlqResourceId" "[[format('{0}/Microsoft.Storage/storageAccounts/{1}/queueServices//default/queues/{2}', variables('ResourcesIdPrefix'), variables('storageAccountName'), variables('dlqName'))]]"
        Set-ArmVariable $variables "EGSystemTopicDefaultName" "[[format('eg-system-topic-{0}-{1}', variables('connectorName'), parameters('workspaceName'))]]"
        Set-ArmVariable $variables "EGSystemTopicName" "[[if(empty(parameters('EGSystemTopicName')), variables('EGSystemTopicDefaultName'), parameters('EGSystemTopicName'))]]"
        Set-ArmVariable $variables "EGTopicResourceId" "[[format('{0}/Microsoft.EventGrid/systemTopics/{1}', variables('ResourcesIdPrefix'), variables('EGSystemTopicName'))]]"
        Set-ArmVariable $variables "EgSubscriptionName" "[[format('{0}-{1}', variables('connectorName'), 'blobcreatedevents')]]"
        Set-ArmVariable $variables "EgSubscriptionResourceId" "[[format('{0}/Microsoft.EventGrid/systemTopics/{1}/eventSubscriptions/{2}', variables('ResourcesIdPrefix'), variables('EGSystemTopicName'), variables('EgSubscriptionName'))]]"
        Set-ArmVariable $variables "storageBlobContributorRoleId" "[[format('/subscriptions/{0}/providers/Microsoft.Authorization/roleDefinitions/ba92f5b4-2d11-453d-a403-e96b0029c9fe', parameters('StorageAccountSubscription'))]]"
        Set-ArmVariable $variables "storageQueueContributorRoleId" "[[format('/subscriptions/{0}/providers/Microsoft.Authorization/roleDefinitions/974c5e8b-45b9-4653-ba55-5f855dd0fb88', parameters('StorageAccountSubscription'))]]"
        Set-ArmVariable $variables "blobRaGuid" "[[guid(variables('storageAccountName'), variables('blobContainerName'))]]"
        Set-ArmVariable $variables "notificationQueueRaGuid" "[[guid(variables('storageAccountName'), variables('queueName'))]]"
        Set-ArmVariable $variables "dlqRaGuid" "[[guid(variables('storageAccountName'), variables('dlqName'))]]"
        Set-ArmVariable $variables "blobRoleAssignmentResourceId" "[[format('{0}/Microsoft.Storage/storageAccounts/{1}/blobServices/default/containers/{2}/providers/Microsoft.Authorization/roleAssignments/{3}', variables('ResourcesIdPrefix'), variables('storageAccountName'), variables('blobContainerName'),variables('blobRaGuid'))]]"
        Set-ArmVariable $variables "notificationQueueRoleAssignmentResourceId" "[[format('{0}/Microsoft.Storage/storageAccounts/{1}/queueServices/default/queues/{2}/providers/Microsoft.Authorization/roleAssignments/{3}', variables('ResourcesIdPrefix'), variables('storageAccountName'), variables('queueName'),variables('notificationQueueRaGuid'))]]"
        Set-ArmVariable $variables "dlqRoleAssignmentResourceId" "[[format('{0}/Microsoft.Storage/storageAccounts/{1}/queueServices/default/queues/{2}/providers/Microsoft.Authorization/roleAssignments/{3}', variables('ResourcesIdPrefix'), variables('storageAccountName'), variables('dlqName'),variables('dlqRaGuid'))]]"
        Set-ArmVariable $variables "nestedDeploymentName" "CreateDataFlowResources"
        Set-ArmVariable $variables "nestedDeploymentId" "[[format('{0}/Microsoft.Resources/deployments/{1}', variables('ResourcesIdPrefix'), variables('nestedDeploymentName'))]]"

        return $variables
    }
    catch {
        Write-Host "Error in Set-ResourceVariables function: $_"
        exit 1
    }
}