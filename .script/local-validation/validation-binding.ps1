$script:ValidationInputExcludedDirectories = @(
    "package",
    "logs",
    "evidence",
    ".git",
    ".venv",
    "__pycache__"
)

function Get-ValidationFileFingerprints {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Root,

        [string[]]$ExcludeDirectories = @(),

        [ValidateSet("Ordinal", "Posix", "Windows")]
        [string]$PathOrder = "Ordinal"
    )

    $rootPath = [System.IO.Path]::GetFullPath($Root)
    if (-not (Test-Path -LiteralPath $rootPath -PathType Container)) {
        throw "Fingerprint root does not exist: $rootPath"
    }
    $rootItem = Get-Item -LiteralPath $rootPath -Force
    if (($rootItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "Fingerprint root cannot be a symbolic link: $rootPath"
    }

    $excluded = @($ExcludeDirectories | ForEach-Object { $_.ToLowerInvariant() })
    $byPath = [System.Collections.Generic.Dictionary[string, object]]::new(
        [System.StringComparer]::Ordinal
    )
    foreach ($item in Get-ChildItem -LiteralPath $rootPath -Force -Recurse -ErrorAction Stop) {
        $relative = [System.IO.Path]::GetRelativePath($rootPath, $item.FullName).Replace("\", "/")
        $parts = $relative -split "/"
        if (@($parts | Where-Object { $excluded -contains $_.ToLowerInvariant() }).Count -gt 0) {
            continue
        }
        if (@($parts | Where-Object {
            $_ -ieq ".env" -or $_.StartsWith(".env.", [System.StringComparison]::OrdinalIgnoreCase)
        }).Count -gt 0) {
            continue
        }
        if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "Fingerprint input cannot be a symbolic link: $relative"
        }
        if ($item.PSIsContainer) {
            continue
        }
        $digest = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant()
        $byPath.Add($relative, [ordered]@{
            path   = $relative
            sha256 = $digest
        })
    }

    [string[]]$paths = @($byPath.Keys)
    if ($PathOrder -in @("Posix", "Windows")) {
        $pathComparer = [System.StringComparer]::Ordinal
        if ($PathOrder -eq "Windows") {
            $normalizedPaths = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
            foreach ($path in $paths) {
                $normalizedPath = (@($path.Split("/") | ForEach-Object { $_.ToLowerInvariant() }) -join "/")
                if (-not $normalizedPaths.Add($normalizedPath)) {
                    throw "Windows Path ordering is ambiguous for case-insensitive duplicate source paths: $path"
                }
            }
        }
        [System.Array]::Sort($paths, [System.Comparison[string]]{
            param([string]$left, [string]$right)

            $leftParts = $left.Split("/")
            $rightParts = $right.Split("/")
            if ($PathOrder -eq "Windows") {
                $leftParts = @($leftParts | ForEach-Object { $_.ToLowerInvariant() })
                $rightParts = @($rightParts | ForEach-Object { $_.ToLowerInvariant() })
            }
            $sharedParts = [Math]::Min($leftParts.Length, $rightParts.Length)
            for ($index = 0; $index -lt $sharedParts; $index++) {
                $comparison = $pathComparer.Compare(
                    $leftParts[$index],
                    $rightParts[$index]
                )
                if ($comparison -ne 0) {
                    return $comparison
                }
            }
            return $leftParts.Length.CompareTo($rightParts.Length)
        })
    }
    else {
        [System.Array]::Sort($paths, [System.StringComparer]::Ordinal)
    }
    $result = [System.Collections.Generic.List[object]]::new()
    foreach ($path in $paths) {
        $result.Add($byPath[$path])
    }
    return ,$result.ToArray()
}

function ConvertTo-ValidationJsonString {
    param([Parameter(Mandatory = $true)][string]$Value)

    $builder = [System.Text.StringBuilder]::new()
    [void]$builder.Append('"')
    foreach ($character in $Value.ToCharArray()) {
        $code = [int]$character
        if ($code -eq 0x22) {
            [void]$builder.Append('\"')
            continue
        }
        if ($code -eq 0x5C) {
            [void]$builder.Append('\\')
            continue
        }
        if ($code -eq 0x08) {
            [void]$builder.Append('\b')
            continue
        }
        if ($code -eq 0x0C) {
            [void]$builder.Append('\f')
            continue
        }
        if ($code -eq 0x0A) {
            [void]$builder.Append('\n')
            continue
        }
        if ($code -eq 0x0D) {
            [void]$builder.Append('\r')
            continue
        }
        if ($code -eq 0x09) {
            [void]$builder.Append('\t')
            continue
        }
        if ($code -lt 0x20 -or $code -ge 0x7F) {
            [void]$builder.Append('\u')
            [void]$builder.Append($code.ToString("x4"))
        }
        else {
            [void]$builder.Append($character)
        }
    }
    [void]$builder.Append('"')
    return $builder.ToString()
}

function Get-ValidationInputFingerprintHash {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [object[]]$Files
    )

    $items = foreach ($file in $Files) {
        '{"path":' + (ConvertTo-ValidationJsonString -Value $file.path) +
            ',"sha256":' + (ConvertTo-ValidationJsonString -Value $file.sha256) + '}'
    }
    $canonical = '[' + (@($items) -join ',') + ']'
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($canonical)
    return [Convert]::ToHexString(
        [System.Security.Cryptography.SHA256]::HashData($bytes)
    ).ToLowerInvariant()
}

function Resolve-ValidationEvidencePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Root,

        [Parameter(Mandatory = $true)]
        [string]$Reference
    )

    if ([string]::IsNullOrWhiteSpace($Reference)) {
        throw "V3.1 package artifact reference is empty"
    }
    $rootPath = [System.IO.Path]::GetFullPath($Root)
    $candidate = if ([System.IO.Path]::IsPathRooted($Reference)) {
        [System.IO.Path]::GetFullPath($Reference)
    }
    else {
        [System.IO.Path]::GetFullPath((Join-Path $rootPath $Reference))
    }
    $prefix = $rootPath.TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
    if (-not $candidate.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "V3.1 package report path escapes the selected solution: $Reference"
    }

    $relative = [System.IO.Path]::GetRelativePath($rootPath, $candidate)
    $cursor = $rootPath
    foreach ($component in ($relative -split '[\\/]')) {
        $cursor = Join-Path $cursor $component
        if (Test-Path -LiteralPath $cursor) {
            $item = Get-Item -LiteralPath $cursor -Force
            if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "V3.1 package report path traverses a symbolic link: $Reference"
            }
        }
    }
    return $candidate
}

function Get-ValidationV31PackageEvidence {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SolutionPath,

        [Parameter(Mandatory = $true)]
        [string]$PackageReportPath
    )

    $solutionRoot = [System.IO.Path]::GetFullPath($SolutionPath)
    $reportPath = Resolve-ValidationEvidencePath -Root $solutionRoot -Reference $PackageReportPath
    if (-not (Test-Path -LiteralPath $reportPath -PathType Leaf)) {
        throw "V3.1 package report does not exist: $reportPath"
    }
    if ([System.IO.Path]::GetFileName($reportPath) -notmatch '^packaging\.v3_1(?:\.[^\\/]+)?\.json$') {
        throw "PackageReportPath must identify a V3.1 packaging report: $reportPath"
    }

    try {
        $reportBytes = [System.IO.File]::ReadAllBytes($reportPath)
        $report = [System.IO.File]::ReadAllText($reportPath) | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        throw "V3.1 package report is unreadable or invalid JSON: $($_.Exception.Message)"
    }
    if ($report.packager -ne "V3.1") {
        throw "PackageReportPath does not contain V3.1 packaging evidence"
    }

    $packageInputSha256 = [string]$report.packageInputs.after.sha256
    if ($packageInputSha256 -notmatch '^[a-fA-F0-9]{64}$') {
        throw "V3.1 package report has no valid post-package input fingerprint"
    }
    if ([string]::IsNullOrWhiteSpace([string]$report.packageAttemptId) -or
        [string]::IsNullOrWhiteSpace([string]$report.workflowRunId)) {
        throw "V3.1 package report has no workflow and package-attempt identity"
    }
    if ([string]::IsNullOrWhiteSpace([string]$report.version)) {
        throw "V3.1 package report has no package version"
    }
    if ($null -eq $report.packageArtifactHashes) {
        throw "V3.1 package report has no package artifact hashes"
    }
    $packageArtifactsSha256 = [string]$report.packageArtifactsSha256
    if ($packageArtifactsSha256 -notmatch '^[a-fA-F0-9]{64}$') {
        throw "V3.1 package report has no valid aggregate package artifact fingerprint"
    }

    $artifactHashes = [ordered]@{}
    foreach ($name in @("mainTemplate", "createUiDefinition", "testParameters", "zip")) {
        $reference = [string]$report.$name
        $expectedHash = [string]$report.packageArtifactHashes.$name
        if ([string]::IsNullOrWhiteSpace($reference) -or $expectedHash -notmatch '^[a-fA-F0-9]{64}$') {
            throw "V3.1 package report is missing a valid $name artifact fingerprint"
        }
        $artifactPath = Resolve-ValidationEvidencePath -Root $solutionRoot -Reference $reference
        if (-not (Test-Path -LiteralPath $artifactPath -PathType Leaf)) {
            throw "V3.1 package artifact is missing: $reference"
        }
        $actualHash = (Get-FileHash -LiteralPath $artifactPath -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant()
        if ($actualHash -ne $expectedHash.ToLowerInvariant()) {
            throw "V3.1 package artifact is stale: $name"
        }
        $artifactHashes[$name] = $expectedHash.ToLowerInvariant()
    }

    $packageDirectory = Join-Path $solutionRoot "Package"
    $packageFiles = Get-ValidationFileFingerprints -Root $packageDirectory
    return [ordered]@{
        path                    = [System.IO.Path]::GetRelativePath($solutionRoot, $reportPath).Replace("\", "/")
        sha256                  = [Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData($reportBytes)).ToLowerInvariant()
        version                 = [string]$report.version
        packageAttemptId        = [string]$report.packageAttemptId
        workflowRunId           = [string]$report.workflowRunId
        packageInputSha256      = $packageInputSha256.ToLowerInvariant()
        packageArtifactsSha256  = $packageArtifactsSha256.ToLowerInvariant()
        packageArtifactHashes   = $artifactHashes
        packageFiles            = $packageFiles
    }
}

function Get-ValidationEvidenceSnapshot {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ToolkitRoot,

        [Parameter(Mandatory = $true)]
        [string]$ContentRoot,

        [Parameter(Mandatory = $true)]
        [string]$SolutionPath,

        [Parameter(Mandatory = $true)]
        [string]$PackageReportPath
    )

    $toolkitPath = [System.IO.Path]::GetFullPath($ToolkitRoot)
    $contentPath = [System.IO.Path]::GetFullPath($ContentRoot)
    $solutionRoot = [System.IO.Path]::GetFullPath($SolutionPath)
    $packageEvidence = Get-ValidationV31PackageEvidence `
        -SolutionPath $solutionRoot `
        -PackageReportPath $PackageReportPath
    $posixInputFiles = Get-ValidationFileFingerprints `
        -Root $solutionRoot `
        -ExcludeDirectories $script:ValidationInputExcludedDirectories `
        -PathOrder Posix
    $posixInputFingerprint = Get-ValidationInputFingerprintHash -Files $posixInputFiles
    $windowsInputFiles = $null
    $windowsInputFingerprint = $null
    try {
        $windowsInputFiles = Get-ValidationFileFingerprints `
            -Root $solutionRoot `
            -ExcludeDirectories $script:ValidationInputExcludedDirectories `
            -PathOrder Windows
        $windowsInputFingerprint = Get-ValidationInputFingerprintHash -Files $windowsInputFiles
    }
    catch {
        $windowsInputFiles = $null
    }

    $matchesPosix = $posixInputFingerprint -eq $packageEvidence.packageInputSha256
    $matchesWindows = $windowsInputFingerprint -and
        $windowsInputFingerprint -eq $packageEvidence.packageInputSha256
    if (-not $matchesPosix -and -not $matchesWindows) {
        throw "V3.1 package report is stale against current solution inputs under both POSIX and Windows Path ordering"
    }
    if ($matchesPosix -and $matchesWindows) {
        $posixJson = ConvertTo-Json -InputObject @($posixInputFiles) -Depth 20 -Compress
        $windowsJson = ConvertTo-Json -InputObject @($windowsInputFiles) -Depth 20 -Compress
        if ($posixJson -cne $windowsJson) {
            throw "V3.1 package input fingerprint ambiguously matches different POSIX and Windows Path orderings"
        }
        $inputFiles = $posixInputFiles
        $sourcePathSemantics = "platform-neutral"
    }
    elseif ($matchesWindows) {
        $inputFiles = $windowsInputFiles
        $sourcePathSemantics = "windows"
    }
    else {
        $inputFiles = $posixInputFiles
        $sourcePathSemantics = "posix"
    }
    $producerPlatform = if ([Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT) {
        "windows"
    }
    else {
        "posix"
    }
    $producerFiles = [ordered]@{}
    foreach ($name in @("build-and-validate.ps1", "validation-binding.ps1")) {
        $path = Join-Path $toolkitPath ".script/local-validation/$name"
        $producerFiles[$name] = (Get-FileHash -LiteralPath $path -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant()
    }
    return [ordered]@{
        capturedAtUtc  = [DateTime]::UtcNow.ToString("o")
        toolkitRoot    = $toolkitPath
        contentRoot    = $contentPath
        solutionPath   = $solutionRoot
        inputFiles     = $inputFiles
        sourcePathSemantics = $sourcePathSemantics
        producerPlatform = $producerPlatform
        package        = $packageEvidence
        producerFiles  = $producerFiles
    }
}

function Complete-ValidationEvidenceBinding {
    param(
        [Parameter(Mandatory = $true)]
        [System.Collections.IDictionary]$Before,

        [Parameter(Mandatory = $true)]
        [System.Collections.IDictionary]$After,

        [Parameter(Mandatory = $true)]
        [object[]]$ValidationEntries,

        [Parameter(Mandatory = $true)]
        [bool]$PackagingSkipped,

        [Parameter(Mandatory = $true)]
        [bool]$ValidationSkipped,

        [Parameter(Mandatory = $true)]
        [string]$EvidenceRunPath
    )

    $validationEntries = @($ValidationEntries | Where-Object { $_.Step -in 2, 3, 4 })
    $passed = @($validationEntries | Where-Object { $_.Status -eq "passed" }).Count
    $failed = @($validationEntries | Where-Object { $_.Status -eq "failed" }).Count
    $skipped = @($validationEntries | Where-Object { $_.Status -eq "skipped" }).Count
    $issues = [System.Collections.Generic.List[string]]::new()

    if (-not $PackagingSkipped) { $issues.Add("V3.1 validation evidence must be collected with packaging skipped") }
    if ($ValidationSkipped) { $issues.Add("validation was skipped") }
    if ($passed -eq 0) { $issues.Add("no validator completed successfully") }
    if ($failed -gt 0) { $issues.Add("one or more validators failed") }
    if ($Before.contentRoot -ne $After.contentRoot -or $Before.solutionPath -ne $After.solutionPath) {
        $issues.Add("ContentRoot or solution path changed during validation")
    }
    if ($Before.sourcePathSemantics -ne $After.sourcePathSemantics -or
        $Before.producerPlatform -ne $After.producerPlatform) {
        $issues.Add("the package Path ordering identity or validation producer platform changed during validation")
    }
    $beforeArtifactHashes = ConvertTo-Json -InputObject $Before.package.packageArtifactHashes -Depth 10 -Compress
    $afterArtifactHashes = ConvertTo-Json -InputObject $After.package.packageArtifactHashes -Depth 10 -Compress
    if ($Before.package.sha256 -ne $After.package.sha256 -or
        $Before.package.packageAttemptId -ne $After.package.packageAttemptId -or
        $Before.package.workflowRunId -ne $After.package.workflowRunId -or
        $Before.package.packageInputSha256 -ne $After.package.packageInputSha256 -or
        $beforeArtifactHashes -cne $afterArtifactHashes) {
        $issues.Add("the V3.1 package report or package identity changed during validation")
    }
    if ((ConvertTo-Json -InputObject @($Before.inputFiles) -Depth 20 -Compress) -cne
        (ConvertTo-Json -InputObject @($After.inputFiles) -Depth 20 -Compress)) {
        $issues.Add("solution input bytes changed during validation")
    }
    if ((ConvertTo-Json -InputObject @($Before.package.packageFiles) -Depth 20 -Compress) -cne
        (ConvertTo-Json -InputObject @($After.package.packageFiles) -Depth 20 -Compress)) {
        $issues.Add("Package artifact bytes changed during validation")
    }
    if (($Before.producerFiles | ConvertTo-Json -Depth 10 -Compress) -cne
        ($After.producerFiles | ConvertTo-Json -Depth 10 -Compress)) {
        $issues.Add("the validation evidence producer changed during validation")
    }

    $status = if ($issues.Count -eq 0) { "PASSED" } else { "FAILED" }
    return [ordered]@{
        schemaVersion             = 1
        producer                  = "build-and-validate.ps1"
        validationResult          = $status
        validationRan             = -not $ValidationSkipped
        packagingSkipped          = $PackagingSkipped
        toolkitRoot               = $After.toolkitRoot
        contentRoot               = $After.contentRoot
        solutionPath              = $After.solutionPath
        sourcePathSemantics       = $After.sourcePathSemantics
        producerPlatform          = $After.producerPlatform
        evidenceRunPath            = [System.IO.Path]::GetFullPath($EvidenceRunPath)
        validationStartedAtUtc    = $Before.capturedAtUtc
        validationCompletedAtUtc = $After.capturedAtUtc
        validatorSummary          = [ordered]@{
            total   = $passed + $failed + $skipped
            passed  = $passed
            failed  = $failed
            skipped = $skipped
        }
        package                   = $After.package
        inputFilesBefore          = $Before.inputFiles
        inputFilesAfter           = $After.inputFiles
        packageFilesBefore        = $Before.package.packageFiles
        packageFilesAfter         = $After.package.packageFiles
        producerFilesBefore       = $Before.producerFiles
        producerFilesAfter        = $After.producerFiles
        issues                    = @($issues)
    }
}

function Write-ValidationEvidenceBinding {
    param(
        [Parameter(Mandatory = $true)]
        [string]$EvidenceRunPath,

        [Parameter(Mandatory = $true)]
        [System.Collections.IDictionary]$Binding
    )

    $path = Join-Path ([System.IO.Path]::GetFullPath($EvidenceRunPath)) "build-and-validate-binding.json"
    $json = ConvertTo-Json -InputObject $Binding -Depth 30
    [System.IO.File]::WriteAllText($path, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    return [ordered]@{
        path   = $path
        sha256 = (Get-FileHash -LiteralPath $path -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant()
    }
}
