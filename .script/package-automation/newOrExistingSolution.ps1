param ($solutionName, $pullRequestNumber, $runId, $baseFolderPath, $instrumentationKey, $isPRMerged = $false)

. ./Tools/Create-Azure-Sentinel-Solution/common/LogAppInsights.ps1

$isNewSolution = $true
$solutionSupportedBy = ''

if ($null -eq $solutionName -or $solutionName -eq '') {
    Write-Host "Skipping NewOrExistingSolution : Solution Name cannot be blank."
}
else {
    try {
        function IgnoreParameterFileInDataFolder { 
            Param
            (
                [Parameter(Mandatory = $true, Position = 0)] 
                [System.Array] $datafolderFiles
            )
            $newDataFolderFilesWithoutExcludedFiles = @()
            foreach ($item in $datafolderFiles) {
                $paramterFileExist = $item -match "parameters.json"
                $paramtersFileExist = $item -match "parameter.json"
                if ($paramterFileExist -or $paramtersFileExist) 
                { } 
                else { 
                    $newDataFolderFilesWithoutExcludedFiles += $item 
                } 
            }
            return $newDataFolderFilesWithoutExcludedFiles;
        }

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
                Write-Output "isNewSolution=$isNewSolution" >> $env:GITHUB_OUTPUT
                Write-Output "solutionSupportedBy=" >> $env:GITHUB_OUTPUT
                Write-Output "solutionOfferId=" >> $env:GITHUB_OUTPUT
                Write-Output "solutionPublisherId=" >> $env:GITHUB_OUTPUT
                exit 0
            } else {
                $diff = git diff --diff-filter=d --name-only --first-parent HEAD^ HEAD
            }
        }
        Write-Host "List of files in PR: $diff"

        $filteredFiles = $diff | Where-Object {$_ -match "Solutions/"} | Where-Object {$_ -notlike "Solutions/Images/*"} | Where-Object {$_ -notlike "Solutions/*.md"} | Where-Object { $_ -notlike '*system_generated_metadata.json' } | Where-Object { $_ -notlike '*testParameters.json' }
        Write-Host "Filtered Files $filteredFiles"

        if ($filteredFiles.Count -le 0)
        {
            Write-Host 'Skipping as changes not in Solutions folder!'
            Write-Output "isNewSolution=$isNewSolution" >> $env:GITHUB_OUTPUT
            Write-Output "solutionSupportedBy=" >> $env:GITHUB_OUTPUT
            Write-Output "solutionOfferId=" >> $env:GITHUB_OUTPUT
            Write-Output "solutionPublisherId=" >> $env:GITHUB_OUTPUT
        }
        else 
        {
            $offerId = ''
            $publisherId = ''
            $solutionFolderPath = 'Solutions/' + $solutionName
            $filesList = git ls-files | Where-Object { $_ -like "Solutions/$solutionName/*" } | Where-Object {$_ -notlike "Solutions/Images/*"} | Where-Object {$_ -notlike "Solutions/*.md"} | Where-Object { $_ -notlike '*system_generated_metadata.json' } | Where-Object { $_ -notlike '*testParameters.json' }

            Write-Host "List of files changed $filesList"
            try {
                $solutionMetadataFilePresent = $filesList -match ([regex]::Escape("SolutionMetadata.json"))
            }
            catch {
                Write-Host "SolutionMetadata file not present so check if any file is present that contains SolutionMetadata file in the Solutions respective folder!"
                $solutionMetadataFilePresent = filesList | Where-Object { $_ -like "Solutions/*SolutionMetadata.json" }
            }
            if ($solutionMetadataFilePresent.Count -le 0) {
                # SOLUTIONMETADATA FILE NOT FOUND SO WE FIND OUR DATA IN DATA INPUT FILE
                Write-Host "::warning::SolutionMetadata.json file not found."
                $solutionDataFolder = "Solutions/" + $solutionName + '/Data/'
                $dataFolderFiles = $filesList -match $solutionDataFolder | ForEach-Object { $_ -replace $solutionDataFolder, '' }

                if ($dataFolderFiles.length -eq 0) {
                    # WE DIDNT FIND FILE FOLDER "Data" inside of solution so find it by "data"
                    $solutionDataFolder = "Solutions/" + $solutionFolderPath + '/data/'
                    $dataFolderFiles = $filesList -match $solutionDataFolder | ForEach-Object { $_ -replace $solutionDataFolder, '' }
                }

                $dataFolderFile = IgnoreParameterFileInDataFolder($dataFolderFiles)
                $dataFilePath = $baseFolderPath + $solutionDataFolder + $dataFolderFile
                $dataFileContentObject = Get-Content "$dataFilePath" | ConvertFrom-Json

                if ($null -ne $dataFileContentObject) {
                    $offerId = $dataFileContentObject.offerId
                    $publisherId = $dataFileContentObject.publisherId
                }
            }
            else {
                $solutionMetadataFilePresent = $solutionMetadataFilePresent.replace($solutionFolderPath, "")
                $solutionMetadataFilePath = $baseFolderPath + $solutionFolderPath + "$solutionMetadataFilePresent"
                $solutionMetadataFileContentObject = Get-Content $solutionMetadataFilePath | ConvertFrom-Json
                $jsonSolutionMetadataContent = $solutionMetadataFileContentObject | ConvertTo-Json
                Write-Host "jsonSolutionMetadataContent $jsonSolutionMetadataContent"
                $offerId = $solutionMetadataFileContentObject.offerId
                $publisherId = $solutionMetadataFileContentObject.publisherId
                Write-Host "offerId is $offerId, publisherId is $publisherId";
            }

            if ($offerId -eq '') {
                Write-Host "OfferId found is empty!"
            }
            else {
                . ./.script/package-automation/catalogAPI.ps1
                $offerDetails = GetCatalogDetails $offerId

                if ($null -eq $offerDetails) {
                    Write-Host "OfferDetails not found for provided offerId $offerDetails"
                    $solutionSupportedBy = 'partner-supported-solution'
                }
                else {
                    $isNewSolution = $false
                    # CHECK IF MICROSOFT OR PARTNER SUPPORTED. WHEN NULL WE WILL NOT ADD ANY LABEL
                    $isMicrosoftSupported = $offerDetails.supportUri.Contains('https://support.microsoft.com/')
                    if ($isMicrosoftSupported) {
                        $solutionSupportedBy = 'microsoft-supported-solution'
                    }
                    else {
                        $solutionSupportedBy = 'partner-supported-solution'
                    }
                }
            }

            Write-Host "isNewSolution : $isNewSolution, solutionSupportedBy : $solutionSupportedBy, offerId : $offerId, publisherId : $publisherId"          
            Write-Output "isNewSolution=$isNewSolution" >> $env:GITHUB_OUTPUT
            Write-Output "solutionSupportedBy=$solutionSupportedBy" >> $env:GITHUB_OUTPUT
            Write-Output "solutionOfferId=$offerId" >> $env:GITHUB_OUTPUT
            Write-Output "solutionPublisherId=$publisherId" >> $env:GITHUB_OUTPUT
        }
    }
    catch {
        Write-Host "isNewSolution : $isNewSolution, solutionSupportedBy is ''"
        Write-Host "Error occured in catch NewOrExistingSolution : Error details $_"
        Write-Output "isNewSolution=$isNewSolution" >> $env:GITHUB_OUTPUT
        Write-Output "solutionSupportedBy=" >> $env:GITHUB_OUTPUT
        Write-Output "solutionOfferId=" >> $env:GITHUB_OUTPUT
        Write-Output "solutionPublisherId=" >> $env:GITHUB_OUTPUT

        exit 1
    }
}