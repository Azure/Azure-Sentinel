# Define paths
$sourceDir = "/Users/shay.n/Azure-Sentinel-Panorays/Solutions/Panorays/Package"
$zipFile = "/Users/shay.n/Azure-Sentinel-Panorays/Solutions/Panorays/PanoraysSolution.zip"

# Create the zip file containing ONLY the files inside the Package folder
# (We use Get-ChildItem to ensure we zip the content, not the parent folder itself)
Compress-Archive -Path "$sourceDir/*" -DestinationPath $zipFile -Force

Write-Host "Package created successfully at: $zipFile" -ForegroundColor Green