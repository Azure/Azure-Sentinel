# How to contribute new workbook

This assumes that you already have a workbook that you want to share as a Sentinel template.<br/>
Once this process is done, Sentinel users will be able to save an instance of your template that will visualize the data in their own workspace. 

To learn how to create workbooks - go to [workbooks documentation](https://docs.microsoft.com/en-us/azure/azure-monitor/app/usage-workbooks) 

## Step 1 - get the workbook gallery template:

1. Go to your workbook -> edit mode -> advanced editor.
2. Copy the gallery template.
3. capture 2 screenshots of your workbook - in dark and white theme (this will eventually be the preview images displayed in the workbooks blade).

## Step 2 - create a PR to this repo

1. In the PR - add the screenshots under workbooks/images/previews
2. Add the gallery template json directly under workbooks directory.
3. (optional) add a logo that you want the workbook to display under workbooks/images/logos - if not supplied - it will be the generic workbooks logo.
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
    
    "provider": "Microsoft"
    }
  
  After this PR is updated, every 2 weeks the workbooks in Sentinel will be synced to the ones in github.
  
 
# how to update workbooks

Just change the version in the WorkbooksMetadata.json file and change the relevant JSON of the workbook you would like to update.
If needed, also update the preview images or the data types.


For questions you can contact Amit Bergman - t-amberm@microsoft.com
