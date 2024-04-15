# Created On: 9/13/2021 3:36 PM
# Created By: Nathan Swift - nathan.swift@swiftsolves.com
# This script is as is and not supported by Microsoft 
# Microsoft does not assume any risk of data loss
# Use it at your own risk
################################################################################

<#  Possible Futures:
 
1. rewrite into Functions with Parameter inputs
2. logic checks on the string inputs
3. Bug: fix output file there is an extra line seperator between externaldata() and open array

#>

<#
# Used for manual testing

$storageaccount = "storageaccountname"
$loganalyticsworkspace = "workspacename"
$tablename = "emailevents"
$startdate = [DateTime] "09/11/2021 02:00 AM"
$enddate = [DateTime] "09/12/2021 12:00 PM"

#>

# Prompt user for key information for look ups
$loganalyticsworkspace = Read-Host -Prompt "Enter your Log Analytics workspace name to lookup logs"

# Log analyticsworkspace resource id
$loganalyticsworkspaceid = (Get-AzResource -Name $loganalyticsworkspace).ResourceId

# Storage account name
$storageaccount = Read-Host -Prompt "Enter your storage account name to lookup logs"

# Storage resource id
$storageid = (Get-AzResource -Name $storageaccount).ResourceId

# Log analytics workspace table name
$tablename = Read-Host -Prompt "Enter your table name to export"
$tablename = $tablename.ToLower()
$containername = "am-" + $tablename
$containernamesearch = "am-" + $tablename + "*"


# generate filepath for kql table query lookup
$file = Get-Date -Format "yyyyMMddhhmmss"
$filepath = $containername + $file + ".yaml" #"c:\temp\" + 

# Start date to find log files for
$startdate = Read-Host -Prompt "Enter your start date using this format as an ex. 09/11/2021 02:00 AM"

# End date to find log files for
$enddate = Read-Host -Prompt "Enter your end date using this format as an ex. 09/12/2021 12:00 PM"

# Storage resource group
$storerg = $storageid.Split('/')[4]

# Obtain storage account key where logs are
$azstorekey = (Get-AzStorageAccountKey -Name $storageaccount -ResourceGroupName $storerg).value[0]

# Generate storage account context
$context = New-AzStorageContext -StorageAccountName $storageaccount -StorageAccountKey $azstorekey

# Obtain storage blobs from within the start and end date ranges
$blobs = Get-AzStorageContainer -Name $containernamesearch -Context $context | Get-AzStorageBlob 
$blobs = $blobs | Where-Object {$_.LastModified -ge $startdate -and $_.LastModified -le $enddate}


# request for generated SAS Uris for 8 hours to KQL query
$expiredattime = (Get-Date).AddHours(8)

# Obtain URL for first line of extenaldata() lookup kql file
$url = 'https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Tools/externaldata/' + $tablename + '.yaml'
$firststring = Invoke-WebRequest -UseBasicParsing $url

#Build Error handling for generic lookup with no schema found


$lineinsert = ($firststring.Content).Split('[')[0] 
Echo $lineinsert | Out-File $filepath -Append



# count number of blobs to determine when last SAS uri is requested
$numblobs = $blobs.Count

# KQL Query insert
$lineinsert = '['
Echo $lineinsert | Out-File $filepath -Append
#Start counter at one
$counter = 1

#For each of the SAS Blobs generate a SAS Uri and KQL Query insert
Foreach ($blob in $blobs){
    
    #generate blob uri
    $bloburi = New-AzStorageBlobSASToken -Context $context -Container $containername -Blob $blob.Name -Permission r -ExpiryTime $expiredattime -FullUri
    
    # KQL Query insert SAS Uri
    if ($counter -lt $numblobs) {
        $lineinsert = 'h@"' + $bloburi + '",'
        Echo $lineinsert | Out-File $filepath -Append
    }
    
    if ($counter -ge $numblobs) {
        $lineinsert = 'h@"' + $bloburi + '"'
        Echo $lineinsert | Out-File $filepath -Append
    }

    # update counter 
    $counter++
}

# KQL Query insert
$lineinsert = ']'
Echo $lineinsert | Out-File $filepath -Append
$lineinsert = 'with(format="json")'
Echo $lineinsert | Out-File $filepath -Append

## Fix Caritridge return space
(Get-Content $filepath) | ? {$_.trim() -ne "" } | set-content $filepath

# Open a notepad of the KQL Query
Start-Process notepad.exe $filepath