# Changelog for ASimWebSessionSalesforceServiceCloud

## Version 0.2.0

- (2026-09-14) Add support for updated connector via SalesforceServiceCloudV3_CL table - [PR #15123](https://github.com/Azure/Azure-Sentinel/pull/15123)

## Version 0.1.0

- (2026-06-05) Initial creation of the parser [PR #14424](https://github.com/Azure/Azure-Sentinel/pull/14424)
- Normalizes Salesforce Service Cloud web session and API request logs from SalesforceServiceCloudV2_CL table
- Maps Salesforce event types (ApiTotalUsage, RestApi, BulkApi2, URI, AuraRequest, LightningPageView, etc.) to ASIM EventType values (ApiRequest, WebServerSession)
- Supports HTTP status code to EventResult mapping
- Extracts destination hostname from URL
- Maps TLS, network duration, and session fields
- Supports optional AdditionalFields packing via pack parameter
