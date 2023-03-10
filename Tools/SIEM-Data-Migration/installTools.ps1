Set-Location -Path "C:\Users\Public\Desktop"

Invoke-WebRequest -Uri https://www.nuget.org/api/v2/package/Microsoft.Azure.Kusto.Tools/6.0.1 -OutFile LightIngest.zip -UseBasicParsing

Expand-Archive -Path .\LightIngest.zip -DestinationPath LightIngest

Invoke-WebRequest -Uri https://aka.ms/downloadazcopy-v10-windows -OutFile AzCopy.zip -UseBasicParsing

Expand-Archive -Path .\AzCopy.zip -DestinationPath AzCopy

Invoke-WebRequest -Uri https://aka.ms/customlogsingestion -OutFile Send-AzMonitorCustomLogs.zip -UseBasicParsing

Expand-Archive -Path .\Send-AzMonitorCustomLogs.zip -DestinationPath Send-AzMonitorCustomLogs