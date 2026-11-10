# Changelog for vimWebSessionSalesforceRealTimeEventMonitoring.yaml

## Version 0.1.0

- (2026-10-26) Initial creation of the parser - [PR #15437](https://github.com/Azure/Azure-Sentinel/pull/15437)
- Maps LightningUriEvent and UriEvent (WebServerSession) from SalesForceRealTimeEventMonitoring_CL
- ApiEvent is not mapped, the source has no request URL
- Url holds the page path or /RecordId without the org domain, which is mapped to DstFQDN
- EventResult is derived from OperationStatus, there is no HTTP status code or method in the source
- Non-IP SourceIp values such as 'Salesforce.com IP' are mapped to SrcDescription
