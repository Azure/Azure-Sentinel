function Get-EventGridRbacModeParameter {
    param([switch]$IncludeDefault)

    $parameter = [PSCustomObject]@{
        type = 'securestring'
        minLength = 1
        allowedValues = @('CreateRoleAssignment', 'UseExistingRoleAssignment')
    }
    if ($IncludeDefault) {
        $parameter | Add-Member -NotePropertyName 'defaultValue' -NotePropertyValue 'CreateRoleAssignment'
    }
    return $parameter
}

function Get-EventGridManagedIdentityDeployments {
    return @(
        [ordered]@{
            type       = 'Microsoft.Resources/deployments'
            apiVersion = '2025-04-01'
            name       = "[[variables('eventGridTopicDeploymentName')]"
            properties = [ordered]@{
                mode = 'Incremental'
                expressionEvaluationOptions = @{ scope = 'inner' }
                parameters = [ordered]@{
                    topicName = @{ value = "[[variables('EGSystemTopicName')]" }
                    StorageAccountLocation = @{ value = "[[parameters('StorageAccountLocation')]" }
                    sourceId = @{
                        value = "[[resourceId(parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts', variables('storageAccountName'))]"
                    }
                    # Read the supplied topic before updating it in the inner-scoped deployment.
                    existingTopic = @{
                        value = "[[if(empty(parameters('EGSystemTopicName')), createObject(), reference(resourceId(parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'), 'Microsoft.EventGrid/systemTopics', variables('EGSystemTopicName')), '2025-02-15', 'Full'))]"
                    }
                }
                template = [ordered]@{
                    '$schema' = 'https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#'
                    contentVersion = '1.0.0.0'
                    parameters = [ordered]@{
                        topicName = @{ type = 'string' }
                        StorageAccountLocation = @{ type = 'securestring' }
                        sourceId = @{ type = 'string' }
                        existingTopic = @{ type = 'object' }
                    }
                    variables = [ordered]@{
                        existingIdentity = "[[if(contains(parameters('existingTopic'), 'identity'), coalesce(parameters('existingTopic').identity, createObject()), createObject())]"
                        userAssignedIdentities = "[[if(contains(variables('existingIdentity'), 'userAssignedIdentities'), coalesce(variables('existingIdentity').userAssignedIdentities, createObject()), createObject())]"
                        topicIdentity = "[[if(empty(variables('userAssignedIdentities')), createObject('type', 'SystemAssigned'), createObject('type', 'SystemAssigned, UserAssigned', 'userAssignedIdentities', variables('userAssignedIdentities')))]"
                    }
                    resources = @(
                        [ordered]@{
                            type       = 'Microsoft.EventGrid/systemTopics'
                            apiVersion = '2025-02-15'
                            name       = "[[parameters('topicName')]"
                            location   = "[[parameters('StorageAccountLocation')]"
                            tags       = "[[if(contains(parameters('existingTopic'), 'tags'), coalesce(parameters('existingTopic').tags, createObject()), createObject())]"
                            identity   = "[[variables('topicIdentity')]"
                            properties = [ordered]@{
                                source = "[[parameters('sourceId')]"
                                topicType = 'microsoft.storage.storageaccounts'
                            }
                        }
                    )
                    outputs = @{
                        principalId = @{
                            type = 'string'
                            value = "[[reference(resourceId('Microsoft.EventGrid/systemTopics', parameters('topicName')), '2025-02-15', 'Full').identity.principalId]"
                        }
                    }
                }
            }
        },
        [ordered]@{
            type       = 'Microsoft.Resources/deployments'
            apiVersion = '2025-04-01'
            name       = "[[variables('eventGridQueueSenderDeploymentName')]"
            condition  = "[[equals(parameters('eventGridRbacMode'), 'CreateRoleAssignment')]"
            dependsOn  = @(
                "[[variables('eventGridTopicDeploymentId')]",
                "[[resourceId(parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts/queueServices/queues', variables('storageAccountName'), 'default', variables('queueName'))]"
            )
            properties = [ordered]@{
                mode = 'Incremental'
                expressionEvaluationOptions = @{ scope = 'inner' }
                parameters = [ordered]@{
                    principalId = @{
                        value = "[[reference(variables('eventGridTopicDeploymentId'), '2025-04-01').outputs.principalId.value]"
                    }
                    storageAccountResourceId = @{
                        value = "[[resourceId(parameters('StorageAccountSubscription'), parameters('StorageAccountResourceGroupName'), 'Microsoft.Storage/storageAccounts', variables('storageAccountName'))]"
                    }
                }
                template = [ordered]@{
                    '$schema' = 'https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#'
                    contentVersion = '1.0.0.0'
                    parameters = [ordered]@{
                        principalId = @{ type = 'string' }
                        storageAccountResourceId = @{ type = 'string' }
                    }
                    variables = @{
                        queueMessageSenderRoleId = "[[subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'c6a89b2d-59bc-44d0-9896-0f6e12d7b80a')]"
                    }
                    resources = @(
                        [ordered]@{
                            type       = 'Microsoft.Authorization/roleAssignments'
                            apiVersion = '2022-04-01'
                            name       = "[[guid(toLower(parameters('storageAccountResourceId')), toLower(parameters('principalId')), toLower(variables('queueMessageSenderRoleId')))]"
                            # Event Grid's Storage Queue destination authorization requires account-scoped sender access.
                            scope      = "[[parameters('storageAccountResourceId')]"
                            properties = [ordered]@{
                                roleDefinitionId = "[[variables('queueMessageSenderRoleId')]"
                                principalId = "[[parameters('principalId')]"
                                principalType = 'ServicePrincipal'
                            }
                        }
                    )
                }
            }
        }
    )
}
