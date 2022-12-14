
$playbooksChanged = (Get-Item env:playbooksChanged).value
$playbookFilesList = (Get-Item env:playbookFilesList).value
$mainTemplateOrCreateUiDefinitionTemplateChanged = (Get-Item env:mainTemplateOrCreateUiDefinitionTemplateChanged).value

Write-Host "List all playbook files $playbookFilesList"

$isDataConnectorFolderNameWithSpace = (Get-Item env:isDataConnectorFolderNameWithSpace).value
$dataConnectorFileNames = (Get-Item env:dataConnectorFileNames).value
$hasDataConnectorFileChanged = (Get-Item env:hasDataConnectorFileChanged).value

Import-Module '/dist/armttk/arm-ttk/arm-ttk.psd1' 
$MainTemplatePath = './dist/Package'

# RUN FOR MAINTEMPLATE.JSON FILE
if ($mainTemplateOrCreateUiDefinitionTemplateChanged -eq $true)
{
    Write-Host "Running ARM-TTK on MainTemplate.json and/or CreateUiDefinition.json file as change is identified those files."
    $MainTemplateTestResults = Test-AzTemplate -TemplatePath $MainTemplatePath
    $MainTemplateTestPassed =  $MainTemplateTestResults | Where-Object { -not $_.Failed }
    Write-Output $MainTemplateTestPassed

    $MainTemplateTestFailures =  $MainTemplateTestResults | Where-Object { -not $_.Passed }

    if ($MainTemplateTestFailures) {
        Write-Host "CreateUiDefinition.json and/or MainTemplate.json templates did not pass the arm-ttk tests"
        exit 1
    } 
    else {
        Write-Host "All tests passed for the given files of CreateUiDefinition.json and/or MainTemplate.json!"
    }
}

# Data Connector file change
if ($hasDataConnectorFileChanged -eq $true)
{
    Write-Host "Running ARM-TTK on Data Connectors Folder, '$dataConnectorFileNames' files as change is identified those file"
    $dataConnectorFolderName = "Data Connectors"
    if($isDataConnectorFolderNameWithSpace -ne $true)
    {
        $dataConnectorFolderName = "DataConnectors"
    }

    $dataConnectorFilesList = $dataConnectorFileNames.Split(" ")
    foreach($dataConnectorFileItem in $dataConnectorFilesList)
    {
        Write-Host "Running ARM-TTK on file '$dataConnectorFileItem'"
        $dataConnectorTestResults = Test-AzTemplate -TemplatePath "./dist/$dataConnectorFolderName/$dataConnectorFileItem"

        $dataConnectorTestPassed =  $dataConnectorTestResults | Where-Object { -not $_.Failed }
        Write-Output $dataConnectorTestPassed

        $dataConnectorFailures =  $dataConnectorTestResults | Where-Object { -not $_.Passed }

        if ($dataConnectorFailures) {
            Write-Host "Data Connectors Folder, '$dataConnectorFileItem' file did not pass the arm-ttk tests!"
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
    Write-Host "Running ARM-TTK on Playbooks Folder, '$playbookFilesListObj' files as change is identified this file"
    foreach($playbookFile in $playbookFilesListObj)
    {
        if($playbookFile.Contains(".json"))
        {
            Write-Host "Running ARM-TTK on file '$playbookFile'"
            $folderEndIndex = $playbookFile.LastIndexOf('/')
            $folderPath = $playbookFile.substring(0, $folderEndIndex)
            $playbooksTestResults = Test-AzTemplate -TemplatePath "./dist/Playbooks/$folderPath"

            $playbooksTestPassed =  $playbooksTestResults | Where-Object { -not $_.Failed }
            Write-Output $playbooksTestPassed

            $playbooksTestFailures =  $playbooksTestResults | Where-Object { -not $_.Passed }

            if ($playbooksTestFailures) {
                Write-Host "Playbooks Folder '$folderPath' json file did not pass the arm-ttk tests!"
                exit 1
            } 
            else {
                Write-Host "All files passed for Playbooks Folder!"
                #exit 0
            }
        }
    }
}

exit 0