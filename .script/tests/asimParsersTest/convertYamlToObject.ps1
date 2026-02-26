Param([string]$Path)
function convertYamlToObject([System.IO.FileInfo] $Path) {
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