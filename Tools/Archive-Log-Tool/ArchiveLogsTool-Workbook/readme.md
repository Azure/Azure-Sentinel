## Review and Manage Data Table Retention
**Author : Matt Lowe**

## Deployment Process
1. Copy the content of the workbook JSON file.
2. Go to the Azure Portal.
3. Go to Microsoft Sentinel.
4. Go to Workbooks.
5. Click 'Add Workbook'.
6. Go into edit mode.
7. Go into the advanced editor.
8. Paste the content that was copied from the JSON file.
9. Click save as and name the workbook 'Archive Log Tool'.

## How to use
1. Set the proper subscription and workspace to review.
2. Click on a table or search table to gather the retention information.
3. If the retention of the table needs to be changed, modify the API body JSON.
- If changing the retention in the workspace, modify retentionInDays
- If changing the retention in archive, set retentionInDays to 'Null' and change the totalRetentionInDays.
4. Click on the corresponding button to modify the retention for the selected table.

### Note: Archive retention is calculated by using archiveRetention = totalRetentionInDays - retentionInDays.
   
