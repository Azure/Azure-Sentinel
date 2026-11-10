function Get-EventGridRbacModeParameter {
    param([switch]$IncludeDefault)

    $parameter = [PSCustomObject]@{
        type = 'string'
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
            condition  = "[[parameters('existingSystemTopicMatchesStorageAccount')]"
            properties = [ordered]@{
                mode = 'Incremental'
                expressionEvaluationOptions = @{ scope = 'inner' }
                parameters = [ordered]@{
                    topicName = @{ value = "[[variables('EGSystemTopicName')]" }
                    StorageAccountLocation = @{ value = "[[parameters('StorageAccountLocation')]" }
                    sourceId = @{
                        value = "[[variables('storageAccountId')]"
                    }
                    existingSystemTopic = @{
                        value = "[[parameters('existingSystemTopic')]"
                    }
                }
                template = [ordered]@{
                    '$schema' = 'https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#'
                    contentVersion = '1.0.0.0'
                    parameters = [ordered]@{
                        topicName = @{ type = 'string' }
                        StorageAccountLocation = @{ type = 'string' }
                        sourceId = @{ type = 'string' }
                        existingSystemTopic = @{ type = 'object' }
                    }
                    variables = [ordered]@{
                        existingTopicIdentity = "[[if(contains(parameters('existingSystemTopic'), 'identity'), coalesce(parameters('existingSystemTopic').identity, createObject()), createObject())]"
                        existingUserAssignedIdentities = "[[if(contains(variables('existingTopicIdentity'), 'userAssignedIdentities'), coalesce(variables('existingTopicIdentity').userAssignedIdentities, createObject()), createObject())]"
                        topicIdentity = "[[if(empty(variables('existingUserAssignedIdentities')), createObject('type', 'SystemAssigned'), createObject('type', 'SystemAssigned, UserAssigned', 'userAssignedIdentities', variables('existingUserAssignedIdentities')))]"
                    }
                    resources = @(
                        [ordered]@{
                            type       = 'Microsoft.EventGrid/systemTopics'
                            apiVersion = '2025-02-15'
                            name       = "[[parameters('topicName')]"
                            location   = "[[if(empty(parameters('existingSystemTopic')), parameters('StorageAccountLocation'), parameters('existingSystemTopic').location)]"
                            tags       = "[[if(contains(parameters('existingSystemTopic'), 'tags'), coalesce(parameters('existingSystemTopic').tags, createObject()), createObject())]"
                            identity   = "[[variables('topicIdentity')]"
                            properties = [ordered]@{
                                source = "[[if(empty(parameters('existingSystemTopic')), parameters('sourceId'), parameters('existingSystemTopic').properties.source)]"
                                topicType = "[[if(empty(parameters('existingSystemTopic')), 'microsoft.storage.storageaccounts', parameters('existingSystemTopic').properties.topicType)]"
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
                "[[variables('notificationQueueResourceId')]"
            )
            properties = [ordered]@{
                mode = 'Incremental'
                expressionEvaluationOptions = @{ scope = 'inner' }
                parameters = [ordered]@{
                    principalId = @{
                        value = "[[if(equals(parameters('eventGridRbacMode'), 'CreateRoleAssignment'), reference(variables('eventGridTopicDeploymentId'), '2025-04-01').outputs.principalId.value, '')]"
                    }
                    storageAccountResourceId = @{
                        value = "[[variables('storageAccountId')]"
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
