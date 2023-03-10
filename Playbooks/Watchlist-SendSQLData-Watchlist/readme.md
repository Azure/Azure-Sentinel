# Watchlist-SendSQLData-Watchlist
author: Yaniv Shasha

This playbook levarages Azure Sentinel Watchlists in order to get the relevant date from Azure SQL, and create a new watchlist or update an exsisting watchlsit with the query output.


Prerequisites
•	A user or registered application with Azure Sentinel Contributor role to be used with the Azure Sentinel connector to Logic Apps.
•	A user with read access to SQL database to be able to query the data




<img src="https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/Watchlist-SendSQLData-Watchlist/images/higlevel.PNG"/><br><br>


The playbook, presented below, works as follows:
1.	Triggers daily.
2.	Take as variables the:
•	Subscription
•	Workspace
•	resource group
•	watchlist name. 
3.	Run SQL Select statement against Azure SQL DB (can be change this logic app to run against SQL On-prem with logic app getaway feature 
4.	Parse the results as JSON (if you are running different SQL query, you should adapt the Parse json schema)
5.	Create CSV payload from the results. 
6.	Check if the watchlist exists.
7.	Based on the result, create, or update the watchlist with the result set from the SQL query 

<br><br>

<img src="https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/Watchlist-SendSQLData-Watchlist/images/pic01-withnumberes.PNG"/><br><br>

<img src="https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/Watchlist-SendSQLData-Watchlist/images/pic2_with_numberes.PNG"/><br><br>


Step 1: Deploy the Logic App on Azure Sentinel.
 
1.	Open the link to the playbook.  Scroll down on the page and Click on “Deploy to Azure” or "Deploy to Azure Gov" button depending on your need.
2.	Fill the parameters:


1.	Playbook name - this is how you'll find the playbook in your subscription
2.	User name (will affect the names of the API connections resources)
3.	Azure Sentinel Workspace Name
4.	Azure Sentinel ResourceGroup
5.	The WatchList name
6.	SQL Query that will run aginst the DB
7.	Check the terms and conditions and click purchase.
8.	The ARM template, contains the Logic App workflow (playbook) and API connections is now deploying to Azure. When finished, you will be taken to the Azure ARM Template summary page.
9.	Click on the Logic Apps name. you will be taken to the Logic Apps resource of this playbook.
Confirm API connections
On the left menu, click on API connections.
For each product being used in this playbook, click on the connection name - in our case, it is only the Azure Sentinel connection.
Click on Authorize to log in with your user, and don't forget to save.

<img src="https://github.com/Azure/Azure-Sentinel/blob/master/Playbooks/Watchlist-SendSQLData-Watchlist/images/deploy.PNG"/><br><br>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlist-SendSQLData-Watchlist%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FWatchlist-SendSQLData-Watchlist%2Fazuredeploy.json)
