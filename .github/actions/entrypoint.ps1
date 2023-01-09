
$playbooksChanged = (Get-Item env:playbooksChanged).value
$playbookFilesList = (Get-Item env:playbookFilesList).value
$mainTemplateChanged = (Get-Item env:mainTemplateChanged).value
$createUiChanged = (Get-Item env:createUiChanged).value

$isDataConnectorFolderNameWithSpace = (Get-Item env:isDataConnectorFolderNameWithSpace).value
$dataConnectorFileNames = (Get-Item env:dataConnectorFileNames).value
$hasDataConnectorFileChanged = (Get-Item env:hasDataConnectorFileChanged).value

Import-Module '/dist/armttk/arm-ttk/arm-ttk.psd1' 
$BasePath = './dist'
$PackageFolderPath = './dist/Package'
$createUiDefinitionFilePath = "$PackageFolderPath/CreateUiDefinition.json"
$mainTemplateFilePath = "$PackageFolderPath/mainTemplate.json"

# RUN FOR MAINTEMPLATE.JSON FILE
if ($mainTemplateChanged -eq $true)
{
    Write-Host "Running ARM-TTK on MainTemplate.json file!"
    $MainTemplateTestResults = Test-AzTemplate -TemplatePath $mainTemplateFilePath
    $MainTemplateTestPassed =  $MainTemplateTestResults | Where-Object { -not $_.Failed }
    Write-Output $MainTemplateTestPassed

    $MainTemplateTestFailures =  $MainTemplateTestResults | Where-Object { -not $_.Passed }

    if ($MainTemplateTestFailures) {
        Write-Host "Please review and rectify the 'MainTemplate.json' file as some of the ARM-TTK tests did not pass!"
        exit 1
    } 
    else {
        Write-Host "All tests passed for the 'MainTemplate.json' file!"
    }
}

# RUN FOR CREATEUIDEFINITION.JSON FILE
if ($createUiChanged -eq $true)
{
    Write-Host "Running ARM-TTK on CreateUiDefinition.json file!"
    $CreateUiTestResults = Test-AzTemplate -TemplatePath $createUiDefinitionFilePath
    $CreateUiTestPassed =  $CreateUiTestResults | Where-Object { -not $_.Failed }
    Write-Output $CreateUiTestPassed

    $CreateUiTestFailures =  $CreateUiTestResults | Where-Object { -not $_.Passed }

    if ($CreateUiTestFailures) {
        Write-Host "Please review and rectify the 'CreateUiDefinition.json' file as some of the ARM-TTK tests did not pass!"
        exit 1
    }
    else {
        Write-Host "All tests passed for the 'CreateUiDefinition.json' file!"
    }
}

# Data Connector file change
if ($hasDataConnectorFileChanged -eq $true)
{
    Write-Host "Running ARM-TTK on Data Connectors Folder, '$dataConnectorFileNames' files!"
    $dataConnectorFolderName = "Data Connectors"
    if($isDataConnectorFolderNameWithSpace -ne $true)
    {
        $dataConnectorFolderName = "DataConnectors"
    }

    $dataConnectorFilesList = $dataConnectorFileNames.Split(" ")
    foreach($dataConnectorFileItem in $dataConnectorFilesList)
    {
        Write-Host "Running ARM-TTK on file '$dataConnectorFileItem'"
        $dataConnectorTestResults = Test-AzTemplate -TemplatePath "$BasePath/$dataConnectorFolderName/$dataConnectorFileItem"

        $dataConnectorTestPassed =  $dataConnectorTestResults | Where-Object { -not $_.Failed }
        Write-Output $dataConnectorTestPassed

        $dataConnectorFailures =  $dataConnectorTestResults | Where-Object { -not $_.Passed }

        if ($dataConnectorFailures) {
            Write-Host "Please review and rectify the Data Connectors Folder, '$dataConnectorFileItem' file as some of the ARM-TTK tests did not pass!"
            exit 1
        } 
        else {
            Write-Host "All files passed for Data Connectors Folder!"
        }
    }
}

# RUN FOR PLAYBOOKS JSON FILE
if ($playbooksChanged -eq $true)
{
    $playbookFilesListObj = $playbookFilesList.Split(" ")
    Write-Host "Running ARM-TTK on Playbooks Folder, '$playbookFilesListObj' files!"
    foreach($playbookFile in $playbookFilesListObj)
    {
        if($playbookFile.Contains(".json"))
        {
            Write-Host "Running ARM-TTK on file '$playbookFile'"
            $folderEndIndex = $playbookFile.LastIndexOf('/')
            if ($folderEndIndex -eq 0)
            {
                $folderPath = $playbookFile.substring(0)
            }
            else 
            {
                $folderPath = $playbookFile
            }
            
            $folderFilePath = "$BasePath/Playbooks/$folderPath"
            $playbooksTestResults = Test-AzTemplate -TemplatePath $folderFilePath
            
            $playbooksTestPassed =  $playbooksTestResults | Where-Object { -not $_.Failed }
            Write-Output $playbooksTestPassed

            $playbooksTestFailures =  $playbooksTestResults | Where-Object { -not $_.Passed }

            if ($playbooksTestFailures) {
                Write-Host "Please review and rectify Playbooks Folder '$folderPath' json file as some of the ARM-TTK tests did not pass!"
                exit 1
            } 
            else {
                Write-Host "All files passed for Playbooks Folder!"
            }
        }
    }
}

exit 0