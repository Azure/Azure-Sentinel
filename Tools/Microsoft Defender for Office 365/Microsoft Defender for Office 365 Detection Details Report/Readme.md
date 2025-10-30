# Microsoft Defender for Office 365 Detection Details Report – Configuration Guide 

## Contents

[Overview](#overview)<br/>
[Example View of Microsoft Defender for Office 365 (MDO) Detection Details Report](#example-view-of-microsoft-defender-for-office-365-mdo-detection-details-report)<br/>
[How to use the .pbit file for Log Analytics/Sentinel](#how-to-use-the-pbit-file-for-log-analyticssentinel)<br/>
[How to use the .pbit file for the Hunting API](#how-to-use-the-pbit-file-for-the-hunting-api)<br/>
[How to publish to Power BI online and configure scheduled auto-refresh](#how-to-publish-to-power-bi-online-and-configure-scheduled-auto-refresh)<br/>

## Overview

These templates will give you an example how to build a Microsoft Defender for Office 365 custom report using Power BI. This way you can visualize Microsoft Defender for Office 365 (MDO) data based on your organization needs. 

Sentinel/Log Analytics version:
* Requires the Defender XDR connector in Sentinel for the EmailEvents, EmailPostDeliveryEvents, EmailUrlInfo, UrlClickEvents and CloudAppEvents tables as described here: [Connect data from Microsoft Defender XDR to Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/connect-microsoft-365-defender?tabs=MDO#connect-events) or a custom solution to push the data into a Log Analytics workspace
* Requires at least read permission for the Log Analytics workspace
* For the maps visuals the Azure Maps option should be enabled in the tenant settings: [Manage Azure Maps Power BI visual within your organization](https://learn.microsoft.com/en-us/azure/azure-maps/power-bi-visual-manage-access)
* Based on the retention of the tables in Log Analytics the data can be stored for up to 12 years [Manage data retention in a Log Analytics workspace](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/data-retention-configure?tabs=portal-3%2Cportal-1%2Cportal-2#configure-table-level-retention) 

M365D Hunting API version (legacy):
* No longer a fully supported API and can break at any moment, being replaced by the Microsoft Graph security API. Using Microsoft Graph directly in PowerBI is not recommended or supported: [Lack of Support for Microsoft Graph in Power Query](https://learn.microsoft.com/en-us/power-query/connecting-to-graph)
* It is using Delegated model to connect to the M365D Hunting API. No need for app registration simply need an admin account which can run the underlying Hunting queries using the API. 
* Access to the Advanced hunting feature in the M365 Defender portal is needed through appropriate permission and license. 
  * The built-in Security Reader or Security Administrator role is enough to have the report working for example. 
  * Defender for Office 365 Plan 2 standalone or included in Microsoft 365 A5/E5/F5/G5 Security

General considerations:
* These are intended to be a template, we encourage everybody to modify queries, visualizations, bring in more data sets based on organization needs. 
* The “ReadMe” tab of the template files has more information about terminology used in the template.  
* This not intended to be a permanent or complete solution rather show an example how to create custom Microsoft Defender for Office 365 (MDO) reports using the hunting API and Power BI. 

## Example View of Microsoft Defender for Office 365 (MDO) Detection Details Report 

![MDOPowerBI1](Media/MDOPowerBI1.png)

## How to use the .pbit file for Log Analytics/Sentinel

Opening the .pbit file will prompt for the Log Analytics Workspace ID at first run. <br/><br/> ![MDOLA1](Media/MDOLA1.png) <br/><br/>
It can be found in the Azure Portal on the Log Analytics page: <br/><br/> ![MDOLA2](Media/MDOLA2.png) <br/><br/>
After that make sure you sign in with the “Organization account” with permissions to the Log Analytics Workspace: <br/><br/> ![MDOLA3](Media/MDOLA3.png) <br/><br/>

## How to use the .pbit file for the Hunting API

Using the .pbit file will load the template with no data and ask for Authentication at first run. 
Power BI will ask for connect/Authenticate to the data source (Hunting API in M365D) <br/> <br/> ![MDOPowerBI2](Media/MDOPowerBI2.png)  <br/> <br/>
Change the settings to “Organization account” and Sign in with an account which has access to the M365D hunting tables. Minimum Azure AD built-in role/permission required to run the queries behind the report is “Security Reader” or “Security Operator” <br/> <br/> ![MDOPowerBI3](Media/MDOPowerBI3.png) <br/> <br/>
Follow the Authentication flow for the account after you clicked “Sign in” <br/> <br/> ![MDOPowerBI4](Media/MDOPowerBI4.png) <br/> <br/>
After you signed in click “Connect” and the data should load. It can take few minutes to load the data at the first time. It depends on the size if the environment Queries may run longer in a larger tenant. 

## How to publish to Power BI online and configure scheduled auto-refresh
You can publish the report to Power BI online when you finished making changes to visuals. In Power BI there is an easy way to share only the report with others without the need to have admin access to the underlying data set. It is also possible to configure scheduled auto-refresh so the report data kept up-to date.

To Publish the report:
* Use Power BI Desktop “Publish” action and click “Save” <br/> <br/> ![MDOPowerBI14](Media/MDOPowerBI14.png) <br/> <br/>
* Select a Power BI online workspace where you want to publish the report to. For example “My workspace” <br/> <br/> ![MDOPowerBI15](Media/MDOPowerBI15.png) <br/> <br/>
* Wait until the publishing process finishes <br/> <br/> ![MDOPowerBI16](Media/MDOPowerBI16.png) <br/> <br/>
* Open the published report and Share from Power BI based on needs. <br/> <br/> ![MDOPowerBI17](Media/MDOPowerBI17.png) <br/> <br/>
* Make sure the credentials used to update the data sets are correct. You can define it in the Data set Settings page. This used to update the data set during auto refresh. <br/> <br/> ![MDOPowerBI18](Media/MDOPowerBI18.png)  ![MDOPowerBI19](Media/MDOPowerBI19.png) <br/> <br/>
* You can also set up regular schedule for Auto refresh on the data set settings page: <br/> <br/> ![MDOPowerBI20](Media/MDOPowerBI20.png) <br/> <br/>
