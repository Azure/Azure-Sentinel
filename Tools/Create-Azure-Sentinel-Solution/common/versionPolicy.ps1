$script:V31LegacyWorkbookVersionExceptions = @{
    'MicrosoftDefenderForOffice365detectionsandinsights' = [version]'4.0.0.0'
    'MicrosoftDefenderForOffice365detectionsandinsights.json' = [version]'4.0.0.0'
    'ThreatIntelligenceWorkbook' = [version]'5.0.0.0'
    'ThreatIntelligence' = [version]'5.0.0.0'
    'ThreatIntelligence.json' = [version]'5.0.0.0'
}

function Test-V31LegacyWorkbookVersionException {
    param(
        [string]$ContentPath,
        [version]$NormalizedVersion
    )

    if ([string]::IsNullOrWhiteSpace($ContentPath) -or $null -eq $NormalizedVersion) {
        return $false
    }
    $normalizedPath = $ContentPath.Trim() -replace '\\', '/'
    $leaf = [System.IO.Path]::GetFileName($normalizedPath)
    $stem = [System.IO.Path]::GetFileNameWithoutExtension($leaf)
    foreach ($candidate in @($normalizedPath, $leaf, $stem, "${stem}Workbook")) {
        foreach ($entry in $script:V31LegacyWorkbookVersionExceptions.GetEnumerator()) {
            if ($entry.Key -ieq $candidate -and $NormalizedVersion -eq $entry.Value) {
                return $true
            }
        }
    }
    return $false
}

function Assert-V31ReleaseVersion {
    param(
        [AllowNull()]
        [AllowEmptyString()]
        [string]$Version,
        [string]$ContentKind,
        [string]$ContentPath
    )

    if (-not $v31VersionPolicy) { return }

    $minimum = if ($ContentKind -eq 'Solution') { [version]'3.2.2.0' } elseif ($ContentKind -eq 'CustomDetection') { [version]'3.1.0.0' } else { [version]'0.0.0.0' }
    $range = if ($ContentKind -eq 'Solution') { '>= 3.2.2 and < 4.0.0' } elseif ($ContentKind -eq 'CustomDetection') { '>= 3.1.0 and < 4.0.0' } else { '< 4.0.0' }
    $parsed = $null
    $valid = $Version -cmatch '\A[0-9]+\.[0-9]+(?:\.[0-9]+){0,2}\z' -and
        [version]::TryParse($Version, [ref]$parsed)
    if ($ContentKind -eq 'CustomDetection') {
        $valid = $valid -and $Version -cmatch '\A3\.[1-9][0-9]*\.(?:0|[1-9][0-9]*)\z'
    }
    if ($valid) {
        $normalized = [version]::new($parsed.Major, $parsed.Minor, [Math]::Max(0, $parsed.Build), [Math]::Max(0, $parsed.Revision))
        $isLegacyWorkbookException = $ContentKind -eq 'Workbook' -and
            (Test-V31LegacyWorkbookVersionException -ContentPath $ContentPath -NormalizedVersion $normalized)
        $valid = $normalized -ge $minimum -and
            ($normalized -lt [version]'4.0.0.0' -or $isLegacyWorkbookException)
    }
    if (-not $valid) {
        $message = "V3.1 version policy: $ContentKind '$ContentPath' has effective release version '$Version'; required $range (numeric release version). No version is automatically promoted."
        if ($ContentKind -eq 'CustomDetection') {
            $message += " Set the XDR YAML top-level version to its own major.minor.patch release. For older files without version, reconvert with --overwrite (initial version 3.1.0), or explicitly author the XDR version. Do not change contentProvenance.source.version; Data 'XDR Detection Version' and solution Version are not fallbacks in V3.1."
        }
        $v31VersionPolicy.Errors.Add($message)
        throw $message
    }
}

function Assert-V31SolutionVersion {
    param(
        [string]$SolutionName,
        [string]$Version,
        [string]$CalculatedVersion = ''
    )
    if (-not $v31VersionPolicy) { return }
    Assert-V31ReleaseVersion -Version $Version -ContentKind Solution -ContentPath $SolutionName
    if (-not [string]::IsNullOrEmpty($CalculatedVersion)) {
        Assert-V31ReleaseVersion -Version $CalculatedVersion -ContentKind Solution -ContentPath "$SolutionName (calculated package version)"
        if ($Version -cne $CalculatedVersion) {
            $message = "V3.1 version policy: Solution '$SolutionName' declares version '$Version' but calculated package version is '$CalculatedVersion'. Align the input Version and calculated package version before packaging; emitted solution fields and ZIP version must agree."
            $v31VersionPolicy.Errors.Add($message)
            throw $message
        }
    }
}

function Assert-V31TargetVersion {
    param([AllowNull()][AllowEmptyString()][string]$Version)

    if ($Version -cnotmatch '\A(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\z') {
        throw "V3.1 target version '$Version' must be canonical major.minor.patch in the range >= 3.2.2 and < 4.0.0."
    }
    $parts = $Version.Split(".")
    $minor = [System.Numerics.BigInteger]::Parse($parts[1])
    $patch = [System.Numerics.BigInteger]::Parse($parts[2])
    if (-not ($parts[0] -ceq "3" -and ($minor -gt 2 -or ($minor -eq 2 -and $patch -ge 2)))) {
        throw "V3.1 target version '$Version' must be in the range >= 3.2.2 and < 4.0.0."
    }
}

function Assert-V31VersionChecksPassed {
    if ($v31VersionPolicy -and $v31VersionPolicy.Errors.Count -gt 0) {
        # Some legacy content readers catch exceptions. Never emit a partial package after a failed guard.
        throw ($v31VersionPolicy.Errors -join [Environment]::NewLine)
    }
}

function Save-V31LocalPackageVersion {
    param([string]$DataFilePath, [string]$Version)

    $data = Get-Content -LiteralPath $DataFilePath -Raw -ErrorAction Stop | ConvertFrom-Json -ErrorAction Stop
    $solutionRoot = Split-Path (Split-Path $DataFilePath -Parent) -Parent
    $metadataReference = Resolve-SolutionContentPath `
        -SolutionRoot $solutionRoot `
        -SolutionName ([System.IO.Path]::GetFileName($solutionRoot)) `
        -ContentPath ([string]$data.Metadata) `
        -RequireFile
    $metadataPath = $metadataReference.FullPath
    $metadata = Get-Content -LiteralPath $metadataPath -Raw -ErrorAction Stop | ConvertFrom-Json -ErrorAction Stop
    $data | Add-Member -NotePropertyName Version -NotePropertyValue $Version -Force
    $metadata | Add-Member -NotePropertyName version -NotePropertyValue $Version -Force
    $dataJson = $data | ConvertTo-Json -Depth 100
    $metadataJson = $metadata | ConvertTo-Json -Depth 100
    Set-Content -LiteralPath $DataFilePath -Value $dataJson -Encoding utf8 -ErrorAction Stop
    Set-Content -LiteralPath $metadataPath -Value $metadataJson -Encoding utf8 -ErrorAction Stop
}
