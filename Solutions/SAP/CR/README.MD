# Required SAP Log change requests

The following table lists the SAP Log change requests that you must configure in order to support ingesting specific SAP logs into Azure Sentinel.
   
   For a typical installation on SAP Basis 7.5+  install NPLK900144
   
   For a typical installation on SAP Basis 7.4  install NPLK900146
   
   For the  role creation (any version) install NPLK900140

<u><b>SAP notes required for version below SAP Basis 7.5 SP13:</u></b>

[SAP Note 2641084](https://launchpad.support.sap.com/#/notes/2641084) (*Standardized read access for the Security Audit log data*)

[SAP Note 2173545](https://launchpad.support.sap.com/#/notes/2173545) (*CD: CHANGEDOCUMENT_READ_ALL*)

[SAP Note 2502336](https://launchpad.support.sap.com/#/notes/2502336) (*CD: RSSCD100 - read only from archive, not from database*)

**Note**: The required SAP log change requests expose custom RFC FMs that are required for the connector, and do not change any standard or custom objects.


| Log | Change Request | Latest Update in Version  | 
| --- | -------------- | -------------------------- |
| **All Logs** | NPLK900144 | 0.0.23 <br> <br>Use the complete package<br> <br>Basis>=7.5 |
| **All Logs** | NPLK900146 | 0.0.23 <br> <br>Use the complete package<br> <br>Basis<7.5 |
| **Sample Authorizations Role** | NPLK900140 | 0.0.23 | 

