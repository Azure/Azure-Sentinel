
param ($solutionName, $pullRequestNumber, $runId, $baseFolderPath, $instrumentationKey,$isPRMerged = $false)
. ./Tools/Create-Azure-Sentinel-Solution/common/LogAppInsights.ps1
$isPackagingRequired = $false
try 
{
    $customProperties = @{ 'RunId'="$runId"; 'PullRequestNumber'= "$pullRequestNumber"; "EventName"="CheckPackagingSkipStatus"; }
    if ($instrumentationKey -ne '')
    {
        Send-AppInsightsEventTelemetry -InstrumentationKey $instrumentationKey -EventName "CheckPackagingSkipStatus" -CustomProperties $customProperties
        Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Execution for CheckPackagingSkipStatus started, Job Run Id : $runId" -Severity Information -CustomProperties $customProperties
    }

    $filesList = git ls-files | Where-Object { $_ -like "Solutions/$solutionName/data/*" } | Where-Object { $_ -match ([regex]::Escape(".json")) } | Where-Object { $_ -notlike '*parameters.json' } | Where-Object { $_ -notlike '*system_generated_metadata.json' } | Where-Object { $_ -notlike '*testParameters.json' }

    Write-Host "Files List $filesList"
    if ($null -eq $filesList -or $filesList.Count -le 0)
    {
        Write-Host "Skipping as data file is not present!"
        Write-Output "isPackagingRequired=$isPackagingRequired" >> $env:GITHUB_OUTPUT
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
            Write-Output "isPackagingRequired=$isPackagingRequired" >> $env:GITHUB_OUTPUT

            $customProperties['isPackagingRequired'] = $isPackagingRequired
            if ($instrumentationKey -ne '')
            {
                Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Execution for CheckPackagingSkipStatus started, Job Run Id : $runId" -Severity Information -CustomProperties $customProperties
            }
        }
        else
        {
            # WHEN CHANGES ARE IN SOLUTION PACKAGE FOLDER THEN WE SHOULD SKIP PACKAGING 
            #$diff = git diff --diff-filter=d --name-only HEAD^ HEAD
            if ($isPRMerged) {
                git fetch --depth=1 origin master
                $diff = git diff --diff-filter=d --name-only --first-parent origin/master..
            } else {
                $diff = git diff --diff-filter=d --name-only --first-parent HEAD^ HEAD
            }
            Write-Host "List of files changed in PR: $diff"

            $changesInPackageFolder = $diff | Where-Object {$_ -notlike '*testParameters.json' } | Where-Object {$_ -like "Solutions/$solutionName/Package/*" }
            Write-Host "List of files changed in Package folder:  $changesInPackageFolder"

            if ($changesInPackageFolder.Count -gt 0)
            {
                # changes are in Package folder so skip packaging
                Write-Output "isPackagingRequired=$isPackagingRequired" >> $env:GITHUB_OUTPUT
                Write-Host "Skip packaging as changes are in Package folder!"
            }
            else
            {
                # IDENTIFY EXCLUSIONS AND IF THERE ARE NO FILES AFTER EXCLUSION THEN SKIP WORKFLOW RUN
                $exclusionList = @(".py$",".png$",".jpg$",".jpeg$",".conf$", ".svg$", ".html$", ".ps1$", ".psd1$", "requirements.txt$", "host.json$", "proxies.json$", "/function.json$", ".xml$", ".zip$", ".md$", "system_generated_metadata.json$", "testParameters.json$")

                $filteredFiles = $diff | Where-Object {$_ -match "Solutions/"} | Where-Object {$_ -notlike "Solutions/$solutionName/Package/*" } | Where-Object {$_ -notlike "Solutions/Images/*"}  

                $changesInSolutionFolder = $filteredFiles | Where-Object { $_ -notmatch ($exclusionList -join '|')  }
                Write-Host "List of files changed in Solution folder: $changesInSolutionFolder"
                # there are no changes in package folder but check if changes in pr are valid and not from exclusion list
                if ($changesInSolutionFolder.Count -gt 0)
                {
                    $isPackagingRequired = $true
                    # has changes in Solution folder and valid files
                    # WE NEED PACKAGING
                    $customProperties['isPackagingRequired'] = $isPackagingRequired
                    Write-Output "isPackagingRequired=$isPackagingRequired" >> $env:GITHUB_OUTPUT
                    Write-Host "isPackagingRequired $isPackagingRequired"
                    if ($instrumentationKey -ne '')
                    {
                        Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "CheckPackagingSkipStatus started, Job Run Id : $runId" -Severity Information -CustomProperties $customProperties
                    }
                }
                else {
                    Write-Output "isPackagingRequired=$isPackagingRequired" >> $env:GITHUB_OUTPUT
                    Write-Host "isPackagingRequired $isPackagingRequired"
                }
            }
        }
    }
}
catch
{
    Write-Output "isPackagingRequired=$isPackagingRequired" >> $env:GITHUB_OUTPUT
    Write-Host "Error in checkSkipPackagingInfo file. Error Details: $_"
    if ($instrumentationKey -ne '')
    {
        Send-AppInsightsExceptionTelemetry -InstrumentationKey $instrumentationKey -Exception $_.Exception -CustomProperties @{ 'RunId' = "$runId"; 'SolutionName' = "$solutionName"; 'PullRequestNumber' = "$pullRequestNumber"; 'ErrorDetails' = "CheckPackagingSkipStatus : Error occured in catch block: $_"; 'EventName' = "CheckPackagingSkipStatus"; }
    }
    exit 1
}