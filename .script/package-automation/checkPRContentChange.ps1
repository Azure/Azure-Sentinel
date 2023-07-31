param ($solutionName, $pullRequestNumber, $runId, $instrumentationKey)
. ./Tools/Create-Azure-Sentinel-Solution/common/LogAppInsights.ps1

try {
    $customProperties = @{ 'RunId' = "$runId"; 'PullRequestNumber' = "$pullRequestNumber"; "EventName" = "CheckContentPR"; }

    if ($instrumentationKey -ne '')
    {
        Send-AppInsightsEventTelemetry -InstrumentationKey $instrumentationKey -EventName "CheckContentPR" -CustomProperties $customProperties

        Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Execution for CheckContentPR started, Job Run Id : $runId" -Severity Information -CustomProperties $customProperties
    }
    function GetValidDataConnectorFileNames { 
        Param
        (
            [Parameter(Mandatory = $true, Position = 0)]
            [System.Array] $dataConnectorFiles
        )
        $newDataConnectorFilesWithoutExcludedFiles = @()
        foreach ($item in $dataConnectorFiles) {
            $hostFileExist = $item -match ([regex]::Escape("host.json"))
            $proxiesFileExist = $item -match ([regex]::Escape("proxies.json"))
            $azureDeployFileExist = $item -match ([regex]::Escape("azureDeploy"))
            $functionFileExist = $item -match ([regex]::Escape("function.json"))
            if ($hostFileExist -or $proxiesFileExist -or $azureDeployFileExist -or $functionFileExist) 
            { }
            else { 
                $newDataConnectorFilesWithoutExcludedFiles += $item
            }
        }
        return $newDataConnectorFilesWithoutExcludedFiles;
    }

    $diff = git diff --diff-filter=d --name-only HEAD^ HEAD
    Write-Host "List of files in Pull Request: $diff"

    # FILTER OUT FILES AND CHECK IF THERE ARE ANY CHNAGES IN FILES BY WHICH USER CAN CREATE PACKAGE.
    $filterDataFiles = $diff | Where-Object { $_ -like "Solutions/$solutionName/Data/*" } | Where-Object { $_ -match ([regex]::Escape(".json")) } | Where-Object { $_ -notlike '*system_generated_metadata.json' }

    $filterAnalyticRuleFiles = $diff | Where-Object { $_ -like "Solutions/$solutionName/Analytic Rules/*" } | Where-Object { $_ -match ([regex]::Escape(".yaml") -or ([regex]::Escape(".yml"))) }

    $filterHuntingQueryFiles = $diff | Where-Object { $_ -like "Solutions/$solutionName/Hunting Queries/*" } | Where-Object { $_ -match ([regex]::Escape(".yaml") -or ([regex]::Escape(".yml"))) }

    $filterDataConnectorFiles = $diff | Where-Object { $_ -like "Solutions/$solutionName/DataConnectors/*" } | Where-Object { $_ -match ([regex]::Escape(".json")) }
    if ($filterDataConnectorFiles.Count -gt 0) {
        $filterDataConnectorFiles = GetValidDataConnectorFileNames($filterDataConnectorFiles)
    }

    $filterDataConnectorWithSpaceFiles = $diff | Where-Object { $_ -like "Solutions/$solutionName/Data Connectors/*" } | Where-Object { $_ -match ([regex]::Escape(".json")) }
    if ($filterDataConnectorWithSpaceFiles.Count -gt 0) {
        $filterDataConnectorWithSpaceFiles = GetValidDataConnectorFileNames($filterDataConnectorWithSpaceFiles)
    }

    $filterPlaybookFiles = $diff | Where-Object { $_ -like "Solutions/$solutionName/Playbooks/*" } | Where-Object { $_ -match ([regex]::Escape(".json")) } | Where-Object { $_ -notlike '*swagger*' }

    $filterCustomConnectorInPlaybooksFolderFiles = $diff | Where-Object { $_ -like "Solutions/$solutionName/Playbooks/CustomConnector/*" } | Where-Object { $_ -match ([regex]::Escape(".json")) } | Where-Object { $_ -notlike '*swagger*' }

    $filterCustomConnectorInSolutionsFolderFiles = $diff | Where-Object { $_ -like "Solutions/$solutionName/*Connector/*" } | Where-Object { $_ -match ([regex]::Escape(".json")) } | Where-Object { $_ -notlike '*swagger*' }

    $filterParserFiles = $diff | Where-Object { $_ -like "Solutions/$solutionName/Parsers/*" } | Where-Object { $_ -match ([regex]::Escape(".json") -or ([regex]::Escape(".txt"))) }

    $filterWatchlistFiles = $diff | Where-Object { $_ -like "Solutions/$solutionName/Watchlists/*" } | Where-Object { $_ -match ([regex]::Escape(".json")) }

    $filterWatchlistInWorkbookFiles = $diff | Where-Object { $_ -like "Solutions/$solutionName/Workbooks/Watchlist/*" } | Where-Object { $_ -match ([regex]::Escape(".json")) }

    $filterWorkbooksFiles = $diff | Where-Object { $_ -like "Solutions/$solutionName/Workbooks/*" } | Where-Object { $_ -match ([regex]::Escape(".json")) }

    $filterDataFilesCount = $filterDataFiles.Count
    $filterAnalyticRuleFilesCount = $filterAnalyticRuleFiles.Count
    $filterHuntingQueryFilesCount = $filterHuntingQueryFiles.Count
    $filterDataConnectorFilesCount = $filterDataConnectorFiles.Count
    $filterDataConnectorWithSpaceFilesCount = $filterDataConnectorWithSpaceFiles.Count
    $filterPlaybookFilesCount = $filterPlaybookFiles.Count
    $filterParserFilesCount = $filterParserFiles.Count
    $filterWatchlistFilesCount = $filterWatchlistFiles.Count
    $filterWatchlistInWorkbookFilesCount = $filterWatchlistInWorkbookFiles.Count
    $filterWorkbooksFilesCount = $filterWorkbooksFiles.Count
    $filterCustomConnectorInPlaybooksFolderFilesCount = $filterCustomConnectorInPlaybooksFolderFiles.Count
    $filterCustomConnectorInSolutionsFolderFilesCount = $filterCustomConnectorInSolutionsFolderFiles.Count

    $details = "filterDataFilesCount $filterDataFilesCount,
    filterAnalyticRuleFilesCount $filterAnalyticRuleFilesCount, 
    filterHuntingQueryFilesCount $filterHuntingQueryFilesCount, 
    filterDataConnectorFilesCount $filterDataConnectorFilesCount, 
    filterDataConnectorWithSpaceFilesCount $filterDataConnectorWithSpaceFilesCount,
    filterPlaybookFilesCount $filterPlaybookFilesCount, 
    filterParserFilesCount $filterParserFilesCount, 
    filterWatchlistFilesCount $filterWatchlistFilesCount, 
    filterWatchlistInWorkbookFilesCount $filterWatchlistInWorkbookFilesCount, 
    filterWorkbooksFilesCount $filterWorkbooksFilesCount,
    filterCustomConnectorInPlaybooksFolderFilesCount $filterCustomConnectorInPlaybooksFolderFilesCount,
    filterCustomConnectorInSolutionsFolderFilesCount $filterCustomConnectorInSolutionsFolderFilesCount"
    Write-Host "$details"

    if ($filterDataFilesCount -gt 0 -or
        $filterAnalyticRuleFilesCount -gt 0 -or 
        $filterHuntingQueryFilesCount -gt 0 -or
        $filterDataConnectorFilesCount -gt 0 -or
        $filterDataConnectorWithSpaceFilesCount -gt 0 -or
        $filterPlaybookFilesCount -gt 0 -or
        $filterParserFilesCount -gt 0 -or
        $filterWatchlistFilesCount -gt 0 -or
        $filterWorkbookWatchlistFiles -gt 0 -or
        $filterWatchlistInWorkbookFilesCount -gt 0 -or
        $filterWorkbooksFilesCount -gt 0 -or
        $filterCustomConnectorInPlaybooksFolderFilesCount -gt 0 -or
        $filterCustomConnectorInSolutionsFolderFilesCount -gt 0) {
        # WHEN THERE ARE ANY CHANGES FOR WHICH PACKAGING CAN BE REGENERATED WE WILL SET LABEL ON THAT PR AS CONTENT-PACKAGE
        Write-Host "Changes found in Content Package!"
        Write-Output "hasContentPackageChange=$true" >> $env:GITHUB_OUTPUT
        $customProperties["hasContentPackageChange"] = 'true'

        if ($instrumentationKey -ne '')
        {
            Send-AppInsightsEventTelemetry -InstrumentationKey $instrumentationKey -EventName "CheckContentPR" -CustomProperties $customProperties
        }
    }
    else {
        Write-Host "Changes Not found in Content Package"
        Write-Output "hasContentPackageChange=$false" >> $env:GITHUB_OUTPUT
        $customProperties = @{ 'RunId' = "$runId"; 'PullRequestNumber' = "$pullRequestNumber"; "EventName" = "CheckContentPR"; "hasContentPackageChange" = "false"; }

        if ($instrumentationKey -ne '')
        {
            Send-AppInsightsEventTelemetry -InstrumentationKey $instrumentationKey -EventName "CheckContentPR" -CustomProperties $customProperties
        }
    }
}
catch {
    Write-Output "hasContentPackageChange=$false" >> $env:GITHUB_OUTPUT
    $errorDetails = $_
    $errorInfo = $_.Exception
    Write-Output "Error Details $errorDetails , Error Info $errorInfo"
    
    if ($instrumentationKey -ne '')
    {
        Send-AppInsightsExceptionTelemetry -InstrumentationKey $instrumentationKey -Exception $_.Exception -CustomProperties @{ 'RunId' = "$runId"; 'SolutionName' = "$solutionName"; 'PullRequestNumber' = "$pullRequestNumber"; 'ErrorDetails' = "CheckContentPR : Error occured in catch block: $_"; 'EventName' = "CheckContentPR"; "hasContentPackageChange" = "false"; }
    }
    Write-Host "Package-generator: Error occured in catch block!"
    exit 1
}