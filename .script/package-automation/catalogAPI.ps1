function GetCatalogDetails($offerId) 
{
    if ($null -eq $offerId -or $offerId -eq '')
    {
        Write-Host "Provided OfferId for CatalogAPI details is blank! Please provide valid OfferId!";
        return $null;
    }
    else {
        try {
            $formatUri = 'https://catalogapi.azure.com/offers?api-version=2018-08-01-beta&$filter=(categoryIds/any(cat:+cat+eq+''AzureSentinelSolution'')+or+keywords/any(key:+contains(key,''f1de974b-f438-4719-b423-8bf704ba2aef'')))+and+(offerId+eq+%27'+ $offerId +'%27)'
            $response = Invoke-RestMethod -Uri $formatUri -Method 'GET' -Headers $headers -Body $body
            
            $offerDetails = $response.items | Where-Object offerId -eq $offerId

            if ($null -eq $offerDetails)
            {
                # when not found by offerId then use planId
                $offerDetails = $response.items | Where-Object planId -eq $offerId
            }

            if ($null -eq $offerDetails)
            {
                # DETAILS NOT FOUND
                Write-Host "CatalogAPI Details not found for offerId $offerId"
                return $null;
            }
            else {
                Write-Host "CatalogAPI Details found for offerId $offerId"
                return $offerDetails;
            }
        }
        catch {
            Write-Host "Error occured in CatalogAPI. Error Details : $_";
            return $null;
        }
    }
}

function CompareVersionStrings([string]$Version1, [string]$Version2) {

    $v1 = $Version1.Split('.') -replace '^0', '0.'
    $v2 = $Version2.Split('.') -replace '^0', '0.'   

    [Array]::Resize( [ref] $v1, 4 )
    [Array]::Resize( [ref] $v2, 4 )

    for ($i=0; $i-lt 4; $i++) {      
        switch (($v1[$i].length).CompareTo(($v2[$i].length))) {
            {$_ -lt 0} { $v1[$i] = $v1[$i].PadRight($v2[$i].Length,'0') }
            {$_ -gt 0} { $v2[$i] = $v2[$i].PadRight($v1[$i].Length,'0') }
        }
    }
    
    $v1f = $v1 | % {[float]$_}
    $v2f = $v2 | % {[float]$_}

    return [Collections.StructuralComparisons]::StructuralComparer.Compare( $v1f, $v2f )  
}

function GetNewVersion($packageVersionAttribute, $dataFileContentObject, $defaultPackageVersion, $templateSpecAttribute, $isNewSolution)
{
    $templateSpecDefaultVersion = '2.0.0'
    if($packageVersionAttribute)
    {
        if ($null -eq $dataFileContentObject.Version -or $dataFileContentObject.Version -eq '')
        {
            return $templateSpecAttribute ? ($templateSpecDefaultVersion, $true) : ($defaultPackageVersion, $true)
        }
        else 
        {
            return ($dataFileContentObject.Version, $false)
        }
    }
    else 
    {
        return $templateSpecAttribute ? ($templateSpecDefaultVersion, $true) : ($defaultPackageVersion, $true)
    }
}

function GetIncrementedVersion($version)
{
    $major,$minor,$build,$revision = $version.split(".")
    $newBuildVersion = [int]$build +  1
    return "$major.$minor.$newBuildVersion"
}

function GetOfferVersion($offerId, $mainTemplateUrl) 
{
    if ($null -eq $mainTemplateUrl -or $mainTemplateUrl -eq '')
    {
        Write-Host "Provided MainTemplateUrl for GetOfferVersion details is blank! Please provide valid MainTemplateUrl!";
        return $null;
    }
    else 
    {
        try 
        {
            $response = Invoke-RestMethod -Uri $mainTemplateUrl -Method 'GET' -Headers $headers
            $metadataDetails = $response.resources | Where-Object { ($_.name -eq "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/', variables('_solutionId'))]" -or $_.name -eq "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/', variables('_sourceId'))]") -and ($_.type -eq "Microsoft.OperationalInsights/workspaces/providers/metadata")};

            if ($null -eq $metadataDetails)
            {
                $metadataDetails = $response.resources | Where-Object { ($_.name -eq "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/', variables('_solutionId'))]" -or $_.name -eq "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/', variables('_sourceId'))]") -and ($_.type -eq "Microsoft.OperationalInsights/workspaces/providers/contentPackages")};
            }
            if ($null -eq $metadataDetails -or $metadataDetails -eq '')
            {
                Write-Host "Offer Metadata Version details in MainTemplate is not found!"
                return $null;
            }
            else 
            {
                Write-Host "Offer Metadata Version details in MainTemplate is found!"
                return $metadataDetails.properties.version;
            }
        }
        catch 
        {
            Write-Host "Error occured in CatalogAPI. Error Details11 : $_";
            return $null;
        }
    }
}

function GetPackageVersion($defaultPackageVersion, $offerId, $offerDetails, $packageVersionAttribute, $userInputPackageVersion)
{
    if ($packageVersionAttribute)
    {
        $userInputMajor,$userInputMinor,$userInputBuild,$userInputRevision = $userInputPackageVersion.split(".")
        $defaultMajor,$defaultMinor,$defaultBuild,$defaultRevision = $defaultPackageVersion.split(".")

        if ($userInputMajor -ge '2' -and $userInputMinor -gt $defaultMinor)
        {
            #return as is value of package version as middle value is greater
            return $userInputPackageVersion 
        }
    }

    $defaultVersionMessage = "Package Version set to Default version $defaultPackageVersion"
    if ($null -eq $offerDetails)
    {
        Write-Host "CatalogAPI Offer details not found for given offerId $offerId. $defaultVersionMessage"
        return $defaultPackageVersion
    }
    else 
    {
        $mainTemplateDetails = $offerDetails.plans.artifacts | Where-Object {$_.type -eq "Template" -and $_.name -eq "DefaultTemplate"}

        if ($null -eq $mainTemplateDetails)
        {
            # WE WILL TAKE WHATEVER VERSION IS SPECIFIED IN THE DATA INPUT FILE WITHOUT INCREMENTING IT
            Write-Host "CatalogAPI mainTemplate details not found for given offerId $offerId. $defaultVersionMessage"
            return $defaultPackageVersion
        }
        else
        {
            # CHECK IF CATALOG API HAS DETAILS AND IDENTIFY THE VERSION
            $mainTemplateUri = $mainTemplateDetails.uri

            if ($null -eq $mainTemplateUri)
            {
                Write-Host "CatalogAPI mainTemplate details missing URI for given offerId $offerId. $defaultVersionMessage"
                return $defaultPackageVersion
            }
            else 
            {
                # OFFER DETAILS FOUND SO IDENTIFY THE VERSION IN MAINTEMPLATE FILE
                $offerMetadataVersion = GetOfferVersion $offerId $mainTemplateUri
                if ($null -eq $offerMetadataVersion -or $offerMetadataVersion -eq '')
                {
                    Write-Host "CatalogAPI mainTemplate details URI file is missing version or version is blank so $defaultVersionMessage"
                    return $defaultPackageVersion
                }
                else 
                {
                    $identifiedOfferVersion = $offerMetadataVersion
                    $catalogMajor,$catalogminor,$catalogbuild,$catalogrevision = $identifiedOfferVersion.split(".")
                    $defaultMajor,$defaultminor,$defaultbuild,$defaultrevision = $defaultPackageVersion.split(".")

                    if ($defaultMajor -gt $catalogMajor)
                    {
                        # eg: 3.0.0 > 2.0.1 ==> 3.0.0
                        Write-Host "Default Package version is greater then the CatalogAPI version so $defaultVersionMessage"
                        return $defaultPackageVersion
                    }
                    else 
                    {
                        $packageVersion = GetIncrementedVersion $identifiedOfferVersion
                        return $packageVersion
                    }
                }
            }
        }
    }
}
