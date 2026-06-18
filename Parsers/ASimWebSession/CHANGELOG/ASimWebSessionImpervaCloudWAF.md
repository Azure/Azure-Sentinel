# Changelog for ASimWebSessionImpervaCloudWAF

## Version 0.1.0 - 2025-07-11

- (2025-07-11) Initial creation of the parser
- Maps Imperva Cloud WAF SIEM integration logs from ImpervaWAFCloud table to ASIM WebSession schema
- Includes severity lookup mapping 15 threat categories (XSS, DDoS, Backdoor, Bot, etc.)
- Includes DvcAction lookup mapping 7 request action types to Allow/Deny/Drop
- Maps geo-location fields (country, city, latitude, longitude) from source
- Supports pack parameter for additional fields (SiteID, AccountID, PostBody, etc.)
