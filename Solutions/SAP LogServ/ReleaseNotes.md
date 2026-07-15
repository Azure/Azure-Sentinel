| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
| 3.0.5       | 10-07-2026                     | DCR KQL transforms route logs to standard tables (Syslog, WindowsEvent, ASimDnsActivityLogs, ASimWebSessionLogs, ABAPAuditLog and more), including Squid proxy access logs to ASimWebSessionLogs both Web Dispatcher access-log formats (bracketed-header and `… sent … ms to …`) and ABAP ICM HTTP access logs (abap/httpaccesslog) to ASimWebSessionLogs (typed as WebServerSession with a path-only URL, since the ABAP server reports its own requests); Squid proxy `-` src/dest IPs normalized to empty strings for ASIM compliance; catch-all retains any unmatched/future source into SAPLogServ_CL instead of dropping it; HANA DB analytic rules read from the Syslog table instead of SAPLogServ_CL; connector description clarifies ASIM/standard-table detections are covered out of the box and not duplicated here; retained SAPLogServ_CL test/test1 columns for upgrade compatibility |
| 3.0.4       |  11-08-2025                    | Connector UI updates |
| 3.0.3       |  17-07-2025                    | Observability Workbook added |
| 3.0.2       |  25-06-2025                    | Analytic Rules for HANA DB added |
| 3.0.1       |  09-04-2025                    | Retention setting dropped from table to default to LogAnalytics ws default |
| 3.0.0       |  17-02-2025                    | Initial Solution Release |
