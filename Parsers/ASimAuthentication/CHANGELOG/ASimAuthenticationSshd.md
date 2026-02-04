# Changelog for ASimAuthenticationSshd.yaml

## Version 0.3.1
- (2026-01-26) [ASIM] Authentication - SSHD Fix invalid user parsing - [PR #13531](https://github.com/Azure/Azure-Sentinel/pull/13531)
- Fix bug where "Invalid user" failed login events were not parsed correctly if it did not include port number.
  - There is a difference in parsing "Invalid user root from 0.0.0.0 port 0" and "Invalid user root from 0.0.0.0"

## Version 0.3.0

- (2026-01-20) [ASIM] Authentication - Sshd Parser fixes - [PR #13460](https://github.com/Azure/Azure-Sentinel/pull/13460)

## Version 0.2.4

- (2025-11-24) Changed Condition for Successful login - [PR #12215](https://github.com/Azure/Azure-Sentinel/pull/12215)

## Version 0.2.2

- (2023-09-18) Multiple ASIM Parser Changes - [PR #9032](https://github.com/Azure/Azure-Sentinel/pull/9032)

## Version 0.2.1

- (2023-07-24) Fix-Authentication-Parsers - [PR #8615](https://github.com/Azure/Azure-Sentinel/pull/8615)

## Version 0.2.0

- (2023-01-29) asim sshd update - [PR #7165](https://github.com/Azure/Azure-Sentinel/pull/7165)

## Version 0.1.1

- (2023-01-21) add ASimAuthentication Parsers for syslog sshd, su and sudo - [PR #7098](https://github.com/Azure/Azure-Sentinel/pull/7098)

