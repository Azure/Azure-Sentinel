# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the repository root.

function Get-DefenderWorkbookSelection {
    param([psobject]$ContentToImport, [string]$SolutionRoot, [string]$SolutionName)

    $property = $ContentToImport.PSObject.Properties['XDR Workbooks']
    if ($null -eq $property) {
        $directory = Join-Path $SolutionRoot 'XDR Workbooks'
        if (Test-Path -LiteralPath $directory) {
            Assert-NoSolutionContentSymlinks -SolutionRoot $SolutionRoot
            if (@(Get-ChildItem -LiteralPath $directory -Recurse -File -Force |
                    Where-Object { $_.Extension -ieq '.json' }).Count -gt 0) {
                throw "Existing XDR Workbooks require an explicit 'XDR Workbooks' selection array; use [] to exclude them."
            }
        }
        return
    }
    if ($property.Value -isnot [array]) {
        throw "Solution Data 'XDR Workbooks' must be an explicit array."
    }
    $seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($reference in $property.Value) {
        if ($reference -isnot [string] -or [string]::IsNullOrWhiteSpace($reference)) {
            throw "XDR Workbooks selection must contain nonempty local path strings."
        }
        $resolved = Resolve-SolutionContentPath -SolutionRoot $SolutionRoot -SolutionName $SolutionName `
            -ContentPath $reference -RequireFile
        if (-not $resolved.RelativePath.StartsWith('XDR Workbooks/', [System.StringComparison]::Ordinal) -or
            [System.IO.Path]::GetExtension($resolved.FullPath) -ine '.json') {
            throw "Defender Workbook selection must reference JSON files under XDR Workbooks: $reference"
        }
        if (-not $seen.Add($resolved.FullPath)) {
            throw "Duplicate Defender Workbook selection: $reference"
        }
        $resolved
    }
}

function Assert-DefenderWorkbookReleaseVersion {
    param([string]$Version)
    if ($Version -cnotmatch '\A3\.[1-9][0-9]*\.(?:0|[1-9][0-9]*)\z') {
        throw "Defender Workbook release version '$Version' must be canonical major.minor.patch in [3.1.0, 4.0.0)."
    }
}

function Assert-NativeDefenderWorkbookDocument {
    param([psobject]$Document, [string]$SolutionRoot,
        [ValidateSet('native_workbooks', 'workbook_updates', 'workbook_publication')][string]$ValidationModule = 'native_workbooks')

    $python = if ($env:SENTINEL_XDR_PYTHON) { $env:SENTINEL_XDR_PYTHON } else { 'python' }
    $start = [System.Diagnostics.ProcessStartInfo]::new()
    $start.FileName = $python
    $start.UseShellExecute = $false
    $start.RedirectStandardInput = $true
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $start.StandardInputEncoding = [System.Text.UTF8Encoding]::new($false)
    $start.StandardOutputEncoding = [System.Text.UTF8Encoding]::new($false)
    foreach ($argument in @('-m', "sentinel_xdr_migration.$ValidationModule", $SolutionRoot)) {
        $start.ArgumentList.Add($argument)
    }
    $start.Environment['PYTHONPATH'] = [System.IO.Path]::GetFullPath(
        (Join-Path $PSScriptRoot '../../SentinelToXDRMigration'))
    $start.Environment['PYTHONIOENCODING'] = 'utf-8'
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $start
    try {
        [void]$process.Start()
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        $process.StandardInput.Write(($Document | ConvertTo-Json -Depth 100 -Compress))
        $process.StandardInput.Close()
        $process.WaitForExit()
        $output = $stdout.GetAwaiter().GetResult()
        $diagnostic = $stderr.GetAwaiter().GetResult()
        if ($process.ExitCode -ne 0) {
            throw "Native Defender Workbook validation failed: $output $diagnostic"
        }
        $receipt = $output | ConvertFrom-Json -ErrorAction Stop
        if ($null -eq $receipt -or $receipt.errors -isnot [array] -or $receipt.errors.Count -ne 0) {
            throw 'Native Defender Workbook validation returned no valid receipt.'
        }
    } finally {
        $process.Dispose()
    }
}

function Assert-DefenderWorkbookDocument {
    param([psobject]$Document, [string]$SolutionRoot, [string]$SolutionName, [string]$ContentPath, [switch]$PassThruSource)

    if ($Document -isnot [pscustomobject] -or $Document.version -cne 'Notebook/1.0' -or
        $Document.items -isnot [array]) {
        throw "Defender Workbook '$ContentPath' must be a complete Notebook/1.0 object with an items array."
    }
    Assert-DefenderWorkbookSerializationDepth -Value $Document
    $metadata = $Document.xdrMetadata
    $guidPattern = '\A[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\z'
    if ($metadata -isnot [pscustomobject] -or $metadata.schemaVersion -cne '1.0.0' -or
        $metadata.contentId -isnot [string] -or $metadata.contentId -cnotmatch $guidPattern -or
        $metadata.instanceId -isnot [string] -or $metadata.instanceId -cnotmatch $guidPattern -or
        $metadata.contentId -ieq $metadata.instanceId -or
        $metadata.displayName -isnot [string] -or [string]::IsNullOrWhiteSpace($metadata.displayName)) {
        throw "Defender Workbook '$ContentPath' requires distinct canonical contentId/instanceId GUIDs and reviewed displayName."
    }
    Assert-DefenderWorkbookReleaseVersion -Version $metadata.version
    $provenance = $Document.contentProvenance
    if ($null -ne $provenance -and $provenance.format -ceq 'public-workbook-v1') {
        Assert-NativeDefenderWorkbookDocument -Document $Document -SolutionRoot $SolutionRoot `
            -ValidationModule workbook_publication
        if ($PassThruSource) { return $Document }
        return
    }
    return (Assert-LegacyDefenderWorkbookDocument -Document $Document -SolutionRoot $SolutionRoot `
        -SolutionName $SolutionName -ContentPath $ContentPath -PassThruSource:$PassThruSource)
}

# Legacy diagnostics are not a publication entry point.
function Assert-LegacyDefenderWorkbookDocument {
    param([psobject]$Document, [string]$SolutionRoot, [string]$SolutionName, [string]$ContentPath, [switch]$PassThruSource)
    $provenance = $Document.contentProvenance
    if ($null -ne $provenance -and $null -ne $provenance.PSObject.Properties['authoredReview']) {
        Assert-NativeDefenderWorkbookDocument -Document $Document -SolutionRoot $SolutionRoot `
            -ValidationModule workbook_updates
        if ($PassThruSource) {
            if ($provenance.origin -ceq 'native-xdr') {
                return $Document
            }
            $resolved = Resolve-SolutionContentPath -SolutionRoot $SolutionRoot -SolutionName $SolutionName `
                -ContentPath $provenance.source.path -RequireFile
            return (Get-Content -LiteralPath $resolved.FullPath -Raw | ConvertFrom-Json -ErrorAction Stop)
        }
        return
    }
    if ($null -ne $provenance -and $provenance.origin -ceq 'native-xdr') {
        Assert-NativeDefenderWorkbookDocument -Document $Document -SolutionRoot $SolutionRoot
        if ($PassThruSource) {
            $nativePayload = $Document | ConvertTo-Json -Depth 100 -Compress |
                ConvertFrom-Json -ErrorAction Stop
            $nativePayload.PSObject.Properties.Remove('xdrMetadata')
            $nativePayload.PSObject.Properties.Remove('contentProvenance')
            return $nativePayload
        }
        return
    }
    if ($null -ne $provenance.PSObject.Properties['origin'] -and
        $provenance.origin -cne 'sentinel-migration') {
        throw "Defender Workbook '$ContentPath' has an unknown origin."
    }
    if ($provenance -isnot [pscustomobject] -or
        $provenance.dependencyReviewRequired -isnot [bool] -or $provenance.dependencyReviewRequired -or
        $provenance.conversion -isnot [pscustomobject] -or
        $provenance.conversion.tool -isnot [string] -or [string]::IsNullOrWhiteSpace($provenance.conversion.tool) -or
        $provenance.conversion.version -isnot [string] -or [string]::IsNullOrWhiteSpace($provenance.conversion.version) -or
        $provenance.conversion.reviewRequired -isnot [bool] -or $provenance.conversion.reviewRequired) {
        throw "Defender Workbook '$ContentPath' requires explicitly reviewed conversion and dependency provenance."
    }
    $source = $provenance.source
    if ($source -isnot [pscustomobject] -or $source.path -isnot [string] -or
        $source.sha256 -isnot [string] -or $source.sha256 -cnotmatch '\A[0-9a-fA-F]{64}\z') {
        throw "Defender Workbook '$ContentPath' requires its current source path and SHA256."
    }
    $resolvedSource = Resolve-SolutionContentPath -SolutionRoot $SolutionRoot -SolutionName $SolutionName `
        -ContentPath $source.path -RequireFile
    if (-not $resolvedSource.RelativePath.StartsWith('Workbooks/', [System.StringComparison]::Ordinal) -or
        [System.IO.Path]::GetExtension($resolvedSource.FullPath) -ine '.json' -or
        (Get-FileHash -LiteralPath $resolvedSource.FullPath -Algorithm SHA256).Hash -ine $source.sha256) {
        throw "Defender Workbook '$ContentPath' source identity/hash is stale or outside Workbooks."
    }
    if ($provenance.conversion.queries -isnot [array]) {
        throw "Defender Workbook '$ContentPath' requires conversion.queries as an array."
    }
    $sourceNotebook = Get-Content -LiteralPath $resolvedSource.FullPath -Raw -ErrorAction Stop |
        ConvertFrom-Json -ErrorAction Stop
    if ($sourceNotebook -isnot [pscustomobject] -or $sourceNotebook.version -cne 'Notebook/1.0' -or
        $sourceNotebook.items -isnot [array]) {
        throw "Defender Workbook '$ContentPath' source must be a complete Notebook/1.0."
    }
    $sourcePointers = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    $targetPointers = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($query in $provenance.conversion.queries) {
        if ($query -isnot [pscustomobject] -or
            $query.status -cnotin @('converted', 'removed-scope-helper') -or
            $query.sourcePath -isnot [string] -or -not $query.sourcePath.StartsWith('/') -or
            $query.sourceSha256 -isnot [string] -or $query.sourceSha256 -cnotmatch '\A[0-9a-fA-F]{64}\z' -or
            -not $sourcePointers.Add($query.sourcePath)) {
            throw "Defender Workbook '$ContentPath' has unreviewed or malformed query provenance."
        }
        $sourceQuery = Get-DefenderWorkbookJsonPointer -Document $sourceNotebook -Pointer $query.sourcePath
        if ($sourceQuery -isnot [string]) {
            throw "Defender Workbook '$ContentPath' source query pointer must resolve to a string."
        }
        $sourceBytes = [System.Text.Encoding]::UTF8.GetBytes($sourceQuery)
        $sourceHash = [System.Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData($sourceBytes))
        if ($sourceHash -ine $query.sourceSha256) {
            throw "Defender Workbook '$ContentPath' source query hash is stale."
        }
        if ($query.status -ceq 'removed-scope-helper') {
            if ($null -ne $query.outputPath -or $null -ne $query.targetSha256) {
                throw "Defender Workbook '$ContentPath' removed scope query must have null output identity."
            }
            continue
        }
        if ($query.outputPath -isnot [string] -or -not $query.outputPath.StartsWith('/') -or
            $query.targetSha256 -isnot [string] -or $query.targetSha256 -cnotmatch '\A[0-9a-fA-F]{64}\z' -or
            -not $targetPointers.Add($query.outputPath)) {
            throw "Defender Workbook '$ContentPath' requires current target query provenance."
        }
        $targetQuery = Get-DefenderWorkbookJsonPointer -Document $Document -Pointer $query.outputPath
        if ($targetQuery -isnot [string]) {
            throw "Defender Workbook '$ContentPath' target query pointer must resolve to a string."
        }
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($targetQuery)
        $hash = [System.Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData($bytes))
        if ($hash -ine $query.targetSha256) {
            throw "Defender Workbook '$ContentPath' target query hash is stale."
        }
    }
    Assert-DefenderWorkbookRemovedScopeQueries -Source $sourceNotebook -Document $Document
    $workloads = @('mde', 'mdo', 'mdi', 'mda', 'mdc', 'entraid', 'purview', 'appgovernance', 'sentinel', 'mtp')
    foreach ($field in @('requiredWorkloads', 'requiredDataConnectors')) {
        $value = $provenance.PSObject.Properties[$field]
        if ($null -eq $value -or $value.Value -isnot [array]) {
            throw "Defender Workbook '$ContentPath' requires contentProvenance.$field as an array."
        }
        $identityField = if ($field -eq 'requiredWorkloads') { 'workload' } else { 'connectorId' }
        $seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
        foreach ($record in $value.Value) {
            if ($record -isnot [pscustomobject] -or $record.$identityField -isnot [string] -or
                [string]::IsNullOrWhiteSpace($record.$identityField) -or
                $record.dataTypes -isnot [array] -or -not $seen.Add($record.$identityField)) {
                throw "Defender Workbook '$ContentPath' has malformed or duplicate $field records."
            }
            if ($field -eq 'requiredWorkloads' -and $record.workload -cnotin $workloads) {
                throw "Defender Workbook '$ContentPath' has unknown workload '$($record.workload)'."
            }
            $types = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
            foreach ($dataType in $record.dataTypes) {
                if ($dataType -isnot [string] -or [string]::IsNullOrWhiteSpace($dataType) -or
                    -not $types.Add($dataType)) {
                    throw "Defender Workbook '$ContentPath' has malformed or duplicate dependency dataTypes."
                }
                if ($dataType -ieq 'Watchlist') {
                    throw "Defender Workbook '$ContentPath' Watchlist is platform reference data, not a telemetry dependency."
                }
            }
        }
    }
    if ($PassThruSource) { return $sourceNotebook }
}

function Assert-DefenderWorkbookSerializationDepth {
    param([AllowNull()][object]$Value, [int]$Depth = 0)
    if ($Depth -gt 85) {
        throw 'Defender Workbook exceeds safe package JSON serialization depth; content cannot be truncated.'
    }
    if ($Value -is [pscustomobject]) {
        foreach ($property in $Value.PSObject.Properties) {
            Assert-DefenderWorkbookSerializationDepth -Value $property.Value -Depth ($Depth + 1)
        }
    }
    elseif ($Value -is [array]) {
        foreach ($item in $Value) {
            Assert-DefenderWorkbookSerializationDepth -Value $item -Depth ($Depth + 1)
        }
    }
}

function Get-DefenderWorkbookJsonPointer {
    param([psobject]$Document, [string]$Pointer)
    $value = $Document
    foreach ($part in $Pointer.Substring(1).Split('/')) {
        if ($part -cmatch '~(?:[^01]|$)') { throw "Invalid Defender Workbook query JSON pointer: $Pointer" }
        $key = $part.Replace('~1', '/').Replace('~0', '~')
        if ($value -is [array] -and $key -cmatch '\A(?:0|[1-9][0-9]*)\z' -and
            [System.Numerics.BigInteger]::Parse($key) -lt $value.Count) {
            $value = $value[[int]$key]
        }
        elseif ($value -is [pscustomobject] -and $null -ne $value.PSObject.Properties[$key]) {
            $value = $value.PSObject.Properties[$key].Value
        }
        else { throw "Unresolvable Defender Workbook query JSON pointer: $Pointer" }
    }
    return $value
}

function Get-DefenderWorkbookDeploymentName {
    param([string]$SolutionName, [string]$ContentId)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes("$SolutionName/$ContentId")
    $hash = [System.Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData($bytes)).ToLowerInvariant()
    return 'DefenderWorkbook-' + $hash.Substring(0, 32)
}

function Get-DefenderWorkbookNodes {
    param([AllowNull()][object]$Value, [string]$Path = '', [object]$QueryType = 0, [string]$ResourceType = '')
    if ($Value -is [pscustomobject]) {
        if ($null -ne $Value.PSObject.Properties['queryType']) { $QueryType = $Value.queryType }
        if ($Value.resourceType) { $ResourceType = $Value.resourceType }
        [pscustomobject]@{ Path = $Path; Node = $Value; QueryType = $QueryType; ResourceType = $ResourceType }
        foreach ($property in $Value.PSObject.Properties) {
            $key = $property.Name.Replace('~', '~0').Replace('/', '~1')
            Get-DefenderWorkbookNodes -Value $property.Value -Path "$Path/$key" -QueryType $QueryType -ResourceType $ResourceType
        }
    }
    elseif ($Value -is [array]) {
        for ($i = 0; $i -lt $Value.Count; $i++) {
            Get-DefenderWorkbookNodes -Value $Value[$i] -Path "$Path/$i" -QueryType $QueryType -ResourceType $ResourceType
        }
    }
}

function Get-DefenderWorkbookParameterReferences {
    param([AllowNull()][object]$Value, [switch]$SkipScope, [switch]$SkipParameters)
    if ($Value -is [string]) {
        foreach ($match in [regex]::Matches($Value, '\{([A-Za-z_][\w .-]*)(?::[^{}]*)?\}')) { $match.Groups[1].Value }
    }
    elseif ($Value -is [pscustomobject]) {
        foreach ($property in $Value.PSObject.Properties) {
            if ($SkipParameters -and $property.Name -ceq 'parameters' -and $property.Value -is [array]) { continue }
            if ($SkipScope -and $property.Name -cin @(
                'crossComponentResources', 'fallbackResourceIds', 'resourceIds', 'workspaceId',
                'workspaceResourceId', 'selectedWorkspaceIds', 'resourceContextFromParameter'
            )) { continue }
            if ($property.Name -cin @('parameterName', 'exportParameterName', 'timeContextFromParameter', 'resourceContextFromParameter') -and
                $property.Value -is [string]) { $property.Value }
            if ($property.Name -ceq 'linkTarget' -and $property.Value -ceq 'parameter') { $Value.cellValue }
            Get-DefenderWorkbookParameterReferences -Value $property.Value -SkipScope:$SkipScope -SkipParameters:$SkipParameters
        }
    }
    elseif ($Value -is [array]) {
        foreach ($item in $Value) {
            Get-DefenderWorkbookParameterReferences -Value $item -SkipScope:$SkipScope -SkipParameters:$SkipParameters
        }
    }
}

function Assert-DefenderWorkbookRemovedScopeQueries {
    param([psobject]$Source, [psobject]$Document)
    $removedQueries = @($Document.contentProvenance.conversion.queries | Where-Object status -CEQ 'removed-scope-helper')
    if ($removedQueries.Count -eq 0) { return }
    # Mirror the reviewed Python _scope_parameters dependency closure; a status alone is not proof.
    $nodes = @(Get-DefenderWorkbookNodes -Value $Source)
    $entries = @($nodes | Where-Object { $_.Path -cmatch '/parameters/[0-9]+$' -and $_.Node.name })
    $params = [System.Collections.Generic.Dictionary[string,object]]::new([System.StringComparer]::Ordinal)
    $eligible = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    $candidates = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    $live = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    $bindings = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($entry in $nodes) {
        foreach ($property in $entry.Node.PSObject.Properties) {
            if ($property.Name -cin @(
                'crossComponentResources', 'fallbackResourceIds', 'resourceIds', 'workspaceId',
                'workspaceResourceId', 'selectedWorkspaceIds', 'resourceContextFromParameter'
            )) {
                foreach ($name in @(Get-DefenderWorkbookParameterReferences -Value $property.Value)) { [void]$bindings.Add($name) }
                if ($property.Name -ceq 'resourceContextFromParameter' -and $property.Value -is [string]) {
                    [void]$bindings.Add($property.Value)
                }
            }
        }
    }
    foreach ($entry in $entries) {
        $p = $entry.Node
        if ($p.name -isnot [string] -or $params.ContainsKey($p.name)) { throw 'Duplicate or invalid scope parameter names.' }
        $params.Add($p.name, $entry)
        $supported = -not $p.query -or $entry.QueryType -cin @(0, $null, 'advancedHunting')
        if (-not ($p.query -and $supported) -and $p.type -ne 4) {
            [void]$eligible.Add($p.name)
            $settings = $p.typeSettings | ConvertTo-Json -Depth 100 -Compress
            if ($p.type -eq 6 -or
                ($p.type -eq 5 -and ($bindings.Contains($p.name) -or $entry.ResourceType -ieq 'microsoft.operationalinsights/workspaces')) -or
                $settings -imatch 'microsoft\.operationalinsights/workspaces' -or
                ($p.queryType -eq 1 -and $p.query -imatch 'microsoft\.operationalinsights/workspaces')) {
                [void]$candidates.Add($p.name)
            }
        }
        $entry | Add-Member -NotePropertyName AllDependencies -NotePropertyValue @(Get-DefenderWorkbookParameterReferences -Value $p)
        $entry | Add-Member -NotePropertyName Dependencies -NotePropertyValue @(Get-DefenderWorkbookParameterReferences -Value $p -SkipScope:$supported)
    }
    do {
        $before = $candidates.Count
        foreach ($name in @($candidates)) {
            foreach ($dep in $params[$name].AllDependencies) {
                if ($eligible.Contains($dep)) { [void]$candidates.Add($dep) }
            }
        }
        foreach ($entry in $entries) {
            if ($eligible.Contains($entry.Node.name) -and $entry.Node.isHiddenWhenLocked -and
                @($entry.AllDependencies | Where-Object { $candidates.Contains($_) }).Count -gt 0) {
                [void]$candidates.Add($entry.Node.name)
            }
        }
    } while ($before -ne $candidates.Count)
    foreach ($name in $params.Keys) { if (-not $candidates.Contains($name)) { [void]$live.Add($name) } }
    foreach ($name in @(Get-DefenderWorkbookParameterReferences -Value $Source -SkipScope -SkipParameters)) {
        if ($params.ContainsKey($name)) { [void]$live.Add($name) }
    }
    do {
        $before = $live.Count
        foreach ($name in @($live)) {
            $deps = if ($candidates.Contains($name)) { $params[$name].AllDependencies } else { $params[$name].Dependencies }
            foreach ($dep in $deps) { if ($params.ContainsKey($dep)) { [void]$live.Add($dep) } }
        }
    } while ($before -ne $live.Count)
    $targetNodes = @(Get-DefenderWorkbookNodes -Value $Document.items -Path '/items')
    foreach ($query in $removedQueries) {
        if (-not $query.sourcePath.EndsWith('/query', [System.StringComparison]::Ordinal)) {
            throw 'Removed scope provenance must identify a query surface.'
        }
        $helper = @($entries | Where-Object {
            $query.sourcePath.StartsWith($_.Path + '/', [System.StringComparison]::Ordinal) -and
            $candidates.Contains($_.Node.name) -and -not $live.Contains($_.Node.name)
        })
        if ($helper.Count -ne 1) { throw 'Only proven scope-helper queries may be removed.' }
        $name = $helper[0].Node.name
        $sourceQuery = Get-DefenderWorkbookJsonPointer -Document $Source -Pointer $query.sourcePath
        if (@($targetNodes | Where-Object {
            ($_.Path -cmatch '/parameters/[0-9]+$' -and $_.Node.name -ceq $name) -or
            ($_.Node.query -is [string] -and $_.Node.query -ceq $sourceQuery)
        }).Count -gt 0 -or
            $name -cin @(Get-DefenderWorkbookParameterReferences -Value $Document.items)) {
            throw 'Removed scope helper is still present or referenced in the target workbook.'
        }
    }
}

function Get-DefenderWorkbookKnownCatalogTables {
    if ($null -eq $script:DefenderWorkbookKnownCatalogTables) {
        $set = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
        $catalogDir = Join-Path $PSScriptRoot '../../SentinelToXDRMigration/solution_manager/migration/_workbook_core/data'
        if (-not (Test-Path -LiteralPath $catalogDir -PathType Container)) {
            $catalogDir = Join-Path $PSScriptRoot '../../SentinelToXDRMigration/sentinel_xdr_migration/_workbook_core/data'
        }
        foreach ($file in @('mapping_catalog.json')) {
            $full = Join-Path $catalogDir $file
            if (Test-Path -LiteralPath $full -PathType Leaf) {
                $json = Get-Content -LiteralPath $full -Raw | ConvertFrom-Json
                if ($null -ne $json.tables) {
                    foreach ($prop in $json.tables.PSObject.Properties) {
                        [void]$set.Add($prop.Name)
                    }
                }
            }
        }
        $script:DefenderWorkbookKnownCatalogTables = $set
    }
    return ,$script:DefenderWorkbookKnownCatalogTables
}

function Get-DefenderWorkbookImplicitFunctions {
    param(
        [AllowNull()][object]$Value,
        [AllowNull()][System.Collections.Generic.HashSet[string]]$AllowedBareTables = $null,
        [AllowNull()][System.Collections.Generic.HashSet[string]]$KnownFunctionAliases = $null,
        [AllowNull()][System.Collections.Generic.HashSet[string]]$ExcludedQueryPaths = $null,
        [string]$Path = ''
    )
    if ($Value -is [pscustomobject]) {
        foreach ($property in $Value.PSObject.Properties) {
            $key = $property.Name.Replace('~', '~0').Replace('/', '~1')
            $childPath = "$Path/$key"
            if ($property.Name -ceq 'query' -and $property.Value -is [string]) {
                if ($null -ne $ExcludedQueryPaths -and $ExcludedQueryPaths.Contains($childPath)) { continue }
                if ($Value.queryType -eq 1 -and $Value.resourceType -ieq 'microsoft.resourcegraph/resources' -and
                    $property.Value -inotmatch 'microsoft\.operationalinsights/workspaces') { continue }
                $queryText = $property.Value
                if ($Value.queryType -eq 18 -and $queryText.TrimStart().StartsWith('{')) {
                    try { $settings = $queryText | ConvertFrom-Json -ErrorAction Stop }
                    catch { throw 'Malformed Defender Workbook query wrapper.' }
                    if ($settings -isnot [pscustomobject] -or
                        $settings.__advancedHuntingSettings -isnot [bool] -or
                        -not $settings.__advancedHuntingSettings -or $settings.query -isnot [string] -or
                        @($settings.PSObject.Properties.Name | Where-Object {
                            $_ -cnotin @('__advancedHuntingSettings', 'query', 'selectedWorkspaceIds')
                        }).Count -gt 0) {
                        throw 'Unrecognized Defender Workbook query wrapper.'
                    }
                    $queryText = $settings.query
                }
                $strPat = '@"(?:""|[^"])*"|@''(?:''''|[^''])*''|"(?:\\.|[^"\\])*"|''(?:\\.|[^''\\])*'''
                # Ignore single-line // comments (/* */ is NOT a KQL comment), but leave string
                # literals intact so a URL such as "https://..." is not mistaken for a comment.
                $noComments = [regex]::Replace($queryText, "(?s)$strPat|//[^\r\n]*", {
                    param($m)
                    if ($m.Value.StartsWith('//')) { ' ' } else { $m.Value }
                })
                $bracketPat = "(?s)\[\s*($strPat)\s*\]"
                $tableCallPat = "(?i)(?<![.\w])(?:table|totable)\s*\(\s*($strPat)\s*(?:,[^;\r\n)]*)?\)"
                $tableAnyCallPat = "(?i)(?<![.\w])(?:table|totable)\s*\("
                function ConvertFrom-KqlQuotedString([string]$lit) {
                    if ($lit.StartsWith('@"') -and $lit.EndsWith('"')) { return $lit.Substring(2, $lit.Length - 3).Replace('""', '"') }
                    if ($lit.StartsWith("@'") -and $lit.EndsWith("'")) { return $lit.Substring(2, $lit.Length - 3).Replace("''", "'") }
                    if ($lit.Length -ge 2 -and $lit[0] -eq $lit[$lit.Length - 1]) {
                        return [regex]::Replace($lit.Substring(1, $lit.Length - 2), '\\(.)', '$1')
                    }
                    return $lit
                }
                function Test-KqlUnionWithsourceBinding([string]$text, [int]$start) {
                    $prefix = [regex]::Replace($text.Substring(0, $start), $strPat, {
                        param($m) ' ' * $m.Length
                    })
                    $segmentStart = [Math]::Max($prefix.LastIndexOf('|'), $prefix.LastIndexOf(';'))
                    return [regex]::IsMatch($prefix.Substring($segmentStart + 1),
                        '(?i)\bunion\b(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*\s+withsource\s*=\s*$')
                }
                $protectedSpans = [System.Collections.Generic.List[pscustomobject]]::new()
                foreach ($m in [regex]::Matches($noComments, $bracketPat)) {
                    $protectedSpans.Add([pscustomobject]@{Start=$m.Index; End=($m.Index + $m.Length)})
                }
                foreach ($m in [regex]::Matches($noComments, $tableCallPat)) {
                    $protectedSpans.Add([pscustomobject]@{Start=$m.Index; End=($m.Index + $m.Length)})
                }
                $validSpans = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
                $validSpanStarts = [System.Collections.Generic.HashSet[int]]::new()
                $strMatches = [regex]::Matches($noComments, $strPat)
                foreach ($sp in $protectedSpans) {
                    $insideOuterString = $false
                    foreach ($sm in $strMatches) {
                        if ($sm.Index -lt $sp.Start -and ($sm.Index + $sm.Length) -gt $sp.Start) {
                            $insideOuterString = $true
                            break
                        }
                    }
                    if (-not $insideOuterString) {
                        [void]$validSpans.Add("$($sp.Start):$($sp.End)")
                        [void]$validSpanStarts.Add($sp.Start)
                    }
                }
                $tokPat = '\{[A-Za-z0-9_.:$ -]+\}'
                $braceBodyPrefixPat = '(?i)(?:\)|(?<![.\w])\bpartition\b(?:\s+hint\.[\w.]+\s*=\s*[\w.*-]+)*\s+by\s+[A-Za-z_]\w*)\s*\z'
                $codeWithTokens = [regex]::Replace($noComments, "(?s)$strPat", ' ')
                $code = [regex]::Replace($codeWithTokens, $tokPat, {
                    param($m)
                    $before = $codeWithTokens.Substring(0, $m.Index)
                    if ([regex]::IsMatch($before, $braceBodyPrefixPat)) { $m.Value }
                    elseif ($m.Value -match '[A-Za-z0-9_]') { ' ' * $m.Length }
                    else { $m.Value }
                })
                $codeWithTokens = [regex]::Replace($codeWithTokens, $tokPat, {
                    param($m)
                    $before = $codeWithTokens.Substring(0, $m.Index)
                    if ([regex]::IsMatch($before, $braceBodyPrefixPat)) { '{()' + $m.Value.Substring(1, $m.Value.Length - 2) + '}' }
                    else { $m.Value }
                })
                $locals = @(
                    @([regex]::Matches($code, '\blet\s+([A-Za-z_]\w*)\s*=') | ForEach-Object { $_.Groups[1].Value }) +
                    @([regex]::Matches($code, '(?i)\|\s*as\b(?:\s+hint\.[\w.]+\s*=\s*[\w.*-]+)*\s+([A-Za-z_]\w*)') | ForEach-Object { $_.Groups[1].Value })
                )
                $builtins = @(
                    'datatable', 'externaldata', 'external_data', 'range', 'print', 'dynamic', 'datetime', 'timespan',
                    'toscalar', 'tostring', 'toint', 'tolong', 'todouble', 'todatetime', 'todecimal', 'todynamic', 'toreal', 'totable',
                    'totimespan', 'tobool', 'now', 'ago', 'startofday', 'endofday', 'startofweek', 'endofweek',
                    'startofmonth', 'endofmonth', 'startofyear', 'endofyear', 'tolower', 'toupper', 'coalesce', 'iff', 'iif', 'case',
                    '_GetWatchlist', '_GetWatchlistAlias', 'workspace', 'app', 'resource', 'cluster', 'database', 'table', 'view', 'materialize',
                    'abs', 'acos', 'asin', 'atan', 'atan2', 'beta_cdf', 'beta_inv', 'beta_pdf', 'bin', 'bin_at', 'ceiling',
                    'cos', 'cot', 'count', 'count_distinct', 'count_distinctif', 'countif', 'countof',
                    'dcount', 'dcount_hll', 'dcountif', 'degrees', 'exp', 'exp10', 'exp2', 'floor', 'gamma',
                    'hash', 'hash_combine', 'hash_many', 'hash_md5', 'hash_sha1', 'hash_sha256', 'hash_xxhash64',
                    'isnan', 'isfinite', 'isinf', 'isascii', 'isempty', 'isnotempty', 'isnull', 'isnotnull', 'isutf8',
                    'log', 'log10', 'log2', 'loggamma', 'max', 'max_of', 'maxif', 'min', 'min_of', 'minif', 'mod',
                    'not', 'and', 'or', 'between', 'in', 'has', 'has_all', 'has_any', 'has_cs', 'contains', 'contains_cs',
                    'startswith', 'startswith_cs', 'endswith', 'endswith_cs', 'matches', 'regex',
                    'avg', 'avgif', 'sum', 'sumif', 'stdev', 'stdevif', 'stdevp', 'variance', 'varianceif', 'variancep',
                    'percentile', 'percentiles', 'percentilew', 'percentilesw', 'arg_max', 'arg_min', 'any', 'anyif', 'take_any', 'take_anyif',
                    'make_list', 'make_list_if', 'make_list_with_nulls', 'makelist', 'make_set', 'make_set_if', 'makeset',
                    'make_bag', 'make_bag_if', 'pack', 'pack_all', 'pack_array', 'pack_dictionary', 'bag_keys', 'bag_pack',
                    'bag_pack_columns', 'bag_merge', 'bag_remove_keys', 'bag_set_key', 'bag_has_key', 'bag_unpack',
                    'unpack_object', 'treepath', 'zip', 'repeat',
                    'array_concat', 'array_iif', 'array_index_of', 'array_iff', 'array_length', 'array_reverse',
                    'array_rotate_left', 'array_rotate_right', 'array_shift_left', 'array_shift_right', 'array_slice',
                    'array_sort_asc', 'array_sort_desc', 'array_split', 'array_strcat', 'array_sum',
                    'set_difference', 'set_has_element', 'set_intersect', 'set_union',
                    'strcat', 'strcat_array', 'strcat_delim', 'strcmp', 'string_size', 'strlen', 'strrep', 'substring',
                    'split', 'trim', 'trim_end', 'trim_start', 'replace', 'replace_regex', 'replace_string', 'replace_strings',
                    'reverse', 'translate', 'url_decode', 'url_encode', 'url_encode_component',
                    'base64_decode_toarray', 'base64_decode_toguid', 'base64_decode_tostring', 'base64_encode_fromguid', 'base64_encode_tostring',
                    'zlib_compress_to_base64_string', 'zlib_decompress_from_base64_string', 'gzip_compress_to_base64_string', 'gzip_decompress_from_base64_string',
                    'extract', 'extract_all', 'extractall', 'extract_json', 'extractjson',
                    'parse_command_line', 'parse_csv', 'parse_ipv4', 'parse_ipv4_mask', 'parse_ipv6', 'parse_ipv6_mask',
                    'parse_json', 'parsejson', 'parse_path', 'parse_url', 'parse_urlquery', 'parse_user_agent', 'parse_version', 'parse_xml',
                    'dynamic_to_json', 'format_bytes', 'format_datetime', 'format_ipv4', 'format_ipv4_mask', 'format_timespan',
                    'datetime_add', 'datetime_diff', 'datetime_local_to_utc', 'datetime_part', 'datetime_utc_to_local',
                    'dayofmonth', 'dayofweek', 'dayofyear', 'getmonth', 'getyear', 'hourofday', 'monthofyear', 'weekofyear', 'week_of_year',
                    'make_datetime', 'make_timespan', 'unixtime_microseconds_todatetime', 'unixtime_milliseconds_todatetime',
                    'unixtime_nanoseconds_todatetime', 'unixtime_seconds_todatetime', 'ingestion_time', 'cursor_after', 'cursor_before_or_at', 'current_cursor',
                    'ipv4_compare', 'ipv4_is_in_any_range', 'ipv4_is_in_range', 'ipv4_is_match', 'ipv4_is_private', 'ipv4_lookup',
                    'ipv4_netmask_suffix', 'ipv6_compare', 'ipv6_is_in_any_range', 'ipv6_is_in_range', 'ipv6_is_match',
                    'geo_distance_2points', 'geo_info_from_ip_address', 'geo_point_in_circle', 'geo_point_in_polygon', 'geo_point_to_geohash', 'geo_point_to_s2cell', 'geo_point_to_h3cell',
                    'indexof', 'indexof_regex', 'next', 'prev', 'row_cumsum', 'row_number', 'row_rank_dense', 'row_rank_min', 'row_window_session',
                    'pi', 'pow', 'radians', 'rand', 'round', 'sign', 'sin', 'sqrt', 'tan',
                    'series_abs', 'series_acos', 'series_add', 'series_asin', 'series_atan', 'series_ceiling', 'series_cos',
                    'series_decompose', 'series_decompose_anomalies', 'series_decompose_forecast', 'series_divide', 'series_equals',
                    'series_exp', 'series_fill_backward', 'series_fill_const', 'series_fill_forward', 'series_fill_linear',
                    'series_fir', 'series_fit_2lines', 'series_fit_2lines_dynamic', 'series_fit_line', 'series_fit_line_dynamic',
                    'series_fit_poly', 'series_greater', 'series_greater_equals', 'series_iir', 'series_less', 'series_less_equals',
                    'series_multiply', 'series_not_equals', 'series_outliers', 'series_pearson_correlation', 'series_periods_detect',
                    'series_periods_validate', 'series_pow', 'series_seasonal', 'series_sign', 'series_sin', 'series_stats',
                    'series_stats_dynamic', 'series_subtract', 'series_tan',
                    'column_ifexists', 'columnifexists', 'gettype', 'typeof', 'bool', 'int', 'long', 'real', 'double', 'decimal', 'string', 'guid', 'new_guid',
                    'autocluster', 'basket', 'diffpatterns', 'narrow', 'pivot', 'rolling_percentile', 'sql_request', 'cosmosdb_sql_request',
                    'true', 'false', 'null', 'by', 'from', 'to', 'on', 'with', 'as', 'asc', 'desc', 'step', 'default', 'kind', 'in'
                )
                $statementPrefixes = @(
                    'let', 'set', 'alias', 'declare', 'pattern', 'restrict', 'access',
                    'find', 'search', 'fork', 'facet', 'evaluate', 'consume', 'as',
                    'where', 'project', 'project-away', 'project-keep', 'project-rename', 'project-reorder',
                    'extend', 'summarize', 'order', 'sort', 'top', 'take', 'limit', 'distinct', 'count', 'render',
                    'mv-expand', 'mvexpand', 'mv-apply', 'mvapply', 'parse', 'parse-where', 'parse-kv',
                    'make-series', 'lookup', 'join', 'union', 'invoke', 'partition', 'serialize',
                    'sample', 'sample-distinct', 'scan', 'reduce', 'top-nested', 'top-hitters', 'getschema'
                )
                $calls = [System.Collections.Generic.List[string]]::new()
                $bare = [System.Collections.Generic.List[string]]::new()
                foreach ($m in [regex]::Matches($noComments, $tableCallPat)) {
                    if ($validSpans.Contains("$($m.Index):$($m.Index + $m.Length)")) {
                        $unq = (ConvertFrom-KqlQuotedString $m.Groups[1].Value).Trim()
                        if (-not [string]::IsNullOrWhiteSpace($unq)) { $bare.Add($unq) }
                    }
                }
                foreach ($m in [regex]::Matches($noComments, $tableAnyCallPat)) {
                    if (Test-KqlUnionWithsourceBinding -text $noComments -start $m.Index) { continue }
                    $inStr = $false
                    foreach ($sm in $strMatches) {
                        if ($sm.Index -le $m.Index -and ($sm.Index + $sm.Length) -gt $m.Index) {
                            $inStr = $true
                            break
                        }
                    }
                    if (-not $inStr -and -not $validSpanStarts.Contains($m.Index)) {
                        $calls.Add('{__unsupported_table_indirection__}')
                    }
                }
                foreach ($m in [regex]::Matches($noComments, $bracketPat)) {
                    if (-not $validSpans.Contains("$($m.Index):$($m.Index + $m.Length)")) { continue }
                    $unq = (ConvertFrom-KqlQuotedString $m.Groups[1].Value).Trim()
                    if ([string]::IsNullOrWhiteSpace($unq)) { continue }
                    $before = $noComments.Substring(0, $m.Index)
                    $after = $noComments.Substring($m.Index + $m.Length)
                    if ([regex]::IsMatch($before, '(?i)\bexternal_?data\s*\([^;|\r\n]*\z')) { continue }
                    $openParensBefore = [regex]::Match($before, '(\(\s*(?:\(\s*)*)\z')
                    $closeParensAfter = [regex]::Match($after, '\A((?:\s*\))*)\s*(?:\*/\s*)?\|')
                    $isUnclosedSubqueryPipe = $openParensBefore.Success -and $closeParensAfter.Success -and (([regex]::Matches($openParensBefore.Groups[1].Value, '\(')).Count -gt ([regex]::Matches($closeParensAfter.Groups[1].Value, '\)')).Count)
                    if ([regex]::IsMatch($after, '\A\s*\(')) {
                        $calls.Add($unq)
                        if ([regex]::IsMatch($before, '(?:[)\]}]|\.[A-Za-z_]\w*)\s*\z')) {
                            $calls.Add('{__unsupported_escaped_call_context__}')
                        }
                    }
                    elseif (-not [regex]::IsMatch($before, '(?:[)\]}]|\.[A-Za-z_]\w*)\s*\z') -and (
                        ([regex]::IsMatch($before, '(?i)(?:^|[;{]|/\*|\*/|\bmaterialize\s*\(|\btoscalar\s*\(|\b(?:join|lookup|union)\b(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*)(?:\s*\()*\s*\z') -and [regex]::IsMatch($after, '\A(?:\s*\))*\s*(?:\*/\s*)?\|')) -or
                        $isUnclosedSubqueryPipe -or
                        [regex]::IsMatch($before, '\binvoke\s*\z') -or
                        ([regex]::IsMatch($before, '\blet\s+[A-Za-z_]\w*\s*=(?:\s*\()*\s*\z') -and [regex]::IsMatch($after, '\A(?:\s*\))*\s*[;|]')) -or
                        ([regex]::IsMatch($before, '\blet\s+[A-Za-z_]\w*\s*=\s*(?:view\s*)?\([^)]*\)\s*\{(?:\s*\()*\s*\z') -and [regex]::IsMatch($after, '\A(?:\s*\))*\s*[;|}]')) -or
                        ([regex]::IsMatch($before, '\bview\s*\([^)]*\)\s*\{(?:\s*\()*\s*\z') -and [regex]::IsMatch($after, '\A(?:\s*\))*\s*[;|}]')) -or
                        ([regex]::IsMatch($before, '(?i)\bpartition\b(?:\s+hint\.[\w.]+\s*=\s*[\w.*-]+)*\s+by\s+[A-Za-z_]\w*\s*\{(?:\s*\()*\s*\z') -and [regex]::IsMatch($after, '\A(?:\s*\))*\s*[;|}]')) -or
                        ([regex]::IsMatch($before, '(?i)\bfork\b(?:\s+[A-Za-z_]\w*\s*=)?\s*\((?:\s*\()*\s*\z') -and [regex]::IsMatch($after, '\A(?:\s*\))*\s*[|)]')) -or
                        ([regex]::IsMatch($before, '(?i)\b(?:toscalar|materialize)\s*\((?:\s*\()*\s*\z') -and [regex]::IsMatch($after, '\A(?:\s*\))*\s*[|)]')) -or
                        ([regex]::IsMatch($before, '\b(?:join|lookup|union)\b(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*(?:\s*\()*\s*\z') -and -not [regex]::IsMatch($after, '\A\s*=')) -or
                        [regex]::IsMatch($before, '\bunion\b[^;|]*,\s*(?:\(\s*)*\z') -or
                        [regex]::IsMatch($before, '(?i)\b(?:find|search)\b(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*\s+in\s*\([^)]*\z'))) {
                        $bare.Add($unq)
                    }
                }
                $codeNoFlags = [regex]::Replace($code, '\b(?:union|join|lookup)\b(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)+', {
                    param($m) [regex]::Replace($m.Value, '\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+', ' ')
                })
                $codeNoPartitionHeader = [regex]::Replace($codeNoFlags, '(?i)\bpartition\b(?:\s+hint\.[\w.]+\s*=\s*[\w.*-]+)*\s+by\s+[A-Za-z_]\w*\s*(?=[({])', 'partition ')
                foreach ($match in [regex]::Matches($codeNoPartitionHeader, '(?<![.\w])([A-Za-z_]\w*)\s*\(|\binvoke\s+([A-Za-z_]\w*)')) {
                    foreach ($group in $match.Groups | Select-Object -Skip 1) {
                        if ($group.Success) { $calls.Add($group.Value) }
                    }
                }
                foreach ($match in [regex]::Matches($codeWithTokens, "($tokPat)\s*\(|(?i)(?:^|[;{]|/\*|\*/|\bmaterialize\s*\(|\btoscalar\s*\(|\b(?:join|lookup|union)\b(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*)(?:\s*\()*\s*($tokPat)(?:\s*\))*\s*(?:\*/\s*)?(?=\|)|\(\s*($tokPat)\s*(?:\*/\s*)?(?=\|)|\binvoke\s+($tokPat)|\blet\s+[A-Za-z_]\w*\s*=(?:\s*\()*\s*($tokPat)(?:\s*\))*\s*(?=[;|(])|\blet\s+[A-Za-z_]\w*\s*=\s*(?:view\s*)?\([^)]*\)\s*\{(?:\s*\()*\s*($tokPat)(?:\s*\))*\s*(?=[;|(\}])|\bview\s*\([^)]*\)\s*\{(?:\s*\()*\s*($tokPat)(?:\s*\))*\s*(?=[;|(\}])|\bpartition\b(?:\s+hint\.[\w.]+\s*=\s*[\w.*-]+)*\s+by\s+[A-Za-z_]\w*\s*\{(?:\s*\()*\s*($tokPat)(?:\s*\))*\s*(?=[;|(\}])|\bfork\b(?:\s+[A-Za-z_]\w*\s*=)?\s*\((?:\s*\()*\s*($tokPat)(?:\s*\))*\s*(?=[|)\(])|\b(?:toscalar|materialize|table|totable)\s*\((?:\s*\()*\s*($tokPat)(?:\s*\))*\s*(?=[|)\(,])")) {
                    $scalarGranularity = [regex]::Match($codeWithTokens.Substring($match.Index), "\A(?i)let\s+gran\s*=\s*($tokPat)\s*;")
                    if ($scalarGranularity.Success -and $scalarGranularity.Groups[1].Value -ieq '{Granularity}' -and
                        @($match.Groups | Where-Object { $_.Success -and $_.Value -ceq $scalarGranularity.Groups[1].Value }).Count -gt 0 -and
                        [regex]::IsMatch($codeWithTokens, '(?is)\bmake-series\b.*?\bstep\s+gran\b|\bbin\s*\([^)]*,\s*gran\s*\)')) { continue }
                    foreach ($group in $match.Groups | Select-Object -Skip 1) {
                        if ($group.Success -and $group.Value -match '[A-Za-z0-9_]') { $calls.Add($group.Value) }
                    }
                }
                foreach ($m in [regex]::Matches($codeWithTokens, "(\(\s*(?:\(\s*)*)($tokPat)((?:\s*\))*)\s*(?:\*/\s*)?(?=\|)")) {
                    $nOpen = ([regex]::Matches($m.Groups[1].Value, '\(')).Count
                    $nClose = ([regex]::Matches($m.Groups[3].Value, '\)')).Count
                    if ($nOpen -gt $nClose -and $m.Groups[2].Value -match '[A-Za-z0-9_]') {
                        $calls.Add($m.Groups[2].Value)
                    }
                }
                foreach ($op in [regex]::Matches($codeWithTokens, '\b(?:union|join|lookup)\b')) {
                    $pos = $op.Index + $op.Length
                    $flags = [regex]::Match($codeWithTokens.Substring($pos), '\A(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*')
                    $pos += $flags.Length
                    $tokTarget = [regex]::Match($codeWithTokens.Substring($pos), "\A(?:\s*\()*\s*($tokPat)")
                    if ($tokTarget.Success -and $tokTarget.Groups[1].Value -match '[A-Za-z0-9_]') { $calls.Add($tokTarget.Groups[1].Value) }
                }
                foreach ($op in [regex]::Matches($codeWithTokens, '(?i)\b(?:find|search)\b(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*\s+in\s*\(([^)]*)\)')) {
                    foreach ($tm in [regex]::Matches($op.Groups[1].Value, $tokPat)) {
                        if ($tm.Value -match '[A-Za-z0-9_]') { $calls.Add($tm.Value) }
                    }
                }
                foreach ($match in [regex]::Matches($codeNoFlags, '(?i)(?:^|[;{]|/\*|\*/|\bmaterialize\s*\(|\btoscalar\s*\(|\b(?:join|lookup|union)\b)(?:\s*\()*\s*([A-Za-z_]\w*)(?:\s*\))*\s*(?:\*/\s*)?(?=\|)|\(\s*([A-Za-z_]\w*)\s*(?:\*/\s*)?(?=\|)|\blet\s+[A-Za-z_]\w*\s*=(?:\s*\()*\s*([A-Za-z_]\w*)(?:\s*\))*\s*(?=[;|])|\blet\s+[A-Za-z_]\w*\s*=\s*(?:view\s*)?\([^)]*\)\s*\{(?:\s*\()*\s*([A-Za-z_]\w*)(?:\s*\))*\s*(?=[;|}])|\bview\s*\([^)]*\)\s*\{(?:\s*\()*\s*([A-Za-z_]\w*)(?:\s*\))*\s*(?=[;|}])|\bpartition\b(?:\s+hint\.[\w.]+\s*=\s*[\w.*-]+)*\s+by\s+[A-Za-z_]\w*\s*\{(?:\s*\()*\s*([A-Za-z_]\w*)(?:\s*\))*\s*(?=[;|}])|\b(?:toscalar|materialize)\s*\((?:\s*\()*\s*([A-Za-z_]\w*)(?:\s*\))*\s*(?=[|)])')) {
                    foreach ($group in $match.Groups | Select-Object -Skip 1) {
                        if ($group.Success) { $bare.Add($group.Value) }
                    }
                }
                foreach ($m in [regex]::Matches($codeNoFlags, '(?i)\bfork\b([^;|]*)')) {
                    foreach ($bm in [regex]::Matches($m.Groups[1].Value, '(?:[A-Za-z_]\w*\s*=\s*)?\((?:\s*\()*\s*([A-Za-z_]\w*)(?:\s*\))*\s*(?=[|)])')) {
                        $bare.Add($bm.Groups[1].Value)
                    }
                }
                foreach ($m in [regex]::Matches($codeNoFlags, '(\(\s*(?:\(\s*)*)([A-Za-z_]\w*)((?:\s*\))*)\s*(?:\*/\s*)?(?=\|)')) {
                    $nOpen = ([regex]::Matches($m.Groups[1].Value, '\(')).Count
                    $nClose = ([regex]::Matches($m.Groups[3].Value, '\)')).Count
                    if ($nOpen -gt $nClose) {
                        $bare.Add($m.Groups[2].Value)
                    }
                }
                foreach ($op in [regex]::Matches($code, '(?i)\b(?:find|search)\b(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*\s+in\s*\(([^)]*)\)')) {
                    foreach ($im in [regex]::Matches($op.Groups[1].Value, '(?<![.\w])([A-Za-z_]\w*)\b(?!\s*\()')) {
                        $bare.Add($im.Groups[1].Value)
                    }
                }
                foreach ($op in [regex]::Matches($code, '\b(?:union|join|lookup)\b')) {
                    $pos = $op.Index + $op.Length
                    $flags = [regex]::Match($code.Substring($pos), '\A(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*')
                    $pos += $flags.Length
                    $tail = $code.Substring($pos)
                    $callTarget = [regex]::Match($tail, '\A(?:\s*\()*\s*([A-Za-z_]\w*)\s*\(')
                    if ($callTarget.Success) {
                        $calls.Add($callTarget.Groups[1].Value)
                    }
                    elseif ($op.Value -cne 'union') {
                        $bareTarget = [regex]::Match($tail, '\A(?:\s*\()*\s*([A-Za-z_]\w*)\b(?!\s*[\(=.])')
                        if ($bareTarget.Success) { $bare.Add($bareTarget.Groups[1].Value) }
                    }
                }
                foreach ($union in [regex]::Matches($code, '\bunion\b')) {
                    $pos = $union.Index + $union.Length
                    $flags = [regex]::Match($code.Substring($pos), '\A(?:\s+[A-Za-z_][\w.]*\s*=\s*[\w.*-]+)*')
                    $pos += $flags.Length
                    $depth = 0
                    $operand = $true
                    for ($i = $pos; $i -lt $code.Length; $i++) {
                        $ch = $code[$i]
                        if ($operand -and -not [char]::IsWhiteSpace($ch)) {
                            $src = [regex]::Match($code.Substring($i), '\A(?:\(\s*)*([A-Za-z_]\w*)\s*(\()?(\s*[=.])?')
                            if ($src.Success -and -not $src.Groups[3].Success) {
                                if ($src.Groups[2].Success) { $calls.Add($src.Groups[1].Value) }
                                else { $bare.Add($src.Groups[1].Value) }
                            }
                            $operand = $false
                        }
                        if ($depth -eq 0 -and ($ch -eq '|' -or $ch -eq ';')) { break }
                        if ($ch -eq '(' -or $ch -eq '[' -or $ch -eq '{') { $depth++ }
                        elseif ($ch -eq ')' -or $ch -eq ']' -or $ch -eq '}') {
                            if ($depth -eq 0) { break }
                            $depth--
                        }
                        elseif ($ch -eq ',' -and $depth -eq 0) { $operand = $true }
                    }
                }
                foreach ($name in $calls) {
                    if ($name -cnotin $builtins -and $name -cnotin $statementPrefixes -and $name -cnotin $locals) { $name }
                }
                $knownTables = Get-DefenderWorkbookKnownCatalogTables
                foreach ($name in $bare) {
                    if ($name -cin $builtins -or $name -cin $statementPrefixes -or $name -cin $locals) { continue }
                    $isKnownFunc = $null -ne $KnownFunctionAliases -and $KnownFunctionAliases.Contains($name)
                    if (-not $isKnownFunc -and ($knownTables.Contains($name) -or
                        ($null -ne $AllowedBareTables -and $AllowedBareTables.Contains($name)))) {
                        continue
                    }
                    $name
                }
            }
            else {
                Get-DefenderWorkbookImplicitFunctions -Value $property.Value `
                    -AllowedBareTables $AllowedBareTables -KnownFunctionAliases $KnownFunctionAliases `
                    -ExcludedQueryPaths $ExcludedQueryPaths -Path $childPath
            }
        }
    }
    elseif ($Value -is [array]) {
        for ($i = 0; $i -lt $Value.Count; $i++) {
            Get-DefenderWorkbookImplicitFunctions -Value $Value[$i] `
                -AllowedBareTables $AllowedBareTables -KnownFunctionAliases $KnownFunctionAliases `
                -ExcludedQueryPaths $ExcludedQueryPaths -Path "$Path/$i"
        }
    }
}

function Get-DefenderWorkbookParserDependencies {
    param(
        [psobject]$Document, [psobject]$ContentToImport, [psobject]$Template,
        [string]$SolutionRoot, [string]$SolutionName
    )

    $sourceNotebook = Assert-DefenderWorkbookDocument -Document $Document -SolutionRoot $SolutionRoot `
        -SolutionName $SolutionName -ContentPath 'prerequisite scan' -PassThruSource
    $provenance = $Document.contentProvenance
    if ($provenance.origin -ceq 'native-xdr') {
        # The shared native validator rejects functions and non-native tables;
        # native imports have no savedSearch/parser deployment prerequisites.
        return
    }
    $declared = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    $property = $provenance.PSObject.Properties['requiredWorkspaceFunctions']
    if ($null -ne $property -and $property.Value -isnot [array]) {
        throw 'Defender Workbook requiredWorkspaceFunctions must be an array.'
    }
    $records = if ($null -ne $property) { @($property.Value) } else { @() }
    foreach ($record in $records) {
        if ($record -isnot [pscustomobject] -or @($record.PSObject.Properties).Count -ne 3 -or
            @($record.PSObject.Properties.Name | Where-Object {
                $_ -cnotin @('functionAlias', 'sourcePath', 'sourceSha256')
            }).Count -gt 0 -or
            $record.functionAlias -isnot [string] -or $record.functionAlias -cnotmatch '\A[A-Za-z_][A-Za-z0-9_]*\z' -or
            $record.sourcePath -isnot [string] -or $record.sourcePath -cnotmatch '\A(?:Parsers|Workspace Functions)/.+\.yaml\z' -or
            $record.sourceSha256 -isnot [string] -or $record.sourceSha256 -cnotmatch '\A[0-9a-f]{64}\z' -or
            -not $declared.Add($record.functionAlias)) {
            throw 'Defender Workbook has malformed or duplicate requiredWorkspaceFunctions.'
        }
    }
    $referenced = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($query in $provenance.conversion.queries) {
        foreach ($container in @($query, $query.contract, $query.conversion)) {
            if ($null -eq $container) { continue }
            $references = $container.PSObject.Properties['workspaceFunctions']
            if ($null -eq $references) { continue }
            if ($references.Value -isnot [array]) { throw 'Query workspaceFunctions must be an array.' }
            foreach ($alias in $references.Value) {
                if ($alias -isnot [string] -or $alias -cnotmatch '\A[A-Za-z_][A-Za-z0-9_]*\z') {
                    throw 'Query workspaceFunctions contains an invalid alias.'
                }
                [void]$referenced.Add($alias)
            }
        }
    }
    if ($provenance.format -ceq 'public-workbook-v1') {
        # Python validated exact current query aliases and hash-bound local proof
        # (or an explicitly requested public Git reproduction) above.
        foreach ($alias in $declared) { [void]$referenced.Add($alias) }
    }
    if (-not $declared.SetEquals($referenced)) {
        throw 'Defender Workbook requiredWorkspaceFunctions must exactly cover reviewed query workspaceFunctions.'
    }
    $knownFunctionAliases = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($item in $declared) { [void]$knownFunctionAliases.Add($item) }
    foreach ($res in @($Template.resources)) {
        if ($null -ne $res -and $res.type -ieq 'Microsoft.OperationalInsights/workspaces/savedSearches' -and
            $null -ne $res.properties -and $res.properties.functionAlias -is [string] -and
            -not [string]::IsNullOrWhiteSpace($res.properties.functionAlias)) {
            [void]$knownFunctionAliases.Add($res.properties.functionAlias)
        }
    }
    foreach ($folderName in @('Parsers', 'Workspace Functions')) {
        $folderPath = Join-Path (Join-Path $SolutionRoot $SolutionName) $folderName
        if (Test-Path -LiteralPath $folderPath -PathType Container) {
            foreach ($file in Get-ChildItem -LiteralPath $folderPath -Filter '*.yaml' -File -Recurse) {
                $rawYaml = Get-Content -LiteralPath $file.FullName -Raw -ErrorAction SilentlyContinue
                if ($null -ne $rawYaml) {
                    foreach ($m in [regex]::Matches($rawYaml, '(?m)^\s*Function(?:Alias|Name)\s*:\s*[''"]?([A-Za-z_][A-Za-z0-9_]*)[''"]?\s*$')) {
                        [void]$knownFunctionAliases.Add($m.Groups[1].Value)
                    }
                }
            }
        }
    }
    $allowedBareTables = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($depField in @('requiredWorkloads', 'requiredDataConnectors')) {
        $depProp = $provenance.PSObject.Properties[$depField]
        if ($null -ne $depProp -and $depProp.Value -is [array]) {
            foreach ($entry in $depProp.Value) {
                if ($null -ne $entry -and $entry.dataTypes -is [array]) {
                    foreach ($dt in $entry.dataTypes) {
                        if ($dt -is [string] -and -not $knownFunctionAliases.Contains($dt)) {
                            [void]$allowedBareTables.Add($dt)
                        }
                    }
                }
            }
        }
    }
    foreach ($query in $provenance.conversion.queries) {
        foreach ($container in @($query, $query.contract, $query.conversion)) {
            if ($null -eq $container) { continue }
            $rtProp = $container.PSObject.Properties['resolvedTables']
            if ($null -ne $rtProp -and $rtProp.Value -is [array]) {
                foreach ($dt in $rtProp.Value) {
                    if ($dt -is [string] -and -not $knownFunctionAliases.Contains($dt)) {
                        [void]$allowedBareTables.Add($dt)
                    }
                }
            }
        }
    }
    $sourceAllowedBareTables = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    if ($null -ne $provenance.PSObject.Properties['authoredReview']) {
        # The shared adapter has checked these against the reconstructed
        # baseline and current KQL, including exact inherited hybrid lineage.
        foreach ($query in $provenance.authoredReview.queries) {
            foreach ($table in $query.tables) { [void]$allowedBareTables.Add($table) }
        }
    }
    foreach ($item in $allowedBareTables) { [void]$sourceAllowedBareTables.Add($item) }
    $catalogPath = Join-Path $PSScriptRoot '../../SentinelToXDRMigration/solution_manager/migration/_workbook_core/data/mapping_catalog.json'
    if (-not (Test-Path -LiteralPath $catalogPath -PathType Leaf)) {
        $catalogPath = Join-Path $PSScriptRoot '../../SentinelToXDRMigration/sentinel_xdr_migration/_workbook_core/data/mapping_catalog.json'
    }
    if (Test-Path -LiteralPath $catalogPath -PathType Leaf) {
        $catalogJson = Get-Content -LiteralPath $catalogPath -Raw | ConvertFrom-Json
        if ($null -ne $catalogJson.tables) {
            foreach ($prop in $catalogJson.tables.PSObject.Properties) {
                $targetTable = $prop.Value.ahTable
                if ($targetTable -is [string] -and $allowedBareTables.Contains($targetTable) -and
                    -not $knownFunctionAliases.Contains($prop.Name)) {
                    [void]$sourceAllowedBareTables.Add($prop.Name)
                }
            }
        }
    }
    if (-not $knownFunctionAliases.Contains('SourceTable')) {
        [void]$sourceAllowedBareTables.Add('SourceTable')
    }
    $excludedQueryPaths = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($query in $provenance.conversion.queries) {
        if ($query.status -ceq 'removed-scope-helper') { [void]$excludedQueryPaths.Add($query.sourcePath) }
    }
    foreach ($alias in @(Get-DefenderWorkbookImplicitFunctions -Value $sourceNotebook.items `
                -AllowedBareTables $sourceAllowedBareTables -KnownFunctionAliases $knownFunctionAliases `
                -ExcludedQueryPaths $excludedQueryPaths -Path '/items') +
            @(Get-DefenderWorkbookImplicitFunctions -Value $Document.items `
                -AllowedBareTables $allowedBareTables -KnownFunctionAliases $knownFunctionAliases)) {
        # Built-in Sentinel ASIM unifying parsers (_ASim_*, _Im_*) ship with the workspace; mirrors
        # is_standard_builtin_asim_parser in solution_manager/migration/_workbook_core/workbook.py.
        if ($alias -imatch '\A_(?:asim|im)_(?!test\z)[a-z0-9_]+\z') { continue }
        if (-not $referenced.Contains($alias)) {
            throw "Defender Workbook has an unreviewed implicit workspace function '$alias'."
        }
    }
    $dependencies = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    foreach ($record in $records) {
        $resolved = Resolve-SolutionContentPath -SolutionRoot $SolutionRoot -SolutionName $SolutionName `
            -ContentPath $record.sourcePath -RequireFile
        if ($resolved.RelativePath -cne $record.sourcePath -or
            (Get-FileHash -LiteralPath $resolved.FullPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne $record.sourceSha256) {
            throw "Defender Workbook workspace function '$($record.functionAlias)' source path/hash is stale."
        }
        $selected = @(
            foreach ($field in @('Parsers', 'Data Parsers', 'Workspace Functions')) {
                foreach ($path in $ContentToImport.$field) {
                    (Resolve-SolutionContentPath -SolutionRoot $SolutionRoot -SolutionName $SolutionName `
                        -ContentPath $path -RequireFile).RelativePath
                }
            }
        )
        if (@($selected | Where-Object { $_ -ceq $record.sourcePath }).Count -ne 1) {
            throw "Defender Workbook workspace function '$($record.functionAlias)' must be selected exactly once for packaging."
        }
        $yaml = ConvertFrom-Yaml (Get-Content -LiteralPath $resolved.FullPath -Raw -ErrorAction Stop)
        $yamlAliases = @($yaml.FunctionName, $yaml.FunctionAlias) | Where-Object { $null -ne $_ }
        $effectiveAlias = if ($null -ne $yaml.FunctionAlias) { $yaml.FunctionAlias } else { $yaml.FunctionName }
        if (@($yamlAliases).Count -eq 0 -or
            @($yamlAliases | Where-Object {
                $_ -isnot [string] -or $_ -cnotmatch '\A[A-Za-z_][A-Za-z0-9_]*\z'
            }).Count -gt 0 -or $effectiveAlias -cne $record.functionAlias -or
            $yaml.FunctionQuery -isnot [string] -or [string]::IsNullOrWhiteSpace($yaml.FunctionQuery)) {
            throw "Defender Workbook workspace function '$($record.functionAlias)' YAML identity/query does not match."
        }
        $matches = @($Template.resources | Where-Object {
            $_.type -ieq 'Microsoft.OperationalInsights/workspaces/savedSearches' -and
            $_.properties.functionAlias -ceq $record.functionAlias
        })
        if ($matches.Count -ne 1) {
            throw "Defender Workbook workspace function '$($record.functionAlias)' requires exactly one emitted top-level savedSearch."
        }
        $resource = $matches[0]
        $parameters = if ($null -ne $yaml.FunctionParams) { ConvertHashTo-StringData $yaml.FunctionParams } else { '' }
        if ($null -ne $resource.PSObject.Properties['condition'] -or $null -ne $resource.PSObject.Properties['copy'] -or
            $resource.properties.query -cne $yaml.FunctionQuery -or
            [string]$resource.properties.functionParameters -cne $parameters -or
            $resource.name -isnot [string] -or [string]::IsNullOrWhiteSpace($resource.name)) {
            throw "Defender Workbook workspace function '$($record.functionAlias)' savedSearch is conditional or does not match current YAML."
        }
        $name = $resource.name
        $dependency = $null
        if ($name -cmatch "\A\[variables\('(parserObject([1-9][0-9]*))'\)\.(?:_?parserName\2|_parserId\2)\]\z") {
            $parserObjectName = $Matches[1]
            $parserIndex = $Matches[2]
            $parserObjectProperty = if ($null -ne $Template.variables) {
                $Template.variables.PSObject.Properties[$parserObjectName]
            } else { $null }
            if ($null -eq $parserObjectProperty -or $parserObjectProperty.Value -isnot [pscustomobject]) {
                throw 'Invalid savedSearch ARM name.'
            }
            $parserIdProperty = $parserObjectProperty.Value.PSObject.Properties["_parserId$parserIndex"]
            if ($null -eq $parserIdProperty -or $parserIdProperty.Value -isnot [string] -or
                [string]::IsNullOrWhiteSpace($parserIdProperty.Value)) {
                throw 'Invalid savedSearch ARM name.'
            }
            $dependency = "[variables('$parserObjectName')._parserId$parserIndex]"
        }
        elseif ($name -cmatch "\A\[variables\('parserObject") {
            throw 'Invalid savedSearch ARM name.'
        }
        elseif ($null -ne $Template.variables) {
            foreach ($prop in $Template.variables.PSObject.Properties) {
                if ($prop.Name -cmatch '\AparserObject([1-9][0-9]*)\z' -and $prop.Value -is [pscustomobject]) {
                    $idx = $Matches[1]
                    $idProp = $prop.Value.PSObject.Properties["_parserId$idx"]
                    $nameProp = $prop.Value.PSObject.Properties["_parserName$idx"]
                    $altNameProp = $prop.Value.PSObject.Properties["parserName$idx"]
                    $nameVal = if ($null -ne $nameProp) { $nameProp.Value } else { $null }
                    $altNameVal = if ($null -ne $altNameProp) { $altNameProp.Value } else { $null }
                    if ($null -ne $idProp -and $idProp.Value -is [string] -and
                        -not [string]::IsNullOrWhiteSpace($idProp.Value) -and
                        ($name -ceq $nameVal -or $name -ceq $altNameVal)) {
                        $dependency = "[variables('$($prop.Name)')._parserId$idx]"
                        break
                    }
                }
            }
        }
        if ($null -eq $dependency) {
            if ($name.StartsWith('[')) {
                if ($name.StartsWith('[[') -or -not $name.EndsWith(']')) { throw 'Invalid savedSearch ARM name.' }
                $argument = $name.Substring(1, $name.Length - 2)
            }
            else {
                if ($name.Split('/').Count -ne 2 -or @($name.Split('/') | Where-Object { -not $_ }).Count -gt 0) {
                    throw 'savedSearch name must include the workspace and resource name.'
                }
                $argument = "'" + $name.Replace("'", "''") + "'"
            }
            $dependency = "[resourceId('Microsoft.OperationalInsights/workspaces/savedSearches', $argument)]"
        }
        if ($dependencies.Add($dependency)) { $dependency }
    }
}

function Get-DefenderWorkbookParserIdentityValue {
    param([AllowNull()][object]$Value, [psobject]$Variables)
    if ($Value -isnot [string]) { return $null }
    if ($Value -cmatch "\A\[variables\('([^']+)'\)(?:\.([A-Za-z_][A-Za-z0-9_]*))?\]\z") {
        $variable = $Variables.PSObject.Properties[$Matches[1]]
        if ($null -eq $variable) { return $null }
        if ($Matches[2]) { return $variable.Value.PSObject.Properties[$Matches[2]].Value }
        return $variable.Value
    }
    return $Value
}

function ConvertTo-DefenderWorkbookArmCopy {
    param([AllowNull()][object]$Value)

    if ($Value -is [string]) {
        # ARM consumes one leading '[' from escaped literals, including authored '[['.
        if ($Value.StartsWith('[')) { return '[' + $Value }
        return $Value
    }
    if ($Value -is [pscustomobject]) {
        $result = [ordered]@{}
        foreach ($property in $Value.PSObject.Properties) {
            $result[$property.Name] = ConvertTo-DefenderWorkbookArmCopy -Value $property.Value
        }
        return [pscustomobject]$result
    }
    if ($Value -is [array]) {
        $result = @(
            foreach ($item in $Value) { ConvertTo-DefenderWorkbookArmCopy -Value $item }
        )
        return ,$result
    }
    return $Value
}

function New-DefenderWorkbookInstallDeployment {
    param([string]$DeploymentName, [psobject]$WorkbookResource, [string[]]$ParserDependencies = @())

    [pscustomobject]@{
        type = 'Microsoft.Resources/deployments'
        apiVersion = '2025-04-01'
        name = $DeploymentName
        condition = "[parameters('DeployDefenderWorkbook')]"
        dependsOn = @(
            "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/contentPackages', variables('_solutionId'))]"
        ) + @($ParserDependencies)
        properties = [pscustomobject]@{
            mode = 'Incremental'
            expressionEvaluationOptions = [pscustomobject]@{ scope = 'inner' }
            template = [pscustomobject]@{
                '$schema' = 'https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#'
                languageVersion = '2.0'
                contentVersion = '1.0.0.0'
                imports = [pscustomobject]@{
                    MicrosoftSecurity = [pscustomobject]@{ provider = 'MicrosoftSecurity'; version = '1.0.0' }
                }
                resources = [pscustomobject]@{ workbook = $WorkbookResource }
            }
        }
    }
}

function New-DefenderWorkbookRegistration {
    param(
        [string]$DeploymentName, [psobject]$InstallDeployment, [psobject]$Document,
        [psobject]$ResolvedProvenance, [string]$PackageName
    )

    $contentId = $ResolvedProvenance.contentId
    $version = $ResolvedProvenance.contentVersion
    $productId = "[concat(take(variables('_solutionId'),50),'-','dwb','-', uniqueString(concat(variables('_solutionId'),'-','DefenderWorkbook','-','$contentId','-','$version')))]"
    $fullProvenance = $ResolvedProvenance | ConvertTo-Json -Depth 100 | ConvertFrom-Json
    $fullProvenance | Add-Member -NotePropertyName requiredWorkloads -NotePropertyValue @($Document.contentProvenance.requiredWorkloads)
    $fullProvenance | Add-Member -NotePropertyName requiredDataConnectors -NotePropertyValue @($Document.contentProvenance.requiredDataConnectors)
    $functions = if ($null -ne $Document.contentProvenance.PSObject.Properties['requiredWorkspaceFunctions']) {
        @($Document.contentProvenance.requiredWorkspaceFunctions)
    } else { @() }
    $fullProvenance | Add-Member -NotePropertyName requiredWorkspaceFunctions -NotePropertyValue @($functions)
    [pscustomobject]@{
        type = 'Microsoft.OperationalInsights/workspaces/providers/contentTemplates'
        apiVersion = '2023-04-01-preview'
        name = "[concat(parameters('workspace'),'/Microsoft.SecurityInsights/',concat(parameters('workspace'),'-dwb-',uniqueString('$contentId')))]"
        location = "[parameters('workspace-location')]"
        condition = "[parameters('DeployDefenderWorkbook')]"
        dependsOn = @(
            "[resourceId('Microsoft.Resources/deployments', '$DeploymentName')]",
            "[extensionResourceId(resourceId('Microsoft.OperationalInsights/workspaces', parameters('workspace')), 'Microsoft.SecurityInsights/contentPackages', variables('_solutionId'))]"
        )
        properties = [pscustomobject]@{
            description = "Defender Workbook: $($Document.xdrMetadata.displayName)"
            mainTemplate = ($InstallDeployment.properties.template | ConvertTo-Json -Depth 100 | ConvertFrom-Json)
            packageKind = 'Solution'
            packageVersion = $ResolvedProvenance.packageVersion
            packageName = (ConvertTo-DefenderWorkbookArmCopy -Value $PackageName)
            packageId = $ResolvedProvenance.packageId
            contentSchemaVersion = '3.0.0'
            contentId = $contentId
            contentKind = 'DefenderWorkbook'
            displayName = (ConvertTo-DefenderWorkbookArmCopy -Value $Document.xdrMetadata.displayName)
            contentProductId = $productId
            id = $productId
            version = $version
            contentProvenance = (ConvertTo-DefenderWorkbookArmCopy -Value $fullProvenance)
        }
    }
}

function Add-XdrDefenderWorkbooksToSolution {
    param(
        [Parameter(Mandatory = $true)][string]$SolutionName,
        [Parameter(Mandatory = $true)][psobject]$ContentToImport,
        [Parameter(Mandatory = $true)][psobject]$Template,
        [string]$RepositoryRoot = ''
    )

    if ([string]::IsNullOrWhiteSpace($RepositoryRoot)) {
        $RepositoryRoot = git rev-parse --show-toplevel
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($RepositoryRoot)) {
            throw 'Unable to resolve the repository root while packaging Defender Workbooks.'
        }
    }
    Assert-SolutionName -SolutionName $SolutionName -SelectedSolutionName $SolutionName
    $solutionsDir = Join-Path $RepositoryRoot 'Solutions'
    $realDir = Get-ChildItem -LiteralPath $solutionsDir -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -ieq $SolutionName } | Select-Object -First 1
    if ($null -ne $realDir) {
        $SolutionName = $realDir.Name
    }
    $solutionRoot = Join-Path $RepositoryRoot "Solutions/$SolutionName"
    $selected = @(Get-DefenderWorkbookSelection -ContentToImport $ContentToImport `
        -SolutionRoot $solutionRoot -SolutionName $SolutionName)
    if ($selected.Count -eq 0) { return 0 }

    $packageId = [string]$Template.variables.solutionId
    $packageVersion = [string]$Template.variables._solutionVersion
    if ([string]::IsNullOrWhiteSpace($packageId) -or $packageId.StartsWith('[')) {
        throw 'Defender Workbook packaging requires a resolved packageId.'
    }
    Assert-DefenderWorkbookReleaseVersion -Version $packageVersion
    if ($packageVersion -cne [string]$ContentToImport.Version) {
        throw 'Defender Workbook package version must match the selected solution release.'
    }
    $contentPackages = @($Template.resources | Where-Object {
        $_.type -ieq 'Microsoft.OperationalInsights/workspaces/providers/contentPackages'
    })
    if ($contentPackages.Count -ne 1 -or $null -eq $contentPackages[0].properties) {
        throw 'Defender Workbook packaging requires exactly one contentPackages resource.'
    }
    $dependencyProperty = $contentPackages[0].properties.PSObject.Properties['dependencies']
    if ($null -ne $dependencyProperty -and
        ($null -eq $dependencyProperty.Value -or
         $null -eq $dependencyProperty.Value.PSObject.Properties['criteria'] -or
         $dependencyProperty.Value.criteria -isnot [array])) {
        throw 'Defender Workbook packaging requires valid contentPackages dependency criteria.'
    }
    $resources = @()
    $criteria = @()
    $requiredAliases = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    $identities = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($file in $selected) {
        $document = Get-Content -LiteralPath $file.FullPath -Raw -ErrorAction Stop | ConvertFrom-Json -ErrorAction Stop
        Assert-DefenderWorkbookDocument -Document $document -SolutionRoot $solutionRoot `
            -SolutionName $SolutionName -ContentPath $file.RelativePath
        $parserDependencies = @(Get-DefenderWorkbookParserDependencies -Document $document `
            -ContentToImport $ContentToImport -Template $Template -SolutionRoot $solutionRoot -SolutionName $SolutionName)
        foreach ($record in $document.contentProvenance.requiredWorkspaceFunctions) {
            [void]$requiredAliases.Add($record.functionAlias)
        }
        foreach ($id in @($document.xdrMetadata.contentId, $document.xdrMetadata.instanceId)) {
            if (-not $identities.Add($id)) { throw "Duplicate Defender Workbook content/instance identity '$id'." }
        }
        $resolved = [pscustomobject]@{
            packageId = $packageId
            packageVersion = $packageVersion
            contentId = $document.xdrMetadata.contentId
            contentVersion = $packageVersion
        }
        $notebook = $document | ConvertTo-Json -Depth 100 | ConvertFrom-Json
        $notebook.PSObject.Properties.Remove('xdrMetadata')
        $notebook.contentProvenance = $resolved
        $resource = [pscustomobject]@{
            import = 'MicrosoftSecurity'
            type = 'Microsoft.Security/workbooks@2026-06-01-preview'
            properties = [pscustomobject]@{
                id = $document.xdrMetadata.instanceId
                name = $document.xdrMetadata.displayName
                content = $notebook
            }
        }
        $resource = ConvertTo-DefenderWorkbookArmCopy -Value $resource
        $deploymentName = Get-DefenderWorkbookDeploymentName -SolutionName $SolutionName -ContentId $document.xdrMetadata.contentId
        $installation = New-DefenderWorkbookInstallDeployment -DeploymentName $deploymentName `
            -WorkbookResource $resource -ParserDependencies $parserDependencies
        $registration = New-DefenderWorkbookRegistration -DeploymentName $deploymentName `
            -InstallDeployment $installation -Document $document -ResolvedProvenance $resolved -PackageName $SolutionName
        $resources += @($installation, $registration)
        $criteria += [pscustomobject]@{
            kind = 'DefenderWorkbook'
            contentId = $resolved.contentId
            version = $resolved.contentVersion
        }
    }
    $requiredResources = @(
        foreach ($existingResource in $Template.resources) {
            $isSavedSearch = $existingResource.type -ieq 'Microsoft.OperationalInsights/workspaces/savedSearches' -and
                $requiredAliases.Contains([string]$existingResource.properties.functionAlias)
            $isParserRegistration = $existingResource.type -in @(
                'Microsoft.OperationalInsights/workspaces/providers/contentTemplates',
                'Microsoft.OperationalInsights/workspaces/providers/metadata'
            ) -and ($existingResource.properties.contentKind -eq 'Parser' -or $existingResource.properties.kind -eq 'Parser')
            $contentId = Get-DefenderWorkbookParserIdentityValue -Value $existingResource.properties.contentId -Variables $Template.variables
            if ($isSavedSearch -or ($isParserRegistration -and @($requiredAliases | Where-Object {
                        $contentId -ceq "$_-Parser"
                    }).Count -gt 0)) {
                if ($null -ne $existingResource.PSObject.Properties['condition'] -or
                    $null -ne $existingResource.PSObject.Properties['copy']) {
                    throw 'Required Defender Workbook parser infrastructure must be unconditional.'
                }
                $existingResource
            }
        }
    )
    # Keep required parser resources gated by DeployParser (defaultValue: true) so
    # Content Hub multi-workspace installation always receives the DeployParser parameter.
    $Template.resources = @($Template.resources) + @($resources)
    if ($null -eq $dependencyProperty) {
        $contentPackages[0].properties | Add-Member -NotePropertyName dependencies -NotePropertyValue (
            [pscustomobject]@{ operator = 'AND'; criteria = @() })
    }
    $existing = @($contentPackages[0].properties.dependencies.criteria | Where-Object { $_.kind -ine 'DefenderWorkbook' })
    $contentPackages[0].properties.dependencies.criteria = @($existing) + @($criteria)
    Write-Warning 'Defender Workbook install/registration is an UNVERIFIED candidate contract. Approved lab installation, registration readback, identity/provenance and repeat-install/update evidence are required; generation does not establish provider acceptance.'
    Write-Host "Added $($selected.Count) Defender Workbook(s) to the hybrid solution template."
    return $selected.Count
}
