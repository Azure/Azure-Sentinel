## Review and Manage Data Table Retention
**Author : Matt Lowe**

With the introduction of the new Search, Archive, and Restoration features within Microsoft Sentinel and Azure Log Analytics, it is imperative that the retention on tables with the workspace is monitored. To make this process easier, this tool has been developed within Microsoft Sentinel Workbooks. This tool allows users to perform the following:
- Identify tables within the workspace.
- Identify search tables that have been generated within the workspace.
- Retention set for the table within the workspace
- Retention set for archiving.
- Total retention of the data in both the worksapce and in archive.
- Update retention for the data in the workspace and archive.

## Prerequisites
1. Join the preview: Sign up for the preview program at https://aka.ms/securityprp.
2. Get onboarded via our sign-up form: https://aka.ms/sentinel/search/private-preview/onboardingform.
3. Have been added to the allow list for the preview (done after the form is filled out and submitted).
4. Use the feature flag included in the onboarding and preview document.

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
   
