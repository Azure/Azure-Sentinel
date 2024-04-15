# How to contribute new workbook

This assumes you already have a workbook that you want to share as a Microsoft Sentinel template.<br/>
Once this process is completed, Microsoft Sentinel users will be able to save an instance of your template that will visualize the data in their own workspace. 

To learn how to create workbooks - go to [workbooks documentation](https://docs.microsoft.com/azure/sentinel/tutorial-monitor-your-data).

## Step 1 - get the workbook gallery template:

1. Go to your workbook -> edit mode -> advanced editor.
2. Copy the gallery template.
3. Add **_fromTemplateId_** to your template - this allows us to identify in our telemetry the specific sentinel workbook that was opened. Please be consistent with the format _sentinel-"workbookName"_, for example (in the end of the gallery template):

   ```
    "styleSettings": {},
    "fromTemplateId": "sentinel-MyNewWorkbook",
    "$schema": "https://github.com/Microsoft/Application-Insights-Workbooks/blob/master/schema/workbook.json"

4. Capture 2 screenshots of your workbook - in dark and light theme (this will eventually be the preview images displayed in the workbooks blade).

## Step 2 - Create a pull request to this repository

This pull request will contain:

* The screenshots of your workbook. Place them under [workbooks/images/preview](https://github.com/Azure/Azure-Sentinel/tree/master/Workbooks/Images/Preview). <br/>Please be consistent with the filename conventions - the dark theme filename should contain the word _"black"_ and the light theme image should contain the word _"white"_.
* The gallery template json of your workbook. Place it directly under workbooks [directory](https://github.com/Azure/Azure-Sentinel/tree/master/Workbooks).
* (optional) A logo that you want the workbook to display. Place it under [workbooks/images/logos](https://github.com/Azure/Azure-Sentinel/tree/master/Workbooks/Images/Logos) - if not supplied - it will be the generic workbooks logo. <br/>
This logo should be in SVG format.
* Change workbooksMetadata.json [file](https://github.com/Azure/Azure-Sentinel/blob/master/Workbooks/WorkbooksMetadata.json), so that it will contain a new section, which will include:

   ```
   {
    "workbookKey": "YourWorkbookKey", // in the format of "<Name>Workbook" - not important what exactly is the name, just make sure it is unique and related to the workbook, for example PaloAltoOverviewWorkbook
    
    "logoFileName": "",//If you added logo - its name goes here
    
    "description": "description of the workbook.", // Will be displayed on the workbooks blade next to the logo and preview images
    
    "dataTypesDependencies": [ "Datatype" ],//The data type(s) that your workbook queries
    
    "dataConnectorsDependencies": [],//Relevant connectors
    
    "previewImagesFileNames": [ ],//The relative path of the preview images you saved under workbooks/images/previews
    
    "version": "1.0", // if this is a new workbook - this should be "1.0"
    
    "title": "Workbook title",//This should be the name of the workbook which will be displayed in the main workbooks blade - for example "Palo Alto overview"
    
    "templateRelativePath": "MyNewWorkbook.json",//The relative path of the JSON of the template (the gallery template you saved) 
    
    "subtitle": "",
    
    "provider": "Microsoft" //The provider of the workbook
    }
    
 Here is an example of the JSON of Palo Alto workbook:
  
    
       {
      "workbookKey": "PaloAltoOverviewWorkbook",
      "logoFileName": "paloalto_logo.svg",
      "description": "Gain insights and comprehensive monitoring into Palo Alto firewalls by analyzing traffic and activities.\nThis workbook correlates all Palo Alto data with threat events to identify suspicious entities and relationships.\nYou can learn about trends across user and data traffic, and drill down into Palo Alto Wildfire and filter results.",
      "dataTypesDependencies": [ "CommonSecurityLog" ],
      "dataConnectorsDependencies": [ "PaloAlto" ],
      "previewImagesFileNames": [ "PaloAltoOverviewWhite1.png", "PaloAltoOverviewBlack1.png", "PaloAltoOverviewWhite2.png", "PaloAltoOverviewBlack2.png", "PaloAltoOverviewWhite3.png", "PaloAltoOverviewBlack3.png" ],
      "version": "1.1",
      "title": "Palo Alto overview",
      "templateRelativePath": "PaloAltoOverview.json",
      "subtitle": "",
      "provider": "Microsoft"
      },
   
  
  After this PR is approved and completed, every 2 weeks the workbooks in Sentinel will be synced with the ones in github.<br/>  
  
 
# How to update an existing workbook

Just create a pull request to this repository in which you change the version of the relevant workbook in the [WorkbooksMetadata.json](https://github.com/Azure/Azure-Sentinel/blob/master/Workbooks/WorkbooksMetadata.json) file and change the relevant JSON of the workbook you would like to update.
If needed, also update the preview images or the data types.


For any feedback on the instructions [Open an issue](https://github.com/Azure/Azure-Sentinel/issues/new?assignees=&labels=&template=bug_report.md&title=)
