
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
            Write-Host "currentFileDCPath $currentFileDCPath"
            #$fileContent = Get-Content -Raw $currentFileDCPath | Out-String | ConvertFrom-Json

            $fileContent = ReadFileContent -filePath $currentFileDCPath
            if ($null -eq $fileContent) {
                exit 1;
            }

            # check if dataconnectorDefinitions type exist in dc array
            if($fileContent.type -eq "Microsoft.SecurityInsights/dataConnectorDefinitions") {
                Write-Host "CCP DataConnectorDefinition File Found, FileName is $file"
                if ($ccpDict.Count -le 0) {
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
                if ($inputFile.Extension -eq ".md" -or $inputFile.Extension -eq ".txt" -or $inputFile.Extension -eq ".py" -or $inputFile.Extension -eq ".zip" -or 
                $inputFile.Name -eq "Images" -or $inputFile.Name -eq "function.json" -or $inputFile.Name -eq "host.json" -or $inputFile.Name -eq "proxies.json")
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

                        if($fileContent.type -eq "Microsoft.SecurityInsights/dataConnectors") {
                            if ($fileContent.properties.connectorDefinitionName -eq $ccpDefinitionFile.DCDefinitionId) {
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
                            }
                        }
                    }
                    catch {
                        Write-Host "Error occured while identifying relation between definition and poller File. Identified error in " + $inputFile.Name + ". Error Details : $_"
                    }
                }
            }
        }
        
        # identify relation between poller and DCR
        foreach ($ccpPollerFile in $ccpDict) {
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

                    try {
                        if($fileContent.type -eq "Microsoft.Insights/dataCollectionRules") {
                            if ($fileContent.properties.dataFlows[0].streams[0] -eq $ccpPollerFile.DCPollerStreamName) {
                                $ccpPollerFile.DCRFilePath = $inputFile.FullName
                                $ccpPollerFile.TableOutputStream = $fileContent.properties.dataFlows[0].outputStream.Replace('Custom-', '')
                                $ccpPollerFile.DCROutputStream = $fileContent.properties.dataFlows[0].outputStream
                            }
                        }
                    }
                    catch {
                        Write-Host "Error occured while identifying relation between Poller and DCR File. Identified error in " + $inputFile.Name + ". Error Details : $_"
                    }
                }
            }
        }

        # identify relation between DCR and table
        foreach ($ccpTable in $ccpDict) {
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

                    try {
                        if($fileContent.type -eq "Microsoft.OperationalInsights/workspaces/tables") {
                            if ($fileContent.name -eq $ccpTable.TableOutputStream) {
                                $ccpTable.TableFilePath = $inputFile.FullName
                            }
                        }
                    }
                    catch {
                        Write-Host "Error occured while identifying relation between DCR and Table File. Identified error in " + $inputFile.Name + ". Error Details : $_"
                    }
                }
            }
        }
    }

    # THROW ERROR IF THERE IS NO RELATION BETWEEN DEFINITION->POLLER AND/OR POLLER->DCR
    if ($ccpDict.Count -gt 0) {
        foreach($localCCPDist in $ccpDict) {
            if ($localCCPDist.DCDefinitionId -eq "" -or $localCCPDist.DCDefinitionFilePath -eq "" -or
            $localCCPDist.DCPollerFilePath -eq "" -or $localCCPDist.DCPollerStreamName -eq "" -or $localCCPDist.DCRFilePath -eq "") 
            {
                Write-Host "Please verify if there is a mapping between ConnectorDefiniton with Poller file and/or Poller file with DCR file! If mapping is correct then check type property for ccp files!"
                exit 1
            }
        }
    }

    return $ccpDict;
  }
  catch {
    Write-Host "Error in get-ccpdetails. Error Details: $_"
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
                        if ($ccpRecord.TableFilePath -ne '' -and $ccpRecord.TableFilePath -eq $currentTableFilePath) {
                            $isTablePresent = $true;
                            break;
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