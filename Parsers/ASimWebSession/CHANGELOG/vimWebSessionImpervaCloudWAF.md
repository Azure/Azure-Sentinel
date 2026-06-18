# Changelog for vimWebSessionImpervaCloudWAF

## Version 0.1.0 - 2025-07-11

- (2025-07-11) Initial creation of the filtering parser
- Supports filtering by time range, source/destination IP prefix, URL, HTTP user agent, event result details, and event result
- Includes ASimMatchingIpAddr field for IP address filter match tracking
- Maps Imperva Cloud WAF SIEM integration logs from ImpervaWAFCloud table to ASIM WebSession schema
- Includes severity lookup mapping 15 threat categories
- Includes DvcAction lookup mapping 7 request action types
