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
    # Get modified ASIM Parser files
    $modifiedFiles = Invoke-Expression "git diff origin/master --name-only -- $($PSScriptRoot)/../../../Parsers/"
    # Get modified parser YAML files
    $modifiedYamlFiles = $modifiedFiles | Where-Object { $_ -like "*.yaml" }

    Write-Host "The following ASIM parser files have been modified. Schema and data tests will be conducted for each of these parsers:"
    Write-Host "***************************************************"
    $modifiedYamlFiles | ForEach-Object { Write-Host $_ -ForegroundColor Green }
    Write-Host "***************************************************"

    # Call testSchema function for each modified parser file
    $modifiedYamlFiles | ForEach-Object { testSchema $_ }
}

function testSchema([string] $ParserFile) {
    $parsersAsObject = & "$($PSScriptRoot)/convertYamlToObject.ps1" -Path "$ParserFile"
    $functionName = "$($parsersAsObject.EquivalentBuiltInParser)V$($parsersAsObject.Parser.Version.Replace('.', ''))"
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
    
    Write-Host "-- Running schema test for '$($parser.Name)'"
    Write-Host "***************************************************"
    $schemaTest = "$parserAsletStatement`r`n$letStatementName | getschema | invoke ASimSchemaTester('$($parser.Schema)')"
    Write-Host "Schema name is: $($parser.Schema)"
    invokeAsimTester $schemaTest $parser.Name "schema"
    
    Write-Host "***************************************************"
    Write-Host "-- Running data test for '$($parser.Name)'"
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
                $resultsArray | ForEach-Object { $TestResults += "$($_.Result)`r`n" }
                Write-Host $TestResults
                $Errorcount = ($resultsArray | Where-Object { $_.Result -like "(0) Error:*" }).Count
                if ($Errorcount -gt 0) {
                    $FinalMessage = "`r`n$name $kind - test failed with $Errorcount errors:`r`n"
                    Write-Host $FinalMessage -ForegroundColor Red
                    $global:failed = 1
                    throw "Test failed with errors. Please fix the errors and try again."
                } else {
                    $FinalMessage = "$name $kind - test completed successfully with no errors."
                    Write-Host $FinalMessage -ForegroundColor Green
                }
            } else {
                Write-Host "  -- $name $kind test done successfully. No records found"
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