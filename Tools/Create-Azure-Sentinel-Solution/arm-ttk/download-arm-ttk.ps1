# Download and un-pack latest arm-ttk
$root = [System.IO.Path]::GetFullPath("$PSScriptRoot/..")
$tmp = "$root/tmp"
$ttkZip = "$tmp/arm-ttk.zip"
$ttkPath = "$tmp/arm-ttk"

# Setup tmp directory
New-Item -Path $tmp -ItemType Directory -Force | Out-Null

# Clean up existing files
Remove-Item $ttkPath, $ttkZip -Recurse -Force -ErrorAction SilentlyContinue

# Download from GitHub (Azure Storage has public access disabled)
try {
    Write-Output "Downloading ARM-TTK from GitHub..."
    
    # Try GitHub API for latest release, fallback to v0.26
    $url = try { 
        (Invoke-RestMethod "https://api.github.com/repos/Azure/arm-ttk/releases/latest" -ErrorAction Stop).zipball_url 
    } catch { 
        "https://github.com/Azure/arm-ttk/releases/download/0.26/arm-ttk.zip" 
    }
    
    Invoke-WebRequest -Uri $url -OutFile $ttkZip -ErrorAction Stop
    Expand-Archive -Path $ttkZip -DestinationPath $tmp -Force
    
    # Handle GitHub folder structure (zipball creates Azure-arm-ttk-<hash> or arm-ttk-master)
    $extractedFolder = Get-ChildItem -Path $tmp -Directory | Where-Object { $_.Name -like "Azure-arm-ttk-*" -or $_.Name -eq "arm-ttk-master" } | Select-Object -First 1
    
    if ($extractedFolder -and (Test-Path "$($extractedFolder.FullName)/arm-ttk")) {
        Move-Item "$($extractedFolder.FullName)/arm-ttk" $ttkPath -Force
        Remove-Item $extractedFolder.FullName -Recurse -Force -ErrorAction SilentlyContinue
    } elseif ($extractedFolder) {
        Move-Item $extractedFolder.FullName $ttkPath -Force
    }
    
    Remove-Item $ttkZip -Force -ErrorAction SilentlyContinue
    Write-Output "ARM-TTK downloaded successfully"
}
catch {
    Remove-Item $ttkZip -Force -ErrorAction SilentlyContinue
    Write-Warning "Failed to download ARM-TTK: $_"
    Write-Warning "ARM-TTK validation will be skipped. You can manually download from https://github.com/Azure/arm-ttk"
    throw
}

# Validate and import module
if (-not (Test-Path "$ttkPath/arm-ttk.psd1")) {
    Write-Warning "ARM-TTK module file not found at $ttkPath/arm-ttk.psd1"
    Write-Warning "ARM-TTK validation will be skipped. Download ARM-TTK from https://github.com/Azure/arm-ttk and place it in the expected location to enable validation."
    throw "ARM-TTK validation cannot proceed - module files missing"
}

if (-not (Get-Command Test-AzTemplate -ErrorAction SilentlyContinue)) {
    Import-Module "$ttkPath/arm-ttk.psd1" -ErrorAction Stop
    Write-Output "ARM-TTK module imported successfully"
}