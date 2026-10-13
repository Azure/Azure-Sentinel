
try {
    $diff = @()
    if (!$env:PR_BASE_SHA -or !$env:PR_HEAD_SHA) {
        Write-Warning "PR_BASE_SHA or PR_HEAD_SHA is missing. Treating this as no changes and skipping ARM-TTK."
    }
    else {
        try {
            $diff = git diff --diff-filter=d --name-only "$($env:PR_BASE_SHA)...$($env:PR_HEAD_SHA)"
            if ($LASTEXITCODE -ne 0) {
                throw "Git comparison failed (exit code $LASTEXITCODE)."
            }
        }
        catch {
            Write-Warning "Unable to identify PR changes: $_ Treating this as no changes and skipping ARM-TTK."
            $diff = @()
        }
    }
    Write-Host "List of files in PR: $diff"

    $filteredFiles = $diff | Where-Object {
        $_ -match '^Solutions/[^/]+/Package/(mainTemplate|createUiDefinition)\.json$'
    }
    Write-Host "Filtered Files $filteredFiles"

    $solutions = @{}
    foreach ($file in $filteredFiles) {
        if ($file -match '^Solutions/([^/]+)/Package/(mainTemplate|createUiDefinition)\.json$') {
            $solutionName = $matches[1]
            $templateName = $matches[2]

            if (!$solutions.ContainsKey($solutionName)) {
                $solutions[$solutionName] = [ordered]@{
                    solutionName = $solutionName
                    mainTemplateChanged = $false
                    createUiChanged = $false
                }
            }

            if ($templateName -eq 'mainTemplate') {
                $solutions[$solutionName].mainTemplateChanged = $true
            }
            else {
                $solutions[$solutionName].createUiChanged = $true
            }
        }
    }

    $solutionsJson = ConvertTo-Json -InputObject @($solutions.Values) -Compress
    if (!$solutionsJson) {
        $solutionsJson = '[]'
    }

    Write-Host "Solutions to validate: $solutionsJson"
    Write-Output "solutionsJson=$solutionsJson" >> $env:GITHUB_OUTPUT
}
catch {
    throw
}