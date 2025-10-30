# Validation for PascalCase (GreaterThan)
$script:regEx_PascalCase = "^[A-Z][a-z]+(?:[A-Z][a-z]+)*$"

# Validation for camelCase (scheduledRule)
$script:regEx_camelCase = "^[a-z]+(?:[A-Z][a-z]+)*$"

# Validation for camelCase (scheduledRule)
$script:regEx_lowerCase = "^[a-z]*$"

# Validation for valid GUID value (00000000-ffff-bbbb-aaaa-000000000000)
$script:regEx_Guid = '^[{]?[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}[}]?$'

# Validation for value between 0 and 10000
$script:regEx_MaxValue = '^([0-9]{1}[0-0]{0,0}|1([0-9]{1,3})|10000)$'

# Validation for Mitre Technique with subvalue (T1078) or (T1078.001)
$script:regEx_Technique = '^(([T0-9]{5}))+(?:[.0-9]{4})?$'

# Validation for version number (1.3.1)
$script:regEx_Version = '^([0-9].([0-9]).{2})$'

# Validation for duration with max values of P14D (14 days), PT24H (24 hours) PT1440M (1440 minutes)
$script:regEx_yamlTime = '^[1-9]d|^1[0-4]d|([1-9]|[1-9][0-9]|[1-2][0-9][0-9]|3[0-3][0-6])h|([5-9]|[1-9][0-9]|[1-9][0-9][0-9]|1[0-3][0-9][0-9]|14[0-3][0-9]|1440)m'

Describe "Detections" {

    $testCases = Get-ChildItem -Path $detectionsPath -Include "*.yaml", "*.yml" -Exclude "action.yml", "*pipelines.yml", "*variables.yml" -Recurse | ForEach-Object -Process {
        @{
            file       = $_.FullName
            yamlObject = (Get-Content -Path $_.FullName | ConvertFrom-Yaml)
            path       = $_.DirectoryName
            name       = $_.Name
        }
    }

    Context "General" {

        It 'MITRE ATT&CK Should be loaded' {
            $attack | Should -Not -BeNullOrEmpty
        }

        It 'Converts from YAML | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )
            $yamlObject | Should -Not -BeNullOrEmpty
        }
    }

    Context "Properties" {

        It 'Do properties use camelCasing | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )
            ($yamlObject.psobject.Properties | Where-Object Name -eq Keys).value.ForEach{
                $_ | Should -MatchExactly $regEx_camelCase
            }
        }

        It 'Kind should be in the allowed list | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )

            $kind = $yamlObject.kind
            $expectedKind = @(
                'Scheduled',
                'NRT'
            )

            $kind | Should -BeIn $expectedKind
        }

        It 'Version should not be empty | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )

            $version = $yamlObject.version
            $version | Should -Not -BeNullOrEmpty
        }

        It 'Version should be in a valid format | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )

            $version = $yamlObject.version
            $version | Should -MatchExactly $regEx_Version
        }

        It 'Severity should be in the allowed list | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )

            $severities = $yamlObject.severity
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
                $yamlObject
            )
            $yamlObject.severity | Should -MatchExactly $regEx_PascalCase
        }

        It 'Trigger should be in the allowed list values | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )

            $expectedOperator = @(
                'eq',
                'gt',
                'lt',
                'ne'
            )
            if ($yamlObject.kind -eq 'Scheduled') {
                $yamlObject.triggerOperator | Should -BeIn $expectedOperator
            }
        }

        It 'TriggerOperator value should be in LowerCase | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )
            if ($yamlObject.kind -eq 'Scheduled') {
                $yamlObject.TriggerOperator | Should -MatchExactly $regEx_LowerCase
            }
        }

        It 'Threshold should be a integer value | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )
            if ($yamlObject.kind -eq 'Scheduled') {
                $yamlObject.triggerThreshold | Should -BeOfType System.ValueType
            }
        }

        It 'Threshold should not be more than 10000 | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )

            if ($yamlObject.kind -eq 'Scheduled') {
                $yamlObject.triggerThreshold | Should -MatchExactly $regEx_MaxValue
            }
        }

        It 'Tactics should be in the expected value list | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
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
                'Impact'
            )
            foreach ($tactic in $yamlObject.tactics) {
                $tactic | Should -BeIn $expectedTactics
            }
        }

        It 'Technique should be in the expected value list | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )

            foreach ($technique in $yamlObject.relevantTechniques) {
                $attack.id | Should -Contain $technique
            }
        }

        It 'Tactics should be in PascalCase | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )
            $tactics = $yamlObject.tactics

            foreach ($tactic in $tactics) {
                $tactic | Should -MatchExactly $regEx_PascalCase
            }
        }

        It 'Technique should be not be empty | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )
            $techniques = $yamlObject.relevantTechniques
            $techniques.count | Should -BeGreaterOrEqual 1

        }

        It 'Technique should start with T followed by 4 numbers | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )
            $techniques = $yamlObject.relevantTechniques

            foreach ($technique in $techniques) {
                $technique | Should -MatchExactly $regEx_Technique
            }
        }

        It 'Technique should map to the correct Tactics | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )
            $techniques = $yamlObject.relevantTechniques

            foreach ($technique in $techniques) {
                $tactics = @( $attack | Where-Object id -eq "$technique" ).tactics -split ',' | Sort-Object -Unique #2 + #1
                [int]$totalTactics = $totalTactics + $tactics.count
                Write-Output "Total Tactics $tactics = [$totalTactics]"
                foreach ($tactic in $tactics) {
                    if ($tactic -in $yamlObject.tactics) {
                        [int]$i = $i + $tactics.count
                        Write-Output "Current Count is with $tactics [$i]"
                    }
                }
                Write-Output "$i"
                if ($i -lt $totalTactics) {
                    $tactic | Should -BeIn $yamlObject.tactics -Because "[$($technique)] is specified in 'relevantTechniques'"
                }
            }
        }

        It 'Tactics should map to the correct Technique | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )
            $tactics = $yamlObject.tactics
            $relevantTechniques = $yamlObject.relevantTechniques

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

        It 'The id should be a valid GUID | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )
            $id = $yamlObject.id
            $id | Should -MatchExactly $regEx_Guid
        }

        It 'Entity Type should be in the expected value list | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )

            $entityTypes = $yamlObject.entityMappings.entityType
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
                $yamlObject
            )
            $entityTypes = $yamlObject.entityMappings.entityType

            foreach ($entityType in $entityTypes) {
                if ($entityType -notlike "*IP*" -and $entityType -notlike "*URL*" -and $entityType -notlike "*DNS*") {
                    $entityType | Should -MatchExactly $regEx_PascalCase
                }
            }
        }

        It 'Entity IP, URL and DNS should be in Capitals | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )
            $entityTypes = $yamlObject.entityMappings.entityType

            foreach ($entityType in $entityTypes) {
                if ($entityType -eq "IP" -or $entityType -eq "URL" -or $entityType -eq "DNS") {
                    $entityType | Should -MatchExactly '^[A-Z]+(?:[A-Z]+)*$'
                }
            }
        }

        It 'Query Frequency should be a valid format | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )

            if($yamlObject.kind -eq 'Scheduled') {
                $yamlObject.queryFrequency | Should -MatchExactly $regEx_yamlTime
            }
        }

        It 'Query Period should be a valid format | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )

            if ($yamlObject.kind -eq 'Scheduled') {
                $yamlObject.queryPeriod | Should -MatchExactly $regEx_yamlTime
            }
        }

        It 'Query Frequency should be less or equal than Query Period | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )

            function Convert-Time($value) {
                switch -wildcard ($value) {
                    "*d*" {
                        $result = New-TimeSpan -Days $value.replace('d', '')
                    }
                    "*h*" {
                        $result = New-TimeSpan -Hours $value.replace('h', '')
                    }
                    "*m*" {
                        $result = New-TimeSpan -Minutes $value.replace('m', '')
                    }
                    Default {}
                }
                return $result
            }

            if ($yamlObject.kind -eq 'Scheduled') {
                $queryFrequency = Convert-Time -value "$($yamlObject.queryFrequency)"
                $queryPeriod = Convert-Time -value "$($yamlObject.queryPeriod)"

                $queryFrequency.TotalMinutes | Should -BeLessOrEqual $queryPeriod.TotalMinutes
            }
        }

        It 'Query Frequency should be more than 60 minutes when Period is greater or equal than 2 days | <Name>' -TestCases $testCases {
            param (
                $file,
                $yamlObject
            )

            function Convert-Time($value) {
                switch -wildcard ($value) {
                    "*d*" {
                        $result = New-TimeSpan -Days $value.replace('d', '')
                    }
                    "*h*" {
                        $result = New-TimeSpan -Hours $value.replace('h', '')
                    }
                    "*m*" {
                        $result = New-TimeSpan -Minutes $value.replace('m', '')
                    }
                    Default {}
                }
                return $result
            }

            if ($yamlObject.kind -eq 'Scheduled') {
                $queryFrequency = Convert-Time -value "$($yamlObject.queryFrequency)"
                $queryPeriod = Convert-Time -value "$($yamlObject.queryPeriod)"

                if ($queryPeriod.TotalDays -ge 2) {
                    $queryFrequency.TotalMinutes | Should -BeGreaterThan 59
                }
            }
        }
    }
}
