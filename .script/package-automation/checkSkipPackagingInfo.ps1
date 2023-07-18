
param ($solutionName, $pullRequestNumber, $runId, $baseFolderPath, $instrumentationKey)
. ./Tools/Create-Azure-Sentinel-Solution/common/LogAppInsights.ps1

try 
{
    $customProperties = @{ 'RunId'="$runId"; 'PullRequestNumber'= "$pullRequestNumber"; "EventName"="CheckPackagingSkipStatus"; }
    if ($instrumentationKey -ne '')
    {
        Send-AppInsightsEventTelemetry -InstrumentationKey $instrumentationKey -EventName "CheckPackagingSkipStatus" -CustomProperties $customProperties
        Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Execution for CheckPackagingSkipStatus started, Job Run Id : $runId" -Severity Information -CustomProperties $customProperties
    }

    $filesList = git ls-files | Where-Object { $_ -like "Solutions/$solutionName/data/*" } | Where-Object { $_ -match ([regex]::Escape(".json")) } | Where-Object { $_ -notlike '*parameters.json' } | Where-Object { $_ -notlike '*system_generated_metadata.json' }

    Write-Host "Files List $filesList"
    if ($null -eq $filesList -or $filesList.Count -le 0)
    {
        Write-Host "Skipping as data file is not present!"
        Write-Output "isPackagingRequired=$false" >> $env:GITHUB_OUTPUT
    }
    else
    {
        Write-Host "Data file is present for Solution $solutionName"

        $dataFilePath = $baseFolderPath + $filesList
        Write-Host "Data File Path $dataFilePath"
        $dataFileContentObject = Get-Content "$dataFilePath" | ConvertFrom-Json

        $hasCreatePackageAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match ([regex]::Escape("createPackage")))
        $isCreatePackageSetToTrue = $dataFileContentObject.createPackage
        if ($hasCreatePackageAttribute -eq $true -and $isCreatePackageSetToTrue -eq $false) {
            Write-Host "::warning::Skipping Package Creation for Solution '$solutionName', as Data File has attribute 'createPackage' set to False!"
            Write-Output "isPackagingRequired=$false" >> $env:GITHUB_OUTPUT

            $customProperties['isPackagingRequired'] = $false
            if ($instrumentationKey -ne '')
            {
                Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Execution for CheckPackagingSkipStatus started, Job Run Id : $runId" -Severity Information -CustomProperties $customProperties
            }
        }
        else
        {
            # WHEN CHANGES ARE IN SOLUTION PACKAGE FOLDER THEN WE SHOULD SKIP PACKAGING 
            $diff = git diff --diff-filter=d --name-only HEAD^ HEAD
            Write-Host "List of files changed in PR: $diff"
            $filteredFiles = $diff | Where-Object {$_ -like "Solutions/$solutionName/Package/*" } | Where-Object { $_ -match ([regex]::Escape(".json")) }

            $isPackagingRequired = $false
            if ($filteredFiles.Count -le 0)
            {
                # WE NEED PACKAGING
                $isPackagingRequired = $true
                $customProperties['isPackagingRequired'] =
                Write-Output "isPackagingRequired=$true" >> $env:GITHUB_OUTPUT
            }

            $customProperties['isPackagingRequired'] = $isPackagingRequired
            Write-Host "isPackagingRequired set to $isPackagingRequired"
            Write-Output "isPackagingRequired=$isPackagingRequired" >> $env:GITHUB_OUTPUT

            if ($instrumentationKey -ne '')
            {
                Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "CheckPackagingSkipStatus started, Job Run Id : $runId" -Severity Information -CustomProperties $customProperties
            }
        }
    }
}
catch
{
    Write-Output "isPackagingRequired=$true" >> $env:GITHUB_OUTPUT
    
    if ($instrumentationKey -ne '')
    {
        Send-AppInsightsExceptionTelemetry -InstrumentationKey $instrumentationKey -Exception $_.Exception -CustomProperties @{ 'RunId' = "$runId"; 'SolutionName' = "$solutionName"; 'PullRequestNumber' = "$pullRequestNumber"; 'ErrorDetails' = "CheckPackagingSkipStatus : Error occured in catch block: $_"; 'EventName' = "CheckPackagingSkipStatus"; }
    }
    exit 1
}