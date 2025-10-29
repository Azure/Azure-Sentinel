param($runId, $pullRequestNumber, $instrumentationKey, $baseFolderPath)

Write-Host "Inside of Validate Classic App Insights!"

try {
  function ReadFileContent($filePath) {
    try {
        if (!(Test-Path -Path "$filePath")) {
            return $null;
        }

        $stream = New-Object System.IO.StreamReader -Arg "$filePath";
        $content = $stream.ReadToEnd();
        $stream.Close();

        return ($null -eq $content -or $content -eq '') ? $null : $content;
    }
    catch {
        Write-Host "Error occured in ReadFileContent. Error details : $_"
        return $null;
    }
  }

  function GetFilesWithoutWorkspaceResourceIds($filesList) {
    $appInsightResourceWithoutWorkspaceResourceList = @()
    foreach($file in $filesList) {
      $filePath = $baseFolderPath + "/" + $file;
      $filePath = $filePath.replace("//", "/")
      Write-Host "File Path is $filePath"
      $fileHasAppInsightsComponentType = Select-String -Path "$filePath" -Pattern '"type": "Microsoft.Insights/components"', '"type":"Microsoft.Insights/components"'

      if ($null -ne $fileHasAppInsightsComponentType) {
        $fileContent = ReadFileContent -filePath "$filePath"
        $objFileContent = $fileContent | ConvertFrom-Json 
        $appInsightComponentObject = $objFileContent.resources | Where-Object { $_.type -eq 'Microsoft.Insights/components'}

        $hasWorkspaceResourceId = [bool]($appInsightComponentObject.properties.PSobject.Properties.name -match "WorkspaceResourceId")
        if (!$hasWorkspaceResourceId) {
          # if not present then throw error by adding to list later
          $appInsightResourceWithoutWorkspaceResourceList += $file;
        }
      }
    }

    return $appInsightResourceWithoutWorkspaceResourceList;
  }

  # identify if changes are in dataConnectors folder which is at root of the repo
  $diff = git diff --diff-filter=A --name-only --first-parent HEAD^ HEAD
  Write-Host "List of new files added in PR for Standalone DataConnectors: $diff"
  $standaloneDataConnectors = $diff | Where-Object { $_ -like 'DataConnectors/*' -and $_ -like '*azuredeploy*' }
  $hasStandaloneDataConnectors = ($null -ne $standaloneDataConnectors -and $standaloneDataConnectors.Count -gt 0) ? $true : $false

  if ($hasStandaloneDataConnectors) {
    Write-Host "Standalone dataConnector files $standaloneDataConnectors"
    $failedStandaloneDataConnectorsList = @()
    # has change in standalone dataconnectors folder
    $failedStandaloneDataConnectorsList = GetFilesWithoutWorkspaceResourceIds -filesList $standaloneDataConnectors

    if ($failedStandaloneDataConnectorsList.Count -gt 0) {
      Write-Host "::error:: Please add property 'WorkspaceResourceId' for 'Microsoft.Insights/components' type in below given file(s)!"
      foreach ($filePath in $failedStandaloneDataConnectorsList) {
        Write-Host "::error:: --> $filePath"
      }
    }
  } else {
    Write-Host "Skipping as there are no new azuredeploy files for validation in standalone data connectors!"
  }

  # when changes are in solutions folder in azuredeploy file
  $solutionFilesdiff = git diff --diff-filter=A --name-only --first-parent HEAD^ HEAD;
  Write-Host "List of new files added in PR for Solution: $diff"
  $solutionsAzureDeployFilesPath = $solutionFilesdiff | Where-Object { $_ -like 'Solutions/*' -and $_ -like '*azuredeploy*' }

  if ($solutionsAzureDeployFilesPath.Count -gt 0) {
    # has some files of azuredeploy which are newly added in PR
    $appInsightResourceWithoutWorkspaceResourceList = @()
    $appInsightResourceWithoutWorkspaceResourceList = GetFilesWithoutWorkspaceResourceIds -filesList $solutionsAzureDeployFilesPath

    if ($appInsightResourceWithoutWorkspaceResourceList.Count -gt 0) {
      Write-Host "::error:: Please add property 'WorkspaceResourceId' for 'Microsoft.Insights/components' type in below given file(s)!"
      foreach ($filePath in $appInsightResourceWithoutWorkspaceResourceList) {
        Write-Host "::error:: --> $filePath"
      }
    }
  } else {
    Write-Host "Skipping as there are no new azuredeploy files for validation in Solutions!"
  }

  if (($null -ne $failedStandaloneDataConnectorsList -and 
  $failedStandaloneDataConnectorsList.Count -gt 0) -or 
  ($null -ne $appInsightResourceWithoutWorkspaceResourceList -and $appInsightResourceWithoutWorkspaceResourceList.Count -gt 0)) {
    exit 1
  }
}
catch {
  Write-Host "Error Occured in validateClassicAppInsights script. Error Details: $_"
  exit 1
}