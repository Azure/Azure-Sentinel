## 1.0
- Azure Function to ingest AWS SecurityHub Findings via SecurityHub REST API
- ARM template to deploy Azure Function for both Azure Commercial and Azure Gov
- README.MD with instructions & filtering capabilities

## 1.1
- Fixed issue with regular expression module

## 2.0
- Added new authentication method, using Azure AD as IdP and the Managed Identity of the function to perform "AssumeRoleWithWebIdentity"
