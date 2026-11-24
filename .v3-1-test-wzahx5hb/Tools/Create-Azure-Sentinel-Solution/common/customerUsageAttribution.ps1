function Assert-CustomerUsageTrackingId {
    param($TrackingId, [string]$Source)

    if ($TrackingId -isnot [string] -or $TrackingId.Length -gt 64 -or
        $TrackingId -cnotmatch '\Apid-[A-Za-z0-9][A-Za-z0-9_.()-]*\z') {
        throw "Invalid trackingId in '$Source'. Copy the complete pid- tracking ID from Partner Center unchanged (not a bare GUID, Partner ID, or plan ID). It must be a literal deployment name of at most 64 characters using letters, digits, hyphens, underscores, periods, or parentheses."
    }
}

function Get-AttributionRemoteJson {
    param([string]$Uri, [string]$Stage)

    try {
        # No credentials, interactive authentication, retries, or unbounded redirects.
        $timeouts = @{ TimeoutSec = 20 }
        if ((Get-Command Microsoft.PowerShell.Utility\Invoke-WebRequest).Parameters.ContainsKey('OperationTimeoutSeconds')) {
            $timeouts.OperationTimeoutSeconds = 20
        }
        $response = Invoke-WebRequest -Uri $Uri -Method Get @timeouts -MaximumRedirection 0 -ErrorAction Stop
    }
    catch {
        $status = $_.Exception.Response.StatusCode
        $classification = if ($status) { "HTTP $([int]$status)" }
            elseif ($_.Exception.ToString() -match 'Timeout|timed out|canceled') { 'timeout' }
            else { 'network/read failure' }
        # Exception text can include a protected artifact URI or its SAS query.
        throw "${Stage}: $classification"
    }
    try {
        # ConvertFrom-Json alone accepts repeated keys by keeping the last value.
        # Reject those documents rather than hiding an ambiguous offer or marker.
        $json = [System.Text.Json.JsonDocument]::Parse([string]$response.Content)
        try {
            $pending = [System.Collections.Generic.Stack[System.Text.Json.JsonElement]]::new()
            $pending.Push($json.RootElement)
            while ($pending.Count -gt 0) {
                $element = $pending.Pop()
                if ($element.ValueKind -eq [System.Text.Json.JsonValueKind]::Object) {
                    $names = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
                    foreach ($property in $element.EnumerateObject()) {
                        if (-not $names.Add($property.Name)) { throw 'Duplicate JSON property' }
                        $pending.Push($property.Value)
                    }
                }
                elseif ($element.ValueKind -eq [System.Text.Json.JsonValueKind]::Array) {
                    foreach ($item in $element.EnumerateArray()) { $pending.Push($item) }
                }
            }
        }
        finally { $json.Dispose() }
        return ConvertFrom-Json -InputObject $response.Content -AsHashtable -NoEnumerate -ErrorAction Stop
    }
    catch { throw "${Stage}: invalid JSON" }
}

function Resolve-PublishedCustomerUsageAttribution {
    param($Metadata)

    $publisher = $Metadata.publisherId
    $offer = $Metadata.offerId
    if ($publisher -isnot [string] -or [string]::IsNullOrWhiteSpace($publisher) -or
        $offer -isnot [string] -or [string]::IsNullOrWhiteSpace($offer)) {
        throw 'catalog identity: publisherId and offerId are required'
    }
    $filter = "publisherId eq '$($publisher.Replace("'", "''"))' and offerId eq '$($offer.Replace("'", "''"))'"
    $uri = 'https://catalogapi.azure.com/offers?api-version=2018-08-01-beta&$filter=' + [uri]::EscapeDataString($filter)
    $catalog = Get-AttributionRemoteJson -Uri $uri -Stage catalog
    if ($catalog -isnot [System.Collections.IDictionary] -or $catalog.items -isnot [array] -or
        $catalog.nextLink -or $catalog.nextPageLink -or $catalog.'@odata.nextLink' -or $catalog.continuationToken) {
        throw 'catalog shape: expected a complete items array'
    }
    $offers = @($catalog.items | Where-Object { $_.publisherId -ceq $publisher -and $_.offerId -ceq $offer })
    if ($offers.Count -ne 1) { throw "catalog match: expected one exact publisher/offer match, found $($offers.Count)" }
    if ($offers[0].plans -isnot [array]) { throw 'plan shape: expected a plans array' }
    $plans = @($offers[0].plans | Where-Object {
        @($_.artifacts | Where-Object { $_.type -ceq 'Template' -and $_.name -ceq 'DefaultTemplate' }).Count -gt 0
    })
    if ($plans.Count -ne 1) { throw "plan selection: expected one applicable plan, found $($plans.Count)" }
    $plan = $plans[0]
    if ($plan.planId -isnot [string] -or [string]::IsNullOrWhiteSpace($plan.planId)) {
        throw 'plan identity: missing planId'
    }
    $artifacts = @($plan.artifacts | Where-Object { $_.type -ceq 'Template' -and $_.name -ceq 'DefaultTemplate' })
    if ($artifacts.Count -ne 1) { throw "template artifact: expected one DefaultTemplate, found $($artifacts.Count)" }
    $templateUri = $null
    if ($artifacts[0].uri -isnot [string] -or
        -not [uri]::TryCreate($artifacts[0].uri, [UriKind]::Absolute, [ref]$templateUri) -or
        $templateUri.Scheme -ne 'https' -or $templateUri.UserInfo -or $templateUri.Fragment) {
        throw 'template artifact: expected one absolute HTTPS URI without embedded credentials or fragment'
    }
    $document = Get-AttributionRemoteJson -Uri $templateUri.AbsoluteUri -Stage template
    $schemaPattern = '\Ahttps?://schema\.management\.azure\.com/schemas/[0-9]{4}-[0-9]{2}-[0-9]{2}/deploymentTemplate\.json#?\z'
    $versionPattern = '\A[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\z'
    if ($document -isnot [System.Collections.IDictionary] -or
        $document.'$schema' -isnot [string] -or $document.'$schema' -notmatch $schemaPattern -or
        $document.contentVersion -isnot [string] -or $document.contentVersion -notmatch $versionPattern) {
        throw 'template shape: expected an ARM deployment template object'
    }
    if ($document.resources -is [array]) {
        $resources = @($document.resources)
    }
    elseif ($document.languageVersion -ceq '2.0' -and $document.resources -is [System.Collections.IDictionary]) {
        $resources = @($document.resources.Values)
    }
    else { throw 'template shape: expected a resources array or languageVersion 2.0 symbolic resource object' }
    if (@($resources | Where-Object { $_ -isnot [System.Collections.IDictionary] }).Count -gt 0) {
        throw 'template shape: root resources must be resource objects'
    }
    $markers = @($resources | Where-Object {
        $_.type -ieq 'Microsoft.Resources/deployments' -and $_.name -is [string] -and $_.name -clike 'pid-*'
    })
    if ($markers.Count -ne 1) { throw "template marker: expected one root pid- deployment, found $($markers.Count)" }
    $marker = $markers[0]
    Assert-CustomerUsageTrackingId -TrackingId $marker.name -Source 'published template'
    $inline = $marker.properties.template
    if ($marker.properties -isnot [System.Collections.IDictionary] -or
        $marker.properties.mode -cne 'Incremental' -or $marker.apiVersion -isnot [string] -or
        $marker.apiVersion -notmatch '\A[0-9]{4}-[0-9]{2}-[0-9]{2}(-preview)?\z' -or
        @($marker.Keys | Where-Object { $_ -notin @('type', 'apiVersion', 'name', 'properties') }).Count -gt 0 -or
        @($marker.properties.Keys | Where-Object { $_ -notin @('mode', 'template') }).Count -gt 0 -or
        $inline -isnot [System.Collections.IDictionary] -or
        @($inline.Keys | Where-Object { $_ -notin @('$schema', 'contentVersion', 'resources') }).Count -gt 0 -or
        $inline.'$schema' -isnot [string] -or $inline.'$schema' -notmatch $schemaPattern -or
        $inline.contentVersion -isnot [string] -or $inline.contentVersion -notmatch $versionPattern -or
        $inline.resources -isnot [array] -or $inline.resources.Count -ne 0) {
        throw 'template marker: not an unconditional empty inline attribution deployment (functional wrappers are not attribution)'
    }
    return [pscustomobject]@{
        TrackingId = $marker.name
        PublisherId = $publisher
        OfferId = $offer
        PlanId = $plan.planId
        # Never log a protected URI's query (including SAS credentials).
        TemplateUrl = $templateUri.GetLeftPart([UriPartial]::Path)
    }
}

function Add-CustomerUsageAttribution {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SolutionMetadataPath,
        [Parameter(Mandatory = $true)]
        [psobject]$Template,
        # Retain the existing parameter name; nested XDR content requires attribution.
        [bool]$WarnIfMissing = $false,
        [switch]$SkipAttributionLookup
    )

    # Consolidated Data metadata is not authoritative for this packaging-only setting.
    $snapshot = [System.IO.File]::ReadAllBytes($SolutionMetadataPath)
    $metadata = [System.Text.Encoding]::UTF8.GetString($snapshot).TrimStart([char]0xfeff) |
        ConvertFrom-Json -ErrorAction Stop
    $trackingId = $metadata.trackingId
    $discovered = $null
    if ($null -eq $trackingId -or ($trackingId -is [string] -and [string]::IsNullOrWhiteSpace($trackingId))) {
        if ($WarnIfMissing -or (-not $SkipAttributionLookup -and $env:SENTINEL_SKIP_ATTRIBUTION_LOOKUP -ne '1')) {
            try {
                $discovered = Resolve-PublishedCustomerUsageAttribution -Metadata $metadata
                $trackingId = $discovered.TrackingId
            }
            catch {
                if ($WarnIfMissing) {
                    throw "CUSTOMER USAGE ATTRIBUTION: Required published lookup failed [$($_.Exception.Message)]. Packaging stopped; SolutionMetadata.json is unchanged. Verify publisherId and offerId identify the correct published offer with one unambiguous plan/marker, or supply the complete trackingId from Partner Center > offer > plan > Technical configuration in '$SolutionMetadataPath' and rebuild. Attribution lookup cannot be skipped for nested XDR content."
                }
                Write-Warning "CUSTOMER USAGE ATTRIBUTION: Published lookup failed [$($_.Exception.Message)]. No attribution marker will be emitted; SolutionMetadata.json is unchanged. Supply the complete trackingId from Partner Center > offer > plan > Technical configuration and rebuild."
            }
        }
    }
    if ($null -eq $trackingId -or ($trackingId -is [string] -and [string]::IsNullOrWhiteSpace($trackingId))) {
        if ($WarnIfMissing) {
            throw "CUSTOMER USAGE ATTRIBUTION: Required trackingId is still absent or blank in '$SolutionMetadataPath'. Packaging stopped; SolutionMetadata.json is unchanged. Verify publisherId and offerId, or supply the complete trackingId from Partner Center > offer > plan > Technical configuration and rebuild. Attribution lookup cannot be skipped for nested XDR content."
        }
        return
    }

    Assert-CustomerUsageTrackingId -TrackingId $trackingId -Source $SolutionMetadataPath

    if (@($Template.resources | Where-Object {
        $_.type -eq 'Microsoft.Resources/deployments' -and $_.name -eq $trackingId
    }).Count -gt 0) {
        throw "Duplicate customer usage attribution deployment name '$trackingId'."
    }

    if ($discovered) {
        try {
            if (-not ('AttributionMetadata' -as [type])) {
                Add-Type -Path (Join-Path $PSScriptRoot 'AttributionMetadata.cs') -ErrorAction Stop
            }
            [AttributionMetadata]::Save($SolutionMetadataPath, $snapshot, $trackingId)
        }
        catch {
            throw "Customer usage attribution metadata write failed for '$SolutionMetadataPath'; no marker emitted: $($_.Exception.Message)"
        }
        Write-Host "CUSTOMER USAGE ATTRIBUTION SOURCE: anonymous public Marketplace catalog/template; publisherId=$($discovered.PublisherId); offerId=$($discovered.OfferId); planId=$($discovered.PlanId); templateURL=$($discovered.TemplateUrl); trackingId=$trackingId; updated metadata=$SolutionMetadataPath"
    }

    $Template.resources = @($Template.resources) + @([pscustomobject]@{
        type       = 'Microsoft.Resources/deployments'
        apiVersion = '2025-04-01'
        name       = $trackingId
        properties = [pscustomobject]@{
            mode     = 'Incremental'
            template = [pscustomobject]@{
                '$schema'      = 'https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#'
                contentVersion = '1.0.0.0'
                resources      = @()
            }
        }
    })
}
