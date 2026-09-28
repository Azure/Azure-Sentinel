| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                           |
|-------------|--------------------------------|--------------------------------------------------------------|
| 3.0.3       | 28-09-2026                     | Fixed Akamai CCF pagination by retaining time-window polling for initial requests and sending only offset parameters on subsequent pages, preventing skipped events without blocking connection initialization. |
| 3.0.2       | 27-08-2026                     | Updated the AkamaiSIEMEvent parser to decode rule and HTTP header values while preserving events with empty rule fields and retaining encoded source values in Raw-suffixed columns. |
| 3.0.1 | 20-07-2026 | Promoted Akamai DDOS CCF data connector from public preview to GA  |
| 3.0.0       | 24-06-2026                     | Created a Data Connector for Akamai DDOS Protection CCF Container with the WAF security events data stream. |
