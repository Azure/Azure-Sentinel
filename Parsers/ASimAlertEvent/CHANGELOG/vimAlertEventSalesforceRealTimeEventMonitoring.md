# Changelog for vimAlertEventSalesforceRealTimeEventMonitoring.yaml

## Version 0.1.0 - 2026-10-30

- (2026-10-30) Initial creation of the Salesforce Real-Time Event Monitoring AlertEvent parser.
- Salesforce anomaly event-store records are normalized as alert events. The source does not supply analyst verdicts or normalized severity, so verdict and severity defaults are conservative; source score remains additional context. Identity-provider and LoginAccessChange coverage are not included.
