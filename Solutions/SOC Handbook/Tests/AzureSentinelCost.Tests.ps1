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
        $expression = [regex]::Replace($expression, 'sum\((Quantity|CoveredQuantity|BinCoveredQuantity)\)', '$1')
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

        $match = [regex]::Match($Query, 'let (?:eligibleTables|freeTypes) = dynamic\((\[[^\]]+\])\)')
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

    function Get-FixtureCoveredUsage {
        param(
            [string]$Query,
            [object[]]$Records,
            [datetimeoffset]$Start,
            [datetimeoffset]$End
        )

        $startUtc = $Start.ToUniversalTime()
        $endUtc = $End.ToUniversalTime()
        $tableSet = if ($Query.Contains('DataType in (eligibleTables)') -or $Query.Contains('DataType in (freeTypes)')) {
            Get-EligibleTables -Query $Query
        }
        foreach ($record in $Records) {
            $timeGenerated = ([datetimeoffset]$record.TimeGenerated).ToUniversalTime()
            $sourceStart = ([datetimeoffset]$record.StartTime).ToUniversalTime()
            $sourceEnd = ([datetimeoffset]$record.EndTime).ToUniversalTime()
            if ($timeGenerated -lt $startUtc.AddHours(-1) -or $timeGenerated -ge $endUtc.AddHours(1) -or
                $sourceStart -ge $endUtc -or $sourceEnd -le $startUtc -or $sourceEnd -le $sourceStart -or
                ($Query.Contains('IsBillable == true') -and -not $record.IsBillable) -or
                ($Query.Contains('IsBillable == false') -and $record.IsBillable) -or
                ($Query.Contains("column_ifexists('Plan'") -and $record.Plan -ne 'Analytics') -or
                ($tableSet -and $record.DataType -notin $tableSet)) {
                continue
            }
            $coveredStart = if ($sourceStart -gt $startUtc) { $sourceStart } else { $startUtc }
            $coveredEnd = if ($sourceEnd -lt $endUtc) { $sourceEnd } else { $endUtc }
            [pscustomobject]@{
                TimeGenerated = $timeGenerated
                StartTime = $sourceStart
                EndTime = $sourceEnd
                Quantity = [double]$record.Quantity
                CoveredQuantity = [double]$record.Quantity * ($coveredEnd - $coveredStart).Ticks /
                    ($sourceEnd - $sourceStart).Ticks
                DataType = $record.DataType
            }
        }
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
        $allocation = Get-QueryExpression -Query $query -Pattern 'extend BinCoveredQuantity = (?<expression>[^|]+)'
        if ($allocation.Trim() -ne 'CoveredQuantity * ((min_of(BinStart + timeGrain, CoveredEnd) - max_of(BinStart, CoveredStart)) / (CoveredEnd - CoveredStart))') {
            throw 'Trend queries must prorate each clipped source interval across its intersecting bins.'
        }
        $startUtc = $Start.ToUniversalTime()
        $endUtc = $End.ToUniversalTime()
        $grain = Get-FixtureTimeGrain -Query $query -Duration ($endUtc - $startUtc)
        $bins = @{}
        foreach ($record in Get-FixtureCoveredUsage -Query $query -Records $Records -Start $startUtc -End $endUtc) {
            $coveredStart = if ($record.StartTime -gt $startUtc) { $record.StartTime } else { $startUtc }
            $coveredEnd = if ($record.EndTime -lt $endUtc) { $record.EndTime } else { $endUtc }
            $coveredQuantity = $record.CoveredQuantity
            $binTicks = $coveredStart.UtcTicks - ($coveredStart.UtcTicks % $grain.Ticks)
            while ($binTicks -lt $coveredEnd.UtcTicks) {
                $binStart = [datetimeoffset]::new($binTicks, [timespan]::Zero)
                $binEnd = if ($binStart.Add($grain) -lt $coveredEnd) { $binStart.Add($grain) } else { $coveredEnd }
                $partStart = if ($binStart -gt $coveredStart) { $binStart } else { $coveredStart }
                $binQuantity = $coveredQuantity * ($binEnd - $partStart).Ticks / ($coveredEnd - $coveredStart).Ticks
                $bins[$binTicks] += $binQuantity
                $binTicks += $grain.Ticks
            }
        }
        $expression = Get-QueryExpression -Query $query -Pattern "summarize \['(?:Mirrored Volume Size|Ingestion Size|Free Data Size)'\] = (?<expression>[^|]+) by TimeGenerated = BinStart"
        foreach ($bucketTicks in $bins.Keys | Sort-Object) {
            $bucket = [datetimeoffset]::new($bucketTicks, [timespan]::Zero)
            $coveredStart = if ($bucket -gt $startUtc) { $bucket } else { $startUtc }
            $coveredEnd = if ($bucket.Add($grain) -lt $endUtc) { $bucket.Add($grain) } else { $endUtc }
            [pscustomobject]@{
                TimeGenerated = $bucket
                CoveredDays = ($coveredEnd - $coveredStart).TotalDays
                IngestionGB = Invoke-WorkbookArithmetic -Expression $expression -Bindings @{
                    BinCoveredQuantity = $bins[$bucketTicks]
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

        $dailyPipeline = '(?s)mv-expand GrantDay = range\(startofday\(OverlapStart\), startofday\(OverlapEnd\), 1d\).*summarize DailyEligibleGB = sum\(CoveredQuantity\) / 1000\.0 by GrantDay.*summarize sum\(min_of\(DailyEligibleGB, dailyGrantGB \* CoveredDays\)\)'
        if ($Query -notmatch $dailyPipeline) {
            throw 'The embedded query must allocate clipped source intervals across UTC days and prorate each cap.'
        }
        $dayCoverage = Get-QueryExpression -Query $Query -Pattern 'extend CoveredDays = (?<expression>[^|]+)'
        if ($dayCoverage.Trim() -ne '(min_of(GrantDay + 1d, selectedEnd) - max_of(GrantDay, selectedStart)) / 1d') {
            throw 'Grant queries must cap each UTC day using only its selected duration.'
        }
        if ($Query -notmatch 'TimeGenerated >= selectedStart - 1h and TimeGenerated < selectedEnd \+ 1h' -or
            $Query -notmatch 'StartTime < selectedEnd and EndTime > selectedStart' -or
            $Query -notmatch 'extend OverlapStart = max_of\(StartTime, selectedStart\), OverlapEnd = min_of\(EndTime, selectedEnd\)' -or
            $Query -notmatch 'extend CoveredQuantity = Quantity \* \(\(min_of\(OverlapEnd, GrantDay \+ 1d\) - max_of\(OverlapStart, GrantDay\)\) / \(EndTime - StartTime\)\)' -or
            $Query -notmatch 'IsBillable == true and DataType in \(eligibleTables\)' -or
            $Query -notmatch "where tostring\(column_ifexists\('Plan', ''\)\) =~ 'Analytics'") {
            throw 'Grant queries must include overlapping source intervals and Analytics-plan data only.'
        }
        $allowance = Get-QueryExpression -Query $Query -Pattern 'let dailyGrantGB = (?<expression>[^;]+);'
        $dailyGrantGB = Invoke-WorkbookArithmetic -Expression $allowance -Bindings @{ licenseCount = $LicenseCount }
        $eligibleTables = Get-EligibleTables -Query $Query
        $startUtc = $Start.ToUniversalTime()
        $endUtc = $End.ToUniversalTime()
        $selected = @($Records | Where-Object {
            $timeGenerated = ([datetimeoffset]$_.TimeGenerated).ToUniversalTime()
            $sourceStart = ([datetimeoffset]$_.StartTime).ToUniversalTime()
            $sourceEnd = ([datetimeoffset]$_.EndTime).ToUniversalTime()
            $timeGenerated -ge $startUtc.AddHours(-1) -and $timeGenerated -lt $endUtc.AddHours(1) -and
            $sourceStart -lt $endUtc -and $sourceEnd -gt $startUtc -and $sourceEnd -gt $sourceStart -and
            $_.IsBillable -and $_.DataType -in $eligibleTables -and $_.Plan -eq 'Analytics'
        })
        $daily = @{}
        foreach ($record in $selected) {
            $sourceStart = ([datetimeoffset]$record.StartTime).ToUniversalTime()
            $sourceEnd = ([datetimeoffset]$record.EndTime).ToUniversalTime()
            $coveredStart = if ($sourceStart -gt $startUtc) { $sourceStart } else { $startUtc }
            $coveredEnd = if ($sourceEnd -lt $endUtc) { $sourceEnd } else { $endUtc }
            $dayTicks = $coveredStart.UtcTicks - ($coveredStart.UtcTicks % [timespan]::TicksPerDay)
            while ($dayTicks -lt $coveredEnd.UtcTicks) {
                $dayStart = [datetimeoffset]::new($dayTicks, [timespan]::Zero)
                $dayEnd = $dayStart.AddDays(1)
                $partStart = if ($coveredStart -gt $dayStart) { $coveredStart } else { $dayStart }
                $partEnd = if ($coveredEnd -lt $dayEnd) { $coveredEnd } else { $dayEnd }
                $daily[$dayTicks] += [double]$record.Quantity * ($partEnd - $partStart).Ticks /
                    ($sourceEnd - $sourceStart).Ticks
                $dayTicks += [timespan]::TicksPerDay
            }
        }
        $total = 0.0
        foreach ($dayTicks in $daily.Keys) {
            $dayStart = [datetimeoffset]::new($dayTicks, [timespan]::Zero)
            $coveredStart = if ($dayStart -gt $startUtc) { $dayStart } else { $startUtc }
            $dayEnd = $dayStart.AddDays(1)
            $coveredEnd = if ($dayEnd -lt $endUtc) { $dayEnd } else { $endUtc }
            $coveredDays = ($coveredEnd - $coveredStart).TotalDays
            $dailyGB = [double]$daily[$dayTicks] / 1000.0
            $total += [math]::Min($dailyGB, $dailyGrantGB * $coveredDays)
        }
        $total
    }

    function Get-FixtureTierUsage {
        param([object[]]$Records, [datetimeoffset]$Now, [string]$Workspace)

        $query = Get-WorkbookQuery -ItemName 'CommitmentTierUsageContext'
        if ($query -notmatch 'Usage\s*\|\s*where TimeGenerated >= historyProbeStart - 1h and TimeGenerated < now\(\) \+ 1h\s*\|\s*where StartTime >= historyProbeStart and StartTime < now\(\)\s*\|\s*where IsBillable == true' -or
            $query -notmatch "UsagePlan =~ 'Analytics'.*UnknownPlanRows") {
            throw 'Tier estimates must use billable Usage intervals, confirmed Analytics plans, and the unknown-plan gate.'
        }
        if ($Workspace) {
            $resources = $script:workbookItems['CommitmentTierUsageContext'].content.crossComponentResources
            if ($resources.Count -ne 1 -or $resources[0] -ne '{CommitmentWorkspace}') {
                throw 'Tier usage must be scoped to the single commitment workspace.'
            }
            $Records = @($Records | Where-Object { $_.Workspace -eq $Workspace })
        }
        $reviewDays = [double](Get-QueryExpression -Query $query -Pattern 'let reviewDays = (?<expression>[0-9.]+);')
        $reviewStart = $Now.AddDays(-[double](Get-QueryExpression -Query $query -Pattern 'let reviewStart = ago\((?<expression>[0-9.]+)d\);'))
        $probeStart = $Now.AddDays(-[double](Get-QueryExpression -Query $query -Pattern 'let historyProbeStart = ago\((?<expression>[0-9.]+)d\);'))
        $selected = @($Records | Where-Object {
            $_.IsBillable -and $_.StartTime -ge $probeStart -and $_.StartTime -lt $Now
        })
        $analytics = @($selected | Where-Object { $_.Plan -eq 'Analytics' })
        $firstObserved = ($analytics | Sort-Object StartTime | Select-Object -First 1).StartTime
        $observedDays = if ($null -eq $firstObserved) { 0.0 } else {
            [math]::Min($reviewDays, [math]::Truncate(($Now - $firstObserved).TotalSeconds) / 86400.0)
        }
        $daysRemaining = [int][math]::Ceiling([math]::Max($reviewDays - $observedDays, 0.0))
        $totalMB = 0.0
        $unknownPlanRows = @($selected | Where-Object {
            $_.StartTime -ge $reviewStart -and $_.Plan -notin @('Analytics', 'Basic', 'Auxiliary')
        }).Count
        foreach ($record in $analytics | Where-Object { $_.StartTime -ge $reviewStart }) {
            $totalMB += $record.Quantity
        }
        $averageDailyGB = if ($daysRemaining -eq 0 -and $unknownPlanRows -eq 0) {
            $expression = Get-QueryExpression -Query $query -Pattern 'AvgDailyGB = iif\(DaysRemaining == 0 and UnknownPlanRows == 0, (?<expression>[^,]+), real\(null\)\)'
            Invoke-WorkbookArithmetic -Expression $expression -Bindings @{ TotalBilledMB = $totalMB; reviewDays = $reviewDays }
        }
        [pscustomobject]@{
            DaysRemaining = $daysRemaining
            AverageDailyGB = $averageDailyGB
        }
    }
}

Describe 'AzureSentinelCost offline calculation regressions' {
    It 'rejects an inflated bin allocation in <ItemName>' -ForEach @(
        @{ ItemName = 'DataLakeMirroredVolumeTrend' }
        @{ ItemName = 'E5DailyIngestionVsGrant' }
        @{ ItemName = 'DfSP2DailyIngestionVsGrant' }
        @{ ItemName = 'FreeDataVsBillableDataDaily' }
    ) {
        $content = $script:workbookItems[$ItemName].content
        $original = $content.query
        try {
            $content.query = $original.Replace('BinCoveredQuantity = CoveredQuantity *', 'BinCoveredQuantity = 2.0 * CoveredQuantity *')
            $content.query | Should -Not -Be $original
            {
                Get-FixtureUsageTrend -ItemName $ItemName -Records @() `
                    -Start ([datetimeoffset]'2026-10-01T00:05:00Z') -End ([datetimeoffset]'2026-10-01T00:15:00Z')
            } | Should -Throw '*prorate each clipped source interval*'
        }
        finally {
            $content.query = $original
        }
    }

    It 'rejects a full-day cap substituted for a partial UTC day in <ItemName>' -ForEach @(
        @{ ItemName = 'EligibleE5Ingestion' }
        @{ ItemName = 'EstimateE5Discount' }
        @{ ItemName = 'DfSP2GrantUsed' }
        @{ ItemName = 'DfSP2EstimatedSavings' }
    ) {
        $original = Get-WorkbookQuery -ItemName $ItemName
        $query = $original.Replace(
            'CoveredDays = (min_of(GrantDay + 1d, selectedEnd) - max_of(GrantDay, selectedStart)) / 1d',
            'CoveredDays = 1.0'
        )
        $query | Should -Not -Be $original
        {
            Get-FixtureGrantUsed -Query $query -Records @() -LicenseCount 1 `
                -Start ([datetimeoffset]'2026-10-01T00:05:00Z') -End ([datetimeoffset]'2026-10-01T00:15:00Z')
        } | Should -Throw '*cap each UTC day using only its selected duration*'
    }

    It 'defaults the global time filter to 30 days and preserves custom time ranges' {
        $timeRange = @($script:workbook.items | ForEach-Object { $_.content.parameters }) | Where-Object name -eq 'TimeRange'
        $timeRange.value.durationMs | Should -Be 2592000000
        $timeRange.typeSettings.selectableValues.durationMs | Should -Contain 2592000000
        $timeRange.typeSettings.allowCustom | Should -BeTrue
    }

    It 'excludes billable records from <ItemName> volumes and savings' -ForEach @(
        @{ ItemName = 'FreeSentinelDataAvgPerDay'; Pattern = "\['Average Free Data Per Day'\] = (?<expression>[^|;]+)"; Expected = 2.0 }
        @{ ItemName = 'FreeSentinelDataAvgDailySavings'; Pattern = "\['Avg Daily Free Data Savings'\] = (?<expression>[^|;]+)"; Expected = 4.0 }
        @{ ItemName = 'FreeSentinelDataPeriod'; Pattern = "\['Free Data'\] = (?<expression>[^|;]+)"; Expected = 2.0 }
        @{ ItemName = 'FreeSentinelDataSavingsPeriod'; Pattern = "\['Estimated Free Data Savings'\] = (?<expression>[^|;]+)"; Expected = 4.0 }
        @{ ItemName = 'FreeSentinelDataDetail'; Pattern = 'TableSizeGB = (?<expression>[^|;]+?) by DataType'; Expected = 2.0 }
        @{ ItemName = 'FreeDataVsBillableDataDaily'; Pattern = "\['Free Data Size'\] = (?<expression>[^|;]+?) by TimeGenerated = BinStart"; Expected = 2.0 }
    ) {
        $query = Get-WorkbookQuery -ItemName $ItemName
        $start = [datetimeoffset]'2026-10-01T00:00:00Z'
        $end = $start.AddDays(1)
        $records = @(
            @{ TimeGenerated = $start.AddHours(12); StartTime = $start.AddHours(12); EndTime = $start.AddHours(13); Quantity = 1000.0; IsBillable = $true; DataType = 'SecurityAlert'; Plan = 'Analytics' }
            @{ TimeGenerated = $start.AddHours(12); StartTime = $start.AddHours(12); EndTime = $start.AddHours(13); Quantity = 2000.0; IsBillable = $false; DataType = 'SecurityAlert'; Plan = 'Analytics' }
            @{ TimeGenerated = $start.AddHours(12); StartTime = $start.AddHours(12); EndTime = $start.AddHours(13); Quantity = 4000.0; IsBillable = $false; DataType = 'NotEligible'; Plan = 'Analytics' }
            @{ TimeGenerated = $start.AddHours(-1); StartTime = $start.AddHours(-1); EndTime = $start; Quantity = 8000.0; IsBillable = $false; DataType = 'SecurityAlert'; Plan = 'Analytics' }
            @{ TimeGenerated = $end; StartTime = $end; EndTime = $end.AddHours(1); Quantity = 8000.0; IsBillable = $false; DataType = 'SecurityAlert'; Plan = 'Analytics' }
        )
        $freeTypes = (Get-QueryExpression -Query $query -Pattern 'let freeTypes = dynamic\((?<expression>\[[^\]]+\])\);') | ConvertFrom-Json
        $selected = @(Get-FixtureCoveredUsage -Query $query -Records $records -Start $start -End $end)
        $coveredQuantity = [double](($selected | Measure-Object -Property CoveredQuantity -Sum).Sum)
        $expression = Get-QueryExpression -Query $query -Pattern $Pattern
        $actual = if ($ItemName -eq 'FreeDataVsBillableDataDaily') {
            [double]((Get-FixtureUsageTrend -ItemName $ItemName -Records $records -Start $start -End $end |
                Measure-Object -Property IngestionGB -Sum).Sum)
        }
        else {
            Invoke-WorkbookArithmetic -Expression $expression -Bindings @{
            CoveredQuantity = $coveredQuantity
            FreeGB = $coveredQuantity / 1000.0
            periodDays = ($end - $start).TotalDays
            Price = 2.0
            }
        }
        $actual | Should -Be $Expected
        $query.IndexOf('| where IsBillable == false') | Should -BeGreaterThan $query.IndexOf('Usage')
        $query.IndexOf('| where IsBillable == false') | Should -BeLessThan $query.IndexOf('| summarize')
    }

    It 'calculates <AverageGB> GB/day from billable Usage without counting probe-only or out-of-range volume' -ForEach @(
        @{ AverageGB = 0.0 }
        @{ AverageGB = 20.0 }
        @{ AverageGB = 50.0 }
        @{ AverageGB = 100.0 }
        @{ AverageGB = 5000.0 }
        @{ AverageGB = 5001.0 }
    ) {
        $now = [datetimeoffset]'2026-10-29T12:00:00Z'
        $records = @(
            @{ TimeGenerated = $now.AddDays(-31.5); StartTime = $now.AddDays(-31.5); Quantity = 1e9; IsBillable = $true; Plan = 'Analytics' }
            @{ TimeGenerated = $now.AddDays(-15); StartTime = $now.AddDays(-15); Quantity = $AverageGB * 31.0 * 1000.0; IsBillable = $true; Plan = 'Analytics' }
            @{ TimeGenerated = $now.AddDays(-2); StartTime = $now.AddDays(-2); Quantity = 1e9; IsBillable = $false; Plan = 'Analytics' }
            @{ TimeGenerated = $now.AddDays(-33); StartTime = $now.AddDays(-33); Quantity = 1e9; IsBillable = $true; Plan = 'Analytics' }
            @{ TimeGenerated = $now; StartTime = $now; Quantity = 1e9; IsBillable = $true; Plan = 'Analytics' }
        )
        $actual = Get-FixtureTierUsage -Records $records -Now $now
        $actual.DaysRemaining | Should -Be 0
        $actual.AverageDailyGB | Should -Be $AverageGB
    }

    It 'preserves the 31-day readiness gate for <Label>' -ForEach @(
        @{ Label = 'no history'; BillableAge = $null; ExpectedDays = 31 }
        @{ Label = 'ten days of billable history'; BillableAge = 10.0; ExpectedDays = 21 }
        @{ Label = 'a fractional final day'; BillableAge = 30.5; ExpectedDays = 1 }
        @{ Label = 'exactly 31 days of billable history'; BillableAge = 31.0; ExpectedDays = 0 }
    ) {
        $now = [datetimeoffset]'2026-10-29T12:00:00Z'
        $records = @(
            @{ TimeGenerated = $now.AddDays(-31.5); StartTime = $now.AddDays(-31.5); Quantity = 1000.0; IsBillable = $false; Plan = 'Analytics' }
            @{ TimeGenerated = $now.AddDays(-33); StartTime = $now.AddDays(-33); Quantity = 1000.0; IsBillable = $true; Plan = 'Analytics' }
            if ($null -ne $BillableAge) {
                @{ TimeGenerated = $now.AddDays(-$BillableAge); StartTime = $now.AddDays(-$BillableAge); Quantity = 1000.0; IsBillable = $true; Plan = 'Analytics' }
            }
        )
        $actual = Get-FixtureTierUsage -Records $records -Now $now
        $actual.DaysRemaining | Should -Be $ExpectedDays
        if ($ExpectedDays -gt 0) {
            $actual.AverageDailyGB | Should -BeNullOrEmpty
        }
        else {
            $actual.AverageDailyGB | Should -Be (1.0 / 31.0)
        }
    }

    It 'withholds a commitment volume estimate when the review period has unknown Usage plans' {
        $now = [datetimeoffset]'2026-10-29T12:00:00Z'
        $records = @(
            @{ TimeGenerated = $now.AddDays(-31.5); StartTime = $now.AddDays(-31.5); Quantity = 0.0; IsBillable = $true; Plan = 'Analytics' }
            @{ TimeGenerated = $now.AddDays(-15); StartTime = $now.AddDays(-15); Quantity = 31000.0; IsBillable = $true; Plan = 'Analytics' }
            @{ TimeGenerated = $now.AddDays(-2); StartTime = $now.AddDays(-2); Quantity = 1000.0; IsBillable = $true; Plan = '' }
        )
        $actual = Get-FixtureTierUsage -Records $records -Now $now
        $actual.DaysRemaining | Should -Be 0
        $actual.AverageDailyGB | Should -BeNullOrEmpty
        (Get-WorkbookQuery -ItemName 'CommitmentTierUsageContext') |
            Should -Match "UnknownPlanRows > 0, 'Not evaluated - unknown Usage plan'"
    }

    It 'withholds a combined tier recommendation when multiple workspaces are selected' {
        $query = Get-WorkbookQuery -ItemName 'CommitmentTierUsageContext'
        $now = [datetimeoffset]'2026-10-29T12:00:00Z'
        $records = @(
            @{ TimeGenerated = $now.AddDays(-31.5); StartTime = $now.AddDays(-31.5); Quantity = 0.0; IsBillable = $true; Plan = 'Analytics' }
            @{ TimeGenerated = $now.AddDays(-15); StartTime = $now.AddDays(-15); Quantity = 40.0 * 31.0 * 1000.0; IsBillable = $true; Plan = 'Analytics'; Workspace = 'workspace-one' }
            @{ TimeGenerated = $now.AddDays(-15); StartTime = $now.AddDays(-15); Quantity = 40.0 * 31.0 * 1000.0; IsBillable = $true; Plan = 'Analytics'; Workspace = 'workspace-two' }
        )
        $actual = Get-FixtureTierUsage -Records $records -Now $now

        $actual.AverageDailyGB | Should -Be 80.0
        $query | Should -Match "extend volumeCeiling = case\(currentTier == 'Multiple workspaces', 'Not evaluated',"
        $query | Should -Match "extend reviewStatus = case\(currentTier == 'Multiple workspaces', 'Not evaluated',"
    }

    It 'provides a required single-workspace selector with a deterministic default and no All option' {
        $parameters = $script:workbookItems['parameters - commitment tier current'].content.parameters
        $selector = $parameters | Where-Object name -eq 'CommitmentWorkspace'
        $selector.type | Should -Be 2
        $selector.isRequired | Should -BeTrue
        $selector.multiSelect | Should -BeFalse
        $selector.query | Should -Match "where name contains 'SecurityInsights'"
        $selector.query | Should -Match 'summarize by workspaceResourceId'
        $selector.query | Should -Match 'join kind=inner'
        $selector.query | Should -Match 'preference = iif\(workspaceResourceId in~ \(\{Workspace\}\), 0, 1\)'
        $selector.query | Should -Match 'order by preference asc, workspaceName asc, workspaceResourceId asc'
        $selector.query | Should -Match 'project value = workspaceResourceId, label = workspaceName, selected = true'
        ($selector | ConvertTo-Json -Depth 20) | Should -Not -Match 'value::all'
        @($parameters.name).IndexOf('CommitmentWorkspace') | Should -BeLessThan (@($parameters.name).IndexOf('CurrentCommitmentTier'))
    }

    It 'uses the same single workspace for current tier detection and Usage history without changing global scope' {
        $parameters = $script:workbookItems['parameters - commitment tier current'].content.parameters
        $current = $parameters | Where-Object name -eq 'CurrentCommitmentTier'
        $current.query | Should -Match "where id =~ '\{CommitmentWorkspace\}'"
        $current.query | Should -Not -Match '\{Workspace\}|value::all'
        $current.query | Should -Match "WorkspaceCount == 0, 'Not available'"
        $usage = $script:workbookItems['CommitmentTierUsageContext'].content
        @($usage.crossComponentResources).Count | Should -Be 1
        $usage.crossComponentResources[0] | Should -Be '{CommitmentWorkspace}'
        $usage.title | Should -Match '\{CommitmentWorkspace:label\}'
        $script:workbookItems['WorkspaceBillableIngestionSizeTrend'].content.crossComponentResources[0] | Should -Be '{Workspace}'
    }

    It 'isolates 40 GB/day per workspace instead of combining two workspaces into 80 GB/day' -ForEach @(
        @{ SelectedWorkspace = 'workspace-one' }
        @{ SelectedWorkspace = 'workspace-two' }
    ) {
        $now = [datetimeoffset]'2026-10-29T12:00:00Z'
        $records = @(
            foreach ($workspace in 'workspace-one', 'workspace-two') {
                @{ TimeGenerated = $now.AddDays(-31.5); StartTime = $now.AddDays(-31.5); Quantity = 0.0; IsBillable = $true; Plan = 'Analytics'; Workspace = $workspace }
                @{ TimeGenerated = $now.AddDays(-15); StartTime = $now.AddDays(-15); Quantity = 40.0 * 31.0 * 1000.0; IsBillable = $true; Plan = 'Analytics'; Workspace = $workspace }
            }
        )
        $actual = Get-FixtureTierUsage -Records $records -Now $now -Workspace $SelectedWorkspace
        $actual.DaysRemaining | Should -Be 0
        $actual.AverageDailyGB | Should -Be 40.0
        (Get-WorkbookQuery -ItemName 'CommitmentTierUsageContext') | Should -Match "VolumeCeilingGBPerDay == 50, '50 GB/day - verify availability'"
    }

    It 'does not borrow another workspace history when switching to a new workspace' {
        $now = [datetimeoffset]'2026-10-29T12:00:00Z'
        $records = @(
            @{ TimeGenerated = $now.AddDays(-31.5); StartTime = $now.AddDays(-31.5); Quantity = 1000.0; IsBillable = $true; Plan = 'Analytics'; Workspace = 'old-workspace' }
            @{ TimeGenerated = $now.AddDays(-10); StartTime = $now.AddDays(-10); Quantity = 1000.0; IsBillable = $true; Plan = 'Analytics'; Workspace = 'new-workspace' }
        )
        $actual = Get-FixtureTierUsage -Records $records -Now $now -Workspace 'new-workspace'
        $actual.DaysRemaining | Should -Be 21
        $actual.AverageDailyGB | Should -BeNullOrEmpty
        $empty = Get-FixtureTierUsage -Records $records -Now $now -Workspace 'empty-workspace'
        $empty.DaysRemaining | Should -Be 31
        $empty.AverageDailyGB | Should -BeNullOrEmpty
    }

    It 'keeps the tier query independent of the selected time range and avoids raw event scans' {
        $content = $script:workbookItems['CommitmentTierUsageContext'].content
        $content.PSObject.Properties.Name | Should -Not -Contain 'timeContextFromParameter'
        $content.PSObject.Properties.Name | Should -Not -Contain 'timeContext'
        $content.query | Should -Not -Match '\bunion\b|\b_BilledSize\b|\b_IsBillable\b'
        $content.query | Should -Match "project \['Log Analytics tier'\] = currentTier, \['Volume ceiling'\] = volumeCeiling, \['50 GB/day offer'\] = offerStatus, Status = reviewStatus"
        $content.query | Should -Not -Match 'suggestedTier|Pay-As-You-Go'
    }

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
        It 'preserves a 10 GB/day source rate for <Label> with <Stamp>-stamped Usage' -ForEach @(
            @{ Label = 'one aligned hour'; Start = '2026-10-01T10:00:00Z'; End = '2026-10-01T11:00:00Z'; Stamp = 'start' }
            @{ Label = 'five minutes inside an hour'; Start = '2026-10-01T10:10:00Z'; End = '2026-10-01T10:15:00Z'; Stamp = 'start' }
            @{ Label = 'fifteen minutes crossing an hour'; Start = '2026-10-01T10:55:00Z'; End = '2026-10-01T11:10:00Z'; Stamp = 'start' }
            @{ Label = 'two partial hourly edges'; Start = '2026-10-01T10:15:00Z'; End = '2026-10-01T11:30:00Z'; Stamp = 'start' }
            @{ Label = 'a UTC midnight crossing'; Start = '2026-10-01T23:55:00Z'; End = '2026-10-02T00:10:00Z'; Stamp = 'end' }
            @{ Label = 'partial six-hour buckets'; Start = '2026-10-01T04:15:00Z'; End = '2026-10-03T02:45:00Z'; Stamp = 'end' }
        ) {
            $query = Get-WorkbookQuery -ItemName $ItemName
            $startTime = [datetimeoffset]$Start
            $endTime = [datetimeoffset]$End
            $firstHour = $startTime.AddTicks(-($startTime.UtcTicks % [timespan]::TicksPerHour))
            $records = @(
                for ($hour = $firstHour.AddHours(-1); $hour -le $endTime.AddHours(1); $hour = $hour.AddHours(1)) {
                    @{
                        TimeGenerated = if ($Stamp -eq 'end') { $hour.AddHours(1) } else { $hour }
                        StartTime = $hour
                        EndTime = $hour.AddHours(1)
                        Quantity = 10.0 * 1000.0 / 24.0
                        IsBillable = $true
                        DataType = $DataType
                        Plan = 'Analytics'
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
                    $expression = Get-QueryExpression -Query $query -Pattern '(?<expression>licenseCount \* [0-9.]+ / 1000\.0 \* CoveredDays)'
                    $grantGB = Invoke-WorkbookArithmetic -Expression $expression -Bindings @{
                        licenseCount = $Licenses
                        CoveredDays = $row.CoveredDays
                    }
                    $dailyMB = if ($ItemName -eq 'E5DailyIngestionVsGrant') { 5.0 } else { 500.0 }
                    [math]::Abs($grantGB - $Licenses * $dailyMB / 1000.0 * $row.CoveredDays) |
                        Should -BeLessThan 0.00000001
                }
                [math]::Abs($row.IngestionGB / $row.CoveredDays - 10.0) | Should -BeLessThan 0.00000001
            }
        }

        It 'includes the first overlapping source hour without an implicit selected-time filter' {
            $content = $script:workbookItems[$ItemName].content
            $content.PSObject.Properties.Name | Should -Not -Contain 'timeContextFromParameter'
            $content.PSObject.Properties.Name | Should -Not -Contain 'timeContext'
            $content.query | Should -Match 'TimeGenerated >= selectedStart - 1h and TimeGenerated < selectedEnd \+ 1h'
            $content.query | Should -Match 'StartTime < selectedEnd and EndTime > selectedStart'
            $content.query | Should -Match 'min_of\(EndTime, selectedEnd\) - max_of\(StartTime, selectedStart\)'
            $content.query | Should -Match 'sum\(BinCoveredQuantity\)'
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
            Pattern = "project \['Illustrative Daily Ingestion Cost'\] = (?<expression>[^|;]+)"
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
            Quantity = 6000.0
            CoveredQuantity = 6000.0
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
        $query | Should -Match 'min_of\(BinStart \+ timeGrain, CoveredEnd\)'
        $query | Should -Match 'max_of\(BinStart, CoveredStart\)'
        $query | Should -Match 'TimeGenerated >= selectedStart - 1h and TimeGenerated < selectedEnd \+ 1h'
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
        $start = [datetimeoffset]'2026-10-01T00:00:00Z'
        $records = @(
            @{ TimeGenerated = $start.AddHours(12); StartTime = $start.AddHours(12); EndTime = $start.AddHours(13); Quantity = 1000.0; IsBillable = $true; DataType = $DataType; Plan = 'Analytics' }
        )
        $actual = Get-FixtureGrantUsed -Query $query -Records $records -LicenseCount $Licenses `
            -Start $start -End $start.AddDays(2)
        $actual | Should -Be 0.5
        $query | Should -Match "iif\(isnull\(licenseCount\), 'N/A',"
    }

    It 'caps separately across UTC days and excludes nonbillable, ineligible and end-boundary data in <ItemName>' -ForEach @(
        @{ ItemName = 'EligibleE5Ingestion'; Licenses = 100.0; DataType = 'AADRiskyUsers' }
        @{ ItemName = 'DfSP2GrantUsed'; Licenses = 1.0; DataType = 'SecurityEvent' }
    ) {
        $query = Get-WorkbookQuery -ItemName $ItemName
        $records = @(
            @{ TimeGenerated = [datetimeoffset]'2026-10-01T23:30:00Z'; StartTime = [datetimeoffset]'2026-10-01T23:30:00Z'; EndTime = [datetimeoffset]'2026-10-02T00:30:00Z'; Quantity = 1000.0; IsBillable = $true; DataType = $DataType; Plan = 'Analytics' }
            @{ TimeGenerated = [datetimeoffset]'2026-10-02T03:30:00+02:00'; StartTime = [datetimeoffset]'2026-10-02T03:30:00+02:00'; EndTime = [datetimeoffset]'2026-10-02T04:30:00+02:00'; Quantity = 100.0; IsBillable = $true; DataType = $DataType; Plan = 'Analytics' }
            @{ TimeGenerated = [datetimeoffset]'2026-10-02T12:00:00Z'; StartTime = [datetimeoffset]'2026-10-02T12:00:00Z'; EndTime = [datetimeoffset]'2026-10-02T13:00:00Z'; Quantity = 900.0; IsBillable = $false; DataType = $DataType; Plan = 'Analytics' }
            @{ TimeGenerated = [datetimeoffset]'2026-10-02T12:00:00Z'; StartTime = [datetimeoffset]'2026-10-02T12:00:00Z'; EndTime = [datetimeoffset]'2026-10-02T13:00:00Z'; Quantity = 900.0; IsBillable = $true; DataType = 'NotEligible'; Plan = 'Analytics' }
            @{ TimeGenerated = [datetimeoffset]'2026-10-02T12:00:00Z'; StartTime = [datetimeoffset]'2026-10-02T12:00:00Z'; EndTime = [datetimeoffset]'2026-10-02T13:00:00Z'; Quantity = 900.0; IsBillable = $true; DataType = $DataType; Plan = 'Basic' }
            @{ TimeGenerated = [datetimeoffset]'2026-10-03T00:00:00Z'; StartTime = [datetimeoffset]'2026-10-03T00:00:00Z'; EndTime = [datetimeoffset]'2026-10-03T01:00:00Z'; Quantity = 900.0; IsBillable = $true; DataType = $DataType; Plan = 'Analytics' }
        )
        $actual = Get-FixtureGrantUsed -Query $query -Records $records -LicenseCount $Licenses `
            -Start '2026-10-01T00:00:00Z' -End '2026-10-03T00:00:00Z'
        $actual | Should -Be 1.0
        (Get-FixtureGrantUsed -Query $query -Records @() -LicenseCount $Licenses `
            -Start '2026-10-01T00:00:00Z' -End '2026-10-03T00:00:00Z') | Should -Be 0.0
    }

    It 'clips overlapping source intervals and prorates grant caps in <ItemName>' -ForEach @(
        @{ ItemName = 'EligibleE5Ingestion'; Licenses = 100.0; DataType = 'SigninLogs'; DailyGrantGB = 0.5 }
        @{ ItemName = 'DfSP2GrantUsed'; Licenses = 1.0; DataType = 'SecurityEvent'; DailyGrantGB = 0.5 }
    ) {
        $query = Get-WorkbookQuery -ItemName $ItemName
        $start = [datetimeoffset]'2026-10-01T12:00:00Z'
        $records = @(
            @{ TimeGenerated = $start; StartTime = $start.AddMinutes(-30); EndTime = $start.AddMinutes(30); Quantity = 1000.0; IsBillable = $true; DataType = $DataType; Plan = 'Analytics' }
            @{ TimeGenerated = [datetimeoffset]'2026-10-01T23:30:00Z'; StartTime = [datetimeoffset]'2026-10-01T23:30:00Z'; EndTime = [datetimeoffset]'2026-10-02T00:30:00Z'; Quantity = 1000.0; IsBillable = $true; DataType = $DataType; Plan = 'Analytics' }
        )
        $actual = Get-FixtureGrantUsed -Query $query -Records $records -LicenseCount $Licenses `
            -Start $start -End '2026-10-02T00:00:00Z'
        $actual | Should -Be ($DailyGrantGB / 2.0)
    }

    It 'prorates the allowance on both sides of UTC midnight in <ItemName>' -ForEach @(
        @{ ItemName = 'EligibleE5Ingestion'; Licenses = 100.0; DataType = 'SigninLogs' }
        @{ ItemName = 'DfSP2GrantUsed'; Licenses = 1.0; DataType = 'SecurityEvent' }
    ) {
        $start = [datetimeoffset]'2026-10-01T23:55:00Z'
        $end = [datetimeoffset]'2026-10-02T00:05:00Z'
        $records = @(
            @{ TimeGenerated = $start; StartTime = $start; EndTime = $start.AddMinutes(5); Quantity = 500.0; IsBillable = $true; DataType = $DataType; Plan = 'Analytics' }
            @{ TimeGenerated = $start.AddMinutes(5); StartTime = $start.AddMinutes(5); EndTime = $end; Quantity = 500.0; IsBillable = $true; DataType = $DataType; Plan = 'Analytics' }
        )
        $actual = Get-FixtureGrantUsed -Query (Get-WorkbookQuery -ItemName $ItemName) -Records $records `
            -LicenseCount $Licenses -Start $start -End $end
        [math]::Abs($actual - (0.5 / 288.0 * 2.0)) | Should -BeLessThan 0.000000001
    }

    It 'bases <ItemName> savings on daily-capped use at the selected price' -ForEach @(
        @{ ItemName = 'EstimateE5Discount' }
        @{ ItemName = 'DfSP2EstimatedSavings' }
    ) {
        $query = Get-WorkbookQuery -ItemName $ItemName
        $expression = Get-QueryExpression -Query $query -Pattern "round\((?<expression>grantUsedGB \* todouble\('\{Price\}'\)), 2\)"
        (Invoke-WorkbookArithmetic -Expression $expression -Bindings @{ grantUsedGB = 0.5; Price = 2.0 }) |
            Should -Be 1.0
        (Invoke-WorkbookArithmetic -Expression $expression -Bindings @{ grantUsedGB = 500.0 / 1000.0; Price = 0.0 }) |
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

    It 'models the grant limit over the exact selected duration in <ItemName>' -ForEach @(
        @{ ItemName = 'DataGrantLimit' }
        @{ ItemName = 'DfSP2PeriodGrant' }
    ) {
        $query = Get-WorkbookQuery -ItemName $ItemName
        $query | Should -Match 'let grantDays = \(\{TimeRange:end\} - \{TimeRange:start\}\) / 1d;'
        $query | Should -Match 'grantDays'
        $query | Should -Not -Match 'ceiling\(|startofday\('
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
            @{ TimeGenerated = $start; StartTime = $start.AddMinutes(-30); EndTime = $start.AddMinutes(30); Quantity = 1000.0; IsBillable = $true; DataType = 'SecurityEvent'; Plan = 'Analytics' }
            @{ TimeGenerated = $end; StartTime = $end; EndTime = $end.AddHours(1); Quantity = 900.0; IsBillable = $true; DataType = 'SecurityEvent'; Plan = 'Analytics' }
        )
        $selected = @(Get-FixtureCoveredUsage -Query $query -Records $records -Start $start -End $end)
        $coveredQuantity = [double](($selected | Measure-Object -Property CoveredQuantity -Sum).Sum)
        $expression = Get-QueryExpression -Query $query -Pattern 'summarize (?:EligibleGB|TableSizeGB) = (?<expression>sum\(CoveredQuantity\) / 1000\.0)'
        $actual = Invoke-WorkbookArithmetic -Expression $expression -Bindings @{
            CoveredQuantity = $coveredQuantity
        }
        $actual | Should -Be 0.5
        $query | Should -Match 'StartTime < selectedEnd and EndTime > selectedStart'
        $query | Should -Match 'min_of\(EndTime, selectedEnd\) - max_of\(StartTime, selectedStart\)'
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
        $content.PSObject.Properties.Name | Should -Not -Contain 'timeContext'
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
