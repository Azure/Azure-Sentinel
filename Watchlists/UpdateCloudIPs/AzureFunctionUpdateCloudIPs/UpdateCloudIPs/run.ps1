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
        [string]$subscriptionId = $subscriptionId,
        $requestHeaders = $requestHeaders
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
        #write-host "Fetching another 100, this is number $($a) time"
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

#Add Watchlist Item
function Add-WatchlistItem{
    param(
        [string]$watchlistAlias,
        [string]$watchlistitem,
        [string]$Notes,
        [string]$resourceURI = $resourceURI,
        [string]$subscriptionId = $subscriptionId,
        [string]$resourceGroupName = $resourceGroupName,
        [string]$workspaceName = $workspaceName,
        $requestHeaders = $requestHeaders,
        $date = $date
    )

    $body = @{
        "properties" = @{
            "itemsKeyValue" = @{
                "IPRange" = "$watchlistitem"
                "Expiration" = "$Date"
                "Notes" = "$Notes"
            }
        }
    }
    $body = $body | ConvertTo-Json
    $Uri = $resourceURI+"/subscriptions/"+$subscriptionId+"/resourceGroups/"+$resourceGroupName+"/providers/Microsoft.OperationalInsights/workspaces/"+$workspaceName+"/providers/Microsoft.SecurityInsights/watchlists/"+$watchlistAlias+"/watchlistItems/"+$watchlistitem+"?api-version=2021-03-01-preview"
    $response = Invoke-RestMethod -Method Put -Headers $requestHeaders -Uri $Uri -Body $body
}

#Compare Watchlist Table to Ip Range Table
function Compare-WatchlistToTable {
    param (
        $WatchlistTable,
        $RangeTable,
        $Property
    )
    $results = Compare-Object $WatchlistTable $RangeTable -Property $Property -IncludeEqual -PassThru
    return $results
}

#Delete Watchlist Item
function Remove-WatchlistItem{
    param (
        [string]$watchlistAlias,
        [string]$watchlistitem,
        [string]$resourceURI = $resourceURI,
        [string]$subscriptionId = $subscriptionId,
        [string]$resourceGroupName = $resourceGroupName,
        [string]$workspaceName = $workspaceName,
        $requestHeaders = $requestHeaders
    )
    $Uri = $resourceURI+"/subscriptions/"+$subscriptionId+"/resourceGroups/"+$resourceGroupName+"/providers/Microsoft.OperationalInsights/workspaces/"+$workspaceName+"/providers/Microsoft.SecurityInsights/watchlists/"+$watchlistAlias+"/watchlistItems/"+$watchlistitem+"?api-version=2021-03-01-preview"
    $response = Invoke-RestMethod -Method Delete -Headers $requestHeaders -Uri $Uri
}

#Update Watchlist Item
function Update-WatchlistItem{
    param(
        [string]$watchlistAlias,
        [string]$watchlistitem,
        [string]$resourceURI = $resourceURI,
        [string]$subscriptionId = $subscriptionId,
        [string]$resourceGroupName = $resourceGroupName,
        [string]$workspaceName = $workspaceName,
        $requestHeaders = $requestHeaders,
        $date = $date
    )

    $body = @{
        "properties" = @{
            "itemsKeyValue" = @{
                "IPRange" = "$watchlistitem"
                "Expiration" = "$Date"
            }
        }
    }
    $body = $body | ConvertTo-Json
    $Uri = $resourceURI+"/subscriptions/"+$subscriptionId+"/resourceGroups/"+$resourceGroupName+"/providers/Microsoft.OperationalInsights/workspaces/"+$workspaceName+"/providers/Microsoft.SecurityInsights/watchlists/"+$watchlistAlias+"/watchlistItems/"+$watchlistitem+"?api-version=2021-03-01-preview"
    $response = Invoke-RestMethod -Method Put -Headers $requestHeaders -Uri $Uri -Body $body
}


#Prepare Variables
$subscriptionId = $env:SubscriptionId
$resourceGroupName = $env:ResourceGroupName
$workspaceName = $env:workspaceName
$resourceURI = $env:resourceURI
$tokenAuthURI = $env:IDENTITY_ENDPOINT + "?resource=$resourceURI&api-version=2019-08-01"
$tokenResponse = Invoke-RestMethod -Method Get -Headers @{"X-IDENTITY-HEADER"="$env:IDENTITY_HEADER"} -Uri $tokenAuthURI
$accessToken = $tokenResponse.access_token
$requestHeaders = @{
    "Authorization" = "Bearer $accessToken"
    "Content-Type"  = "application/json"
}
$Date = (Get-Date).AddDays(7) | Get-Date -Format yyyy-MM-ddT00:00:00Z

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
        
        #Write to Watchlist
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
        if (($response.id) -ne "" -or ($response.id) -ne $null) {
            Write-Host "Created new AWS IP watchlist with all ranges."
        }
        else {
            Write-Host "Creation of the watchlist may have errored"
        }        
    }
    elseif ($new -eq $false) {
        Write-Host "Found existing AWS watchlist"
        #build tables
        $AWSIPRanges = Get-AWSIPRanges
        $AWSIPRangesTable = @()
        $totalCount = $AWSIPRanges.Count
        $a = 0
        $b = 0
        $c = 0
        foreach($item in $AWSIPRanges){
            $range = $item.ip_prefix
            $serviceName = $item.service
            $AWSIPRangesTableObject = New-Object psobject
            $AWSIPRangesTableObject | Add-Member -MemberType NoteProperty -Name "IPRange" -Value $range
            $AWSIPRangesTableObject | Add-Member -MemberType NoteProperty -Name "Notes" -Value $serviceName
            $AWSIPRangesTableObject | Add-Member -MemberType NoteProperty -Name "ItemId" -Value ""
            $AWSIPRangesTable += $AWSIPRangesTableObject
            $a++
            $b++
            $c++
            if($a -eq 100){
                #Write-Host "$b entries of $totalCount processed"
                $a = 0
            }
        }
        Write-Host "$b entries with total of $c AWS IP Ranges"
    
        #Build Watchlist Table
        $WatchListItemsTable = Get-WatchlistItemTable -watchlistAlias $watchlistAlias
        
        #Compare Watchlist Table to Ip Range Table
        $compareResults = Compare-WatchlistToTable -WatchlistTable $WatchListItemsTable -RangeTable $AWSIPRangesTable -Property "IPRange"
        
        $rawContent = "IPRange,Expiration,Notes`r`n"
        foreach ($compareresult in $compareResults) {
            if (($compareresult.SideIndicator) -eq "==" -or ($compareresult.SideIndicator) -eq "=>") {
                #Update Expiration since it was in both lists
                #Write-Host "Updating expiration for $($compareresult.IPRange)" -ForegroundColor Blue
                $rawContent += "$($compareresult.IpRange),$Date,$($compareresult.Notes)`r`n"             
            }          
        }
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
        if (($response.id) -ne "" -or ($response.id) -ne $null) {
            Write-Host "Updated AWS IP watchlist."
        }
        else {
            Write-Host "Updating of the watchlist may have errored"
        } 
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
            if ($item.ipv4Prefix) {
                $range = $item.ipv4Prefix
            }
            if ($item.ipv6prefix) {
                $range = $item.ipv6prefix           
            }

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
        
        #Write to Watchlist
        $body = @{
            "properties" = @{
                "displayName" = "GCPIPRanges"
                "provider" = "Google"
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
        if (($response.id) -ne "" -or ($response.id) -ne $null) {
            Write-Host "Created new GCP IP watchlist with all ranges."
        }
        else {
            Write-Host "Creation of the watchlist may have errored"
        }
    }
    elseif ($new -eq $false) {
        Write-Host "Found existing GCP watchlist"
        #build tables
        $GCPIPRanges = Get-GCPIPRanges
        $GCPIPRangesTable = @()
        $totalCount = $GCPIPRanges.Count
        $a = 0
        $b = 0
        $c = 0
        foreach($item in $GCPIPRanges){
            if ($item.ipv4Prefix) {
                $range = $item.ipv4Prefix
            }
            if ($item.ipv6prefix) {
                $range = $item.ipv6prefix           
            }
            $serviceName = $item.service
            $GCPIPRangesTableObject = New-Object psobject
            $GCPIPRangesTableObject | Add-Member -MemberType NoteProperty -Name "IPRange" -Value $range
            $GCPIPRangesTableObject | Add-Member -MemberType NoteProperty -Name "Notes" -Value $serviceName
            $GCPIPRangesTableObject | Add-Member -MemberType NoteProperty -Name "ItemId" -Value ""
            $GCPIPRangesTable += $GCPIPRangesTableObject
            $a++
            $b++
            $c++
            if($a -eq 100){
                #Write-Host "$b entries of $totalCount processed"
                $a = 0
            }
        }
        Write-Host "$b entries with total of $c GCP IP Ranges"
    
        #Build Watchlist Table
        $WatchListItemsTable = Get-WatchlistItemTable -watchlistAlias $watchlistAlias
        
        #Compare Watchlist Table to Ip Range Table
        $compareResults = Compare-WatchlistToTable -WatchlistTable $WatchListItemsTable -RangeTable $GCPIPRangesTable -Property "IPRange"
    
        $rawContent = "IPRange,Expiration,Notes`r`n"
        foreach ($compareresult in $compareResults) {
            if (($compareresult.SideIndicator) -eq "==" -or ($compareresult.SideIndicator) -eq "=>") {
                #Update Expiration since it was in both lists
                #Write-Host "Updating expiration for $($compareresult.IPRange)" -ForegroundColor Blue
                $rawContent += "$($compareresult.IpRange),$Date,$($compareresult.Notes)`r`n"             
            }          
        }
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
        if (($response.id) -ne "" -or ($response.id) -ne $null) {
            Write-Host "Updated GCP IP watchlist with all ranges."
        }
        else {
            Write-Host "Updating of the watchlist may have errored"
        }
    }
}
if ($env:Azure -eq "Yes") {
    Write-Host "Azure is enabled, processing..."
    $watchlistAlias = "AzureIPRanges"
    $new = Check-Watchlist -watchlistAlias $watchlistAlias
    if ($new -eq $true) {
        Write-Host "No existing Azure IP watchlist found, building it"
        $AzureIPRanges = (Get-AzNetworkServiceTag -location centralus).Values
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
                "source" = "https://docs.microsoft.com/rest/api/virtualnetwork/service-tags/list"
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
        $AzureIPRanges = (Get-AzNetworkServiceTag -location centralus).Values
        $AzureIPRangesTable = @()
        $totalCount = $AzureIPRanges.Count
        $a = 0
        $b = 0
        $c = 0
        foreach($item in $AzureIPRanges){
            if(($item.properties.Region) -eq ""){
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
                    $AzureIPRangesTableObject | Add-Member -MemberType NoteProperty -Name "ItemId" -Value ""
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
        $compareResults = Compare-WatchlistToTable -WatchlistTable $WatchListItemsTable -RangeTable $AzureIPRangesTable -Property "IPRange"
    
        $rawContent = "IPRange,Expiration,Notes`r`n"
        foreach ($compareresult in $compareResults) {
            if (($compareresult.SideIndicator) -eq "==" -or ($compareresult.SideIndicator) -eq "=>") {
                #Update Expiration since it was in both lists
                #Write-Host "Updating expiration for $($compareresult.IPRange)" -ForegroundColor Blue
                $rawContent += "$($compareresult.IpRange),$Date,$($compareresult.Notes)`r`n"             
            }          
        }
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
            Write-Host "Updated Azure IP watchlist with all ranges."
        }
        else {
            Write-Host "Updating of the watchlist may have errored"
        }
    }
}

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"
