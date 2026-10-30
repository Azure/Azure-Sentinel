# Changelog for vimAlertEventSalesforceRealTimeEventMonitoring.yaml

## Version 0.1.0 - 2026-10-30

- Forward all filtering and control parameters to the inner parser; apply constant and source-field filters before normalization and packing.
- Reference all seven Salesforce event-store APIs, normalize the guest user's original user type, and retain documented login, report, SOQL, controller, and anomaly-feature context when packing.
- Keep anomaly scores as source context: documented scales differ by event type and do not establish an analyst verdict or severity.
- (2026-10-30) Initial creation of the Salesforce Real-Time Event Monitoring AlertEvent parser.
- Salesforce anomaly event-store records are normalized as alert events. The source does not supply analyst verdicts or normalized severity, so verdict and severity defaults are conservative; source score remains additional context. Identity-provider and LoginAccessChange coverage are not included.
