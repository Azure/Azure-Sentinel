Param([string]$Path)
function convertYamlToObject([string] $Path) {
    if (Get-Module -ListAvailable -Name powershell-yaml) {
        Write-Verbose "Module already installed"
    }
    else {
        Write-Verbose "Installing PowerShell-YAML module"
        try {
            Install-Module powershell-yaml -AllowClobber -Force -ErrorAction Stop
            Import-Module powershell-yaml
        }
        catch {
            Write-Error $_.Exception.Message
            break
        }
    }

    try {
        # Handle both single files and directories
        if (Test-Path $Path -PathType Leaf) {
            # Single file
            $content = Get-Item $Path -ErrorAction Stop
        } else {
            # Directory - get all yaml files recursively
            $content = Get-ChildItem -Path $Path -Filter *.yaml -Recurse -ErrorAction Stop
        }
    }
    catch {
        Write-Error "Error accessing path '$Path': $($_.Exception.Message)"
        return $null
    }

    if ($content) {
        if ($content -is [System.Array]) {
            Write-Host "'$($content.count)' templates found to convert"
        } else {
            Write-Host "1 template found to convert"
        }
        $data = @()
        $content | ForEach-Object {
            $convert = $_ | Get-Content -Raw | ConvertFrom-Yaml -ErrorAction Stop
            $data += $convert
        }
        # If we only have one file, return the single object instead of array
        if ($data.Count -eq 1) {
            return $data[0]
        }
    }
    else {
        Write-Error "No YAML templates found"
        break
    }
    return $data
}

convertYamlToObject $Path