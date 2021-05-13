# Supported SAP logs reference

This article lists the SAP logs supported by the Azure Sentinel SAP logs connector, together with any details and documentation links available.


**Copyright (c) Microsoft Corporation**.  This preview software is Microsoft Confidential, and is subject to your Non-Disclosure Agreement with Microsoft.  You may use this preview software internally and only in accordance with the Azure preview terms, located at [Preview terms](https://azure.microsoft.com/support/legal/preview-supplemental-terms/).  Microsoft reserves all other rights.


Log | Backend (OP/Cloud Hosted) | Documentation / References | Client Specific / Cross Client |
--- | ------- | -------------  | -----|
| **ABAP Security Audit Log** | R/3 4.6C -> S/4 | [NW RFC][rfcnote], [XAL][sapdocxal] | Cross Client |
| **ABAP Security Audit Log - SAL** | SAP_BASIS >= 750 , Connector CR, SAL Note | [NW RFC][rfcnote], [SAL][auditlogsalnote] | Cross Client |
| **ABAP Change Documents Log** | ECC 5 -> S/4, SAP_BASIS >= 700, Connector CR, Change Docs Note | [NW RFC][rfcnote],[Change Docs Note 1][cdocnote], [Change Docs Note 2][cdocnote2] | Client Specific |
| **ABAP Spool Log** | R/3 4.6C -> S/4, Connector CR | [NW RFC][rfcnote] | Cross Client |
| **ABAP Spool Output Log** | R/3 4.6C -> S/4, Connector CR | [NW RFC][rfcnote] | Cross Client |
| **ABAP Job Log** | ECC 5 -> S/4, SAP_BASIS >= 700, Connector CR| [NW RFC][rfcnote], [XBP 3.0][sapdocxbp3] | Cross Client |
| **ABAP Application Log** | ECC 5 -> S/4 , SAP_BASIS >= 700, Connector CR| [NW RFC][rfcnote], [XBP 3.0][sapdocxbp3] | Client Specific |
| **ABAP Workflow Log** | R/3 4.6C -> S/4 , SAP_BASIS >= 600, Connector CR| [NW RFC][rfcnote] | Client Specific |
| **ABAP CR Log** | R/3 4.6C -> S/4 , Connector CR| [NW RFC][rfcnote] | Cross Client |
| **ABAP DB Table Data Log** | R/3 4.6C -> S/4, Connector CR, Unicode| [NW RFC][rfcnote] | Cross Client |
| **ABAP SysLog** | ECC 5 -> S/4 | [SAP Control Web Service][sapctlws] | Cross Client |
| **ABAP ICM Log** | ECC 5 -> S/4 | [SAP Control Web Service][sapctlws] | Cross Client |
| **ABAP WorkProcess Log** | ECC 5 -> S/4 | [SAP Control Web Service][sapctlws] | Cross Client |
| **ABAP Gateway Log** | ECC 5 -> S/4 | [SAP Control Web Service][sapctlws] | Cross Client |
| **ABAP ICM Log** | ECC 5 -> S/4 | [SAP Control Web Service][sapctlws]   | Cross Client |
| **JAVA Application** | NW >= 700, Rev 96 | [SAP Control Web Service][sapctlws] | Cross Client |
| **JAVA System (cluster and server process)** | NW >= 700, Rev 96 | [SAP Control Web Service][sapctlws]  | Cross Client |
| **JAVA Performance** | NW >= 700, Rev 96 | [SAP Control Web Service][sapctlws]  | Cross Client |
| **JAVA Gateway** | NW >= 700, Rev 96 | [SAP Control Web Service][sapctlws] | Cross Client |
| **JAVA Developer Traces** | NW >= 700, Rev 96 | [SAP Control Web Service][sapctlws] | Cross Client |
| **JAVA DefaultTrace** | NW >= 700, Rev 96 | [SAP Control Web Service][sapctlws] | Cross Client |

**Note**:

When using the XBP 3.0 interface, the Azure Sentinel SAP Logs connector uses *Not Released* services. These services do not affect backend system or connector behavior.

To "release" these services, implement the following SAP note in the backend: [SAP Note 2910263 - Unreleased XBP functions][xbp3note]

**See also**:

- [Azure Sentinel SAP Logs Connector - Limited Private Preview](../README.md)
- [Azure Sentinel SAP logs connector requirements](prereqs.md)
- [Deploy the Azure Sentinel SAP logs connector on Azure](deploy-azure.md)
- [Deploy the Azure Sentinel SAP logs connector on-premises](deploy-onprem.md)
- [Configure the Azure Sentinel SAP logs connector](config-gen.md)

[cdocnote]: https://launchpad.support.sap.com/#/notes/2173545
[cdocnote2]: https://launchpad.support.sap.com/#/notes/2502336
[auditlogsalnote]: https://launchpad.support.sap.com/#/notes/2641084
[rfcnote]: https://launchpad.support.sap.com/#/notes/2573790
[sapdocxal]: https://archive.sap.com/documents/docs/DOC-16459
[sapdocxbp3]: https://archive.sap.com/documents/docs/DOC-14201
[xbp3note]: https://launchpad.support.sap.com/#/notes/2910263
[sapctlws]: https://www.sap.com/documents/2016/09/0a40e60d-8b7c-0010-82c7-eda71af511fa.html
[PreviewTerms]: https://azure.microsoft.com/en-us/support/legal/preview-supplemental-terms/
