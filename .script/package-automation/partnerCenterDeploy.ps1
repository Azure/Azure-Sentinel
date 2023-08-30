param ($solutionName, $pullRequestNumber, $runId, $instrumentationKey, $defaultPackageVersion, $offerId, $isNewSolution, $inputBaseFolderPath)

$eventName = 'DeployToPartnerCenter'
Write-Host "Deployement to Partner Center started!"

. ./Tools/Create-Azure-Sentinel-Solution/common/LogAppInsights.ps1
. ./.script/package-automation/catelogAPI.ps1

try {
    function GetPartnerCenterPackageUploadStatus {
        Param([Parameter(Mandatory = $true, Position = 0)]
            [string] $statusUrl)   
        try {
            $uploadStatusResponse = Invoke-WebRequest -Uri $statusUrl -Method Get
            Write-Host $uploadStatusResponse
            $statusCode = $uploadStatusResponse.StatusCode
            Write-Host $statusCode
                
            if ($statusCode -eq 200) {
                #completed,
                return $true
            }
            elseif ($statusCode -eq 202) {
                #pending
                Start-Sleep -Seconds 3
                return GetPartnerCenterPackageUploadStatus($statusUrl)				
            }
            else {
                #error
                return $false
            }	
        }
        catch {
            Write-Host "Error occured while getting status for uploaded package to partner center. Error Details $_"
            return $false
        }
    }

    function IgnoreParameterFileInDataFolder { 
        Param
        (
            [Parameter(Mandatory = $true, Position = 0)] 
            [System.Array] $datafolderFiles
        )
        $newDataFolderFilesWithoutExcludedFiles = @()
        foreach ($item in $datafolderFiles) {
            $paramterFileExist = $item -match ([regex]::Escape("parameters.json"))
            $paramtersFileExist = $item -match ([regex]::Escape("parameter.json"))
            if ($paramterFileExist -or $paramtersFileExist) 
            { } 
            else { 
                $newDataFolderFilesWithoutExcludedFiles += $item 
            } 
        }
        return $newDataFolderFilesWithoutExcludedFiles;
    }

    $customProperties = @{ 'RunId' = "$runId"; 'PullRequestNumber' = "$pullRequestNumber"; 'EventName' = "$eventName"; 'IsNewSolution' = '$isNewSolution'; 'SolutionOfferId' = '$offerId'; 'SolutionName' = '$solutionName'; }
    Send-AppInsightsEventTelemetry -InstrumentationKey $instrumentationKey -EventName "$eventName" -CustomProperties $customProperties

    Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Execution for partnerCenterDeploy started for Solution Name : $solutionName, Job Run Id : $runId" -Severity Information -CustomProperties $customProperties

    $solutionFolderPath = 'Solutions/' + $solutionName + "/"
    $filesList = git ls-files | Where-Object { $_ -like "$solutionFolderPath*" }

    $dataFolderFiles = $filesList | Where-Object { $_ -like "*/Data/*" } | Where-Object { $_ -notlike '*system_generated_metadata.json' }

    if ($dataFolderFiles.Count -gt 0) {
        $selectFirstdataFolderFile = $dataFolderFiles | Select-Object -first 1
        $filteredString = $selectFirstdataFolderFile.Replace("$solutionFolderPath", '')
        $nextSlashIndex = $filteredString.IndexOf('/')
        $dataFolderActualName = $filteredString.Substring(0, $nextSlashIndex)
        $replaceInitialPath = "$solutionFolderPath" + "$dataFolderActualName/"
        $dataFolderFiles = $dataFolderFiles.Replace("$replaceInitialPath", '')
    }
    else {
        Write-Host "Data Folder not present!"
        ErrorOutput
    }

    $dataFolderFile = IgnoreParameterFileInDataFolder($dataFolderFiles)
    $solutionDataFolder = $solutionFolderPath + "$dataFolderActualName/"
    Write-Host "solutionDataFolder is $solutionDataFolder"

    $baseFolderPath = $inputBaseFolderPath
    $dataFilePath = $baseFolderPath + $solutionDataFolder + $dataFolderFile

    $dataFileContentObject = Get-Content "$dataFilePath" | ConvertFrom-Json
    $dataFileContentObject = $null -eq $dataFileContentObject[0] ? $dataFileContentObject[1] : $dataFileContentObject[0]

    $hasCreatePackageAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match ([regex]::Escape("createPackage")))
    $isCreatePackageSetToTrue = $dataFileContentObject.createPackage
    if ($hasCreatePackageAttribute -eq $true -and $isCreatePackageSetToTrue -eq $false) {
        Write-Host "::warning::Skipping Partner Center deploy for Solution '$solutionName', as Data File '$dataFolderFile' either doesn't have attribute 'createPackage' and/or not set to 'true'"
        exit 0
    }

    $packageVersionAttribute = [bool]($dataFileContentObject.PSobject.Properties.Name -match "Version")
    $userInputPackageVersion = ''
    if ($packageVersionAttribute) {
        $userInputPackageVersion = $dataFileContentObject.version
    }

    $updateSolution = $isNewSolution -eq "true" -or $isNewSolution -eq "True" ? "New" : "Update"

    $offerDetails = GetCatelogDetails $offerId

    $packageVersion = GetPackageVersion $defaultPackageVersion $offerId $offerDetails $packageVersionAttribute $userInputPackageVersion
    Write-Host "Package version identified is $packageVersion"

    $blobFolderName = $solutionName + "_" + $pullRequestNumber + "_" + $packageVersion + "/" + $packageVersion + ".zip" 

    Write-Host "SolutionName : $solutionName, pullRequestNumber : $pullRequestNumber , IsNewSolution: $isNewSolution, defaultPackageVersion : $defaultPackageVersion, offerId : $offerId, Blob Name : $blobFolderName"

    $headers = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
    $headers.Add("Content-Type", "application/json")
    $body = "{
        `n    `"OfferId`" : `"$offerId`",
        `n    `"SolutionType`" : `"$updateSolution`",
        `n    `"SolutionName`" : `"$solutionName`",
        `n    `"FileName`" : `"$blobFolderName`",
        `n    `"FileVersion`" : `"$packageVersion`"
    `n}"

    $response = Invoke-RestMethod 'https://catpartnercenter.azurewebsites.net/api/HttpStart' -Method 'POST' -Headers $headers -Body $body
    if ($null -ne $response) {
        $uploadStatusUrl = $response.statusQueryGetUri
        Write-Host "$uploadStatusUrl"

        $isPackageUploaded = GetPartnerCenterPackageUploadStatus($uploadStatusUrl)
        Write-Host "isPackageUploaded $isPackageUploaded"
        if ($isPackageUploaded -eq $false) {
            Write-Host "Package upload to Partner Center failed!!"
            Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Publishing of artifacts to Partner Center failed for solutionName $solutionName for Job Run Id : $runId" -Severity Information -CustomProperties @{ 'RunId' = "$runId"; 'PullRequestNumber' = "$pullRequestNumber"; 'EventName' = "$eventName"; 'IsNewSolution' = '$isNewSolution'; 'SolutionOfferId' = '$offerId'; 'SolutionName' = '$solutionName'; 'FunctionAppResponse' = '$response'; }
            Write-Output "IsPartnerCenterDeploymentSuccess=$false" >> $env:GITHUB_OUTPUT
            exit 1
        }
        else {
            Write-Host "Package upload to Partner Center Succeeded!!"
            Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "Publishing of artifacts to Partner Center Succeeded for solutionName $solutionName for Job Run Id : $runId" -Severity Information -CustomProperties @{ 'RunId' = "$runId"; 'PullRequestNumber' = "$pullRequestNumber"; 'EventName' = "$eventName"; 'IsNewSolution' = '$isNewSolution'; 'SolutionOfferId' = '$offerId'; 'SolutionName' = '$solutionName'; 'FunctionAppResponse' = '$response'; }
            Write-Output "IsPartnerCenterDeploymentSuccess=$true" >> $env:GITHUB_OUTPUT
            exit 0
        }
    }
    else {
        Write-Host "No API response. Package upload to Partner Center failed!!"
        Send-AppInsightsTraceTelemetry -InstrumentationKey $instrumentationKey -Message "No API response. Package upload to Partner Center failed for solutionName $solutionName for Job Run Id : $runId" -Severity Information -CustomProperties $customProperties
        Write-Output "IsPartnerCenterDeploymentSuccess=$false" >> $env:GITHUB_OUTPUT
        exit 1
    }
}
catch {
    Write-Host "Error occured in catch block. Error Details : $_"
    Send-AppInsightsExceptionTelemetry -InstrumentationKey $instrumentationKey -Exception $_.Exception -CustomProperties @{ 'RunId' = "$runId"; 'SolutionName' = "$solutionName"; 'PullRequestNumber' = "$pullRequestNumber"; 'ErrorDetails' = "PartnerCenterDeploy file : Error occured in catch block: $_"; 'EventName' = "$eventName"; 'SolutionOfferId' = "$offerId"; }
    Write-Output "IsPartnerCenterDeploymentSuccess=$false" >> $env:GITHUB_OUTPUT
    exit 1
}