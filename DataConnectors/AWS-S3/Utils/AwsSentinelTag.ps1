function Get-SentinelTagKey {
    return "Operator"
}

function Get-SentinelTagValue {
    return "Microsoft_Sentinel_Automation_Script"
}

function Get-SentinelTagInJsonFormat {
    $key = Get-SentinelTagKey
    $value = Get-SentinelTagValue
    $sentinelTag = ConvertTo-Json -InputObject @{Key = $key; Value = $value } -Depth 99 -Compress
    return $sentinelTag
} 