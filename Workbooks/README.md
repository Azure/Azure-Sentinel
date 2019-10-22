# How to contribute new workbook

This assumes that you already have a workbook that you want to share as a Sentinel template.<br/>
Once this process is done, Sentinel users will be able to save an instance of your template that will visualize the data in their own workspace. 

To learn how to create workbooks - go to [workbooks documentation](https://docs.microsoft.com/en-us/azure/azure-monitor/app/usage-workbooks) 

## Step 1 - get the workbook gallery template:

1. Go to your workbook -> edit mode -> advanced editor.
2. Copy the gallery template.
3. Add **_fromTemplateId_** to your template - this allows us to identify in our telemetry the specific sentinel workbook that was opened: for example (in the end of the gallery template):

   ```
    "styleSettings": {},
    "fromTemplateId": "sentinel-MyNewWorkbook",
    "$schema": "https://github.com/Microsoft/Application-Insights-Workbooks/blob/master/schema/workbook.json"

4. capture 2 screenshots of your workbook - in dark and light theme (this will eventually be the preview images displayed in the workbooks blade).

## Step 2 - Create a PR to this repository

1. In the PR - add the screenshots under [workbooks/images/preview](https://github.com/Azure/Azure-Sentinel/tree/master/Workbooks/Images/Preview). <br/>Try to be consistent with the filename conventions - the dark theme filename should contain the word _"black"_ and the light theme image should contain the work _"white"_
2. Add the gallery template json of your workbook directly under workbooks [directory](https://github.com/Azure/Azure-Sentinel/tree/master/Workbooks).
3. (optional) add a logo that you want the workbook to display under [workbooks/images/logos](https://github.com/Azure/Azure-Sentinel/tree/master/Workbooks/Images/Logos) - if not supplied - it will be the generic workbooks logo. <br/>
This logo should be in SVG format.
4. Under workbooksMetadata.json file, add another section, which will include:

   ```
   {
    "workbookKey": "YourWorkbookKey", // in the format of "<Name>Workbook"
    
    "logoFileName": "",//If you added logo - its name goes here
    
    "description": "description of the workbook.", // Will be displayed on the workbook
    
    "dataTypesDependencies": [ "Datatype" ],//The data type(s) that your workbook queries
    
    "datasourceCardKeysDependencies": [],//Relevant connectors
    
    "previewImagesFileNames": [ ],//The relative path of the preview images you saved under workbooks/images/previews
    
    "version": "1.0", // if this is a new workbook - this should be "1.0"
    
    "title": "Workbook title",//This should be the name of the workbook which will be displayed in the main workbooks blade - for example "Palo Alto overview"
    
    "templateRelativePath": "MyNewWorkbook.json",//The relative path of the JSON of the template (the gallery template you saved) 
    
    "subtitle": "",
    
    "provider": "Microsoft" //The provider of the workbook
    }
  
  After this PR is updated, every 2 weeks the workbooks in Sentinel will be synced to the ones in github.<br/>
  If you cannot wait 2 weeks, contact t-amberm@microsoft.com or mor.shabi@microsoft.com.
  
 
# How to update workbooks

Just change the version in the WorkbooksMetadata.json file and change the relevant JSON of the workbook you would like to update.
If needed, also update the preview images or the data types.


For questions you can contact Amit Bergman - t-amberm@microsoft.com
