<#
.SYNOPSIS
    Collects diagnostics for an ASIM ingestion-time parser validation run.

.DESCRIPTION
    Downloads GitHub Actions metadata, relevant logs, and asim-ingestion-*
    artifacts, then produces normalized JSON and Markdown summaries. The script
    is read-only with respect to GitHub, the repository, and Azure.

.PARAMETER Run
    A numeric GitHub Actions run ID or a URL containing /actions/runs/<id>.

.PARAMETER Repository
    GitHub repository in owner/name form. Defaults to Azure/Azure-Sentinel.

.PARAMETER OutputDirectory
    Destination for diagnostics. Defaults to a timestamped directory under
    $env:TEMP.

.PARAMETER Attempt
    Specific run attempt. An /attempts/<number> URL sets this automatically.

.PARAMETER IncludeSuccessfulTargetLogs
    Also download logs for successful static and ingestion target jobs.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory, Position = 0)]
    [string]$Run,

    [ValidatePattern('^[^/]+/[^/]+$')]
    [string]$Repository = "Azure/Azure-Sentinel",

    [ValidateRange(0, [int]::MaxValue)]
    [int]$Attempt = 0,

    [string]$OutputDirectory,

    [switch]$IncludeSuccessfulTargetLogs
)

$ErrorActionPreference = "Stop"

function Get-RunId {
    param([string]$Value)

    if ($Value -match '^\d+$') {
        return $Value
    }
    if ($Value -match '/actions/runs/(?<id>\d+)') {
        return $Matches.id
    }
    throw "Run must be a numeric ID or a GitHub Actions run URL."
}

function Invoke-GhText {
    param(
        [string[]]$Arguments,
        [switch]$AllowFailure
    )

    $output = & gh @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $text = ($output | ForEach-Object { $_.ToString() }) -join "`n"
    if ($exitCode -ne 0 -and -not $AllowFailure) {
        throw "gh $($Arguments -join ' ') failed:`n$text"
    }
    return [PSCustomObject]@{
        ExitCode = $exitCode
        Text = $text
    }
}

function Invoke-GhJson {
    param([string[]]$Arguments)

    $result = Invoke-GhText -Arguments $Arguments
    if (-not $result.Text) {
        throw "gh $($Arguments -join ' ') returned no JSON."
    }
    return $result.Text | ConvertFrom-Json -Depth 100
}

function Read-JsonFile {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    return Get-Content -LiteralPath $Path -Raw |
        ConvertFrom-Json -Depth 100
}

function Get-DurationSeconds {
    param(
        [object]$StartedAt,
        [object]$CompletedAt
    )

    if (-not $StartedAt -or -not $CompletedAt) {
        return $null
    }
    $start = [DateTimeOffset]::Parse($StartedAt.ToString())
    $end = [DateTimeOffset]::Parse($CompletedAt.ToString())
    if ($end -lt $start) {
        return $null
    }
    return [Math]::Round(($end - $start).TotalSeconds, 3)
}

function Get-SafeName {
    param([string]$Value)

    $safe = $Value -replace '[^A-Za-z0-9._-]+', '-'
    return $safe.Trim('-')
}

function ConvertTo-MarkdownCell {
    param([object]$Value)

    if ($null -eq $Value) {
        return ""
    }
    return ($Value.ToString() -replace '\|', '\|' -replace '\r?\n', '<br>')
}

function Get-NestedMessages {
    param([object]$Value)

    $messages = [System.Collections.Generic.List[string]]::new()

    function Visit-Node {
        param([object]$Node)

        if ($null -eq $Node) {
            return
        }
        if ($Node -is [string]) {
            return
        }
        if ($Node -is [System.Collections.IEnumerable] -and
            $Node -isnot [System.Collections.IDictionary]) {
            foreach ($item in $Node) {
                Visit-Node -Node $item
            }
            return
        }
        foreach ($property in $Node.PSObject.Properties) {
            if ($property.Name -eq "message" -and
                $property.Value -is [string] -and
                $property.Value) {
                $messages.Add($property.Value)
            }
            Visit-Node -Node $property.Value
        }
    }

    Visit-Node -Node $Value
    return @($messages | Select-Object -Unique)
}

function Add-Recommendation {
    param(
        [System.Collections.Generic.List[string]]$Recommendations,
        [string]$Text
    )

    if ($Text -and -not $Recommendations.Contains($Text)) {
        $Recommendations.Add($Text)
    }
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI 'gh' is required."
}

$auth = Invoke-GhText -Arguments @("auth", "status") -AllowFailure
if ($auth.ExitCode -ne 0) {
    throw "GitHub CLI authentication is required. Run 'gh auth login'."
}

$runId = Get-RunId -Value $Run
if ($Attempt -eq 0 -and $Run -match '/attempts/(?<attempt>\d+)') {
    $Attempt = [int]$Matches.attempt
}
if (-not $OutputDirectory) {
    $timestamp = [DateTimeOffset]::UtcNow.ToString("yyyyMMddTHHmmssZ")
    $OutputDirectory = Join-Path $env:TEMP (
        "asim-itp-validation-$runId-$timestamp"
    )
}
$OutputDirectory = [System.IO.Path]::GetFullPath($OutputDirectory)
$artifactDirectory = Join-Path $OutputDirectory "artifacts"
$logDirectory = Join-Path $OutputDirectory "logs"
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
New-Item -ItemType Directory -Force -Path $artifactDirectory | Out-Null
New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null

$latestRunApi = Invoke-GhJson -Arguments @(
    "api",
    "repos/$Repository/actions/runs/$runId"
)
$runApi = if ($Attempt -gt 0) {
    Invoke-GhJson -Arguments @(
        "api",
        "repos/$Repository/actions/runs/$runId/attempts/$Attempt"
    )
} else {
    $latestRunApi
}
$runViewArguments = @(
    "run", "view", $runId,
    "--repo", $Repository,
    "--json", "jobs"
)
if ($Attempt -gt 0) {
    $runViewArguments += @("--attempt", $Attempt)
}
$runView = Invoke-GhJson -Arguments $runViewArguments

$pullRequestNumber = $null
if ($Run -match '[?&]pr=(?<pr>\d+)') {
    $pullRequestNumber = [int]$Matches.pr
} elseif (
    $latestRunApi.pull_requests -and
    $latestRunApi.pull_requests.Count -gt 0
) {
    $pullRequestNumber = [int]$latestRunApi.pull_requests[0].number
}

$pullRequest = $null
if ($pullRequestNumber) {
    $pullRequestFields = (
        "number,title,state,baseRefName,baseRefOid,headRefName,headRefOid," +
        "files,commits,updatedAt,url"
    )
    $pullRequest = Invoke-GhJson -Arguments @(
        "pr", "view", $pullRequestNumber,
        "--repo", $Repository,
        "--json", $pullRequestFields
    )
}

$jobSummaries = @()
foreach ($job in $runView.jobs) {
    $failedSteps = @(
        $job.steps |
            Where-Object { $_.conclusion -in @("failure", "cancelled") } |
            ForEach-Object { $_.name }
    )
    $jobSummaries += [PSCustomObject][ordered]@{
        id = $job.databaseId
        name = $job.name
        status = $job.status
        conclusion = $job.conclusion
        startedAt = $job.startedAt
        completedAt = $job.completedAt
        durationSeconds = Get-DurationSeconds `
            -StartedAt $job.startedAt `
            -CompletedAt $job.completedAt
        failedSteps = $failedSteps
        url = $job.url
    }

    $isTargetJob = (
        $job.name -like "Static template validation (*" -or
        $job.name -like "Ingested data validation (*"
    )
    $downloadLog = (
        $job.name -eq "Discover ASIM ingestion validation targets" -or
        $job.name -eq "ASIM ingestion-time parser validation report" -or
        $job.conclusion -in @("failure", "cancelled") -or
        ($IncludeSuccessfulTargetLogs -and $isTargetJob)
    )
    if ($downloadLog -and $job.databaseId) {
        $logName = "{0}-{1}.log" -f $job.databaseId, (Get-SafeName $job.name)
        $logPath = Join-Path $logDirectory $logName
        $logResult = Invoke-GhText -Arguments @(
            "run", "view", $runId,
            "--repo", $Repository,
            "--job", $job.databaseId,
            "--log"
        ) -AllowFailure
        [System.IO.File]::WriteAllText(
            $logPath,
            $logResult.Text,
            [System.Text.UTF8Encoding]::new($false)
        )
    }
}

$artifactAttemptIsCurrent = (
    $Attempt -eq 0 -or
    $Attempt -eq [int]$latestRunApi.run_attempt
)
$artifactResult = if ($artifactAttemptIsCurrent) {
    Invoke-GhText -Arguments @(
        "run", "download", $runId,
        "--repo", $Repository,
        "--pattern", "asim-ingestion-*",
        "--dir", $artifactDirectory
    ) -AllowFailure
} else {
    [PSCustomObject]@{
        ExitCode = 1
        Text = (
            "Artifact download skipped for attempt $Attempt because " +
            "'gh run download' is not attempt-scoped. Use the attempt " +
            "page for manual artifact retrieval if required."
        )
    }
}

$discoveryPath = Get-ChildItem -LiteralPath $artifactDirectory `
    -Recurse -Filter "discovery.json" -File -ErrorAction SilentlyContinue |
    Select-Object -First 1 -ExpandProperty FullName
$matrixPath = Get-ChildItem -LiteralPath $artifactDirectory `
    -Recurse -Filter "matrix.json" -File -ErrorAction SilentlyContinue |
    Select-Object -First 1 -ExpandProperty FullName
$discovery = if ($discoveryPath) {
    Read-JsonFile -Path $discoveryPath
} else {
    $null
}
$matrix = if ($matrixPath) {
    Read-JsonFile -Path $matrixPath
} else {
    $null
}

$targetSummaries = @()
$reportFiles = @(
    Get-ChildItem -LiteralPath $artifactDirectory `
        -Recurse -Filter "report.json" -File -ErrorAction SilentlyContinue
)
$targetFiles = @(
    Get-ChildItem -LiteralPath $artifactDirectory `
        -Recurse -Filter "target.json" -File -ErrorAction SilentlyContinue
)

$targetIds = [System.Collections.Generic.HashSet[string]]::new(
    [System.StringComparer]::OrdinalIgnoreCase
)
foreach ($file in $reportFiles + $targetFiles) {
    $document = Read-JsonFile -Path $file.FullName
    if ($document.targetId) {
        [void]$targetIds.Add($document.targetId)
    } elseif ($document.correlation.targetId) {
        [void]$targetIds.Add($document.correlation.targetId)
    }
}
if ($matrix -and $matrix.targets) {
    foreach ($target in $matrix.targets) {
        if ($target.targetId) {
            [void]$targetIds.Add($target.targetId)
        }
    }
}

$stageOrder = @(
    "discovery", "counterpart", "template", "fixture", "filtering",
    "parserDcr", "parserIngestion", "schema", "data", "rawDcr",
    "rawIngestion", "qtpExecution", "parity", "cleanup"
)
$recommendations = [System.Collections.Generic.List[string]]::new()

if ($pullRequest -and $pullRequest.headRefOid -ne $runApi.head_sha) {
    Add-Recommendation -Recommendations $recommendations -Text (
        "The PR moved after this run. Diagnose commit $($runApi.head_sha), " +
        "then compare it with current head $($pullRequest.headRefOid)."
    )
}
foreach ($job in $jobSummaries) {
    if ($job.name -eq "Discover ASIM ingestion validation targets" -and
        $job.conclusion -eq "cancelled" -and
        $job.failedSteps -contains "Checkout trusted base revision") {
        Add-Recommendation -Recommendations $recommendations -Text (
            "Discovery timed out during trusted checkout. Inspect the exact " +
            "fetch refspec and fetch-depth before investigating Python discovery."
        )
    }
}

foreach ($targetId in $targetIds) {
    $matrixTarget = $null
    if ($matrix -and $matrix.targets) {
        $matrixTarget = $matrix.targets |
            Where-Object { $_.targetId -eq $targetId } |
            Select-Object -First 1
    }

    $reportPath = $reportFiles |
        Where-Object {
            (Read-JsonFile -Path $_.FullName).correlation.targetId -eq
                $targetId
        } |
        Select-Object -First 1 -ExpandProperty FullName
    $report = if ($reportPath) {
        Read-JsonFile -Path $reportPath
    } else {
        $null
    }

    $targetArtifactPath = $targetFiles |
        Where-Object {
            (Read-JsonFile -Path $_.FullName).targetId -eq $targetId
        } |
        Select-Object -First 1 -ExpandProperty FullName
    $targetArtifact = if ($targetArtifactPath) {
        Read-JsonFile -Path $targetArtifactPath
    } else {
        $null
    }

    $staticPath = Get-ChildItem -LiteralPath $artifactDirectory `
        -Recurse -Filter "static-validation.json" -File |
        Where-Object {
            $_.DirectoryName -match [regex]::Escape($targetId)
        } |
        Select-Object -First 1 -ExpandProperty FullName
    $staticResult = if ($staticPath) {
        Read-JsonFile -Path $staticPath
    } else {
        $null
    }

    $validationPath = Get-ChildItem -LiteralPath $artifactDirectory `
        -Recurse -Filter "validation-result.json" -File |
        Where-Object {
            $_.DirectoryName -match [regex]::Escape($targetId)
        } |
        Select-Object -First 1 -ExpandProperty FullName
    $validationResult = if ($validationPath) {
        Read-JsonFile -Path $validationPath
    } else {
        $null
    }

    $stages = @()
    if ($report -and $report.stages) {
        foreach ($stageName in $stageOrder) {
            $stageProperty = $report.stages.PSObject.Properties[$stageName]
            if ($stageProperty) {
                $stage = $stageProperty.Value
                $stages += [PSCustomObject][ordered]@{
                    name = $stageName
                    status = $stage.status
                    detail = $stage.detail
                }
            }
        }
    }

    $discoveryErrors = @()
    if ($matrixTarget -and $matrixTarget.discoveryErrors) {
        $discoveryErrors = @($matrixTarget.discoveryErrors)
    }
    foreach ($errorMessage in $discoveryErrors) {
        if ($errorMessage -like "*non-static expression*") {
            Add-Recommendation -Recommendations $recommendations -Text (
                "Remove dynamic EventVendor/EventProduct assignments for " +
                "$targetId; every assignment must use the same literal."
            )
        } elseif ($errorMessage -like "Missing source-table-specific fixture:*") {
            Add-Recommendation -Recommendations $recommendations -Text (
                $errorMessage -replace "^Missing ", "Add the missing "
            )
        }
    }

    $staticFindings = @()
    if ($staticResult -and $staticResult.findings) {
        $staticFindings = @($staticResult.findings)
        foreach ($finding in $staticFindings) {
            Add-Recommendation -Recommendations $recommendations -Text (
                "Resolve $($finding.code) for $targetId at " +
                "$($finding.field): $($finding.message)"
            )
        }
    }

    $errorObject = if ($report -and $report.error) {
        $report.error
    } elseif ($validationResult -and $validationResult.error) {
        $validationResult.error
    } else {
        $null
    }
    $errorMessages = Get-NestedMessages -Value $errorObject
    foreach ($message in $errorMessages) {
        if ($message -match 'Undefined symbol:\s*(?<symbol>[A-Za-z0-9_]+)') {
            Add-Recommendation -Recommendations $recommendations -Text (
                "Trace '$($Matches.symbol)' through project/project-rename " +
                "for $targetId; use its renamed value or create aliases " +
                "before the original name is removed."
            )
        }
    }

    $targetSummaries += [PSCustomObject][ordered]@{
        targetId = $targetId
        ingestTimeParserPath = if ($matrixTarget) {
            $matrixTarget.ingestTimeParserPath
        } elseif ($targetArtifact) {
            $targetArtifact.ingestTimeParserPath
        } else {
            $null
        }
        queryTimeParserPath = if ($matrixTarget) {
            $matrixTarget.queryTimeParserPath
        } elseif ($targetArtifact) {
            $targetArtifact.queryTimeParserPath
        } else {
            $null
        }
        discoveryErrors = $discoveryErrors
        staticValid = if ($staticResult) { $staticResult.valid } else { $null }
        staticFindings = $staticFindings
        requiredFailure = if ($report) {
            $report.requiredFailure
        } else {
            $null
        }
        error = $errorObject
        errorMessages = $errorMessages
        stages = $stages
    }
}

if ($discovery -and
    -not $discovery.changedParserPaths -and
    $discovery.changedPaths) {
    Add-Recommendation -Recommendations $recommendations -Text (
        "No canonical ITP path was detected. Verify exact " +
        "'IngestTimeParsers' casing and the parser filename/path."
    )
}

$runRecord = [PSCustomObject][ordered]@{
    version = 1
    repository = $Repository
    runId = [string]$runId
    runAttempt = $runApi.run_attempt
    workflowName = $runApi.name
    displayTitle = $runApi.display_title
    event = $runApi.event
    status = $runApi.status
    conclusion = $runApi.conclusion
    createdAt = $runApi.created_at
    updatedAt = $runApi.updated_at
    headBranch = $runApi.head_branch
    headSha = $runApi.head_sha
    url = $runApi.html_url
    pullRequest = $pullRequest
    pullRequestHeadChanged = (
        $pullRequest -and $pullRequest.headRefOid -ne $runApi.head_sha
    )
    jobs = $jobSummaries
}
$runRecord | ConvertTo-Json -Depth 100 |
    Set-Content -LiteralPath (Join-Path $OutputDirectory "run.json") `
        -Encoding utf8

$diagnostics = [PSCustomObject][ordered]@{
    version = 1
    run = $runRecord
    artifactDownload = [PSCustomObject][ordered]@{
        succeeded = $artifactResult.ExitCode -eq 0
        attemptScoped = $artifactAttemptIsCurrent
        message = $artifactResult.Text
        directory = $artifactDirectory
    }
    discovery = $discovery
    matrix = $matrix
    targets = $targetSummaries
    recommendations = @($recommendations)
    outputDirectory = $OutputDirectory
}
$diagnostics | ConvertTo-Json -Depth 100 |
    Set-Content -LiteralPath (
        Join-Path $OutputDirectory "diagnostics.json"
    ) -Encoding utf8

$markdown = [System.Collections.Generic.List[string]]::new()
$markdown.Add("# ASIM ITP validation diagnostics")
$markdown.Add("")
$markdown.Add("- **Run:** $runId (attempt $($runApi.run_attempt))")
$markdown.Add("- **Workflow:** $(ConvertTo-MarkdownCell $runApi.name)")
$markdown.Add("- **Conclusion:** $($runApi.conclusion)")
$markdown.Add(('- **Head:** `{0}`' -f $runApi.head_sha))
if ($pullRequestNumber) {
    $markdown.Add("- **Pull request:** #$pullRequestNumber")
}
if ($pullRequest -and $pullRequest.headRefOid -ne $runApi.head_sha) {
    $markdown.Add(
        ('- **Current PR head:** `{0}` (different from the run head)' -f
            $pullRequest.headRefOid)
    )
}
$markdown.Add("")
$markdown.Add("## Jobs")
$markdown.Add("")
$markdown.Add("| Job | Conclusion | Duration (s) | Failed/cancelled steps |")
$markdown.Add("|---|---:|---:|---|")
foreach ($job in $jobSummaries) {
    $markdown.Add(
        "| $(ConvertTo-MarkdownCell $job.name) | " +
        "$(ConvertTo-MarkdownCell $job.conclusion) | " +
        "$(ConvertTo-MarkdownCell $job.durationSeconds) | " +
        "$(ConvertTo-MarkdownCell ($job.failedSteps -join ', ')) |"
    )
}

$markdown.Add("")
$markdown.Add("## Discovery")
$markdown.Add("")
if ($discovery) {
    $markdown.Add(
        "- Changed paths: $(@($discovery.changedPaths).Count)"
    )
    $markdown.Add(
        "- Changed parser paths: $(@($discovery.changedParserPaths).Count)"
    )
    $markdown.Add("- Targets: $(@($discovery.targets).Count)")
    if ($discovery.indexErrors) {
        foreach ($indexError in $discovery.indexErrors) {
            $markdown.Add(
                "- Index error: $(ConvertTo-MarkdownCell $indexError)"
            )
        }
    }
} else {
    $markdown.Add(
        "- No discovery artifact was available. Inspect the discovery log."
    )
    if ($artifactResult.Text) {
        $markdown.Add(
            "- Artifact note: $(ConvertTo-MarkdownCell $artifactResult.Text)"
        )
    }
}

$markdown.Add("")
$markdown.Add("## Targets")
$markdown.Add("")
if ($targetSummaries.Count -eq 0) {
    $markdown.Add("No validation targets were produced.")
}
foreach ($target in $targetSummaries) {
    $markdown.Add("### $($target.targetId)")
    $markdown.Add("")
    if ($target.ingestTimeParserPath) {
        $markdown.Add(
            ('- Parser: `{0}`' -f
                (ConvertTo-MarkdownCell $target.ingestTimeParserPath))
        )
    }
    foreach ($discoveryError in $target.discoveryErrors) {
        $markdown.Add(
            "- Discovery error: $(ConvertTo-MarkdownCell $discoveryError)"
        )
    }
    foreach ($finding in $target.staticFindings) {
        $markdown.Add(
            ('- Static finding: `{0}` {1} — {2}' -f
                $finding.code,
                (ConvertTo-MarkdownCell $finding.field),
                (ConvertTo-MarkdownCell $finding.message))
        )
    }
    foreach ($message in $target.errorMessages) {
        $markdown.Add(
            "- Runtime error: $(ConvertTo-MarkdownCell $message)"
        )
    }
    if ($target.stages.Count -gt 0) {
        $markdown.Add("")
        $markdown.Add("| Stage | Status | Detail |")
        $markdown.Add("|---|---:|---|")
        foreach ($stage in $target.stages) {
            $markdown.Add(
                "| $($stage.name) | " +
                "$(ConvertTo-MarkdownCell $stage.status) | " +
                "$(ConvertTo-MarkdownCell $stage.detail) |"
            )
        }
    }
    $markdown.Add("")
}

$markdown.Add("")
$markdown.Add("## Recommendations")
$markdown.Add("")
if ($recommendations.Count -eq 0) {
    $markdown.Add(
        "No automatic recommendation was generated. Review the earliest " +
        "failed stage and its exact artifact evidence."
    )
} else {
    foreach ($recommendation in $recommendations) {
        $markdown.Add("- $recommendation")
    }
}

$markdown.Add("")
$markdown.Add("## Evidence directory")
$markdown.Add("")
$markdown.Add(('`{0}`' -f $OutputDirectory))

[System.IO.File]::WriteAllLines(
    (Join-Path $OutputDirectory "diagnostics.md"),
    $markdown,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Output "Diagnostics written to: $OutputDirectory"
Write-Output (
    "Summary: " + (Join-Path $OutputDirectory "diagnostics.md")
)
