param(
    [Parameter(Mandatory=$true)]
    [string]$Command
)

# Allowed az CLI command prefixes
$allowedPrefixes = @(
    "az account show",
    "az account get-access-token",
    "az monitor log-analytics query",
    "az monitor log-analytics workspace",
    "az deployment group create",
    "az deployment group validate",
    "az group show",
    "az resource show"
)

# Dangerous shell patterns
$dangerousPatterns = @(
    '[;&|]',
    '\$\(',
    '`',
    '>[>]?',
    '<',
    '\beval\b',
    '\brm\b',
    '\bdel\b',
    '--delete'
)

$trimmed = $Command.Trim()

# Validate the command starts with "az "
if (-not $trimmed.StartsWith("az ")) {
    Write-Error "Command must start with 'az'. Only Azure CLI commands are allowed."
    exit 1
}

# Validate against allowed prefixes
$isAllowed = $false
foreach ($prefix in $allowedPrefixes) {
    if ($trimmed.StartsWith($prefix)) {
        $isAllowed = $true
        break
    }
}
if (-not $isAllowed) {
    Write-Error "Command not allowed. Permitted commands must start with one of:`n$($allowedPrefixes | ForEach-Object { "  - $_" } | Out-String)"
    exit 1
}

# Check for dangerous patterns
if ($trimmed -match "[\r\n]") {
    Write-Error "Command must be a single line. Newline characters are not allowed."
    exit 1
}

foreach ($pattern in $dangerousPatterns) {
    if ($trimmed -match $pattern) {
        Write-Error "Command contains disallowed shell operators or patterns."
        exit 1
    }
}

# Execute the command
Invoke-Expression $trimmed
