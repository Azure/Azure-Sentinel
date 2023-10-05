<#
.Synopsis
   Script that hydrates a given Log Analytics workspace with data for use with Sentinel for SAP solution
.DESCRIPTION
   Script iterates through folders in scenarios subfolder and for each scenario posts data to supplied Log Analytics workspace
   Script replaces markers {{}} with data supplied in replacements.json (global list of markers) and metadata.json
   Script skips folders that have .processed file in it
   Replacements.json format: 
   array of elements in the following form:
   {
			"ReplacementName":"MarkerScriptLooksForIntheCSVFile",
			"ReplacementValueScriptBlock":"EscapedPowershellScriptBlockReturningDesiredValue",
			"ReplacementValue":"Leave Empty"
   }
   sample:
   {
			"ReplacementName":"TargetUserName4",
			"ReplacementValueScriptBlock":"\"User\"+((Get-Random 90000)+10000)",
			"ReplacementValue":""
	}
    Above scriptblock returns string User followed by a random 5 digit number, but can be any powershell scriptblock
   
    metadata.json format:
   {
	"Message":"Descriptive message of the scenario that is being processed",
	"ID":"Unused, but set to some integer value",
	"RunCount":"Amount of Iterations to process each of the CSV files in the folder",
	"Replacements":[
		<array of replacements in same format as metadata.json
        for metadata.json, ReplacementValueScriptBlock can take arguments too
        {
			"ReplacementName":"SampleParametrized",
			"ReplacementValueScriptBlock":"param($param) Get-Random $param",
			"ReplacementValue":""
		}
	],
    "Arguments":
	[
		{"RandomizerSeed":"Get-Random"}
        List of arguments that will be passed to the scriptblock
	]
}
.EXAMPLE
   Hydrate-LogAnalytics -LogAnalyticsWorkspaceID "YourLogAnalyticsWorkspaceIDHere" -LogAnalyticsWorkspaceKey "YourLogAnalyticsWorspacePrimaryOrSecondaryKeyHere"
.PARAMETER  LogAnalyticsWorkspaceID
   Log Analytics workspace ID (GUID string)
.PARAMETER  LogAnalyticsWorkspaceKey
   Log Analytics workspace primary or secondary access key
#>

[CmdletBinding(   SupportsShouldProcess=$false, 
                  PositionalBinding=$false,
                  HelpUri = 'http://www.microsoft.com/',
                  ConfirmImpact='Medium')]
    [Alias()]
    Param
    (
        [Parameter(Mandatory=$true, 
                   HelpMessage="ID of the Log Analytics workspace",
                   ValueFromPipeline=$true,
                   ValueFromPipelineByPropertyName=$true, 
                   ValueFromRemainingArguments=$false, 
                   Position=0)
                   ]
        [ValidateNotNull()]
        [ValidateNotNullOrEmpty()]
        [ValidateScript({
                        if ($null -ne [guid]$_)
                        {$true}
                        else {
                            throw "$_ is an invalid value. Expected the ID of the Log Analytics workspace (GUID)"
                        }
                        })
        ]
        [string]
        $LogAnalyticsWorkspaceID,

        [Parameter(Mandatory=$true, 
                   HelpMessage="Primary or secondary access key of the Log Analytics workspace",
                   ValueFromPipeline=$true,
                   ValueFromPipelineByPropertyName=$true, 
                   ValueFromRemainingArguments=$false, 
                   Position=1)
                   ]
        [ValidateNotNull()]
        [ValidateNotNullOrEmpty()]
        [ValidateScript({
                        if ($null -ne [System.Convert]::FromBase64String($_))
                        {
                            $true
                        }
                        else {
                            throw "$_ is an invalid value. Check the supplied"
                        }                    
                    })]
        [string]
        $LogAnalyticsWorkspaceKey,

        [Parameter(Mandatory=$false, 
                   HelpMessage="URI location of the settings.json file",
                   ValueFromPipeline=$true,
                   ValueFromPipelineByPropertyName=$true, 
                   ValueFromRemainingArguments=$false, 
                   Position=2)
                   ]
        [ValidateNotNull()]
        [ValidateNotNullOrEmpty()]
        [string]
        $ConfigURI="https://raw.githubusercontent.com/Azure/Azure-Sentinel/master/Solutions/SAP/Demo/settings.json"
    )

Function Build-Signature ($customerId, $LogAnalyticsWorkspaceKey, $date, $contentLength, $method, $contentType, $resource) {
    $xHeaders = "x-ms-date:" + $date
    $stringToHash = $method + "`n" + $contentLength + "`n" + $contentType + "`n" + $xHeaders + "`n" + $resource

    $bytesToHash = [Text.Encoding]::UTF8.GetBytes($stringToHash)
    $keyBytes = [Convert]::FromBase64String($LogAnalyticsWorkspaceKey)

    $sha256 = New-Object System.Security.Cryptography.HMACSHA256
    $sha256.Key = $keyBytes
    $calculatedHash = $sha256.ComputeHash($bytesToHash)
    $encodedHash = [Convert]::ToBase64String($calculatedHash)
    $authorization = 'SharedKey {0}:{1}' -f $customerId, $encodedHash
    return $authorization
}
Function Post-LogAnalyticsData($LogAnalyticsWorkspaceID, $LogAnalyticsWorkspaceKey, $object, $logTableName, $TimeStampField) {
    $method = "POST"
    $contentType = "application/json"
    $resource = "/api/logs"
    $rfc1123date = [DateTime]::UtcNow.ToString("r")
    
    $bodyAsJson = ConvertTo-Json $object
    $body = [System.Text.Encoding]::UTF8.GetBytes($bodyAsJson)
    
    $contentLength = $body.Length
    $signature = Build-Signature `
        -customerId $LogAnalyticsWorkspaceID `
        -LogAnalyticsWorkspaceKey $LogAnalyticsWorkspaceKey `
        -date $rfc1123date `
        -contentLength $contentLength `
        -method $method `
        -contentType $contentType `
        -resource $resource
    $uri = "https://" + $LogAnalyticsWorkspaceID + ".ods.opinsights.azure.com" + $resource + "?api-version=2016-04-01"

    $headers = @{
        "Authorization"        = $signature;
        "Log-Type"             = $logTableName;
        "x-ms-date"            = $rfc1123date;
        "time-generated-field" = $TimeStampField;
    }
    $response = Invoke-WebRequest -Uri $uri -Method $method -ContentType $contentType -Headers $headers -Body $body -UseBasicParsing
    if ($response.StatusCode -ne 200) {
        Write-Warning "Error while posting to log analytics. logTableName: $logTableName"
    }    
}
Function Get-SampleMetadata {
    param (
        [Parameter(Mandatory = $false, ValueFromPipeline = $true)]
        [string]
        $location)
    process {
            $metadata = Get-WebContent -URI ($location,"metadata.json" -join "/") | ConvertFrom-Json
            return $metadata
    }
}

Function Cleanup-Line {
    param ($line)
    process {
        $line.psobject.Members.Remove("TenantId")
        $line.psobject.Members.Remove("SourceSystem")
        $line.psobject.Members.Remove("MG")
        $line.psobject.Members.Remove("ManagementGroupName")
        $line.psobject.Members.Remove("Computer")
        $line.psobject.Members.Remove("RawData")
        $line.psobject.Members.Remove("_ResourceId")
        $line.psobject.Members.Remove("Type")
        if ($null -ne $line.TimeGenerated) {
            $lineTimeStamp = $line.TimeGenerated
            $line.psobject.Members.Remove("TimeGenerated")

        }
        elseif ($null -ne $line.'TimeGenerated [UTC]') {
            $lineTimeStamp = $line.'TimeGenerated [UTC]'
            $line.psobject.Members.Remove("TimeGenerated [UTC]")
        }
        Add-Member -InputObject $line -MemberType NoteProperty -Name RecordTime -Value ($lineTimeStamp)
        #return $line
    }
}
Function Init-Replacements {
    param ($Replacements)
    foreach ($replacement in $Replacements.GetEnumerator()) {
        if ($null -eq $replacement.Value.ReplacementValueSB) {
            $scriptBlock = [scriptblock]::Create($replacement.Value.ReplacementValueScriptBlock)
            $replacement.Value.ReplacementValueSB = $scriptBlock
        }
    }
}
Function Compute-Replacements {
    param (
        $localReplacements,
        $globalReplacements,
        $arguments
    )
    $sbarguments = @{}
    if ($null -ne $arguments)
    {
        foreach ($argument in $arguments)
        {
            $element=$argument.psobject.Members.Where({$_.MemberType -eq "NoteProperty"})
            $sbarguments.Add($element.Name,(&([scriptblock]::Create($element.value))))
        }
    }
    $replacements = $localReplacements + $globalReplacements
    foreach ($replacement in $replacements.GetEnumerator()) {
        if ($null -ne $replacement.Value.ReplacementValueSB) {
            #$scriptBlock = [scriptblock]::Create($replacement.Value.ReplacementValueScriptBlock)
            $replacement.Value.ReplacementValue = &$replacement.Value.ReplacementValueSB @sbarguments
        }
        else {
            $replacement.Value.ReplacementValue = &([scriptblock]::Create($replacement.Value.ReplacementValueScriptBlock)) @sbarguments
        }
    }
    return $replacements
}
Function Make-LineReplacements {
    param (
        $line,
        $replacements
    )
    process {        
        foreach ($property in ($line.psobject.Members.Where({ ($_.MemberType -eq "NoteProperty") -and ($_.Value -match "{{.*}}") }))) {
            $property.Value | Select-String -pattern "{{(.*?)}}" -AllMatches |
            ForEach-Object { $_.Matches } |
            Foreach-Object {
                $property.Value = $property.Value.Replace($_.Groups[0].Value, $replacements.($_.Groups[1].Value).ReplacementValue)
            }
        }
        return $line
    }
}
Function Get-WebContent
{
    param(
        $URI
    )
    begin
    {
        try
        {
            $response = Invoke-WebRequest -Uri $URI -UseBasicParsing -ErrorAction SilentlyContinue -Headers @{"Cache-Control"="no-cache"}
            if ($response.StatusCode -eq 200)
            {
                return $response.Content
            }
            else {
                throw "Received invalid status code while retreiving content from URL $URI. Code $($response.StatusCode)"
            }
        }
        catch [System.Net.WebException]
        {
            if ($_.Exception.Response.StatusCode.value__ -eq 404)
            {
                return $false
            }
        }
    }
}
$Config = Get-WebContent $ConfigURI | ConvertFrom-Json

$globalReplacementsarr = Get-WebContent -Uri ($config.Base,"replacements.json" -join "/") -Raw | ConvertFrom-Json
$globalReplacements = @{}
foreach ($gr in $globalReplacementsarr) {
    $globalReplacements.Add($gr.ReplacementName, @{ReplacementValueScriptBlock = ($gr.ReplacementValueScriptBlock); ReplacementValue = ($gr.ReplacementValue) })
}
Init-Replacements -Replacements $globalReplacements

foreach ($scenario in $config.Scenarios) {
    if (Get-WebContent ($Config.Base,"scenarios",$scenario,".processed" -join "/")) {
        continue
    }
    $metadata = Get-SampleMetadata -location ($Config.Base,"scenarios",$scenario -join "/")
    if ($null -ne $metadata.RunCount) { $RunCount = $metadata.RunCount }
    else { $RunCount = 1 }
    if ($null -ne $metadata.Replacements) { $localReplacementsarr = $metadata.Replacements }
    else { $localReplacementsarr = @() }
    $localReplacements = @{}
    foreach ($lr in $localReplacementsarr) {
        $localReplacements.Add($lr.ReplacementName, @{ReplacementValueScriptBlock = ($lr.ReplacementValueScriptBlock); ReplacementValue = ($lr.ReplacementValue) })
    }
    Init-Replacements -Replacements $localReplacements    

    $outLines = New-Object 'system.collections.generic.dictionary[string,System.Collections.ArrayList]'
    $inLines = New-Object 'system.collections.generic.dictionary[string,PSCustomObject]'

    foreach ($samplefile in $metadata.Files) {
        $tablename = $samplefile.Split('.')[0]
        $data = (Get-WebContent -Uri ($config.Base,"scenarios",$scenario,$samplefile -join "/")).Split("`r")
        if (-not $data)
        {
            throw "Invalid data received for scenario $scenario sample file $samplefile"
        }
        if ($data[0].Contains("_s`"")) {
            $data[0] = $data[0].Replace("_s`"", "`"")
        }
        $currentCSV = ConvertFrom-Csv $data
        foreach ($line in $currentCSV) {
            Cleanup-Line -line $line
        }
        $inLines.Add($samplefile, $currentCSV)
    }

    for ($i = 0; $i -lt $metadata.RunCount; $i++) {
        $replacements = Compute-Replacements -globalReplacements $globalReplacements -localReplacements $localReplacements -arguments $metadata.Arguments
        foreach ($file in $inLines.Keys) {
            foreach ($line in $inLines[$file]) {
                $newline = $line.psobject.copy()
                $newline = (Make-LineReplacements -line $newline -replacements $replacements -arguments )
                if (-not $outLines.ContainsKey($file)) {
                    $outLines.Add($file, (New-Object System.Collections.ArrayList)) | Out-Null
                }
                $outLines[$file].Add($newline) | Out-Null
                if ($outlines[$file].Count -ge 1000) {
                    Write-Host "Processing $file; Importing $($metadata.Message), Iteration $i of $RunCount"
                    $runparams = @{
                        LogAnalyticsWorkspaceID = $LogAnalyticsWorkspaceID
                        LogAnalyticsWorkspaceKey= $LogAnalyticsWorkspaceKey
                        logTableName            = $tablename
                        object                  = $outlines[$file]
                        TimeStampField          = "RecordTime"
                    }
                    Post-LogAnalyticsData @runparams
                    $outlines[$file].Clear()
                }
            }           
        }
    }

    foreach ($logfile in $outLines.Keys) {
        if ($outLines[$logfile].Count -gt 0) {
            Write-Host "Processing $logfile; Importing $($metadata.Message), Iteration $i of $RunCount"
            $runparams = @{
                LogAnalyticsWorkspaceID = $LogAnalyticsWorkspaceID
                LogAnalyticsWorkspaceKey= $LogAnalyticsWorkspaceKey
                logTableName            = $logfile.Split('.')[0]
                object                  = $outLines[$logfile]
                TimeStampField          = "RecordTime"
            }
            Post-LogAnalyticsData @runparams
            $outlines[$logfile].Clear()
        }
    }
}
