param($runId, $pullRequestNumber, $instrumentationKey, $baseFolderPath, $SolutionPath)

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

  if ($SolutionPath) {
    $solutionsRoot = [System.IO.Path]::GetFullPath((Join-Path $baseFolderPath "Solutions")).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    $resolvedSolutionPath = [System.IO.Path]::GetFullPath($SolutionPath)
    if ([System.IO.Path]::GetDirectoryName($resolvedSolutionPath) -ne $solutionsRoot -or
        -not (Test-Path $resolvedSolutionPath -PathType Container) -or
        ((Get-Item $resolvedSolutionPath).Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
      throw "Invalid solution folder '$SolutionPath'. Expected an existing direct child of '$solutionsRoot'."
    }
    $solutionAzureDeployFiles = @(Get-ChildItem $resolvedSolutionPath -Recurse -File | Where-Object { $_.Name -like '*azuredeploy*' } |
      ForEach-Object { [System.IO.Path]::GetRelativePath($baseFolderPath, $_.FullName).Replace('\', '/') })
    if ($solutionAzureDeployFiles.Count -gt 0) {
      Write-Host "Current azuredeploy files in solution folder: $solutionAzureDeployFiles"
    }
    else {
      Write-Host "No current azuredeploy files found in the selected solution folder."
    }
    Write-Host "Skipping standalone DataConnectors validation because it is outside the selected solution folder."
    $standaloneDataConnectors = @()
    $hasStandaloneDataConnectors = $false
  }
  else {
    # Preserve CI's commit-diff based discovery when no solution folder is supplied.
    $diff = git diff --diff-filter=A --name-only --first-parent HEAD^ HEAD
    Write-Host "List of new files added in PR for Standalone DataConnectors: $diff"
    $standaloneDataConnectors = $diff | Where-Object { $_ -like 'DataConnectors/*' -and $_ -like '*azuredeploy*' }
    $hasStandaloneDataConnectors = ($null -ne $standaloneDataConnectors -and $standaloneDataConnectors.Count -gt 0) ? $true : $false
  }

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
  } elseif (-not $SolutionPath) {
    Write-Host "Skipping as there are no new azuredeploy files for validation in standalone data connectors!"
  }

  # Check the explicit current solution folder, or preserve CI's commit-diff based discovery.
  if ($SolutionPath) {
    $solutionsAzureDeployFilesPath = $solutionAzureDeployFiles
  }
  else {
    $solutionFilesdiff = git diff --diff-filter=A --name-only --first-parent HEAD^ HEAD
    Write-Host "List of new files added in PR for Solution: $solutionFilesdiff"
    $solutionsAzureDeployFilesPath = $solutionFilesdiff | Where-Object { $_ -like 'Solutions/*' -and $_ -like '*azuredeploy*' }
  }

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
    if ($SolutionPath) {
      Write-Host "Skipping solution azuredeploy validation — no current azuredeploy files found in the selected folder."
    }
    else {
      Write-Host "Skipping as there are no new azuredeploy files for validation in Solutions!"
    }
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