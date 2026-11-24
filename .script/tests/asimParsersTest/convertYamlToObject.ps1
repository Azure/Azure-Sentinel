Param([string]$Path)
function convertYamlToObject([System.IO.FileInfo] $Path) {
    $requiredVersion = [version]"0.4.12"
    $installedModule = Get-Module -ListAvailable -Name powershell-yaml |
        Where-Object Version -eq $requiredVersion |
        Select-Object -First 1
    if ($installedModule) {
        Write-Verbose "Required PowerShell-YAML module is installed"
    }
    else {
        Write-Verbose "Installing PowerShell-YAML $requiredVersion"
        try {
            Install-Module powershell-yaml `
                -RequiredVersion $requiredVersion `
                -Scope CurrentUser `
                -AllowClobber `
                -Force `
                -ErrorAction Stop
        }
        catch {
            throw "Failed to install PowerShell-YAML ${requiredVersion}: $($_.Exception.Message)"
        }
    }
    Import-Module powershell-yaml `
        -RequiredVersion $requiredVersion `
        -Force `
        -ErrorAction Stop

    try {
        $content = Get-ChildItem -Path $Path -Filter *.yaml -Recurse -ErrorAction Stop
    }
    catch {
        Write-Error $_.Exception.Message
    }

    if ($content) {
        Write-Host "'$($content.count)' templates found to convert"
        $data = @()
        $content | ForEach-Object {
            $convert = $_ | Get-Content -Raw | ConvertFrom-Yaml -ErrorAction Stop
            $data += $convert
        }
    }
    else {
        Write-Error "No YAML templates found"
        break
    }
    return $data
}

convertYamlToObject $Path