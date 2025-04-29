
function Set-UriProperty {
    param (
        [string]$propertyName,
        [string]$queueVarName
    )
    $uriValue = "[[uri(concat('https://', variables('storageAccountName'), parameters('blobContainerUriDomain'), '/', variables('$queueVarName')))]"

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
        Write-Host "name: $name , value: $value"
    }
}

function CreateStorageAccountBlobContainerResourceProperties($armResource, $templateContentConnections, $fileType) {
    try {
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

        $hasVariables = [bool]($templateContentConnections.properties.mainTemplate.PSobject.Properties.name -match "variables")
        if (!$hasVariables) {
            $templateContentConnections.properties.mainTemplate | Add-Member -NotePropertyName "variables" -NotePropertyValue @{}
        }

        $templateContentConnections.properties.mainTemplate.variables = Set-ResourceVariables 
        $templateContentConnections.properties.mainTemplate.resources += Get-StorageAccountDeploymentTemplate
    }
    catch {
        Write-Host "Error in CreateStorageAccountBlobContainerResourceProperties function. Error Details $_"
    }
}

function Get-StorageAccountDeploymentTemplate {
        return [ordered]@{
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
                            properties = @{
                                provisioningState = "Succeeded"
                                source            = "[[variables('storageAccountId')]"
                                topicType         = "microsoft.storage.storageaccounts"
                                metricResourceId  = "0cefe8d9-3269-4f68-a44e-46a4fc26e4a9"
                            }
                            condition  = "[[empty(parameters('EGSystemTopicName'))]"
                        },
                        [ordered]@{
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
                        [ordered]@{
                            type       = "Microsoft.Storage/storageAccounts/blobServices/containers/providers/roleAssignments"
                            apiVersion = "2018-01-01-preview"
                            name       = "[[concat(variables('storageAccountName'), '/default/', variables('blobContainerName'), '/Microsoft.Authorization/', variables('blobRaGuid'))]"
                            properties = @{
                                roleDefinitionId = "[[variables('storageBlobContributorRoleId')]"
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
                            properties = @{
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

function Set-ResourceVariables {
    try {
        # Initialize variables hashtable if not already done
        if (-not $variables) { $variables = @{} }

        $dayAndMonth = Get-Date -Format 'dd-MM'
        $connectorName = "sentinel-connector-$dayAndMonth"
        $blobContainerUriPart = "[concat('.blob.core', '.windows.net')]"
        Set-ArmVariable $variables "_dataConnectorContentIdConnections$global:connectorCounter" "[variables('_dataConnectorContentIdConnections$global:connectorCounter')]"
        Set-ArmVariable $variables "connectorName" "$connectorName"
        Set-ArmVariable $variables "blobContainerUriPart" "$blobContainerUriPart"
        Set-ArmVariable $variables "storageAccountName" "[[split(split(parameters('blobContainerUri'), 'https://')[1], variables('blobContainerUriPart'))[0]]"
        Set-ArmVariable $variables "blobContainerName" "[[split(split(parameters('blobContainerUri'), variables('blobContainerUriPart'), '/')[1], '/')[0]]"
        Set-ArmVariable $variables "queueName" "[[concat(variables('connectorName'), '-notification')]"
        Set-ArmVariable $variables "dlqName" "[[concat(variables('connectorName'), '-dlq')]"
        Set-ArmVariable $variables "ResourcesIdPrefix" "[[format('/subscriptions/{0}/resourceGroups/{1}/providers', parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'))]"
        Set-ArmVariable $variables "storageAccountId" "[[subscriptionResourceId(parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts', variables('storageAccountName'))]"
        Set-ArmVariable $variables "notificationQueueResourceId" "[[resourceId(concat(variables('ResourcesIdPrefix'), '/storageAccounts/', variables('storageAccountName'), '/queueServices/default/queues/', variables('queueName')))]"
        Set-ArmVariable $variables "dlqResourceId" "[[resourceId(concat(variables('ResourcesIdPrefix'), '/Microsoft.Storage/storageAccounts/', variables('storageAccountName'), '/queueServices/default/queues/', variables('dlqName')))]"
        Set-ArmVariable $variables "EGSystemTopicDefaultName" "[[format('eg-system-topic-{0}-{1}', variables('connectorName'), parameters('workspaceName'))]"
        Set-ArmVariable $variables "EGSystemTopicName" "[[if(empty(parameters('EGSystemTopicName')), variables('EGSystemTopicDefaultName'), parameters('EGSystemTopicName'))]"
        Set-ArmVariable $variables "EGTopicResourceId" "[[resourceId(concat(variables('ResourcesIdPrefix'), '/Microsoft.EventGrid/systemTopics/', variables('EGSystemTopicName')))]"
        Set-ArmVariable $variables "EgSubscriptionName" "[[format('{0}-{1}', variables('connectorName'), 'blobcreatedevents')]"
        Set-ArmVariable $variables "EgSubscriptionResourceId" "[[resourceId(concat(variables('ResourcesIdPrefix'), '/Microsoft.EventGrid/systemTopics/', variables('EGSystemTopicName'), '/eventSubscriptions/', variables('EgSubscriptionName')))]"
        Set-ArmVariable $variables "storageBlobContributorRoleId" "[[subscriptionResourceId(parameters('StorageAccountSubscription'), '', 'Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')]"
        Set-ArmVariable $variables "storageQueueContributorRoleId" "[[subscriptionResourceId(parameters('StorageAccountSubscription'), '', 'Microsoft.Authorization/roleDefinitions', '974c5e8b-45b9-4653-ba55-5f855dd0fb88')]"
        Set-ArmVariable $variables "blobRaGuid" "[[guid(variables('storageAccountName'), variables('blobContainerName'))]"
        Set-ArmVariable $variables "notificationQueueRaGuid" "[[guid(variables('storageAccountName'), variables('queueName'))]"
        Set-ArmVariable $variables "dlqRaGuid" "[[guid(variables('storageAccountName'), variables('dlqName'))]"
        Set-ArmVariable $variables "blobRoleAssignmentResourceId" "[[resourceId('Microsoft.Storage/storageAccounts/blobServices/containers/providers/Microsoft.Authorization/roleAssignments', variables('storageAccountName'), 'default', variables('blobContainerName'), variables('blobRaGuid'))]"
        Set-ArmVariable $variables "notificationQueueRoleAssignmentResourceId" "[[resourceId('Microsoft.Storage/storageAccounts/queueServices/queues/providers/Microsoft.Authorization/roleAssignments', variables('storageAccountName'), 'default', variables('queueName'), variables('notificationQueueRaGuid'))]"
        Set-ArmVariable $variables "dlqRoleAssignmentResourceId" "[[resourceId(concat(variables('ResourcesIdPrefix'), '/Microsoft.Storage/storageAccounts/', variables('storageAccountName'), '/queueServices/default/queues/', variables('dlqName'), '/providers/Microsoft.Authorization/roleAssignments/', variables('dlqRaGuid')))]"
        Set-ArmVariable $variables "nestedDeploymentName" "CreateDataFlowResources"
        Set-ArmVariable $variables "nestedDeploymentId" "[[resourceId(concat(variables('ResourcesIdPrefix'), '/Microsoft.Resources/deployments/', variables('nestedDeploymentName')))]"

        return $variables
    }
    catch {
        Write-Host "Error in Set-ResourceVariables function: $_"
        exit 1
    }
}