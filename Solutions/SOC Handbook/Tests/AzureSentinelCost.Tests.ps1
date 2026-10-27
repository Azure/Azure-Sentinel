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
        $query | Should -Match 'TimeGenerated >= selectedStart and TimeGenerated < selectedEnd'
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
