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
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Url,
        [Parameter(Mandatory = $true, Position = 1)]
        [string]$Pattern
    )
        # Create WebResponseObject from Download URL
        $WebResponseObj = Invoke-WebRequest -Uri $Url -UseBasicParsing

        # Find all href tags and match for json string in URL
        $OutputUrl = $WebResponseObj.Links  | Where-Object {$_.href -like $Pattern} | Get-Unique | % href

        return $OutputUrl
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
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$ConnectionString,
        [Parameter(Mandatory = $true, Position = 1)]
        [string]$Container,
        [Parameter(Mandatory = $true, Position = 2)]
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

# Get the current universal time in the default string format
$currentUTCtime = (Get-Date).ToUniversalTime()

$azstoragestring = $Env:WEBSITE_CONTENTAZUREFILECONNECTIONSTRING
$Container = 'lookuptables'

$azurepublic = 'https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519'
$msftpublic = 'https://www.microsoft.com/en-us/download/confirmation.aspx?id=53602'
$awsipranges = 'https://ip-ranges.amazonaws.com/ip-ranges.json'
$officeworldwide = 'https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7'


#Additional Parsing for MSFT and Azure Urls
$azurepublicjson = ParseUrlfromHTML -Url $azurepublic -Pattern '*json'
$msftpubliccsv = ParseUrlfromHTML -Url $msftpublic -Pattern '*csv'

# Download Output URL to Temp directory and normalize file name with out Date
Invoke-WebRequest -Uri $azurepublicjson -OutFile $env:TEMP\ServiceTags_Public.json 
Invoke-WebRequest -Uri $msftpubliccsv -OutFile $env:TEMP\MSFT-Public-IPs.csv
Invoke-WebRequest -Uri $awsipranges -OutFile $env:TEMP\AWS-IP-Ranges.json
Invoke-WebRequest -Uri $officeworldwide -OutFile $env:TEMP\Office-WorldWide.json

# Upload Files to Blob Storage
UploadtoBlob -ConnectionString $azstoragestring -Container $Container -InputFile $env:TEMP\ServiceTags_Public.json
UploadtoBlob -ConnectionString $azstoragestring -Container $Container -InputFile $env:TEMP\MSFT-Public-IPs.csv
UploadtoBlob -ConnectionString $azstoragestring -Container $Container -InputFile $env:TEMP\AWS-IP-Ranges.json
UploadtoBlob -ConnectionString $azstoragestring -Container $Container -InputFile $env:TEMP\Office-WorldWide.json    

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"