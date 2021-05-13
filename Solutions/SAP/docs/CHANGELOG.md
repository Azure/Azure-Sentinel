# Microsoft SAP Logs Connector - Limited Private Preview

Copyright (c) Microsoft Corporation.  This preview software is Microsoft Confidential, and is subject to your Non-Disclosure Agreement with Microsoft.  You may use this preview software internally and only in accordance with the Azure preview terms, located at [Preview terms][PreviewTerms].  Microsoft reserves all other rights

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.19] - 2021-02-28
### Added
- Audit Log Legacy Files Interface using RFC for 7.4 support of full metadata - Terminal/IP/Transaction Code.
- Time chunker for recovery from downtimes - Audit Log - (XAL/Files), Change Documents, JobLog, Change Request, Workflow, Spool, Spool Output.
- Improved Error Handling and Logging - Configuration checks according to activated logs.
### Fixed
- Time chunker for recovery from downtimes - Audit Log - SAL.
- Seperate Variables in Audit Log - XAL.

## [0.0.18] - 2021-02-18
### Added
- Time chunker for recovery from downtimes - SAP Control Files ABAP + Java, ABAP Audit Log - SAL.
### Fixed
- API Failover mechanism - persist during partial fails only.
- ABAP DB Table Data Log - Fix Support for ABAP versions < 7.50.
- Default Logs configuration

## [0.0.17] - 2021-01-28
### Added
- Initial Analytics package.
### Fixed
- Configuration Generator Menu - Docker build using mounted folder.
- Change default logs activation status.

## [0.0.16] - 2021-01-21
### Added
- ABAP Audit Log - Classify Computer and TerminalIPV6 according to retrieved data.
### Fixed
- Align Logs Schema.
- Improve integration with Azure Key Vault as Secrets Source.


## [0.0.15] - 2021-01-12
### Fixed
- ABAP RFC connections cleanup.
- Java connection support.

## [0.0.14] - 2020-12-07
### Added
- Decouple SAP Control Configuration and RFC Calls.
- SAP Control Web Service additional logging.
### Fixed
- Azure Sentinel Secrets in Key Vault.

## [0.0.13] - 2020-12-01
### Added
- Configure User Email extraction using Configuration Generator.
### Fixed
- ABAP Change Documents Log - Support for lower ABAP Backend Versions.

## [0.0.12] - 2020-11-30
### Fixed
- ABAP Change Documents Log - Support for lower ABAP Backend Versions.
- ABAP DB Table Data Log - Support for Non Hana DB and lower ABAP Backend Versions.

## [0.0.11] - 2020-11-20
### Added
- ABAP Audit Log - Support SAL Interface - Provides additional data such as Terminal, IPv6, Transaction Code.
### Fixed
- Initialization Messages

## [0.0.10] - 2020-10-20
### Added
- Configuration Generator Menu
- Azure Key Vault Support for Credentials

## [0.0.9] - 2020-09-24
### Added
- Docker Secret Support for Credentials
- Docker Runtime Environment Variables Support for Credentials

## [0.0.8] - 2020-08-25

### Fixed
- ABAP Job Log Performance
- ABAP DB Table Data Log compatability issues

## [0.0.7] - 2020-08-13

### Added
- ABAP CR Log
- ABAP DB Table Data Log

## [0.0.6] - 2020-08-06

### Added
- ABAP Workflow Log
- Configuration for Logs Activation

### Fixed
- Time offset for non UTC backend ABAP systems

## [0.0.5] - 2020-07-30

### Added
- ABAP Job Log
- ABAP Spool and Spool Output Log
- ABAP Change Documents Log
- ABAP Application Log
- ABAP WorkProcess
- ABAP GW Logs
- JAVA Application
- JAVA System (cluster and server process)
- JAVA Performance
- JAVA Gateway
- JAVA Developer Traces
- JAVA DefaultTrace

## [0.0.4] - 2020-07-14

### Added
- SysLog System information
- Delta Fix in ABAP Audit Log
- ICM Log

## [0.0.3] - 2020-07-02

### Added
- ABAP Audit Log Filtering
- SOAP Certificate
- ABAP X509 Certificate

## [0.0.2] - 2020-06-20

### Added
- README

### Fixed
- Filter messages for Sentinel ABAP Backend user Audit Log 

## [0.0.1] - 2020-06-02

### Added
- Delta Management
- API Failover

[0.0.8]: ./
[0.0.7]: ./
[0.0.6]: ./
[0.0.5]: ./
[0.0.4]: ./
[0.0.3]: ./
[0.0.2]: ./
[0.0.1]: ./

[PreviewTerms]: https://azure.microsoft.com/en-us/support/legal/preview-supplemental-terms/