## 2.1
- Implemented new logic to ingest users without duplication
- Adding UserId and UserName to Storage Account Table to avoid duplication

## 2.0
- Added CHANGELOG.MD to track future code changes
- Re-designed architecture of the Data connector
- Implemented logic to generate JWT Token and then get Access Token to interact with DocuSign API
- Implemented logic to ingest DocuSign Users into Log Analytics Table
- Added logic to update base uri to retrive users using Environment Variable
- Created single ARM Template to support both Azure Commerical & Azure Gov (.US) Tenants
- Updated README.MD


## 1.0
- Ingesting DocuSign Security Events into Azure Log Analytics Workspace
- Using DocuSign Access Token to interact with DocuSign Monitor API
- Access Token expires every 1 hr
- Updated "function.json" inorder to accept TimeTrigger(CRON Expression) from Function App environment variable. Providing more flexibility to the user to change schedule to trigger Function App