
function Get-CCP-Dict($dataFileMetadata, $baseFolderPath, $solutionName, $DCFolderName) {
    try {
    $ccpDict = @()
    $dataConnectorsInputArray = $dataFileMetadata.PsObject.Properties | Where-Object { $_.Name -eq "$DCFolderName" };

    # IDENTIFY CCP DATA DEFINITION IN DATA INPUT FILE
    foreach ($objectProperties in $dataConnectorsInputArray) {
        $items = $objectProperties.Value 
        if ($items -is [System.String]) {
            $items = $items | ConvertFrom-Json
        }

        foreach ($file in $items) {
            $file = $file.Replace("$baseFolderPath/", "").Replace("Solutions/", "").Replace("$solutionName/", "")

            $currentFileDCPath = ($baseFolderPath + $solutionName + "/" + $file).Replace("//", "/")
            $ccpBaseFolderPath = (Split-Path -Path $currentFileDCPath -Parent) -replace '\\', '/'
            Write-Host "currentFileDCPath $currentFileDCPath, ccpBaseFolderPath $ccpBaseFolderPath"
            #$fileContent = Get-Content -Raw $currentFileDCPath | Out-String | ConvertFrom-Json
            
            $fileContent = ReadFileContent -filePath "$currentFileDCPath"
            if ($null -eq $fileContent) {
                exit 1;
            }

            # check if dataconnectorDefinitions type exist in dc array
            if($fileContent.type -eq "Microsoft.SecurityInsights/dataConnectorDefinitions") {
                Write-Host "CCP DataConnectorDefinition File Found, FileName is $file"

                $isDynamicStreamName = $false;
                $definitionInstructions = $fileContent.properties.connectorUiConfig.instructionSteps
                $dataConnectorDefinitionFileInstructions = $definitionInstructions.psobject.properties.match('instructions').Count
                if ($dataConnectorDefinitionFileInstructions.Count -gt 0) {
                    $contextPaneContent = $definitionInstructions.instructions | Where-Object { $_.type -eq "ContextPane" }

                    if ($null -ne $contextPaneContent) {
                        $contextPaneContentDropDownObj = $definitionInstructions.instructions.parameters.instructionSteps.instructions | Where-Object { $_.type -eq "Dropdown" }

                        if ($null -ne $contextPaneContentDropDownObj) {
                            if ($contextPaneContentDropDownObj.parameters.name -eq "streamName") {
                                $isDynamicStreamName = $true;
                                Write-Host "Info: Dropdown Parameter with name 'streamName' found in Data Connector Definition file, so poller file StreamName and destinationTable value will be automatically in mainTemplate file!"
                            }
                        }
                    }
                }
                if ($ccpDict.Count -le 0) {
                    # if single data connector definition has "id" property with multiple poller file names separated by comma
                    $hasIdProperty = $fileContent.properties.connectorUiConfig.psobject.properties.match('id').Count
                    if (!$hasIdProperty) {
                        Write-Host "File $currentFileDCPath doesnt have id property in connectorUiConfig!"
                        exit 1;
                    }

                    if ($ccpDict.Count -eq 0) {
                        $ccpDict = [PSCustomObject]@{
                            title = $fileContent.Properties.connectorUiConfig.title;
                            DCDefinitionFullPath = $currentFileDCPath
                            DCDefinitionFilePath = $file;
                            DCDefinitionId = $fileContent.properties.connectorUiConfig.id;
                            DCPollerFilePath = "";
                            DCPollerStreamName = "";
                            DCRFilePath = "";
                            DCROutputStream = "";
                            TableFilePath = "";
                            TableOutputStream = "";
                            PollerDataCollectionEndpoint = "";
                            PollerDataCollectionRuleImmutableId = "";
                            PollerKind = "";
                            PollerConnectorDefinitionName = $pollerName
                            IsProcessed = $false;
                            DCPollerName = "";
                            CCPBaseFolder = $ccpBaseFolderPath;
                            isDynamicStreamName = $isDynamicStreamName;
                        }
                    } else {
                        [array]$ccpDict += [PSCustomObject]@{
                            Title = $fileContent.Properties.connectorUiConfig.title;
                            DCDefinitionFullPath = $currentFileDCPath
                            DCDefinitionFilePath = $file;
                            DCDefinitionId = $fileContent.properties.connectorUiConfig.id;
                            DCPollerFilePath = "";
                            DCPollerStreamName = "";
                            DCRFilePath = "";
                            DCROutputStream = "";
                            TableFilePath = "";
                            TableOutputStream = "";
                            PollerDataCollectionEndpoint = "";
                            PollerDataCollectionRuleImmutableId = "";
                            PollerKind = "";
                            PollerConnectorDefinitionName = $pollerName
                            IsProcessed = $false;
                            DCPollerName = "";
                            CCPBaseFolder = $ccpBaseFolderPath;
                            isDynamicStreamName = $isDynamicStreamName;
                        }
                    }
                } else {
                    [array]$ccpDict += [PSCustomObject]@{
                        Title = $fileContent.Properties.connectorUiConfig.title;
                        DCDefinitionFullPath = $currentFileDCPath
                        DCDefinitionFilePath = $file;
                        DCDefinitionId = $fileContent.properties.connectorUiConfig.id;
                        DCPollerFilePath = "";
                        DCPollerStreamName = "";
                        DCRFilePath = "";
                        DCROutputStream = "";
                        TableFilePath = "";
                        TableOutputStream = "";
                        PollerDataCollectionEndpoint = "";
                        PollerDataCollectionRuleImmutableId = "";
                        PollerKind = "";
                        PollerConnectorDefinitionName = ""
                        IsProcessed = $false;
                        DCPollerName = "";
                        CCPBaseFolder = $ccpBaseFolderPath;
                        isDynamicStreamName = $isDynamicStreamName;
                    }
                }
            }
        }
    }

    # identify ccp files definition provided has corresponding poller files if no then fail it.
    if ($ccpDict.Count -gt 0) {
        $identifiedDCPath = ($baseFolderPath + $solutionName + "/" + $DCFolderName).Replace("//", "/")
        
        # identify relation between definition and poller files
        foreach ($ccpDefinitionFile in $ccpDict) {
            #identify given file is present in dc folder or not
            foreach ($inputFile in $(Get-ChildItem -Path $identifiedDCPath -Include *.json -Recurse)) {
                $currentFolderPath = $inputFile.DirectoryName -replace '\\', '/'
                if ($currentFolderPath -ne $ccpDefinitionFile.CCPBaseFolder -or
                ($inputFile.Extension -eq ".md" -or $inputFile.Extension -eq ".txt" -or $inputFile.Extension -eq ".py" -or $inputFile.Extension -eq ".zip" -or 
                $inputFile.Name -eq "Images" -or $inputFile.Name -eq "function.json" -or $inputFile.Name -eq "host.json" -or $inputFile.Name -eq "proxies.json"))
                {
                    continue;
                }
                else {
                    try
                    {
                        #$fileContent = Get-Content -Raw $inputFile.FullName | Out-String | ConvertFrom-Json
                        $fileContent = ReadFileContent -filePath $inputFile.FullName
                        if ($null -eq $fileContent) {
                            exit 1;
                        }

                        if ($fileContent -is [System.Object[]]) {
                            $counter = 0;
                            foreach ($pollerArrayItem in $fileContent) {
                                if($pollerArrayItem.type -eq "Microsoft.SecurityInsights/dataConnectors") {
                                    if ($pollerArrayItem.properties.connectorDefinitionName -eq $ccpDefinitionFile.DCDefinitionId -or
                                    $pollerArrayItem.properties.connectorDefinitionName -eq $ccpDefinitionFile.PollerConnectorDefinitionName
                                    ) {
                                        if ($counter -eq 0) {
                                            # update details for this record only.
                                            $ccpDefinitionFile.DCPollerFilePath = $inputFile.FullName
                                            $ccpDefinitionFile.DCPollerStreamName = $pollerArrayItem.properties.dcrConfig.streamName
                                            $ccpDefinitionFile.PollerKind = $pollerArrayItem.kind;
                                            if ($null -eq $pollerArrayItem.properties.dcrConfig.dataCollectionEndpoint) {
                                                $ccpDefinitionFile.PollerDataCollectionEndpoint = "data collection endpoint";
                                            } else {
                                                $dataCollectionEndpoint = $pollerArrayItem.properties.dcrConfig.dataCollectionEndpoint;
                                                $ccpDefinitionFile.PollerDataCollectionEndpoint = "$dataCollectionEndpoint";
                                            }
                                            
                                            if ($null -eq $pollerArrayItem.properties.dcrConfig.dataCollectionRuleImmutableId) {
                                                $ccpDefinitionFile.PollerDataCollectionRuleImmutableId = "data collection rule immutableId";
                                            } else {
                                                $dataCollectionRuleImmutableId = $pollerArrayItem.properties.dcrConfig.dataCollectionRuleImmutableId;
                                                $ccpDefinitionFile.PollerDataCollectionRuleImmutableId = "$dataCollectionRuleImmutableId";
                                            }

                                            $ccpDefinitionFile.DCPollerName = ($null -eq $pollerArrayItem.name -or $pollerArrayItem.name -eq '') ? $pollerArrayItem.properties.connectorUiConfig.id : $pollerArrayItem.name;
                                        } else {
                                            # we have to add new record in ccpDict as it is an array
                                            [array]$ccpDict += [PSCustomObject]@{
                                                Title = $pollerArrayItem.Properties.connectorUiConfig.title;
                                                DCDefinitionFullPath = $currentFileDCPath
                                                DCDefinitionFilePath = $file;
                                                DCDefinitionId = $pollerArrayItem.properties.connectorUiConfig.id;
                                                DCPollerFilePath = "";
                                                DCPollerStreamName = "";
                                                DCRFilePath = "";
                                                DCROutputStream = "";
                                                TableFilePath = "";
                                                TableOutputStream = "";
                                                PollerDataCollectionEndpoint = "";
                                                PollerDataCollectionRuleImmutableId = "";
                                                PollerKind = "";
                                                PollerConnectorDefinitionName = ""
                                                IsProcessed = $false;
                                                DCPollerName = ($null -eq $pollerArrayItem.name -or $pollerArrayItem.name -eq '') ? $pollerArrayItem.properties.connectorUiConfig.id : $pollerArrayItem.name;
                                            }
                                        }
                                    }
                                }
                            }
                        } else {
                            if($fileContent.type -eq "Microsoft.SecurityInsights/dataConnectors") {
                                if ($fileContent.properties.connectorDefinitionName -eq $ccpDefinitionFile.DCDefinitionId -or
                                $fileContent.properties.connectorDefinitionName -eq $ccpDefinitionFile.PollerConnectorDefinitionName
                                ) {
                                    $ccpDefinitionFile.DCPollerFilePath = $inputFile.FullName
                                    $ccpDefinitionFile.DCPollerStreamName = $fileContent.properties.dcrConfig.streamName
                                    $ccpDefinitionFile.PollerKind = $fileContent.kind;
                                    if ($null -eq $fileContent.properties.dcrConfig.dataCollectionEndpoint) {
                                        $ccpDefinitionFile.PollerDataCollectionEndpoint = "data collection endpoint";
                                    } else {
                                        $dataCollectionEndpoint = $fileContent.properties.dcrConfig.dataCollectionEndpoint;
                                        $ccpDefinitionFile.PollerDataCollectionEndpoint = "$dataCollectionEndpoint";
                                    }
    
                                    if ($null -eq $fileContent.properties.dcrConfig.dataCollectionRuleImmutableId) {
                                        $ccpDefinitionFile.PollerDataCollectionRuleImmutableId = "data collection rule immutableId";
                                    } else {
                                        $dataCollectionRuleImmutableId = $fileContent.properties.dcrConfig.dataCollectionRuleImmutableId;
                                        $ccpDefinitionFile.PollerDataCollectionRuleImmutableId = "$dataCollectionRuleImmutableId";
                                    }

                                    $ccpDefinitionFile.DCPollerName = ($null -eq $fileContent.name -or $fileContent.name -eq '') ? $fileContent.properties.connectorUiConfig.id : $fileContent.name;
                                }
                            }
                        }
                    }
                    catch {
                        Write-Host "Error occurred while identifying relation between definition and poller File. Identified error in " + $inputFile.Name + ". Error Details : $_"
                    }
                }
            }
        }
        
        # identify relation between poller and DCR
        foreach ($ccpPollerFile in $ccpDict) {
            foreach ($inputFile in $(Get-ChildItem -Path $identifiedDCPath -Include *.json -Recurse)) {
                $currentFolderPath = $inputFile.DirectoryName -replace '\\', '/'
                if ($currentFolderPath -ne $ccpPollerFile.CCPBaseFolder -or
                $inputFile.Extension -eq ".md" -or $inputFile.Extension -eq ".txt" -or $inputFile.Extension -eq ".py" -or $inputFile.Extension -eq ".zip" -or 
                $inputFile.Name -eq "Images" -or $inputFile.Name -eq "function.json" -or $inputFile.Name -eq "host.json" -or $inputFile.Name -eq "proxies.json")
                {
                    continue;
                }
                else {
                    #$fileContent = Get-Content -Raw $inputFile.FullName | Out-String | ConvertFrom-Json
                    $fileContent = ReadFileContent -filePath $inputFile.FullName
                    if ($null -eq $fileContent) {
                        exit 1;
                    }

                    try {
                        if($fileContent.type -eq "Microsoft.Insights/dataCollectionRules" -and $fileContent.properties.dataFlows.streams -is [System.String]) {
                            $dataFlowStreams = $fileContent.properties.dataFlows;
                            foreach ($dcrDataFlowStream in $dataFlowStreams) {
                                $dcrStreamName = $dcrDataFlowStream.streams[0]

                                if (!$dcrStreamName.Contains('Custom-')) {
                                    . "$PSScriptRoot/standardLogStreams.ps1" # load standard data connector poller and dcr mapper
                                    $dcPollerStreamNameValue = GetKeyValue -key $ccpPollerFile.DCPollerStreamName

                                    if ($null -eq $dcPollerStreamNameValue) {
                                        # not found in mapping
                                        Write-Host "Error For given CCP Data Connector poller, mapping not found in StandardLogStreams. Please make sure that StreamName in Data Connector poller file and that in DCR Stream name are correct. Refer StandardLogStreams.ps1 file for Standard mapping. Refer Tools/Create-Azure-Sentinel-Solution/common/StandardLogStreams.ps1 file for Standard mapping." -BackgroundColor Red
                                        exit 1; 
                                    } elseif ($dcrDataFlowStream.streams[0].ToString() -ne $dcPollerStreamNameValue) {
                                        # when dc poller streamname expected mapping value is not equal to dcr file stream name
                                        Write-Host "Error For given CCP, DCR file 'stream' value is not correct. Please make sure that StreamName in Data Connector poller file and that in DCR Stream name are correct. Refer Tools/Create-Azure-Sentinel-Solution/common/StandardLogStreams.ps1 file for Standard mapping." -BackgroundColor Red
                                        exit 1; 
                                    } else {
                                        $ccpPollerFile.DCRFilePath = $inputFile.FullName
                                    }
                                }
                                else {
                                    # this is a custom table
                                    if ($dcrDataFlowStream.streams[0] -eq $ccpPollerFile.DCPollerStreamName) {
                                        $ccpPollerFile.DCRFilePath = $inputFile.FullName
                                        if ($fileContent.properties.dataFlows[0].outputStream.contains('Custom-')) {
                                            $ccpPollerFile.TableOutputStream = $dcrDataFlowStream.outputStream.Replace('Custom-', '')
                                            $ccpPollerFile.DCROutputStream = $dcrDataFlowStream.outputStream
                                        }
                                    }
                                }
                            }
                        } else {
                            if($fileContent.type -eq "Microsoft.Insights/dataCollectionRules") {
                                if ($fileContent.properties.dataFlows.Count -gt 1) {
                                    foreach ($dataFlowItem in $fileContent.properties.dataFlows) {
                                        $dataFlowStreamName = $dataFlowItem.streams[0]
                                        $dataFlowOutputStreamName = $dataFlowItem.outputStream

                                        if ($dataFlowStreamName -eq $ccpPollerFile.DCPollerStreamName) {
                                            $ccpPollerFile.DCRFilePath = $inputFile.FullName

                                            if ($dataFlowOutputStreamName.contains('Custom-')) {
                                                $ccpPollerFile.TableOutputStream = $dataFlowStreamName.Replace('Custom-', '')
                                                $ccpPollerFile.DCROutputStream = $dataFlowOutputStreamName
                                            }
                                            
                                            break
                                        }

                                        if ($null -eq $dataFlowOutputStreamName) {
                                            # if standard table
                                            . "$PSScriptRoot/standardLogStreams.ps1" # load standard data connector poller and dcr mapper
                                            $dcPollerStreamNameValue = GetKeyValue -key $ccpPollerFile.DCPollerStreamName
                                            if ($dcPollerStreamNameValue -eq $dataFlowStreamName) {
                                                $ccpPollerFile.DCRFilePath = $inputFile.FullName
                                            }
                                        }
                                    }
                                }
                                if ($fileContent.properties.dataFlows[0].streams[0] -eq $ccpPollerFile.DCPollerStreamName) {
                                    $ccpPollerFile.DCRFilePath = $inputFile.FullName
                                    if ($fileContent.properties.dataFlows[0].outputStream.contains('Custom-')) {
                                        $ccpPollerFile.TableOutputStream = $fileContent.properties.dataFlows[0].outputStream.Replace('Custom-', '')
                                        $ccpPollerFile.DCROutputStream = $fileContent.properties.dataFlows[0].outputStream
                                    }
                                }
                            }
                        }
                    }
                    catch {
                        Write-Host "Error occurred while identifying relation between Poller and DCR File. Identified error in " + $inputFile.Name + ". Error Details : $_"
                    }
                }
            }
        }

        # identify relation between DCR and table
        foreach ($ccpTable in $ccpDict) {
            foreach ($inputFile in $(Get-ChildItem -Path $identifiedDCPath -Include *.json -Recurse)) {
                $currentFolderPath = $inputFile.DirectoryName -replace '\\', '/'
                if ($currentFolderPath -ne $ccpTable.CCPBaseFolder -or
                $inputFile.Extension -eq ".md" -or $inputFile.Extension -eq ".txt" -or $inputFile.Extension -eq ".py" -or $inputFile.Extension -eq ".zip" -or 
                $inputFile.Name -eq "Images" -or $inputFile.Name -eq "function.json" -or $inputFile.Name -eq "host.json" -or $inputFile.Name -eq "proxies.json")
                {
                    continue;
                }
                else {
                    #$fileContent = Get-Content -Raw $inputFile.FullName | Out-String | ConvertFrom-Json
                    $fileContent = ReadFileContent -filePath $inputFile.FullName
                    if ($null -eq $fileContent) {
                        exit 1;
                    }

                    try {
                        if ($fileContent -is [System.Object[]]) {
                            foreach ($tableArrayItem in $fileContent) {
                                if($tableArrayItem.type -eq "Microsoft.OperationalInsights/workspaces/tables") {
                                    if ($tableArrayItem.name -eq $ccpTable.TableOutputStream) {
                                        $ccpTable.TableFilePath = $inputFile.FullName
                                    }
                                }
                            }
                        } else {
                            if($fileContent.type -eq "Microsoft.OperationalInsights/workspaces/tables") {
                                if ($fileContent.name -eq $ccpTable.TableOutputStream) {
                                    $ccpTable.TableFilePath = $inputFile.FullName
                                }
                            }
                        }
                    }
                    catch {
                        Write-Host "Error occurred while identifying relation between DCR and Table File. Identified error in " + $inputFile.Name + ". Error Details : $_"
                    }
                }
            }
        }
    }

    # THROW ERROR IF THERE IS NO RELATION BETWEEN DEFINITION->POLLER AND/OR POLLER->DCR
    if ($ccpDict.Count -gt 0) {
        foreach($localCCPDist in $ccpDict) {
            if (($localCCPDist.DCDefinitionId -eq "" -or $localCCPDist.DCDefinitionFilePath -eq "" -or
            $localCCPDist.DCPollerFilePath -eq "" -or $localCCPDist.DCPollerStreamName -eq "" -or $localCCPDist.DCRFilePath -eq "") -and
            $localCCPDist.PollerKind -eq 'RestApiPoller') 
            {
                Write-Host "Please verify if there is a mapping between ConnectorDefinition with Poller file and/or Poller file with DCR file! If mapping is correct then check type property for ccp files!"
                exit 1
            }
        }
    }

    return $ccpDict;
  }
  catch {
    Write-Host "Error in get-ccpdetails. Error Details: $_" -ForegroundColor Red
    return $null;
  }
}

function GetCCPTableFilePaths($existingCCPDict, $baseFolderPath, $solutionName, $DCFolderName) {
    # call this only when there are atleast 1 ccp connector
    $ccpTablesFilePaths = @()
    $identifiedDCPath = ($baseFolderPath + $solutionName + "/" + $DCFolderName).Replace("//", "/")
    #$currentFileDCPath = ($baseFolderPath + $solutionName + "/" + $identifiedDCPath).Replace("//", "/")

    foreach ($inputFile in $(Get-ChildItem -Path $identifiedDCPath -Include *.json -Recurse)) {
        if ($inputFile.Extension -eq ".md" -or $inputFile.Extension -eq ".txt" -or $inputFile.Extension -eq ".py" -or $inputFile.Extension -eq ".zip" -or 
        $inputFile.Name -eq "Images" -or $inputFile.Name -eq "function.json" -or $inputFile.Name -eq "host.json" -or $inputFile.Name -eq "proxies.json")
        {
            continue;
        }
        else {
            #$fileContent = Get-Content -Raw $inputFile.FullName | Out-String | ConvertFrom-Json
            $fileContent = ReadFileContent -filePath $inputFile.FullName
            if ($null -eq $fileContent) {
                exit 1;
            }

            if($fileContent.type -eq "Microsoft.OperationalInsights/workspaces/tables") {
                $currentTableFilePath = $inputFile.FullName
                if ($existingCCPDict.Count -gt 0) {
                    # check if current file path already present in variable $existingCCPDict if not present then add it in new variable list
                    $isTablePresent = $false;
                    foreach ($ccpRecord in $existingCCPDict) {
                        $currentFolderPath = $inputFile.DirectoryName -replace '\\', '/'
                        if ($currentFolderPath -eq $ccpDefinitionFile.CCPBaseFolder) {
                            if ($ccpRecord.TableFilePath -ne '' -and $ccpRecord.TableFilePath -eq $currentTableFilePath) {
                                $isTablePresent = $true;
                                break;
                            }
                        }
                    }
                    if (!$isTablePresent) {
                        $ccpTablesFilePaths += "$currentTableFilePath"
                    }
                }
            }
        }
    }

    return $ccpTablesFilePaths;
}