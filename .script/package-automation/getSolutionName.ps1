param($instrumentationKey, $runId, $pullRequestNumber)

. ./Tools/Create-Azure-Sentinel-Solution/V2/LogAppInsights.ps1

$solutionName = ''

try 
{
    Send-AppInsightsEventTelemetry -InstrumentationKey $instrumentationKey -EventName "GetSolutionName" -CustomProperties @{ 'RunId'="$runId"; 'PullRequestNumber'= "$pullRequestNumber"; "EventName"="GetSolutionName"; }

    Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Execution for getSolutionName started, Job Run Id : $runId" -Severity Information -CustomProperties @{ 'RunId'="$runId"; 'PullRequestNumber'= "$pullRequestNumber"; "EventName"="GetSolutionName"; }

    $diff = git diff --diff-filter=d --name-only HEAD^ HEAD
    Write-Host "List of files in PR: $diff"

    $filteredFiles = $diff | Where-Object {$_ -match "Solutions/"}
    Write-Host "Filtered Files $filteredFiles"

    if ($filteredFiles.Count -gt 0)
    {
        Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Executing getSolutionName and inside of Filtered Files, Job Run Id : $runId" -Severity Information -CustomProperties @{ 'RunId'="$runId"; 'PullRequestNumber'="$pullRequestNumber"; 'FilesChanged'="$filteredFiles"; "EventName"="GetSolutionName";}

        foreach ($currentFile in $filteredFiles)
        {
            $solutionIndex = $currentFile.IndexOf("Solutions/")
            if ($solutionName -eq '' -and $solutionIndex -eq 0)
            {					
                $solutionNameWithSubstring = $currentFile.SubString($solutionIndex + 10)
                $firstForwardSlashIndex = $solutionNameWithSubstring.IndexOf("/")
                $solutionName = $solutionNameWithSubstring.SubString(0, $firstForwardSlashIndex)
                Write-Host "Solution Name is $solutionName"
            }
            else
            {
                break;
            }
        }

        if ($solutionName -eq '')
        {
            Write-Host "Skipping Github workflow as Solution name cannot be blank."
            Write-Output "solutionName=''" >> $env:GITHUB_OUTPUT
            Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Executing getSolutionName : Unable to identify solution name for Job Run Id : $runId" -Severity Information -CustomProperties @{ 'RunId'="$runId"; 'PullRequestNumber'="$pullRequestNumber"; "EventName"="GetSolutionName";}
        }
        else
        {
            Write-Output "solutionName=$solutionName" >> $env:GITHUB_OUTPUT
            Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Executing getSolutionName : Identified Solution Name : $solutionName for Job Run Id : $runId" -Severity Information -CustomProperties @{ 'RunId'="$runId"; 'SolutionName'="$solutionName"; 'PullRequestNumber'="$pullRequestNumber"; "EventName"="GetSolutionName";}
        }
    }
    else
    {
        Write-Output "Skipping Github workflow as changes are not in Solutions folder."
        Write-Output "solutionName=$solutionName" >> $env:GITHUB_OUTPUT
        Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Executing getSolutionName : Skipping as changes are not in solutions folder for Job Run Id : $runId" -Severity Information -CustomProperties @{ 'RunId'="$runId"; 'PullRequestNumber'="$pullRequestNumber"; 'FilesChanged'="$filteredFiles"; "EventName"="GetSolutionName"}
    }
}
catch
{
    Write-Output "solutionName=$solutionName" >> $env:GITHUB_OUTPUT
    Write-Host "Skipping as exception occured: Unable to identify Solution name. Error Details: $_"
    if ($solutionName -eq '')
    {
        Send-AppInsightsExceptionTelemetry -InstrumentationKey $instrumentationKey -Exception $_.Exception -CustomProperties @{ 'RunId'="$runId"; 'PullRequestNumber'= "$pullRequestNumber"; 'ErrorDetails'="getSolutionName : Error occured in catch block: $_"; "EventName"="GetSolutionName"}
    }
    else
    {
        Send-AppInsightsExceptionTelemetry -InstrumentationKey $instrumentationKey -Exception $_.Exception -CustomProperties @{ 'RunId'="$runId"; 'SolutionName'="$solutionName"; 'PullRequestNumber'= "$pullRequestNumber"; 'ErrorDetails'="getSolutionName : Error occured in catch block: $_"; "EventName"="GetSolutionName"}
    }
    exit 1
}