$global:failed=0
$global:subscriptionId="419581d6-4853-49bd-83b6-d94bb8a77887"
$global:workspaceId="059f037c-1b3b-42b1-bb90-e340e8c3142c"

Class Parser {
    [string] $Name;
    [string] $OriginalQuery;
    [string] $Schema;
    [System.Collections.Generic.List`1[System.Object]] $Parameters
    Parser([string] $Name, [string] $OriginalQuery, [string] $Schema, [System.Collections.Generic.List`1[System.Object]] $Parameters) {
        $this.Name = $Name;
        $this.OriginalQuery = $OriginalQuery;
        $this.Schema = $Schema;
        $this.Parameters = $Parameters;
    }
}

function run {
    $subscription = Select-AzSubscription -SubscriptionId $global:subscriptionId
    $modifiedSchemas = & "$($PSScriptRoot)/../../getModifiedASimSchemas.ps1"
    $modifiedSchemas | ForEach-Object { testSchema($_) }
}

function testSchema([string] $schema) {
    $parsersAsObjects = & "$($PSScriptRoot)/convertYamlToObject.ps1"  -Path "$($PSScriptRoot)/../../../Parsers/$($schema)/Parsers"
    Write-Host "Testing $($schema) schema, $($parsersAsObjects.count) parsers were found"
    $parsersAsObjects | ForEach-Object {
        $functionName = "$($_.EquivalentBuiltInParser)V$($_.Parser.Version.Replace('.',''))"
        if ($_.Parsers) {
            Write-Host "The parser '$($functionName)' is a main parser, ignoring it"
        }
        else {
            testParser([Parser]::new($functionName, $_.ParserQuery, $schema.replace("ASim", ""), $_.ParserParams))
        }
    }
}

function testParser([Parser] $parser) {
    Write-Host "Testing parser- '$($parser.Name)'"
    $letStatementName = "generated$($parser.Name)"
    $parserAsletStatement = "let $($letStatementName)= ($(getParameters($parser.Parameters))) { $($parser.OriginalQuery) };"

    Write-Host "-- Running schema test for '$($parser.Name)'"
    $schemaTest = "$($parserAsletStatement)`r`n$($letStatementName) | getschema | invoke ASimSchemaTester('$($parser.Schema)')"
    invokeAsimTester $schemaTest $parser.Name "schema"
    Write-Host ""

    Write-Host "-- Running data test for '$($parser.Name)'"
    $dataTest = "$($parserAsletStatement)`r`n$($letStatementName) | invoke ASimDataTester('$($parser.Schema)')"
    invokeAsimTester $dataTest  $parser.Name "data"
    Write-Host ""
    Write-Host ""
}

function invokeAsimTester([string] $test, [string] $name, [string] $kind) {
        $query = $test + " | where Result startswith '(0) Error:'"
        try {
            $rawResults = Invoke-AzOperationalInsightsQuery -WorkspaceId $global:workspaceId -Query $query -ErrorAction Stop
            if ($rawResults.Results) {
                $resultsArray = [System.Linq.Enumerable]::ToArray($rawResults.Results)
                if ($resultsArray.count) {  
                    $errorMessage = "`r`n$($name) $($kind)- test failed with $($resultsArray.count) errors:`r`n"        
                    $resultsArray | ForEach-Object { $errorMessage += "$($_.Result)`r`n" } 
                    Write-Host $errorMessage
                    $global:failed = 1
                }
                else {
                    Write-Host "  -- $($name) $($kind) test done successfully"
                }
            }    
        }
        catch {
            Write-Host "  -- $_"
            Write-Host "     $(((Get-Error -Newest 1)?.Exception)?.Response?.Content)"
            $global:failed = 1
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
    return $paramsString
}

run
exit $global:failed