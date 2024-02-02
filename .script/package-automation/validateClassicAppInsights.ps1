param($runId, $pullRequestNumber, $instrumentationKey, $baseFolderPath)

Write-Host "Inside of Validate Classic App Insights!"

try {
  $baseFolderPath = $baseFolderPath + "/"
  $baseFolderPath = $baseFolderPath.replace("//", "/")

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

        $hasWorkspaceResourceId = [bool]($appInsightComponentObject.PSobject.Properties.name -match "WorkspaceResourceId")
        if (!$hasWorkspaceResourceId) {
          # if not present then throw error by adding to list later
          $appInsightResourceWithoutWorkspaceResourceList += $file;
        }
      }
    }

    return $appInsightResourceWithoutWorkspaceResourceList;
  }

  # identify if changes are in dataConnectors folder which is at root of the repo
  $diff = git diff --diff-filter=d --name-only --first-parent HEAD^ HEAD
  Write-Host "List of files in PR: $diff"
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
  }

  # when changes are in Solution folder
  . $PSScriptRoot/getSolutionName.ps1 $runId $pullRequestNumber $instrumentationKey $false
  $hasSolutionName = $solutionName -eq '' ? $false : $true
  if ($hasSolutionName) {
    Write-Host "SolutionName is $solutionName"
    $solutionFolderPath = 'Solutions/' + $solutionName + "/"
    $filesinSolutions = git ls-files | Where-Object { $_ -like "$solutionFolderPath*" }
    Write-Host "Solution files $filesinSolutions"
    if ($null -ne $filesinSolutions -and $filesinSolutions.Count -gt 0) {
      $filterSolutionFiles = $filesinSolutions | Where-Object { $_ -like '*azureDeploy*' }

      if ($null -ne $filterSolutionFiles -and $filterSolutionFiles.Count -gt 0) {
        $filterSolutionFilesCount = $filterSolutionFiles.Count
        Write-Host "Number of azuredeploy files found in Solution $filterSolutionFilesCount"
        
        $appInsightResourceWithoutWorkspaceResourceList = @()
        $appInsightResourceWithoutWorkspaceResourceList = GetFilesWithoutWorkspaceResourceIds -filesList $filterSolutionFiles

        if ($appInsightResourceWithoutWorkspaceResourceList.Count -gt 0) {
          Write-Host "::error:: Please add property 'WorkspaceResourceId' for 'Microsoft.Insights/components' type in below given file(s)!"
          foreach ($filePath in $appInsightResourceWithoutWorkspaceResourceList) {
            Write-Host "::error:: --> $filePath"
          }
        }
      }
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