# Azure Active Directory User Details into Log Analytics

## Azure Active Directory Log Analytics Enrichment (Script)
This scripts is a manual ingestion of Azure Active Directory data (unfiltered) to Log Analytics.
Requirements are setting up and configuring service account that has access to Azure Active Directory

## Azure Automation AAD Import (Script)
This script is a automation ingestion of AAD Data (unfiltered) into Log Analytics.
Requirements are allowing the Automation account access to the Azure AD (GraphAPI) Read Directory permissions
Note: Due to some data set size(memory) issue it was configured to ingest 10 users at a time, you can expand this depending on what information you're wanting to pull from AAD

## Azure Active Directory Function (Copy of script example)
This script is using API's from Azure AD with Graph Security API and ingesting data from AAD into Log Analytics much like the Azure Automation script without modules.
