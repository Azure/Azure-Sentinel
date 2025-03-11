param($runId, $pullRequestNumber, $instrumentationKey, $baseFolderPath, $isPRMerged)

try {
  Write-Host "Inside of Validate Parameter Field Types!"

  $baseFolderPath = $baseFolderPath + "/"
  $baseFolderPath = $baseFolderPath.replace("//", "/")

  # Get Solution Name
  . $PSScriptRoot/getSolutionName.ps1 $runId $pullRequestNumber $instrumentationKey $false
  if ($solutionName -eq '')
  {
    exit 0 
  }

  function GetInvalidFields($resourceParameterProp) {
    $fieldsToValidate = $resourceParameterProp.PSobject.Properties.name | Where-Object { $_ -like "*Password*" -or 
      $_ -like "*ClientSecret*" -or 
      $_ -like "*Authorization*" -or 
      $_ -like "*AuthorizationCode*" -or 
      $_ -like "*Secret*" -or 
      $_ -like "*token*" -or 
      $_ -like "*apptoken*" -or
      $_ -like "*appkey*"
    };

    $invalidFields = @();
    if ($null -eq $fieldsToValidate) {
      # there are no fields to validate
      return $invalidFields
    }

    $validateFields = $resourceParameterProp.PSobject.Properties.name | Where-Object { $_.ToLower() -in $fieldsToValidate };

    foreach($item in $validateFields) {
      $record = $resourceParameterProp.PSobject.Properties -match "$item";
      if ($record.Value.type.ToLower() -ne 'securestring') {
        $invalidFields += $item
      }
    }

    return $invalidFields;
  }

  $diff = git diff --diff-filter=d --name-only --first-parent HEAD^ HEAD
  Write-Host "List of files in PR: $diff"

  $solutionMainTemplatePath = 'Solutions/' + $solutionName + "/Package/mainTemplate.json"
  $hasMainTemplateFile = $diff | Where-Object {$_ -match "$solutionMainTemplatePath"}

  if ($null -eq $hasMainTemplateFile) {
    Write-Host "Skipping validation as there is no change in maintemplate.json file for solution $solutionName"
  } else {
    $mainTemplateFileContent = Get-Content "$solutionMainTemplatePath" | ConvertFrom-Json

    $hasInvalidGlobalParameterType = $false
    $hasInvalidResourceParameterType = $false
    # identify in global parameters
    $globalParameters = $mainTemplateFileContent.parameters
    if ($null -ne $globalParameters -and $globalParameters.Count -gt 0) {
      $globalInvalidFieldsList = @();
      $globalInvalidFieldsList = GetInvalidFields -resourceParameterProp $globalParameters

      if ($null -ne $globalInvalidFieldsList -and $globalInvalidFieldsList.Count -gt 0) {
        $hasInvalidGlobalParameterType = $true
        Write-Host "Invalid global level parameters field(s) type. Please update the 'type' value for below given list to 'securestring'"
        foreach ($item in $globalInvalidFieldsList) {
          Write-Host "--> $item"
        }
      }
    }

    # identify in active resource parameters
    $resourceContent = $mainTemplateFileContent.resources | Where-Object { $_.type -eq 'Microsoft.OperationalInsights/workspaces/providers/contentTemplates' }

    if ($null -ne $resourceContent -and $resourceContent.Count -gt 0) {
      foreach($rc in $resourceContent) {
        $rcParam = $rc.properties.mainTemplate.parameters
        $resourceInvalidFieldsList = @();
        $resourceInvalidFieldsList = GetInvalidFields -resourceParameterProp $rcParam

        if ($resourceInvalidFieldsList.Count -gt 0) {
          $hasInvalidResourceParameterType = $true
          Write-Host "Invalid resource level parameters field(s) type. Please update the 'type' value for below given list to 'securestring'"
          foreach ($item in $resourceInvalidFieldsList) {
            Write-Host "--> $item"
          }
        }
      }
    }

    if ($hasInvalidResourceParameterType -or $hasInvalidGlobalParameterType) {
      exit 1
    }
  }
}
catch {
  Write-Host "Error occured in validateFieldTypes file. Error Details : $_"
  exit 1
}