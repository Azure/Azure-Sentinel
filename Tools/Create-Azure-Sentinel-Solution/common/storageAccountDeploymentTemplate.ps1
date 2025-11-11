
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

        Set-ResourceVariables 
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
}

function Set-ResourceVariables {
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
        $variables["storageBlobContributorRoleId"] = "[[subscriptionResourceId(parameters('StorageAccountSubscription'), 'Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')]"
        $variables["storageQueueContributorRoleId"] = "[[subscriptionResourceId(parameters('StorageAccountSubscription'), 'Microsoft.Authorization/roleDefinitions', '974c5e8b-45b9-4653-ba55-5f855dd0fb88')]"
        $variables["blobRaGuid"] = "[[guid(variables('storageAccountName'), variables('blobContainerName'))]"
        $variables["notificationQueueRaGuid"] = "[[guid(variables('storageAccountName'), variables('queueName'))]"
        $variables["dlqRaGuid"] = "[[guid(variables('storageAccountName'), variables('dlqName'))]"
        $variables["blobRoleAssignmentResourceId"] = "[[resourceId(parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts/blobServices/containers/providers/roleAssignments', variables('storageAccountName'), 'default', variables('blobContainerName'), 'Microsoft.Authorization', variables('blobRaGuid'))]"
        $variables["notificationQueueRoleAssignmentResourceId"] = "[[resourceId(parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts/queueServices/queues/providers/roleAssignments', variables('storageAccountName'), 'default', variables('queueName'), 'Microsoft.Authorization', variables('notificationQueueRaGuid'))]"
        $variables["dlqRoleAssignmentResourceId"] = "[[resourceId(parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts/queueServices/queues/providers/roleAssignments', variables('storageAccountName'), 'default', variables('dlqName'), 'Microsoft.Authorization', variables('dlqRaGuid'))]"
        $variables["nestedDeploymentName"] = "CreateDataFlowResources"
        $variables["nestedDeploymentId"] = "[[resourceId(parameters('StorageAccountResourceGroupName'), 'Microsoft.Resources/deployments', variables('nestedDeploymentName'))]"

        $templateContentConnections.properties.mainTemplate.variables = $variables
    }
    catch {
        Write-Host "Error in Set-ResourceVariables function: $_"
        exit 1
    }
}