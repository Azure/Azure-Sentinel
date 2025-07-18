param($runId, $pullRequestNumber, $instrumentationKey, $isPRMerged = $false)
. ./Tools/Create-Azure-Sentinel-Solution/common/LogAppInsights.ps1

$solutionName = ''
try 
{
    #$diff = git diff --diff-filter=d --name-only HEAD^ HEAD
    if ($isPRMerged) {
        $masterMergeCommitId = git log --format="%H" --merges --grep="Merge pull request #$pullRequestNumber" master
        if ($null -ne $masterMergeCommitId) {
            Write-Host "masterMergeCommitId $masterMergeCommitId"
            $diff = git diff --diff-filter=d --name-only $masterMergeCommitId^ $masterMergeCommitId
        } else {
            Write-Host "PR not merged into master!"
            exit 0;
        }
    } else {
        $masterMergeCommit = git show -s --format='%s' -1
        Write-Host "masterMergeCommit $masterMergeCommit"
        if ($masterMergeCommit -like "*Merge branch*") {
            Write-Host "Skipping as Master merge commit!"
            Write-Output "solutionName=" >> $env:GITHUB_OUTPUT
            exit 0
        } else {
            $diff = git diff --diff-filter=d --name-only --first-parent HEAD^ HEAD
        }
    }

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
        }
        else
        {
            Write-Output "solutionName=$solutionName" >> $env:GITHUB_OUTPUT
        }
    }
    else
    {
        Write-Output "Skipping Github workflow as changes are not in Solutions folder or changes are in .md file or images folder inside of Solutions!"
        Write-Output "solutionName=" >> $env:GITHUB_OUTPUT
    }
}
catch
{
    Write-Output "solutionName=" >> $env:GITHUB_OUTPUT
    Write-Host "Skipping as exception occured: Unable to identify Solution name. Error Details: $($_ | Out-String)"

    exit 1
}