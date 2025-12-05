# TacitRed Defender Threat Intelligence - Release Notes

## Version 1.0.0

### Initial Release
- Integration with TacitRed threat intelligence feed
- Automated ingestion of compromised credentials into Microsoft Sentinel
- Azure Function App for data retrieval and transformation
- Logic App for orchestration
- Support for STIX 2.1 indicator format
- Upload API integration for threat intelligence ingestion
- Auto-deployment via Content Hub

### Features
- **Automated Threat Intelligence Ingestion**: Retrieves threat indicators from TacitRed API
- **STIX 2.1 Compliant**: Uses official stix2 library for valid indicator format
- **Managed Identity**: Secure authentication using System-Assigned Managed Identity
- **Role-Based Access**: Automatic Microsoft Sentinel Contributor role assignment
- **Scalable Architecture**: Built on Azure Function Apps for high performance

### Requirements
- Microsoft Sentinel workspace
- TacitRed API key
- Azure subscription

### Deployment
- One-click installation via Microsoft Sentinel Content Hub
- All infrastructure automatically deployed via ARM template
