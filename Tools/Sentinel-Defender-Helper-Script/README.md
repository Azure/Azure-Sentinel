# Sentinel Transition To Defender Helper Script
This repository contains an helper script to assist Sentinel customer to adopt Sentinel in Defender. 

## Overview

**Microsoft Sentinel** is generally available in the **Microsoft Defender portal**, either with Microsoft Defender XDR, or on its own, delivering a unified experience across SIEM and XDR for faster and more accurate threat detection and response, simplified workflows, and enhanced operational efficiency.

Starting in **July 2026**, Microsoft Sentinel will be supported in the Defender portal only, and any remaining customers using the Azure portal will be automatically redirected.
If you're currently using Microsoft Sentinel in the Azure portal, **Microsoft recommends that you start planning your transition to the Defender portal now to ensure a smooth transition*** and take full advantage of the unified security operations experience offered by Microsoft Defender.

However, adopting Sentinel in Defender requires some attention to some elements such as the retention of _Defender XDR data_, _Analytics Rules_ and _Automation Rules_. 

### Defender XDR data
You can query and **correlate your Defender XDR logs** (30 days of default retention) **with third-party logs from Microsoft Sentinel without ingesting the Microsoft Defender XDR logs into Microsoft Sentinel**. If you have detection use cases that involve both Defender XDR and Microsoft Sentinel data, where you don't need to retain Defender XDR data for more than 30 days, Microsoft recommends creating custom detection rules that query data from both Microsoft Sentinel and Defender XDR tables.

### Analytics Rules
**Fusion rules will be automatically disabled after Microsoft Sentinel is onboarded to Defender**. However, you will not lose the alert correlation functionality. The alert correlation functionality previously managed by Fusion will now be handled by the Defender XDR engine, which consolidates all signals in one place. While the engines are different, they serve the same purpose. The script shows a note about this if Fusion Engine is enabled.

If you have Microsoft Sentinel analytics rules configured to trigger alerts only, with incident creation turned off, these **alerts aren't visible in the Defender portal**. You can use the _SecurityAlerts_ table to have visibilty about them.

### Automation Rules
The Defender portal uses a unique engine to correlate incidents and alerts. When onboarding your workspace to the Defender portal, **existing incident names might be changed if the correlation is applied**. For this reason, change the trigger condition from _Incident Title_ to _Analytics Rule Name_. Also the _Incident provider_ condition property is removed, as all incidents have Microsoft XDR as the incident provider (the value in the _ProviderName_ field).

## The script
To help make the transition as smooth as possible, the **_Sentinel Transition To Defender Helper_** PowerShell script was developed. It analyses the integration of Defender XDR data into Sentinel, the Analytics Rules, and the Automation Rules defined in Sentinel for compatibility with the Defender platform. The script calls the _Microsoft.SecurityInsights APIs_ to retrieve data of interest. The APIs are executed with **Application Context**, where the registered app has the **Sentinel Reader** role for the Log Analytics Workspace.

<div align="center">
<img src="https://github.com/mariocuomo/Sentinel-Transition-To-Defender-Helper-Script/blob/main/resources/diagram.png" width="600">
</div>

The script outputs the findings. <br>
The findings are printed to the [shell](https://github.com/mariocuomo/Sentinel-Transition-To-Defender-Helper-Script/blob/main/resources/output.png) or exported to a [PDF file](https://github.com/mariocuomo/Sentinel-Transition-To-Defender-Helper-Script/blob/main/resources/report.pdf).

``` powershell
.\SentinelTransitionHelper.ps1 -FileName "Report.pdf" -EnvironmentsFile ".\sentinelEnvironments.json"
```

## Reference
The script is developed by [Mario Cuomo](https://www.linkedin.com/in/mariocuomo/), Cloud Solution Architect at Microsoft. <br>
All the different versions of the script are available [here](https://github.com/mariocuomo/Sentinel-Transition-To-Defender-Helper-Script/tree/main)





