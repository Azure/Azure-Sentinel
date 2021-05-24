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
#
# This example demonstrates how to process an S3 Event that follows the process:
# S3 Event -> SNS Topic -> Lambda Function

#Requires -Modules @{ModuleName='AWS.Tools.Common';ModuleVersion='4.1.5.0'}
#Requires -Modules @{ModuleName='AWS.Tools.S3';ModuleVersion='4.1.5.0'}
#Requires -Modules @{ModuleName='AWS.Tools.SecretsManager';ModuleVersion='4.1.5.0'}

# Uncomment to send the input event to CloudWatch Logs
#Write-Host (ConvertTo-Json -InputObject $LambdaInput -Compress -Depth 5)
#$PSVersionTable

# Get the current universal time in the default string format.
$currentUTCtime = (Get-Date).ToUniversalTime()

# Code to retrieve credentials from AWS Secrets Manager
$secretName = $env:SecretName
$secretValue = ConvertFrom-Json (Get-SECSecretValue -SecretId $secretName -ErrorAction Stop -Verbose).SecretString -ErrorAction Stop

$workspaceId = $secretValue.LAWID
$workspaceKey = $secretValue.LAWKEY
$LATableName = $env:LogAnalyticsTableName
$IsCoreFieldsAllTable = $env:CoreFieldsAllTable
$IsSplitAWSResourceTypes = $env:SplitAWSResourceTypeTables
$ResourceID = ''  

#The $eventobjectlist is the Json Parameter field names that form the core of the Json message that we want in the ALL Table in Log Ananlytics
$eventobjectlist = @('eventTime', 'eventVersion', 'userIdentity', 'eventSource', 'eventName', 'awsRegion', 'sourceIPAddress', 'userAgent', 'errorCode', 'errorMessage', 'requestID', 'eventID', 'eventType', 'apiVersion', 'managementEvent', 'readOnly', 'resources', 'recipientAccountId', 'serviceEventDetails', 'sharedEventID', 'vpcEndpointId', 'eventCategory', 'additionalEventData')


Function Expand-GZipFile {
    Param(
        $infile,
        $outfile       
    )
	Write-Host "Processing Expand-GZipFile for: infile = $infile, outfile = $outfile"
    $inputfile = New-Object System.IO.FileStream $infile, ([IO.FileMode]::Open), ([IO.FileAccess]::Read), ([IO.FileShare]::Read)	
    $output = New-Object System.IO.FileStream $outfile, ([IO.FileMode]::Create), ([IO.FileAccess]::Write), ([IO.FileShare]::None)	
    $gzipStream = New-Object System.IO.Compression.GzipStream $inputfile, ([IO.Compression.CompressionMode]::Decompress)	
	
    $buffer = New-Object byte[](1024)	
    while ($true) {
        $read = $gzipstream.Read($buffer, 0, 1024)		
        if ($read -le 0) { break }		
		$output.Write($buffer, 0, $read)		
	}
	
    $gzipStream.Close()
    $output.Close()
    $inputfile.Close()
}

#function to create HTTP Header signature required to authenticate post
Function New-BuildSignature {
    param(
        $customerId, 
        $sharedKey, 
        $date, 
        $contentLength, 
        $method, 
        $contentType, 
        $resource )
    
    $xHeaders = "x-ms-date:" + $date
    $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $resource
    $bytesToHash = [Text.Encoding]::UTF8.GetBytes($stringToHash)
    $keyBytes = [Convert]::FromBase64String($sharedKey)
    $sha256 = New-Object System.Security.Cryptography.HMACSHA256
    $sha256.Key = $keyBytes
    $calculatedHash = $sha256.ComputeHash($bytesToHash)
    $encodedHash = [Convert]::ToBase64String($calculatedHash)
    $authorization = 'SharedKey {0}:{1}' -f $customerId, $encodedHash
    return $authorization
}
        
# Function to create and post the request
Function Invoke-LogAnalyticsData {
    Param( 
        $CustomerId, 
        $SharedKey, 
        $Body, 
        $LogTable, 
        $TimeStampField,
        $resourceId)

    $method = "POST"
    $contentType = "application/json"
    $resource = "/api/logs"
    $rfc1123date = [DateTime]::UtcNow.ToString("r")
    $contentLength = $Body.Length
    $signature = New-BuildSignature `
        -customerId $CustomerId `
        -sharedKey $SharedKey `
        -date $rfc1123date `
        -contentLength $contentLength `
        -method $method `
        -contentType $contentType `
        -resource $resource
    $uri = "https://" + $CustomerId + ".ods.opinsights.azure.com" + $resource + "?api-version=2016-04-01"
    $headers1 = @{
        "Authorization"        = $signature;
        "Log-Type"             = $LogTable;
        "x-ms-date"            = $rfc1123date;
        "x-ms-AzureResourceId" = $resourceId;
        "time-generated-field" = $TimeStampField;
    }  
    $status = $false
    do {
        $response = Invoke-WebRequest -Uri $uri -Method $method -ContentType $contentType -Headers $headers1 -Body $Body
		#If requests are being made at a rate higher than this, then these requests will receive HTTP status code 429 (Too Many Requests) along with the Retry-After: 
		#<delta-seconds> header which indicates the number of seconds until requests to this application are likely to be accepted.If requests are being made at a rate higher than this, 
		#then these requests will receive HTTP status code 429 (Too Many Requests) along with the Retry-After: <delta-seconds> header which indicates the number of seconds until requests to this application are likely to be accepted.																																				  
        If ($reponse.StatusCode -eq 429) {
            $rand = get-random -minimum 10 -Maximum 80
            start-sleep -seconds $rand 
        }
        else { $status = $true }
    }until($status) 
    Remove-variable -name Body
    return $response.StatusCode
    
}


Function Ingest-Core-Fields-Single-Table {
	Param(
	$coreEvents)
	
	$coreJson = convertto-json $coreEvents -depth 5 -Compress    
	$Table = "$LATableName" + "_All"
	IF (($corejson.Length) -gt 28MB) {
		Write-Host "Log length is greater than 28 MB, splitting and sending to Log Analytics"
		$bits = [math]::Round(($corejson.length) / 20MB) + 1
		$TotalRecords = $coreEvents.Count
		$RecSetSize = [math]::Round($TotalRecords / $bits) + 1
		$start = 0
		For ($x = 0; $x -lt $bits; $x++) {
			IF ( ($start + $recsetsize) -gt $TotalRecords) {
				$finish = $totalRecords
			}
			ELSE {
				$finish = $start + $RecSetSize
			}
			$body = Convertto-Json ($coreEvents[$start..$finish]) -Depth 5 -Compress
			$result = Invoke-LogAnalyticsData -CustomerId $workspaceId -SharedKey $workspaceKey -Body $body -LogTable $Table -TimeStampField 'eventTime' -ResourceId $ResourceID          
			if ($result -eq 200)
			{
				Write-Host "CloudTrail Logs successfully ingested to LogAnalytics Workspace under Custom Logs --> Table: $Table"
			}
			$start = $finish + 1
		}
		$null = Remove-variable -name body        

	}
	Else {
		#$logEvents = Convertto-Json $events -depth 20 -compress
		$result = Invoke-LogAnalyticsData -CustomerId $workspaceId -SharedKey $workspaceKey -Body $coreJson -LogTable $Table -TimeStampField 'eventTime' -ResourceId $ResourceID
		if ($result -eq 200)
		{
			Write-Host "CloudTrail Logs successfully ingested to LogAnalytics Workspace under Custom Logs --> Table: $Table"
		}
	}

	$null = remove-variable -name coreEvents
	$null = remove-variable -name coreJson
}


Function Ingest-AWS-ResourceType-Multi-Tables {
	Param(
	$eventSources,
	$groupEvents)
	
	$RecCount = 0
	foreach ($d in $eventSources) { 
		#$events = $groupevents[$d]
		$eventsJson = ConvertTo-Json $groupEvents[$d] -depth 5 -Compress
		$Table = $LATableName + '_' + $d
		$TotalRecords = $groupEvents[$d].Count
		$recCount += $TotalRecords
		IF (($eventsjson.Length) -gt 28MB) {
			#$events = Convertfrom-json $corejson
			$bits = [math]::Round(($eventsjson.length) / 20MB) + 1
			$TotalRecords = $groupEvents[$d].Count
			$RecSetSize = [math]::Round($TotalRecords / $bits) + 1
			$start = 0
			For ($x = 0; $x -lt $bits; $x++) {
				IF ( ($start + $recsetsize) -gt $TotalRecords) {
					$finish = $totalRecords
				}
				ELSE {
					$finish = $start + $RecSetSize
				}
				$body = Convertto-Json ($groupEvents[$d][$start..$finish]) -Depth 5 -Compress
				$result = Invoke-LogAnalyticsData -CustomerId $workspaceId -SharedKey $workspaceKey -Body $body -LogTable $Table -TimeStampField 'eventTime' -ResourceId $ResourceID                
				if ($result -eq 200)
				{
					Write-Host "CloudTrail Logs successfully ingested to LogAnalytics Workspace under Custom Logs --> Table: $Table"
				}
				$start = $finish + 1
			}
			$null = Remove-variable -name body        
		}
		Else {
			#$logEvents = Convertto-Json $events -depth 20 -compress
			$result = Invoke-LogAnalyticsData -CustomerId $workspaceId -SharedKey $workspaceKey -Body $eventsJson -LogTable $Table -TimeStampField 'eventTime' -ResourceId $ResourceID
			if ($result -eq 200)
			{
				Write-Host "CloudTrail Logs successfully ingested to LogAnalytics Workspace under Custom Logs --> Table: $Table"
			}
		}
	}
	
}

foreach ($sqsRecord in $LambdaInput.Records)
{    
	$sqsRecordBody = ConvertFrom-Json -InputObject $sqsRecord.body
    foreach ($s3Event in $sqsRecordBody.Records)
    {
        $s3BucketName = $s3Event.s3.bucket.name
        $s3BucketKey = $s3Event.s3.object.key

        Write-Host "Processing event for: bucket = $s3BucketName, key = $s3BucketKey"
	
		IF ($Null -ne $s3BucketName -and $Null -ne $s3BucketKey) {
			$s3KeyPath = $s3BucketKey -Replace ('%3A', ':')			
			$fileNameSplit = $s3KeyPath.split('/')			
			$fileSplits = $fileNameSplit.Length - 1			
			$fileName = $filenameSplit[$fileSplits].replace(':', '_')			
			$downloadedFile = Read-S3Object -BucketName $s3BucketName -Key $s3BucketKey -File "/tmp/$filename"			
			Write-Host "Object $s3BucketKey is $($downloadedFile.Size) bytes; Extension is $($downloadedFile.Extension)"
			
			IF ($downloadedFile.Extension -eq '.gz' ) {
				$infile = "/tmp/$filename"				
				$outfile = "/tmp/" + $filename -replace ($downloadedFile.Extension, '')					
				Expand-GZipFile $infile.Trim() $outfile.Trim()
				$null = Remove-Item -Path $infile -Force -Recurse -ErrorAction Ignore
				$filename = $filename -replace ($downloadedFile.Extension, '')
				$filename = $filename.Trim()
			
    
				$logEvents = Get-Content -Raw -LiteralPath ("/tmp/$filename" ) 
				$logEvents = $LogEvents.Substring(0, ($LogEvents.length) - 1)
				$LogEvents = $LogEvents -Replace ('{"Records":', '')
				$loglength = $logEvents.Length    
				$logevents = Convertfrom-json $LogEvents -AsHashTable
				$groupevents = @{}
				$coreEvents = @()
				$eventSources = @()
				Foreach ($log in $logevents) {
					$Logdetails = @{}
					$Logdetails1 = @{}
					$b = ((($log.eventSource).split('.'))[0]) -replace ('-', '')
					IF ($b -eq 'ec2') {
						foreach ($col in $eventobjectlist) {
							$logdetails1 += @{$col = $log.$col }
						}
						$ec2Header = $b + '_Header'
						IF ($null -eq $groupevents[$ec2Header]) {
							Add-Member -inputobject $groupevents -Name $b -MemberType NoteProperty -value @() -Force
							$groupevents[$ec2Header] = @()
							$eventSources += $ec2Header
						}
						$groupevents[$ec2Header] += $Logdetails1
						$Ec2Request = $b + '_Request'
						IF ($null -eq $groupevents[$Ec2Request]) {
							Add-Member -inputobject $groupevents -Name $Ec2Request -MemberType NoteProperty -value @() -Force
							$groupevents[$Ec2Request] = @()
							$eventSources += $Ec2Request
						}
						$ec2Events = @{} 
						$ec2Events += @{'eventID' = $log.eventID }
						$ec2Events += @{'awsRegion' = $log.awsRegion }
						$ec2Events += @{'requestID' = $log.requestID }
						$ec2Events += @{'eventTime' = $log.eventTime }
						$ec2Events += @{'requestParameters' = $log.requestParameters }
						$groupevents[$Ec2Request] += $ec2Events
						$Ec2Response = $b + '_Response'
						IF ($null -eq $groupevents[$Ec2Response]) {
							Add-Member -inputobject $groupevents -Name $Ec2Response -MemberType NoteProperty -value @() -Force
							$groupevents[$Ec2Response] = @()
							$eventSources += $Ec2Response
						}
						$ec2Events = @{} 
						$ec2Events += @{'eventID' = $log.eventID }
						$ec2Events += @{'awsRegion' = $log.awsRegion }
						$ec2Events += @{'requestID' = $log.requestID }
						$ec2Events += @{'eventTime' = $log.eventTime }
						$ec2Events += @{'responseElements' = $log.responseElements }
						$groupevents[$Ec2Response] += $ec2Events
					}
					Else {
						IF ($null -eq $groupevents[$b]) {
							Add-Member -inputobject $groupevents -Name $b -MemberType NoteProperty -value @() -Force
							$groupevents[$b] = @()
							$eventSources += $b
						}
						$groupevents[$b] += $log
					}
					foreach ($col in $eventobjectlist) {
						$logdetails += @{$col = $log.$col }
					}
					$coreEvents += $Logdetails
				
				}

				IF ($IsCoreFieldsAllTable -eq "true" -and $IsSplitAWSResourceTypes -eq "true") {
					Ingest-Core-Fields-Single-Table -CoreEvents $coreEvents
					Ingest-AWS-ResourceType-Multi-Tables -EventSources $eventSources -GroupEvents $groupevents
				}
				ELSEIF ($IsCoreFieldsAllTable -eq "true" -and $IsSplitAWSResourceTypes -eq "false"){
					Ingest-Core-Fields-Single-Table -CoreEvents $coreEvents
				}
				ELSEIF ($IsCoreFieldsAllTable -eq "false" -and $IsSplitAWSResourceTypes -eq "true"){
					Ingest-AWS-ResourceType-Multi-Tables -EventSources $eventSources -GroupEvents $groupevents
				}
				ELSE {
					Write-Host "Make sure you have correct values supplied in Environment Variables for CoreFieldsAllTable and SplitAWSResourceTypeTables"
				}
				
				$null = Remove-Variable -Name groupevents
				$null = Remove-Variable -Name LogEvents
			}
			ELSEIF ($downloadedFile.Extension -eq '.json'){
				$coreEvents = Get-Content -Raw -LiteralPath ("/tmp/$filename") | ConvertFrom-Json
				Ingest-Core-Fields-Single-Table -CoreEvents $coreEvents
			}
			ELSEIF ($downloadedFile.Extension -eq '.csv'){
				$coreEvents = import-csv "/tmp/$filename"
				Ingest-Core-Fields-Single-Table -CoreEvents $coreEvents
			}
		}
	}
}