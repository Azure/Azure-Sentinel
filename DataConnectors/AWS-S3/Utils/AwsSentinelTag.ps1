function Get-SentinelTagKey
{
    return "Operator"
}

function Get-SentinelTagValue
{
    return "Microsoft_Sentinel_Automation_Script"
}

function Get-SentinelTagInJsonFormat
{
    $key = Get-SentinelTagKey
    $value = Get-SentinelTagValue
    return  "{\""Key\"": \""$key\"", \""Value\"": \""$value\""}"
}