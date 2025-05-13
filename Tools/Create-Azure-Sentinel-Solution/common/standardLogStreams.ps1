# Standard Tables in Microsoft Sentinel mapping for Scuba and Streams.
$standardStreamMapping = @()

  # key is the Data connector poller StreamName and value is the DCR file streamName
  # Example: For GCP audit, data connector poller file, 'StreamName' should be 'SENTINEL_GCP_AUDIT_LOGS' and in dcr file 'stream' should be 'Microsoft-GCPAuditLogs' which is your standard table name. Here SENTINEL_GCP_AUDIT_LOGS is used for Scuba.

$standardStreamMapping += @{ Key = 'SAP_ABAPAUDITLOG'; Value = 'Microsoft-ABAPAuditLog'}
$standardStreamMapping += @{ Key = 'SECURITY_ALERT_DATA'; Value = 'Microsoft-SecurityAlert'}
$standardStreamMapping += @{ Key = 'SENTINEL_SECURITY_ALERT_DATA'; Value = 'Microsoft-SecurityAlert'}
$standardStreamMapping += @{ Key = 'LINUX_NAGIOSALERTS_BLOB'; Value = 'Microsoft-Alert'}
$standardStreamMapping += @{ Key = 'OMSALERTS_BLOB'; Value = 'Microsoft-Alert'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGALERTEVIDENCE'; Value = 'Microsoft-AlertEvidence'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGALERTINFO'; Value = 'Microsoft-AlertInfo'}
$standardStreamMapping += @{ Key = 'SENTINEL_ANOMALIES'; Value = 'Microsoft-Anomalies'}
$standardStreamMapping += @{ Key = 'APP_CENTER_ERROR_DATA'; Value = 'Microsoft-AppCenterError'}
$standardStreamMapping += @{ Key = 'SENTINEL_AUDIT_EVENTS'; Value = 'Microsoft-ASimAuditEventLogs'}
$standardStreamMapping += @{ Key = 'SENTINEL_AUTHENTICATION_EVENTS'; Value = 'Microsoft-ASimAuthenticationEventLogs'}
$standardStreamMapping += @{ Key = 'SENTINEL_DHCP_EVENTS'; Value = 'Microsoft-ASimDhcpEventLogs'}
$standardStreamMapping += @{ Key = 'SENTINEL_WINDOWS_DNS_EVENTS'; Value = 'Microsoft-ASimDnsActivityLogs'}
$standardStreamMapping += @{ Key = 'SENTINEL_FILE_EVENT_LOGS'; Value = 'Microsoft-ASimFileEventLogs'}
$standardStreamMapping += @{ Key = 'SENTINEL_NETWORK_SESSION_NORMALIZED'; Value = 'Microsoft-ASimNetworkSessionLogs'}
$standardStreamMapping += @{ Key = 'SENTINEL_NETWORK_SESSION_WINDOWS_FIREWALL_AMA'; Value = 'Microsoft-ASimNetworkSessionLogs'}
$standardStreamMapping += @{ Key = 'SENTINEL_PROCESS_EVENTS'; Value = 'Microsoft-ASimProcessEventLogs'}
$standardStreamMapping += @{ Key = 'SENTINEL_REGISTRY_EVENTS'; Value = 'Microsoft-ASimRegistryEventLogs'}
$standardStreamMapping += @{ Key = 'SENTINEL_USER_MANAGEMENT_ACTIVITY_LOGS'; Value = 'Microsoft-ASimUserManagementActivityLogs'}
$standardStreamMapping += @{ Key = 'SENTINEL_WEB_SESSION_LOGS'; Value = 'Microsoft-ASimWebSessionLogs'}
$standardStreamMapping += @{ Key = 'SENTINEL_AWSCLOUDTRAIL'; Value = 'Microsoft-AWSCloudTrail'}
$standardStreamMapping += @{ Key = 'SENTINEL_AWSCLOUDWATCH'; Value = 'Microsoft-AWSCloudWatch'}
$standardStreamMapping += @{ Key = 'SENTINEL_AWSGUARDDUTY'; Value = 'Microsoft-AWSGuardDuty'}
$standardStreamMapping += @{ Key = 'SENTINEL_AWSVPCFLOW'; Value = 'Microsoft-AWSVPCFlow'}
$standardStreamMapping += @{ Key = 'SENTINEL_AWSWAF'; Value = 'Microsoft-AWSWAF'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGCLOUDAPPEVENTS'; Value = 'Microsoft-CloudAppEvents'}
$standardStreamMapping += @{ Key = 'SECURITY_CISCO_ASA_BLOB'; Value = 'Microsoft-CommonSecurityLog'}
$standardStreamMapping += @{ Key = 'SECURITY_CEF_BLOB'; Value = 'Microsoft-CommonSecurityLog'}
$standardStreamMapping += @{ Key = 'COMPUTER_GROUP_BLOB'; Value = 'Microsoft-ComputerGroup'}
$standardStreamMapping += @{ Key = 'SENTINEL_WATCHLIST'; Value = 'Microsoft-Watchlist'}
$standardStreamMapping += @{ Key = 'OFFICEDATAVERSE_RESTAPI'; Value = 'Microsoft-DataverseActivity'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGDEVICEEVENTS'; Value = 'Microsoft-DeviceEvents'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGDEVICEFILECERTIFICATEINFO'; Value = 'Microsoft-DeviceFileCertificateInfo'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGDEVICEFILEEVENTS'; Value = 'Microsoft-DeviceFileEvents'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGDEVICEIMAGELOADEVENTS'; Value = 'Microsoft-DeviceImageLoadEvents'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGDEVICEINFO'; Value = 'Microsoft-DeviceInfo'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGDEVICELOGONEVENTS'; Value = 'Microsoft-DeviceLogonEvents'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGDEVICENETWORKEVENTS'; Value = 'Microsoft-DeviceNetworkEvents'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGDEVICENETWORKINFO'; Value = 'Microsoft-DeviceNetworkInfo'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGDEVICEPROCESSEVENTS'; Value = 'Microsoft-DeviceProcessEvents'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGDEVICEREGISTRYEVENTS'; Value = 'Microsoft-DeviceRegistryEvents'}
$standardStreamMapping += @{ Key = 'TVM_DEVICETVMSECURECONFIGURATIONASSESSMENT'; Value = 'Microsoft-DeviceTvmSecureConfigurationAssessment'}
$standardStreamMapping += @{ Key = 'TVM_DEVICETVMSECURECONFIGURATIONASSESSMENT_KB'; Value = 'Microsoft-DeviceTvmSecureConfigurationAssessmentKB'}
$standardStreamMapping += @{ Key = 'TVM_DEVICETVMSOFTWAREINVENTORY'; Value = 'Microsoft-DeviceTvmSoftwareInventory'}
$standardStreamMapping += @{ Key = 'TVM_DEVICETVMSOFTWAREVULNERABILITIES'; Value = 'Microsoft-DeviceTvmSoftwareVulnerabilities'}
$standardStreamMapping += @{ Key = 'TVM_DEVICETVMSOFTWAREVULNERABILITIES_KB'; Value = 'Microsoft-DeviceTvmSoftwareVulnerabilitiesKB'}
$standardStreamMapping += @{ Key = 'SENTINEL_WINDOWS_DNS_AUDIT_EVENTS'; Value = 'Microsoft-DnsAuditEvents'}
$standardStreamMapping += @{ Key = 'DNS_ANALYTICS_BLOB'; Value = 'Microsoft-DnsEvents'}
$standardStreamMapping += @{ Key = 'DNS_AUDIT_BLOB'; Value = 'Microsoft-DnsEvents'}
$standardStreamMapping += @{ Key = 'DNS_DYNAMIC_BLOB'; Value = 'Microsoft-DnsEvents'}
$standardStreamMapping += @{ Key = 'DNS_INVENTORY_BLOB'; Value = 'Microsoft-DnsInventory'}
$standardStreamMapping += @{ Key = 'DYNAMICS365_ACTIVITY_RESTAPI'; Value = 'Microsoft-Dynamics365Activity'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGEMAILATTACHMENTINFO'; Value = 'Microsoft-EmailAttachmentInfo'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGEMAILEVENTS'; Value = 'Microsoft-EmailEvents'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGEMAILPOSTDELIVERYEVENTS'; Value = 'Microsoft-EmailPostDeliveryEvents'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGEMAILURLINFO'; Value = 'Microsoft-EmailUrlInfo'}
$standardStreamMapping += @{ Key = 'SENTINEL_GCP_AUDIT_LOGS'; Value = 'Microsoft-GCPAuditLogs'}
$standardStreamMapping += @{ Key = 'SENTINEL_GCP_FIREWALL_LOGS'; Value = 'Microsoft-GCPFirewallLogs'}
$standardStreamMapping += @{ Key = 'SENTINEL_GOOGLE_CLOUD_SCC'; Value = 'Microsoft-GoogleCloudSCC'}
$standardStreamMapping += @{ Key = 'HUNTING_BOOKMARKS_LOGANALYTICS'; Value = 'Microsoft-HuntingBookmark'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGIDENTITYDIRECTORYEVENTS'; Value = 'Microsoft-IdentityDirectoryEvents'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGIDENTITYLOGONEVENTS'; Value = 'Microsoft-IdentityLogonEvents'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGIDENTITYQUERYEVENTS'; Value = 'Microsoft-IdentityQueryEvents'}
$standardStreamMapping += @{ Key = 'INSIGHTS_METRICS_BLOB'; Value = 'Microsoft-InsightsMetrics'}
$standardStreamMapping += @{ Key = 'LINUX_AUDITD_BLOB'; Value = 'Microsoft-LinuxAuditLog'}
$standardStreamMapping += @{ Key = 'McasShadowItReportingId'; Value = 'Microsoft-McasShadowItReporting'}
$standardStreamMapping += @{ Key = 'MICROSOFTPURVIEWINFORMATIONPROTECTION_RESTAPI'; Value = 'Microsoft-MicrosoftPurviewInformationProtection'}
$standardStreamMapping += @{ Key = 'OFFICEACTIVITY_RESTAPI'; Value = 'Microsoft-OfficeActivity'}
$standardStreamMapping += @{ Key = 'OPERATION_JSON'; Value = 'Microsoft-Operation'}
$standardStreamMapping += @{ Key = 'OPERATION_BLOB'; Value = 'Microsoft-Operation'}
$standardStreamMapping += @{ Key = 'OFFICEPOWERAPPS_RESTAPI'; Value = 'Microsoft-PowerAppsActivity'}
$standardStreamMapping += @{ Key = 'OFFICEPOWERAUTOMATE_RESTAPI'; Value = 'Microsoft-PowerAutomateActivity'}
$standardStreamMapping += @{ Key = 'OFFICEPOWERBI_RESTAPI'; Value = 'Microsoft-PowerBIActivity'}
$standardStreamMapping += @{ Key = 'OFFICEPOWERPLATFORMADMIN_RESTAPI'; Value = 'Microsoft-PowerPlatformAdminActivity'}
$standardStreamMapping += @{ Key = 'OFFICEPOWERAPPSRESOURCE_RESTAPI'; Value = 'Microsoft-PowerPlatformConnectorActivity'}
$standardStreamMapping += @{ Key = 'OFFICEPOWERPLATFORMADMINDLP_RESTAPI'; Value = 'Microsoft-PowerPlatformDlpActivity'}
$standardStreamMapping += @{ Key = 'OFFICEPROJECT_RESTAPI'; Value = 'Microsoft-ProjectActivity'}
$standardStreamMapping += @{ Key = 'SECURITY_ALERT_DATA'; Value = 'Microsoft-SecurityAlert'}
$standardStreamMapping += @{ Key = 'SENTINEL_SECURITY_ALERT_DATA'; Value = 'Microsoft-SecurityAlert'}
$standardStreamMapping += @{ Key = 'SECURITY_EVENT_BLOB'; Value = 'Microsoft-SecurityEvent'}
$standardStreamMapping += @{ Key = 'SECURITY_INCIDENT_DATA'; Value = 'Microsoft-SecurityIncident'}
$standardStreamMapping += @{ Key = 'SENTINEL_HEALTH'; Value = 'Microsoft-SentinelHealth'}
$standardStreamMapping += @{ Key = 'THREAT_INTELLIGENCE_INDICATOR_DATA'; Value = 'Microsoft-ThreatIntelligenceIndicator'}
$standardStreamMapping += @{ Key = 'TENANTMICROSOFTWINDOWSDEFENDERATP_ADVANCEDHUNTINGURLCLICKEVENTS'; Value = 'Microsoft-UrlClickEvents'}
$standardStreamMapping += @{ Key = 'USAGE_METERING'; Value = 'Microsoft-Usage'}
$standardStreamMapping += @{ Key = 'SENTINEL_WATCHLIST'; Value = 'Microsoft-Watchlist'}
$standardStreamMapping += @{ Key = 'SECURITY_WEF_EVENT_BLOB'; Value = 'Microsoft-WindowsEvent'}
$standardStreamMapping += @{ Key = 'SECURITY_WEF_EVENT_BLOB_OBO'; Value = 'Microsoft-WindowsEvent'}
$standardStreamMapping += @{ Key = 'SENTINEL_AWSSECHUB'; Value = 'Microsoft-AWSSecurityHubFindings'}


# Function to check if a key exists in the array of hashtables
function GetKeyValue {
  param (
      [string]$key
  )

  # Iterate through each hashtable in the array
  foreach ($pair in $standardStreamMapping) {
      # Explicitly check if the 'Key' property matches the key you're looking for
      if ($pair["Key"] -eq $key) {
          return $pair["Value"]  # Key found
      }
  }

  return $null  # Key not found
}