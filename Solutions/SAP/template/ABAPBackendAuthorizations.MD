# Microsoft SAP Logs Connector - Limited Private Preview

Copyright (c) Microsoft Corporation.  This preview software is Microsoft Confidential, and is subject to your Non-Disclosure Agreement with Microsoft.  You may use this preview software internally and only in accordance with the Azure preview terms, located at [Preview terms][PreviewTerms].  Microsoft reserves all other rights

# ABAP Backend Authorizations
- The following authorizations are required for the backend user: (Sample profile is available under [Template] folder)

Log | Authorization Object | Field | Value
--- | -------------------- | ----- | -----
All RFC | S_RFC | FUGR | /OSP/SYSTEM_TIMEZONE
All RFC | S_RFC | FUGR | ARFC
All RFC | S_RFC | FUGR | STFC
All RFC | S_RFC | FUGR | RFC1
All RFC | S_RFC | FUGR | SDIFRUNTIME
All RFC | S_RFC | FUGR | SMOI
All RFC | S_RFC | FUGR | SYST
All RFC | S_RFC | FUGR/FUNC | SRFC/RFC_SYSTEM_INFO
All RFC | S_RFC | FUGR/FUNC | THFB/TH_SERVER_LIST
All RFC | S_TCODE | TCD | SM51
ABAP Application Log | S_APPL_LOG | ACTVT | 03
ABAP Application Log | S_APPL_LOG | ALG_OBJECT | *
ABAP Application Log | S_APPL_LOG | ALG_SUBOBJ | *
ABAP Application Log | S_RFC | FUGR | SXBP_EXT
ABAP Application Log | S_RFC | FUGR | /MSFTSEN/SENTINEL_APPLOG  
ABAP Change Documents Log | S_RFC | FUGR | /MSFTSEN/SENTINEL_CHANGE_DOCS
ABAP Change Documents Log | S_SCD0_OBJ | ACTVT | 08
ABAP Change Documents Log | S_SCD0_OBJ | OBJECT | *
ABAP CR Log | S_RFC | FUGR | CTS_API
ABAP CR Log | S_RFC | FUGR | /MSFTSEN/SENTINEL_CR
ABAP CR Log | S_TRANSPRT | ACTVT | Display
ABAP CR Log | S_TRANSPRT | TTYPE | *
ABAP DB Table Data Log | S_RFC | FUGR | /MSFTSEN/SENTINEL_TD
ABAP DB Table Data Log | S_TABU_DIS | ACTVT | Display
ABAP DB Table Data Log | S_TABU_DIS | DICBERCLS | &NC&
ABAP DB Table Data Log | S_TABU_DIS | DICBERCLS | + Any object required for logging
ABAP DB Table Data Log | S_TABU_NAM | ACTVT | Display
ABAP DB Table Data Log | S_TABU_NAM | TABLE | + Any object required for logging    
ABAP DB Table Data Log | S_TABU_NAM | TABLE | DBTABLOG
ABAP Job Log | S_RFC | FUGR | SXBP
ABAP Job Log | S_RFC | FUGR | /MSFTSEN/SENTINEL_JOBLOG
ABAP Job Log, ABAP Application Log | S_XMI_PROD | INTERFACE | XBP
ABAP Security Audit Log | All RFC | S_RFC | FUGR | SU_USER
ABAP Security Audit Log | S_ADMI_FCD | S_ADMI_FCD | AUDD
ABAP Security Audit Log - XAL | S_RFC | FUGR | SALX
ABAP Security Audit Log - XAL | S_USER_GRP | ACTVT | Display
ABAP Security Audit Log - XAL | S_USER_GRP | CLASS | *
ABAP Security Audit Log - XAL | S_XMI_PROD | INTERFACE | XAL
ABAP Security Audit Log - XAL, ABAP Job Log, ABAP Application Log | S_RFC | FUGR | SXMI
ABAP Security Audit Log - XAL, ABAP Job Log, ABAP Application Log | S_XMI_PROD | EXTCOMPANY | Microsoft
ABAP Security Audit Log - XAL, ABAP Job Log, ABAP Application Log | S_XMI_PROD | EXTPRODUCT | Azure Sentinel
ABAP Security Audit Log - SAL | S_RFC | FUGR | RSAU_LOG
ABAP Security Audit Log - SAL | S_RFC | FUGR | /MSFTSEN/SENTINEL_AUDITLOG
ABAP Spool Log, ABAP Spool Output Log | S_RFC | FUGR | /MSFTSEN/SENTINEL_SPOOL
ABAP Spool Log, ABAP Spool Output Log | S_ADMI_FCD | S_ADMI_FCD | SPOS
ABAP Workflow Log | S_RFC | FUGR | SWRR
ABAP Workflow Log | S_RFC | FUGR | /MSFTSEN/SENTINEL_WF
ABAP Workflow Log | S_WF_WI | WI_TYPE | *
ABAP Workflow Log | S_WF_WI | TASK_CLASS | *
ABAP Workflow Log | S_WF_WI | WFACTVT | 44 Display Log


[PreviewTerms]: https://azure.microsoft.com/en-us/support/legal/preview-supplemental-terms/