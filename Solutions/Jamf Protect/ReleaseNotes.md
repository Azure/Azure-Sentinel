| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                          |
|-------------|--------------------------------|---------------------------------------------|
|3.3.0        | 02-09-2025                     | Adding support for newly added event types in Telemetry, TCC_MODIFY,NETWORK_CONNECT, PTY_GRANT, PTY_CLOSE and some enhancements to mount and process object mapping.
|3.2.4        | 27-03-2025                     | Resolving issues related to the new Push Connector and the DCE/DCRs. Removing support for Telemetry Legacy in this newer Push Connector. Removing Hunting Queries as they were not relevant anymore. Updated Analytic Rules and Workbooks to work with the updated parsers, the single parser got split up to be more useful to customers that only use certain features. 
|3.2.1        | 24-02-2025                     | Adding support for the newly released `gatekeeper_user_override` event and removing totalRetentionInDays from the Push Connector.
| 3.2.0       | 04-02-2025                     | Added new CCP **Data Connector** to the Solution.
| 3.1.1       | 30-04-2024                     | Repackaged for parser issue fix while reinstall.
| 3.1.0       | 12-01-2024                     | Improved data normalization in the parser JamfProtect, ParentProcess is better mapped now, productVersion has been added and more. Added new macOS Hunting Queries including recent malware IOCs.
| 3.0.1       | 05-12-2023                     | Minor tweak to parser related to signerType
| 3.0.0       | 20-10-2023                     | Added **Parser** for parsing jamfprotect_CL raw logs.
|             |                                | Modified existing **Analytic Rules** & **Workbooks** to make use of newly added parser in this release.
|             |                                | Added macOS Threat Hunting **Hunting Queries** for hunting macOS specific threats retrospectivly
|             |                                | Added **Playbooks** for interacting with the Jamf Protect and Jamf Pro API's, including Remote Locking a computer, and changes Alert statusses based on a Microsoft Sentinel incident. 
| 2.1.1       | 03-03-2023                     | Updating **Analytic Rules** to include MITRE Tactics and Techniques.
| 2.1.0       | 10-02-2023                     | Added **Data Connector** for monitoring logs
|             |                                | Added **Analytics Rules** for automated incident creation within Microsoft Sentinel
|             |                                | Improved **Workbook** and added Endpoint Telemetry
| 2.0.0       | 12-10-2022                     | Initial Solution Release |
