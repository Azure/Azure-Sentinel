# VMware SD-WAN and SASE Solution for Microsoft Sentinel

VMware SASE and SD-WAN are cloud-native networking and security solutions that offer a comprehensive approach to securing and optimizing branch connectivity for today's distributed enterprises. By integrating VMware SASE and SD-WAN with Microsoft Sentinel, you can gain a unified view of your network and security posture, enabling you to proactively identify and remediate threats, improve application performance, and reduce operational complexity. 

# Release Notes:
v1.0.0 (Initial release):

## Solutions supported:
1. VMware SD-WAN
2. VMware Cloud Web Security

## Events collected:

Via Syslog (Using AMA):
1. Edge Firewall Events
2. Edge Firewall IDS/IPS Events

Via API (Function App):
1. Edge Firewall IDS/IPS Events (Backup)
2. VMware SD-WAN Audit Events
3. VMware Cloud Web Security Audit Events
4. VMware Cloud Web Security Web Logs
5. VMware Cloud Web Security DLP Logs
6. VMware SD-WAN Events
7. VMware SD-WAN NSD/CSS Events

# Deployment Guide
A detailed implementation plan will be provided as soon as the solution is published. This readme will be updated with a link to the documentation as soon as its published.

## VECO API Authorization
The solution contains a function app that deploys in Microsoft Azure. It is worth testing the ARM template in a test RG/subscription so that created tables, rules, incidents do not collide with your existing integration or other data streams.

The solution is using API Token-based authorization in a VECO enterprise. Partner/Operator-level integrations are not supported by the Function App. All API calls require an enterprise-level admin user accunt. Please follow the instructions to create an API token:
https://docs.vmware.com/en/VMware-SD-WAN/5.2/VMware-SD-WAN-Administration-Guide/GUID-2FA3763F-835C-4D10-A32B-450FEB5397D8.html

## Function App Authorization:

The Function App requires authentication to be able to call the Log Ingestion API. The ARM template does not contain these settings, so please ensure that you authorize access for each DCR (Data Collection Rule) by following the steps "Create Microsoft Entra application" and "Assign permissions to the DCR" from the following guide: https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-portal#assign-permissions-to-the-dcr.


# Solution support
All components of the solution are provided as-is. If you find a bug or if you have an idea, please share it with us on: sase-siem-integration@vmware.com Thank you!

# Function App: SD-WAN Events Collected
The Function App collects various Events from the VECO API. The list of these events can be expanded to adjust your requirements
## Cloud Security Service / Non-SD-WAN Destination:
- "ALL_CSS_DOWN",
- "CSS_UP",
- "VPN_DATACENTER_STATUS"
## Audit Events:
- BROWSER_ENTERPRISE_LOGIN",
- "USER_LOGIN_FAILURE",
- "USER_LOGIN_SSO",
- "USER_LOGIN_FAILURE_SSO",
- "EDGE_SSH_LOGIN",
- "NEW_INTEGRATED_CA",
- "CERTIFICATE_REVOCATION",
- "CERTIFICATE_RENEWAL",
- "UPDATED_CLIENT_DEVICE_HOSTNAME_VIA_API",
- "CREATE_USER",
- "EDIT_PROFILE"
## Management Plane Events:
- "NTP_CONF_APPLIED",
- "MGD_CONF_APPLIED",
- "MGD_CONF_FAILED",
- "MGD_CONF_PENDING",
- "MGD_CONF_UPDATE_INVALID",
- "MGD_DEACTIVATED",
- "MGD_DIAG_REBOOT",
- "MGD_DIAG_RESTART",
- "MGD_EDGE_TUNNEL_DISABLED",
- "MGD_EDGE_TUNNEL_ENABLED",
- "MGD_EXITING",
- "MGD_HARD_RESET",
- "MGD_INVALID_VCO_ADDRESS",
- "MGD_NETWORK_SETTINGS_UPDATED",
- "MGD_ROUTE_CHANGE",
- "MGD_ROUTE_DIRECT",
- "MGD_ROUTE_GATEWAY",
- "MGD_SHUTDOWN",
- "MGD_START",
- "MGD_CONF_ROLLBACK"
## Edge Events:
- "EDGE_MGD_SERVICE_DISABLED",
- "EDGE_MGD_SERVICE_FAILED",
- "EDGE_NEW_DEVICE",
- "EDGE_NEW_USER",
- "EDGE_DHCP_BAD_OPTION",
- "EDGE_DOT1X_SERVICE_DISABLED",
- "EDGE_DOT1X_SERVICE_FAILED",
- "EDGE_MEMORY_USAGE_ERROR",
- "EDGE_MEMORY_USAGE_WARNING",
- "EDGE_OTHER_SERVICE_DISABLED",
- "EDGE_OTHER_SERVICE_FAILED",
- "EDGE_REBOOTING",
- "EDGE_RESTARTING",
- "EDGE_SERVICE_DISABLED",
- "EDGE_SERVICE_DUMPED",
- "EDGE_SERVICE_FAILED",
- "EDGE_SHUTTING_DOWN",
- "EDGE_STARTUP",
- "EDGE_USB_PORTS_ENABLE_FAILURE",
- "EDGE_USB_PORTS_DISABLE_FAILURE",
- "EDGE_USB_PLUGGED_IN",
- "EDGE_USB_UNPLUGGED",
- "EDGE_NVS_TUNNEL_UP",
- "EDGE_NVS_TUNNEL_DOWN",
- "EDGE_TUNNEL_CAP_WARNING",
- "EDGE_DIRECT_TUNNEL_UNKNOWN",
- "EDGE_CONGESTED",
- "EDGE_STABLE"

## Cloud Web Security Audit:
- "CWS_EVENT"
> Please Note: CWS Web and Data Loss Prevention Events are collected separately. This event is used to capture policy changes.

## Enhanced Firewall Services:
- "POLL_IDPS_SIGNATURE_FAIL",
- "MGD_ATPUP_DOWNLOAD_IDPS_SIGNATURE_FAILED",
- "MGD_ATPUP_DECRYPT_IDPS_SIGNATURE_FAILED",
- "MGD_ATPUP_APPLY_IDPS_SIGNATURE_FAILED",
- "MGD_ATPUP_APPLY_IDPS_SIGNATURE_SUCCEEDED",
- "MGD_ATPUP_STANDBY_UPDATE_START",
- "MGD_ATPUP_STANDBY_UPDATE_FAILED",
- "MGD_ATPUP_STANDBY_UPDATED",
- "MGD_ATPUP_INVALID_IDPS_SIGNATURE",
- "IDPS_SIGNATURE_VCO_VERSION_CHECK_FAIL",
- "IDPS_SIGNATURE_GSM_VERSION_CHECK_FAIL",
- "IDPS_SIGNATURE_SKIP_DOWNLOAD_NO_UPDATE",
- "IDPS_SIGNATURE_STORE_FAILURE_NO_PATH",
- "IDPS_SIGNATURE_DOWNLOAD_SUCCESS",
- "IDPS_SIGNATURE_DOWNLOAD_FAILURE",
- "IDPS_SIGNATURE_STORE_SUCCESS",
- "IDPS_SIGNATURE_STORE_SIGNATURE_FAILURE",
- "IDPS_SIGNATURE_METADATA_INSERT_SUCCESS",
- "IDPS_SIGNATURE_METADATA_INSERT_FAILURE",
- "IDPS_SIGNATURE_INCORRECT_CHECKSUM"
