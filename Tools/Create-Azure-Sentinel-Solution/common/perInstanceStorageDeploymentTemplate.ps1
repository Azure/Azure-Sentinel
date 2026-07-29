# Opt-in V3 packaging support for StorageAccountBlobContainer pollers that declare
# a top-level connectionDeployment object with mode "PerInstance". The poller,
# DCR, and table JSON remain authoritative; this generator composes their
# per-connection ARM topology without requiring edits to Package/mainTemplate.json.

function Copy-PerInstanceJsonObject {
    param(
        [Parameter(Mandatory = $true)] $InputObject
    )

    return $InputObject | ConvertTo-Json -Depth 100 | ConvertFrom-Json
}

function Set-PerInstanceTemplateVariable {
    param(
        [Parameter(Mandatory = $true)] $Template,
        [Parameter(Mandatory = $true)] [string] $Name,
        [Parameter(Mandatory = $true)] $Value
    )

    $Template.variables | Add-Member -MemberType NoteProperty -Name $Name -Value $Value -Force
}

function Get-PerInstanceStorageDeployment {
    param(
        [Parameter(Mandatory = $true)] $DeploymentConfig
    )

    # The storage-side resources are deployed into the storage account's own
    # subscription/resource group, which is frequently different from the Sentinel
    # workspace scope. The nested deployment therefore MUST use inner-scope
    # expression evaluation: under the default (outer) scope, resourceId() inside
    # this template is evaluated against the *parent* deployment's subscription and
    # resource group, so every intra-template dependsOn resolves to an identifier
    # that does not exist in the nested deployment and ARM fails validation with
    # "The resource '<queue id>' is not defined in the template.".
    # Inner scope means the nested template can only see its own parameters, so all
    # parent values are passed in explicitly below.
    return [ordered]@{
        type           = "Microsoft.Resources/deployments"
        apiVersion     = "2021-04-01"
        name           = "[[variables('storageNestedDeploymentName')]"
        properties     = [ordered]@{
            mode                        = "Incremental"
            expressionEvaluationOptions = [ordered]@{
                scope = "inner"
            }
            parameters                  = [ordered]@{
                storageAccountName            = [ordered]@{ value = "[[variables('storageAccountName')]" }
                storageAccountId              = [ordered]@{ value = "[[variables('storageAccountId')]" }
                blobContainerName             = [ordered]@{ value = "[[variables('blobContainerName')]" }
                queueName                     = [ordered]@{ value = "[[variables('queueName')]" }
                dlqName                       = [ordered]@{ value = "[[variables('dlqName')]" }
                eventGridSystemTopicName      = [ordered]@{ value = "[[variables('eventGridSystemTopicName')]" }
                eventGridSubscriptionName     = [ordered]@{ value = "[[variables('eventGridSubscriptionName')]" }
                createEventGridSystemTopic    = [ordered]@{ value = "[[variables('createEventGridSystemTopic')]" }
                principalId                   = [ordered]@{ value = "[[parameters('principalId')]" }
                storageQueueContributorRoleId = [ordered]@{ value = "[[variables('storageQueueContributorRoleId')]" }
                storageBlobContributorRoleId  = [ordered]@{ value = "[[variables('storageBlobContributorRoleId')]" }
                notificationQueueRaGuid       = [ordered]@{ value = "[[variables('notificationQueueRaGuid')]" }
                dlqRaGuid                     = [ordered]@{ value = "[[variables('dlqRaGuid')]" }
                blobRaGuid                    = [ordered]@{ value = "[[variables('blobRaGuid')]" }
            }
            template                    = [ordered]@{
                '$schema'      = "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#"
                contentVersion = "1.0.0.0"
                parameters     = [ordered]@{
                    storageAccountName            = [ordered]@{ type = "string" }
                    storageAccountId              = [ordered]@{ type = "string" }
                    blobContainerName             = [ordered]@{ type = "string" }
                    queueName                     = [ordered]@{ type = "string" }
                    dlqName                       = [ordered]@{ type = "string" }
                    eventGridSystemTopicName      = [ordered]@{ type = "string" }
                    eventGridSubscriptionName     = [ordered]@{ type = "string" }
                    createEventGridSystemTopic    = [ordered]@{ type = "bool" }
                    principalId                   = [ordered]@{ type = "securestring" }
                    storageQueueContributorRoleId = [ordered]@{ type = "string" }
                    storageBlobContributorRoleId  = [ordered]@{ type = "string" }
                    notificationQueueRaGuid       = [ordered]@{ type = "string" }
                    dlqRaGuid                     = [ordered]@{ type = "string" }
                    blobRaGuid                    = [ordered]@{ type = "string" }
                }
                resources      = @(
                    [ordered]@{
                        type       = "Microsoft.Storage/storageAccounts/queueServices/queues"
                        apiVersion = "2025-06-01"
                        name       = "[[concat(parameters('storageAccountName'), '/default/', parameters('queueName'))]"
                        properties = @{}
                    },
                    [ordered]@{
                        type       = "Microsoft.Storage/storageAccounts/queueServices/queues"
                        apiVersion = "2025-06-01"
                        name       = "[[concat(parameters('storageAccountName'), '/default/', parameters('dlqName'))]"
                        properties = @{}
                    },
                    [ordered]@{
                        type       = "Microsoft.Authorization/roleAssignments"
                        apiVersion = "2022-04-01"
                        name       = "[[parameters('notificationQueueRaGuid')]"
                        scope      = "[[resourceId('Microsoft.Storage/storageAccounts/queueServices/queues', parameters('storageAccountName'), 'default', parameters('queueName'))]"
                        dependsOn  = @(
                            "[[resourceId('Microsoft.Storage/storageAccounts/queueServices/queues', parameters('storageAccountName'), 'default', parameters('queueName'))]"
                        )
                        properties = [ordered]@{
                            roleDefinitionId = "[[parameters('storageQueueContributorRoleId')]"
                            principalId      = "[[parameters('principalId')]"
                            principalType    = "ServicePrincipal"
                        }
                    },
                    [ordered]@{
                        type       = "Microsoft.Authorization/roleAssignments"
                        apiVersion = "2022-04-01"
                        name       = "[[parameters('dlqRaGuid')]"
                        scope      = "[[resourceId('Microsoft.Storage/storageAccounts/queueServices/queues', parameters('storageAccountName'), 'default', parameters('dlqName'))]"
                        dependsOn  = @(
                            "[[resourceId('Microsoft.Storage/storageAccounts/queueServices/queues', parameters('storageAccountName'), 'default', parameters('dlqName'))]"
                        )
                        properties = [ordered]@{
                            roleDefinitionId = "[[parameters('storageQueueContributorRoleId')]"
                            principalId      = "[[parameters('principalId')]"
                            principalType    = "ServicePrincipal"
                        }
                    },
                    [ordered]@{
                        type       = "Microsoft.EventGrid/systemTopics"
                        apiVersion = "2025-02-15"
                        name       = "[[parameters('eventGridSystemTopicName')]"
                        location   = "[[reference(parameters('storageAccountId'), '2022-09-01', 'Full').location]"
                        condition  = "[[parameters('createEventGridSystemTopic')]"
                        properties = [ordered]@{
                            source    = "[[parameters('storageAccountId')]"
                            topicType = "microsoft.storage.storageaccounts"
                        }
                    },
                    [ordered]@{
                        type       = "Microsoft.EventGrid/systemTopics/eventSubscriptions"
                        apiVersion = "2025-02-15"
                        name       = "[[format('{0}/{1}', parameters('eventGridSystemTopicName'), parameters('eventGridSubscriptionName'))]"
                        dependsOn  = @(
                            "[[resourceId('Microsoft.EventGrid/systemTopics', parameters('eventGridSystemTopicName'))]",
                            "[[resourceId('Microsoft.Storage/storageAccounts/queueServices/queues', parameters('storageAccountName'), 'default', parameters('queueName'))]"
                        )
                        properties = [ordered]@{
                            destination = [ordered]@{
                                endpointType = "StorageQueue"
                                properties   = [ordered]@{
                                    queueName  = "[[parameters('queueName')]"
                                    resourceId = "[[parameters('storageAccountId')]"
                                }
                            }
                            filter      = [ordered]@{
                                includedEventTypes = @("Microsoft.Storage.BlobCreated")
                                subjectBeginsWith  = "[[format('{0}/{1}', '/blobServices/default/containers', parameters('blobContainerName'))]"
                            }
                        }
                    },
                    [ordered]@{
                        type       = "Microsoft.Authorization/roleAssignments"
                        apiVersion = "2022-04-01"
                        name       = "[[parameters('blobRaGuid')]"
                        scope      = "[[resourceId('Microsoft.Storage/storageAccounts/blobServices/containers', parameters('storageAccountName'), 'default', parameters('blobContainerName'))]"
                        properties = [ordered]@{
                            roleDefinitionId = "[[parameters('storageBlobContributorRoleId')]"
                            principalId      = "[[parameters('principalId')]"
                            principalType    = "ServicePrincipal"
                        }
                    }
                )
            }
        }
        subscriptionId = "[[trim(parameters('StorageAccountSubscription'))]"
        resourceGroup  = "[[trim(parameters('StorageAccountResourceGroupName'))]"
    }
}

function Get-PerInstancePropagationBuffer {
    param(
        [Parameter(Mandatory = $true)] [int] $DelaySeconds
    )

    $scriptContent = @"
`$ErrorActionPreference = 'Stop'
`$delaySeconds = $DelaySeconds
`$intervalSeconds = 15
`$elapsedSeconds = 0
Write-Host "Starting bounded Azure role-assignment propagation buffer for `$delaySeconds seconds."
while (`$elapsedSeconds -lt `$delaySeconds) {
    `$sleepSeconds = [Math]::Min(`$intervalSeconds, `$delaySeconds - `$elapsedSeconds)
    Start-Sleep -Seconds `$sleepSeconds
    `$elapsedSeconds += `$sleepSeconds
    Write-Host "Propagation buffer progress: `$elapsedSeconds / `$delaySeconds seconds."
}
Write-Host 'Propagation buffer complete. Data-plane authorization can still take longer; deterministic redeployment is safe.'
"@

    return [ordered]@{
        type       = "Microsoft.Resources/deploymentScripts"
        apiVersion = "2023-08-01"
        name       = "[[variables('rbacPropagationScriptName')]"
        location   = "[parameters('workspace-location')]"
        kind       = "AzurePowerShell"
        dependsOn  = @(
            "[[variables('storageNestedDeploymentId')]"
        )
        properties = [ordered]@{
            azPowerShellVersion = "11.5"
            forceUpdateTag      = "[[parameters('forceUpdateTag')]"
            retentionInterval   = "PT1H"
            cleanupPreference   = "Always"
            timeout             = "PT5M"
            scriptContent       = $scriptContent
        }
    }
}

function CreatePerInstanceStorageAccountBlobContainerResourceProperties {
    param(
        [Parameter(Mandatory = $true)] $ArmResource,
        [Parameter(Mandatory = $true)] $TemplateContentConnections,
        [Parameter(Mandatory = $true)] [string] $FileType,
        [Parameter(Mandatory = $true)] $DeploymentConfig,
        [Parameter(Mandatory = $true)] $CcpItem
    )

    try {
        $resourcePrefix = [string]$DeploymentConfig.resourcePrefix
        $queuePrefix = [string]$DeploymentConfig.queuePrefix
        $tableName = [string]$DeploymentConfig.tableName
        $identityParameters = @($DeploymentConfig.identityParameters)
        $rolePropagationDelaySeconds = [int]$DeploymentConfig.rolePropagationDelaySeconds

        if ($resourcePrefix -notmatch '^[a-z][a-z0-9-]{1,19}$') {
            throw "connectionDeployment.resourcePrefix must be 2-20 lowercase alphanumeric or hyphen characters and start with a letter."
        }
        if ($queuePrefix -notmatch '^[a-z0-9](?:[a-z0-9-]{0,14})[a-z0-9]$') {
            throw "connectionDeployment.queuePrefix must be 2-16 lowercase alphanumeric or hyphen characters without leading or trailing hyphens."
        }
        if ($identityParameters.Count -eq 0) {
            throw "connectionDeployment.identityParameters must contain at least one immutable identity parameter."
        }
        if ($rolePropagationDelaySeconds -lt 0 -or $rolePropagationDelaySeconds -gt 240) {
            throw "connectionDeployment.rolePropagationDelaySeconds must be between 0 and 240 seconds."
        }
        if ([string]::IsNullOrWhiteSpace($CcpItem.DCRFilePath) -or [string]::IsNullOrWhiteSpace($CcpItem.TableFilePath)) {
            throw "Per-instance storage deployment requires both DCR and table source files."
        }

        $template = $TemplateContentConnections.properties.mainTemplate

        foreach ($parameterName in $identityParameters) {
            if ($null -eq $template.parameters.PSObject.Properties[$parameterName]) {
                throw "Immutable identity parameter '$parameterName' is not present in the generated connection template."
            }
        }

        if ($null -ne $template.parameters.PSObject.Properties["dcrConfig"]) {
            $template.parameters.PSObject.Properties.Remove("dcrConfig")
        }
        if ($null -ne $template.parameters.PSObject.Properties["guidValue"]) {
            $template.parameters.PSObject.Properties.Remove("guidValue")
        }

        $forceUpdateTagParameter = [PSCustomObject]@{
            type         = "securestring"
            defaultValue = "[[utcNow()]"
            metadata     = [PSCustomObject]@{
                description = "Forces the bounded RBAC propagation buffer to run whenever the same deterministic collector is submitted again."
            }
        }
        $template.parameters | Add-Member -MemberType NoteProperty -Name "forceUpdateTag" -Value $forceUpdateTagParameter -Force

        $tableNameParameter = [PSCustomObject]@{
            type         = "string"
            defaultValue = $tableName
            metadata     = [PSCustomObject]@{
                description = "Log Analytics custom table this collector writes to. Must end in _CL. Leave blank to use the solution default '$tableName'."
            }
        }
        $template.parameters | Add-Member -MemberType NoteProperty -Name "TableName" -Value $tableNameParameter -Force

        $identityExpressions = @()
        foreach ($parameterName in $identityParameters) {
            $identityExpressions += "toLower(trim(parameters('$parameterName')))"
        }
        $identityExpressions += "toLower(variables('workspaceResourceId'))"

        Set-PerInstanceTemplateVariable -Template $template -Name "resourcePrefix" -Value $resourcePrefix
        Set-PerInstanceTemplateVariable -Template $template -Name "queuePrefix" -Value $queuePrefix
        Set-PerInstanceTemplateVariable -Template $template -Name "tableNameDefault" -Value $tableName
        Set-PerInstanceTemplateVariable -Template $template -Name "tableName" -Value "[[if(empty(trim(parameters('TableName'))), variables('tableNameDefault'), trim(parameters('TableName')))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "outputStreamName" -Value "[[concat('Custom-', variables('tableName'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "workspaceResourceId" -Value "[[resourceId('Microsoft.OperationalInsights/workspaces', parameters('innerWorkspace'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "instanceKey" -Value "[[uniqueString($($identityExpressions -join ', '))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "connectorName" -Value "[[format('{0}-{1}', variables('resourcePrefix'), variables('instanceKey'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "dceName" -Value "[[format('{0}-{1}', variables('resourcePrefix'), variables('instanceKey'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "dcrName" -Value "[[format('{0}-{1}', variables('resourcePrefix'), variables('instanceKey'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "diagnosticSettingName" -Value "[[format('{0}-{1}-logerrors', variables('resourcePrefix'), variables('instanceKey'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "storageAccountName" -Value "[[toLower(trim(parameters('StorageAccountName')))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "blobContainerName" -Value "[[toLower(trim(parameters('ContainerName')))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "queueName" -Value "[[format('{0}-{1}-notification', variables('queuePrefix'), variables('instanceKey'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "dlqName" -Value "[[format('{0}-{1}-dlq', variables('queuePrefix'), variables('instanceKey'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "storageAccountId" -Value "[[resourceId(trim(parameters('StorageAccountSubscription')), trim(parameters('StorageAccountResourceGroupName')), 'Microsoft.Storage/storageAccounts', variables('storageAccountName'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "blobContainerResourceId" -Value "[[resourceId(trim(parameters('StorageAccountSubscription')), trim(parameters('StorageAccountResourceGroupName')), 'Microsoft.Storage/storageAccounts/blobServices/containers', variables('storageAccountName'), 'default', variables('blobContainerName'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "notificationQueueResourceId" -Value "[[resourceId(trim(parameters('StorageAccountSubscription')), trim(parameters('StorageAccountResourceGroupName')), 'Microsoft.Storage/storageAccounts/queueServices/queues', variables('storageAccountName'), 'default', variables('queueName'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "dlqResourceId" -Value "[[resourceId(trim(parameters('StorageAccountSubscription')), trim(parameters('StorageAccountResourceGroupName')), 'Microsoft.Storage/storageAccounts/queueServices/queues', variables('storageAccountName'), 'default', variables('dlqName'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "eventGridSystemTopicDefaultName" -Value "[[format('sentinel-{0}-{1}', variables('resourcePrefix'), uniqueString(toLower(trim(parameters('StorageAccountSubscription'))), toLower(trim(parameters('StorageAccountResourceGroupName'))), variables('storageAccountName')))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "eventGridSystemTopicName" -Value "[[if(empty(parameters('EGSystemTopicName')), variables('eventGridSystemTopicDefaultName'), parameters('EGSystemTopicName'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "eventGridSubscriptionName" -Value "[[format('{0}-{1}-blobcreated', variables('resourcePrefix'), variables('instanceKey'))]"
        # Resolved as a variable rather than inline in the nested deployment's parameter
        # values so the inner boolean parameter is not type-compared against the
        # securestring 'EGSystemTopicName' parameter it is derived from.
        Set-PerInstanceTemplateVariable -Template $template -Name "createEventGridSystemTopic" -Value "[[empty(parameters('EGSystemTopicName'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "storageBlobContributorRoleId" -Value "[[subscriptionResourceId(trim(parameters('StorageAccountSubscription')), 'Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')]"
        Set-PerInstanceTemplateVariable -Template $template -Name "storageQueueContributorRoleId" -Value "[[subscriptionResourceId(trim(parameters('StorageAccountSubscription')), 'Microsoft.Authorization/roleDefinitions', '974c5e8b-45b9-4653-ba55-5f855dd0fb88')]"
        Set-PerInstanceTemplateVariable -Template $template -Name "blobRaGuid" -Value "[[guid(variables('blobContainerResourceId'), parameters('principalId'), variables('storageBlobContributorRoleId'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "notificationQueueRaGuid" -Value "[[guid(variables('notificationQueueResourceId'), parameters('principalId'), variables('storageQueueContributorRoleId'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "dlqRaGuid" -Value "[[guid(variables('dlqResourceId'), parameters('principalId'), variables('storageQueueContributorRoleId'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "dceResourceId" -Value "[[resourceId('Microsoft.Insights/dataCollectionEndpoints', variables('dceName'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "dcrResourceId" -Value "[[resourceId('Microsoft.Insights/dataCollectionRules', variables('dcrName'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "tableResourceId" -Value "[[resourceId('Microsoft.OperationalInsights/workspaces/tables', parameters('innerWorkspace'), variables('tableName'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "storageNestedDeploymentName" -Value "[[format('{0}-{1}-storage', variables('resourcePrefix'), variables('instanceKey'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "storageNestedDeploymentId" -Value "[[resourceId(trim(parameters('StorageAccountSubscription')), trim(parameters('StorageAccountResourceGroupName')), 'Microsoft.Resources/deployments', variables('storageNestedDeploymentName'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "rbacPropagationScriptName" -Value "[[format('{0}-{1}-rbac', variables('resourcePrefix'), variables('instanceKey'))]"
        Set-PerInstanceTemplateVariable -Template $template -Name "rbacPropagationScriptId" -Value "[[resourceId('Microsoft.Resources/deploymentScripts', variables('rbacPropagationScriptName'))]"

        $tableSource = Get-Content -Raw $CcpItem.TableFilePath | ConvertFrom-Json
        if ($tableSource -is [System.Array]) {
            $tableSource = $tableSource[0]
        }
        if ($tableSource.name -ne $tableName) {
            throw "connectionDeployment.tableName '$tableName' does not match the authoritative table source '$($tableSource.name)'."
        }
        $tableProperties = Copy-PerInstanceJsonObject -InputObject $tableSource.properties
        if ($null -eq $tableProperties.schema) {
            throw "The authoritative table source must contain a schema object."
        }
        $tableProperties.schema.name = "[[variables('tableName')]"
        $tableResource = [ordered]@{
            type       = "Microsoft.OperationalInsights/workspaces/tables"
            apiVersion = "2022-10-01"
            name       = "[[concat(parameters('innerWorkspace'), '/', variables('tableName'))]"
            location   = "[parameters('workspace-location')]"
            properties = $tableProperties
        }

        $dceResource = [ordered]@{
            type       = "Microsoft.Insights/dataCollectionEndpoints"
            apiVersion = "2022-06-01"
            name       = "[[variables('dceName')]"
            location   = "[parameters('workspace-location')]"
            dependsOn  = @(
                "[[variables('tableResourceId')]"
            )
            properties = [ordered]@{
                networkAcls = [ordered]@{
                    publicNetworkAccess = "Enabled"
                }
            }
        }

        $dcrSource = Get-Content -Raw $CcpItem.DCRFilePath | ConvertFrom-Json
        if ($dcrSource -is [System.Array]) {
            $dcrSource = $dcrSource[0]
        }
        $dcrProperties = Copy-PerInstanceJsonObject -InputObject $dcrSource.properties
        $dcrProperties.dataCollectionEndpointId = "[[variables('dceResourceId')]"
        if ($null -eq $dcrProperties.destinations.logAnalytics -or $dcrProperties.destinations.logAnalytics.Count -eq 0) {
            throw "The authoritative DCR source must contain a Log Analytics destination."
        }
        $dcrProperties.destinations.logAnalytics[0].workspaceResourceId = "[[variables('workspaceResourceId')]"
        if ($null -eq $dcrProperties.dataFlows -or $dcrProperties.dataFlows.Count -eq 0) {
            throw "The authoritative DCR source must contain at least one data flow."
        }
        foreach ($dataFlow in $dcrProperties.dataFlows) {
            if ($dataFlow.outputStream -ne "Custom-$tableName") {
                throw "DCR data flow outputStream '$($dataFlow.outputStream)' does not match the authoritative table 'Custom-$tableName'."
            }
            $dataFlow.outputStream = "[[variables('outputStreamName')]"
        }

        $dcrResource = [ordered]@{
            type       = "Microsoft.Insights/dataCollectionRules"
            apiVersion = "2022-06-01"
            name       = "[[variables('dcrName')]"
            location   = "[parameters('workspace-location')]"
            dependsOn  = @(
                "[[variables('dceResourceId')]",
                "[[variables('tableResourceId')]"
            )
            properties = $dcrProperties
        }

        $template.resources += $tableResource
        $template.resources += $dceResource
        $template.resources += $dcrResource

        if ([bool]$DeploymentConfig.enableDcrLogErrors) {
            $diagnosticResource = [ordered]@{
                type       = "Microsoft.Insights/diagnosticSettings"
                apiVersion = "2021-05-01-preview"
                name       = "[[variables('diagnosticSettingName')]"
                scope      = "[[format('Microsoft.Insights/dataCollectionRules/{0}', variables('dcrName'))]"
                dependsOn  = @(
                    "[[variables('dcrResourceId')]"
                )
                properties = [ordered]@{
                    workspaceId = "[[variables('workspaceResourceId')]"
                    logs        = @(
                        [ordered]@{
                            category = "LogErrors"
                            enabled  = $true
                        }
                    )
                }
            }
            $template.resources += $diagnosticResource
        }

        $template.resources += Get-PerInstanceStorageDeployment -DeploymentConfig $DeploymentConfig
        if ($rolePropagationDelaySeconds -gt 0) {
            $template.resources += Get-PerInstancePropagationBuffer -DelaySeconds $rolePropagationDelaySeconds
        }

        if (-not ($ArmResource.properties.PSObject.Properties.Name -contains "request")) {
            $ArmResource.properties | Add-Member -MemberType NoteProperty -Name "request" -Value ([PSCustomObject]@{})
        }
        $ArmResource.properties.request | Add-Member -MemberType NoteProperty -Name "QueueUri" -Value "[[uri(concat('https://', variables('storageAccountName'), '.queue.core', '.windows.net', '/'), variables('queueName'))]" -Force
        $ArmResource.properties.request | Add-Member -MemberType NoteProperty -Name "DlqUri" -Value "[[uri(concat('https://', variables('storageAccountName'), '.queue.core', '.windows.net', '/'), variables('dlqName'))]" -Force
        $ArmResource.properties.dcrConfig.dataCollectionEndpoint = "[[reference(variables('dceResourceId'), '2022-06-01').logsIngestion.endpoint]"
        $ArmResource.properties.dcrConfig.dataCollectionRuleImmutableId = "[[reference(variables('dcrResourceId'), '2022-06-01').immutableId]"
        $ArmResource.name = "[[concat(parameters('innerWorkspace'), '/Microsoft.SecurityInsights/', variables('connectorName'))]"

        $connectorDependencies = @(
            "[[variables('dcrResourceId')]",
            "[[variables('dceResourceId')]",
            "[[variables('storageNestedDeploymentId')]"
        )
        if ($rolePropagationDelaySeconds -gt 0) {
            $connectorDependencies = @("[[variables('rbacPropagationScriptId')]") + $connectorDependencies
        }
        if ($null -ne $ArmResource.PSObject.Properties["dependsOn"]) {
            $ArmResource.dependsOn = $connectorDependencies
        }
        else {
            $ArmResource | Add-Member -MemberType NoteProperty -Name "dependsOn" -Value $connectorDependencies
        }

        $TemplateContentConnections.properties.mainTemplate = $template
    }
    catch {
        Write-Host "Error in CreatePerInstanceStorageAccountBlobContainerResourceProperties. Error Details: $_" -BackgroundColor Red
        throw
    }
}
