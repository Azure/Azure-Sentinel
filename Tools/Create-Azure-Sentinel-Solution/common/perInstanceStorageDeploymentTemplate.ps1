# Opt-in connection-time topology. The source table and DCR remain authoritative;
# Event Grid identity/RBAC resources are composed by the current shared helper.

function Get-PerInstanceArmStringLiteral([AllowEmptyString()][string]$Value) {
    return "'" + $Value.Replace("'", "''") + "'"
}

function Get-PerInstanceAttributionTransform {
    param(
        [Parameter(Mandatory)][string]$Transform,
        [Parameter(Mandatory)][PSCustomObject]$Attribution,
        [ValidatePattern('^[A-Za-z_][A-Za-z0-9_]*$')][string]$TransformVariableName
    )

    $replacements = @(
        foreach ($property in $Attribution.PSObject.Properties) {
            if ($property.Name -cnotmatch '^[A-Za-z_][A-Za-z0-9_]*$' -or
                $property.Value -isnot [string] -or $property.Value -cnotmatch '^[A-Za-z_][A-Za-z0-9_]*$') {
                throw 'attributionColumns must map KQL column identifiers to connection parameter identifiers.'
            }
            $pattern = "(?<![A-Za-z0-9_])$([regex]::Escape($property.Name))\s*=\s*''(?!')"
            $matches = [regex]::Matches($Transform, $pattern)
            if ($matches.Count -ne 1) {
                throw "attributionColumns column '$($property.Name)' requires exactly one empty-string assignment in the authoritative DCR transform."
            }
            [pscustomobject]@{ Match = $matches[0]; Column = $property.Name; Parameter = $property.Value }
        }
    )
    if ($replacements.Count -eq 0) { return $Transform }

    $segments = @()
    $cursor = 0
    foreach ($replacement in $replacements | Sort-Object { $_.Match.Index }) {
        if ($TransformVariableName) {
            # Large vendor transforms can exceed ARM's 24,576-character expression
            # limit. Keep source text in a literal variable; only slice positions
            # and encoded attribution values belong in the expression.
            $segments += "substring(variables('$TransformVariableName'), $cursor, $($replacement.Match.Index - $cursor))"
        }
        else {
            $segments += Get-PerInstanceArmStringLiteral $Transform.Substring($cursor, $replacement.Match.Index - $cursor)
        }
        $segments += Get-PerInstanceArmStringLiteral "$($replacement.Column) = base64_decodestring('"
        # ARM encodes the exact configured value at connection time. Only base64
        # characters enter the KQL literal, preserving quotes, slashes and Unicode
        # without allowing a value to become query syntax. Azure Monitor transforms
        # support base64_decodestring (not the base64_decode_tostring spelling).
        $segments += "base64(parameters('$($replacement.Parameter)'))"
        $segments += Get-PerInstanceArmStringLiteral "')"
        $cursor = $replacement.Match.Index + $replacement.Match.Length
    }
    if ($TransformVariableName) {
        $segments += "substring(variables('$TransformVariableName'), $cursor, $($Transform.Length - $cursor))"
    }
    else {
        $segments += Get-PerInstanceArmStringLiteral $Transform.Substring($cursor)
    }
    return "[[concat($($segments -join ', '))]"
}

function CreatePerInstanceStorageAccountBlobContainerResourceProperties {
    param(
        [Parameter(Mandatory)]$ArmResource,
        [Parameter(Mandatory)]$TemplateContentConnections,
        [Parameter(Mandatory)]$DeploymentConfig,
        [Parameter(Mandatory)]$CcpItem,
        [Parameter(Mandatory)]$InstructionParameters
    )

    if ($DeploymentConfig -isnot [PSCustomObject] -or $DeploymentConfig.mode -cne 'PerInstance') {
        throw "connectionDeployment must be an object with mode 'PerInstance'."
    }
    $supportedOptions = @('mode', 'resourcePrefix', 'queuePrefix', 'tableName', 'identityParameters', 'enableDcrLogErrors', 'attributionColumns')
    foreach ($option in $DeploymentConfig.PSObject.Properties.Name) {
        if ($option -cnotin $supportedOptions) { throw "Unsupported connectionDeployment option '$option'." }
    }
    if ($DeploymentConfig.resourcePrefix -isnot [string] -or
        $DeploymentConfig.resourcePrefix -cnotmatch '^[a-z][a-z0-9-]{1,19}$') {
        throw 'connectionDeployment.resourcePrefix must be 2-20 lowercase alphanumeric or hyphen characters and start with a letter.'
    }
    if ($DeploymentConfig.queuePrefix -isnot [string] -or
        $DeploymentConfig.queuePrefix -cnotmatch '^[a-z0-9][a-z0-9-]{0,14}[a-z0-9]$' -or $DeploymentConfig.queuePrefix.Contains('--')) {
        throw 'connectionDeployment.queuePrefix must be 2-16 lowercase alphanumeric or single hyphen characters without leading or trailing hyphens.'
    }
    if ($DeploymentConfig.tableName -isnot [string] -or
        $DeploymentConfig.tableName -cnotmatch '^[A-Za-z][A-Za-z0-9_]{0,96}_CL$') {
        throw 'connectionDeployment.tableName must be a custom table identifier ending in _CL (at most 100 characters).'
    }
    if ($DeploymentConfig.PSObject.Properties.Name -contains 'enableDcrLogErrors' -and
        $DeploymentConfig.enableDcrLogErrors -isnot [bool]) {
        throw 'connectionDeployment.enableDcrLogErrors must be a boolean.'
    }
    if ($DeploymentConfig.identityParameters -isnot [array] -or $DeploymentConfig.identityParameters.Count -eq 0) {
        throw 'connectionDeployment.identityParameters must be a nonempty array of immutable connection parameter names.'
    }
    $identityParameters = $DeploymentConfig.identityParameters
    $seen = @{}
    foreach ($name in $identityParameters) {
        if ($name -isnot [string] -or $name -cnotmatch '^[A-Za-z_][A-Za-z0-9_]*$' -or $seen.ContainsKey($name)) {
            throw 'connectionDeployment.identityParameters must contain unique parameter identifiers.'
        }
        $seen[$name] = $true
    }
    foreach ($name in @('StorageAccountSubscription', 'StorageAccountResourceGroupName', 'StorageAccountName', 'ContainerName')) {
        if ($name -cnotin $identityParameters) { throw "connectionDeployment.identityParameters must include '$name'." }
    }
    if ($ArmResource.eventGridUseManagedIdentity -isnot [bool] -or -not $ArmResource.eventGridUseManagedIdentity) {
        throw 'Per-instance storage requires eventGridUseManagedIdentity: true.'
    }
    if ($ArmResource.properties.auth.type -cne 'ManagedServicePrincipal') {
        throw 'Per-instance storage requires ManagedServicePrincipal collector authentication.'
    }
    $definitionId = $ArmResource.properties.connectorDefinitionName
    if ($definitionId -isnot [string] -or $definitionId -cnotmatch '^[A-Za-z0-9._-]+$' -or $definitionId -cne $CcpItem.DCDefinitionId) {
        throw 'Per-instance connectorDefinitionName must be the literal connector definition ID.'
    }
    $attribution = [pscustomobject]@{}
    if ($DeploymentConfig.PSObject.Properties.Name -contains 'attributionColumns') {
        if ($DeploymentConfig.attributionColumns -isnot [PSCustomObject]) {
            throw 'connectionDeployment.attributionColumns must be an object.'
        }
        $attribution = $DeploymentConfig.attributionColumns
    }
    $requiredParameters = @($identityParameters) + @(
        'StorageAccountSubscription', 'StorageAccountResourceGroupName', 'StorageAccountName',
        'ContainerName', 'StorageAccountLocation', 'principalId'
    ) + @($attribution.PSObject.Properties | ForEach-Object { $_.Value })
    foreach ($name in $requiredParameters | Select-Object -Unique) {
        if ($name -isnot [string] -or $name -cnotmatch '^[A-Za-z_][A-Za-z0-9_]*$' -or
            $null -eq $InstructionParameters.PSObject.Properties[$name] -or
            $InstructionParameters.$name.type -ne 'securestring') {
            throw "Per-instance parameter '$name' must be declared as a scalar input in the connector instructions."
        }
    }
    foreach ($name in @('TableName', 'EGSystemTopicName', 'blobFolderName', 'eventGridRbacMode')) {
        if ($null -ne $InstructionParameters.PSObject.Properties[$name] -and $InstructionParameters.$name.type -ne 'securestring') {
            throw "Optional per-instance parameter '$name' must be a scalar input (Textbox or Radio), not an array."
        }
    }
    foreach ($name in $identityParameters) {
        if ($name -in @('TableName', 'EGSystemTopicName', 'blobFolderName', 'eventGridRbacMode', 'StorageAccountLocation', 'principalId')) {
            throw "Mutable setting '$name' cannot be an instance identity parameter."
        }
        if ($InstructionParameters.$name.minLength -lt 1) {
            throw "Immutable identity parameter '$name' must be a required connector input."
        }
    }
    if ([string]::IsNullOrWhiteSpace($CcpItem.DCRFilePath) -or [string]::IsNullOrWhiteSpace($CcpItem.TableFilePath)) {
        throw 'Per-instance storage requires authoritative DCR and table source files.'
    }

    # Read fresh objects and retain all source properties, schema columns,
    # descriptions, tags and transform text rather than copying a vendor schema.
    $table = Get-Content -LiteralPath $CcpItem.TableFilePath -Raw -ErrorAction Stop | ConvertFrom-Json -Depth 100 -ErrorAction Stop
    $dcr = Get-Content -LiteralPath $CcpItem.DCRFilePath -Raw -ErrorAction Stop | ConvertFrom-Json -Depth 100 -ErrorAction Stop
    # Fixed per-instance names and unconditional references require exactly one
    # deployed table and DCR. Reject these controls by presence, even when false.
    foreach ($source in @(@{ Name = 'table'; Resource = $table }, @{ Name = 'DCR'; Resource = $dcr })) {
        foreach ($control in @('condition', 'copy')) {
            if ($source.Resource.PSObject.Properties.Name -contains $control) {
                throw "Per-instance $($source.Name) source does not support top-level '$control'."
            }
        }
    }
    if ($table -is [array] -or $table.type -ne 'Microsoft.OperationalInsights/workspaces/tables' -or
        $table.name -cne $DeploymentConfig.tableName -or $table.properties.schema.name -cne $DeploymentConfig.tableName -or
        $table.properties.schema.columns -isnot [array] -or $table.properties.schema.columns.Count -eq 0) {
        throw 'Per-instance table source must declare one matching table with schema.name and columns.'
    }
    foreach ($column in $attribution.PSObject.Properties.Name) {
        $declared = @($table.properties.schema.columns | Where-Object { $_.name -ceq $column -and $_.type -eq 'string' })
        if ($declared.Count -ne 1) { throw "Attribution column '$column' must be declared once as a string in the authoritative table schema." }
    }
    if ($dcr -is [array] -or $dcr.type -ne 'Microsoft.Insights/dataCollectionRules' -or
        @($dcr.properties.destinations.logAnalytics).Count -ne 1 -or
        [string]::IsNullOrWhiteSpace($dcr.properties.destinations.logAnalytics[0].name) -or
        $dcr.properties.dataFlows -isnot [array] -or $dcr.properties.dataFlows.Count -eq 0) {
        throw 'Per-instance DCR source must declare one Log Analytics destination and at least one data flow.'
    }
    $streamName = $ArmResource.properties.dcrConfig.streamName
    if ($streamName -isnot [string] -or
        $streamName -cnotin @($dcr.properties.streamDeclarations.PSObject.Properties.Name) -or
        $streamName -cnotin @($dcr.properties.dataFlows.streams)) {
        throw 'Per-instance poller streamName must name an input stream declared and routed by the authoritative DCR.'
    }
    $sourceTransforms = [ordered]@{}
    foreach ($flow in $dcr.properties.dataFlows) {
        if ($flow.outputStream -cne "Custom-$($DeploymentConfig.tableName)" -or
            @($flow.destinations).Count -ne 1 -or $flow.destinations[0] -cne $dcr.properties.destinations.logAnalytics[0].name) {
            throw 'Every per-instance DCR data flow must route to the configured source table and Log Analytics destination.'
        }
        foreach ($stream in $flow.streams) {
            if ($stream -cnotin @($dcr.properties.streamDeclarations.PSObject.Properties.Name)) {
                throw "DCR data flow references undeclared input stream '$stream'."
            }
        }
        $flow.outputStream = "[[variables('outputStreamName')]"
        if (@($attribution.PSObject.Properties).Count -gt 0) {
            $transformVariable = "perInstanceSourceTransform$($sourceTransforms.Count)"
            $sourceTransforms[$transformVariable] = $flow.transformKql
            $flow.transformKql = Get-PerInstanceAttributionTransform -Transform $flow.transformKql `
                -Attribution $attribution -TransformVariableName $transformVariable
        }
    }

    $template = $TemplateContentConnections.properties.mainTemplate
    foreach ($parameter in $InstructionParameters.PSObject.Properties) {
        if ($parameter.Name -notin @('dcrConfig', 'guidValue')) {
            $template.parameters | Add-Member -NotePropertyName $parameter.Name -NotePropertyValue $parameter.Value -Force
        }
    }
    foreach ($name in @('dcrConfig', 'guidValue')) { $template.parameters.PSObject.Properties.Remove($name) }
    . (Join-Path $PSScriptRoot 'eventGridManagedIdentityDeploymentTemplate.ps1')
    foreach ($parameterSet in @($template.parameters, $InstructionParameters)) {
        # Keep UI-derived parameters synchronized with the final dispatcher merge.
        foreach ($name in @('TableName', 'EGSystemTopicName', 'blobFolderName')) {
            $parameterSet | Add-Member -NotePropertyName $name -NotePropertyValue ([pscustomobject]@{ type = 'securestring'; defaultValue = '' }) -Force
        }
        $parameterSet | Add-Member -NotePropertyName 'eventGridRbacMode' -NotePropertyValue (Get-EventGridRbacModeParameter -IncludeDefault) -Force
    }

    $variables = [ordered]@{}
    foreach ($property in $template.variables.PSObject.Properties) { $variables[$property.Name] = $property.Value }
    foreach ($name in $sourceTransforms.Keys) { $variables[$name] = $sourceTransforms[$name] }
    $identityExpressions = @($identityParameters | ForEach-Object { "toLower(trim(parameters('$_')))" })
    # Do not reorder/sort identity inputs or change this workspace hash: existing
    # PR14792 instances must reconnect to the same connector, queues, DCR and DCE.
    $identityExpressions += "toLower(variables('workspaceResourceId'))"
    $variables['resourcePrefix'] = $DeploymentConfig.resourcePrefix
    $variables['queuePrefix'] = $DeploymentConfig.queuePrefix
    $variables['tableNameDefault'] = $DeploymentConfig.tableName
    $variables['tableName'] = "[[if(empty(trim(parameters('TableName'))), variables('tableNameDefault'), trim(parameters('TableName')))]"
    $variables['outputStreamName'] = "[[concat('Custom-', variables('tableName'))]"
    $variables['workspaceResourceId'] = "[[resourceId('Microsoft.OperationalInsights/workspaces', parameters('innerWorkspace'))]"
    $variables['instanceKey'] = "[[uniqueString($($identityExpressions -join ', '))]"
    foreach ($name in @('connectorName', 'dcrName', 'dceName')) {
        $variables[$name] = "[[format('{0}-{1}', variables('resourcePrefix'), variables('instanceKey'))]"
    }
    $variables['diagnosticSettingName'] = "[[format('{0}-{1}-logerrors', variables('resourcePrefix'), variables('instanceKey'))]"
    $variables['storageAccountName'] = "[[toLower(trim(parameters('StorageAccountName')))]"
    $variables['blobContainerName'] = "[[toLower(trim(parameters('ContainerName')))]"
    $variables['queueName'] = "[[format('{0}-{1}-notification', variables('queuePrefix'), variables('instanceKey'))]"
    $variables['dlqName'] = "[[format('{0}-{1}-dlq', variables('queuePrefix'), variables('instanceKey'))]"
    $storageScope = "trim(parameters('StorageAccountSubscription')), trim(parameters('StorageAccountResourceGroupName'))"
    $variables['storageAccountId'] = "[[resourceId($storageScope, 'Microsoft.Storage/storageAccounts', variables('storageAccountName'))]"
    $variables['blobContainerResourceId'] = "[[resourceId($storageScope, 'Microsoft.Storage/storageAccounts/blobServices/containers', variables('storageAccountName'), 'default', variables('blobContainerName'))]"
    $variables['notificationQueueResourceId'] = "[[resourceId($storageScope, 'Microsoft.Storage/storageAccounts/queueServices/queues', variables('storageAccountName'), 'default', variables('queueName'))]"
    $variables['dlqResourceId'] = "[[resourceId($storageScope, 'Microsoft.Storage/storageAccounts/queueServices/queues', variables('storageAccountName'), 'default', variables('dlqName'))]"
    # A storage account has one system topic, shared by its isolated subscriptions.
    $variables['EGSystemTopicDefaultName'] = "[[format('sentinel-{0}-{1}', variables('resourcePrefix'), uniqueString(toLower(trim(parameters('StorageAccountSubscription'))), toLower(trim(parameters('StorageAccountResourceGroupName'))), variables('storageAccountName')))]"
    $variables['EGSystemTopicName'] = "[[if(empty(parameters('EGSystemTopicName')), variables('EGSystemTopicDefaultName'), parameters('EGSystemTopicName'))]"
    $variables['EGTopicResourceId'] = "[[resourceId($storageScope, 'Microsoft.EventGrid/systemTopics', variables('EGSystemTopicName'))]"
    $variables['EgSubscriptionName'] = "[[format('{0}-{1}-blobcreated', variables('resourcePrefix'), variables('instanceKey'))]"
    $variables['EgSubscriptionResourceId'] = "[[resourceId($storageScope, 'Microsoft.EventGrid/systemTopics/eventSubscriptions', variables('EGSystemTopicName'), variables('EgSubscriptionName'))]"
    $variables['storageBlobReaderRoleId'] = "[[subscriptionResourceId(trim(parameters('StorageAccountSubscription')), 'Microsoft.Authorization/roleDefinitions', '2a2b9908-6ea1-4ae2-8e65-a410df84e7d1')]"
    $variables['storageQueueContributorRoleId'] = "[[subscriptionResourceId(trim(parameters('StorageAccountSubscription')), 'Microsoft.Authorization/roleDefinitions', '974c5e8b-45b9-4653-ba55-5f855dd0fb88')]"
    # Keep the previous scope/principal/role-keyed queue GUIDs. Reader uses a
    # different role key from the old Contributor grant, never a role downgrade
    # behind an immutable assignment ID. Old grants are not deleted.
    $variables['blobRaGuid'] = "[[guid(variables('blobContainerResourceId'), parameters('principalId'), variables('storageBlobReaderRoleId'))]"
    $variables['notificationQueueRaGuid'] = "[[guid(variables('notificationQueueResourceId'), parameters('principalId'), variables('storageQueueContributorRoleId'))]"
    $variables['dlqRaGuid'] = "[[guid(variables('dlqResourceId'), parameters('principalId'), variables('storageQueueContributorRoleId'))]"
    $variables['dceResourceId'] = "[[resourceId('Microsoft.Insights/dataCollectionEndpoints', variables('dceName'))]"
    $variables['dcrResourceId'] = "[[resourceId('Microsoft.Insights/dataCollectionRules', variables('dcrName'))]"
    $variables['tableResourceId'] = "[[resourceId('Microsoft.OperationalInsights/workspaces/tables', parameters('innerWorkspace'), variables('tableName'))]"
    $variables['nestedDeploymentName'] = "[[format('{0}-{1}-storage', variables('resourcePrefix'), variables('instanceKey'))]"
    $variables['nestedDeploymentId'] = "[[resourceId($storageScope, 'Microsoft.Resources/deployments', variables('nestedDeploymentName'))]"
    $template.variables = $variables

    $table.name = "[[concat(parameters('innerWorkspace'), '/', variables('tableName'))]"
    $table.properties.schema.name = "[[variables('tableName')]"
    $table | Add-Member -NotePropertyName 'location' -NotePropertyValue "[parameters('workspace-location')]" -Force
    # Match Get-ArmResource's deployment API policy. Source schemas/transforms
    # are authoritative, but obsolete/private-preview authoring APIs are not.
    $table | Add-Member -NotePropertyName 'apiVersion' -NotePropertyValue '2022-10-01' -Force
    $dce = [ordered]@{
        type = 'Microsoft.Insights/dataCollectionEndpoints'
        apiVersion = '2022-06-01'
        name = "[[variables('dceName')]"
        location = "[parameters('workspace-location')]"
        properties = @{ networkAcls = @{ publicNetworkAccess = 'Enabled' } }
    }
    $dcr.name = "[[variables('dcrName')]"
    $dcr | Add-Member -NotePropertyName 'location' -NotePropertyValue "[parameters('workspace-location')]" -Force
    $dcr | Add-Member -NotePropertyName 'apiVersion' -NotePropertyValue '2022-06-01' -Force
    $dcr.properties | Add-Member -NotePropertyName 'dataCollectionEndpointId' -NotePropertyValue "[[variables('dceResourceId')]" -Force
    $dcr.properties.destinations.logAnalytics[0] | Add-Member -NotePropertyName 'workspaceResourceId' -NotePropertyValue "[[variables('workspaceResourceId')]" -Force
    $dcr | Add-Member -NotePropertyName 'dependsOn' -NotePropertyValue @(
        @($dcr.dependsOn | Where-Object { $null -ne $_ }) + @("[[variables('dceResourceId')]", "[[variables('tableResourceId')]") | Select-Object -Unique
    ) -Force
    $template.resources += @($table, $dce, $dcr)
    if ($DeploymentConfig.enableDcrLogErrors -eq $true) {
        $template.resources += [ordered]@{
            type = 'Microsoft.Insights/diagnosticSettings'
            apiVersion = '2021-05-01-preview'
            name = "[[variables('diagnosticSettingName')]"
            scope = "[[variables('dcrResourceId')]"
            dependsOn = @("[[variables('dcrResourceId')]")
            properties = @{
                workspaceId = "[[variables('workspaceResourceId')]"
                logs = @(@{ category = 'LogErrors'; enabled = $true })
            }
        }
    }

    $advancedFilters = $ArmResource.eventGridAdvancedFilters
    $ArmResource.PSObject.Properties.Remove('eventGridAdvancedFilters')
    $ArmResource.PSObject.Properties.Remove('eventGridUseManagedIdentity')
    $storageDeployment = Get-StorageAccountDeploymentTemplate -eventGridUseManagedIdentity $true `
        -isManagedServicePrincipal $true -resourceVariables $variables -eventGridAdvancedFilters $advancedFilters
    $storageDeployment.subscriptionId = "[[trim(parameters('StorageAccountSubscription'))]"
    $storageDeployment.resourceGroup = "[[trim(parameters('StorageAccountResourceGroupName'))]"
    $template.resources += $storageDeployment

    $ArmResource.name = "[[concat(parameters('innerWorkspace'), '/Microsoft.SecurityInsights/', variables('connectorName'))]"
    $ArmResource.properties.dataType = "[[variables('tableName')]"
    if ($null -eq $ArmResource.properties.request) {
        $ArmResource.properties | Add-Member -NotePropertyName 'request' -NotePropertyValue ([pscustomobject]@{}) -Force
    }
    foreach ($entry in @(@('QueueUri', 'queueName'), @('DlqUri', 'dlqName'))) {
        $ArmResource.properties.request | Add-Member -NotePropertyName $entry[0] -NotePropertyValue "[[uri(concat('https://', variables('storageAccountName'), '.queue.', environment().suffixes.storage, '/'), variables('$($entry[1])'))]" -Force
    }
    $ArmResource.properties.dcrConfig.dataCollectionEndpoint = "[[reference(variables('dceResourceId'), '2022-06-01').logsIngestion.endpoint]"
    $ArmResource.properties.dcrConfig.dataCollectionRuleImmutableId = "[[reference(variables('dcrResourceId'), '2022-06-01').immutableId]"
    $ArmResource | Add-Member -NotePropertyName 'dependsOn' -NotePropertyValue @(
        @($ArmResource.dependsOn | Where-Object { $null -ne $_ }) + @(
            "[[variables('dcrResourceId')]", "[[variables('dceResourceId')]", "[[variables('nestedDeploymentId')]"
        ) | Select-Object -Unique
    ) -Force
    $ArmResource.properties = Convert-CCPPropertyPlaceholders -Value $ArmResource.properties -templateContentConnections $TemplateContentConnections
}
