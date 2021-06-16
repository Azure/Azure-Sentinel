# Process - Azure Sentinel Information Model

This template deploys the following:
* vimProcessEmpty - Empty ASim Process table
* imProcess - Process Events from all normalized process events providers
* imProcessCreation - Process creation Events from all normalized process events providers
* imProcessTermination - Process termination Events from all normalized process events providers
* vimProcessEventsMicrosft365D - Process events from Microsoft Defender for Endpoints
* vimProcessEventsMicrosftSysmon1 - Process Creation Events from sysmon
* vimProcessEventsMicrosftSysmon5 - Process Termination Events from sysmon
* vimProcessEventsMicrosftWindowsEvent4688 - Process Creation Events from windows logs

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Forigin%2Fdev%2Fprocess_events%2FParsers%2FASimProcess%2FARM%2FimProcess.json)








