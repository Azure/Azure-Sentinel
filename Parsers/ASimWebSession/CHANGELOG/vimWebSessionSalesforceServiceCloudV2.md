# Changelog for vimWebSessionSalesforceServiceCloud

## Version 0.1.0 - 2026-06-05

- (2026-06-05) Initial creation of the filtering parser
- Adds filtering parameters: starttime, endtime, srcipaddr_has_any_prefix, ipaddr_has_any_prefix, url_has_any, httpuseragent_has_any, eventresultdetails_in, eventresult
- Pre-filters on physical fields before parsing for optimal performance
- Post-filters ipaddr_has_any_prefix on resolved SrcIpAddr
- Normalizes Salesforce Service Cloud web session and API request logs from SalesforceServiceCloudV2_CL table
