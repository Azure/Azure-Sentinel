$global:failed = 0

# Subscription ID which contains Log Analytics workspace where the ASim schema and data tests will be conducted
$global:subscriptionId = "4383ac89-7cd1-48c1-8061-b0b3c5ccfd97"

# Workspace ID for the Log Analytics workspace where the ASim schema and data tests will be conducted
$global:workspaceId = "46bec743-35fa-4608-b7e2-2aa3c38a97c2"

Class Parser {
    [string] $Name
    [string] $OriginalQuery
    [string] $Schema
    [System.Collections.Generic.List`1[System.Object]] $Parameters

    Parser([string] $Name, [string] $OriginalQuery, [string] $Schema, [System.Collections.Generic.List`1[System.Object]] $Parameters) {
        $this.Name = $Name
        $this.OriginalQuery = $OriginalQuery
        $this.Schema = $Schema
        $this.Parameters = $Parameters
    }
}

function run {
    #$subscription = Select-AzSubscription -SubscriptionId $global:subscriptionId
    # Get modified ASIM Parser files along with their status
    $modifiedFilesStatus = Invoke-Expression "git diff --name-status origin/master -- $($PSScriptRoot)/../../../Parsers/"
    # Split the output into lines
    $modifiedFilesStatusLines = $modifiedFilesStatus -split "`n"
    # Initialize an empty array to store the file names and their status
    $global:modifiedFiles = @()
    # Iterate over the lines
    foreach ($line in $modifiedFilesStatusLines) {
        # Split the line into status and file name
        $status, $file = $line -split "\t", 2
        # Check if the file is a YAML file
        if ($file -like "*.yaml") {
            # Add the file name and status to the array
            $modifiedFiles += New-Object PSObject -Property @{
                Name = $file
                Status = switch ($status) {
                    "A" { "Added" }
                    "M" { "Modified" }
                    "D" { "Deleted" }
                    default { "Unknown" }
                }
            }
        }
    }
    # Print the file names and their status
    Write-Host "The following ASIM parser files have been updated. 'Schema' and 'Data' tests will be performed for each of these parsers:"
    foreach ($file in $modifiedFiles) {
        Write-Host ("{0} ({1})" -f $file.Name, $file.Status) -ForegroundColor Green
    }
    Write-Host "***************************************************"

    # Call testSchema function for each modified parser file
    $modifiedFiles | ForEach-Object { testSchema $_.Name }
}

function testSchema([string] $ParserFile) {
    $parsersAsObject = & "$($PSScriptRoot)/convertYamlToObject.ps1" -Path "$ParserFile"
    $functionName = "$($parsersAsObject.EquivalentBuiltInParser)V$($parsersAsObject.Parser.Version.Replace('.', ''))"
    # Iterate over the modified files
    for ($i = 0; $i -lt $modifiedFiles.Count; $i++) {
        # Check if the current file is the parser file
        if ($modifiedFiles[$i].Name -eq $parserfile) {
            # Replace 'Name' with the function name
            $modifiedFiles[$i].Name = $functionName
        }
    }
    $Schema = (Split-Path -Path $ParserFile -Parent | Split-Path -Parent)
    if ($parsersAsObject.Parsers) {
        Write-Host "***************************************************"
        Write-Host "The parser '$functionName' is a main parser, ignoring it" -ForegroundColor Yellow
        Write-Host "***************************************************"
    } else {
        testParser ([Parser]::new($functionName, $parsersAsObject.ParserQuery, $Schema.Replace("Parsers/ASim", ""), $parsersAsObject.ParserParams))
    }
}

function testParser([Parser] $parser) {
    Write-Host "***************************************************"
    Write-Host "Testing parser - '$($parser.Name)'" -ForegroundColor Green
    $letStatementName = "generated$($parser.Name)"
    $parserAsletStatement = "let $letStatementName = ($(getParameters($parser.Parameters))) { $($parser.OriginalQuery) };"
    
    Write-Host "Running ASIM 'Schema' tests for '$($parser.Name)' parser"
    Write-Host "***************************************************"
    $schemaTest = "$parserAsletStatement`r`n$letStatementName | getschema | invoke ASimSchemaTester('$($parser.Schema)')"
    Write-Host "Schema name is: $($parser.Schema)"
    invokeAsimTester $schemaTest $parser.Name "schema"
    
    Write-Host "***************************************************"
    Write-Host "Running ASIM 'Data' tests for '$($parser.Name)' parser"
    $dataTest = "$parserAsletStatement`r`n$letStatementName | invoke ASimDataTester('$($parser.Schema)')"
    invokeAsimTester $dataTest $parser.Name "data"
    Write-Host "***************************************************"
}

function invokeAsimTester([string] $test, [string] $name, [string] $kind) {
    $query = $test
    $TestResults = ""
    try {
        $rawResults = Invoke-AzOperationalInsightsQuery -WorkspaceId $global:workspaceId -Query $query -ErrorAction Stop
        if ($rawResults.Results) {
            $resultsArray = [System.Linq.Enumerable]::ToArray($rawResults.Results)
            if ($resultsArray.Count) {
                # Iterate over the modified files
                foreach ($file in $modifiedFiles) {
                    # Check if the file name matches and the status is 'Added'
                    if ($file.Name -eq $name -and $file.Status -eq 'Added') {
                        # Iterate over the test results
                        for ($i = 0; $i -lt $resultsArray.Count; $i++) {
                            # Check if the test result contains the specified strings
                            if (($resultsArray[$i].Result -like '*Error: 1 invalid value(s)*') -and ($resultsArray[$i].Result -like '*EventProduct*' -or $resultsArray[$i].Result -like '*EventVendor*')) {
                                # Replace 'Error' with 'Warning'
                                $resultsArray[$i].Result = $resultsArray[$i].Result -replace 'Error', 'Warning'
                            }
                        }
                    }
                }
                $resultsArray | ForEach-Object { $TestResults += "$($_.Result)`r`n" }
                Write-Host $TestResults
                $Errorcount = ($resultsArray | Where-Object { $_.Result -like "(0) Error:*" }).Count
                if ($Errorcount -gt 0) {
                    $FinalMessage = "`r`n'$name' '$kind' - test failed with $Errorcount errors:`r`n"
                    Write-Host $FinalMessage -ForegroundColor Red
                    $global:failed = 1
                    throw "Test failed with errors. Please fix the errors and try again."
                } else {
                    $FinalMessage = "'$name' '$kind' - test completed successfully with no errors."
                    Write-Host $FinalMessage -ForegroundColor Green
                }
            } else {
                Write-Host "$name $kind test done successfully. No records found"
            }
        }
    } catch {
        Write-Host "  -- $_"
        Write-Host "     $(((Get-Error -Newest 1)?.Exception)?.Response?.Content)"
        $global:failed = 1
        throw $_
    }
}

function getParameters([System.Collections.Generic.List`1[System.Object]] $parserParams) {
    $paramsArray = @()
    if ($parserParams) {
        $parserParams | ForEach-Object {
            if ($_.Type -eq "string") {
                $_.Default = "'$($_.Default)'"
            }
            $paramsArray += "$($_.Name):$($_.Type)= $($_.Default)"
        }
        return $paramsArray -join ','
    }
    return ""
}

run

if ($global:failed -ne 0) {
    Write-Host "Script failed with errors." -ForegroundColor Red
    exit 1
} else {
    Write-Host "Script completed successfully." -ForegroundColor Green
    exit 0
}