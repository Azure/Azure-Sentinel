$jsonConversionDepth = 50
$path = "$PSScriptRoot\input"

function handleEmptyInstructionProperties ($inputObj) {
    $outputObj = $inputObj |
    Get-Member -MemberType *Property |
    Select-Object -ExpandProperty Name |
    Sort-Object |
    ForEach-Object -Begin { $obj = New-Object PSObject } {
        if (($null -eq $inputObj.$_) -or ($inputObj.$_ -eq "") -or ($inputObj.$_.Count -eq 0)) {
            Write-Host "Removing empty property $_"
        }
        else {
            $obj | Add-Member -memberType NoteProperty -Name $_ -Value $inputObj.$_
        }
    } { $obj }
    $outputObj
}
function removePropertiesRecursively ($resourceObj) {
    foreach ($prop in $resourceObj.PsObject.Properties) {
        $key = $prop.Name
        $val = $prop.Value
        if ($null -eq $val) {
            $resourceObj.PsObject.Properties.Remove($key)
        }
        elseif ($val -is [System.Object[]]) {
            if ($val.Count -eq 0) {
                $resourceObj.PsObject.Properties.Remove($key)
            }
            else {
                foreach ($item in $val) {
                    $itemIndex = $val.IndexOf($item)
                    $resourceObj.$key[$itemIndex] = $(removePropertiesRecursively $val[$itemIndex])
                }
            }
        }
        else {
            if ($val -is [PSCustomObject]) {
                if ($($val.PsObject.Properties).Count -eq 0) {
                    $resourceObj.PsObject.Properties.Remove($key)
                }
                else {
                    $resourceObj.$key = $(removePropertiesRecursively $val)
                    if ($($resourceObj.$key.PsObject.Properties).Count -eq 0) {
                        $resourceObj.PsObject.Properties.Remove($key)
                    }
                }
            }
        }
    }
    $resourceObj
}

function queryResourceExists () {
    foreach ($resource in $baseMainTemplate.resources) {
        if ($resource.type -eq "Microsoft.OperationalInsights/workspaces") {
            return $true
        }
    }
    return $false
}

function getQueryResourceLocation () {
    for($i = 0; $i -lt $baseMainTemplate.resources.Length; $i++){
        if ($baseMainTemplate.resources[$i].type -eq "Microsoft.OperationalInsights/workspaces") {
            return $i
        }
    }
}

foreach ($inputFile in $(Get-ChildItem $path)) {
    $inputJsonPath = Join-Path -Path $path -ChildPath "$($inputFile.Name)"

    $contentToImport = Get-Content -Raw $inputJsonPath | Out-String | ConvertFrom-Json
    $basePath = $(if ($contentToImport.BasePath) { $contentToImport.BasePath + "/" } else { "https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/" })

    # Content Counters - (for adding numbering to each item)
    $analyticRuleCounter = 1
    $connectorCounter = 1
    $workbookCounter = 1
    $playbookCounter = 1
    $parserCounter = 1
    $savedSearchCounter = 1
    $huntingQueryCounter = 1
    $watchlistCounter = 1

    # Convenience Variables
    $solutionName = $contentToImport.Name
	

    # Base JSON Object Paths
    $baseMainTemplatePath = "$PSScriptRoot/templating/baseMainTemplate.json"
    $baseCreateUiDefinitionPath = "$PSScriptRoot/templating/baseCreateUiDefinition.json"

    # Base JSON Objects
    $baseMainTemplate = Get-Content -Raw $baseMainTemplatePath | Out-String | ConvertFrom-Json
    $baseCreateUiDefinition = Get-Content -Raw $baseCreateUiDefinitionPath | Out-String | ConvertFrom-Json

    $DependencyCriteria = @();

    foreach ($objectProperties in $contentToImport.PsObject.Properties) {
        # Access the value of the property
        if ($objectProperties.Value -is [System.Array]) {
            foreach ($file in $objectProperties.Value) {
                $finalPath = $basePath + $file
                $rawData = $null
                try {
                    Write-Host "Downloading $file"
                    $rawData = (New-Object System.Net.WebClient).DownloadString($finalPath)
                }
                catch {
                    Write-Host "Failed to download $file -- Please ensure that it exists in $([System.Uri]::EscapeUriString($basePath))" -ForegroundColor Red
                    break;
                }

                try {
                    $json = ConvertFrom-Json $rawData -ErrorAction Stop; # Determine whether content is JSON or YAML
                    $validJson = $true;
                }
                catch {
                    $validJson = $false;
                }
				#Replace the special characters in the solution name.
				function Replace-SpecialChars {
				param($InputString,$Type)
					if ($Type.ToLower() -eq 'solutionname') {
						$SpecialChars = '[#?\{\[\(\)\]\}]'
						$Replacement  = ' '
					}
					elseif ($Type.ToLower() -eq 'filename') {
						$SpecialChars = '[#?\{\[\(\)\]\}]'
						$Replacement  = ''
					}
					else {
						$SpecialChars = '[#?\{\[\(\)\]\}]'
						$Replacement  = ''
					}
				return $InputString -replace $SpecialChars,$Replacement
				}

                if ($validJson) {
                    # If valid JSON, must be Workbook or Playbook
                    $objectKeyLowercase = $objectProperties.Name.ToLower()
                    if ($objectKeyLowercase -eq "workbooks") {
                        Write-Host "Generating Workbook using $file"
						#$solutionName = $solutionName -replace '[(]',' ' -replace '[)]','';
						$solutionRename = Replace-SpecialChars -InputString $solutionName -Type 'solutionname'
                        $fileName = Split-Path $file -leafbase;
						#$fileName = $fileName -replace '[(\)]','';
						$fileName = Replace-SpecialChars -InputString $fileName -Type 'filename'
                        $fileName = $fileName + "_workbook";
                        $baseMainTemplate.variables | Add-Member -NotePropertyName $fileName -NotePropertyValue $fileName
                        $baseMainTemplate.variables | Add-Member -NotePropertyName "_$fileName" -NotePropertyValue "[variables('$fileName')]"

                        $DependencyCriteria += [PSCustomObject]@{
                            kind      = "Workbook";
                            contentId = "[variables('_$fileName')]";
                            version   = $contentToImport.Version;
                        };

                        if ($workbookCounter -eq 1) {
                            # Add workbook source variables
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "workbook-source" -NotePropertyValue "[concat(resourceGroup().id, '/providers/Microsoft.OperationalInsights/workspaces/',parameters('workspace'))]"
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "_workbook-source" -NotePropertyValue "[variables('workbook-source')]"

                            $baseWorkbookStep = [PSCustomObject] @{
                                name       = "workbooks";
                                label      = "Workbooks";
                                subLabel   = [PSCustomObject] @{
                                    preValidation  = "Configure the workbooks";
                                    postValidation = "Done";
                                };
                                bladeTitle = "Workbooks";
                                elements   = @(
                                    [PSCustomObject] @{
                                        name    = "workbooks-text";
                                        type    = "Microsoft.Common.TextBlock";
                                        options = [PSCustomObject] @{
                                            text = "This Microsoft Sentinel Solution installs workbooks. Workbooks provide a flexible canvas for data monitoring, analysis, and the creation of rich visual reports within the Azure portal. They allow you to tap into one or many data sources from Microsoft Sentinel and combine them into unified interactive experiences.";
                                            link = [PSCustomObject] @{
                                                label = "Learn more";
                                                uri   = "https://docs.microsoft.com/azure/sentinel/tutorial-monitor-your-data";
                                            }
                                        }
                                    }
                                )
                            }
                            $baseCreateUiDefinition.parameters.steps += $baseWorkbookStep
                            #Add formattedTimeNow parameter since workbooks exist
                            $timeNowParameter = [PSCustomObject]@{
                                type         = "string";
                                defaultValue = "[utcNow('g')]";
                                metadata     = [PSCustomObject]@{
                                    description = "Appended to workbook displayNames to make them unique";
                                }
                            }
                            $baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name "formattedTimeNow" -Value $timeNowParameter
                        }
                        try {
                            $data = $rawData
                            # Serialize workbook data
                            $serializedData = $data |  ConvertFrom-Json -Depth $jsonConversionDepth
                            # Remove empty braces
                            $serializedData = $(removePropertiesRecursively $serializedData) | ConvertTo-Json -Compress -Depth $jsonConversionDepth | Out-String
                        }
                        catch {
                            Write-Host "Failed to serialize $file" -ForegroundColor Red
                            break;
                        }
                        $workbookDescriptionText = $(if ($contentToImport.WorkbookDescription -and $contentToImport.WorkbookDescription -is [System.Array]) { $contentToImport.WorkbookDescription[$workbookCounter - 1] } elseif ($contentToImport.WorkbookDescription -and $contentToImport.WorkbookDescription -is [System.String]) { $contentToImport.WorkbookDescription } else { "" })
						
                        $workbookUiParameter = [PSCustomObject] @{
                            name     = "workbook$workbookCounter";
                            type     = "Microsoft.Common.Section";
                            label    = $solutionName;
                            elements = @(
                                [PSCustomObject] @{
                                    name    = "workbook$workbookCounter-text";
                                    type    = "Microsoft.Common.TextBlock";
                                    options = [PSCustomObject] @{ text = $workbookDescriptionText; }
                                },
                                [PSCustomObject] @{
                                    name         = "workbook$workbookCounter-name";
                                    type         = "Microsoft.Common.TextBox";
                                    label        = "Display Name";
                                    defaultValue = $solutionRename.trimEnd();
                                    toolTip      = "Display name for the workbook.";
                                    constraints  = [PSCustomObject] @{
                                        required          = $true;
                                        regex             = "[a-z0-9A-Z]{1,256}$";
                                        validationMessage = "Please enter a workbook name"
                                    }
                                }
                            )
                        }
                        #creating parameters in mainTemplate
                        $workbookIDParameterName = "workbook$workbookCounter-id"
                        $workbookNameParameterName = "workbook$workbookCounter-name"
                        $workbookIDParameter = [PSCustomObject] @{ type = "string"; defaultValue = "[newGuid()]"; minLength = 1; metadata = [PSCustomObject] @{ description = "Unique id for the workbook" }; }
                        $workbookNameParameter = [PSCustomObject] @{ type = "string"; defaultValue = $solutionRename.trimEnd(); minLength = 1; metadata = [PSCustomObject] @{ description = "Name for the workbook" }; }

                        # Create Workbook Resource Object
                        $newWorkbook = [PSCustomObject]@{
                            type       = "Microsoft.Insights/workbooks";
                            name       = "[parameters('workbook$workbookCounter-id')]";
                            location   = "[parameters('workspace-location')]";
                            kind       = "shared";
                            apiVersion = "2021-08-01";
                            properties = [PSCustomObject] @{
                                displayName    = "[concat(parameters('workbook$workbookCounter-name'), ' - ', parameters('formattedTimeNow'))]";
                                serializedData = $serializedData;
                                version        = "1.0";
                                sourceId       = "[variables('_workbook-source')]";
                                category       = "sentinel"
                            }
                        }

                        $baseMainTemplate.resources += $newWorkbook
                        $baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name $workbookIDParameterName -Value $workbookIDParameter
                        $baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name $workbookNameParameterName -Value $workbookNameParameter

                        $baseCreateUiDefinition.parameters.steps[$baseCreateUiDefinition.parameters.steps.Count - 1].elements += $workbookUiParameter
                        $baseCreateUiDefinition.parameters.outputs | Add-Member -NotePropertyName "workbook$workbookCounter-name" -NotePropertyValue "[steps('workbooks').workbook$workbookCounter.workbook$workbookCounter-name]"

                        $workbookCounter += 1
                    }
                    elseif ($objectKeyLowercase -eq "playbooks") {
                        Write-Host "Generating Playbook using $file"
                        $playbookData = $json
                        $playbookName = $(if ($playbookData.parameters.PlaybookName) { $playbookData.parameters.PlaybookName.defaultValue }elseif ($playbookData.parameters."Playbook Name") { $playbookData.parameters."Playbook Name".defaultValue })

                        $fileName = Split-path -Parent $file | Split-Path -leaf
                        $fileName = "playbook$playbookCounter-$fileName";
                        $baseMainTemplate.variables | Add-Member -NotePropertyName $fileName -NotePropertyValue $fileName
                        $baseMainTemplate.variables | Add-Member -NotePropertyName "_$fileName" -NotePropertyValue "[variables('$fileName')]"

                        $DependencyCriteria += [PSCustomObject]@{
                            kind      = "Playbook";
                            contentId = "[variables('_$fileName')]";
                            version   = $contentToImport.Version;
                        };

                        if ($playbookCounter -eq 1) {
                            # If a playbook exists, add CreateUIDefinition step before playbook elements while handling first playbook.
                            $playbookStep = [PSCustomObject] @{
                                name       = "playbooks";
                                label      = "Playbooks";
                                subLabel   = [PSCustomObject] @{
                                    preValidation  = "Configure the playbooks";
                                    postValidation = "Done";
                                };
                                bladeTitle = "Playbooks";
                                elements   = @(
                                    [PSCustomObject] @{
                                        name    = "playbooks-text";
                                        type    = "Microsoft.Common.TextBlock";
                                        options = [PSCustomObject] @{
                                            text = "This solution installs playbook resources.  A security playbook is a collection of procedures that can be run from Microsoft Sentinel in response to an alert. A security playbook can help automate and orchestrate your response, and can be run manually or set to run automatically when specific alerts are triggered. Security playbooks in Microsoft Sentinel are based on Azure Logic Apps, which means that you get all the power, customizability, and built-in templates of Logic Apps. Each playbook is created for the specific subscription you choose, but when you look at the Playbooks page, you will see all the playbooks across any selected subscriptions.";
                                            link = [PSCustomObject] @{
                                                label = "Learn more";
                                                uri   = "https://docs.microsoft.com/azure/sentinel/tutorial-respond-threats-playbook?WT.mc_id=Portal-Microsoft_Azure_CreateUIDef"
                                            };
                                        };
                                    }
                                )
                            }
                            $baseCreateUiDefinition.parameters.steps += $playbookStep
                        }
                        $playbookElement = [PSCustomObject] @{
                            name     = "playbook$playbookCounter";
                            type     = "Microsoft.Common.Section";
                            label    = $playbookName;
                            elements = @(
                                [PSCustomObject] @{
                                    name    = "playbook$playbookCounter-text";
                                    type    = "Microsoft.Common.TextBlock";
                                    options = [PSCustomObject] @{ text = if ($playbookData.metadata -and $playbookData.metadata.comments) { $playbookData.metadata.comments } else { "This playbook ingests events from $solutionName into Log Analytics using the API." } }
                                }
                            )
                        }
                        $currentStepNum = $baseCreateUiDefinition.parameters.steps.Count - 1
                        $baseCreateUiDefinition.parameters.steps[$currentStepNum].elements += $playbookElement

                        foreach ($param in $playbookData.parameters.PsObject.Properties) {
                            $paramName = $param.Name
                            $defaultParamValue = $(if ($playbookData.parameters.$paramName.defaultValue) { $playbookData.parameters.$paramName.defaultValue } else { "" })
                            if ($param.Name.ToLower().contains("playbookname")) {
                                $playbookNameObject = [PSCustomObject] @{
                                    name         = "playbook$playbookCounter-$paramName";
                                    type         = "Microsoft.Common.TextBox";
                                    label        = "Playbook Name";
                                    defaultValue = $defaultParamValue;
                                    toolTip      = "Resource name for the logic app playbook.  No spaces are allowed";
                                    constraints  = [PSCustomObject] @{
                                        required          = $true;
                                        regex             = "[a-z0-9A-Z]{1,256}$";
                                        validationMessage = "Please enter a playbook resource name"
                                    }
                                }
                                $baseCreateUiDefinition.parameters.steps[$currentStepNum].elements[$baseCreateUiDefinition.parameters.steps[$currentStepNum].elements.Length - 1].elements += $playbookNameObject
                                $baseMainTemplate.parameters | Add-Member -NotePropertyName "playbook$playbookCounter-$paramName" -NotePropertyValue ([PSCustomObject] @{
                                        defaultValue = $playbookName;
                                        type         = "string";
                                        minLength    = 1;
                                        metadata     = [PSCustomObject] @{ description = "Resource name for the logic app playbook.  No spaces are allowed"; }
                                    })
                            }
                            elseif ($param.Name.ToLower().contains("username")) {
                                $playbookUsernameObject = [PSCustomObject] @{
                                    name         = "playbook$playbookCounter-$paramName";
                                    type         = "Microsoft.Common.TextBox";
                                    label        = "$solutionName Username";
                                    defaultValue = $defaultParamValue;
                                    toolTip      = "Username to connect to $solutionName API";
                                    constraints  = [PSCustomObject] @{
                                        required          = $true;
                                        regex             = "[a-z0-9A-Z]{1,256}$";
                                        validationMessage = "Please enter a playbook username";
                                    }
                                }
                                $baseCreateUiDefinition.parameters.steps[$currentStepNum].elements[$baseCreateUiDefinition.parameters.steps[$currentStepNum].elements.Length - 1].elements += $playbookUsernameObject
                                $baseMainTemplate.parameters | Add-Member -NotePropertyName "playbook$playbookCounter-$paramName" -NotePropertyValue ([PSCustomObject] @{
                                        defaultValue = $defaultParamValue;
                                        type         = "string";
                                        minLength    = 1;
                                        metadata     = [PSCustomObject] @{ description = "Username to connect to $solutionName API" }
                                    })
                            }
                            elseif ($param.Name.ToLower().contains("password")) {
                                $playbookPasswordObject = [PSCustomObject] @{
                                    name        = "playbook$playbookCounter-$paramName";
                                    type        = "Microsoft.Common.PasswordBox";
                                    label       = [PSCustomObject] @{ password = $defaultParamValue; };
                                    toolTip     = "Password to connect to $solutionName API";
                                    constraints = [PSCustomObject] @{ required = $true; };
                                    options     = [PSCustomObject] @{ hideConfirmation = $false; };
                                }
                                $baseCreateUiDefinition.parameters.steps[$currentStepNum].elements[$baseCreateUiDefinition.parameters.steps[$currentStepNum].elements.Length - 1].elements += $playbookPasswordObject
                                $baseMainTemplate.parameters | Add-Member -NotePropertyName "playbook$playbookCounter-$paramName" -NotePropertyValue ([PSCustomObject] @{
                                        type      = "securestring";
                                        minLength = 1;
                                        metadata  = [PSCustomObject] @{ description = "Password to connect to $solutionName API"; }
                                    }
								)
                            }
							elseif ($param.Name.ToLower().contains("apikey")) {
                                $playbookPasswordObject = [PSCustomObject] @{
                                    name        = "playbook$playbookCounter-$paramName";
                                    type        = "Microsoft.Common.PasswordBox";
                                    label       = [PSCustomObject] @{password = "ApiKey"};
                                    toolTip     = "ApiKey to connect to $solutionName API";
                                    constraints = [PSCustomObject] @{ required = $true; };
                                    options     = [PSCustomObject] @{ hideConfirmation = $true; };
                                }
                                $baseCreateUiDefinition.parameters.steps[$currentStepNum].elements[$baseCreateUiDefinition.parameters.steps[$currentStepNum].elements.Length - 1].elements += $playbookPasswordObject
                                $baseMainTemplate.parameters | Add-Member -NotePropertyName "playbook$playbookCounter-$paramName" -NotePropertyValue ([PSCustomObject] @{
                                        type      = "securestring";
                                        minLength = 1;
                                        metadata  = [PSCustomObject] @{ description = "ApiKey to connect to $solutionName API"; }
                                    })
                            }
                            else {
                                function PascalSplit ($pascalStr) {
                                    foreach ($piece in $pascalStr) {
                                        if ($piece -is [array]) {
                                            foreach ($subPiece in $piece) { PascalSplit $subPiece }
                                        }
                                        else {
                                            ($piece.ToString() -creplace '[A-Z]', ' $&').Trim().Split($null)
                                        }
                                    }
                                }

                                $playbookParamObject = $(
                                    if ($playbookData.parameters.$paramName.allowedValues) {
                                        [PSCustomObject] @{
                                            name         = "playbook$playbookCounter-$paramName";
                                            type         = "Microsoft.Common.DropDown";
                                            label        = "$(PascalSplit $paramName)";
                                            placeholder  = "$($playbookData.parameters.$paramName.allowedValues[0])";
                                            defaultValue = "$($playbookData.parameters.$paramName.allowedValues[0])";
                                            toolTip      = "Please enter $(if($paramName.IndexOf("-") -ne -1){$paramName}else{PascalSplit $paramName})";
                                            constraints  = [PSCustomObject] @{
                                                allowedValues = $playbookData.parameters.$paramName.allowedValues | ForEach-Object {
                                                    [PSCustomObject] @{
                                                        label = $_;
                                                        value = $_;
                                                    }
                                                }
                                                required      = $true;
                                            }
                                            visible      = $true;
                                        }
                                    }
                                    else {
                                        [PSCustomObject] @{
                                            name         = "playbook$playbookCounter-$paramName";
                                            type         = "Microsoft.Common.TextBox";
                                            label        = "$(PascalSplit $paramName)";
                                            defaultValue = $defaultParamValue;
                                            toolTip      = "Please enter $(if($paramName.IndexOf("-") -ne -1){$paramName}else{PascalSplit $paramName})";
                                            constraints  = [PSCustomObject] @{
                                                required          = $true;
                                                regex             = "[a-z0-9A-Z]{1,256}$";
                                                validationMessage = "Please enter the $(PascalSplit $paramName)"
                                            }
                                        }
                                    }
                                )
                                $baseCreateUiDefinition.parameters.steps[$currentStepNum].elements[$baseCreateUiDefinition.parameters.steps[$currentStepNum].elements.Length - 1].elements += $playbookParamObject
                                $defaultValue = $(if ($defaultParamValue) { $defaultParamValue } else { "" })
                                $baseMainTemplate.parameters | Add-Member -NotePropertyName "playbook$playbookCounter-$paramName" -NotePropertyValue ([PSCustomObject] @{
                                        defaultValue = $defaultValue;
                                        type         = "string";
                                        minLength    = 1;
                                    })
                            }
                            $baseCreateUiDefinition.parameters.outputs | Add-Member -NotePropertyName "playbook$playbookCounter-$paramName" -NotePropertyValue "[steps('playbooks').playbook$playbookCounter.playbook$playbookCounter-$paramName]"
                        }

                        foreach ($playbookVariable in $playbookData.variables.PsObject.Properties) {
                            $variableName = $playbookVariable.Name
                            $variableValue = $playbookVariable.Value
                            if ($variableValue -is [System.String]) {
                                $variableValue = $(node "$PSScriptRoot/templating/replacePlaybookParamNames.js" $variableValue $playbookCounter)
                            }
                            if (($solutionName.ToLower() -eq "cisco meraki") -and ($variableName.ToLower().contains("apikey")))
                            {
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "playbook-$variableName" -NotePropertyValue "[$variableValue]"
                            }
                            else
                            {
                                $baseMainTemplate.variables | Add-Member -NotePropertyName "playbook$playbookCounter-$variableName" -NotePropertyValue $variableValue
                            }                           
                        }

                        $azureManagementUrlExists = $false
                        $azureManagementUrl = "management.azure.com"

                        function replaceQuotes ($inputStr) {
                            $baseStr = $resourceObj.$key
                            $outputStr = $baseStr.Replace("`"", "\`"")
                            $outputStr
                        }
                        function replaceVarsRecursively ($resourceObj) {
                            if ($resourceObj.GetType() -ne [System.DateTime]) {
                                foreach ($prop in $resourceObj.PsObject.Properties) {
                                    $key = $prop.Name
                                    if ($prop.Value -is [System.String]) {
                                        $resourceObj.$key = $(node "$PSScriptRoot/templating/replacePlaybookParamNames.js" "$(replaceQuotes $resourceObj.$key)" $playbookCounter)
                                        if ($resourceObj.$key.StartsWith("[") -and $resourceObj.$key[$resourceObj.$key.Length - 1] -eq "]") {
                                            $resourceObj.$key = $(node "$PSScriptRoot/templating/replacePlaybookVarNames.js" "$(replaceQuotes $resourceObj.$key)" $playbookCounter)
                                        }
                                        $resourceObj.$key = $(node "$PSScriptRoot/templating/replaceLocationValue.js" "$(replaceQuotes $resourceObj.$key)" $playbookCounter)
                                        if ($resourceObj.$key.IndexOf($azureManagementUrl)) {
                                            $resourceObj.$key = $resourceObj.$key.Replace($azureManagementUrl, "@{variables('azureManagementUrl')}")
                                            $azureManagementUrlExists = $true
                                        }
                                        if ($key -eq "operationId") {
                                            $baseMainTemplate.variables | Add-Member -NotePropertyName "operationId-$($resourceobj.$key)" -NotePropertyValue $($resourceobj.$key)
                                            $baseMainTemplate.variables | Add-Member -NotePropertyName "_operationId-$($resourceobj.$key)" -NotePropertyValue "[variables('operationId-$($resourceobj.$key)')]"
                                            $resourceObj.$key = "[variables('_operationId-$($resourceobj.$key)')]"
                                        }
                                    }
                                    elseif ($prop.Value -is [System.Array]) {
                                        foreach ($item in $prop.Value) {
                                            $itemIndex = $prop.Value.IndexOf($item)
                                            if ($null -ne $itemIndex) {
                                                if ($item -is [System.String]) {
                                                    $item = $(node "$PSScriptRoot/templating/replaceLocationValue.js" $item $playbookCounter)
                                                    $item = $(node "$PSScriptRoot/templating/replacePlaybookParamNames.js" $item $playbookCounter)
                                                    if ($item.StartsWith("[") -and $item[$item.Length - 1] -eq "]") {
                                                        $item = $(node "$PSScriptRoot/templating/replacePlaybookVarNames.js" $item $playbookCounter)
                                                    }
                                                    $resourceObj.$key[$itemIndex] = $item
                                                }
                                                elseif ($item -is [System.Management.Automation.PSCustomObject]) {
                                                    $resourceObj.$key[$itemIndex] = $(replaceVarsRecursively $item)
                                                }
                                            }
                                        }
                                    }
                                    else {
                                        if (($prop.Value -isnot [System.Int32]) -and ($prop.Value -isnot [System.Int64])) {
                                            $resourceObj.$key = $(replaceVarsRecursively $resourceObj.$key)
                                        }
                                    }
                                }
                            }
                            $resourceObj
                        }
                        $connectionCounter = 1
                        function getConnectionVariableName($connectionVariable) {
                            foreach ($templateVar in $($baseMainTemplate.variables).PSObject.Properties) {
                                if ($templateVar.Value -eq $connectionVariable) {
                                    return $templateVar.Name
                                }
                            }
                            return $false
                        }
                        foreach ($playbookResource in $playbookData.resources) {
                            if ($playbookResource.type -eq "Microsoft.Web/connections") {
                                if ($playbookResource.properties -and $playbookResource.properties.api -and $playbookResource.properties.api.id) {
                                    $connectionVar = $playbookResource.properties.api.id
                                    $connectionVar = $connectionVar.Replace("resourceGroup().location", "parameters('workspace-location')")
                                    $variableReferenceString = "[variables"
                                    $varName = ""
                                    if ($connectionVar.StartsWith($variableReferenceString)) {
                                        # Get value of variable
                                        $varName = $($connectionVar.Split("'"))[1]
                                        # Handle variable reference pairs
                                        if ($playbookData.variables.$varName.StartsWith($variableReferenceString)) {
                                            $varName = $($playbookData.variables.$varName.Split("'"))[1]
                                        }
                                        $connectionVar = $playbookData.variables.$varName
                                        $connectionVar = $connectionVar.Replace("resourceGroup().location", "parameters('workspace-location')")
                                    }
                                    $foundConnection = getConnectionVariableName $connectionVar
                                    if ($foundConnection) {
                                        $playbookResource.properties.api.id = "[variables('_$foundConnection')]"                     
                                    }
                                    else {
                                        $baseMainTemplate.variables | Add-Member -NotePropertyName "playbook-$playbookCounter-connection-$connectionCounter" -NotePropertyValue $(replaceVarsRecursively $connectionVar)
                                        $baseMainTemplate.variables | Add-Member -NotePropertyName "_playbook-$playbookCounter-connection-$connectionCounter" -NotePropertyValue "[variables('playbook-$playbookCounter-connection-$connectionCounter')]"
                                        $playbookResource.properties.api.id = "[variables('_playbook-$playbookCounter-connection-$connectionCounter')]"               
                                    }
                                    if(($playbookResource.properties.parameterValues) -and ($null -ne $baseMainTemplate.variables.'playbook-ApiKey'))
                                        {
                                            $playbookResource.properties.parameterValues.api_key = "[variables('playbook-ApiKey')]"
                                        }
                                }
                            }
                            $playbookResource = $(replaceVarsRecursively $playbookResource)
                            $playbookResource = $(removePropertiesRecursively $playbookResource)
                            $baseMainTemplate.resources += $playbookResource
                            $connectionCounter += 1
                        }
                        if ($azureManagementUrlExists) {
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "azureManagementUrl" -NotePropertyValue $azureManagementUrl
                        }
                        $playbookCounter += 1
                    }
                    elseif ($objectKeyLowercase -eq "data connectors") {
                        Write-Host "Generating Data Connector using $file"
                        try {
                            $connectorData = ConvertFrom-Json $rawData
                        }
                        catch {
                            Write-Host "Failed to deserialize $file" -ForegroundColor Red
                            break;
                        }
                        $connectorNameParamObj = [PSCustomObject] @{
                            type         = "string";
                            defaultValue = $(New-Guid).Guid
                        }
                        $baseMainTemplate.parameters | Add-Member -NotePropertyName "connector$connectorCounter-name" -NotePropertyValue $connectorNameParamObj
                        $baseMainTemplate.variables | Add-Member -NotePropertyName "connector$connectorCounter-source" -NotePropertyValue "[concat('/subscriptions/',subscription().subscriptionId,'/resourceGroups/',resourceGroup().name,'/providers/Microsoft.OperationalInsights/workspaces/',parameters('workspace'),'/providers/Microsoft.SecurityInsights/dataConnectors/',parameters('connector$connectorCounter-name'))]"
                        $baseMainTemplate.variables | Add-Member -NotePropertyName "_connector$connectorCounter-source" -NotePropertyValue "[variables('connector$connectorCounter-source')]"

                        $connectorId = $connectorData.id + 'Connector';
                        $baseMainTemplate.variables | Add-Member -NotePropertyName $connectorId -NotePropertyValue $connectorId
                        $baseMainTemplate.variables | Add-Member -NotePropertyName "_$connectorId" -NotePropertyValue "[variables('$connectorId')]"

                        $DependencyCriteria += [PSCustomObject]@{
                            kind      = "DataConnector";
                            contentId = "[variables('_$connectorId')]";
                            version   = $contentToImport.Version;
                        };
                        foreach ($step in $connectorData.instructionSteps) {
                            # Remove empty properties from each instructionStep
                            $stepIndex = $connectorData.instructionSteps.IndexOf($step)
                            $connectorData.instructionSteps[$stepIndex] = handleEmptyInstructionProperties $step
                        }

                        $connectorObj = [PSCustomObject]@{}
                        # If direct title is available, assume standard connector format
                        if ($connectorData.title) {
                            $connectorObj = [PSCustomObject]@{
                                id         = "[variables('_connector$connectorCounter-source')]";
                                name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',parameters('connector$connectorCounter-name'))]"
                                apiVersion = "2021-03-01-preview";
                                type       = "Microsoft.OperationalInsights/workspaces/providers/dataConnectors";
                                location   = "[parameters('workspace-location')]";
                                kind       = "GenericUI";
                                properties = [PSCustomObject]@{
                                    connectorUiConfig = [PSCustomObject]@{
                                        title                 = $connectorData.title;
                                        publisher             = $connectorData.publisher;
                                        descriptionMarkdown   = $connectorData.descriptionMarkdown;
                                        graphQueries          = $connectorData.graphQueries;
                                        sampleQueries         = $connectorData.sampleQueries;
                                        dataTypes             = $connectorData.dataTypes;
                                        connectivityCriterias = $connectorData.connectivityCriterias;
                                        availability          = $connectorData.availability;
                                        permissions           = $connectorData.permissions;
                                        instructionSteps      = $connectorData.instructionSteps
                                    }
                                }
                            }
                        }
                        elseif ($connectorData.resources -and 
                            $connectorData.resources[0] -and 
                            $connectorData.resources[0].properties -and 
                            $connectorData.resources[0].properties.connectorUiConfig -and 
                            $connectorData.resources[0].properties.pollingConfig) {
                            # Else check if Polling connector
                            $connectorData = $connectorData.resources[0]
                            $connectorUiConfig = $connectorData.properties.connectorUiConfig
                            $connectorUiConfig.PSObject.Properties.Remove('id')
                            $connectorObj = [PSCustomObject]@{
                                id         = "[variables('_connector$connectorCounter-source')]";
                                name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',parameters('connector$connectorCounter-name'))]"
                                apiVersion = "2021-03-01-preview";
                                type       = "Microsoft.OperationalInsights/workspaces/providers/dataConnectors";
                                location   = "[parameters('workspace-location')]";
                                kind       = $connectorData.kind;
                                properties = [PSCustomObject]@{
                                    connectorUiConfig = $connectorUiConfig;
                                    pollingConfig     = $connectorData.properties.pollingConfig;
                                }
                            }
                        }
                        if ($connectorData.additionalRequirementBanner) {
                            $connectorObj.properties.connectorUiConfig | Add-Member -NotePropertyName "additionalRequirementBanner" -NotePropertyValue $connectorData.additionalRequirementBanner
                        }

                        $baseMainTemplate.resources += $connectorObj

                        $syslog = "Syslog"
                        $commonSecurityLog = "CommonSecurityLog"
                        function getConnectorDataTypes($dataTypesArray) {
                            $typeResult = "custom log"
                            foreach ($dataType in $dataTypesArray) {
                                if ($dataType.name.IndexOf($syslog) -ne -1) {
                                    $typeResult = $syslog
                                }
                                elseif ($dataType.name.IndexOf($commonSecurityLog) -ne -1) {
                                    $typeResult = $commonSecurityLog
                                }
                            }
                            return $typeResult
                        }
                        function getAllDataTypeNames($dataTypesArray) {
                            $typeResult = @()
                            foreach ($dataType in $dataTypesArray) {
                                $typeResult += $dataType.name
                            }
                            return $typeResult
                        }
                        $connectorDataType = $(getConnectorDataTypes $connectorData.dataTypes)
                        $isParserAvailable = $($contentToImport.Parsers -and ($contentToImport.Parsers.Count -gt 0))
                        $baseDescriptionText = "This Solution installs the data connector for $solutionName. You can get $solutionName $connectorDataType data in your Microsoft Sentinel workspace. Configure and enable this data connector in the Data Connector gallery after this Solution deploys."
                        $parserText = "The Solution installs a parser that transforms the ingested data into Microsoft Sentinel normalized format. The normalized format enables better correlation of different types of data from different data sources to drive end-to-end outcomes seamlessly in security monitoring, hunting, incident investigation and response scenarios in Microsoft Sentinel."
                        $customLogsText = "$baseDescriptionText This data connector creates custom log table(s) $(getAllDataTypeNames $connectorData.dataTypes) in your Microsoft Sentinel / Azure Log Analytics workspace."
                        $syslogText = "$baseDescriptionText The logs will be received in the Syslog table in your Microsoft Sentinel / Azure Log Analytics workspace."
                        $commonSecurityLogText = "$baseDescriptionText The logs will be received in the CommonSecurityLog table in your Microsoft Sentinel / Azure Log Analytics workspace."
                        $connectorDescriptionText = $(if ($connectorDataType -eq $commonSecurityLog) { $commonSecurityLogText } elseif ($connectorDataType -eq $syslog) { $syslogText } else { $customLogsText })

                        $baseDataConnectorStep = [PSCustomObject] @{
                            name       = "dataconnectors";
                            label      = "Data Connectors";
                            bladeTitle = "Data Connectors";
                            elements   = @();
                        }
                        $baseDataConnectorTextElement = [PSCustomObject] @{
                            name    = "dataconnectors$connectorCounter-text";
                            type    = "Microsoft.Common.TextBlock";
                            options = [PSCustomObject] @{
                                text = $connectorDescriptionText;
                            }
                        }
                        if ($connectorCounter -eq 1) {
                            $baseCreateUiDefinition.parameters.steps += $baseDataConnectorStep
                        }
                        $currentStepNum = $baseCreateUiDefinition.parameters.steps.Count - 1
                        $baseCreateUiDefinition.parameters.steps[$currentStepNum].elements += $baseDataConnectorTextElement
                        if ($connectorCounter -eq $contentToImport."Data Connectors".Count) {
                            $parserTextElement = [PSCustomObject] @{
                                name    = "dataconnectors-parser-text";
                                type    = "Microsoft.Common.TextBlock";
                                options = [PSCustomObject] @{
                                    text = $parserText;
                                }
                            }
                            $normalizedFormatLink = [PSCustomObject] @{
                                name    = "dataconnectors-link1";
                                type    = "Microsoft.Common.TextBlock";
                                options = [PSCustomObject] @{
                                    link = [PSCustomObject] @{
                                        label = "Learn more about normalized format";
                                        uri   = "https://docs.microsoft.com/azure/sentinel/normalization-schema";
                                    }
                                }
                            }
                            $connectDataSourcesLink = [PSCustomObject] @{
                                name    = "dataconnectors-link2";
                                type    = "Microsoft.Common.TextBlock";
                                options = [PSCustomObject] @{
                                    link = [PSCustomObject] @{
                                        label = "Learn more about connecting data sources";
                                        uri   = "https://docs.microsoft.com/azure/sentinel/connect-data-sources";
                                    }
                                }
                            }
                            if ($isParserAvailable) {
                                $baseCreateUiDefinition.parameters.steps[$currentStepNum].elements += $parserTextElement
                            }
                            $baseCreateUiDefinition.parameters.steps[$currentStepNum].elements += $normalizedFormatLink
                            $baseCreateUiDefinition.parameters.steps[$currentStepNum].elements += $connectDataSourcesLink
                        }

                        # Update Connector Counter
                        $connectorCounter += 1
                    }
                    elseif ($objectKeyLowercase -eq "savedsearches") {
                        $isStandardTemplate = $false
                        $searchData = $json # Assume input is basic array of SavedSearches to start
                        # Check if SavedSearch input file uses direct structure given by export
                        if ($searchData -isnot [System.Array] -and $searchData.value) {
                            $searchData = $searchData.value 
                        }
                        # Check if SavedSearch input file uses standard template structure
                        if ($searchData -isnot [System.Array] -and $searchData.resources) {
                            $isStandardTemplate = $true
                            $searchData = $searchData.resources
                        }
                        if($searchData -is [System.Array] -and !$isStandardTemplate) {
                            foreach($search in $searchData) {
                                $savedSearchIdParameterName = "savedsearch$savedSearchCounter-id"
                                $savedSearchIdParameter = [PSCustomObject] @{ type = "string"; defaultValue = "[newGuid()]"; minLength = 1; metadata = [PSCustomObject] @{ description = "Unique id for the watchlist" }; }
                                $baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name $savedSearchIdParameterName -Value $savedSearchIdParameter

                                $savedSearchResource = [PSCustomObject]@{
                                    type = "Microsoft.OperationalInsights/workspaces/savedSearches";
                                    apiVersion = "2020-08-01";
                                    name = "[concat(parameters('workspace'),'/',parameters('$savedSearchIdParameterName'))]";
                                    properties = [PSCustomObject]@{
                                        category = $search.properties.category;
                                        displayName = $search.properties.displayName;
                                        query = $search.properties.query;
                                        functionAlias = $search.properties.functionAlias;
                                        version = $search.properties.version;
                                    };
                                }
                                $baseMainTemplate.resources += $savedSearchResource
                                $savedSearchCounter++
                            }
                        } elseif ($isStandardTemplate) {
                            $baseMainTemplate.resources += $searchData
                        }
                    }
                    elseif ($objectKeyLowercase -eq "watchlists") {
                        $watchlistData = $json.resources[0]

                        $watchlistName = $watchlistData.properties.displayName;
                        $baseMainTemplate.variables | Add-Member -NotePropertyName $watchlistName -NotePropertyValue $watchlistName
                        $baseMainTemplate.variables | Add-Member -NotePropertyName "_$watchlistName" -NotePropertyValue "[variables('$watchlistName')]"

                        $DependencyCriteria += [PSCustomObject]@{
                            kind      = "Watchlist";
                            contentId = "[variables('_$watchlistName')]";
                            version   = $contentToImport.Version;
                        };

                        #Handle CreateUiDefinition Base Step
                        if ($watchlistCounter -eq 1) {
                            $baseWatchlistStep = [PSCustomObject]@{
                                name       = "watchlists";
                                label      = "Watchlists";
                                subLabel   = [PSCustomObject]@{
                                    preValidation  = "Configure the watchlists";
                                    postValidation = "Done";
                                }
                                bladeTitle = "Watchlists";
                                elements   = @(
                                    [PSCustomObject]@{
                                        name    = "watchlists-text";
                                        type    = "Microsoft.Common.TextBlock";
                                        options = [PSCustomObject]@{
                                            text = "Microsoft Sentinel watchlists enable the collection of data from external data sources for correlation with the events in your Microsoft Sentinel environment. Once created, you can use watchlists in your search, detection rules, threat hunting, and response playbooks. Watchlists are stored in your Microsoft Sentinel workspace as name-value pairs and are cached for optimal query performance and low latency. Once deployment is successful, the installed watchlists will be available in the Watchlists blade under 'My Watchlists'.";
                                            link = [PSCustomObject]@{
                                                label = "Learn more";
                                                uri   = "https://aka.ms/sentinelwatchlists";
                                            }
                                        }
                                    }
                                )
                            }
                            $baseCreateUiDefinition.parameters.steps += $baseWatchlistStep
                        }

                        #Handle CreateUiDefinition Step Sub-Element
                        $currentStepNum = $baseCreateUiDefinition.parameters.steps.Count - 1
                        $watchlistStepElement = [PSCustomObject]@{
                            name     = "watchlist$watchlistCounter";
                            type     = "Microsoft.Common.Section";
                            label    = $watchlistData.properties.displayName;
                            elements = @(
                                [PSCustomObject]@{
                                    name    = "watchlist$watchlistCounter-text";
                                    type    = "Microsoft.Common.TextBlock";
                                    options = [PSCustomObject]@{
                                        text = $watchlistData.properties.description
                                    }
                                }
                            )
                        }
                        $baseCreateUiDefinition.parameters.steps[$currentStepNum].elements += $watchlistStepElement

                        # Add Watchlist ID to MainTemplate parameters
                        $watchlistIdParameterName = "watchlist$watchlistCounter-id"
                        $watchlistIdParameter = [PSCustomObject] @{ type = "string"; defaultValue = "[newGuid()]"; minLength = 1; metadata = [PSCustomObject] @{ description = "Unique id for the watchlist" }; }
                        $baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name $watchlistIdParameterName -Value $watchlistIdParameter

                        # Replace watchlist resource id
                        $watchlistData.name = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',parameters('watchlist$watchlistCounter-id'))]"

                        # Handle MainTemplate Resource
                        $baseMainTemplate.resources += $watchlistData #Assume 1 watchlist per template

                        # Update Watchlist Counter
                        $watchlistCounter += 1
                    }
                }
                else {
                    if ($file -match "(\.yaml)$") {
                        $objectKeyLowercase = $objectProperties.Name.ToLower()
                        if ($objectKeyLowercase -eq "hunting queries") {
                            Write-Host "Generating Hunting Query using $file"
                            $content = ''
                            foreach ($line in $rawData) {
                                $content = $content + "`n" + $line
                            }
                            try {
                                $yaml = ConvertFrom-YAML $content
                            }
                            catch {
                                Write-Host "Failed to deserialize $file" -ForegroundColor Red
                                break;
                            }

                            $fileName = Split-Path $file -leafbase;
                            $fileName += "_HuntingQueries";
                            $baseMainTemplate.variables | Add-Member -NotePropertyName $fileName -NotePropertyValue $fileName
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "_$fileName" -NotePropertyValue "[variables('$fileName')]"

                            $DependencyCriteria += [PSCustomObject]@{
                                kind      = "HuntingQuery";
                                contentId = "[variables('_$fileName')]";
                                version   = $contentToImport.Version;
                            };

                            if ($huntingQueryCounter -eq 1) {
                                if (!$(queryResourceExists)) {
                                    $baseHuntingQueryResource = [PSCustomObject] @{
                                        type       = "Microsoft.OperationalInsights/workspaces";
                                        apiVersion = "2020-08-01";
                                        name       = "[parameters('workspace')]";
                                        location   = "[parameters('workspace-location')]";
                                        resources  = @()
                                    }
                                    $baseMainTemplate.resources += $baseHuntingQueryResource
                                }
                                if ($null -eq $baseMainTemplate.variables.'workspace-dependency') {
                                    #Add parser dependency variable once to ensure validation passes.
                                    $baseMainTemplate.variables | Add-Member -MemberType NoteProperty -Name "workspace-dependency" -Value "[concat('Microsoft.OperationalInsights/workspaces/', parameters('workspace'))]"
                                }
                                $huntingQueryBaseStep = [PSCustomObject] @{
                                    name       = "huntingqueries";
                                    label      = "Hunting Queries";
                                    bladeTitle = "Hunting Queries";
                                    elements   = @(
                                        [PSCustomObject] @{
                                            name    = "huntingqueries-text";
                                            type    = "Microsoft.Common.TextBlock";
                                            options = [PSCustomObject] @{
                                                text = "This Microsoft Sentinel Solution installs hunting queries for $solutionName that you can run in Microsoft Sentinel. These hunting queries will be deployed in the Hunting gallery of your Microsoft Sentinel workspace. Run these hunting queries to hunt for threats in the Hunting gallery after this Solution deploys.";
                                                link = [PSCustomObject] @{
                                                    label = "Learn more";
                                                    uri   = "https://docs.microsoft.com/azure/sentinel/hunting"
                                                }
                                            }
                                        }
                                    )
                                }
                                $baseCreateUiDefinition.parameters.steps += $huntingQueryBaseStep
                            }
                            $huntingQueryObj = [PSCustomObject] @{
                                type       = "savedSearches";
                                apiVersion = "2020-08-01";
                                name       = "$solutionName Hunting Query $huntingQueryCounter";
                                dependsOn  = @(
                                    "[variables('workspace-dependency')]"
                                );
                                properties = [PSCustomObject] @{
                                    eTag        = "*";
                                    displayName = $yaml.name;
                                    category    = "Hunting Queries";
                                    query       = $yaml.query;
                                    version     = 1;
                                    tags        = @()
                                }
                            }
                            $huntingQueryDescription = ""
                            if ($yaml.description) {
                                $huntingQueryDescription = $yaml.description.substring(1, $yaml.description.length - 3)
                                $descriptionObj = [PSCustomObject]@{
                                    name  = "description";
                                    value = $huntingQueryDescription
                                }
                                $huntingQueryObj.properties.tags += $descriptionObj
                                $huntingQueryDescription = "$huntingQueryDescription "
                            }
                            if ($yaml.tactics -and $yaml.tactics.Count -gt 0) {
                                $tacticsObj = [PSCustomObject]@{
                                    name  = "tactics";
                                    value = $yaml.tactics -join ","
                                }
                                if ($tacticsObj.value.ToString() -match ' ') {
                                    $tacticsObj.value = $tacticsObj.value -replace ' ', ''
                                }
                                $huntingQueryObj.properties.tags += $tacticsObj
                            }
                            $baseMainTemplate.resources[$(getQueryResourceLocation)].resources += $huntingQueryObj

                            $dependencyDescription = ""
                            if ($yaml.requiredDataConnectors) {
                                $dependencyDescription = "It depends on the $($yaml.requiredDataConnectors.connectorId) data connector and $($($yaml.requiredDataConnectors.dataTypes)) data type and $($yaml.requiredDataConnectors.connectorId) parser."
                            }
                            $huntingQueryElement = [PSCustomObject]@{
                                name     = "huntingquery$huntingQueryCounter";
                                type     = "Microsoft.Common.Section";
                                label    = $yaml.name;
                                elements = @()
                            }
                            $huntingQueryElementDescription = [PSCustomObject]@{
                                name    = "huntingquery$huntingQueryCounter-text";
                                type    = "Microsoft.Common.TextBlock";
                                options = [PSCustomObject]@{
                                    text = "$($huntingQueryDescription)$dependencyDescription";
                                }
                            }
                            if ($huntingQueryDescription -or $dependencyDescription) {
                                $huntingQueryElement.elements += $huntingQueryElementDescription
                            }
                            $baseCreateUiDefinition.parameters.steps[$baseCreateUiDefinition.parameters.steps.Count - 1].elements += $huntingQueryElement

                            # Update HuntingQuery Counter
                            $huntingQueryCounter += 1
                        }

                        else {
                            # If yaml and not hunting query, process as Alert Rule
                            Write-Host "Generating Alert Rule using $file"
                            if ($analyticRuleCounter -eq 1) {
                                $baseAnalyticRuleStep = [PSCustomObject] @{
                                    name       = "analytics";
                                    label      = "Analytics";
                                    subLabel   = [PSCustomObject] @{
                                        preValidation  = "Configure the analytics";
                                        postValidation = "Done";
                                    };
                                    bladeTitle = "Analytics";
                                    elements   = @(
                                        [PSCustomObject] @{
                                            name    = "analytics-text";
                                            type    = "Microsoft.Common.TextBlock";
                                            options = [PSCustomObject] @{
                                                text = "This Microsoft Sentinel Solution installs analytic rules for $solutionName that you can enable for custom alert generation in Microsoft Sentinel. These analytic rules will be deployed in disabled mode in the analytics rules gallery of your Microsoft Sentinel workspace. Configure and enable these rules in the analytic rules gallery after this Solution deploys.";
                                                link = [PSCustomObject] @{
                                                    label = "Learn more";
                                                    uri   = "https://docs.microsoft.com/azure/sentinel/tutorial-detect-threats-custom?WT.mc_id=Portal-Microsoft_Azure_CreateUIDef";
                                                }
                                            }
                                        }
                                    )
                                }
                                $baseCreateUiDefinition.parameters.steps += $baseAnalyticRuleStep
                            }
                            $yamlPropertiesToCopyFrom = "name", "severity", "triggerThreshold", "query"
                            $yamlPropertiesToCopyTo = "displayName", "severity", "triggerThreshold", "query"
                            $alertRuleParameterName = "analytic$analyticRuleCounter-id"
                            $alertRule = [PSCustomObject] @{ description = ""; displayName = ""; enabled = $false; query = ""; queryFrequency = ""; queryPeriod = ""; severity = ""; suppressionDuration = ""; suppressionEnabled = $false; triggerOperator = ""; triggerThreshold = 0; }
                            $alertRuleParameter = [PSCustomObject] @{ type = "string"; defaultValue = "[newGuid()]"; minLength = 1; metadata = [PSCustomObject] @{ description = "Unique id for the scheduled alert rule" }; }
                            $content = ''

                            $fileName = Split-Path $file -leafbase;
                            $fileName += "_AnalyticalRules";
                            $baseMainTemplate.variables | Add-Member -NotePropertyName $fileName -NotePropertyValue $fileName
                            $baseMainTemplate.variables | Add-Member -NotePropertyName "_$fileName" -NotePropertyValue "[variables('$fileName')]"

                            $DependencyCriteria += [PSCustomObject]@{
                                kind      = "AnalyticsRule";
                                contentId = "[variables('_$fileName')]";
                                version   = $contentToImport.Version;
                            };

                            foreach ($line in $rawData) {
                                $content = $content + "`n" + $line
                            }
                            try {
                                $yaml = ConvertFrom-YAML $content # Convert YAML to PSObject
                            }
                            catch {
                                Write-Host "Failed to deserialize $file" -ForegroundColor Red
                                break;
                            }
                            # Copy all directly transposable properties
                            foreach ($yamlProperty in $yamlPropertiesToCopyFrom) {
                                $index = $yamlPropertiesToCopyFrom.IndexOf($yamlProperty)
                                $alertRule.$($yamlPropertiesToCopyTo[$index]) = $yaml.$yamlProperty
                            }
                            if (!$yaml.severity) {
                                $alertRule.severity = "Medium"
                            }

                            # Content Modifications
                            $triggerOperators = [PSCustomObject] @{ gt = "GreaterThan" ; lt = "LessThan" ; eq = "Equal" ; ne = "NotEqual" }
                            $alertRule.triggerOperator = $triggerOperators.$($yaml.triggerOperator)
                            if ($yaml.tactics -and ($yaml.tactics.Count -gt 0) ) {
                                if ($yaml.tactics -match ' ') {
                                    $yaml.tactics = $yaml.tactics -replace ' ', ''
                                }
                                $alertRule | Add-Member -NotePropertyName tactics -NotePropertyValue $yaml.tactics # Add Tactics property if exists
                            }
                            $alertRule.description = $yaml.description.TrimEnd() #remove newlines at the end of the string if there are any.
                            if ($alertRule.description.StartsWith("'") -or $alertRule.description.StartsWith('"')) {
                                # Remove surrounding single-quotes (') from YAML block literal string, in case the string starts with a single quote in Yaml.
                                # This block is for backwards compatibility as YAML doesn't require having strings quotes by single (or double) quotes
                                $alertRule.description = $alertRule.description.substring(1, $alertRule.description.length - 2)
                            }

                            # Check whether Day or Hour/Minut format need be used
                            function checkISO8601Format($field) {
                                if ($field.IndexOf("D") -ne -1) {
                                    return "P$field"
                                }
                                else {
                                    "PT$field"
                                }
                            }
                            $alertRule.queryFrequency = $(checkISO8601Format $yaml.queryFrequency.ToUpper())
                            $alertRule.queryPeriod = $(checkISO8601Format $yaml.queryPeriod.ToUpper())
                            $alertRule.suppressionDuration = "PT1H"
                            
                            # Handle optional fields
                            foreach ($yamlField in @("entityMappings", "eventGroupingSettings", "customDetails", "alertDetailsOverride", "incidentConfiguration", "sentinelEntitiesMappings")) {
                                if ($yaml.$yamlField) {
                                    $alertRule | Add-Member -MemberType NoteProperty -Name $yamlField -Value $yaml.$yamlField
                                }
                            }

                            # Create Alert Rule Resource Object
                            $newAnalyticRule = [PSCustomObject]@{
                                type       = "Microsoft.OperationalInsights/workspaces/providers/alertRules";
                                name       = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',parameters('analytic$analyticRuleCounter-id'))]";
                                apiVersion = "2021-03-01-preview";
                                kind       = "Scheduled";
                                location   = "[parameters('workspace-location')]";
                                properties = $alertRule;
                            }

                            # Add Resource and Parameters to Template
                            $baseMainTemplate.resources += $newAnalyticRule
                            $baseMainTemplate.parameters | Add-Member -MemberType NoteProperty -Name $alertRuleParameterName -Value $alertRuleParameter


                            $alertRuleUIParameter = [PSCustomObject] @{ name = "analytic$analyticRuleCounter"; type = "Microsoft.Common.Section"; label = $alertRule.displayName; elements = @( [PSCustomObject] @{ name = "analytic$analyticRuleCounter-text"; type = "Microsoft.Common.TextBlock"; options = @{ text = $alertRule.description; } } ) }
                            $baseCreateUiDefinition.parameters.steps[$baseCreateUiDefinition.parameters.steps.Count - 1].elements += $alertRuleUIParameter

                            # Update Counter
                            $analyticRuleCounter += 1
                        }
                    }
                    else {
                        # Assume file is Parser due to parsers having inconsistent types. (.txt, .kql, or none)
                        Write-Host "Generating Data Parser using $file"
                        if ($parserCounter -eq 1 -and $null -eq $baseMainTemplate.variables.'workspace-dependency') {
                            # Add parser dependency variable once to ensure validation passes.
                            $baseMainTemplate.variables | Add-Member -MemberType NoteProperty -Name "workspace-dependency" -Value "[concat('Microsoft.OperationalInsights/workspaces/', parameters('workspace'))]"
                        }

                        $fileName = Split-Path $file -leafbase;
                        $fileName = $fileName + "_Parser";
                        $baseMainTemplate.variables | Add-Member -NotePropertyName $fileName -NotePropertyValue $fileName
                        $baseMainTemplate.variables | Add-Member -NotePropertyName "_$fileName" -NotePropertyValue "[variables('$fileName')]"

                        $DependencyCriteria += [PSCustomObject]@{
                            kind      = "Parser";
                            contentId = "[variables('_$fileName')]";
                            version   = $contentToImport.Version;
                        };

                        $content = ''
                        $rawData = $rawData.Split("`n")
                        foreach ($line in $rawData) {
                            # Remove comment lines before condensing query
                            if (!$line.StartsWith("//")) {
                                $content = $content + "`n" + $line
                            }
                        }

                        function getFileNameFromPath ($inputFilePath) {
                            # Split out path
                            $output = $inputFilePath.Split("/")
                            $output = $output[$output.Length - 1]
                            # Split out file type
                            $output = $output.Split(".")[0]
                            return $output
                        }

                        # Use File Name as Parser Name
                        $functionAlias = getFileNameFromPath $file
                        if ($parserCounter -eq 1 -and !$(queryResourceExists)) {
                            $baseParserResource = [PSCustomObject] @{
                                type       = "Microsoft.OperationalInsights/workspaces";
                                apiVersion = "2020-08-01";
                                name       = "[parameters('workspace')]";
                                location   = "[parameters('workspace-location')]";
                                resources  = @(

                                )
                            }
                            $baseMainTemplate.resources += $baseParserResource
                        }
                        $parserObj = [PSCustomObject] @{
                            type       = "savedSearches";
                            apiVersion = "2020-08-01";
                            name       = "$solutionName Data Parser";
                            dependsOn  = @(
                                "[variables('workspace-dependency')]"
                            );
                            properties = [PSCustomObject] @{
                                eTag          = "*";
                                displayName   = "$solutionName Data Parser";
                                category      = "Samples";
                                functionAlias = "$functionAlias";
                                query         = $content;
                                version       = 1;
                            }
                        }
                        $baseMainTemplate.resources[$(getQueryResourceLocation)].resources += $parserObj

                        # Update Parser Counter
                        $parserCounter += 1
                    }
                }
            }
        }
        elseif ($objectProperties.Name.ToLower() -eq "metadata") {
            $finalPath = $basePath + $objectProperties.Value
            $rawData = $null
            try {
                Write-Host "Downloading $file"
                $rawData = (New-Object System.Net.WebClient).DownloadString($finalPath)
            }
            catch {
                Write-Host "Failed to download $file -- Please ensure that it exists in $([System.Uri]::EscapeUriString($basePath))" -ForegroundColor Red
                break;
            }

            try {
                $json = ConvertFrom-Json $rawData -ErrorAction Stop; # Determine whether content is JSON or YAML
                $validJson = $true;
            }
            catch {
                $validJson = $false;
            }

            if ($validJson -and $json) {
                # Create Metadata Resource Object
                if ($json.publisherId -and $json.offerId) {
                    $sourceId = $json.publisherId + "." + $json.offerId;
                }
                if ($json.support) {
                    $support = $json.support;
                }
                if ($json.categories) {
                    $categories = $json.categories;
                }

                if ($sourceId) {
                    $baseMainTemplate.variables | Add-Member -NotePropertyName "sourceId" -NotePropertyValue $sourceId;
                    $baseMainTemplate.variables | Add-Member -NotePropertyName "_sourceId" -NotePropertyValue "[variables('sourceId')]"
                }

                $Author = $contentToImport.Author.Split(" - ");

                $newMetadata = [PSCustomObject]@{
                    type       = "Microsoft.OperationalInsights/workspaces/providers/metadata";
                    apiVersion = "2021-03-01-preview";
                    properties = [PSCustomObject] @{
                        version = $contentToImport.Version;
                        kind    = "Solution";
                    };
                };

                $source = [PSCustomObject]@{
                    kind = "Solution";
                    name = "$solutionName";
                };
                $authorDetails = [PSCustomObject]@{
                    name  = $Author[0];
                    email = $Author[1];
                };
                if ($sourceId) {
                    $newMetadata | Add-Member -Name 'name' -Type NoteProperty -Value "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/', variables('_sourceId'))]";
                    $newMetadata.Properties | Add-Member -Name 'contentId' -Type NoteProperty -Value "[variables('_sourceId')]";
                    $newMetadata.Properties | Add-Member -Name 'parentId' -Type NoteProperty -Value "[variables('_sourceId')]";

                    $source | Add-Member -Name 'sourceId' -Type NoteProperty -value "[variables('_sourceId')]";
                    $newMetadata.Properties | Add-Member -Name 'source' -Type NoteProperty -value $source;
                }

                $newMetadata.Properties | Add-Member -Name 'author' -Type NoteProperty -value $authorDetails

                $supportDetails = New-Object psobject;

                if ($support -and $support.psobject.properties["name"] -and $support.psobject.properties["name"].value) {
                    $supportDetails | Add-Member -Name 'name' -Type NoteProperty -value $support.psobject.properties["name"].value;
                }

                if ($support -and $support.psobject.properties["email"] -and $support.psobject.properties["email"].value) {
                    $supportDetails | Add-Member -Name 'email' -Type NoteProperty -value $support.psobject.properties["email"].value;
                }

                if ($support -and $support.psobject.properties["tier"] -and $support.psobject.properties["tier"].value) {
                    $supportDetails | Add-Member -Name 'tier' -Type NoteProperty -value $support.psobject.properties["tier"].value;
                }

                if ($support -and $support.psobject.properties["link"] -and $support.psobject.properties["link"].value) {
                    $supportDetails | Add-Member -Name 'link' -Type NoteProperty -value $support.psobject.properties["link"].value;
                }

                if ($support.psobject.properties["name"] -or $support.psobject.properties["email"] -or $support.psobject.properties["tier"] -or $support.psobject.properties["link"]) {
                    $newMetadata.Properties | Add-Member -Name 'support' -Type NoteProperty -value $supportDetails;
                }

                $dependencies = [PSCustomObject]@{
                    operator = "AND";
                    criteria = $DependencyCriteria;
                };

                $newMetadata.properties | Add-Member -Name 'dependencies' -Type NoteProperty -Value $dependencies;

                if ($json.firstPublishDate -and $json.firstPublishDate -ne "") {
                    $newMetadata.Properties | Add-Member -Name 'firstPublishDate' -Type NoteProperty -value $json.firstPublishDate;
                }

                if ($json.lastPublishDate -and $json.lastPublishDate -ne "") {
                    $newMetadata.Properties | Add-Member -Name 'lastPublishDate' -Type NoteProperty -value $json.lastPublishDate;
                }

                if ($json.providers -and $json.providers -ne "") {
                    $newMetadata.Properties | Add-Member -Name 'providers' -Type NoteProperty -value $json.providers;
                }
                $categoriesDetails = New-Object psobject;
                if ($categories -and $categories.psobject.properties['domains'] -and $categories.psobject.properties["domains"].Value.Length -gt 0) {
                    $categoriesDetails | Add-Member -Name 'domains' -Type NoteProperty -Value $categories.psobject.properties["domains"].Value;
                    $newMetadata.properties | Add-Member -Name 'categories' -Type NoteProperty -Value $categoriesDetails;
                }

                if ($categories -and $categories.psobject.properties['verticals'] -and $categories.psobject.properties["verticals"].Value.Length -gt 0) {
                    $categoriesDetails | Add-Member -Name 'verticals' -Type NoteProperty -Value $categories.psobject.properties["verticals"].value;
                    $newMetadata.properties | Add-Member -Name 'categories' -Type NoteProperty -Value $categoriesDetails;
                }
                $baseMainTemplate.resources += $newMetadata;
            }
            else {
                Write-Host "Failed to load Metadata file $file -- Please ensure that it exists in $([System.Uri]::EscapeUriString($basePath))" -ForegroundColor Red
            }
        }
    }
	
	
    # Update CreateUiDefinition Description with Content Counts
    function updateDescriptionCount($counter, $emplaceString, $replaceString, $countStringCondition) {
        if ($counter -gt 0) {
            $ruleCountSubstring = "$emplaceString$counter"
            $ruleCountString = $(if ($countStringCondition) { "$ruleCountSubstring, " } else { $ruleCountSubstring })
            $baseCreateUiDefinition.parameters.config.basics.description = $baseCreateUiDefinition.parameters.config.basics.description -replace $replaceString, $ruleCountString
        }
        else {
            $baseCreateUiDefinition.parameters.config.basics.description = $baseCreateUiDefinition.parameters.config.basics.description -replace $replaceString, ""
        }
    }
    function checkResourceCounts ($countList) {
        if ($countList -isnot [System.Array]) { return $false }
        else {
            foreach ($count in $countList) { if ($count -gt 0) { return $true } }
            return $false
        }
    }
    if ($contentToImport.Description) {
        $baseCreateUiDefinition.parameters.config.basics.description = $baseCreateUiDefinition.parameters.config.basics.description -replace "{{SolutionDescription}}", $contentToImport.Description
    }
    else {
        $baseCreateUiDefinition.parameters.config.basics.description = $baseCreateUiDefinition.parameters.config.basics.description -replace "{{SolutionDescription}}", ""
    }

    $analyticRuleCounter -= 1
    $workbookCounter -= 1
    $playbookCounter -= 1
    $connectorCounter -= 1
    $parserCounter -= 1
    $huntingQueryCounter -= 1
    $watchlistCounter -= 1
    updateDescriptionCount $connectorCounter    "**Data Connectors:** " "{{DataConnectorCount}}" $(checkResourceCounts $parserCounter, $analyticRuleCounter, $workbookCounter, $playbookCounter, $huntingQueryCounter, $watchlistCounter)
    updateDescriptionCount $parserCounter       "**Parsers:** "         "{{ParserCount}}"        $(checkResourceCounts $analyticRuleCounter, $workbookCounter, $playbookCounter, $huntingQueryCounter, $watchlistCounter)
    updateDescriptionCount $workbookCounter     "**Workbooks:** "       "{{WorkbookCount}}"      $(checkResourceCounts $analyticRuleCounter, $playbookCounter, $huntingQueryCounter, $watchlistCounter)
    updateDescriptionCount $analyticRuleCounter "**Analytic Rules:** "  "{{AnalyticRuleCount}}"  $(checkResourceCounts $playbookCounter, $huntingQueryCounter, $watchlistCounter)
    updateDescriptionCount $huntingQueryCounter "**Hunting Queries:** " "{{HuntingQueryCount}}"  $(checkResourceCounts $playbookCounter, $watchlistCounter)
    updateDescriptionCount $watchlistCounter    "**Watchlists:** "      "{{WatchlistCount}}"     $(checkResourceCounts @($playbookCounter))
    updateDescriptionCount $playbookCounter     "**Playbooks:** "       "{{PlaybookCount}}"      $false

    # Update Logo in CreateUiDefinition Description
    if ($contentToImport.Logo) {
        $baseCreateUiDefinition.parameters.config.basics.description = $baseCreateUiDefinition.parameters.config.basics.description -replace "{{Logo}}", $contentToImport.Logo
    }
    else {
        $baseCreateUiDefinition.parameters.config.basics.description = $baseCreateUiDefinition.parameters.config.basics.description -replace "{{Logo}}\n\n", ""
    }

    # Update Metadata in MainTemplate
    $baseMainTemplate.metadata.author = $(if ($contentToImport.Author) { $contentToImport.Author } else { "" })
    $baseMainTemplate.metadata.comments = $baseMainTemplate.metadata.comments -replace "{{SolutionName}}", $solutionName

    $repoRoot = $(git rev-parse --show-toplevel)
    $solutionFolderName = $solutionName
    $solutionFolder = "$repoRoot/Solutions/$solutionFolderName"
    if (!(Test-Path -Path $solutionFolder)) {
        New-Item -ItemType Directory $solutionFolder
    }
    $solutionFolder = "$solutionFolder/Package"
    if (!(Test-Path -Path $solutionFolder)) {
        New-Item -ItemType Directory $solutionFolder
    }
    $mainTemplateOutputPath = "$solutionFolder/mainTemplate.json"
    $createUiDefinitionOutputPath = "$solutionFolder/createUiDefinition.json"

    try {
        $baseMainTemplate | ConvertTo-Json -Depth $jsonConversionDepth | Out-File $mainTemplateOutputPath -Encoding utf8
    }
    catch {
        Write-Host "Failed to write output file $mainTemplateOutputPath" -ForegroundColor Red
        break;
    }
    try {
        # Sort UI Steps before writing to file
        $createUiDefinitionOrder = "dataconnectors", "parsers", "workbooks", "analytics", "huntingqueries", "watchlists", "playbooks"
        $baseCreateUiDefinition.parameters.steps = $baseCreateUiDefinition.parameters.steps | Sort-Object { $createUiDefinitionOrder.IndexOf($_.name) }
        # Ensure single-step UI Definitions have proper type for steps
        if ($($baseCreateUiDefinition.parameters.steps).GetType() -ne [System.Object[]]) {
            $baseCreateUiDefinition.parameters.steps = @($baseCreateUiDefinition.parameters.steps)
        }
        $baseCreateUiDefinition | ConvertTo-Json -Depth $jsonConversionDepth | Out-File $createUiDefinitionOutputPath -Encoding utf8
    }
    catch {
        Write-Host "Failed to write output file $createUiDefinitionOutputPath" -ForegroundColor Red
        break;
    }
    $zipPackageName = "$(if($contentToImport.Version){$contentToImport.Version}else{"newSolutionPackage"}).zip"
    Compress-Archive -Path "$solutionFolder/*" -DestinationPath "$solutionFolder/$zipPackageName" -Force

    #downloading and running arm-ttk on generated solution
    $armTtkFolder = "$PSScriptRoot/arm-ttk"
    if (!$(Get-Command Test-AzTemplate -ErrorAction SilentlyContinue)) {
        Write-Output "Missing arm-ttk validations. Downloading module..."
        Invoke-Expression "$armTtkFolder/download-arm-ttk.ps1"
    }
    Invoke-Expression "$armTtkFolder/run-arm-ttk-in-automation.ps1 '$solutionName'"
}