## 2.1.1
- Moved version 2.1.0 to sub folder AzureFunctionOktaSSO_V2 under Azure-Sentinel/DataConnectors/Okta Single Sign-On/
- Created V2 versions of Azure Deploy and Connector Json files to enable both versions to co-exist
- Changed zip file reference to use 'https://aka.ms/sentineloktaazuredeployv2' in Azure Deploy json file
- Changed run.ps1 reference to use 'https://aka.ms/sentineloktaazurefunctioncodev2' in Connector json file

## 2.1.0
- Modified Okta Event log tracking to use next URI link from header
- Fixed Total record counter to record correctly the total number of records ingested

## 2.0.2
- Added  ACN_CD_OktaIssue925 resolution to add domain to output records

## 2.0.1
- Added CHANGELOG.md to track future code changes
- Complete rewrite of Azure Function code to address the following
    - Code needs to loop requests to Okta as each response from Okta is limited to max of 1000 records
    - relying on Timetrigger time minus (-) 5 minutes is unreliable and may result in duplicates and missing records
    - Okta communicates via HTTP Headers details about log event pagination orginal version did not utilise this information
- Added using a table on Azure Storage account of function to maintain state of latest event time provided in OKTA Response 
- Added logic to use OKTA time detials in records to track last record returned from OKTA
- Added Loop to continue getting paged results from OKTA until either all records retrieved or getting close (260 seconds) to Azure Function default timeout (300 seconds)
- Added dependency on Powershell modules 'AZTable' and 'Az.OperationalInsights'
- Fixed Timestamp to corret field from OKTA "published" field for Azure Log Analytics Time Generated header in Post HTTP
- Fixed HTTP Request to OKTA, we need the Headers and 'Invoke-RestMethod' won't provide them
- Fixed HTTP request to OKTA to use limit, since and after parameters to make sure we get all records and also don't get duplicates
- Removed need for Environment setting of 'TimeTrigger' Function is now self managing event log times
- Cleanup of Azure Function Log messages, consistent format of output
- Added inline comments to explain code logic

## 1.1
- Added Hardcoded table name