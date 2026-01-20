# CommonSecurityLog Behaviors

List of behavior detection rules for CommonSecurityLog data source (CyberArk, Palo Alto, etc.)

**Total Behaviors**: 142

| Name | Title |
|------|-------|
| BehaviorAppServiceLateralMovement | Lateral Movement via Internal Application-Specific TCP Services |
| BehaviorAsymmetricBulkTransfer | High-Volume Asymmetric Data Transfer to External Web, SaaS, Remote Access Services |
| BehaviorAuditTrailSuppression | Defense Evasion – CyberArk Vault Session Audit Artifact Suppression |
| BehaviorBackupReplicationOutbound | Outbound Backup and Replication Service Traffic to External Network Destinations |
| BehaviorBittorrentOutboundTraffic | Outbound Bittorrent Peer-to-Peer Traffic Through Perimeter Firewall |
| BehaviorBlockedP2PRemoteAccess | Firewall-Blocked Outbound Peer-to-Peer Remote Access Application Traffic |
| BehaviorBruteForceMultiService | Source IP Conducting Brute Force Authentication Across Multiple Services |
| BehaviorChainedPivot | Chained Internal Remote Management Pivot through Intermediate Host |
| BehaviorChainedWebExploit | Chained Web Exploit Activity From Directory Traversal To Remote Code Execution On Single Server |
| BehaviorCloudControllerComm | Outbound Communication to Network Infrastructure Management Cloud Controllers |
| BehaviorCloudEmailExfiltration | Exfiltration Over Web Service via Cloud Email Delivery Platform Access |
| BehaviorCloudExfiltrationDetection | Web Service Exfiltration to Cloud Applications Flagged by Firewall Content Inspection |
| BehaviorCloudPushManagement | Outbound Communication to Cloud Push Notification and Endpoint Management Services |
| BehaviorConcentratedThreatDnsQueries | Internal Host Generating Concentrated Threat-Flagged DNS Queries |
| BehaviorConcentratedUnknownUdp | Command and Control – Concentrated Unknown UDP Application Sessions Involving Single Host |
| BehaviorContentInspectionBypass | Network Evasion: Repeated Use of Content Inspection Bypass Policies Through Palo Alto Firewall |
| BehaviorCredentialScreenshotSequence | Credential Access and Collection – Sequential Use of Authentication and Screenshot Capture Services from Same Host |
| BehaviorCyberArkMultiHostActivity | Account Manipulation: CyberArk Password Management Identity Used From Multiple Source Hosts in Short Interval |
| BehaviorCyberArkSshKeyVerification | Credential Access via CyberArk SSH Key Retrieval Followed by CPM SSH Key Verification |
| BehaviorDNP3OperateReadBurst | ICS Command and Telemetry via Combined DNP3 Direct-Operate and Read Operations |
| BehaviorDataReplicationBurst | Concentrated Data Replication Application Traffic to Single Destination Host via Palo Alto Firewall |
| BehaviorDatabaseTrafficNonStandardPort | Database Application Traffic On Non-Standard Ports To Single Destination Host |
| BehaviorDefaultPasswordAuth | Credential Access via Compromised or Default Passwords in HTTP Basic Authentication |
| BehaviorDirectoryEnumerationBurst | Account Discovery via LDAP and LDAPS Queries to Multiple Directory Endpoints Across Firewall |
| BehaviorDirectoryServiceNonStandardPort | Directory Service Application Traffic To Single Host On Non-Standard Destination Ports Via Palo Alto Firewall |
| BehaviorDistributedWebExploit | Concentrated Web Exploit Activity from Multiple Sources to Single Public-Facing Host |
| BehaviorDnsPortDeviation | DNS Protocol Use on Unconventional Network Ports |
| BehaviorDriveByExposure | Drive-by Compromise Exposure via Clustered Malicious Web Content |
| BehaviorDualControlRapidApprovals | Privilege Escalation – CyberArk Dual-Control User Multiple Final File Access Approvals in Short Timeframe |
| BehaviorEncryptedDnsEgress | Application Layer Protocol: Encrypted DNS Traffic Through Perimeter Firewall |
| BehaviorEncryptedDnsRotation | Command and Control: Rotation Across Multiple Encrypted DNS Services by Single Internal Host |
| BehaviorEntitlementChangeBurst | Account Manipulation – CyberArk Identity-Entitlement Reconfiguration Burst |
| BehaviorEnvConfigScan | External Web Scanning for Environment and Configuration Files on a Single Host |
| BehaviorExternalIdentitySync | Account Manipulation – CyberArk LDAP-Sourced External Identity Synchronization |
| BehaviorExternalOracleFormsAccess | Initial Access via External Client to Internal Oracle Forms Service over Non-Standard Port |
| BehaviorFileServiceExternalAccess | SMB and NFS File Service Sessions Between Internal Hosts and External IP Addresses |
| BehaviorHighFrequencyDnsOutbound | Application Layer Protocol: High-Frequency DNS Communications from Single Host to Multiple Destinations |
| BehaviorHighVolumeSaaSExfil | Exfiltration over Web Services – High-Volume Outbound Data Transfers from Single Internal Host to Cloud SaaS and Security Services |
| BehaviorHighVolumeServiceTransfer | High-Volume Data Transfer Over Database, OPC UA, SNMP Services Between Single Host Pair |
| BehaviorHistorianMultiHostAccess | ICS Historian or SCADA Data Server Accessed by Multiple Internal Hosts Over Historian Protocols |
| BehaviorHostSweepScan | Palo Alto Host Sweep Scanning from a Single Source Host |
| BehaviorHttp2RstC2 | Command and Control Over HTTPS Using Repeated Suspicious HTTP/2 RST Stream Frames |
| BehaviorHttpExfilOversizedResponse | Exfiltration Over HTTP via Repeated Oversized Web Responses Between Internal Hosts Through Palo Alto Firewall |
| BehaviorIcmpMultiProbeDiscovery | Network Discovery – Multi-Type ICMP Probing from Single Source Host |
| BehaviorIcsDiscoveryCommandSequence | ICS Command Sessions Following CIP EtherNet/IP Device Discovery to Same Host |
| BehaviorIcsProtocolNonStandardPort | ICS Application Protocol Traffic Over Non-Standard Ports from Single Source Host |
| BehaviorIcsWebAccess | Web-Based ICS and Building Management Interface Access from Single Internal Host |
| BehaviorInboundTcpFlood | Network Denial-of-Service via High-Volume Inbound TCP Connections from Internet to Single Internal Host |
| BehaviorInboundVpnAccess | External Remote Services via Inbound VPN Sessions to Internal Private IP Addresses |
| BehaviorJavaDeserializationAbuse | Repeated Java Deserialization Exploit Traffic from Single Source to Web Service |
| BehaviorJavaDeserializationBurst | Destination Host Receiving Multiple Java Deserialization Exploit Threat Signatures from Single Source |
| BehaviorJwtKeyUpdateSshRetrieval | CyberArk JWT Authentication Public Key Update Followed by SSH Key Retrieval on Same Vault |
| BehaviorLateralBackupReplication | Lateral Backup and Replication Service Communication Between Internal Network Segments |
| BehaviorLateralSMBBurst | Concentrated Internal SMB and Remote Administration Service Connectivity from Single Source Host |
| BehaviorLdapSmbSequence | LDAP NTLM Authentication Followed by SMB Login to Remote Windows Host |
| BehaviorLdapSyncBurst | CyberArk Vault LDAP-Synchronized External Identity Management Burst |
| BehaviorLsaQueryDeleteAccess | Remote LSA Policy Query Followed by Delete-Access Operations Over Windows Network Protocols |
| BehaviorManagementChannelExfiltration | Exfiltration Over Trusted Enterprise Management Services |
| BehaviorManagementProtocolOutboundBlocked | Outbound Management Protocol Communications Blocked by Firewall |
| BehaviorManagementServiceMultiHostAccess | Internal Management Service Endpoint Receiving Connections from Multiple Hosts |
| BehaviorMassSSHKeyRetrieval | Credential Access via High-Volume CyberArk SSH Key Retrieval Across Multiple Accounts or Hosts |
| BehaviorMemcachedAmplification | Network Denial of Service via UDP Memcached Amplification Traffic Through Firewall |
| BehaviorMultiCategoryWebExploit | Web Exploit Signature Activity From Single Source Across Multiple URL Categories |
| BehaviorMultiComponentKeyUpdate | CyberArk Vault Multi-Component JWT Authentication Key Update Sequence |
| BehaviorMultiProtocolFileSharing | Single Destination Host Accessed Via Multiple File-Sharing Application Protocols |
| BehaviorMultiProtocolHostAccess | Single Destination Host Accessed via Multiple ICS Protocols from Diverse Source Addresses |
| BehaviorMultiProtocolSession | Multi-Protocol ICS and Building Automation Network Sessions from Single Source Host |
| BehaviorMultiRCEExploitTarget | Multiple Remote Code Execution Exploit Signatures Targeting Enterprise Security and Management Platforms on Single Host |
| BehaviorMultiRemoteAccessUsage | Network Security Device Handling Multiple Commercial Remote Access and RMM Applications |
| BehaviorMultiSaaSExfiltration | Exfiltration Over Web Services to Multiple SaaS Destinations from Single Internal Host |
| BehaviorMultiServiceBruteForce | Credential Access via Multi-Service Network Authentication Brute Force Activity |
| BehaviorMultiServiceCloudAccess | Anomalous Multi-Service Web Access to Cloud and SaaS Platforms from Single Host |
| BehaviorMultiSourceVpnTunnel | Single Destination IP With Multiple Source VPN Or Tunneling Sessions |
| BehaviorMultiSourceXSSAttack | Web Application Targeted by Cross-Site Scripting Requests from Multiple Source Hosts |
| BehaviorMultiThreatSignature | Source-Destination Pair with Multiple Distinct Palo Alto Vulnerability THREAT Signatures |
| BehaviorMultiThreatWebTraffic | User Account with Multiple Palo Alto Threat Events in Web and Encrypted Traffic |
| BehaviorMultiVulnScanning | Reconnaissance – Multi-Vulnerability Web and Gateway Scanning from Single Source Host |
| BehaviorMultipleSMBLSASSAuthAttempts | Destination Host Targeted by Multiple Windows SMB and LSASS Authentication Attempts |
| BehaviorMultipleThreatEventsSamePort | Destination Host Receiving Multiple Palo Alto Vulnerability THREAT Events on the Same Service Port |
| BehaviorMultipleWebExploitSSLTarget | Multiple Web Exploit Signatures Against Single SSL Non-Decrypted Web Destination |
| BehaviorMultipleXSSAttempts | Multiple Cross-Site Scripting Signature Matches On Single Web Resource From Single Source |
| BehaviorNmapHNAP1Probing | Discovery – Nmap Scripting Engine Probing of HNAP1 Web Device Endpoints |
| BehaviorNonBlockingRCE | Remote Code Execution Web Exploit Traffic Permitted by Non-Blocking Firewall Policies |
| BehaviorNonBrowsingWebC2 | Web Command and Control via Non-Browsing Application Protocols to External Destinations |
| BehaviorOTServiceRecon | OT Service Discovery via Control Protocol Scanning |
| BehaviorObfuscatedScriptDelivery | External Host Serving Repeated Obfuscated Or Embedded Script Content |
| BehaviorOutboundDatabaseConnection | Outbound Database Protocol Connections from Internal Network to External Hosts |
| BehaviorOverlayTunnelSessions | Overlay Tunneling Sessions Across Diverse Network Segments |
| BehaviorOwnerChangeSequence | CyberArk Vault Account Owner Modification Sequence |
| BehaviorP2PWebMediaExfil | Command and Control Over Peer-to-Peer and Consumer Web Media Services From Single Internal Host Through Palo Alto Firewall |
| BehaviorPackageManagerIngress | Ingress Tool Transfer via Linux Package Manager Traffic Over HTTP |
| BehaviorPaloAltoHttpThreatBurst | Concentrated Palo Alto HTTP Threat Signature Activity Toward Single Destination Service |
| BehaviorPortScanProbe | Network Discovery via Port Scanning and Vulnerability Probing Observed by Firewall |
| BehaviorPrintServiceSessionFlood | Device Receiving Concentrated Direct Print Service Sessions From Multiple Hosts |
| BehaviorProtocolPortMismatch | Application-Layer Protocol Use on Unexpected Network Ports |
| BehaviorRceWebAttackBurst | Concentrated Remote Code Execution Web Vulnerability Signatures On Single Destination Host |
| BehaviorRemoteAccessConcentration | Virtual Desktop Application Sessions Concentrated on Single Destination Host |
| BehaviorRemoteAdminSession | Remote Administrative Service Sessions via Palo Alto Firewall |
| BehaviorRemoteCodeProbe | Remote Code Execution Web Vulnerability Probing From Single Source Host |
| BehaviorRepeatedBlockedInboundTCP | Repeated Blocked Inbound TCP Connections from External Source Host |
| BehaviorRepeatedIkeProbing | Repeated Outbound IKE VPN Service Probing From Single Internal Host |
| BehaviorRepeatedSmbAdminAccess | Repeated SMB Administrative Share Access Attempts Logged as Palo Alto Threats |
| BehaviorRepeatedTlsNoInspection | Repeated TLS Traffic with Disabled Content Inspection from Single Source |
| BehaviorRepeatedUpdateProtocolDenials | Command and Control: Repeated Firewall-Denied Application-Layer Update Protocol Connections from Single Host |
| BehaviorRepeatedVulnSignatureEmptyPath | Repeated Web Vulnerability Signatures With Empty URL Path Between Single Source And Server |
| BehaviorSIPExploitBlocked | Exploit Public-Facing SIP Service Traffic Matching Vulnerability Signature Dropped by Firewall |
| BehaviorSMBMaliciousTransfer | SMB File Transfer of Malicious or Obfuscated Payloads Between Internal Hosts |
| BehaviorSMBRpcLateralMovement | Lateral Movement Over SMB Using Encrypted Microsoft Windows RPC Between Internal Hosts |
| BehaviorScadaProtocolExploit | Exploitation: SCADA DNP3 or Modbus Protocol Exploit Signature on Internal Traffic |
| BehaviorScadaThreatBurst | Concentrated Palo Alto SCADA Protocol Threat Alerts From Single Source Host |
| BehaviorScannerBurst | Reconnaissance – Concentrated Network Scanner Application Traffic |
| BehaviorScriptObfuscationBurst | Concentrated Script Obfuscation And Embedded Script Threats In Web Traffic |
| BehaviorServiceControllerLateralMovement | Remote Windows Service Control Lateral Movement via ms-service-controller Traffic to Multiple Internal Hosts |
| BehaviorSmbBruteForceLogin | SMB Remote Login Attempt Following SMB Password Brute Force Activity |
| BehaviorSmbBruteForceSequence | SMB Login Attempt Followed by Password Brute Force from Same Source to Same Destination |
| BehaviorSmbNonStandardPort | SMB Application Traffic To Non-Standard TCP Ports From Single Source Host |
| BehaviorSmbRegistryWrite | Remote Registry Modification Attempt After SMB Login to Windows Host |
| BehaviorSmbShareEnumeration | Discovery via SMB NetrShareEnum File Share Enumeration Through Palo Alto Firewall |
| BehaviorSnmpFlood | High-Volume SNMP Management Traffic Across Network Boundary |
| BehaviorSslTlsReconScan | Network Reconnaissance Using SSL/TLS Vulnerability Scanning Across Multiple Hosts |
| BehaviorTelnetLateralMovement | Lateral Movement via Internal Telnet Remote Administrative Sessions |
| BehaviorThreatConnectionBurst | External Source Host with Repeated Palo Alto THREAT-Flagged Connections to Internal Addresses |
| BehaviorUnencryptedUdpExfiltration | Exfiltration Over Unencrypted UDP to External Reporting Service |
| BehaviorVaultFileMassDeletion | CyberArk PSM application repeated vault file deletion activity |
| BehaviorVaultHistoryClearing | Defense Evasion – Automated CyberArk Vault History Clearing by Batch Process |
| BehaviorVaultMultiAccountOperations | CyberArk client host performing multiple vault file operations via different accounts |
| BehaviorVoiceSignalingC2 | Command and Control – Voice Signaling Protocol Connectivity Across Firewall Boundaries |
| BehaviorVoipBypassOutbound | Outbound Encrypted VoIP Bypass Sessions From Internal Host to External Service |
| BehaviorVpnLateralMovement | VPN Client Lateral Movement via Direct Database and Data-Store Service Access |
| BehaviorVulnScannerProbing | Web-Browsing Vulnerability Scanner Probing Multiple Internal Hosts from a Single Source |
| BehaviorWebAppExploitDetection | Web Application Exploitation via Palo Alto Vulnerability and Malicious HTTP Payload Signatures |
| BehaviorWebAuthBruteForce | Credential Access via High-Volume Web Account Authentication Flows |
| BehaviorWebExploitMultiHost | Web Exploit Signature Activity From Single User Account Across Multiple Hosts |
| BehaviorWebExploitScan | Wide-Range Web Application Exploit Scanning From Single Source To Multiple Servers |
| BehaviorWebRCEBlocked | Exploit Public-Facing Application via Remote Code Execution or Command Injection Web Requests Blocked by Firewall |
| BehaviorWebRCEPivot | Lateral Movement via Internal Web-Based Remote Code Execution Against Managed Services |
| BehaviorWebServiceRotation | Outbound Web Service Rotation Across Multiple Public Platforms by Single Internal Host |
| BehaviorWhitelistedWebExploit | Web Exploit Signatures Over Whitelisted Business Web Destinations From Single Source Host |
| BehaviorWhoisScan | Reconnaissance – Repeated Outbound Whois Queries from Single Internal Host |
| BehaviorXSSAdminInterface | Cross-Site Scripting Exploit Attempts Against Authentication and Management Web Interfaces |
| BehaviorXSSScanBurst | Cross-Site Scripting Scanning from Single Source Across Web Applications |
| BehaviorXSSWeakDestination | Cross-Site Scripting Classified Web Requests Reaching Weakly Controlled Destinations |
