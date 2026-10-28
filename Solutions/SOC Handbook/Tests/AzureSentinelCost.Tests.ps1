BeforeAll {
    $solutionRoot = Split-Path -Parent $PSScriptRoot
    $workbookPath = Join-Path (Join-Path $solutionRoot 'Workbooks') 'AzureSentinelCost.json'
    $script:workbookText = Get-Content -LiteralPath $workbookPath -Raw
    $script:workbook = $script:workbookText | ConvertFrom-Json -Depth 100
    $script:workbookItems = @{}

    function Add-WorkbookItems {
        param([object[]]$Items)

        foreach ($item in $Items) {
            if ($item.name) {
                if ($script:workbookItems.ContainsKey($item.name)) {
                    throw "Duplicate workbook item name: $($item.name)"
                }
                $script:workbookItems[$item.name] = $item
            }
            if ($item.content.items) {
                Add-WorkbookItems -Items $item.content.items
            }
        }
    }

    Add-WorkbookItems -Items $script:workbook.items

    function Get-WorkbookQuery {
        param([string]$ItemName)

        if (-not $script:workbookItems.ContainsKey($ItemName) -or
            -not $script:workbookItems[$ItemName].content.query) {
            throw "Workbook query not found: $ItemName"
        }
        $script:workbookItems[$ItemName].content.query
    }

    function Get-QueryExpression {
        param([string]$Query, [string]$Pattern)

        $match = [regex]::Match($Query, $Pattern)
        if (-not $match.Success) {
            throw "Expected query expression not found: $Pattern"
        }
        $match.Groups['expression'].Value.Trim()
    }

    function Invoke-WorkbookArithmetic {
        param([string]$Expression, [hashtable]$Bindings)

        $expression = [regex]::Replace($Expression, "todouble\('\{(\w+)\}'\)", '$1')
        $expression = [regex]::Replace($expression, '\{(\w+)\}', '$1')
        $expression = $expression.Replace('sum(Quantity)', 'Quantity')
        $expression = $expression.Replace('sum(CoveredQuantity)', 'CoveredQuantity')
        $numeric = [regex]::Replace($expression, "\['([^']+)'\]|[A-Za-z_][A-Za-z0-9_]*", {
            param($match)
            $key = if ($match.Groups[1].Success) { $match.Groups[1].Value } else { $match.Value }
            if (-not $Bindings.ContainsKey($key)) {
                throw "No numeric fixture binding for $key"
            }
            ([double]$Bindings[$key]).ToString('G17', [cultureinfo]::InvariantCulture)
        })
        if ($numeric -notmatch '^[0-9.eE+*/()\s-]+$') {
            throw "Fixture expression is not numeric arithmetic: $numeric"
        }
        $calculator = [System.Data.DataTable]::new()
        try {
            [double]$calculator.Compute($numeric, '')
        }
        finally {
            $calculator.Dispose()
        }
    }

    function Get-EligibleTables {
        param([string]$Query)

        $match = [regex]::Match($Query, 'let eligibleTables = dynamic\((\[[^\]]+\])\)')
        if (-not $match.Success) {
            throw 'The query must declare its eligible table set.'
        }
        @($match.Groups[1].Value | ConvertFrom-Json)
    }

    function Get-FixtureTimeGrain {
        param([string]$Query, [timespan]$Duration)

        $terms = (Get-QueryExpression -Query $Query -Pattern 'let timeGrain = case\((?<expression>[^;]+)\);') -split ',\s*'
        $secondsPerUnit = @{ m = 60; h = 3600; d = 86400 }
        $grain = $terms[-1]
        for ($index = 0; $index -lt $terms.Count - 1; $index += 2) {
            if ($terms[$index] -notmatch '^selectedDuration <= (\d+)([mhd])$') {
                throw "Unexpected time-grain condition: $($terms[$index])"
            }
            if ($Duration.TotalSeconds -le [double]$Matches[1] * $secondsPerUnit[$Matches[2]]) {
                $grain = $terms[$index + 1]
                break
            }
        }
        if ($grain -notmatch '^(\d+)([mhd])$') {
            throw "Unexpected time grain: $grain"
        }
        [timespan]::FromSeconds([double]$Matches[1] * $secondsPerUnit[$Matches[2]])
    }

    function Get-FixtureUsageTrend {
        param(
            [string]$ItemName,
            [object[]]$Records,
            [datetimeoffset]$Start,
            [datetimeoffset]$End
        )

        $content = $script:workbookItems[$ItemName].content
        $query = $content.query
        $grain = Get-FixtureTimeGrain -Query $query -Duration ($End - $Start)
        $scanStart = $Start
        if ($query.Contains('TimeGenerated >= bin(selectedStart, 1h)')) {
            $scanStart = $Start.AddTicks(-($Start.UtcTicks % [timespan]::TicksPerHour))
        }
        if ($content.timeContextFromParameter -eq 'TimeRange') {
            $scanStart = $Start
        }
        $clipsSource = $query.Contains('CoveredQuantity = Quantity * ((min_of(EndTime, selectedEnd) - max_of(StartTime, selectedStart)) / (EndTime - StartTime))')
        $eligibleTables = if ($query.Contains('DataType in (eligibleTables)')) { Get-EligibleTables -Query $query }
        $bins = @{}
        foreach ($record in $Records) {
            if ($record.TimeGenerated -lt $scanStart -or $record.TimeGenerated -ge $End -or
                ($query.Contains('IsBillable == true') -and -not $record.IsBillable) -or
                ($eligibleTables -and $record.DataType -notin $eligibleTables)) {
                continue
            }
            $quantity = $record.Quantity
            if ($clipsSource) {
                $coveredStart = if ($record.StartTime -gt $Start) { $record.StartTime } else { $Start }
                $coveredEnd = if ($record.EndTime -lt $End) { $record.EndTime } else { $End }
                $quantity *= ($coveredEnd - $coveredStart).Ticks / ($record.EndTime - $record.StartTime).Ticks
            }
            $bucketTicks = $record.TimeGenerated.UtcTicks - ($record.TimeGenerated.UtcTicks % $grain.Ticks)
            $bins[$bucketTicks] += $quantity
        }
        $expression = Get-QueryExpression -Query $query -Pattern "summarize \['(?:Mirrored Volume Size|Ingestion Size)'\] = (?<expression>[^|]+) by bin"
        foreach ($bucketTicks in $bins.Keys | Sort-Object) {
            $bucket = [datetimeoffset]::new($bucketTicks, [timespan]::Zero)
            $coveredStart = if ($bucket -gt $Start) { $bucket } else { $Start }
            $coveredEnd = if ($bucket.Add($grain) -lt $End) { $bucket.Add($grain) } else { $End }
            [pscustomobject]@{
                TimeGenerated = $bucket
                CoveredDays = ($coveredEnd - $coveredStart).TotalDays
                IngestionGB = Invoke-WorkbookArithmetic -Expression $expression -Bindings @{
                    Quantity = $bins[$bucketTicks]
                    CoveredQuantity = $bins[$bucketTicks]
                }
            }
        }
    }

    function Get-FixtureGrantUsed {
        param(
            [string]$Query,
            [object[]]$Records,
            [double]$LicenseCount,
            [datetimeoffset]$Start,
            [datetimeoffset]$End
        )

        $dailyPipeline = '\|\s*summarize DailyEligibleGB = sum\(Quantity\) / 1024\.0 by bin\(TimeGenerated, 1d\)\s*\|\s*summarize sum\(min_of\(DailyEligibleGB, dailyGrantGB\)\)'
        if ($Query -notmatch $dailyPipeline) {
            throw 'The embedded query must cap each UTC day before summing grant use.'
        }
        if ($Query -notmatch 'TimeGenerated >= \{TimeRange:start\} and TimeGenerated < \{TimeRange:end\}') {
            throw 'Grant queries must exclude the next UTC day at the selected end boundary.'
        }
        $allowance = Get-QueryExpression -Query $Query -Pattern 'let dailyGrantGB = (?<expression>[^;]+);'
        $dailyGrantGB = Invoke-WorkbookArithmetic -Expression $allowance -Bindings @{ licenseCount = $LicenseCount }
        $eligibleTables = Get-EligibleTables -Query $Query
        $selected = @($Records | Where-Object {
            $_.IsBillable -and $_.DataType -in $eligibleTables -and
            $_.TimeGenerated -ge $Start -and $_.TimeGenerated -lt $End
        })
        $total = 0.0
        foreach ($day in $selected | Group-Object { $_.TimeGenerated.UtcDateTime.Date }) {
            $dailyGB = [double](($day.Group | Measure-Object -Property Quantity -Sum).Sum) / 1024.0
            $total += [math]::Min($dailyGB, $dailyGrantGB)
        }
        $total
    }
}

Describe 'AzureSentinelCost offline calculation regressions' {
    It 'never presents hourly Usage as sub-hour measurements in <ItemName>' -ForEach @(
        @{ ItemName = 'WorkspaceBillableIngestionSizeTrend' }
        @{ ItemName = 'DataLakeMirroredVolumeTrend' }
        @{ ItemName = 'FreeDataVsBillableDataDaily' }
        @{ ItemName = 'E5DailyIngestionVsGrant' }
        @{ ItemName = 'DfSP2DailyIngestionVsGrant' }
    ) {
        $query = Get-WorkbookQuery -ItemName $ItemName
        foreach ($duration in @('00:05:00', '01:00:00', '04:00:00', '1.00:00:00', '7.00:00:00', '31.00:00:00', '90.00:00:00', '100.00:00:00')) {
            (Get-FixtureTimeGrain -Query $query -Duration $duration).TotalHours | Should -BeGreaterOrEqual 1
        }
    }

    Context '<ItemName> hourly Usage source intervals' -ForEach @(
        @{ ItemName = 'DataLakeMirroredVolumeTrend'; DataType = 'SecurityEvent'; Licenses = 1.0 }
        @{ ItemName = 'E5DailyIngestionVsGrant'; DataType = 'SigninLogs'; Licenses = 100.0 }
        @{ ItemName = 'DfSP2DailyIngestionVsGrant'; DataType = 'SecurityEvent'; Licenses = 1.0 }
    ) {
        It 'preserves a 10 GB/day source rate for <Label>' -ForEach @(
            @{ Label = 'one aligned hour'; Start = '2026-10-01T10:00:00Z'; End = '2026-10-01T11:00:00Z' }
            @{ Label = 'five minutes inside an hour'; Start = '2026-10-01T10:10:00Z'; End = '2026-10-01T10:15:00Z' }
            @{ Label = 'fifteen minutes crossing an hour'; Start = '2026-10-01T10:55:00Z'; End = '2026-10-01T11:10:00Z' }
            @{ Label = 'two partial hourly edges'; Start = '2026-10-01T10:15:00Z'; End = '2026-10-01T11:30:00Z' }
            @{ Label = 'a UTC midnight crossing'; Start = '2026-10-01T23:55:00Z'; End = '2026-10-02T00:10:00Z' }
            @{ Label = 'partial six-hour buckets'; Start = '2026-10-01T04:15:00Z'; End = '2026-10-03T02:45:00Z' }
        ) {
            $query = Get-WorkbookQuery -ItemName $ItemName
            $startTime = [datetimeoffset]$Start
            $endTime = [datetimeoffset]$End
            $firstHour = $startTime.AddTicks(-($startTime.UtcTicks % [timespan]::TicksPerHour))
            $records = @(
                for ($hour = $firstHour.AddHours(-1); $hour -le $endTime.AddHours(1); $hour = $hour.AddHours(1)) {
                    @{
                        TimeGenerated = $hour
                        StartTime = $hour
                        EndTime = $hour.AddHours(1)
                        Quantity = 10.0 * 1024.0 / 24.0
                        IsBillable = $true
                        DataType = $DataType
                    }
                }
            )
            $rows = @(Get-FixtureUsageTrend -ItemName $ItemName -Records $records -Start $startTime -End $endTime)
            $rows.Count | Should -BeGreaterThan 0
            $totalGB = [double](($rows | Measure-Object -Property IngestionGB -Sum).Sum)
            [math]::Abs($totalGB - 10.0 * ($endTime - $startTime).TotalDays) | Should -BeLessThan 0.00000001
            foreach ($row in $rows) {
                if ($ItemName -eq 'DataLakeMirroredVolumeTrend') {
                    $expression = Get-QueryExpression -Query $query -Pattern "extend \['Retained Raw Log Size'\] = (?<expression>[^|;]+)"
                    $retainedGB = Invoke-WorkbookArithmetic -Expression $expression -Bindings @{
                        'Mirrored Volume Size' = $row.IngestionGB
                        CoveredDays = $row.CoveredDays
                        chargeableDays = 270.0
                    }
                    [math]::Abs($retainedGB - 2700.0) | Should -BeLessThan 0.00000001
                }
                else {
                    $expression = Get-QueryExpression -Query $query -Pattern '(?<expression>licenseCount \* [0-9.]+ / 1024\.0 \* CoveredDays)'
                    $grantGB = Invoke-WorkbookArithmetic -Expression $expression -Bindings @{
                        licenseCount = $Licenses
                        CoveredDays = $row.CoveredDays
                    }
                    [math]::Abs($grantGB - 500.0 / 1024.0 * $row.IngestionGB / 10.0) | Should -BeLessThan 0.00000001
                }
                [math]::Abs($row.IngestionGB / $row.CoveredDays - 10.0) | Should -BeLessThan 0.00000001
            }
        }

        It 'includes the first overlapping source hour without an implicit selected-time filter' {
            $content = $script:workbookItems[$ItemName].content
            $content.PSObject.Properties.Name | Should -Not -Contain 'timeContextFromParameter'
            $content.timeContext.durationMs | Should -Be 0
            $content.query | Should -Match 'TimeGenerated >= bin\(selectedStart, 1h\) and TimeGenerated < selectedEnd'
            $content.query | Should -Match 'EndTime > selectedStart'
            $content.query | Should -Match 'min_of\(EndTime, selectedEnd\) - max_of\(StartTime, selectedStart\)'
            $content.query | Should -Match 'sum\(CoveredQuantity\)'
        }

        It 'does not invent a data point for empty Usage' {
            @(Get-FixtureUsageTrend -ItemName $ItemName -Records @() `
                -Start '2026-10-01T10:10:00Z' -End '2026-10-01T10:15:00Z').Count | Should -Be 0
        }
    }

    It 'uses the selected ingestion price <Price> for Other data' -ForEach @(
        @{ Price = 0.0 }
        @{ Price = 2.0 }
        @{ Price = 4.0 }
        @{ Price = 6.25 }
    ) {
        $query = Get-WorkbookQuery -ItemName 'query - 2'
        $expression = Get-QueryExpression -Query $query -Pattern '(?<expression>sizeOther\s*\*\s*(?:\{Price\}|[0-9.]+))'
        $actual = Invoke-WorkbookArithmetic -Expression $expression -Bindings @{ sizeOther = 12.0; Price = $Price }
        $actual | Should -Be (12.0 * $Price)
    }

    It 'normalizes six-hour ingestion and savings to a full daily rate in <ItemName>' -ForEach @(
        @{
            ItemName = 'WorkspaceAvgDailyBillableIngestion'
            Pattern = "summarize \['Avg Daily Billable Ingestion'\] = (?<expression>[^|;]+)"
            Expected = 24.0
        }
        @{
            ItemName = 'WorkspaceEstDailyIngestionCost'
            Pattern = "project \['Est. Daily Ingestion Cost'\] = (?<expression>[^|;]+)"
            Expected = 48.0
        }
        @{
            ItemName = 'FreeSentinelDataAvgPerDay'
            Pattern = "summarize \['Average Free Data Per Day'\] = (?<expression>[^|;]+)"
            Expected = 24.0
        }
        @{
            ItemName = 'FreeSentinelDataAvgDailySavings'
            Pattern = "project \['Avg Daily Free Data Savings'\] = (?<expression>[^|;]+)"
            Expected = 48.0
        }
    ) {
        $query = Get-WorkbookQuery -ItemName $ItemName
        $expression = Get-QueryExpression -Query $query -Pattern $Pattern
        $days = 0.25
        if ($query -match "let (?:selectedDays|periodDays) = max_of\(datetime_diff\('second', \{TimeRange:end\}, \{TimeRange:start\}\) / 86400\.0, (?<minimum>[0-9.]+)\);") {
            $days = [math]::Max($days, [double]$Matches['minimum'])
        }
        $actual = Invoke-WorkbookArithmetic -Expression $expression -Bindings @{
            Quantity = 6.0 * 1024.0
            BillableGB = 6.0
            FreeGB = 6.0
            selectedDays = $days
            periodDays = $days
            Price = 2.0
        }
        $actual | Should -Be $Expected
        $query | Should -Match 'let (?:selectedDays|periodDays) = \(\{TimeRange:end\} - \{TimeRange:start\}\) / 1d;'
    }

    It 'normalizes a <Label> Data Lake bucket by its actual covered days' -ForEach @(
        @{ Label = 'six-hour'; Days = 0.25 }
        @{ Label = 'partial two-hour edge'; Days = 2.0 / 24.0 }
        @{ Label = 'five-minute'; Days = 5.0 / 1440.0 }
        @{ Label = 'seven-day'; Days = 7.0 }
    ) {
        $query = Get-WorkbookQuery -ItemName 'DataLakeMirroredVolumeTrend'
        $expression = Get-QueryExpression -Query $query -Pattern "extend \['Retained Raw Log Size'\] = (?<expression>[^|;]+)"
        $actual = Invoke-WorkbookArithmetic -Expression $expression -Bindings @{
            'Mirrored Volume Size' = 10.0 * $Days
            CoveredDays = $Days
            selectedDays = 7.0
            chargeableDays = 270.0
        }
        [math]::Abs($actual - 2700.0) | Should -BeLessThan 0.000001
        $compressed = Get-QueryExpression -Query $query -Pattern "extend \['Billed Compressed Log Size'\] = (?<expression>[^|;]+)"
        $compressedGB = Invoke-WorkbookArithmetic -Expression $compressed -Bindings @{
            'Retained Raw Log Size' = $actual
            compressionRatio = 6.0
        }
        [math]::Abs($compressedGB - 450.0) | Should -BeLessThan 0.000001
    }

    It 'clips trend buckets to both selected edges and preserves chart output columns' {
        $query = Get-WorkbookQuery -ItemName 'DataLakeMirroredVolumeTrend'
        $query | Should -Match 'min_of\(TimeGenerated \+ timeGrain, selectedEnd\)'
        $query | Should -Match 'max_of\(TimeGenerated, selectedStart\)'
        $query | Should -Match 'TimeGenerated >= bin\(selectedStart, 1h\) and TimeGenerated < selectedEnd'
        $query | Should -Match "project TimeGenerated, \['Mirrored Volume Size'\], \['Retained Raw Log Size'\], \['Billed Compressed Log Size'\]"
    }

    It 'does not round a partial-day Data Lake rate up to a full day in <ItemName>' -ForEach @(
        @{ ItemName = 'DataLakeAverageMirroredVolume' }
        @{ ItemName = 'DataLakeEstimatedDailyCost' }
        @{ ItemName = 'DataLakeEstimatedStorageCostPeriod' }
        @{ ItemName = 'DataLakeStorageCostByTable' }
    ) {
        $query = Get-WorkbookQuery -ItemName $ItemName
        $query | Should -Match 'let selectedDays = \(\{TimeRange:end\} - \{TimeRange:start\}\) / 1d;'
        $query | Should -Not -Match 'selectedDays = max_of'
    }

    It 'keeps the short-range Data Lake table estimate consistent with a 10 GB/day trend' {
        $query = Get-WorkbookQuery -ItemName 'DataLakeStorageCostByTable'
        $daily = Get-QueryExpression -Query $query -Pattern 'extend AverageDailyLogSize = (?<expression>[^|;]+)'
        $dailyGB = Invoke-WorkbookArithmetic -Expression $daily -Bindings @{ RawGB = 5.0; selectedDays = 0.5 }
        $retained = Get-QueryExpression -Query $query -Pattern 'extend RetainedRawLogSize = (?<expression>[^|;]+)'
        (Invoke-WorkbookArithmetic -Expression $retained -Bindings @{
            AverageDailyLogSize = $dailyGB
            chargeableDays = 270.0
        }) | Should -Be 2700.0
    }

    It 'does not transfer unused daily allowance in <ItemName>' -ForEach @(
        @{ ItemName = 'EligibleE5Ingestion'; Licenses = 100.0; DataType = 'SigninLogs' }
        @{ ItemName = 'EstimateE5Discount'; Licenses = 100.0; DataType = 'SigninLogs' }
        @{ ItemName = 'DfSP2GrantUsed'; Licenses = 1.0; DataType = 'SecurityEvent' }
        @{ ItemName = 'DfSP2EstimatedSavings'; Licenses = 1.0; DataType = 'SecurityEvent' }
    ) {
        $query = Get-WorkbookQuery -ItemName $ItemName
        $records = @(
            @{ TimeGenerated = [datetimeoffset]'2026-10-01T12:00:00Z'; Quantity = 1000.0; IsBillable = $true; DataType = $DataType }
        )
        $actual = Get-FixtureGrantUsed -Query $query -Records $records -LicenseCount $Licenses `
            -Start '2026-10-01T00:00:00Z' -End '2026-10-03T00:00:00Z'
        $actual | Should -Be (500.0 / 1024.0)
        $query | Should -Match "iif\(isnull\(licenseCount\), 'N/A',"
    }

    It 'caps separately across UTC days and excludes nonbillable, ineligible and end-boundary data in <ItemName>' -ForEach @(
        @{ ItemName = 'EligibleE5Ingestion'; Licenses = 100.0; DataType = 'AADRiskyUsers' }
        @{ ItemName = 'DfSP2GrantUsed'; Licenses = 1.0; DataType = 'SecurityEvent' }
    ) {
        $query = Get-WorkbookQuery -ItemName $ItemName
        $records = @(
            @{ TimeGenerated = [datetimeoffset]'2026-10-01T23:30:00Z'; Quantity = 1000.0; IsBillable = $true; DataType = $DataType }
            @{ TimeGenerated = [datetimeoffset]'2026-10-02T03:30:00+02:00'; Quantity = 100.0; IsBillable = $true; DataType = $DataType }
            @{ TimeGenerated = [datetimeoffset]'2026-10-02T12:00:00Z'; Quantity = 900.0; IsBillable = $false; DataType = $DataType }
            @{ TimeGenerated = [datetimeoffset]'2026-10-02T12:00:00Z'; Quantity = 900.0; IsBillable = $true; DataType = 'NotEligible' }
            @{ TimeGenerated = [datetimeoffset]'2026-10-03T00:00:00Z'; Quantity = 900.0; IsBillable = $true; DataType = $DataType }
        )
        $actual = Get-FixtureGrantUsed -Query $query -Records $records -LicenseCount $Licenses `
            -Start '2026-10-01T00:00:00Z' -End '2026-10-03T00:00:00Z'
        $actual | Should -Be (600.0 / 1024.0)
        (Get-FixtureGrantUsed -Query $query -Records @() -LicenseCount $Licenses `
            -Start '2026-10-01T00:00:00Z' -End '2026-10-03T00:00:00Z') | Should -Be 0.0
    }

    It 'bases <ItemName> savings on daily-capped use at the selected price' -ForEach @(
        @{ ItemName = 'EstimateE5Discount' }
        @{ ItemName = 'DfSP2EstimatedSavings' }
    ) {
        $query = Get-WorkbookQuery -ItemName $ItemName
        $expression = Get-QueryExpression -Query $query -Pattern "round\((?<expression>grantUsedGB \* todouble\('\{Price\}'\)), 2\)"
        (Invoke-WorkbookArithmetic -Expression $expression -Bindings @{ grantUsedGB = 500.0 / 1024.0; Price = 2.0 }) |
            Should -Be (1000.0 / 1024.0)
        (Invoke-WorkbookArithmetic -Expression $expression -Bindings @{ grantUsedGB = 500.0 / 1024.0; Price = 0.0 }) |
            Should -Be 0.0
    }

    It 'uses the same risk-inclusive Microsoft 365 eligibility set in <ItemName>' -ForEach @(
        @{ ItemName = 'E5IngestionSize' }
        @{ ItemName = 'EligibleE5Ingestion' }
        @{ ItemName = 'EstimateE5Discount' }
        @{ ItemName = 'E5EligibleDataDetail' }
        @{ ItemName = 'E5DailyIngestionVsGrant' }
    ) {
        $expected = Get-EligibleTables -Query (Get-WorkbookQuery -ItemName 'E5EligibleDataDetail')
        $actual = Get-EligibleTables -Query (Get-WorkbookQuery -ItemName $ItemName)
        @($actual | Where-Object { $_ -in @('AADUserRiskEvents', 'AADRiskyUsers') }).Count | Should -Be 2
        @(Compare-Object ($expected | Sort-Object) ($actual | Sort-Object)).Count | Should -Be 0
        @($actual | Sort-Object -Unique).Count | Should -Be $actual.Count
    }

    It 'counts intersected UTC dates rather than pooling elapsed-day allowances in <ItemName>' -ForEach @(
        @{ ItemName = 'DataGrantLimit' }
        @{ ItemName = 'DfSP2PeriodGrant' }
    ) {
        $query = Get-WorkbookQuery -ItemName $ItemName
        $query | Should -Match 'ceiling\(\(\{TimeRange:end\} - startofday\(\{TimeRange:start\}\)\) / 1d\)'
        $query | Should -Not -Match 'periodDays = max_of'
    }

    It 'prorates the visible comparison to partial edge buckets in <ItemName>' -ForEach @(
        @{ ItemName = 'E5DailyIngestionVsGrant' }
        @{ ItemName = 'DfSP2DailyIngestionVsGrant' }
    ) {
        $query = Get-WorkbookQuery -ItemName $ItemName
        $query | Should -Match 'min_of\(TimeGenerated \+ timeGrain, selectedEnd\)'
        $query | Should -Match 'max_of\(TimeGenerated, selectedStart\)'
        $query | Should -Match '\* CoveredDays\)'
        $query | Should -Match "project TimeGenerated, \['Ingestion Size'\], \['Grant Limit for Interval'\]"
    }

    It 'removes the unused monthly licensing-price control while retaining protected-node input' {
        $script:workbookText | Should -Not -Match 'DfSP2LicensePrice'
        $parameters = $script:workbookItems['parameters - Defender for Servers Plan 2 benefit'].content.parameters
        @($parameters).Count | Should -Be 1
        $parameters[0].name | Should -Be 'TotalDfSP2Licenses'
    }

    It 'excludes the selected end from Defender eligible totals in <ItemName>' -ForEach @(
        @{ ItemName = 'DfSP2IngestionSize current' }
        @{ ItemName = 'DfSP2CapacityDetailCurrent' }
    ) {
        $query = Get-WorkbookQuery -ItemName $ItemName
        $start = [datetimeoffset]'2026-10-01T00:00:00Z'
        $end = [datetimeoffset]'2026-10-02T00:00:00Z'
        $records = @(
            @{ TimeGenerated = [datetimeoffset]'2026-10-01T12:00:00Z'; Quantity = 100.0 }
            @{ TimeGenerated = $end; Quantity = 900.0 }
        )
        if ($query.Contains('TimeGenerated between ({TimeRange:start} .. {TimeRange:end})')) {
            $selected = $records | Where-Object { $_.TimeGenerated -ge $start -and $_.TimeGenerated -le $end }
        }
        elseif ($query.Contains('TimeGenerated >= {TimeRange:start} and TimeGenerated < {TimeRange:end}')) {
            $selected = $records | Where-Object { $_.TimeGenerated -ge $start -and $_.TimeGenerated -lt $end }
        }
        else {
            throw 'Unexpected selected-time predicate in the eligibility query.'
        }
        $expression = Get-QueryExpression -Query $query -Pattern 'summarize (?:EligibleGB|TableSizeGB) = (?<expression>sum\(Quantity\) / 1024\.0)'
        $actual = Invoke-WorkbookArithmetic -Expression $expression -Bindings @{
            Quantity = [double](($selected | Measure-Object -Property Quantity -Sum).Sum)
        }
        $actual | Should -Be (100.0 / 1024.0)
    }

    It 'uses the same exclusive selected end throughout the workbook' {
        [regex]::Matches($script:workbookText, 'TimeGenerated\s+between\s+\(\{TimeRange:start\}\s*\.\.\s*\{TimeRange:end\}\)').Count |
            Should -Be 0
    }

    It 'scans retained history independently of the global time selection in <ItemName>' -ForEach @(
        @{ ItemName = 'AverageDailyRetentionCost' }
        @{ ItemName = 'RetentionCostForTimeRange' }
        @{ ItemName = 'RetentionDataDetail' }
    ) {
        $content = $script:workbookItems[$ItemName].content
        $content.PSObject.Properties.Name | Should -Not -Contain 'timeContextFromParameter'
        $content.timeContext.durationMs | Should -Be 0
        $content.query | Should -Match 'TimeGenerated < startofday\(now\(\)\) - 90d'
    }

    It 'uses the actual selected duration only as the retention cost multiplier in <ItemName>' -ForEach @(
        @{ ItemName = 'RetentionCostForTimeRange' }
        @{ ItemName = 'RetentionDataDetail' }
    ) {
        $query = Get-WorkbookQuery -ItemName $ItemName
        $query | Should -Match 'let selectedDays = \(\{TimeRange:end\} - \{TimeRange:start\}\) / 1d;'
        $query | Should -Not -Match 'TimeGenerated (?:between|>=) \(\{TimeRange:start\}'
    }
}
