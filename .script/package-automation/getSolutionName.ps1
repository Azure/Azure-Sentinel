param($runId, $pullRequestNumber)

$solutionName = ''
try 
{
    $diff = git diff --diff-filter=d --name-only HEAD^ HEAD
    Write-Host "List of files in PR: $diff"

    $filteredFiles = $diff | Where-Object {$_ -match "Solutions/"}
    Write-Host "Filtered Files $filteredFiles"

    if ($filteredFiles.Count -gt 0)
    {
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
        }
        else
        {
            Write-Output "solutionName=$solutionName" >> $env:GITHUB_OUTPUT
        }
    }
    else
    {
        Write-Output "Skipping Github workflow as changes are not in Solutions folder."
        Write-Output "solutionName=$solutionName" >> $env:GITHUB_OUTPUT
    }
}
catch
{
    Write-Output "solutionName=$solutionName" >> $env:GITHUB_OUTPUT
    Write-Host "Skipping as exception occured: Unable to identify Solution name. Error Details: $_"
    exit 1
}