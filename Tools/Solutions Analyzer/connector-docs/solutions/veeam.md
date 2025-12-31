# Veeam

## Solution Information

| Attribute | Value |
|:------------------------|:------|
| **Publisher** | Veeam Software |
| **Support Tier** | Partner |
| **Support Link** | [https://helpcenter.veeam.com/docs/security_plugins_microsoft_sentinel/guide/](https://helpcenter.veeam.com/docs/security_plugins_microsoft_sentinel/guide/) |
| **Categories** | domains |
| **Version** | 3.0.2 |
| **First Published** | 2025-08-26 |
| **Solution Folder** | [https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam) |

## Data Connectors

This solution provides **1 data connector(s)**:

- [Veeam Data Connector (using Azure Functions)](../connectors/veeamcustomtablesdataconnector.md)

## Tables Reference

This solution uses **7 table(s)**:

| Table | Used By Connectors | Used By Content |
|-------|-------------------|----------------|
| [`Syslog`](../tables/syslog.md) | - | Analytics, Workbooks |
| [`VeeamAuthorizationEvents_CL`](../tables/veeamauthorizationevents-cl.md) | [Veeam Data Connector (using Azure Functions)](../connectors/veeamcustomtablesdataconnector.md) | Workbooks |
| [`VeeamCovewareFindings_CL`](../tables/veeamcovewarefindings-cl.md) | [Veeam Data Connector (using Azure Functions)](../connectors/veeamcustomtablesdataconnector.md) | Workbooks |
| [`VeeamMalwareEvents_CL`](../tables/veeammalwareevents-cl.md) | [Veeam Data Connector (using Azure Functions)](../connectors/veeamcustomtablesdataconnector.md) | Analytics, Workbooks |
| [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) | [Veeam Data Connector (using Azure Functions)](../connectors/veeamcustomtablesdataconnector.md) | Analytics, Workbooks |
| [`VeeamSecurityComplianceAnalyzer_CL`](../tables/veeamsecuritycomplianceanalyzer-cl.md) | [Veeam Data Connector (using Azure Functions)](../connectors/veeamcustomtablesdataconnector.md) | Analytics, Workbooks |
| [`VeeamSessions_CL`](../tables/veeamsessions-cl.md) | [Veeam Data Connector (using Azure Functions)](../connectors/veeamcustomtablesdataconnector.md) | Analytics |

## Content Items

This solution includes **164 content item(s)**:

| Content Type | Count |
|:-------------|:------|
| Analytic Rules | 132 |
| Playbooks | 15 |
| Watchlists | 11 |
| Parsers | 4 |
| Workbooks | 2 |

### Analytic Rules

| Name | Severity | Tactics | Tables Used |
|:-----|:---------|:--------|:------------|
| [Adding User or Group Failed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Adding_User_or_Group_Failed.yaml) | Low | - | [`Syslog`](../tables/syslog.md) |
| [Application Group Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Application_Group_Deleted.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Application Group Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Application_Group_Settings_Updated.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Archive Repository Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Archive_Repository_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Archive Repository Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Archive_Repository_Settings_Updated.yaml) | Low | - | [`Syslog`](../tables/syslog.md) |
| [Attempt to Delete Backup Failed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Attempt_to_Delete_Backup_Failed.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Attempt to Update Security Object Failed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Attempt_to_Update_Security_Object_Failed.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Backup Proxy Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Backup_Proxy_Deleted.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Backup Repository Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Backup_Repository_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Backup Repository Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Backup_Repository_Settings_Updated.yaml) | Low | - | [`Syslog`](../tables/syslog.md) |
| [Best Practice Compliance Check Not Passed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Best_Practice_Compliance_Check_Not_Passed.yaml) | Medium | - | [`VeeamSecurityComplianceAnalyzer_CL`](../tables/veeamsecuritycomplianceanalyzer-cl.md) |
| [Cloud Gateway Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Cloud_Gateway_Deleted.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Cloud Gateway Pool Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Cloud_Gateway_Pool_Deleted.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Cloud Gateway Pool Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Cloud_Gateway_Pool_Settings_Updated.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Cloud Gateway Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Cloud_Gateway_Settings_Updated.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Cloud Replica Permanent Failover Performed by Tenant](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Cloud_Replica_Permanent_Failover_Performed_by_Tenant.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Configuration Backup Failed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Configuration_Backup_Failed.yaml) | High | - | [`VeeamSessions_CL`](../tables/veeamsessions-cl.md) |
| [Configuration Backup Job Failed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Configuration_Backup_Job_Failed.yaml) | Medium | - | [`Syslog`](../tables/syslog.md) |
| [Configuration Backup Job Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Configuration_Backup_Job_Settings_Updated.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Connection to Backup Repository Lost](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Connection_to_Backup_Repository_Lost.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Credential Record Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Credential_Record_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Credential Record Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Credential_Record_Updated.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Detaching Backups Started](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Detaching_Backups_Started.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Encryption Password Added](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Encryption_Password_Added.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Encryption Password Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Encryption_Password_Changed.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Encryption Password Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Encryption_Password_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [External Repository Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/External_Repository_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [External Repository Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/External_Repository_Settings_Updated.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Failover Plan Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Failover_Plan_Deleted.yaml) | Low | - | [`Syslog`](../tables/syslog.md) |
| [Failover Plan Failed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Failover_Plan_Failed.yaml) | Low | - | [`Syslog`](../tables/syslog.md) |
| [Failover Plan Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Failover_Plan_Settings_Updated.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Failover Plan Started](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Failover_Plan_Started.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Failover Plan Stopped](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Failover_Plan_Stopped.yaml) | Medium | - | [`Syslog`](../tables/syslog.md) |
| [File Server Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/File_Server_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [File Server Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/File_Server_Settings_Updated.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [File Share Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/File_Share_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Four-Eyes Authorization Disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Four_Eyes_Authorization_Disabled.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Four-Eyes Authorization Request Created](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Four_Eyes_Authorization_Request_Created.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Four-Eyes Authorization Request Expired](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Four_Eyes_Authorization_Request_Expired.yaml) | Medium | - | [`Syslog`](../tables/syslog.md) |
| [Four-Eyes Authorization Request Rejected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Four_Eyes_Authorization_Request_Rejected.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [General Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/General_Settings_Updated.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Global Network Traffic Rules Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Global_Network_Traffic_Rules_Deleted.yaml) | Low | - | [`Syslog`](../tables/syslog.md) |
| [Global VM Exclusions Added](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Global_VM_Exclusions_Added.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Global VM Exclusions Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Global_VM_Exclusions_Changed.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Global VM Exclusions Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Global_VM_Exclusions_Deleted.yaml) | Low | - | [`Syslog`](../tables/syslog.md) |
| [Host Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Host_Deleted.yaml) | Low | - | [`Syslog`](../tables/syslog.md) |
| [Host Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Host_Settings_Updated.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Hypervisor Host Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Hypervisor_Host_Deleted.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Hypervisor Host Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Hypervisor_Host_Settings_Updated.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Invalid Code for Multi-Factor Authentication Entered](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Invalid_Code_for_Multi_Factor_Authentication_Entered.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Job Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Job_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Job No Longer Used as Second Destination](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Job_No_Longer_Used_as_Second_Destination.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [KMS Key Rotation Job Finished](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/KMS_Key_Rotation_Job_Finished.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [KMS Server Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/KMS_Server_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [KMS Server Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/KMS_Server_Settings_Updated.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [License Expired](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/License_Expired.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [License Expiring](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/License_Expiring.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [License Grace Period Started](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/License_Grace_Period_Started.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [License Limit Exceeded](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/License_Limit_Exceeded.yaml) | Medium | - | [`Syslog`](../tables/syslog.md) |
| [License Removed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/License_Removed.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [License Support Expired](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/License_Support_Expired.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [License Support Expiring](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/License_Support_Expiring.yaml) | Low | - | [`Syslog`](../tables/syslog.md) |
| [Malware Activity Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Malware_Activity_Detected.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Malware Detection Exclusions List Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Malware_Detection_Exclusions_List_Updated.yaml) | Medium | - | [`Syslog`](../tables/syslog.md) |
| [Malware Detection Session Finished](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Malware_Detection_Session_Finished.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Malware Detection Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Malware_Detection_Settings_Updated.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Malware Event Detected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Malware_Event_Detected.yaml) | Medium | - | [`VeeamMalwareEvents_CL`](../tables/veeammalwareevents-cl.md) |
| [Multi-Factor Authentication Disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Multi_Factor_Authentication_Disabled.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Multi-Factor Authentication Token Revoked](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Multi_Factor_Authentication_Token_Revoked.yaml) | Medium | - | [`Syslog`](../tables/syslog.md) |
| [Multi-Factor Authentication User Locked](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Multi_Factor_Authentication_User_Locked.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Multi-Factor Authentication for User Disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Multi_Factor_Authentication_for_User_Disabled.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [NDMP Server Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/NDMP_Server_Deleted.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Object Marked as Clean](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Object_Marked_as_Clean.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Object Storage Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Object_Storage_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Object Storage Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Object_Storage_Settings_Updated.yaml) | Low | - | [`Syslog`](../tables/syslog.md) |
| [Objects Added to Malware Detection Exclusions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Objects_Added_to_Malware_Detection_Exclusions.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Objects Deleted from Malware Detection Exclusions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Objects_Deleted_from_Malware_Detection_Exclusions.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Objects for Job Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Objects_for_Job_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Objects for Protection Group Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Objects_for_Protection_Group_Changed.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Objects for Protection Group Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Objects_for_Protection_Group_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Preferred Networks Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Preferred_Networks_Deleted.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Protection Group Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Protection_Group_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Protection Group Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Protection_Group_Settings_Updated.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Recovery Token Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Recovery_Token_Deleted.yaml) | Low | - | [`Syslog`](../tables/syslog.md) |
| [Restore Point Marked as Clean](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Restore_Point_Marked_as_Clean.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Restore Point Marked as Infected](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Restore_Point_Marked_as_Infected.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [SSH Credentials Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/SSH_Credentials_Changed.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Scale-Out Backup Repository Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Scale_Out_Backup_Repository_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Scale-Out Backup Repository Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Scale_Out_Backup_Repository_Settings_Updated.yaml) | Low | - | [`Syslog`](../tables/syslog.md) |
| [Service Provider Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Service_Provider_Deleted.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Service Provider Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Service_Provider_Updated.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Storage Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Storage_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Storage Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Storage_Settings_Updated.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Subtenant Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Subtenant_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Subtenant Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Subtenant_Updated.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [SureBackup Job Failed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/SureBackup_Job_Failed.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Tape Erase Job Started](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Tape_Erase_Job_Started.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Tape Library Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Tape_Library_Deleted.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Tape Media Pool Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Tape_Media_Pool_Deleted.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Tape Media Vault Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Tape_Media_Vault_Deleted.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Tape Medium Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Tape_Medium_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Tape Server Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Tape_Server_Deleted.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Tenant Password Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Tenant_Password_Changed.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Tenant Quota Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Tenant_Quota_Changed.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Tenant Quota Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Tenant_Quota_Deleted.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Tenant Replica Started](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Tenant_Replica_Started.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [Tenant Replica Stopped](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Tenant_Replica_Stopped.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Tenant State Changed](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Tenant_State_Changed.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [User or Group Added](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/User_or_Group_Added.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [User or Group Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/User_or_Group_Deleted.yaml) | High | - | [`Syslog`](../tables/syslog.md) |
| [Veeam ONE Application with No Recent Data Backup Sessions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_Application_with_no_recent_data_backup_sessions.yaml) | High | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Veeam ONE Backup Copy RPO](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_Backup_Copy_RPO.yaml) | High | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Veeam ONE Backup Server Security and Compliance State](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_Backup_server_security_%26_compliance_state.yaml) | Medium | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Veeam ONE Computer with No Backup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_Computer_with_no_backup.yaml) | High | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Veeam ONE Immutability Change Tracking](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_Immutability_change_tracking.yaml) | Medium | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Veeam ONE Immutability State](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_Immutability_state.yaml) | Medium | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Veeam ONE Job Disabled](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_Job_disabled.yaml) | Medium | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Veeam ONE Job Disabled (Veeam Backup for Microsoft 365)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_Job_disabled_Veeam_Backup_for_Microsoft_365.yaml) | Medium | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Veeam ONE Malware Detection Change Tracking](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_Veeam_malware_detection_change_tracking.yaml) | High | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Veeam ONE Possible Ransomware Activity (Hyper-V)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_Possible_ransomware_activity_Hyper_V.yaml) | High | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Veeam ONE Possible Ransomware Activity (vSphere)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_Possible_ransomware_activity_vSphere.yaml) | High | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Veeam ONE Suspicious Incremental Backup Size](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_Suspicious_incremental_backup_size.yaml) | High | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Veeam ONE Unusual Job Duration](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_Unusual_job_duration.yaml) | Medium | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Veeam ONE Unusual Job Duration (Veeam Backup for Microsoft 365)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_Unusual_job_duration_Veeam_Backup_for_Microsoft_365.yaml) | Medium | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Veeam ONE VM with No Backup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_VM_with_no_backup.yaml) | High | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Veeam ONE VM with No Backup (Hyper-V)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_VM_with_no_backup_Hyper_V.yaml) | High | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Veeam ONE VM with No Replica](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_VM_with_no_replica.yaml) | High | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Veeam ONE VM with No Replica (Hyper-V)](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Veeam_One_VM_with_no_replica_Hyper_V.yaml) | High | - | [`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md) |
| [Virtual Lab Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Virtual_Lab_Deleted.yaml) | Low | - | [`Syslog`](../tables/syslog.md) |
| [Virtual Lab Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/Virtual_Lab_Settings_Updated.yaml) | Low | - | [`Syslog`](../tables/syslog.md) |
| [WAN Accelerator Deleted](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/WAN_Accelerator_Deleted.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |
| [WAN Accelerator Settings Updated](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Analytic%20Rules/WAN_Accelerator_Settings_Updated.yaml) | Informational | - | [`Syslog`](../tables/syslog.md) |

### Workbooks

| Name | Tables Used |
|:-----|:------------|
| [VeeamDataPlatformMonitoring](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Workbooks/VeeamDataPlatformMonitoring.json) | [`Syslog`](../tables/syslog.md) |
| [VeeamSecurityActivities](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Workbooks/VeeamSecurityActivities.json) | [`Syslog`](../tables/syslog.md)<br>[`VeeamAuthorizationEvents_CL`](../tables/veeamauthorizationevents-cl.md)<br>[`VeeamCovewareFindings_CL`](../tables/veeamcovewarefindings-cl.md)<br>[`VeeamMalwareEvents_CL`](../tables/veeammalwareevents-cl.md)<br>[`VeeamOneTriggeredAlarms_CL`](../tables/veeamonetriggeredalarms-cl.md)<br>[`VeeamSecurityComplianceAnalyzer_CL`](../tables/veeamsecuritycomplianceanalyzer-cl.md) |

### Playbooks

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Veeam-ChangeCollectionTime](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Playbooks/Veeam-ChangeCollectionTime/ChangeCollectionTime.json) | This Microsoft Sentinel playbook adjusts the recurrence intervals for Veeam collection playbooks bas... | - |
| [Veeam-CollectConfigurationBackups](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Playbooks/Veeam-CollectConfigurationBackups/Veeam-CollectConfigurationBackups.json) | A Microsoft Sentinel playbook that automatically runs configuration backup sessions on Veeam Backup ... | - |
| [Veeam-CollectCovewareFindings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Playbooks/Veeam-CollectCovewareFindings/CollectCovewareFindingsPlaybook.json) | This Microsoft Sentinel playbook automatically collects Coveware findings on a schedule. Retrieves C... | - |
| [Veeam-CollectMalwareEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Playbooks/Veeam-CollectMalwareEvents/CollectMalwareEventsPlaybook.json) | A Microsoft Sentinel playbook that automatically collects malware events from Veeam Backup & Replica... | - |
| [Veeam-CollectSecurityComplianceAnalyzerResult](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Playbooks/Veeam-CollectSecurityComplianceAnalyzerResult/Veeam-CollectSecurityComplianceAnalyzerResult.json) | A Microsoft Sentinel playbook that automatically collects Veeam Security Compliance Analyzer results... | - |
| [Veeam-CollectVeeamAuthorizationEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Playbooks/Veeam-CollectVeeamAuthorizationEvents/CollectVeeamAuthorizationEventsPlaybook.json) | This Microsoft Sentinel playbook automatically collects Veeam authorization events Veeam Backup & Re... | - |
| [Veeam-CollectVeeamONEAlarms](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Playbooks/Veeam-CollectVoneAlarms/CollectVoneAlarmsPlaybook.json) | This Microsoft Sentinel playbook automatically collects Veeam ONE alarms on a schedule. Retrieves Ve... | - |
| [Veeam-FindCleanRestorePoints](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Playbooks/Veeam-FindCleanRestorePoints/FindCleanRestorePoints.json) | A Microsoft Sentinel playbook with the incident trigger, that finds the last clean restore point for... | - |
| [Veeam-PerformConfigurationBackupOnIncident](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Playbooks/Veeam-PerformConfigurationBackupOnIncident/Veeam-PerformConfigurationBackupOnIncident.json) | A Microsoft Sentinel playbook that automatically runs configuration backup session when triggered by... | - |
| [Veeam-PerformInstantVMRecovery](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Playbooks/Veeam-PerformInstantVMRecovery/PerformInstantVMRecovery.json) | This Microsoft Sentinel playbook performs instant VM recovery on the vm specified by MachineDisplayN... | - |
| [Veeam-PerformScanBackup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Playbooks/Veeam-PerformScanBackup/PerformScanBackup.json) | This Microsoft Sentinel playbook with an incident trigger performs antivirus scan on Veeam backup us... | - |
| [Veeam-ResolveTriggeredAlarm](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Playbooks/Veeam-ResolveTriggeredAlarm/ResolveTriggeredAlarm.json) | A Microsoft Sentinel playbook with an incident trigger that resolves Veeam ONE alarms (identified by... | - |
| [Veeam-SetupConnections](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Playbooks/Veeam-SetupConnectionsPlaybook/SetupConnectionsPlaybook.json) | A Microsoft Sentinel playbook that configures Key Vault secrets and hybrid connections for Veeam ser... | - |
| [Veeam-StartQuickBackup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Playbooks/Veeam-StartQuickBackup/StartQuickBackup.json) | A Microsoft Sentinel playbook with an incident trigger, that performs quick backup support for affec... | - |
| [Veeam-StartSecurityComplianceAnalyzer](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Playbooks/Veeam-StartSecurityComplianceAnalyzer/Veeam-StartSecurityComplianceAnalyzer.json) | This Microsoft Sentinel playbook initiates and monitors Veeam Security and Compliance Analyzer sessi... | - |

### Parsers

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [Veeam_GetFinishedConfigurationBackupSessions](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Parsers/Veeam_GetFinishedConfigurationBackupSessions.yaml) | - | - |
| [Veeam_GetJobFinished](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Parsers/Veeam_GetJobFinished.yaml) | - | - |
| [Veeam_GetSecurityEvents](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Parsers/Veeam_GetSecurityEvents.yaml) | - | - |
| [Veeam_GetVeeamONEAlarms](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Parsers/Veeam_GetVeeamONEAlarms.yaml) | - | - |

### Watchlists

| Name | Description | Tables Used |
|:-----|:------------|:------------|
| [action_results_lookup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Watchlists/action_results_lookup.json) | - | - |
| [collection_schedule_settings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Watchlists/collection_schedule_settings.json) | - | - |
| [coveware_settings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Watchlists/coveware_settings.json) | - | - |
| [job_types_lookup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Watchlists/job_types_lookup.json) | - | - |
| [license_editions_lookup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Watchlists/license_editions_lookup.json) | - | - |
| [license_types_lookup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Watchlists/license_types_lookup.json) | - | - |
| [operation_names_lookup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Watchlists/operation_names_lookup.json) | - | - |
| [session_states_lookup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Watchlists/session_states_lookup.json) | - | - |
| [vbr_events_lookup](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Watchlists/vbr_events_lookup.json) | - | - |
| [vbr_settings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Watchlists/vbr_settings.json) | - | - |
| [vone_settings](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Veeam/Watchlists/vone_settings.json) | - | - |

## Release Notes

| **Version** | **Date Modified (DD-MM-YYYY)** | **Change History**                                                                  |
|-------------|--------------------------------|-------------------------------------------------------------------------------------|
| 3.0.2       | 15-10-2025                     | Updated author to Veeam Software                                                   |
| 3.0.1       | 03-10-2025                     | Updated Coveware security findings integration; Removed irrelevant mappings from all analytic rules; Updated Workbooks' drilldown capabilities |
| 3.0.0       | 26-08-2025                     | Initial Solution Release                                                            |

---

**Browse:**

- [← Back to Solutions Index](../solutions-index.md)
- [Connectors Index](../connectors-index.md)
- [Tables Index](../tables-index.md)
