# PowerShell script file to be executed as a AWS Lambda function.
#
# When executing in Lambda the following variables will be predefined.
#   $LambdaInput - A PSObject that contains the Lambda function input data.
#   $LambdaContext - An Amazon.Lambda.Core.ILambdaContext object that contains information about the currently running Lambda environment.
#
# The last item in the PowerShell pipeline will be returned as the result of the Lambda function.
#
# To include PowerShell modules with your Lambda function, like the AWS.Tools.S3 module, add a "#Requires" statement
# indicating the module and version. If using an AWS.Tools.* module the AWS.Tools.Common module is also required.
#
# The following link contains documentation describing the structure of the S3 event object.
# https://docs.aws.amazon.com/AmazonS3/latest/dev/notification-content-structure.html

#Requires -Modules @{ModuleName='AWS.Tools.Common';ModuleVersion='4.0.6.0'}
#Requires -Modules @{ModuleName='AWS.Tools.S3';ModuleVersion='4.0.6.0'}

# Uncomment to send the input event to CloudWatch Logs
# Write-Host (ConvertTo-Json -InputObject $LambdaInput -Compress -Depth 5)

foreach ($record in $LambdaInput.Records) {
    #Credit to Travis Roberts for the function from https://github.com/tsrob50/LogAnalyticsAPIFunction/blob/master/Write-OMSLogfile.ps1
    function Write-OMSLogfile {
        <#
        .SYNOPSIS
        Inputs a hashtable, date and workspace type and writes it to a Log Analytics Workspace.
        .DESCRIPTION
        Given a  value pair hash table, this function will write the data to an OMS Log Analytics workspace.
        Certain variables, such as Customer ID and Shared Key are specific to the OMS workspace data is being written to.
        This function will not write to multiple OMS workspaces.  Build-signature and post-analytics function from Microsoft documentation
        at https://docs.microsoft.com/azure/log-analytics/log-analytics-data-collector-api
        .PARAMETER DateTime
        date and time for the log.  DateTime value
        .PARAMETER Type
        Name of the logfile or Log Analytics "Type".  Log Analytics will append _CL at the end of custom logs  String Value
        .PARAMETER LogData
        A series of key, value pairs that will be written to the log.  Log file are unstructured but the key should be consistent
        withing each source.
        .INPUTS
        The parameters of data and time, type and logdata.  Logdata is converted to JSON to submit to Log Analytics.
        .OUTPUTS
        The Function will return the HTTP status code from the Post method.  Status code 200 indicates the request was received.
        .NOTES
        Version:        2.0
        Author:         Travis Roberts
        Creation Date:  7/9/2018
        Purpose/Change: Crating a stand alone function.
        .EXAMPLE
        This Example will log data to the "LoggingTest" Log Analytics table
        $type = 'LoggingTest'
        $dateTime = Get-Date
        $data = @{
            ErrorText   = 'This is a test message'
            ErrorNumber = 1985
        }
        $returnCode = Write-OMSLogfile $dateTime $type $data -Verbose
        write-output $returnCode
        #>
        [cmdletbinding()]
        Param(
            [Parameter(Mandatory = $true, Position = 0)]
            [datetime]$dateTime,
            [parameter(Mandatory = $true, Position = 1)]
            [string]$type,
            [Parameter(Mandatory = $true, Position = 2)]
            [psobject]$logdata,
            [Parameter(Mandatory = $true, Position = 3)]
            [string]$CustomerID,
            [Parameter(Mandatory = $true, Position = 4)]
            [string]$SharedKey
        )
        Write-Verbose -Message "DateTime: $dateTime"
        Write-Verbose -Message ('DateTimeKind:' + $dateTime.kind)
        Write-Verbose -Message "Type: $type"
        write-Verbose -Message "LogData: $logdata"
    
        #region Workspace ID and Key
        # Workspace ID for the workspace
        #$CustomerID = 'ENTER WORKSPACE ID HERE'
    
        # Shared key needs to be set for environment
        #$SharedKey = 'ENTER WORKSPACE KEY HERE'
    
        #endregion
    
        # Supporting Functions
        # Function to create the auth signature
        function Build-signature ($CustomerID, $SharedKey, $Date, $ContentLength, $method, $ContentType, $resource) {
            $xheaders = 'x-ms-date:' + $Date
            $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $resource
            $bytesToHash = [text.Encoding]::UTF8.GetBytes($stringToHash)
            $keyBytes = [Convert]::FromBase64String($SharedKey)
            $sha256 = New-Object System.Security.Cryptography.HMACSHA256
            $sha256.key = $keyBytes
            $calculateHash = $sha256.ComputeHash($bytesToHash)
            $encodeHash = [convert]::ToBase64String($calculateHash)
            $authorization = 'SharedKey {0}:{1}' -f $CustomerID, $encodeHash
            return $authorization
        }
        # Function to create and post the request
        Function Post-LogAnalyticsData ($CustomerID, $SharedKey, $Body, $Type) {
            $method = "POST"
            $ContentType = 'application/json'
            $resource = '/api/logs'
            $rfc1123date = ($dateTime).ToString('r')
            $ContentLength = $Body.Length
            $signature = Build-signature `
                -customerId $CustomerID `
                -sharedKey $SharedKey `
                -date $rfc1123date `
                -contentLength $ContentLength `
                -method $method `
                -contentType $ContentType `
                -resource $resource
            $uri = "https://" + $customerId + ".ods.opinsights.azure.com" + $resource + "?api-version=2016-04-01"
            $headers = @{
                "Authorization"        = $signature;
                "Log-Type"             = $type;
                "x-ms-date"            = $rfc1123date
                "time-generated-field" = $dateTime
            }
            $response = Invoke-WebRequest -Uri $uri -Method $method -ContentType $ContentType -Headers $headers -Body $body -UseBasicParsing
            Write-Verbose -message ('Post Function Return Code ' + $response.statuscode)
            return $response.statuscode
        }
    
        # Check if time is UTC, Convert to UTC if not.
        # $dateTime = (Get-Date)
        if ($dateTime.kind.tostring() -ne 'Utc') {
            $dateTime = $dateTime.ToUniversalTime()
            Write-Verbose -Message $dateTime
        }
    
        # Add DateTime to hashtable
        #$logdata.add("DateTime", $dateTime)
        $logdata | Add-Member -MemberType NoteProperty -Name "DateTime" -Value $dateTime
    
        #Build the JSON file
        $logMessage = ConvertTo-Json $logdata -Depth 20
        Write-Verbose -Message $logMessage
    
        #Submit the data
        $returnCode = Post-LogAnalyticsData -CustomerID $CustomerID -SharedKey $SharedKey -Body ([System.Text.Encoding]::UTF8.GetBytes($logMessage)) -Type $type
        Write-Verbose -Message "Post Statement Return Code $returnCode"
        return $returnCode
    }
    
    $bucket = $record.s3.bucket.name
    $key = $record.s3.object.key

    $workspaceId = "workspaceId"
    $workspaceKey = "workspaceKey"
    $CustomLogName = "CustomLog"
    #$worksapceId = $env:workspaceId
    #$workspaceKey = $env:workspaceKey
    #$CustomLogName = $env:CustomLogName


    Write-Host "Processing event for: bucket = $bucket, key = $key"

    # TODO: Add logic to handle S3 event record, for example
    $obj = Get-S3Object -Bucket $bucket -Key $key
    Write-Host "Object $key is $($obj.Size) bytes"

    #Download the file
    Write-Host "Downloading $key to /tmp/$key"
    Read-S3Object -BucketName $bucket -Key $key -File "/tmp/$key"
    Write-Host "Downloaded $key to /tmp/$key"

    #Determine if CSV or JSON or whatever
    $FileName = "/tmp/$key"
    if ($fileName -like "*.csv") {
        Write-Host "Handling CSV File"
        $data = import-csv $filename
    }
    elseif ($filename -like "*.json") {
        Write-Host "Handling JSON File"
        $Data = Get-Content $filename | ConvertFrom-Json
    }
    elseif ($filename -like "*.log") {
        Write-Host "Handling Log File"
        #Assuming CEF formatted logs
        $cefdata = Get-Content $filename
        $data = @()
        $cefmsg = @{}
        foreach ($line in $cefdata) {
            if ($line -like "*CEF:*") {
                #Write-Host "Handling CEF Data"
                $CEFtimegenerated = ($line -split '(?<time>(?:\w+ +){2,3}(?:\d+:){2}\d+|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.[\w\-\:\+]{3,12})')[1]
                #$CEFHost = (($line -split '(?<time>(?:\w+ +){2,3}(?:\d+:){2}\d+|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.[\w\-\:\+]{3,12})')[2] -split "CEF:")[0]
                #$CEFVersion = $line.Split("CEF: ").Split("|")[1]
                $CEFDeviceVendor = $line.split("|")[1]
                $CEFDeviceProduct = $line.split("|")[2]
                $CEFDeviceVersion = $line.split("|")[3]
                $CEFDeviceEventClassId = $line.split("|")[4]
                $CEFName = $line.split("|")[5]
                $CEFSeverity = $line.split("|")[6]
                $CEFExtension = $line.split("|")[7] -split '([^=\s]+=(?:[\\]=|[^=])+)(?:\s|$)'
                foreach ($extenstion in $CEFExtension) {
                    if ($extenstion -like "*=*") { $cefmsg += @{$extenstion.Split("=")[0] = $extenstion.Split("=")[1] } }
                }      
                $CEFmsg += @{TimeGenerated = $CEFtimegenerated }
                $CEFmsg += @{DeviceVendor = $CEFDeviceVendor }
                $CEFmsg += @{DeviceProduct = $CEFDeviceProduct }
                $CEFmsg += @{DeviceVersion = $CEFDeviceVersion }
                $CEFmsg += @{DeviceEventClassID = $CEFDeviceEventClassId }
                $CEFmsg += @{Activity = $CEFName }
                $CEFmsg += @{LogSeverity = $CEFSeverity }
                $data += $CEFmsg
                $cefmsg = @{}
            }
        }
        Write-Host "Finished Handling Log file"
    }
    else { Write-Host "$filename is not supported yet" }

    Write-Host "Number of data records: " ($Data.Count)
    #Parsing Function to drop or add or edit fields
    #FUTURE

    #Test Size; Log A limit is 30MB
    $tempdata = @()
    $tempDataSize = 0
    Write-Host "Checking if upload is over 25MB"
    if ((($Data |  Convertto-json -depth 20).Length) -gt 25MB) {
        Write-Host "Upload needs to be split"
        foreach ($record in $data) {
            $tempdata += $record
            $tempDataSize += ($record | ConvertTo-Json -depth 20).Length
            if ($tempDataSize -gt 25MB) {
                Write-OMSLogfile -dateTime (Get-Date) -type $CustomLogName -logdata $tempdata -CustomerID $workspaceId -SharedKey $workspaceKey
                write-Host "Sending data = $TempDataSize"
                $tempdata = $null
                $tempdata = @()
                $tempDataSize = 0
            }
        }
        Write-Host "Sending left over data = $Tempdatasize"
        Write-OMSLogfile -dateTime (Get-Date) -type $CustomLogName -logdata $tempdata -CustomerID $workspaceId -SharedKey $workspaceKey
    }
    Else {
        #Send to Log A as is
        Write-Host "Upload does not need to be split, sending to Log A"
        Write-OMSLogfile -dateTime (Get-Date) -type $CustomLogName -logdata $Data -CustomerID $workspaceId -SharedKey $workspaceKey
    }

    Remove-Item $FileName -Force
}

