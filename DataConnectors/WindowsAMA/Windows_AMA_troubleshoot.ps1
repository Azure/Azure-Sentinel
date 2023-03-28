# Prompt intro
Write-Output "Statrting to run Windows AMA troubleshooting script"
Write-Output "Starting to collect data"
$Scenario = Read-Host -Prompt 'Input the scenario name you would like to investgate: 1) ForwardedEvents 2) Security 3) Application 4) Setup 5) System 6) DNS 7) All'

# Create output files set-up
Remove-Item 'C:\test_folder\' -Recurse 2> $null
Remove-Item 'C:\Draft.zip' 2> $null
md C:\test_folder\ > $null
New-Item C:\test_folder\tmp.txt > $null

"Script version: 1.0" | Out-File -FilePath C:\test_folder\tmp.txt -Append

"Date:" | Out-File -FilePath C:\test_folder\tmp.txt -Append
Get-Date | Out-File -FilePath C:\test_folder\tmp.txt -Append

# The scenario being investigated
"Scenario (Connector name):" | Out-File -FilePath C:\test_folder\tmp.txt -Append
$Scenario | Out-File -FilePath C:\test_folder\tmp.txt -Append


# Collect top consuming CPU processes
"Top consuming CPU processes:" | Out-File -FilePath C:\test_folder\tmp.txt -Append
Get-Process | Sort-Object CPU -desc | Select-Object -first 10 | Out-File -FilePath C:\test_folder\tmp.txt -Append

# Collect disk space stats 
"Disk space stats:" | Out-File -FilePath C:\test_folder\tmp.txt -Append
Get-Volume -DriveLetter C | Out-File -FilePath C:\test_folder\tmp.txt -Append


# Collect logs and agent configurations including DCR's
Copy-Item -Path "C:\WindowsAzure\Resources\" -Destination "C:\test_folder\" -Recurse
Copy-Item -Path "C:\WindowsAzure\Logs\Plugins\" -Destination "C:\test_folder\" -Recurse

# Compress all data
$compress = @{
    LiteralPath= "C:\test_folder\"
    CompressionLevel = "Fastest"
    DestinationPath = "C:\Draft.zip"
    }
    Compress-Archive @compress

# Prompt outro
Write-Output "Finished collecting data. Please supply CSS with the following file in order to continue the investigation- C:\Draft.zip"