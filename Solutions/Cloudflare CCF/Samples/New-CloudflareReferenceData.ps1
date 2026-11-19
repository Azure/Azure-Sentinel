#Requires -Version 7.0
param(
    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory,

    [ValidatePattern('^[a-zA-Z0-9-]{1,48}$')]
    [string]$RunId = ("cfr-" + [datetime]::UtcNow.ToString('yyyyMMddHHmmss'))
)

$ErrorActionPreference = 'Stop'
$directory = [System.IO.Path]::GetFullPath($OutputDirectory)
[System.IO.Directory]::CreateDirectory($directory) | Out-Null
$manifestPath = Join-Path $directory "$RunId-manifest.json"
$accounts = @(
    @{ key = 'a'; nativeId = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'; ipPrefix = '198.51.100.' },
    @{ key = 'b'; nativeId = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'; ipPrefix = '203.0.113.' }
)
$datasets = @('http_requests', 'gateway_http', 'firewall_events', 'sinkhole_http_logs')
$statuses = @(200, 201, 301, 400, 403, 503)
$methods = @('GET', 'POST', 'PUT', 'HEAD', 'DELETE', 'OPTIONS')
$encoding = [System.Text.UTF8Encoding]::new($false)
$start = [datetime]::UtcNow
$expectedPaths = @($manifestPath)
foreach ($account in $accounts) {
    $expectedPaths += Join-Path $directory "$RunId-$($account.key).ndjson"
    $expectedPaths += Join-Path $directory "$RunId-$($account.key).ndjson.gz"
}
foreach ($path in $expectedPaths) {
    if (Test-Path -LiteralPath $path) {
        throw "Refusing to overwrite existing reference data: $path"
    }
}

$manifest = [ordered]@{
    runId = $RunId
    generatedAtUtc = $start.ToString('o')
    expectedTotalRecords = 48
    datasets = $datasets
    files = @()
}

foreach ($account in $accounts) {
    $records = @(
        foreach ($dataset in $datasets) {
            foreach ($index in 0..5) {
                $number = $index + 1
                $eventTime = $start.AddMinutes(-$index)
                $timestamp = $eventTime.ToString('o')
                $clientIp = "$($account.ipPrefix)$($index + 10)"
                $originIp = "192.0.2.$($index + 10)"
                $path = "/$RunId/$($account.key)/$dataset/$number"
                $url = "https://cloudflare-reference.example.com$path"
                $nativeId = "$RunId-$($account.key)-$dataset-$number"
                $userAgent = "CloudflareReference$number/1.0"
                $action = if ($statuses[$index] -lt 400) { 'allow' } else { 'block' }

                # Collector attribution is absent so the DCR must supply it.
                $record = [ordered]@{ AccountID = $account.nativeId }
                switch ($dataset) {
                    'http_requests' {
                        $record['RayID'] = $nativeId
                        $record['ClientIP'] = $clientIp
                        $record['ClientSrcPort'] = 40000 + $number
                        $record['OriginIP'] = $originIp
                        $record['OriginPort'] = 443
                        $record['ClientRequestURI'] = $path
                        $record['ClientRequestHost'] = 'cloudflare-reference.example.com'
                        $record['ClientRequestMethod'] = $methods[$index]
                        $record['ClientRequestProtocol'] = 'HTTP/2'
                        $record['ClientRequestUserAgent'] = $userAgent
                        $record['EdgeStartTimestamp'] = $timestamp
                        $record['EdgeEndTimestamp'] = $eventTime.AddMilliseconds(5).ToString('o')
                        $record['EdgeResponseStatus'] = $statuses[$index]
                        $record['SecurityAction'] = $action
                    }
                    'gateway_http' {
                        $record['RequestID'] = $nativeId
                        $record['Datetime'] = $timestamp
                        $record['SourceIP'] = $clientIp
                        $record['SourcePort'] = 40000 + $number
                        $record['DestinationIP'] = $originIp
                        $record['DestinationPort'] = 443
                        $record['URL'] = $url
                        $record['HTTPHost'] = 'cloudflare-reference.example.com'
                        $record['HTTPMethod'] = $methods[$index]
                        $record['HTTPVersion'] = 'HTTP/2'
                        $record['HTTPStatusCode'] = $statuses[$index]
                        $record['UserAgent'] = $userAgent
                        $record['Action'] = $action
                        $record['Email'] = 'sanitized@sanitized.com'
                        $record['PolicyName'] = 'Reference test policy'
                        $record['CategoryNames'] = @('Reference')
                    }
                    'firewall_events' {
                        $record['Kind'] = 'firewall'
                        $record['RayID'] = $nativeId
                        $record['Datetime'] = $timestamp
                        $record['ClientIP'] = $clientIp
                        $record['ClientSrcPort'] = 40000 + $number
                        $record['OriginIP'] = $originIp
                        $record['OriginPort'] = 443
                        $record['ClientRequestPath'] = $path
                        $record['ClientRequestHost'] = 'cloudflare-reference.example.com'
                        $record['ClientRequestMethod'] = $methods[$index]
                        $record['ClientRequestProtocol'] = 'HTTP/2'
                        $record['ClientRequestUserAgent'] = $userAgent
                        $record['EdgeResponseStatus'] = $statuses[$index]
                        $record['Action'] = $action
                        $record['Description'] = 'Reference test firewall rule'
                    }
                    'sinkhole_http_logs' {
                        $record['SinkholeID'] = "reference-sinkhole-$($account.key)"
                        $record['Timestamp'] = $timestamp
                        $record['SrcAddr'] = $clientIp
                        $record['DestAddr'] = $originIp
                        $record['URL'] = $url
                        $record['URI'] = $path
                        $record['Host'] = 'cloudflare-reference.example.com'
                        $record['Method'] = $methods[$index]
                        $record['UserAgent'] = $userAgent
                        $record['Username'] = 'reference-user'
                        $record['BodyLength'] = 0
                    }
                }
                $record
            }
        }
    )

    $ndjsonPath = Join-Path $directory "$RunId-$($account.key).ndjson"
    $gzipPath = "$ndjsonPath.gz"
    $lines = @($records | ForEach-Object { $_ | ConvertTo-Json -Compress -Depth 10 })
    $bytes = $encoding.GetBytes(($lines -join "`n") + "`n")
    [System.IO.File]::WriteAllBytes($ndjsonPath, $bytes)
    $stream = [System.IO.File]::Open($gzipPath, [System.IO.FileMode]::CreateNew)
    try {
        $gzip = [System.IO.Compression.GZipStream]::new(
            $stream, [System.IO.Compression.CompressionLevel]::Optimal, $true
        )
        try {
            $gzip.Write($bytes, 0, $bytes.Length)
        }
        finally {
            $gzip.Dispose()
        }
    }
    finally {
        $stream.Dispose()
    }

    $manifest.files += [ordered]@{
        account = $account.key
        nativeAccountId = $account.nativeId
        records = $records.Count
        recordsPerDataset = 6
        pathMarker = "/$RunId/$($account.key)/"
        blobName = "$RunId/$RunId-$($account.key).ndjson.gz"
        ndjsonFile = [System.IO.Path]::GetFileName($ndjsonPath)
        gzipFile = [System.IO.Path]::GetFileName($gzipPath)
        sha256 = (Get-FileHash -LiteralPath $gzipPath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
}

$json = $manifest | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText($manifestPath, $json, $encoding)
$json
