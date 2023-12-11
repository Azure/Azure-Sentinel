param($runId, $pullRequestNumber, $instrumentationKey)
. ./Tools/Create-Azure-Sentinel-Solution/common/LogAppInsights.ps1

$solutionName = ''
try 
{
    if ($instrumentationKey -ne '')
    {
        Send-AppInsightsEventTelemetry -InstrumentationKey $instrumentationKey -EventName "GetSolutionName" -CustomProperties @{ 'RunId'="$runId"; 'PullRequestNumber'= "$pullRequestNumber"; "EventName"="GetSolutionName"; }

        Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Execution for getSolutionName started, Job Run Id : $runId" -Severity Information -CustomProperties @{ 'RunId'="$runId"; 'PullRequestNumber'= "$pullRequestNumber"; "EventName"="GetSolutionName"; }
    }

    $diff = git diff --diff-filter=d --name-only HEAD^ HEAD
    Write-Host "List of files in PR: $diff"

    $filteredFiles = $diff | Where-Object {$_ -match "Solutions/"} | Where-Object {$_ -notlike "Solutions/Images/*"} | Where-Object {$_ -notlike "Solutions/*.md"} | Where-Object { $_ -notlike '*system_generated_metadata.json' } | Where-Object { $_ -notlike '*testParameters.json' } 
    Write-Host "Filtered Files $filteredFiles"

    # IDENTIFY EXCLUSIONS AND IF THERE ARE NO FILES AFTER EXCLUSION THEN SKIP WORKFLOW RUN
    $exclusionList = @(".py$",".png$",".jpg$",".jpeg$",".conf$", ".svg$", ".html$", ".ps1$", ".psd1$", "requirements.txt$", "host.json$", "proxies.json$", "/function.json$", ".xml$", ".zip$", ".md$")

    $filterOutExclusionList = $filteredFiles | Where-Object { $_ -notmatch ($exclusionList -join '|')  }

    if ($filterOutExclusionList.Count -le 0)
    {
        Write-Host "Skipping GitHub Action as changes in PR are not valid and contains only excluded files!"
        Write-Output "solutionName=" >> $env:GITHUB_OUTPUT
        exit 0
    }

    if ($filteredFiles.Count -gt 0)
    {
        if ($instrumentationKey -ne '')
        {
            Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Executing getSolutionName and inside of Filtered Files, Job Run Id : $runId" -Severity Information -CustomProperties @{ 'RunId'="$runId"; 'PullRequestNumber'="$pullRequestNumber"; 'FilesChanged'="$filteredFiles"; "EventName"="GetSolutionName";}
        }

        foreach ($currentFile in $filteredFiles)
        {
            $solutionIndex = $currentFile.IndexOf("Solutions/")
            if ($solutionName -eq '' -and $solutionIndex -eq 0)
            {
                $countForwardSlashes = ($currentFile.Split('/')).count-1
                if ($countForwardSlashes -gt 1)
                {
                    # identify solution Name
                    $solutionNameWithSubstring = $currentFile.SubString($solutionIndex + 10)
                    $firstForwardSlashIndex = $solutionNameWithSubstring.IndexOf("/")
                    $solutionName = $solutionNameWithSubstring.SubString(0, $firstForwardSlashIndex)
                    Write-Host "Solution Name is $solutionName"
                }
            }
            else
            {
                break;
            }
        }

        if ($solutionName -eq 'SAP')
        {
            Write-Host "Skipping Github workflow for SAP Solution as solution dont have data file and SolutionMetadata file!"
            Write-Output "solutionName=" >> $env:GITHUB_OUTPUT
        }
        elseif ($solutionName -eq '')
        {
            Write-Host "Skipping Github workflow as Solution name cannot be blank."
            Write-Output "solutionName=" >> $env:GITHUB_OUTPUT

            if ($instrumentationKey -ne '')
            {
                Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Executing getSolutionName : Unable to identify solution name for Job Run Id : $runId" -Severity Information -CustomProperties @{ 'RunId'="$runId"; 'PullRequestNumber'="$pullRequestNumber"; "EventName"="GetSolutionName";}
            }
        }
        else
        {
            Write-Output "solutionName=$solutionName" >> $env:GITHUB_OUTPUT
            if ($instrumentationKey -ne '')
            {
                Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Executing getSolutionName : Identified Solution Name : $solutionName for Job Run Id : $runId" -Severity Information -CustomProperties @{ 'RunId'="$runId"; 'SolutionName'="$solutionName"; 'PullRequestNumber'="$pullRequestNumber"; "EventName"="GetSolutionName";}
            }
        }
    }
    else
    {
        Write-Output "Skipping Github workflow as changes are not in Solutions folder or changes are in .md file or images folder inside of Solutions!"
        Write-Output "solutionName=" >> $env:GITHUB_OUTPUT

        if ($instrumentationKey -ne '')
        {
            Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Executing getSolutionName : Skipping as changes are not in solutions folder or changes are in .md file or images folder inside of Solutions for Job Run Id : $runId" -Severity Information -CustomProperties @{ 'RunId'="$runId"; 'PullRequestNumber'="$pullRequestNumber"; 'FilesChanged'="$filteredFiles"; "EventName"="GetSolutionName"}
        }
    }
}
catch
{
    Write-Output "solutionName=" >> $env:GITHUB_OUTPUT
    Write-Host "Skipping as exception occured: Unable to identify Solution name. Error Details: $_"

    if ($instrumentationKey -ne '')
    {
        if ($solutionName -eq '')
        {
            Send-AppInsightsExceptionTelemetry -InstrumentationKey $instrumentationKey -Exception $_.Exception -CustomProperties @{ 'RunId'="$runId"; 'PullRequestNumber'= "$pullRequestNumber"; 'ErrorDetails'="getSolutionName : Error occured in catch block: $_"; "EventName"="GetSolutionName"}
        }
        else
        {
            Send-AppInsightsExceptionTelemetry -InstrumentationKey $instrumentationKey -Exception $_.Exception -CustomProperties @{ 'RunId'="$runId"; 'SolutionName'="$solutionName"; 'PullRequestNumber'= "$pullRequestNumber"; 'ErrorDetails'="getSolutionName : Error occured in catch block: $_"; "EventName"="GetSolutionName"}
        }
    }
    exit 1
}