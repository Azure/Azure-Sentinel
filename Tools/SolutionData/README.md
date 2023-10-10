# SolutionData
Create a CSV to show solution information.  Includes PowerBI and Workbook to show data

To Run:

 Export-AzSentineMITREIncidentsToCSV -WorkspaceName "WorkspaceName" -ResourceGroupName "rgname"

        In this example you will get the file named "mitrerules.csv" generated containing the count of the active rule's MITRE information

Export-AzSentineMITREIncidentsToCSV -WorkspaceName "WorkspaceName" -ResourceGroupName "rgname" -FileName "test"

        In this example you will get the file named "test.csv" generated containing  the count of the active rule's MITRE information

There is an included "solutionexport.csv" file that serves as an example of the output.  You can upload this into a Microsoft Sentinel watchlist and then use the included workbook to view it.

> Note:  Due to the size of the CSV file, it must first be uploaded into an Azure Blog storage account and then used to create the watchlist. [Create Large Watchlists using SAS Key](https://techcommunity.microsoft.com/t5/microsoft-sentinel-blog/large-watchlist-using-sas-key-is-in-public-preview)

There can be an issue where the CSV file failed to work correctly when creating the watchlist.  In that case, open it in Excel and save it again.

When creating the Watchlist, set both the name to whatever you like, the alias to "SolutionData", and the SearchKey to the "Index" column.