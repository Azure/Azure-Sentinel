<#
.SYNOPSIS
    This script will export the watchlist items to a csv file. 
.DESCRIPTION
    Depending on the size of the watchlist(s) this script might take a while.
.NOTES
    Author      : Dagny Verbeeck
    Company     : The Collective Consulting BV
    Last Edit   : 2023-05-23
#>

#region Functions
#Get all watchlists
Function Get-Watchlists() {
    param(
        [string] $resourceURI = $resourceURI,
        [string] $sentinelSubscriptionID = $subscriptionId,
        [string] $sentinelResourceGroup = $resourceGroupName,
        [string] $sentinelWorkspaceName = $workspaceName,
        [string] $apiVersion = $apiVersion,
        $requestHeaders = $requestHeader
    )

    #API that gets all watchlists
    $apiWatchlist = $resourceURI + "/subscriptions/" + $sentinelSubscriptionID + "/resourceGroups/" + $sentinelResourceGroup + "/providers/Microsoft.OperationalInsights/workspaces/" + $sentinelWorkspaceName + "/providers/Microsoft.SecurityInsights/watchlists?api-version=" + $apiVersion

    try {
        #Retrieve the watchlist aliases
        $responseWatchlist = (Invoke-RestMethod -Method Get -Headers $requestHeaders -Uri $apiWatchlist)
        # Check if there is a nextLink and retrieve all watchlist aliases
        while ($responseWatchlist.nextLink) {
            $aliases += ($responseWatchlist.value | ForEach-Object { $_.properties.watchlistAlias })
            $responseWatchlist = (Invoke-RestMethod -Method Get -Headers $requestHeaders -Uri $responseWatchlist.nextLink)
        }
        # Add the last set of aliases
        $aliases += ($responseWatchlist.value | ForEach-Object { $_.properties.watchlistAlias })
    }
    catch {
        # Display error message to user
        Write-Host "API request to retrieve watchlists failed"
        Write-Host "Response code: $($_.Exception.Response.StatusCode.value__)"
        Write-Host "Exception message: $($_.Exception.Message)"
    }
    Write-Information "The watchlists with following aliases are found:"
    Write-Information ($aliases -join ", ")

    return $aliases
}

#Get all watchlist items
function Get-WatchlistItems {
    param(
        [Parameter(Mandatory = $true)]
        $watchlistAlias,
        [string] $resourceURI = $resourceURI,
        [string] $sentinelSubscriptionID = $subscriptionId,
        [string] $sentinelResourceGroup = $resourceGroupName,
        [string] $sentinelWorkspaceName = $workspaceName,
        [string] $apiVersion = $apiVersion,
        $requestHeaders = $requestHeader
    )
    
    Write-Host "Getting watchlist items for watchlist: $watchlistAlias"
    
    #API that gets all watchlist items
    $apiWatchlistItems = $resourceURI + "/subscriptions/" + $sentinelSubscriptionID + "/resourceGroups/" + $sentinelResourceGroup + "/providers/Microsoft.OperationalInsights/workspaces/" + $sentinelWorkspaceName + "/providers/Microsoft.SecurityInsights/watchlists/" + $watchlistAlias + "/watchlistItems?api-version=" + $apiVersion
        
    try {
        #Retrieve the watchlist items for the current watchlist
        $response = Invoke-RestMethod -Method Get -Headers $requestHeader -Uri $apiWatchlistItems
        $responseWatchlistItems = $response.value
    }
    catch {
        # Display error message to user
        Write-Host "API request to retrieve watchlist items failed"
        Write-Host "Response code: $($_.Exception.Response.StatusCode.value__)"
        Write-Host "Exception message: $($_.Exception.Message)"
    }
    
    #Create an empty list to store the watchlist items as strings
    $watchlistItemsStrings = @()

    #Create an empty list to store the column headings
    $columnHeadings = @()

    #Add the watchlist items to the list
    foreach ($item in $responseWatchlistItems) {
        #Get the current watchlist item's data
        $watchlistItemData = $item.properties.itemsKeyValue

        #Create an empty array to store the current watchlist item's values
        $watchlistItemValues = @()

        #Get the current watchlist item's column headings
        $currentColumnHeadings = $watchlistItemData.PSObject.Properties.Name

        #Add any new column headings to the list
        foreach ($heading in $currentColumnHeadings) {
            if ($columnHeadings -notcontains $heading) {
                $columnHeadings += $heading
            }
        }

        #Add the current watchlist item's values to the array in the same order as the column headings
        foreach ($heading in $columnHeadings) {
            $watchlistItemValues += $watchlistItemData.$heading
        }

        #Join the current watchlist item's values into a single string
        $watchlistItemString = $watchlistItemValues -join ','

        #Add the current watchlist item's string to the list
        $watchlistItemsStrings += $watchlistItemString
    }

    #Join the column headings into a single string
    $columnHeadingsString = $columnHeadings -join ','

    try {
        #Export the column headings and watchlist items to a CSV file
        $columnHeadingsString | Set-Content -Path "$HOME\Downloads\$watchlist.csv"
        $watchlistItemsStrings | Add-Content -Path "$HOME\Downloads\$watchlist.csv"

        Write-Host "Succesfully exported the watchlist data to a csv file."
        Write-Host "File is found at 'Downloads' with name: $watchlist.csv"
    }
    catch {
        #Display error message to user
        Write-Host "An error occurred while exporting the watchlist items: "
        Write-Host "$($_.Exception.Message)"
    }
}
#endRegion

#Connect to Azure 
Write-Host "Connect to azure, make sure you have access to Sentinel."
Connect-AzAccount

#Get subscription ID
$subscriptionId = Read-Host -Prompt 'Enter your Sentinel Subscription ID'

#Set subscription context
Select-AzSubscription -SubscriptionId $subscriptionId

#region Variables
$resourceURI = "https://management.azure.com"
$apiVersion = "2023-04-01-preview"

#Get access token
$accessToken = (Get-AzAccessToken -ResourceUrl "https://management.azure.com").Token

#Set request header 
$requestHeader = @{
    "Authorization" = "Bearer $($accessToken)"
}
#endRegion

#Get resource group
$resourceGroupName = Read-Host -Prompt 'Enter your Sentinel Resource Group'

#Get workspace name
$workspaceName = Read-Host -Prompt 'Enter your Sentinel Workspace Name'

#Main
$watchlists = Get-Watchlists

$notFound = $true

while ($notFound) {
    #Prompt user for input
    $selectedWatchlists = Read-Host -Prompt 'Enter the watchlist aliases you want to export (separated by commas)'

    #Remove leading/trailing whitespace and split input into an array
    $selectedWatchlists = $selectedWatchlists.Trim() -split ',' | ForEach-Object { $_.Trim() }

    #Check if any of the selected watchlists are not in the list of watchlists
    $notFound = Compare-Object -ReferenceObject $watchlists -DifferenceObject $selectedWatchlists -PassThru | Where-Object { $_.SideIndicator -eq '=>' }
    if ($notFound) {
        Write-Host "The following watchlist aliases were not found: $($notFound -join ', '). Please check your spelling."
    }
}

foreach ($watchlist in $watchlists) {
    #Check if the current watchlist is in the selected watchlists (case-insensitive)
    if ($selectedWatchlists -icontains $watchlist) {
        $watchlistItems = Get-WatchlistItems -watchlistAlias $watchlist
    }
}