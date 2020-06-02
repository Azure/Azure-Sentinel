# Input bindings are passed in via param block.
param($Timer)


function ParseUrlfromHTML {
    <#
    .DESCRIPTION
    This function parses HTML response text for all links and extract link ending with json.
    .PARAMETER Url
    Input URL to parse HTML response and extract output Json link.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Url
    )
        # Create WebResponseObject from Download URL
        $WebResponseObj = Invoke-WebRequest -Uri $Url -UseBasicParsing

        # Find all href tags and match for json string in URL
        $JsonUrl = $WebResponseObj.Links  | Where-Object {$_.href -like "*json"} | Get-Unique | % href

        return $JsonUrl
}


function UploadtoBlob {
    <#
    .DESCRIPTION
    This function uploads input file to blob storage.
    .PARAMETER ConnectionString
    Storage Connection string to connect to storage account.
    .PARAMETER Container
    Storage container or folder where file to be uploaded
    .PARAMETER InputFile
    Input File to be uploaded to blob storage under container
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ConnectionString,
        [Parameter(Mandatory)]
        [string]$Container,
        [Parameter(Mandatory)]
        [string]$InputFile
    )

    $Context = New-AzStorageContext -ConnectionString $connectionstring
    if((Get-AzStorageContainer -Context $Context).Name -eq $Container){
    #Set Storage Blob Content as inputfile parameter to Upload
    Set-AzStorageBlobContent -file $InputFile -Container $Container -Context $Context -Force   
    }
    else{
    #create container
    New-AzStorageContainer -Name $Container -Context $Context
    #Set Storage Blob Content as inputfile parameter to Upload
    Set-AzStorageBlobContent -file $InputFile -Container $Container -Context $Context -Force  
    }
}

# Get the current universal time in the default string format
$currentUTCtime = (Get-Date).ToUniversalTime()

# The 'IsPastDue' porperty is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

       
$InputUrl = 'https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519'
$OutputUrl = ParseUrlfromHTML -Url $InputUrl

#Additional Parsing of Dates from Url string to compare date for conditional logic
$JsonDate = $OutputUrl.Split('_')[2].Split('.')[0]

# Get the current universal time in the default string format
$currentUTCtime = (Get-Date).ToUniversalTime()

$azstoragestring = $Env:WEBSITE_CONTENTAZUREFILECONNECTIONSTRING
$Container = 'whitelist'
$InputFile = "$env:TEMP\ServiceTags_Public.json"

# Download Output JSON URL to Temp directory and normalize file name with out Date
Invoke-WebRequest -Uri $OutputUrl -OutFile $env:TEMP\ServiceTags_Public.json 
#Upload Json file to blob storage
UploadtoBlob -ConnectionString $azstoragestring -Container $Container -InputFile $InputFile

$Tracker = 'processedtracker'
# Write Date of Url to File
$JsonDate | Out-File "$env:TEMP\ServiceTagsLastProcessed.log"
$TrackerFile = "$env:TEMP\ServiceTagsLastProcessed.log"

# Upload Tracker File
UploadtoBlob -ConnectionString $azstoragestring -Container $Tracker -InputFile $TrackerFile

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"
