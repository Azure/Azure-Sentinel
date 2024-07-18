
try {
    $diff = git diff --diff-filter=d --name-only --first-parent HEAD^ HEAD
    Write-Host "List of files in PR: $diff"

    $hasmainTemplateChanged = $false
    $hasCreateUiDefinitionTemplateChanged = $false

    $isChangeInSolutionsFolder = [bool]($diff | Where-Object {$_ -like 'Solutions/*'})
    if (!$isChangeInSolutionsFolder)
    {
        Write-Host "Skipping as change is not in Solutions folder!"
        exit 0
    }

    $requiredFiles = @("mainTemplate.json", "createUiDefinition.json")
    $filteredFiles = $diff | Where-Object {$_ -match ($requiredFiles -Join "|")}
    Write-Host "Filtered Files $filteredFiles"

    $sName = ''
    $hasmainTemplateChanged = $false
    $hasCreateUiDefinitionTemplateChanged = $false

    if ($filteredFiles.Count -gt 0)
    {
        $mainTemplateValue = $filteredFiles -match "mainTemplate.json" 
        $createUiValue = $filteredFiles -match "createUiDefinition.json"

        if ($mainTemplateValue -or $createUiValue)
        {
            $hasmainTemplateChanged = $true
            $hasCreateUiDefinitionTemplateChanged = $true
        }

        if ($filteredFiles.Count -eq 1)
        {
            $packageIndex = $filteredFiles.IndexOf("/Package")
            $sName = $filteredFiles.SubString(10, $packageIndex - 10)
        }
        else
        {
            $packageIndex = $filteredFiles[0].IndexOf("/Package")
            $sName = $filteredFiles[0].SubString(10, $packageIndex - 10)
        }
    }

    Write-Host "solutionName $sName, mainTemplateChanged $hasmainTemplateChanged, createUiChanged $hasCreateUiDefinitionTemplateChanged"
    Write-Output "solutionName=$sName" >> $env:GITHUB_OUTPUT
    Write-Output "mainTemplateChanged=$hasmainTemplateChanged" >> $env:GITHUB_OUTPUT
    Write-Output "createUiChanged=$hasCreateUiDefinitionTemplateChanged" >> $env:GITHUB_OUTPUT
}
catch {
    Write-Host "Skipping as exception has occured Error Details: $_"
    Write-Output "solutionName=''" >> $env:GITHUB_OUTPUT
    Write-Output "mainTemplateChanged=$false" >> $env:GITHUB_OUTPUT
    Write-Output "createUiChanged=$false" >> $env:GITHUB_OUTPUT
}