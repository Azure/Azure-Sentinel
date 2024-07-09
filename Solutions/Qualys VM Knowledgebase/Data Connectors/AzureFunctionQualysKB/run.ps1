<#
    Title:          Qualys KnowledgeBase (KB) Data Connector
    Language:       PowerShell
    Version:        1.0
    Author(s):      Microsoft
    Last Modified:  12/04/2020
    Comment:        Initial Release

    DESCRIPTION
    This Function App calls the Qualys Vulnerability Management (VM) - KnowledgeBase (KB) API (https://www.qualys.com/docs/qualys-api-vmpc-user-guide.pdf) to pull vulnerability data from the Qualys KB.
    The response from the Qualys API is recieved in XML format. This function will build the signature and authorization header
    needed to post the data to the Log Analytics workspace via the HTTP Data Connector API. This Function App will the vulnerability records to the QualysKB_CL table in Microsoft Sentinel/Log Analytics
#>

# Input bindings are passed in via param block.
param($Timer)

# Get the current universal time in the default string format.
$currentUTCtime = (Get-Date).ToUniversalTime()

$logAnalyticsUri = $env:logAnalyticsUri

# The 'IsPastDue' property is 'true' when the current function invocation is later than scheduled.
if ($Timer.IsPastDue) {
    Write-Host "PowerShell timer is running late!"
}

function Html-ToText {
    param([System.String] $html)

    # remove line breaks, replace with spaces
    $html = $html -replace "(`r|`n|`t)", " "

    # remove invisible content
    @('head', 'style', 'script', 'object', 'embed', 'applet', 'noframes', 'noscript', 'noembed') | % {
    $html = $html -replace "<$_[^>]*?>.*?</$_>", ""
    }

    # Condense extra whitespace
    $html = $html -replace "( )+", " "

    # Add line breaks
    @('div','p','blockquote','h[1-9]') | % { $html = $html -replace "</?$_[^>]*?>.*?</$_>", ("`n" + '$0' )}

    # Add line breaks for self-closing tags
    @('div','p','blockquote','h[1-9]','br') | % { $html = $html -replace "<$_[^>]*?/>", ('$0' + "`n")}

    #strip tags
    $html = $html -replace "<[^>]*?>", ""

    # replace common entities
    @(
    @("&amp;bull;", " * "),
    @("&amp;lsaquo;", "<"),
    @("&amp;rsaquo;", ">"),
    @("&amp;(rsquo|lsquo);", "'"),
    @("&amp;(quot|ldquo|rdquo);", '"'),
    @("&amp;trade;", "(tm)"),
    @("&amp;frasl;", "/"),
    @("&amp;(quot|#34|#034|#x22);", '"'),
    @('&amp;(amp|#38|#038|#x26);', "&amp;"),
    @("&amp;(lt|#60|#060|#x3c);", "<"),
    @("&amp;(gt|#62|#062|#x3e);", ">"),
    @('&amp;(copy|#169);', "(c)"),
    @("&amp;(reg|#174);", "(r)"),
    @("&amp;nbsp;", " "),
    @("&amp;(.{2,6});", "")) | % { $html = $html -replace $_[0], $_[1] }

    return $html

}
 # Function to retrieve the checkpoint start time of the last successful API call for a given logtype. Checkpoint file will be created if none exists
function GetStartTime($CheckpointFile, $timeInterval){

    $firstStartTimeRecord = [datetime]::UtcNow.AddMinutes(-$timeInterval).ToString("yyyy-MM-ddTHH:mm:ssZ")

    if ([System.IO.File]::Exists($CheckpointFile) -eq $false) {
        $CheckpointLog = @{}
        $CheckpointLog.Add('LastSuccessfulTime', $firstStartTimeRecord)
        $CheckpointLog.GetEnumerator() | Select-Object -Property Key,Value | Export-CSV -Path $CheckpointFile -NoTypeInformation
        return $firstStartTimeRecord
    }
    else {
        $GetLastRecordTime = Import-Csv -Path $CheckpointFile
        $startTime = $GetLastRecordTime | ForEach-Object{
                        if($_.Key -eq 'LastSuccessfulTime'){
                            $_.Value
                        }
                    }
        return $startTime
    }
}


# Function to update the checkpoint time with the last successful API call end time
function UpdateCheckpointTime($CheckpointFile, $LastSuccessfulTime){
    $checkpoints = Import-Csv -Path $CheckpointFile
    $checkpoints | ForEach-Object{ if($_.Key -eq 'LastSuccessfulTime'){$_.Value = $LastSuccessfulTime.ToString("yyyy-MM-ddTHH:mm:ssZ")}}
    $checkpoints | Select-Object -Property Key,Value | Export-CSV -Path $CheckpointFile -NoTypeInformation
}

function UrlValidation{
    Param(
        [ValidatePattern('^https:\/\/qualysapi.([\w\.]+)\/api\/2.0$')]
        [string]$Uri
    )
    return $true
}

function QualysKB {

    $cwd = (Get-Location).Drive.Root
    $CheckpointFile = "$($cwd)home\site\QualysKBCheckpoint.csv"
    $endTime = [datetime]::UtcNow
    $customerId = $env:workspaceId
    $sharedKey = $env:workspacekey
    $username = [uri]::EscapeDataString($env:apiUsername)
    $password = [uri]::EscapeDataString($env:apiPassword)
    $tableName = "QualysKB"
    $timeInterval = 5
    $filterparameters = $env:filterParameters
    $Uri = $env:Uri

    if ([string]::IsNullOrEmpty($logAnalyticsUri))
    {
        $logAnalyticsUri = "https://" + $customerId + ".ods.opinsights.azure.com"
    }

    # Returning if the Log Analytics Uri is in incorrect format.
    # Sample format supported: https://" + $customerId + ".ods.opinsights.azure.com
    if($logAnalyticsUri -notmatch 'https:\/\/([\w\-]+)\.ods\.opinsights\.azure.([a-zA-Z\.]+)$')
    {
        throw "Qualys KB: Invalid Log Analytics Uri."
    }

    # Validate Uri
    $UriValidation = UrlValidation -Uri $Uri
    if($null -eq $UriValidation){
        Write-Output "ERROR: Invalid URI format detected. Validated URI format before next execution. Function exiting..."
        exit
    }

    # If filter parameters are defined, add a "&" prefix
    if($filterparameters -ne ""){
        $filterparameters = "&$filterparameters"
    }

    $startDate = GetStartTime -CheckpointFile $CheckPointFile  -timeInterval $timeInterval
    $hdrs = @{"X-Requested-With"="powershell"}
    $base = "$Uri/fo"
    $body = "action=login&username=$username&password=$password"

    Try {
        Invoke-RestMethod -Headers $hdrs -Uri "$base/session/" -Method Post -Body $body -SessionVariable sess
    }
    catch {
        Write-Host "Error in initializing session StatusCode:" $_.Exception.Response.StatusCode.value__
        Write-Error -Message $_.Exception.Message
    }

    Write-Host "Start Time :" $($startDate)
    Write-Host " UTC current Time :" [datetime]::UtcNow
    Write-Host "Constructed URL : $base/knowledge_base/vuln/?action=list&published_after=$($startDate)$filterparameters"

    $response = Try {
        Invoke-RestMethod -Headers $hdrs -Uri "$base/knowledge_base/vuln/?action=list&published_after=$($startDate)$filterparameters" -WebSession $sess
    }
    catch {
        Write-Host "StatusCode:" $_.Exception.Response.StatusCode.value__
        Write-Error -Message $_.Exception.Message
    }
    # Really simple error check, if we get a 200 return the bearer token, ortherwise return false

    if($null -ne $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN){
        Write-Host "Number of records returned after published Date $($startDate) : " $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN.Length
        try {
            # Iterate through each vulnerability recieved from the API call and assign the variables (Column Names in LA) to each XML variable and place each vulnerability as an object in the $objs array.
            $objs = @()
            0 .. $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN.Length | ForEach-Object {
                if($null -eq $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].QID) {     # if the vuln ID is mull which will mean the entry is null, this occurs on the last entry of the response. Should only occur once.
                    Write-Host "A null line was excluded"
                }
                else {
                    $DiagnosisParsed = Html-ToText($response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].DIAGNOSIS."#cdata-section")
                    $ConsequenceParsed = Html-ToText($response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].CONSEQUENCE."#cdata-section")
                    $SolutionParsed = Html-ToText($response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].SOLUTION."#cdata-section")

                    $obj = @{'QID'= $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].QID
                    'Title' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].TITLE."#cdata-section"
                    'Category' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].CATEGORY
                    'Consequence' = $ConsequenceParsed
                    'Diagnosis' = $DiagnosisParsed
                    'Last_Service_Modification_DateTime' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].LAST_SERVICE_MODIFICATION_DATETIME
                    'Patchable' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].PATCHABLE
                    'CVE_ID' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].CVE_LIST.CVE.ID."#cdata-section"
                    'CVE_URL' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].CVE_LIST.CVE.URL."#cdata-section"
                    'Vendor_Reference_ID' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].VENDOR_REFERENCE_LIST.VENDOR_REFERENCE.ID."#cdata-section"
                    'Vendor_Reference_URL' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].VENDOR_REFERENCE_LIST.VENDOR_REFERENCE.URL."#cdata-section"
                    'PCI_Flag' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].PCI_FLAG
                    'Published_DateTime' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].PUBLISHED_DATETIME
                    'Severity_Level' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].SEVERITY_LEVEL
                    'Software_Product' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].SOFTWARE_LIST.SOFTWARE.PRODUCT."#cdata-section"
                    'Software_Vendor' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].SOFTWARE_LIST.SOFTWARE.VENDOR."#cdata-section"
                    'Solution' = $SolutionParsed
                    'Vuln_Type' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].VULN_TYPE
                    'Discovery_Additional_Info' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].DISCOVERY.ADDITIONAL_INFO
                    'Discovery_Auth_Type' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].DISCOVERY.AUTH_TYPE_LIST.AUTH_TYPE
                    'Discovery_Remote' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].DISCOVERY.REMOTE
                    'THREAT_INTELLIGENCE' = $response.KNOWLEDGE_BASE_VULN_LIST_OUTPUT.RESPONSE.VULN_LIST.VULN[$_].THREAT_INTELLIGENCE.THREAT_INTEL | Select-Object id, "#cdata-section" | ConvertTo-Json
                    }

                $objs += $obj
                Write-Host "Individual Object is processed and assigned to Array"

                }
            }

            Write-Host "Number of Objects processed : " $objs.Length

        # Logout of the Session
        Invoke-RestMethod -Headers $hdrs -Uri "$base/session/" -Method Post -Body "action=logout" -WebSession $sess

        # Iterate through each vulnerabilty obj in the $objs array, covert it to JSON and POST it to the Log Analytics API individually
        $startInterval = $startDate
        $endInterval = $endTime.ToString("yyyy-MM-ddTHH:mm:ssZ")
        $objsLength = $objs.Length
        if ($objs.Length -ne 0){
            $jsonPayload = $objs | ConvertTo-Json
            $mbytes = ([System.Text.Encoding]::UTF8.GetBytes($objs)).Count/1024/1024
            # Check the payload size, if under 30MB post to Log Analytics.
            if (($mbytes -le 30)){
                $responseCode = Post-LogAnalyticsData -customerId $customerId -sharedKey $sharedKey -body ([System.Text.Encoding]::UTF8.GetBytes($jsonPayload)) -logType $tablename

                if ($responseCode -ne 200){
                    Write-Error -Message "ERROR: Log Analytics POST, Status Code: $responseCode, unsuccessful."
                }
                else {
                    Write-Host "SUCCESS: $objsLength Qualys KB vulnerability records found between $startInterval and $endInterval and posted to Log Analytics: $mbytes MB" -ForegroundColor Green
                    UpdateCheckpointTime -CheckpointFile $checkPointFile -LastSuccessfulTime $endTime
                }
            }
            else {
                Write-Error "ERROR: Log Analytics POST failed due to paylog exceeding 30Mb: $mbytes"
                }
            }
            else {
            Write-Host INFO: "No new Qualys KB vulnerability records between $startInterval and $endInterval"
            # UpdateCheckpointTime -CheckpointFile $checkPointFile -LastSuccessfulTime $endTime
            }

        }
        catch {
            Write-Host "Error in initializing session StatusCode:" $_.Exception.Response.StatusCode.value__
            Write-Error -Message $_.Exception.Message
        }
    }
    else {
         # Logout of the Session
        Invoke-RestMethod -Headers $hdrs -Uri "$base/session/" -Method Post -Body "action=logout" -WebSession $sess
        $endInterval = $endTime.ToString("yyyy-MM-ddTHH:mm:ssZ")
        # UpdateCheckpointTime -CheckpointFile $checkPointFile -LastSuccessfulTime $endTime
        Write-Host "INFO: No new Qualys KB vulnerability records between $startDate and $endInterval"
    }
 }


# Function to build the authorization signature to post to Log Analytics
function Build-Signature ($customerId, $sharedKey, $date, $contentLength, $method, $contentType, $resource)
{
    $xHeaders = "x-ms-date:" + $date;
    $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $resource;
    $bytesToHash = [Text.Encoding]::UTF8.GetBytes($stringToHash);
    $keyBytes = [Convert]::FromBase64String($sharedKey);
    $sha256 = New-Object System.Security.Cryptography.HMACSHA256;
    $sha256.Key = $keyBytes;
    $calculatedHash = $sha256.ComputeHash($bytesToHash);
    $encodedHash = [Convert]::ToBase64String($calculatedHash);
    $authorization = 'SharedKey {0}:{1}' -f $customerId,$encodedHash;
    return $authorization;
}

# Function to POST the data payload to a Log Analytics workspace
function Post-LogAnalyticsData($customerId, $sharedKey, $body, $logType)
{
    $TimeStampField = "DateValue"
    $method = "POST";
    $contentType = "application/json";
    $resource = "/api/logs";
    $rfc1123date = [DateTime]::UtcNow.ToString("r");
    $contentLength = $body.Length;
    $signature = Build-Signature -customerId $customerId -sharedKey $sharedKey -date $rfc1123date -contentLength $contentLength -method $method -contentType $contentType -resource $resource;
    $logAnalyticsUri = $logAnalyticsUri + $resource + "?api-version=2016-04-01"

    $headers = @{
        "Authorization" = $signature;
        "Log-Type" = $logType;
        "x-ms-date" = $rfc1123date;
        "time-generated-field" = $TimeStampField;
    };
    $response = Invoke-WebRequest -Body $body -Uri $logAnalyticsUri -Method $method -ContentType $contentType -Headers $headers -UseBasicParsing
    return $response.StatusCode
}

QualysKB

# Write an information log with the current time.
Write-Host "PowerShell timer trigger function ran! TIME: $currentUTCtime"
