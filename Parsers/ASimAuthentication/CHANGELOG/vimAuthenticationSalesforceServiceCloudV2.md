# Changelog for vimAuthenticationSalesforceServiceCloud

## Version 0.1.0 - 2026-06-05

- (2026-06-05) Initial creation of the filtering parser
- Normalizes Salesforce Service Cloud V2 authentication logs from 'SalesforceServiceCloudV2_CL' table
- Supports filtering by starttime, endtime, username_has_any, targetappname_has_any, srcipaddr_has_any_prefix, srchostname_has_any, eventtype_in, eventresultdetails_in, and eventresult
- Maps Login/Logout events to ASIM Logon/Logoff EventType
- Maps LoginStatus to EventResult and EventResultDetails
- Maps UserType to TargetUserType
- Includes ASimMatchingUsername for username filter match tracking
