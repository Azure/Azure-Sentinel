# ARM-TTK release 20260213 (module 0.27), commit 0ec9a41a4503e970a0ec8efb0cd08415cc172175.
$armTtkUri = "https://github.com/Azure/arm-ttk/releases/download/20260213/arm-ttk.zip"
$expectedSha256 = "2A2D21F17CC31299BA2C78CAF97DEF3C1F9F37EB3A7BAB7900CDA18C95D4C657"

$root = Split-Path -Parent $PSScriptRoot
$tmp = Join-Path $root "tmp"
$ttkZip = Join-Path $tmp "AzTemplateToolKit.zip"
$extractPath = Join-Path $tmp "arm-ttk-extract"
$modulePath = Join-Path $tmp "arm-ttk"
$moduleManifest = Join-Path $modulePath "arm-ttk.psd1"

New-Item -Path $tmp -ItemType Directory -Force | Out-Null

try {
    $webRequestParameters = @{
        Uri = $armTtkUri
        OutFile = $ttkZip
    }
    if ($PSVersionTable.PSEdition -eq "Desktop") {
        $webRequestParameters.UseBasicParsing = $true
    }
    Invoke-WebRequest @webRequestParameters

    $actualSha256 = (Get-FileHash -Path $ttkZip -Algorithm SHA256).Hash
    if ($actualSha256 -ne $expectedSha256) {
        throw "ARM-TTK archive checksum mismatch. Expected $expectedSha256 but received $actualSha256."
    }

    Remove-Item -Path $extractPath -Recurse -Force -ErrorAction SilentlyContinue
    Expand-Archive -Path $ttkZip -DestinationPath $extractPath -Force

    $extractedModulePath = Join-Path (Join-Path $extractPath "arm-ttk") "arm-ttk"
    $extractedModuleManifest = Join-Path $extractedModulePath "arm-ttk.psd1"
    if (-not (Test-Path -Path $extractedModuleManifest -PathType Leaf)) {
        throw "ARM-TTK archive does not contain the expected module manifest."
    }

    Remove-Item -Path $modulePath -Recurse -Force -ErrorAction SilentlyContinue
    Move-Item -Path $extractedModulePath -Destination $modulePath
}
finally {
    Remove-Item -Path $ttkZip -Force -ErrorAction SilentlyContinue
    Remove-Item -Path $extractPath -Recurse -Force -ErrorAction SilentlyContinue
}

if (-not (Get-Command Test-AzTemplate -ErrorAction SilentlyContinue)) {
    Import-Module $moduleManifest
}
