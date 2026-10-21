| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                 |
|-------------|--------------------------------|--------------------------------------------------------------------|
| 3.2.2       | 19-10-2026                     | Restored `DeployParser` parameter and `Parser` resource deployment condition for the two workspace function **Parsers** alongside the seven disabled **Defender XDR Custom Detections** and two **Defender Workbooks** so Content Hub installation and multi-workspace deployment succeed. |
| 3.2.1       | 14-10-2026                     | Added seven disabled **Defender XDR Custom Detections**, including an hourly (`PT1H`) scheduled approximation of the source NRT mining-pool rule with unspecified engine-managed lookback, and two converted **Defender Workbooks** with mandatory workspace-function dependencies for the Syslog overview. Offline content validation passed; runtime, NRT parity, workbook UI and provider acceptance remain unverified. |
| 3.1.2       | 12-10-2026                     |  Added seven disabled **Defender XDR Custom Detections** converted from Syslog **Analytic Rules**, with source provenance. Offline structural validation passed; runtime validation was not performed.  |
| 3.0.7       | 04-11-2024                     |  Updated the Syslog **Data Connector** template to latest version  |
| 3.0.6       | 01-08-2024                     |  Updated **Analytic rules** for entity mappings and parameter for parser function  |
| 3.0.5       | 16-07-2024                     |  Added 2 new Workspace Function **Parsers** and a new **Workbook**       |
| 3.0.4       | 27-06-2024                     |  Updated Connectivity criteria query for **Data Connector**        |
| 3.0.3       | 10-04-2024                     |  Updated Entity Mappings **Analytic Rule** FailedLogonAttempts_UnknownUser.yaml    |
| 3.0.2       | 21-02-2024                     |  Addition of new Syslog AMA **Data Connector**                     |
| 3.0.1       | 01-02-2024                     |  **Hunting Queries** Description updated                           |                                                                                                                                 
