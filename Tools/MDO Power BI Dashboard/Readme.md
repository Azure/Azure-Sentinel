# Microsoft Defender for Office 365 Detection Details Report – Configuration Guide 

## Contents

[Overview](#overview)<br/>
[Example View of Microsoft Defender for Office 365 (MDO) Detection Details Report](#example-view-of-microsoft-defender-for-office-365-mdo-detection-details-report)<br/>
[How to use the .pbit file](#how-to-use-the-pbit-file)<br/>
[How to use the .pbix file](#how-to-use-the-pbix-file)<br/>
[How to publish to Power BI online and configure scheduled auto-refresh](#how-to-publish-to-power-bi-online-and-configure-scheduled-auto-refresh)<br/>

## Overview

This report template will give you an example how to use Microsoft 365 Defender Hunting API to built a custom report using Power BI. This way you can visualise Microsoft Defender for Office 365 (MDO) data based on your organisation needs. 

* It is using Delegated model to connect to the M365D Hunting API. No need for app regirstartion simply need an admin account which can run the underlying Hunting queries using the API. 
* The built-in Security Reader or Security Administrator role is enough to have the report working for example. 
* This is inteneded to be a template, we encourage everybody to modify queries, visualisations, bring in more data sets based on organisation needs. 
* The “ReadMe” tab of the template files has more information about terminology used in the template.  
* This not intended to be a permanent or complete solution rather show an example how to create custom Microsoft Defender for Office 365 (MDO) reports unsing the hunting API and Power BI. 

## Example View of Microsoft Defender for Office 365 (MDO) Detection Details Report 

**Example view opening the .pbit template in Power BI Desktop**
![MDOPowerBI1](Media/MDOPowerBI1.png)

## How to use the .pbit file

Using the .pbit file will load the template with no data and ask for Authentication at first run.
Power BI will ask for connect/Authenticate to the data source (Hunting API in M365D) <br/> ![MDOPowerBI2](Media/MDOPowerBI2.png)
Change the settings to “Organization account” and Sign in with an account which has access to the M365D hunting tables. Minimum Azure AD built-in role/permission required to run the queries behind the report is “Security Reader” or “Security Operator” <br/> ![MDOPowerBI3](Media/MDOPowerBI3.png)
Follow the Authentication flow for the account after you clicked “Sign in” <br/> ![MDOPowerBI4](Media/MDOPowerBI4.png)
After you signed in click “Connect” and the data should load. It can take few minutes to load the data at the first time. It depends on the size if the environment Queries may run longer in a larger tenant. 

## How to use the .pbix file
When the .pbix file opens, it loads with data from a sample demo environment.

To update the file with your organization tenant data:
* Expand on the fields side pane, and then right click on any table entry and open the Edit query option. <br/> ![MDOPowerBI5](Media/MDOPowerBI5.png)
* In the Power Query Editor window click on data source settings in the top <br/> ![MDOPowerBI6](Media/MDOPowerBI6.png)
* Select “Data sources in this file” and the entry for M365D API connection. Click “Edit permission” <br/> ![MDOPowerBI7](Media/MDOPowerBI7.png)
* On the ”Edit Permissions” window click on “Edit…” <br/> ![MDOPowerBI8](Media/MDOPowerBI8.png)
* On the Access Web Content page select “Organizational Account” and “Sign in”. Use your admin account for your organization to Authenticate.<br/> ![MDOPowerBI9](Media/MDOPowerBI9.png)
* Click “Save” <br/> ![MDOPowerBI10](Media/MDOPowerBI10.png)
* Click “OK” and “Close” <br/> ![MDOPowerBI11](Media/MDOPowerBI11.png)
* Click on “Close and Apply” <br/> ![MDOPowerBI12](Media/MDOPowerBI12.png)
* The data should load from your tenant now. <br/>
**Note:** It can take quite a few minutes to load the data in a live environment. The dashboard using separate Advance Hunting queries to get the data from the M365D Hunting API. <br/> ![MDOPowerBI13](Media/MDOPowerBI13.png)

## How to publish to Power BI online and configure scheduled auto-refresh
You can publish the report to Power BI online when you finished making changes to visuals. In Power BI there is an easy way to share only the report with others without the need to have admin access to the underlying data set. It is also possible to configure scheduled auto-refresh so the report data kept up-to date.

To Publish the report:
* Use Power BI Desktop “Publish” action and click “Save” <br/> ![MDOPowerBI14](Media/MDOPowerBI14.png)
* Select a Power BI online workspace where you want to publish the report to. For example “My workspace” <br/> ![MDOPowerBI15](Media/MDOPowerBI15.png)
* Wait until the publishing process finishes <br/> ![MDOPowerBI16](Media/MDOPowerBI16.png)
* Open the published report and Share from Power BI based on needs. <br/> ![MDOPowerBI17](Media/MDOPowerBI17.png)
* Make sure the credentials used to update the data sets are correct. You can define it in the Data set Settings page. This used to update the data set during auto refresh. <br/> ![MDOPowerBI18](Media/MDOPowerBI18.png) <br/> ![MDOPowerBI19](Media/MDOPowerBI19.png)
* You can also set up regular schedule for Auto refresh on the data set settings page: <br/> ![MDOPowerBI20](Media/MDOPowerBI20.png)
