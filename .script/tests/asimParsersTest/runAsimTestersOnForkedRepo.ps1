Param([string]$fork, [string]$branch, [string]$repoBaseFolder)

$global:failed=0
$global:subscriptionId="419581d6-4853-49bd-83b6-d94bb8a77887"
$global:workspaceId="059f037c-1b3b-42b1-bb90-e340e8c3142c"
$global:schemas = ("DNS", "WebSession", "NetworkSession", "ProcessEvent")


function run {
    $subscription = Select-AzSubscription -SubscriptionId $global:subscriptionId
    $modifiedSchemas = & "$($PSScriptRoot)/../../getModifiedASimSchemas.ps1"
    $modifiedSchemas | ForEach-Object { testSchema($_) }
}

function testSchema([string] $fork, [string] $branch, [string] $repoBaseFolder) {
    if ($repoBaseFolder) {
        Set-Location $repoBaseFolder
    } else {
        $repoBaseFolder = "$($PSScriptRoot)/../../../"
    }

	$filesThatWereChanged=$(echo $(git diff --name-only))
	if($filesThatWereChanged) {
		Write-Error "Please commit your changes or stash them before run the script. "
	}
	else {   
        Write-Host "git remote add $($fork) https://github.com/$($fork)/Azure-Sentinel"
		git remote add $fork "https://github.com/$($fork)/Azure-Sentinel"

        Write-Host "git fetch $($fork)"
		git fetch $fork

        Write-Host "git checkout $($branch)"
		git checkout $branch

        Write-Host "runAsimTesters"
        & "$($repoBaseFolder)/.script/tests/asimParsersTest/runAsimTesters.ps1"
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
            # Write-Host "     $(((Get-Error -Newest 1)?.Exception)?.Response?.Content)"
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

testSchema $fork $branch $repoBaseFolder
exit $global:failed