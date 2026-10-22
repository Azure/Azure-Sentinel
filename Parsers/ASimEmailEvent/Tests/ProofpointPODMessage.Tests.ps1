$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
$parserPath = Join-Path $PSScriptRoot '..\Parsers\ASimEmailEventProofpointPODMessage.yaml'
$text = Get-Content -LiteralPath $parserPath -Raw
$query = ($text -split 'ParserQuery: \|\r?\n', 2)[1]
if (-not $query) { throw 'ParserQuery is missing.' }

$checks = 0
function Assert-Parser($Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
    $script:checks++
}

Assert-Parser ($text -cmatch '(?m)^ParserName: ASimEmailEventProofpointPODMessage\r?$') 'Incorrect parser name.'
Assert-Parser ($text -cmatch '(?m)^EquivalentBuiltInParser: _ASim_EmailEvent_ProofpointPODMessage\r?$') 'Incorrect built-in parser name.'
Assert-Parser ($query -match 'ProofpointPODMessage_CL\s*\| where not\(disabled\)') 'Disabled must filter the declared source before parsing.'
Assert-Parser ($query -notmatch '(?i)\|\s*(mv-\w+|summarize|distinct|join|union|externaldata)\b') 'Parser must preserve source-row cardinality without enrichment.'
Assert-Parser ($query -notmatch '(?i)\b(arg_min|arg_max|project-away)\b') 'Parser must use an explicit projection without aggregation.'
Assert-Parser ($query -match 'EventType="EmailInspection"') 'Message inspection must not be reported as delivery.'
Assert-Parser ($query -match 'EventResult="NA"') 'Filter disposition must not invent delivery success.'
Assert-Parser ($query -match 'AdditionalFields=iff\(pack,') 'Source details must be opt-in.'

$projection = ($query -split '\| project\s*\r?\n', 2)[1]
Assert-Parser ([bool]$projection) 'Final projection is missing.'
$projection = ($projection -split '\r?\n\s*\};', 2)[0]
$fields = @($projection -split '[,\s]+' | Where-Object { $_ })
$schema = Import-Csv -LiteralPath (Join-Path $repo 'ASIM\dev\ASimTester\ASimTester.csv') |
    Where-Object { $_.Schema -in 'Common', 'EmailEvent' }
foreach ($field in $schema | Where-Object Class -eq 'Mandatory') {
    Assert-Parser ($fields -ccontains $field.ColumnName) "Missing mandatory field: $($field.ColumnName)"
}
foreach ($field in $schema | Where-Object { $_.ColumnName -match '(EntityKey|AdditionalIds)$|^AdditionalEntities$' }) {
    Assert-Parser ($fields -ccontains $field.ColumnName) "Missing entity placeholder: $($field.ColumnName)"
}
foreach ($field in $fields) {
    Assert-Parser (($schema.ColumnName -ccontains $field) -or $field -eq 'Type') "Unnormalized output field: $field"
}
Assert-Parser ($fields.Count -eq @($fields | Sort-Object -Unique).Count) 'Duplicate projected fields.'

$connector = Join-Path $repo 'Solutions\Proofpoint On demand(POD) Email Security\Data Connectors\ProofPointEmailSecurity_CCP'
$table = Get-Content -LiteralPath (Join-Path $connector 'ProofpointPOD_Table_Message.json') -Raw | ConvertFrom-Json
$fixtureSchema = Import-Csv -LiteralPath (Join-Path $repo 'Sample Data\ASIM\ProofpointPODMessage_CL_Schema.csv')
foreach ($column in $table.properties.schema.columns) {
    $fixtureColumn = @($fixtureSchema | Where-Object ColumnName -CEQ $column.name)
    Assert-Parser ($fixtureColumn.Count -eq 1 -and $fixtureColumn[0].ColumnType -ceq $column.type) "Fixture schema differs from source: $($column.name)"
}
Assert-Parser ($fixtureSchema.Count -eq $table.properties.schema.columns.Count) 'Fixture schema adds undeclared source columns.'
$dcr = Get-Content -LiteralPath (Join-Path $connector 'ProofpointPOD_DCR.json') -Raw | ConvertFrom-Json
$flow = $dcr.properties.dataFlows | Where-Object outputStream -EQ 'Custom-ProofpointPODMessage_CL'
Assert-Parser ($flow.transformKql -match 'eventTime = todatetime\(ts\)') 'Source event-time transform changed.'

$rows = @(Import-Csv -LiteralPath (Join-Path $repo 'Sample Data\ASIM\Proofpoint_POD_EmailEvent_IngestedLogs.csv'))
Assert-Parser ($rows.Count -eq 4) 'Expected single, multiple, unknown and discarded fixtures.'
foreach ($row in $rows) {
    Assert-Parser ($row.Type -ceq 'ProofpointPODMessage_CL') 'Fixture targets another source table.'
    foreach ($column in $table.properties.schema.columns) {
        $value = if ($column.type -eq 'datetime') { $row.("$($column.name) [UTC]") } else { $row.($column.name) }
        Assert-Parser ($null -ne $value) "Missing fixture column: $($column.name)"
        if ($column.type -eq 'dynamic') { $null = ConvertFrom-Json -InputObject $value }
        if ($column.type -eq 'datetime') { $null = [datetime]::Parse($value, [cultureinfo]::InvariantCulture) }
    }
}
$multi = $rows[1].msg | ConvertFrom-Json
Assert-Parser ($multi.parsedAddresses.from.Count -gt 1) 'Multi-valued sender coverage is missing.'
Assert-Parser (($rows[1].filter | ConvertFrom-Json).modules.dkimv.Count -gt 1) 'Multiple DKIM signature coverage is missing.'
Assert-Parser ($query -match 'array_length\(msg.parsedAddresses.from\) == 1') 'Multiple senders must not silently select the first.'
Assert-Parser ($query -match "array_length\(\['filter'\].modules.dkimv\) == 1") 'Multiple signatures must not silently select the first.'
Assert-Parser ($query -notmatch 'Email(File|Url)(Count|s)\s*=') 'MIME parts must not be mislabeled as attachments or URLs.'
$change = Get-Content -LiteralPath (Join-Path $PSScriptRoot '..\CHANGELOG\ASimEmailEventProofpointPODMessage.md') -Raw
Assert-Parser ($change.StartsWith('# Changelog for ASimEmailEventProofpointPODMessage.yaml')) 'Changelog filename does not match.'
Assert-Parser ($change -match '## Version 0\.1\.0') 'Changelog version does not match.'
Assert-Parser (-not ($text.ToCharArray() | Where-Object { [int]$_ -gt 127 })) 'Parser YAML must be ASCII-only.'

$analyzerPath = Join-Path $repo '.script\tests\KqlvalidationsTests\bin\Debug\net8.0\Kusto.Language.dll'
if (-not (Test-Path -LiteralPath $analyzerPath)) {
    throw 'Build .script\tests\KqlvalidationsTests\Kqlvalidations.Tests.csproj before running these checks to restore the repository KQL analyzer.'
}
Add-Type -Path $analyzerPath
$columns = [Kusto.Language.Symbols.ColumnSymbol[]]@(
    foreach ($column in $fixtureSchema) {
        [Kusto.Language.Symbols.ColumnSymbol]::new(
            $column.ColumnName,
            [Kusto.Language.Symbols.ScalarTypes]::GetSymbol($column.ColumnType))
    }
)
$tableSymbol = [Kusto.Language.Symbols.TableSymbol]::new('ProofpointPODMessage_CL', $columns)
$database = [Kusto.Language.Symbols.DatabaseSymbol]::new('Fixture', [Kusto.Language.Symbols.Symbol[]]@($tableSymbol))
$globals = [Kusto.Language.GlobalState]::Default.WithDatabase($database)
$code = [Kusto.Language.KustoCode]::ParseAndAnalyze("let disabled=false; let pack=false;`n$query", $globals)
$errors = @($code.GetDiagnostics() | Where-Object Severity -EQ 'Error')
if ($errors.Count) {
    $errors | Format-List Code, Message, Start, Length | Out-Host
    throw "$($errors.Count) KQL semantic errors."
}
foreach ($column in $code.ResultType.Columns) {
    if ($column.Name -eq 'Type') { continue }
    $definition = @($schema | Where-Object ColumnName -CEQ $column.Name)
    Assert-Parser ($column.Type.Name -cin $definition.ColumnType) "Incorrect output type: $($column.Name) ($($column.Type.Name))"
}
Assert-Parser ($code.ResultType.Columns.Count -eq $fields.Count) 'Inferred KQL output differs from the explicit field projection.'

Add-Type -Path (Join-Path (Split-Path $analyzerPath) 'YamlDotNet.dll')
$yaml = [YamlDotNet.Serialization.Deserializer]::new()
$source = $yaml.Deserialize($text, [object])
$vimText = Get-Content -LiteralPath (Join-Path $PSScriptRoot '..\Parsers\vimEmailEventProofpointPODMessage.yaml') -Raw
$vim = $yaml.Deserialize($vimText, [object])
$unifier = $yaml.Deserialize((Get-Content -LiteralPath (Join-Path $PSScriptRoot '..\Parsers\ASimEmailEvent.yaml') -Raw), [object])
$filteringUnifier = $yaml.Deserialize((Get-Content -LiteralPath (Join-Path $PSScriptRoot '..\Parsers\imEmailEvent.yaml') -Raw), [object])
$empty = $yaml.Deserialize((Get-Content -LiteralPath (Join-Path $PSScriptRoot '..\Parsers\vimEmailEventEmpty.yaml') -Raw), [object])

function Get-KqlParameters($Parser, [switch]$Declarations) {
    (@(foreach ($parameter in $Parser['ParserParams']) {
        $value = if ($parameter['Type'] -eq 'string') { "'$($parameter['Default'])'" } else { "$($parameter['Default'])".ToLowerInvariant() }
        if ($Declarations) { "$($parameter['Name']):$($parameter['Type'])=$value" }
        else { "let $($parameter['Name'])=$value;" }
    }) -join $(if ($Declarations) { ',' } else { "`n" }))
}

foreach ($parser in @($source, $vim)) {
    $name = $parser['ParserName']
    $body = $parser['ParserQuery']
    Assert-Parser ($body -notmatch '(?i)\|\s*(mv-\w+|summarize|distinct|join|union|externaldata)\b') "$name violates source-row integrity."
    Assert-Parser (-not ($body.ToCharArray() | Where-Object { [int]$_ -gt 127 })) "$name query must be ASCII."
    $preamble = Get-KqlParameters $parser
    $analysis = [Kusto.Language.KustoCode]::ParseAndAnalyze("$preamble`n$body", $globals)
    $diagnostics = @($analysis.GetDiagnostics() | Where-Object Severity -EQ 'Error')
    if ($diagnostics.Count) {
        $diagnostics | Format-List Code, Message, Start, Length | Out-Host
        throw "$name has KQL semantic errors."
    }
    Assert-Parser ($analysis.ResultType.Columns.Count -eq $fields.Count) "$name output has changed."
    foreach ($column in $analysis.ResultType.Columns) {
        $expected = @($code.ResultType.Columns | Where-Object Name -CEQ $column.Name)
        Assert-Parser ($expected.Count -eq 1 -and $column.Type.Name -ceq $expected[0].Type.Name) "$name output differs at $($column.Name)."
    }
    $history = Get-Content -LiteralPath (Join-Path $PSScriptRoot "..\CHANGELOG\$name.md") -Raw
    Assert-Parser ($history -match "## Version $([regex]::Escape($parser['Parser']['Version']))") "$name changelog version mismatch."
}

foreach ($parameter in $filteringUnifier['ParserParams']) {
    $matches = @($vim['ParserParams'] | Where-Object { $_['Name'] -ceq $parameter['Name'] })
    Assert-Parser ($matches.Count -eq 1 -and $matches[0]['Type'] -ceq $parameter['Type']) "Missing or incorrect filtering parameter: $($parameter['Name'])"
    Assert-Parser ($vim['ParserQuery'] -match "$($parameter['Name'])=$($parameter['Name'])") "Parameter is not forwarded: $($parameter['Name'])"
}
$filterBody = $vim['ParserQuery']
Assert-Parser ($filterBody -match 'isnull\(starttime\) or eventTime >= starttime') 'Start boundary must use inclusive event time.'
Assert-Parser ($filterBody -match 'isnull\(endtime\) or eventTime <= endtime') 'End boundary must use inclusive event time.'
Assert-Parser ($filterBody -match "eventresult == '\*' or eventresult == 'NA'") 'Result filter must match normalized inspection results.'
Assert-Parser ($filterBody -match 'where array_length\(emaildeliverylocation_in\) == 0') 'Unknown delivery location must not match a nonempty filter.'
foreach ($parameter in @('ipaddr_has_any_prefix', 'emailfromaddress_has_any', 'emailrecipient_has_any', 'emailsubject_has_any', 'emaildirection_in')) {
    Assert-Parser ($filterBody -match "array_length\($parameter\) == 0") "Missing no-filter behavior: $parameter"
}
Assert-Parser ($filterBody.IndexOf('has_any_ipv4_prefix') -lt $filterBody.IndexOf('| project-rename')) 'IP filtering must precede remaining normalization.'
Assert-Parser ($filterBody.IndexOf('EmailDirection in~') -lt $filterBody.IndexOf('| project-rename')) 'Direction filtering must precede remaining normalization.'
$mapStart = '\| extend\r?\n\s*Dvc=coalesce'
$sourceMap = (($source['ParserQuery'] -split $mapStart, 2)[1] -split '\r?\n\s*\};', 2)[0]
$vimMap = (($vim['ParserQuery'] -split $mapStart, 2)[1] -split '\r?\n\s*\};', 2)[0]
Assert-Parser ($sourceMap -and $sourceMap -ceq $vimMap) 'Shared post-filter normalization must stay identical.'

$functionDefinitions = @(
    "let _GetWatchlist=(name:string){datatable(SearchKey:string, SourceSpecificParser:string)[]};"
    "let vimEmailEventEmpty=(){$($empty['ParserQuery'])};"
    foreach ($parser in @($source, $vim)) {
        "let $($parser['ParserName'])=($(Get-KqlParameters $parser -Declarations)){$($parser['ParserQuery'])};"
    }
) -join "`n"
$filterCalls = @(
    'disabled=true',
    'pack=true',
    'starttime=datetime(2026-10-01T12:00:00Z)',
    'endtime=datetime(2026-10-01T12:01:00Z)',
    'starttime=datetime(null), endtime=datetime(null)',
    'ipaddr_has_any_prefix=dynamic(["192.0.2."])',
    'ipaddr_has_any_prefix=dynamic(["192.0.2.", "198.51.100."])',
    'emailfromaddress_has_any=dynamic(["sanitized"])',
    'emailrecipient_has_any=dynamic(["sanitized"])',
    'emailsubject_has_any=dynamic(["Example", "message"])',
    'emaildirection_in=dynamic(["Inbound", "Outbound"])',
    'emaildeliverylocation_in=dynamic(["Inbox"])',
    "eventresult='NA'",
    "eventresult='Failure'",
    'starttime=datetime(2026-10-01T12:00:00Z), endtime=datetime(2026-10-01T12:01:00Z), emaildirection_in=dynamic(["inbound"]), pack=true'
)
foreach ($arguments in $filterCalls) {
    $analysis = [Kusto.Language.KustoCode]::ParseAndAnalyze("$functionDefinitions`nvimEmailEventProofpointPODMessage($arguments)", $globals)
    $errors = @($analysis.GetDiagnostics() | Where-Object Severity -EQ 'Error')
    Assert-Parser ($errors.Count -eq 0) "Filter invocation fails semantic analysis: $arguments"
}
foreach ($parser in @($unifier, $filteringUnifier)) {
    $name = $parser['ParserName']
    $body = $parser['ParserQuery']
    $child = if ($name -eq 'ASimEmailEvent') { $source } else { $vim }
    Assert-Parser ($parser['Parsers'] -ccontains $child['EquivalentBuiltInParser']) "$name dependency registration missing."
    Assert-Parser ($body.Contains($child['ParserName'] + '(')) "$name source invocation missing."
    Assert-Parser ($body.Contains("'Exclude$($child['ParserName'])' in (DisabledParsers)")) "$name source disable control missing."
    $analysis = [Kusto.Language.KustoCode]::ParseAndAnalyze("$functionDefinitions`n$(Get-KqlParameters $parser)`n$body", $globals)
    $errors = @($analysis.GetDiagnostics() | Where-Object Severity -EQ 'Error')
    if ($errors.Count) {
        $errors | Format-List Code, Message, Start, Length | Out-Host
        throw "$name has KQL semantic errors with the source definitions."
    }
    $history = Get-Content -LiteralPath (Join-Path $PSScriptRoot "..\CHANGELOG\$name.md") -Raw
    Assert-Parser ($history -match "## Version $([regex]::Escape($parser['Parser']['Version']))") "$name changelog version mismatch."
}

foreach ($parser in @($source, $vim, $unifier, $filteringUnifier)) {
    $name = $parser['ParserName']
    $armPath = Join-Path $PSScriptRoot "..\ARM\$name\$name.json"
    $arm = Get-Content -LiteralPath $armPath -Raw | ConvertFrom-Json
    $properties = $arm.resources[0].properties
    Assert-Parser ($properties.query -ceq $parser['ParserQuery']) "$name ARM query differs from YAML."
    Assert-Parser ($properties.FunctionAlias -ceq $name) "$name ARM function alias differs."
    Assert-Parser ($properties.functionParameters -ieq (Get-KqlParameters $parser -Declarations)) "$name ARM parameters differ."
    $armQuery = "$functionDefinitions`nlet DeployedParser=($($properties.functionParameters)){$($properties.query)}; DeployedParser()"
    $analysis = [Kusto.Language.KustoCode]::ParseAndAnalyze($armQuery, $globals)
    $errors = @($analysis.GetDiagnostics() | Where-Object Severity -EQ 'Error')
    Assert-Parser ($errors.Count -eq 0) "$name generated ARM signature/query fails semantic analysis."
}
$fullArm = Get-Content -LiteralPath (Join-Path $PSScriptRoot '..\ARM\FullDeploymentEmailEvent.json') -Raw | ConvertFrom-Json
foreach ($name in @($source['ParserName'], $vim['ParserName'])) {
    Assert-Parser ($fullArm.resources.name -ccontains "linked$name") "$name is absent from full deployment."
}
Write-Output "PASS: $checks offline contract, KQL semantic/type, registration and ARM checks. Live execution and ASIM data/filter tests are deferred."
