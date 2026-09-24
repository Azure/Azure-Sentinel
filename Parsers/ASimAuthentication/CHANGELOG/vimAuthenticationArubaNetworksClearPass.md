# Changelog for vimAuthenticationArubaNetworksClearPass.yaml

## Version 0.1.0

- (2026-09-24) Initial creation of the parser
    - Only RADIUS/TACACS+ logon decision events (`DeviceEventClassID` 2000, 2001, 2003) are mapped. Accounting (2002, 2004), Guest Access (2006), Audit Records (3xxx), and System Events (4xxx) are excluded as they carry no useful authentication outcome
    - For TACACS (`2003`), keep only `TACACS_AUTHENTICATION` / `AUTHEN` (or missing request type)`TACACS_AUTHORIZATION` are dropped.
- [PR #15192](https://github.com/Azure/Azure-Sentinel/pull/15192)
