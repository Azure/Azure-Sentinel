# Required SAP Log change requests

The following table lists the SAP Log change requests that you must configure in order to support ingesting specific SAP logs into Azure Sentinel.
   
   For a typical installation on SAP Basis 7.5+  install *NPLK900202*
   
   For a typical installation on SAP Basis 7.4  install *NPLK900201*
   
   For the role creation (any version) install *NPLK900271* or loading the role authorizations from the [MSFTSEN_SENTINEL_CONNECTOR_ROLE_V0.0.27.SAP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP/Sample%20Authorizations%20Role%20File/MSFTSEN_SENTINEL_CONNECTOR_ROLE_V0.0.27.SAP) file.

   > **Note:**   
   > Alternatively, you can create a role that has minimal permissions by installing change request *NPLK900268* or loading the role authorizations from the [MSFTSEN_SENTINEL_AGENT_BASIC_ROLE_V0.0.1.SAP](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/SAP/Sample%20Authorizations%20Role%20File/MSFTSEN_SENTINEL_AGENT_BASIC_ROLE_V0.0.1.SAP) file.
   > This change request or authorizations file creates the **/MSFTSEN/SENTINEL_AGENT_BASIC** role. This role has the minimal required permissions for the data connector to operate. Note that if you choose to deploy this role, you might need to update it frequently.

<u><b>SAP notes required for version below SAP Basis 7.5 SP13:</u></b>

[SAP Note 2641084](https://launchpad.support.sap.com/#/notes/2641084) (*Standardized read access for the Security Audit log data*)

[SAP Note 2173545](https://launchpad.support.sap.com/#/notes/2173545) (*CD: CHANGEDOCUMENT_READ_ALL*)

[SAP Note 2502336](https://launchpad.support.sap.com/#/notes/2502336) (*CD: RSSCD100 - read only from archive, not from database*)

**Note**: The required SAP log change requests expose custom RFC FMs that are required for the connector, and do not change any standard or custom objects.


| Log | Change Request | Latest Update in Version  | 
| --- | -------------- | -------------------------- |
| **All Logs** | NPLK900202 | 0.0.26 <br> <br>Use the complete package<br> <br>Basis>=7.5 |
| **All Logs** | NPLK900201 | 0.0.26 <br> <br>Use the complete package<br> <br>Basis<7.5 |
| **Sample Authorizations Role** | NPLK900271 | 0.0.27 | 
| **Sample Authorizations Role that has minimal permissions** | NPLK900268 | 0.0.1 |

# How do I remove the user role and the optional CR deployed on my ABAP system?

To remove the user role and optional CR imported to your system, import the deletion CR NPLK900259 into your ABAP system.