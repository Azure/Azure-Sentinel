Compress-Archive -Path .\DataConnectors\M365Defender-VulnerabilityManagement\functionPackage\* -DestinationPath .\DataConnectors\M365Defender-VulnerabilityManagement\functionPackage.zip -Force

az bicep build --file .\DataConnectors\M365Defender-VulnerabilityManagement\main.bicep --outfile .\DataConnectors\M365Defender-VulnerabilityManagement\azureDeploy.json