# Microsoft Azure Sentinel SAP Continuous Threat Monitoring - Limited Private Preview

The Azure Sentinel SAP Logs connector enables you to ingest your SAP logs with your Azure Sentinel workspace and view dashboards, create custom alerts, and improve investigation. 

These benefits provide you with more insight into your organization's network, improving your security operation capabilities. 

The SAP logs connector provides both stateless and stateful connections for logs from the entire SAP system landscape, and collects logs from both ABAP and the OS.

**Note**: Once configured and initialized, SAP logs are retrieved for the configured time span, until the 24 hours before the initialization time.


**Copyright (c) Microsoft Corporation**.  This preview software is Microsoft Confidential, and is subject to your Non-Disclosure Agreement with Microsoft.  You may use this preview software internally and only in accordance with the Azure preview terms, located at [Preview terms][PreviewTerms].  Microsoft reserves all other rights.


## Table of Contents

- [System requirements and prerequisites](docs/prereqs.md)

    - [Required SAP Log change requests](CR/README.MD)
    - [Required ABAP backend authorizations](docs/abap-backend-authorizations.md)

- [Installation guide: Using an Azure VM as the connector and Azure Key Vault for credentials storage](Quick%20Installation%20Guide.docx)

- [Supported SAP logs reference](docs/logs.md)

## Additional Resources

**Release notes**:

[Azure Sentinel SAP logs connector changelog][Changelog]

**SAP documentation**:
- [SAP Documentation - Support and Availability of the SAP NetWeaver RFC Library 7.50][rfcnote]
- [SAP Documentation - XAL Interface Support][sapdocxal]
- [SAP Documentation - XBP Interface Support - XBP 3.0][sapdocxbp3]
- [SAP Note 2173545 - CD: CHANGEDOCUMENT_READ_ALL][cdocnote]
- [SAP Note 2502336 - CD: RSSCD100 - read only from archive, not from database][cdocnote2]
- [SAP Note 2910263 - Unreleased XBP functions][xbp3note]
- [SAP Note 927637 - Web service authentication in sapstartsrv as of Release 7.00][sapsrvauth]


[Template]: ./template
[CR]: ./CR
[sapcon]: ./sapcon
[Initsetup.sh]: ./initsetup.sh
[Initmenu.sh]: ./initmenu.sh
[Changelog]: ./docs/CHANGELOG.md
[LOGS]: ./docs/Logs.MD
[ABAPBackendAuth]: ./docs/ABAPBackendAuthorizations.MD
[config/filter]: ./sapcon/config/filter
[cdocnote]: https://launchpad.support.sap.com/#/notes/2173545
[cdocnote2]: https://launchpad.support.sap.com/#/notes/2502336
[rfcnote]: https://launchpad.support.sap.com/#/notes/2573790
[sapdocxal]: https://archive.sap.com/documents/docs/DOC-16459
[sapdocxbp3]: https://archive.sap.com/documents/docs/DOC-14201
[xbp3note]: https://launchpad.support.sap.com/#/notes/2910263
[sapctlws]: https://www.sap.com/documents/2016/09/0a40e60d-8b7c-0010-82c7-eda71af511fa.html
[sapsrvauth]: https://launchpad.support.sap.com/#/notes/927637
[OnPremDep]: ./docs/OnPrem_Deployment.md
[AzureDep]: ./docs/Azure_Deployment_Support.md
[ConfigGen]: ./docs/ConfigGen.md
[PreviewTerms]: https://azure.microsoft.com/en-us/support/legal/preview-supplemental-terms/
