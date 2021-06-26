# Input bindings are passed in via param block.
param($Timer)

# Get the current universal time in the default string format
$currentUTCtime = (Get-Date).ToUniversalTime()

# The 'IsPastDue' porperty is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

#Functions
#Try to get the Watchlist
function Check-Watchlist {
    # Parameter help description
    param(
        [Parameter(Mandatory)]
        [string]$watchlistAlias,
        [string]$resourceURI = $resourceURI,
        [string]$subscriptionId = $subscriptionId,
        [string]$resourceGroupName = $resourceGroupName,
        [string]$workspaceName = $workspaceName
        
    )
    $Uri = $resourceURI + "/subscriptions/" + $subscriptionId + "/resourceGroups/" + $resourceGroupName + "/providers/Microsoft.OperationalInsights/workspaces/" + $workspaceName + "/providers/Microsoft.SecurityInsights/watchlists/" + $watchlistAlias + "?api-version=2021-03-01-preview"
    $new = $false
    try {
        $IPWatchlist = Invoke-RestMethod -Method GET -Headers $requestHeaders -Uri $Uri
    }
    catch {
        $new = $true
    }
    return $new
}

# Get Azure IP Ranges
function Get-AzureIPRanges {
    param(
        [string]$resourceURI = $resourceURI,
        [string]$subscriptionId = $subscriptionId
    )
    $Uri = $resourceURI + "/subscriptions/" + $subscriptionId + "/providers/Microsoft.Network/locations/centralus/serviceTags?api-version=2020-11-01"
    $AzureIPRanges = Invoke-RestMethod -Method Get -Headers $requestHeaders -Uri $Uri
    #add nextlink logic
    return ($AzureIPRanges.values)
}

#Get AWS IP Ranges
function Get-AWSIPRanges {
    $Uri = "https://ip-ranges.amazonaws.com/ip-ranges.json"
    $AWSIPRanges = (Invoke-WebRequest $Uri ).Content | ConvertFrom-Json
    return ($AWSIPRanges.prefixes)
}

#Get GCP IP Ranges
function Get-GCPIPRanges {
    $Uri = "https://www.gstatic.com/ipranges/cloud.json"
    $GCPIPRanges = (Invoke-WebRequest $uri).Content | ConvertFrom-Json
    return ($GCPIPRanges.prefixes)
}

# Watchlist table
function Get-WatchlistItemTable {
    # Parameter help description
    param(
        [Parameter(Mandatory)]
        [string]$watchlistAlias,
        [string]$resourceURI = $resourceURI,
        [string]$subscriptionId = $subscriptionId,
        [string]$resourceGroupName = $resourceGroupName,
        [string]$workspaceName = $workspaceName
        
    )
    $nextLink = $true
    $Uri = $resourceURI + "/subscriptions/" + $subscriptionId + "/resourceGroups/" + $resourceGroupName + "/providers/Microsoft.OperationalInsights/workspaces/" + $workspaceName + "/providers/Microsoft.SecurityInsights/watchlists/" + $watchlistAlias + "/watchlistItems?api-version=2021-03-01-preview"
    $WatchListItems = Invoke-RestMethod -Method Get -Headers $requestHeaders -Uri $Uri
    $WatchListItemsCollection = $WatchListItems.value
    $a = 0
    do {
        if (($WatchListItems.nextLink) -eq $null) {
            $nextLink = $false
        }
        else {
            $Uri = $WatchListItems.nextLink
            $WatchListItems = Invoke-RestMethod -Method Get -Headers $requestHeaders -Uri $Uri
            $WatchListItemsCollection += $WatchListItems.value
        }
        $a++
        write-host $a
    } until ($nextLink -eq $false)

    #Build Table from all the results
    $WatchListItemsTable = @()
    foreach ($item in $WatchListItemsCollection) {
        $WatchListItemsTableObject = New-Object psobject
        $WatchListItemsTableObject | Add-Member -MemberType NoteProperty -Name "IPRange" -Value ($item.properties.itemsKeyValue.IpRange)
        $WatchListItemsTableObject | Add-Member -MemberType NoteProperty -Name "Notes" -Value ($item.properties.itemsKeyValue.Notes)
        $WatchListItemsTableObject | Add-Member -MemberType NoteProperty -Name "Expiration" -Value ($item.properties.itemsKeyValue.Expiration)
        $WatchListItemsTableObject | Add-Member -MemberType NoteProperty -Name "ItemId" -Value ($item.Name)
        $WatchListItemsTable += $WatchListItemsTableObject
    }

    return $WatchListItemsTable
}

#Prepare Variables
$AzureWebJobsStorage = $env:AzureWebJobsStorage
$subscriptionId = $env:SubscriptionId
$resourceGroupName = $env:ResourceGroupName
$workspaceName = $env:workspaceName
$watchlistAlias = $env:watchlistAlias
$resourceURI = "https://management.azure.com"
$tokenAuthURI = $env:IDENTITY_ENDPOINT + "?resource=$resourceURI&api-version=2019-08-01"
$tokenResponse = Invoke-RestMethod -Method Get -Headers @{"X-IDENTITY-HEADER"="$env:IDENTITY_HEADER"} -Uri $tokenAuthURI
$accessToken = $tokenResponse.access_token

$AzureWebJobsStorage = "DefaultEndpointsProtocol=https;AccountName=aaduserinfotest;AccountKey=mXz7E6ogZ3XqWTxuYxGovDxWIJpOdPsxlF5VRTYHUj2VY/0Os729oZ9eSp+0lmdpj5pBMoUA6IsB2k04vqiR8A==;EndpointSuffix=core.windows.net"
$subscriptionId = "1c61ccbf-70b3-45a3-a1fb-848ce46d70a6"
$resourceGroupName = "cxe-yanivsh"
$workspaceName = "Yanivsh-Sentinel"
$accessToken = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6Im5PbzNaRHJPRFhFSzFqS1doWHNsSFJfS1hFZyIsImtpZCI6Im5PbzNaRHJPRFhFSzFqS1doWHNsSFJfS1hFZyJ9.eyJhdWQiOiJodHRwczovL21hbmFnZW1lbnQuYXp1cmUuY29tIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNWYxMDYwZjItZDlhNC00ZjU5LWJmOWMtMWRkOGYzNjA0YTRiLyIsImlhdCI6MTYyNDQ2OTI0OSwibmJmIjoxNjI0NDY5MjQ5LCJleHAiOjE2MjQ0NzMxNDksImFpbyI6IkUyWmdZSWhNOTJMcmVENTFTcEdZN0RZbTMzV3JBQT09IiwiYXBwaWQiOiIwY2RjMTUxMy05ZGVjLTRhODItYmZlZS1kNWMyMzJmZGM3MDgiLCJhcHBpZGFjciI6IjEiLCJpZHAiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC81ZjEwNjBmMi1kOWE0LTRmNTktYmY5Yy0xZGQ4ZjM2MDRhNGIvIiwib2lkIjoiMTRjOTNjZjMtZTVlMy00NWNmLThiNGUtMWE2ZjYyYmRmMjAyIiwicmgiOiIwLkFXNEE4bUFRWDZUWldVLV9uQjNZODJCS1N4TVYzQXpzbllKS3YtN1Z3akw5eHdodUFBQS4iLCJzdWIiOiIxNGM5M2NmMy1lNWUzLTQ1Y2YtOGI0ZS0xYTZmNjJiZGYyMDIiLCJ0aWQiOiI1ZjEwNjBmMi1kOWE0LTRmNTktYmY5Yy0xZGQ4ZjM2MDRhNGIiLCJ1dGkiOiJUazRCc1c3RWVVQ2VBcjY1aU1rc0FBIiwidmVyIjoiMS4wIiwieG1zX3RjZHQiOjE1OTY3MzcyMTh9.XrlKNiI-imQHF5pG2D0_ccFg6P4KWKhKMX_zzxfKTEckKit6mhVnFoJC8u_HeIy-VQ7I5qcbwN2bjH-LwBjyGFlOA8jUnFY7MfIsurwSvRHyQdTuNK2fBm31_f7r8oZV0ptss0e1YU23lnlwPXqRsBG_tQj2rgXFk712E-sjIs0KZ8SvT1_r2yH2UPwOxV8B_eQ7L37iE9fClej6ng8ifZWgjpZMQC5ofoAhnwg6fAlzHS_XLre48ET9KBN39KcTWeFsXKoH7yqnwBfm51hfOYFd124PfSVvH7G8IVj5_Aetr7px4VmLiXxE8uEGw0Egsj4RV5OnidLsx6fMit_1TQ"

$requestHeaders = @{
    "Authorization" = "Bearer $accessToken"
    "Content-Type" = "application/json"
}

$Date = (Get-Date).AddDays(7) | Get-Date -Format yyyy-MM-ddTHH:mm:ssZ -asUTC

# Main
if ($env:AWS -eq "Yes") {
    Write-Host "AWS is enabled, processing..."
    $watchlistAlias = "AWSIPRanges"
    $new = Check-Watchlist -watchlistAlias $watchlistAlias
    if ($new -eq $true) {
        Write-Host "No existing AWS IP watchlist found, building it"
        $AWSIPRanges = Get-AWSIPRanges
        $totalCount = $AWSIPRanges.Count
        $a = 0
        $b = 0
        $rawContent = "IPRange,Expiration,Notes`r`n"
        foreach($item in $AWSIPRanges){
            $range = $item.ip_prefix
            $serviceName = $item.service
            $rawContent += "$range,$Date,$serviceName`r`n"
            $a++
            $b++
            if($a -eq 100){
                Write-Host "$b entries of $totalCount processed"
                $a = 0
            }
        }
        Write-Host "$b entries with total of $totalCount GCP IP Ranges"
        
        #Write to Azure Watchlist
        $body = @{
            "properties" = @{
                "displayName" = "AWSIPRanges"
                "provider" = "AWS"
                "source" = "https://ip-ranges.amazonaws.com/ip-ranges.json"
                "itemsSearchKey" = "IPRange"
                "rawContent" = "$rawContent"
                "contentType" = "Text/csv"
                "numberOfLinesToSkip" = 0
            }
        }
        $body = $body | ConvertTo-Json
        $Uri = $resourceURI+"/subscriptions/"+$subscriptionId+"/resourceGroups/"+$resourceGroupName+"/providers/Microsoft.OperationalInsights/workspaces/"+$workspaceName+"/providers/Microsoft.SecurityInsights/watchlists/"+$watchlistAlias+"?api-version=2021-03-01-preview"
        $response = Invoke-RestMethod -Method Put -Headers $requestHeaders -Uri $Uri -Body $body
        #add error handling?
        Write-Host "Created new GCP IP watchlist with all ranges."
        
    }
    elseif ($new -eq $false) {
        
    }
}
if ($env:GCP -eq "Yes") {
    Write-Host "GCP is enabled, processing..."
    $watchlistAlias = "GCPIPRanges"
    $new = Check-Watchlist -watchlistAlias $watchlistAlias
    if ($new -eq $true) {
        Write-Host "No existing GCP IP watchlist found, building it"
        $GCPIPRanges = Get-GCPIPRanges
        $totalCount = $GCPIPRanges.Count
        $a = 0
        $b = 0
        $rawContent = "IPRange,Expiration,Notes`r`n"
        foreach($item in $GCPIPRanges){
            $range = $item.ipv4Prefix
            $serviceName = $item.service
            $rawContent += "$range,$Date,$serviceName`r`n"
            $a++
            $b++
            if($a -eq 100){
                Write-Host "$b entries of $totalCount processed"
                $a = 0
            }
        }
        Write-Host "$b entries with total of $totalCount GCP IP Ranges"
        
        #Write to Azure Watchlist
        $body = @{
            "properties" = @{
                "displayName" = "GCPIPRanges"
                "provider" = "Goolge"
                "source" = "https://www.gstatic.com/ipranges/cloud.json"
                "itemsSearchKey" = "IPRange"
                "rawContent" = "$rawContent"
                "contentType" = "Text/csv"
                "numberOfLinesToSkip" = 0
            }
        }
        $body = $body | ConvertTo-Json
        $Uri = $resourceURI+"/subscriptions/"+$subscriptionId+"/resourceGroups/"+$resourceGroupName+"/providers/Microsoft.OperationalInsights/workspaces/"+$workspaceName+"/providers/Microsoft.SecurityInsights/watchlists/"+$watchlistAlias+"?api-version=2021-03-01-preview"
        $response = Invoke-RestMethod -Method Put -Headers $requestHeaders -Uri $Uri -Body $body
        #add error handling?
        Write-Host "Created new GCP IP watchlist with all ranges."
    }
    elseif ($new -eq $false) {
        
    }
}
if ($env:Azure -eq "Yes") {
    Write-Host "Azure is enabled, processing..."
    $watchlistAlias = "AzureIPRanges"
    $new = Check-Watchlist -watchlistAlias $watchlistAlias
    if ($new -eq $true) {
        Write-Host "No existing Azure IP watchlist found, building it"
        $AzureIPRanges = Get-AzureIPRanges
        $totalCount = $AzureIPRanges.Count
        $a = 0
        $b = 0
        $c = 0
        $rawContent = "IPRange,Expiration,Notes`r`n"
        foreach($item in $AzureIPRanges){
            if(($item.properties.region) -eq ""){
                If(($item.properties.systemService) -eq ""){
                    $serviceName = $item.Id
                }
                else {
                    $serviceName = $Item.properties.systemService
                }
                foreach ($range in ($item.properties.addressPrefixes)){
                    $rawContent += "$range,$Date,$serviceName`r`n"
                    $c++
                }
            }
            $a++
            $b++
            if($a -eq 100){
                Write-Host "$b entries of $totalCount processed"
                $a = 0
            }
        }
        Write-Host "$b entries with total of $c Azure IP Ranges"
        
        #Write to Azure Watchlist
        $body = @{
            "properties" = @{
                "displayName" = "AzureIPRanges"
                "provider" = "Microsoft"
                "source" = "https://docs.microsoft.com/en-us/rest/api/virtualnetwork/service-tags/list"
                "itemsSearchKey" = "IPRange"
                "rawContent" = "$rawContent"
                "contentType" = "Text/csv"
                "numberOfLinesToSkip" = 0
            }
        }
        $body = $body | ConvertTo-Json
        #create function
        $Uri = $resourceURI+"/subscriptions/"+$subscriptionId+"/resourceGroups/"+$resourceGroupName+"/providers/Microsoft.OperationalInsights/workspaces/"+$workspaceName+"/providers/Microsoft.SecurityInsights/watchlists/"+$watchlistAlias+"?api-version=2021-03-01-preview"
        $response = Invoke-RestMethod -Method Put -Headers $requestHeaders -Uri $Uri -Body $body
        if (($response.id) -ne "" -or ($response.id) -ne $null) {
            Write-Host "Created new Azure IP watchlist with all ranges."
        }
        else {
            Write-Host "Creation of the watchlist may have errored"
        }
        
    }
    elseif ($new -eq $false) {
        Write-Host "Found existing Azure watchlist"
        #build tables
        $AzureIPRanges = Get-AzureIPRanges
        $AzureIPRangesTable = @()
        $totalCount = $AzureIPRanges.Count
        $a = 0
        $b = 0
        $c = 0
        foreach($item in $AzureIPRanges){
            if(($item.properties.region) -eq ""){
                If(($item.properties.systemService) -eq ""){
                    $serviceName = $item.Id
                }
                else {
                    $serviceName = $Item.properties.systemService
                }
                foreach ($range in ($item.properties.addressPrefixes)){
                    $AzureIPRangesTableObject = New-Object psobject
                    $AzureIPRangesTableObject | Add-Member -MemberType NoteProperty -Name "IPRange" -Value $range
                    $AzureIPRangesTableObject | Add-Member -MemberType NoteProperty -Name "Notes" -Value $serviceName
                    $AzureIPRangesTable += $AzureIPRangesTableObject
                    $c++
                }
            }
            $a++
            $b++
            if($a -eq 100){
                Write-Host "$b entries of $totalCount processed"
                $a = 0
            }
        }
        Write-Host "$b entries with total of $c Azure IP Ranges"
    
        #Build Watchlist Table
        $WatchListItemsTable = Get-WatchlistItemTable -watchlistAlias $watchlistAlias
        
        #Compare Watchlist Table to Ip Range Table
        $compareResults = Compare-Object $WatchListItemsTable $AzureIPRangesTable -Property IPRange -IncludeEqual -PassThru
    
        foreach ($compareresult in $compareResults) {
            if (($compareresult.SideIndicator) -eq "==") {
                #UpdateExpiration
                $Uri = $Uri = $resourceURI+"/subscriptions/"+$subscriptionId+"/resourceGroups/"+$resourceGroupName+"/providers/Microsoft.OperationalInsights/workspaces/"+$workspaceName+"/providers/Microsoft.SecurityInsights/watchlists/"+$watchlistAlias+"/watchlistItems?api-version=2021-03-01-preview"
            }
            elseif (($compareresult.SideIndicator) -eq "<=") {
                # Detele the item
            }
            elseif (($compareresult.SideIndicator) -eq "=>") {
                # Add new item
                            
            }
            
        }
    }
}

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"
