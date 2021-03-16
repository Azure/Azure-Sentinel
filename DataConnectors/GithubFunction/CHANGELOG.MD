## 1.3
- Added secret-scanning/alerts logs
- Updated ARM template to support both Commercial and Azure Gov
- Removed previously added logic
	- Environment variables to provide additional support for users to supply their own values for Table names
	
	

## 1.2
- Fixed issues raised on Sentinel GitHub Repo on AuditLogs
- Updated logic to ingest each AuditLog as an individual record
- Added two environment variables to provide additional support for users to supply their own values for Table names
- Pushing all these latest changes as in-place upgrade, if users dont create environment variables, it will use old tables

## 1.1
- Added CHANGELOG.MD to track future code changes
- Updated "lastrun-Audit.json" to support multiple org's
- Implemented logic to support multiple org's in Function App code
- Implemented logic to support Azure Gov (.US) Tenants in Function App code
- Created new ARM Template to Support Azure Gov (.US) Tenants
- Updated "function.json" inorder to accept TimeTrigger(CRON Expression) from Function App environment variable. Providing more flexibility to the user to change schedule to trigger Function App
- Updated README.MD
- Updated File structure

## 1.0
- Converted GitHub Data connector from Logic Apps to Azure Function
- Splitting the data if it is more than 25MB