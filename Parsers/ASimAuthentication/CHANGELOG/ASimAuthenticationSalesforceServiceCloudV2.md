# Changelog for ASimAuthenticationSalesforceServiceCloud

## Version 0.1.0 - 2026-06-05

- (2026-06-05) Initial creation of the parser
- Normalizes Salesforce Service Cloud V2 authentication logs from 'SalesforceServiceCloudV2_CL' table
- Maps Login/Logout events to ASIM Logon/Logoff EventType
- Maps LoginStatus to EventResult and EventResultDetails
- Maps UserType to TargetUserType
- Supports SourceIp and ClientIp fallback for SrcIpAddr
