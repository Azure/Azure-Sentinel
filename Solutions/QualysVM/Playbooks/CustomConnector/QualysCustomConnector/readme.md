# Qualys VM Logic App Custom Connector

This custom connector connects to Qualys API endpoint to execute actions supported by Qualys and returns back response in xml/json format.

### Authentication methods supported by this connector

* Basic Authentication (Username and Password based)

### Prerequisites to deploy Custom Connector 
- Qualys API Endpoint Url. API endpoint url according to Qualys subscription can be found here [Platform Identification](https://www.qualys.com/platform-identification/).


## Actions supported by Qualys VM Logic App Connector
| **Component** | **Description** |
| --------- | -------------- |
| **Get Portal Details** | It fetches the Qualys Portal Component Versions. |
| **Get Detections By IP** | Get Vulnerability Details for an IP. |
| **Get Asset Details By IP** | Get Details of an Asset. |
| **Add IP For Scanning** | Add a New IP to Asset List for Continuous Scanning by Scanners. |
| **Report Operations** | List, Launch, Fetch and Delete Scan Reports. |
| **VM Scan Operations** | List, Launch and Fetch VM Scan. |
| **Option Profile Operations** | List, Create and Delete Option Profile. |
| **List Scanner Appliances** | List All the Available Scanners. |
| **Scan Report Template Operations** | Create and Delete Scan Report Template. |
| **Dynamic Search List Operations** | List, Create and Delete Dynamic Search Lists. |
| **Search Asset By Criteria** | Get All Assets for Given Criteria. |
| **Asset Count By Criteria** | Get Asset Count for Given Criteria. |


### Deployment Instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    - Connector Name: Enter the custom connector name (e.g. QualysCustomConnector)
    - Service Endpoint: Enter the Qualys API endpoint url (e.g. https://qualysapi.qualys.com). Make sure to prefix with https://.  

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FQualysVM%2FPlaybooks%2FCustomConnector%2FQualysCustomConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FQualysVM%2FPlaybooks%2FCustomConnector%2FQualysCustomConnector%2Fazuredeploy.json) 

#  References
 - [Qualys API Quick Reference](https://www.qualys.com/docs/qualys-api-quick-reference.pdf)
 - [Qualys VM API Guide](https://www.qualys.com/docs/qualys-api-vmpc-user-guide.pdf)
