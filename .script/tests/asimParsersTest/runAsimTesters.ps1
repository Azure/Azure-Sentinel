# Workspace ID for the Log Analytics workspace where the ASim schema and data tests will be conducted
$global:workspaceId = "cb6a2b4f-7073-4e59-9ab0-803cde6b2221"

# ANSI escape code for green text
$green = "`e[32m"
# ANSI escape code for yellow text
$yellow = "`e[33m"
# ANSI escape code to reset color
$reset = "`e[0m"

# Parser exclusion file path
$ParserExclusionsFilePath ="$($PSScriptRoot)/ExclusionListForASimTests.csv"

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
    Write-Host "ASIM Parser Tester Script"
    
    # Get user input for YAML file path
    $yamlFilePath = Read-Host "Please enter the full path to the ASIM YAML parser file you want to test"
    
    # Validate the file exists
    if (-not (Test-Path $yamlFilePath)) {
        Write-Host "::error::File not found: $yamlFilePath"
        throw "The specified YAML file does not exist."
    }
    
    # Validate it's a YAML file
    if (-not ($yamlFilePath -like "*.yaml" -or $yamlFilePath -like "*.yml")) {
        Write-Host "::error::Invalid file type. Please provide a YAML file (.yaml or .yml extension)."
        throw "Invalid file type."
    }
    
    # Initialize the global modified files array with the user-provided file
    $global:modifiedFiles = @()
    $global:modifiedFiles += New-Object PSObject -Property @{
        Name = $yamlFilePath
        Status = "UserProvided"
    }
    
    # Print the file that will be tested
    Write-Host "${green}The following ASIM parser file will be tested. 'Schema' and 'Data' tests will be performed:${reset}"
    Write-Host ${yellow}("$yamlFilePath (User Provided)")${reset}
    Write-Host "***************************************************"

    # Call testSchema function for the provided parser file
    testSchema $yamlFilePath
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
    
    # Extract schema from the YAML file content
    $Schema = ""
    if ($parsersAsObject.Normalization -and $parsersAsObject.Normalization.Schema) {
        $Schema = $parsersAsObject.Normalization.Schema
        Write-Host "${green}Schema automatically detected from YAML file: $Schema${reset}"
    } elseif ($ParserFile -match "Parsers[/\\]ASim([/\\][^/\\]+)") {
        # Fallback: extract from file path
        $Schema = $matches[1].Replace('\', '').Replace('/', '')
        Write-Host "${yellow}Schema extracted from file path: $Schema${reset}"
    } else {
        # Last resort: ask user for schema if it can't be determined
        $Schema = Read-Host "Please enter the ASIM schema name (e.g., Authentication, DNS, NetworkSession, etc.)"
    }
    
    if ($parsersAsObject.Parsers -or ($parsersAsObject.ParserName -like "*Empty")){
        Write-Host "***************************************************"
        Write-Host "${yellow}The parser '$functionName' is a union or empty parser, ignoring it from 'Schema' and 'Data' testing.${reset}"
        Write-Host "***************************************************"
    } else {
        testParser ([Parser]::new($functionName, $parsersAsObject.ParserQuery, $Schema, $parsersAsObject.ParserParams))
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
    # Test with only last 30 minutes of data.
    $dataTest = "$parserAsletStatement`r`n$letStatementName | where TimeGenerated >= ago(30min) | invoke ASimDataTester('$($parser.Schema)')"
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
                    # Check if the file name matches and the status is 'Added' or 'UserProvided'
                    if ($file.Name -eq $name -and ($file.Status -eq 'Added' -or $file.Status -eq 'UserProvided')) {
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
                $WarningCount = ($resultsArray | Where-Object { $_.Result -like "(0) Warning:*" }).Count
                
                # Extract detailed error messages for better diagnostics
                $ErrorMessages = ($resultsArray | Where-Object { $_.Result -like "(0) Error:*" }) | ForEach-Object { $_.Result }
                $WarningMessages = ($resultsArray | Where-Object { $_.Result -like "(0) Warning:*" }) | ForEach-Object { $_.Result }
                
                $IgnoreParserIsSet = IgnoreValidationForASIMParsers | Where-Object { $name -like "$_*" }
                if ($Errorcount -gt 0 -and $IgnoreParserIsSet)
                {
                    $FinalMessage = "'$name' '$kind' - test failed with $Errorcount error(s) and $WarningCount warning(s)"
                    Write-Host "::error::$FinalMessage"
                    Write-Host "::error::Detailed error messages:"
                    foreach ($errorMsg in $ErrorMessages) {
                        Write-Host "::error::  - $errorMsg"
                    }
                    if ($WarningMessages.Count -gt 0) {
                        Write-Host "::warning::Warning messages:"
                        foreach ($warningMsg in $WarningMessages) {
                            Write-Host "::warning::  - $warningMsg"
                        }
                    }
                    Write-Host "::warning::The parser '$name' is listed in the parser exclusions file. Therefore, this workflow run will not fail because of it. To allow this parser to cause the workflow to fail, please remove its name from the exclusions list file located at: '$ParserExclusionsFilePath'"
                }
                elseif ($Errorcount -gt 0) {
                    $FinalMessage = "'$name' '$kind' - test failed with $Errorcount error(s) and $WarningCount warning(s)"
                    Write-Host "::error::$FinalMessage"
                    Write-Host "::error::Detailed error messages:"
                    foreach ($errorMsg in $ErrorMessages) {
                        Write-Host "::error::  - $errorMsg"
                    }
                    if ($WarningMessages.Count -gt 0) {
                        Write-Host "::warning::Warning messages:"
                        foreach ($warningMsg in $WarningMessages) {
                            Write-Host "::warning::  - $warningMsg"
                        }
                    }
                    Write-Host "::error::Please review the above error details and fix the issues in your YAML parser file."
                    throw "Test failed with $Errorcount error(s). See detailed error messages above." # Commented out to allow the script to continue running
                } else {
                    $FinalMessage = "'$name' '$kind' - test completed successfully with no errors"
                    if ($WarningCount -gt 0) {
                        $FinalMessage += " and $WarningCount warning(s)"
                        Write-Host "${yellow}$FinalMessage${reset}"
                        Write-Host "::warning::Warning messages:"
                        foreach ($warningMsg in $WarningMessages) {
                            Write-Host "::warning::  - $warningMsg"
                        }
                    } else {
                        Write-Host "${green}$FinalMessage${reset}"
                    }
                }
            } else {
                Write-Host "::warning::$name $kind - test completed. No records found"
            }
        }
    } catch {
        $errorMessage = $_.Exception.Message
        $errorDetails = $_.Exception.ToString()
        
        Write-Host "::error::An exception occurred while running the '$kind' test for parser '$name':"
        Write-Host "::error::Error Message: $errorMessage"
        
        # Check if there's additional response content (common with Azure API errors)
        $responseContent = ((Get-Error -Newest 1)?.Exception)?.Response?.Content
        if ($responseContent) {
            Write-Host "::error::Response Content: $responseContent"
        }
        
        # Provide more context about the query that failed
        Write-Host "::error::Failed Query:"
        Write-Host "::error::$query"
        
        Write-Host "::error::Full Exception Details:"
        Write-Host "::error::$errorDetails"
        
        throw "Test execution failed for '$name' '$kind' test. See detailed error information above." # Commented out to allow the script to continue running
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