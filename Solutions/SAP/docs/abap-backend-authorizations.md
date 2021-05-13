# Required ABAP backend authorizations

The following table lists the ABAP authorizations required for the backend SAP user in order to connect Azure Sentinel to the SAP logs. 

Required authorizations are listed by log type. You only need the authorizations listed for the types of logs you plan to ingest into Azure Sentinel.

To create the role with all required authorizations, deploy the SAP change request S4HK9000862 on your SAP system. This change request creates the **/MSFTSEN/SENTINEL_connector** role, and assigns the role to the ABAP connecting to Azure Sentinel.

**Tip**: You can find a sample user profile in the [Template] folder of this GitHub repository. 

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
ABAP Application Log | S_APPL_LOG | ACTVT | Display
ABAP Application Log | S_APPL_LOG | ALG_OBJECT | *
ABAP Application Log | S_APPL_LOG | ALG_SUBOBJ | *
ABAP Application Log | S_RFC | FUGR | SXBP_EXT
ABAP Application Log | S_RFC | FUGR | /MSFTSEN/SENTINEL_APPLOG  
ABAP Change Documents Log | S_RFC | FUGR | /MSFTSEN/SENTINEL_CHANGE_DOCS
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
ABAP Job Log, ABAP Application Log | S_XMI_PRD | INTERFACE | XBP
ABAP Security Audit Log - XAL | All RFC | S_RFC | FUGR | SU_USER
ABAP Security Audit Log - XAL | S_ADMI_FCD | S_ADMI_FCD | AUDD
ABAP Security Audit Log - XAL | S_RFC | FUGR | SALX
ABAP Security Audit Log - XAL | S_USER_GRP | ACTVT | Display
ABAP Security Audit Log - XAL | S_USER_GRP | CLASS | *
ABAP Security Audit Log - XAL | S_XMI_PRD | INTERFACE | XAL
ABAP Security Audit Log - XAL, ABAP Job Log, ABAP Application Log | S_RFC | FUGR | SXMI
ABAP Security Audit Log - XAL, ABAP Job Log, ABAP Application Log | S_XMI_PRD | EXTCOMPANY | Microsoft
ABAP Security Audit Log - XAL, ABAP Job Log, ABAP Application Log | S_XMI_PRD | EXTPRODUCT | Azure Sentinel
ABAP Security Audit Log - SAL | S_RFC | FUGR | RSAU_LOG
ABAP Security Audit Log - SAL | S_RFC | FUGR | /MSFTSEN/SENTINEL_AUDITLOG
ABAP Spool Log, ABAP Spool Output Log | S_RFC | FUGR | /MSFTSEN/SENTINEL_SPOOL
ABAP Workflow Log | S_RFC | FUGR | SWRR
ABAP Workflow Log | S_RFC | FUGR | /MSFTSEN/SENTINEL_WF
