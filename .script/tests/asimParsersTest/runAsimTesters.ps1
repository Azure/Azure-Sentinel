# Workspace ID for the Log Analytics workspace where the ASim schema and data tests will be conducted
$global:workspaceId = "8ecf8077-cf51-4820-aadd-14040956f35d"
#$global:workspaceId = "059f037c-1b3b-42b1-bb90-e340e8c3142c"
$global:subscriptionId="d1d8779d-38d7-4f06-91db-9cbc8de0176f"

# ANSI escape code for green text
$green = "`e[32m"
# ANSI escape code for yellow text
$yellow = "`e[33m"
# ANSI escape code to reset color
$reset = "`e[0m"

# Parser exclusion file path
$ParserExclusionsFilePath ="$($PSScriptRoot)/ExclusionListForASimTests.csv"
# Sentinel repository URL
$SentinelRepoUrl = "https://github.com/Azure/Azure-Sentinel.git"

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
    $subscription = Select-AzSubscription -SubscriptionId $global:subscriptionId
    Write-Host "This is the script from PR."
    # Check if upstream remote already exists
    $remoteExists = Invoke-Expression "git remote" | Select-String -Pattern "upstream"

    if (-not $remoteExists) {
        Write-Host "Adding upstream remote..."
        Invoke-Expression "git remote add upstream $SentinelRepoUrl"
    }

    # Fetch the latest changes from upstream repositories
    Write-Host "Fetching latest changes from upstream..."
    Invoke-Expression "git fetch upstream" *> $null

    # Get modified ASIM Parser files along with their status
    $modifiedFilesStatus = Invoke-Expression "git diff --name-status upstream/master -- $($PSScriptRoot)/../../../Parsers/"
    # Split the output into lines
    $modifiedFilesStatusLines = $modifiedFilesStatus -split "`n"
    # Initialize an empty array to store the file names and their status
    $global:modifiedFiles = @()
    # Iterate over the lines
    foreach ($line in $modifiedFilesStatusLines) {
        # Split the line into status and file name
        # Splitting the line into parts
        $parts = $line -split "\t"
        # Assigning the first part to $status and the last part to $file
        $status = $parts[0]
        $file = $parts[-1]  # -1 index refers to the last element
        # Check if the file is a YAML file
        if ($file -like "*.yaml") {
            # Add the file name and status to the array
            $global:modifiedFiles += New-Object PSObject -Property @{
                Name = $file
                Status = switch -Regex ($status) {
                    "A" { "Added" }
                    "M" { "Modified" }
                    "D" { "Deleted" }
                    "R" { "Renamed" }
                    default { "Unknown" }
                }
            }
        }
    }
    # Print the file names and their status
    Write-Host "${green}The following ASIM parser files have been updated. 'Schema' and 'Data' tests will be performed for each of these parsers:${reset}"
    foreach ($file in $modifiedFiles) {
        Write-Host ${yellow}("{0} ({1})" -f $file.Name, $file.Status)${reset}
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
        Write-Host "${yellow}The parser '$functionName' is a union parser, ignoring it from 'Schema' and 'Data' testing.${reset}"
        Write-Host "***************************************************"
    } else {
        testParser ([Parser]::new($functionName, $parsersAsObject.ParserQuery, $Schema.Replace("Parsers\ASim", ""), $parsersAsObject.ParserParams))
    }
}

function testParser([Parser] $parser) {
    Write-Host "***************************************************"
    Write-Host "${yellow}Testing parser - '$($parser.Name)'${reset}"
    $letStatementName = "generated$($parser.Name)"
    $parserAsletStatement = "let $letStatementName = ($(getParameters($parser.Parameters))) { $($parser.OriginalQuery) };"
    
    Write-Host "${yellow}Running 'Schema' test for '$($parser.Name)' parser${reset}"
    Write-Host "***************************************************"
    $schemaTest = "$parserAsletStatement`r`n$letStatementName | getschema | invoke ASimSchemaTester('$($parser.Schema)')"
    Write-Host "${yellow}Schema name : $($parser.Schema)${reset}"
    invokeAsimTester $schemaTest $parser.Name "schema"
    
    Write-Host "***************************************************"
    Write-Host "${yellow}Running 'Data' tests for '$($parser.Name)' parser${reset}"
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
                $IgnoreParserIsSet = IgnoreValidationForASIMParsers | Where-Object { $name -like "$_*" }
                if ($Errorcount -gt 0 -and $IgnoreParserIsSet)
                {
                    $FinalMessage = "'$name' '$kind' - test failed with $Errorcount error(s):"
                    Write-Host "::error::$FinalMessage"
                    Write-Host "::warning::The parser '$name' is listed in the parser exclusions file. Therefore, this workflow run will not fail because of it. To allow this parser to cause the workflow to fail, please remove its name from the exclusions list file located at: '$ParserExclusionsFilePath'"
                }
                elseif ($Errorcount -gt 0) {
                    $FinalMessage = "'$name' '$kind' - test failed with $Errorcount error(s):"
                    Write-Host "::error:: $FinalMessage"
                    # throw "Test failed with errors. Please fix the errors and try again." # Commented out to allow the script to continue running
                } else {
                    $FinalMessage = "'$name' '$kind' - test completed successfully with no error."
                    Write-Host "${green}$FinalMessage${reset}"
                }
            } else {
                Write-Host "::warning::$name $kind - test completed. No records found"
            }
        }
    } catch {
        Write-Host "::error::  -- $_"
        Write-Host "::error::     $(((Get-Error -Newest 1)?.Exception)?.Response?.Content)"
        #throw $_ # Commented out to allow the script to continue running
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

function IgnoreValidationForASIMParsers() {
    $csvContent = Import-Csv -Path $ParserExclusionsFilePath
    $parserNames = @()

    foreach ($row in $csvContent) {
        $parserNames += $row.ParserName
    }

    return $parserNames
}

# Call the run function. This is the entry point of the script
run