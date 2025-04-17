# SqsPolicyHelper.ps1

# Dictionary: PS version-specific JSON formatting
$JsonSettingsByVersion = @{
    Legacy = @{
        CompareDepth = 5
        FullDepth    = 16
        Compress     = $false
    }
    Modern = @{
        CompareDepth = 99
        FullDepth    = 99
        Compress     = $true
    }
}

# Function to get the current JSON settings
function Get-JsonSettings {
    $version = if ($PSVersionTable.PSVersion.Major -lt 7) { "Legacy" } else { "Modern" }
    return $JsonSettingsByVersion[$version]
}

# Compare and find missing policy statements
function Get-MissingPolicyStatements {
    param (
        [array]$Required,
        [array]$Current
    )

    $settings = Get-JsonSettings
    $depth = $settings.CompareDepth
    $compress = $settings.Compress

    $currentJson = $Current | ForEach-Object {
        if ($compress) {
            $_ | ConvertTo-Json -Depth $depth -Compress
        } else {
            $_ | ConvertTo-Json -Depth $depth
        }
    }

    return $Required | Where-Object {
        $json = if ($compress) {
            $_ | ConvertTo-Json -Depth $depth -Compress
        } else {
            $_ | ConvertTo-Json -Depth $depth
        }
        $json -notin $currentJson
    }
}

# Build final SQS policy object for AWS CLI
function Build-PolicyJsonForAws {
    param (
        # [object]$Policy
		[Parameter(Mandatory = $true)]
        [object]$Policy
    )

    $settings = Get-JsonSettings
    $depth = $settings.FullDepth
    $compress = $settings.Compress

    if ($compress) {
        return (@{ Policy = ($Policy | ConvertTo-Json -Depth $depth -Compress) } | ConvertTo-Json -Depth $depth -Compress)
    } else {
        $escapedPolicy = ($Policy | ConvertTo-Json -Depth $depth -Compress).Replace('"', '\\\"')
        return ("{'Policy':'${escapedPolicy}'}").Replace("'", '\"')
    }
}
