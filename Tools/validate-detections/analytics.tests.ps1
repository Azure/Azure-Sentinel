# Validation for PascalCase (GreaterThan)
$script:regEx_PascalCase = "^[A-Z][a-z]+(?:[A-Z][a-z]+)*$"

# Validation for camelCase (scheduledRule)
$script:regEx_camelCase = "^[a-z]+(?:[A-Z][a-z]+)*$"

# Validation for valid GUID value (00000000-ffff-bbbb-aaaa-000000000000)
$script:regEx_Guid = '^[{]?[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}[}]?$'

# Validation for value between 0 and 10000
$script:regEx_MaxValue = '^([0-9]{1}[0-0]{0,0}|1([0-9]{1,3})|10000)$'

# Validation for Mitre Technique with subvalue (T1078) or (T1078.001)
$script:regEx_Technique = '^(([T0-9]{5}))+(?:[.0-9]{4})?$'

# Validation for CVE value (min. value CVE1999-***)
$script:regEx_CVE = '^(CVE-(1999|2\d{3})-(0\d{2}[1-9]|[1-9]\d{3,}))$'

# Validation for date format yyyy-MM-dd 2022-12-31
$script:regEx_Date = '^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$'

# Validation for ISO8601 duration with max values of P14D (14 days), PT24H (24 hours) PT1440M (1440 minutes)
$script:regEx_ISO8601 = '^P[1-9]D|^P1[0-4]D|PT([1-9]|[1-9][0-9]|[1-2][0-9][0-9]|3[0-3][0-6])H|PT([5-9]|[1-9][0-9]|[1-9][0-9][0-9]|1[0-3][0-9][0-9]|14[0-3][0-9]|1440)M'

# Validation for ISO8601 duration with max values of P14D (14 days), PT24H (24 hours) PT1440M (1440 minutes)
$script:regEx_ISO8601_7D = '^P[1-7]D|PT([1-9]|[1-9][0-9]|[1-2][0-9][0-9]|3[0-3][0-6])H|PT([5-9]|[1-9][0-9]|[1-9][0-9][0-9]|1[0-3][0-9][0-9]|14[0-3][0-9]|1440)M'

Describe "Detections" {

    $testCases = Get-ChildItem -Path $detectionsPath -Include "*.json" -Exclude "*.parameters.json" -Recurse | ForEach-Object -Process {
        @{
            file       = $_.FullName
            jsonObject = (Get-Content -Path $_.FullName | ConvertFrom-Json)
            path       = $_.DirectoryName
            name       = $_.Name
            parameters = (Get-Content -Path $_.FullName | ConvertFrom-Json).parameters
            resources  = (Get-Content -Path $_.FullName | ConvertFrom-Json).resources | Where-Object Type -eq 'Microsoft.OperationalInsights/workspaces/providers/alertRules'
            properties = ((Get-Content -Path $_.FullName | ConvertFrom-Json).resources  | Where-Object Type -eq 'Microsoft.OperationalInsights/workspaces/providers/alertRules').properties
        }
    }

    Context "General" {

        It 'MITRE ATT&CK Should be loaded' {
            $attack | Should -Not -BeNullOrEmpty
        }

        It 'Converts from JSON | <Name>' -TestCases $testCases {
            param (
                $file,
                $jsonObject
            )
            Write-Output "$File"
            $jsonObject | Should -Not -BeNullOrEmpty
        }

        It 'Do parameters use camelCasing | <Name>' -TestCases $testCases {
            param (
                $file,
                $parameters
            )
            $parameters.psobject.Properties.Name.ForEach{
                $_ | Should -MatchExactly $regEx_camelCase
            }
        }

    }

    Context "Resources" {

        It 'Enabled should be a boolean | <Name>' -TestCases $testCases {
            param (
                $file,
                $resources
            )
            if ($resources.enabled) {
                $resources.enabled | Should -BeOfType Boolean
            }
        }

        It 'Type should be [Microsoft.OperationalInsights/workspaces/providers/alertRules] | <Name>' -TestCases $testCases {
            param (
                $file,
                $resources
            )
            $resources.type | Should -BeExactly 'Microsoft.OperationalInsights/workspaces/providers/alertRules'
        }

    }

    Context "Properties" {

        It 'Do properties use camelCasing | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )
            $properties.psobject.Properties.Name.ForEach{
                $_ | Should -MatchExactly $regEx_camelCase
            }
        }

        It 'Displayname should not contain GH Prefix | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $properties.displayName | Should -Not -MatchExactly '^([Gg][Hh]-).*$'
        }

        It 'Severity should be in the allowed list | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $severities = $properties.severity
            $expectedSeverity = @(
                'Low',
                'Medium',
                'High',
                'Informational'
            )
            foreach ($severity in $severities) {
                $severity | Should -BeIn $expectedSeverity
            }
        }

        It 'Severity should be in PascalCase | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )
            $properties.severity | Should -MatchExactly $regEx_PascalCase
        }

        It 'Enabled should be a boolean | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )
            if ($properties.enabled) {
                $properties.enabled | Should -BeOfType Boolean
            }
        }

        It 'Trigger should be in the allowed list values | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $expectedOperator = @(
                'Equal',
                'GreaterThan',
                'LessThan',
                'NotEqual'
            )
            $properties.triggerOperator | Should -BeIn $expectedOperator
        }

        It 'TriggerOperator value should be in PascalCase | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )
            $properties.TriggerOperator | Should -MatchExactly $regEx_PascalCase
        }

        It 'Threshold should be a integer value | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )
            $properties.triggerThreshold | Should -BeOfType System.ValueType
        }

        It 'Threshold should not be more than 10000 | <Name>' -TestCases $testCases {
            param (
                $file,
                $rules
            )

            $properties.triggerThreshold | Should -MatchExactly $regEx_MaxValue
        }

        It 'suppressionEnabled should be a boolean | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $properties.suppressionEnabled | Should -BeOfType Boolean
        }

        It 'Tactics should be in the expected value list | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $expectedTactics = @(
                'Reconnaissance',
                'ResourceDevelopment',
                'InitialAccess',
                'Execution',
                'Persistence',
                'PrivilegeEscalation',
                'DefenseEvasion',
                'CredentialAccess',
                'Discovery',
                'LateralMovement',
                'Collection',
                'CommandandControl',
                'Exfiltration',
                'Impact',
                'ImpairProcessControl',
                'InhibitResponseFunction'
            )
            foreach ($tactic in $properties.tactics) {
                $tactic | Should -BeIn $expectedTactics
            }
        }

        It 'Technique should be in the expected value list | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            foreach ($technique in $properties.techniques) {
                $attack.id | Should -Contain $technique -Because ''#"[$($attack.id)] is invalid!"
            }
        }

        It 'Tactics should be in PascalCase | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )
            $tactics = $properties.tactics

            foreach ($tactic in $tactics) {
                $tactic | Should -MatchExactly $regEx_PascalCase
            }
        }

        It 'Technique should be not be empty | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )
            $techniques = $properties.techniques

            $techniques.count | Should -BeGreaterOrEqual 1

        }

        It 'Technique should start with T followed by 4 numbers | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )
            $techniques = $properties.techniques

            foreach ($technique in $techniques) {
                $technique | Should -MatchExactly $regEx_Technique
            }
        }

        It 'Technique should map to the correct Tactics | <Name>' -TestCases $testCases {
            #Validated and Tested!
            param (
                $file,
                $properties
            )
            $techniques = $properties.techniques

            foreach ($technique in $techniques) {
                $tactics = @( $attack | Where-Object id -eq "$technique" ).tactics -split ',' | Sort-Object -Unique #2 + #1
                [int]$totalTactics = $totalTactics + $tactics.count
                Write-Output "Total Tactics $tactics = [$totalTactics]"
                foreach ($tactic in $tactics) {
                    if ($tactic -in $properties.tactics) {
                        [int]$i = $i + $tactics.count
                        Write-Output "Current Count is with $tactics [$i]"
                    }
                }
                Write-Output "$i"
                if ($i -lt $totalTactics) {
                    $tactic | Should -BeIn $properties.tactics -Because "[$($technique)] is specified in 'techniques'"
                }
            }
        }

        It 'Tactics should map to the correct Technique | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )
            $tactics = $properties.tactics
            $relevantTechniques = $properties.techniques

            if ($null -ne $relevantTechniques) {
                foreach ($tactic in $tactics) {
                    $techniques = @( $attack | Where-Object tactics -like "*$tactic*" ).id -split ',' | Sort-Object -Descending -Unique
                    [int]$totalTechniques = $totalTechniques + $techniques.count
                    foreach ($technique in $techniques) {
                        if ($technique -in $relevantTechniques) {
                            [int]$i = $i + $techniques.count
                        }
                    }
                    if ($i -lt $totalTechniques) {
                        'a valid technique' | Should -BeIn $relevantTechniques -Because "[$($tactic)] is specified in tactics"
                    }
                }
            }
        }

        #For now this value should stay empty in our templates
        It 'Alert Rules template should be empty or a valid GUID | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )
            $alertRuleTemplateName = $properties.alertRuleTemplateName
            if ($null -ne $alertRuleTemplateName) {
                $alertRuleTemplateName | Should -MatchExactly $regEx_Guid
            }
        }

        It 'Aggregation Kind should be in the expected value list | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $aggregationKind = $properties.EventGroupingSettings.aggregationKind
            $expectedKind = @(
                'AlertPerResult',
                'SingleAlert'
            )
            foreach ($kind in $aggregationKind) {
                $kind | Should -BeIn $expectedKind
            }
        }

        It 'Aggregation Kind should be in PascalCase | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $aggregationKind = $properties.EventGroupingSettings.aggregationKind
            $aggregationKind | Should -MatchExactly $regEx_PascalCase
        }

        It 'Entity Type should be in the expected value list | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $entityTypes = $properties.entityMappings.entityType
            $expectedEntityTypes = @(
                'Account',
                'AzureResource',
                'CloudApplication',
                'DNS',
                'File',
                'FileHash',
                'Host',
                'IP',
                'MailCluster',
                'MailMessage',
                'Mailbox',
                'Malware',
                'Process',
                'RegistryKey',
                'RegistryValue',
                'SecurityGroup',
                'SubmissionMail',
                'URL'
            )
            foreach ($entityType in $entityTypes) {
                $entityType | Should -BeIn $expectedEntityTypes
            }
        }

        It 'Entity Type should be in PascalCase | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )
            $entityTypes = $properties.entityMappings.entityType

            foreach ($entityType in $entityTypes) {
                if ($entityType -notlike "*IP*" -and $entityType -notlike "*URL*" -and $entityType -notlike "*DNS*") {
                    $entityType | Should -MatchExactly $regEx_PascalCase
                }
            }
        }

        It 'Entity IP and URL should be in Capitals | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )
            $entityTypes = $properties.entityMappings.entityType

            foreach ($entityType in $entityTypes) {
                if ($entityType -eq "IP" -or $entityType -eq "URL") {
                    $entityType | Should -MatchExactly '^[A-Z]+(?:[A-Z]+)*$'
                }
            }
        }

        It 'Suppression Duration should be a valid ISO 8601 format | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $properties.suppressionDuration | Should -MatchExactly $regEx_ISO8601
        }

        It 'Query Frequency should be a valid ISO 8601 format | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $properties.queryFrequency | Should -MatchExactly $regEx_ISO8601
        }

        It 'Query Period should be a valid ISO 8601 format | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $properties.queryPeriod | Should -MatchExactly $regEx_ISO8601
        }

        It 'Query Frequency should be less or equal than Query Period | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $queryFrequency = [System.Xml.XmlConvert]::ToTimeSpan("$($properties.queryFrequency)")
            $queryPeriod = [System.Xml.XmlConvert]::ToTimeSpan("$($properties.queryPeriod)")

            $queryFrequency.TotalMinutes | Should -BeLessOrEqual $queryPeriod.TotalMinutes
        }

        It 'Query Frequency should be more than 60 minutes when Period is greater or equal than 2 days | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $queryFrequency = [System.Xml.XmlConvert]::ToTimeSpan("$($properties.queryFrequency)")
            $queryPeriod = [System.Xml.XmlConvert]::ToTimeSpan("$($properties.queryPeriod)")

            if ($queryPeriod.TotalDays -ge 2) {
                $queryFrequency.TotalMinutes | Should -BeGreaterThan 59
            }
        }
    }

    Context "Incident Configuration" {

        It 'Do properties use camelCasing | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )
            $properties.incidentConfiguration.psobject.Properties.Name.ForEach{
                $_ | Should -MatchExactly $regEx_camelCase
            }
        }

        It 'createIncident should be a boolean | <Name>' -TestCases $testCases {

            param (
                $file,
                $properties
            )

            $incidentConfiguration = $properties.incidentConfiguration

            if ($incidentConfiguration.createIncident) {
                $incidentConfiguration.createIncident | Should -BeOfType Boolean
            }
        }
    }

    Context "Grouping Configuration" {

        It 'Do properties use camelCasing | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $groupingConfiguration = $properties.incidentConfiguration.groupingConfiguration

            $groupingConfiguration.psobject.Properties.Name.ForEach{
                $_ | Should -MatchExactly $regEx_camelCase
            }
        }

        It 'Enabled should be a boolean | <Name>' -TestCases $testCases {

            param (
                $file,
                $properties
            )

            $groupingConfiguration = $properties.incidentConfiguration.groupingConfiguration

            if ($groupingConfiguration.enabled) {
                $groupingConfiguration.enabled | Should -BeOfType Boolean
            }
        }

        It 'Reopen Closed Incident should be a boolean | <Name>' -TestCases $testCases {

            param (
                $file,
                $properties
            )

            $groupingConfiguration = $properties.incidentConfiguration.groupingConfiguration

            if ($groupingConfiguration.reopenClosedIncident) {
                $groupingConfiguration.reopenClosedIncident | Should -BeOfType Boolean
            }
        }

        It 'Lookback Duration should be a valid ISO 8601 format and max 7 days | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $groupingConfiguration = $properties.incidentConfiguration.groupingConfiguration
            $groupingConfiguration.lookbackDuration | Should -MatchExactly $regEx_ISO8601_7D
        }

        It 'Matching method be in the expected value list | <Name>' -TestCases $testCases {

            param (
                $file,
                $properties
            )

            $groupingConfiguration = $properties.incidentConfiguration.groupingConfiguration

            $expectedMethod = @(
                'Selected',
                'AnyAlert',
                'AllEntities'
            )

            $groupingConfiguration.matchingMethod | Should -BeIn $expectedMethod
        }

        It 'Group By Entities be in the expected value list | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $groupByEntities = $properties.incidentConfiguration.groupingConfiguration.groupByEntities

            $expectedEntityTypes = @(
                'Account',
                'AzureResource',
                'CloudApplication',
                'DNS',
                'File',
                'FileHash',
                'Host',
                'IP',
                'MailCluster',
                'MailMessage',
                'Mailbox',
                'Malware',
                'Process',
                'RegistryKey',
                'RegistryValue',
                'SecurityGroup',
                'SubmissionMail',
                'URL'
            )

            foreach ($entityType in $groupByEntities) {
                $entityType | Should -BeIn $expectedEntityTypes
            }
        }

        It 'Entity Type should be in PascalCase | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $entityTypes = $properties.incidentConfiguration.groupingConfiguration.groupByEntities

            foreach ($entityType in $entityTypes) {
                if ($entityType -notlike "*IP*" -and $entityType -notlike "*URL*" -and $entityType -notlike "*DNS*") {
                    $entityType | Should -MatchExactly $regEx_PascalCase
                }
            }
        }

        It 'Entity IP, URL and DNS should be in Capitals | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $entityTypes = $properties.incidentConfiguration.groupingConfiguration.groupByEntities

            foreach ($entityType in $entityTypes) {
                if ($entityType -eq "IP" -or $entityType -eq "URL" -or $entityType -eq "*DNS*") {
                    $entityType | Should -MatchExactly '^[A-Z]+(?:[A-Z]+)*$'
                }
            }
        }

        It 'Group By Alert Details be in the expected value list | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $groupByAlertDetails = $properties.incidentConfiguration.groupingConfiguration.groupByAlertDetails

            $expectedGroupByTypes = @(
                'Name',
                'Severity'
            )

            foreach ($groupBy in $groupByAlertDetails) {
                $groupBy | Should -BeIn $expectedGroupByTypes
            }
        }

        It 'Group By Entities should be in PascalCase | <Name>' -TestCases $testCases {
            param (
                $file,
                $properties
            )

            $groupByAlertDetails = $properties.incidentConfiguration.groupingConfiguration.groupByAlertDetails

            if ($groupByAlertDetails) {
                $groupByAlertDetails | Should -MatchExactly $regEx_PascalCase
            }
        }
    }
}
