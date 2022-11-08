#requires -version 6.2
<#
    .SYNOPSIS
        This command will generate a CSV file containing the information about all the Azure Sentinel
        MITRE tactics and techniques being used.
    .DESCRIPTION
        This command will generate a CSV file containing the information about all the Azure Sentinel
        MITRE tactics and techniques being used.
    .PARAMETER WorkSpaceName
        Enter the Log Analytics workspace name, this is a required parameter
    .PARAMETER ResourceGroupName
        Enter the Log Analytics workspace name, this is a required parameter
    .PARAMETER FileName
        Enter the file name to use.  Defaults to "ruletemplates"  ".csv" will be appended to all filenames
    .PARAMETER IncludeDisabled
        Include disabled rules in the count.  Defaults to false
    .PARAMETER ShowZeroSimulatedRuleTemplates
        Include those rule templates that would cover any techniques not already covered (count == 0).  Defaults to false
    .NOTES
        AUTHOR= Gary Bushey
        LASTEDIT= 17 July 2022
    .EXAMPLE
        Export-AzSentineMITREtoCSV -WorkspaceName "workspacename" -ResourceGroupName "rgname"
        In this example you will get the file named "mitrerules.csv" generated containing all the rule's MITRE information
    .EXAMPLE
        Export-AzSentineMITREtoCSV -WorkspaceName "workspacename" -ResourceGroupName "rgname" -fileName "test"
        In this example you will get the file named "test.csv" generated containing all the rule's MITRE information
     .EXAMPLE
        Export-AzSentineMITREtoCSV -WorkspaceName "workspacename" -ResourceGroupName "rgname" -IncludeDisabled $true
        In this example you will get the file named "mitrerules.csv" generated containing all the rule's MITRE information, including those rules that are disabled
      .EXAMPLE
        Export-AzSentineMITREtoCSV -WorkspaceName "workspacename" -ResourceGroupName "rgname" -fileName "simulated" -ShowZeroSimulatedRuleTemplates $true
        In this example you will get the file named "simulated.csv" generated containing those rule templates that will cover techniques whose count == 0
      .EXAMPLE
        Export-AzSentineMITREtoCSV -WorkspaceName "workspacename" -ResourceGroupName "rgname" -fileName "simulated" -ShowAllSimulatedRuleTemplates $true
        In this example you will get the file named "simulated.csv" generated containing those rule templates that will cover techniques and have not been used yet.
#>


[CmdletBinding()]
param (
  [Parameter(Mandatory = $true)]
  [string]$WorkSpaceName,

  [Parameter(Mandatory = $true)]
  [string]$ResourceGroupName,

  [string]$FileName = "mitrerules.csv",

  [bool]$IncludeDisabled = $false,

  [bool]$ShowZeroSimulatedRuleTemplates = $false,

  [bool]$ShowAllSimulatedRuleTemplates = $false
  
)

Add-Type -AssemblyName System.Collections

$outputObject = New-Object system.Data.DataTable
[void]$outputObject.Columns.Add('Tactic', [string]::empty.GetType() )
[void]$outputObject.Columns.Add('Technique', [string]::empty.GetType() )
[void]$outputObject.Columns.Add('Name', [string]::empty.GetType() )
[void]$outputObject.Columns.Add('Count', [string]::empty.GetType() )
[void]$outputObject.Columns.Add('Description', [string]::empty.GetType() )

$simulatedOutput = New-Object System.Data.DataTable
[void]$simulatedOutput.Columns.Add('Tactic', [string]::empty.GetType() )
[void]$simulatedOutput.Columns.Add('Technique', [string]::empty.GetType() )
[void]$simulatedOutput.Columns.Add('Name', [string]::empty.GetType() )
[void]$simulatedOutput.Columns.Add('RuleName', [string]::empty.GetType() ) 


#[collections.generic.list[object]]$outputObject = @("Tactic" , "Technique" , "Name" , "Count" ,"Description" )


$tacticHash = [ordered]@{
  "Reconnaissance"          = @("T1595", "T1592", "T1589", "T1590", "T1591", "T1598", "T1597", "T1596", "T1593", "T1594")
  "ResourceDevelopment"     = @("T1583", "T1586", "T1584", "T1587", "T1585", "T1588", "T1608")
  "InitialAccess"           = @("T1189", "T1190", "T1133", "T1200", "T1566", "T1091", "T1195", "T1199", "T1078")
  "Execution"               = @("T1059", "T1203", "T1559", "T1106", "T1053", "T1129", "T1072", "T1569", "T1204", "T1047")
  "Persistence"             = @("T1098", "T1197", "T1547", "T1037", "T1176", "T1554", "T1136", "T1543", "T1546", "T1133", "T1574", "T1525", "T1556", "T1137", "T1542", "T1053", "T1505", "T1205", "T1078", "T0839", "T0859", "T0889", "T0873", "T0857")
  "PrivilegeEscalation"     = @("T1548", "T1134", "T1547", "T1037", "T1543", "T1484", "T1611", "T1546", "T1068", "T1574", "T1055", "T1053", "T1078", "T0874", "T0890")
  "DefenseEvasion"          = @("T1548", "T1134", "T1197", "T1612", "T1140", "T1610", "T1006", "T1484", "T1480", "T1211", "T1222", "T1564", "T1574", "T1562", "T1070", "T1202", "T1036", "T1556", "T1578", "T1112", "T1601", "T1599", "T1027", "T1542", "T1055", "T1207", "T1014", "T1218", "T1216", "T1553", "T1221", "T1205", "T1127", "T1535", "T1550", "T1078", "T1497", "T1600", "T1220", "T0872", "T0820", "T0849", "T0858", "T0851", "T0856")
  "CredentialAccess"        = @("T1110", "T1555", "T1212", "T1187", "T1606", "T1056", "T1557", "T1556", "T1040", "T1003", "T1528", "T1558", "T1539", "T1111", "T1552", "T1613", "T1614")
  "Discovery"               = @("T1087", "T1010", "T1217", "T1580", "T1538", "T1526", "T1482", "T1083", "T1046", "T1135", "T1040", "T1201", "T1120", "T1069", "T1057", "T1012", "T1018", "T1518", "T1082", "T1016", "T1049", "T1033", "T1007", "T1124", "T1497", "T0842", "T0840", "T0888", "T0887", "T0846")
  "LateralMovement"         = @("T1210", "T1534", "T1570", "T1563", "T1021", "T1091", "T1072", "T1080", "T1550", "T0812", "T0859", "T0886", "T0843", "T0866", "T0867")
  "Collection"              = @("T1560", "T1123", "T1119", "T1115", "T1530", "T1602", "T1213", "T1005", "T1039", "T1025", "T1074", "T1114", "T1056", "T1185", "T1557", "T1113", "T1125", "T1609", "T1610", "T0802", "T0811", "T0887", "T0877", "T0830", "T0801", "T0868", "T0852", "T0861", "T0845")
  "CommandAndControl"       = @("T1071", "T1092", "T1132", "T1001", "T1568", "T1573", "T1008", "T1105", "T1104", "T1095", "T1571", "T1572", "T1090", "T1219", "T1205", "T1102", "T0884", "T0869", "T0885")
  "Exfiltration"            = @("T1020", "T1030", "T1048", "T1041", "T1011", "T1052", "T1567", "T1029", "T1537")
  "Impact"                  = @("T1531", "T1485", "T1486", "T1565", "T1491", "T1561", "T1499", "T1495", "T1490", "T1498", "T1496", "T1489", "T1529", "T0882", "T0813", "T0879", "T0880", "T0815", "T0837", "T0826", "T0832", "T0828", "T0831", "T0829", "T0827")  
  "ImpairProcessControl"    = @("T0836", "T0839", "T0806", "T0855", "T0856", "T0857")
  "InhibitResponseFunction" = @("T0838", "T0805", "T0804", "T0814", "T0851", "T0878", "T0835", "T0809", "T0816", "T0800", "T0803", "T0881", "T0857")
}

$techniqueNameHash = @{
  T1595 = "Active Scanning"
  T1592 = "Gather Victim Host Information"
  T1589 = "Gather Victim Identity Information"
  T1590 = "Gather Victim Network Information"
  T1591 = "Gather Victim Org Information"
  T1598 = "Phishing for Information"
  T1597 = "Search Closed Sources"
  T1596 = "Search Open Technical Databases"
  T1593 = "Search Open Websites/Domains"
  T1594 = "Search Victim-Owned Websites"
  T1583 = "Acquire Infrastructure"
  T1586 = "Compromise Accounts"
  T1584 = "Compromise Infrastructure"
  T1587 = "Develop Capabilities"
  T1585 = "Establish Accounts"
  T1588 = "Obtain Capabilities"
  T1608 = "Stage Capabilities"
  T1189 = "Drive-by Compromise"
  T1190 = "Exploit Public-Facing Application"
  T1133 = "External Remote Services"
  T1200 = "Hardware Additions"
  T1566 = "Phishing"
  T1091 = "Replication Through Removable Media"
  T1195 = "Supply Chain Compromise"
  T1199 = "Trusted Relationship"
  T1078 = "Valid Accounts"
  T1059 = "Command and Scripting Interpreter"
  T1609 = "Container Administration Command"
  T1610 = "Deploy Container"
  T1203 = "Exploitation for Client Execution"
  T1559 = "Inter-Process Communication"
  T1106 = "Native API"
  T1053 = "Scheduled Task/Job"
  T1129 = "Shared Modules"
  T1072 = "Software Deployment Tools"
  T1569 = "System Services"
  T1204 = "User Execution"
  T1047 = "Windows Management Instrumentation"
  T1098 = "Account Manipulation"
  T1197 = "BITS Jobs"
  T1547 = "Boot or Logon Autostart Execution"
  T1037 = "Boot or Logon Initialization Scripts"
  T1176 = "Browser Extensions"
  T1554 = "Compromise Client Software Binary"
  T1136 = "Create Account"
  T1543 = "Create or Modify System Process"
  T1546 = "Event Triggered Execution"
  T1574 = "Hijack Execution Flow"
  T1525 = "Implant Internal Image"
  T1556 = "Modify Authentication Process"
  T1137 = "Office Application Startup"
  T1542 = "Pre-OS Boot"
  T1505 = "Server Software Component"
  T1205 = "Traffic Signaling"
  T1548 = "Abuse Elevation Control Mechanism"
  T1134 = "Access Token Manipulation"
  T1484 = "Domain Policy Modification"
  T1611 = "Escape to Host"
  T1068 = "Exploitation for Privilege Escalation"
  T1055 = "Process Injection"
  T1612 = "Build Image on Host"
  T1140 = "Deobfuscate/Decode Files or Information"
  T1006 = "Direct Volume Access"
  T1480 = "Execution Guardrails"
  T1211 = "Exploitation for Defense Evasion"
  T1222 = "File and Directory Permissions Modification"
  T1564 = "Hide Artifacts"
  T1562 = "Impair Defenses"
  T1070 = "Indicator Removal on Host"
  T1202 = "Indirect Command Execution"
  T1036 = "Masquerading"
  T1578 = "Modify Cloud Compute Infrastructure"
  T1112 = "Modify Registry"
  T1601 = "Modify System Image"
  T1599 = "Network Boundary Bridging"
  T1027 = "Obfuscated Files or Information"
  T1207 = "Rogue Domain Controller"
  T1014 = "Rootkit"
  T1218 = "Signed Binary Proxy Execution"
  T1216 = "Signed Script Proxy Execution"
  T1553 = "Subvert Trust Controls"
  T1221 = "Template Injection"
  T1127 = "Trusted Developer Utilities Proxy Execution"
  T1535 = "Unused/Unsupported Cloud Regions"
  T1550 = "Use Alternate Authentication Material"
  T1497 = "Virtualization/Sandbox Evasion"
  T1600 = "Weaken Encryption"
  T1220 = "XSL Script Processing"
  T1110 = "Brute Force"
  T1555 = "Credentials from Password Stores"
  T1212 = "Exploitation for Credential Access"
  T1187 = "Forced Authentication"
  T1606 = "Forge Web Credentials"
  T1056 = "Input Capture"
  T1557 = "Man-in-the-Middle"
  T1040 = "Network Sniffing"
  T1003 = "OS Credential Dumping"
  T1528 = "Steal Application Access Token"
  T1558 = "Steal or Forge Kerberos Tickets"
  T1539 = "Steal Web Session Cookie"
  T1111 = "Two-Factor Authentication Interception"
  T1552 = "Unsecured Credentials"
  T1087 = "Account Discovery"
  T1010 = "Application Window Discovery"
  T1217 = "Browser Bookmark Discovery"
  T1580 = "Cloud Infrastructure Discovery"
  T1538 = "Cloud Service Dashboard"
  T1526 = "Cloud Service Discovery"
  T1613 = "Container and Resource Discovery"
  T1482 = "Domain Trust Discovery"
  T1083 = "File and Directory Discovery"
  T1046 = "Network Service Scanning"
  T1135 = "Network Share Discovery"
  T1201 = "Password Policy Discovery"
  T1120 = "Peripheral Device Discovery"
  T1069 = "Permission Groups Discovery"
  T1057 = "Process Discovery"
  T1012 = "Query Registry"
  T1018 = "Remote System Discovery"
  T1518 = "Software Discovery"
  T1082 = "System Information Discovery"
  T1614 = "System Location Discovery"
  T1016 = "System Network Configuration Discovery"
  T1049 = "System Network Connections Discovery"
  T1033 = "System Owner/User Discovery"
  T1007 = "System Service Discovery"
  T1124 = "System Time Discovery"
  T1210 = "Exploitation of Remote Services"
  T1534 = "Internal Spearphishing"
  T1570 = "Lateral Tool Transfer"
  T1563 = "Remote Service Session Hijacking"
  T1021 = "Remote Services"
  T1080 = "Taint Shared Content"
  T1560 = "Archive Collected Data"
  T1123 = "Audio Capture"
  T1119 = "Automated Collection"
  T1115 = "Clipboard Data"
  T1530 = "Data from Cloud Storage Object"
  T1602 = "Data from Configuration Repository"
  T1213 = "Data from Information Repositories"
  T1005 = "Data from Local System"
  T1039 = "Data from Network Shared Drive"
  T1025 = "Data from Removable Media"
  T1074 = "Data Staged"
  T1114 = "Email Collection"
  T1185 = "Man in the Browser"
  T1113 = "Screen Capture"
  T1125 = "Video Capture"
  T1071 = "Application Layer Protocol"
  T1092 = "Communication Through Removable Media"
  T1132 = "Data Encoding"
  T1001 = "Data Obfuscation"
  T1568 = "Dynamic Resolution"
  T1573 = "Encrypted Channel"
  T1008 = "Fallback Channels"
  T1105 = "Ingress Tool Transfer"
  T1104 = "Multi-Stage Channels"
  T1095 = "Non-Application Layer Protocol"
  T1571 = "Non-Standard Port"
  T1572 = "Protocol Tunneling"
  T1090 = "Proxy"
  T1219 = "Remote Access Software"
  T1102 = "Web Service"
  T1020 = "Automated Exfiltration"
  T1030 = "Data Transfer Size Limits"
  T1048 = "Exfiltration Over Alternative Protocol"
  T1041 = "Exfiltration Over C2 Channel"
  T1011 = "Exfiltration Over Other Network Medium"
  T1052 = "Exfiltration Over Physical Medium"
  T1567 = "Exfiltration Over Web Service"
  T1029 = "Scheduled Transfer"
  T1537 = "Transfer Data to Cloud Account"
  T1531 = "Account Access Removal"
  T1485 = "Data Destruction"
  T1486 = "Data Encrypted for Impact"
  T1565 = "Data Manipulation"
  T1491 = "Defacement"
  T1561 = "Disk Wipe"
  T1499 = "Endpoint Denial of Service"
  T1495 = "Firmware Corruption"
  T1490 = "Inhibit System Recovery"
  T1498 = "Network Denial of Service"
  T1496 = "Resource Hijacking"
  T1489 = "Service Stop"
  T1529 = "System Shutdown/Reboot"
  T0801 = "Monitor Process State"
  T0843 = "Program Download"
  T0836 = "Modify Parameter"
  T0802 = "Automated Collection"
  T0856 = "Spoof Reporting Message"
  T0855 = "Unauthorized Command Message"
  T0804 = "Block Reporting Message"
  T0852 = "Screen Capture"
  T0887 = "Wireless Sniffing"
  T0830 = "Man in the Middle"
  T0845 = "Program Upload"
  T0877 = "I/O Image"
  T0811 = "Data from Information Repositories"
  T0861 = "Point & Tag Identification"
  T0834 = "Native API"
  T0868 = "Detect Operating Mode"
  T0885 = "Commonly Used Port"
  T0869 = "Standard Application Layer Protocol"
  T0884 = "Connection Proxy"
  T0846 = "Remote System Discovery"
  T0888 = "Remote System Information Discovery"
  T0857 = "System Firmware"
  T0840 = "Network Connection Enumeration"
  T0842 = "Network Sniffing"
  T0849 = "Masquerading"
  T0820 = "Exploitation for Evasion"
  T0851 = "Rootkit"
  T0858 = "Change Operating Mode"
  T0872 = "Indicator Removal on Host"
  T0853 = "Scripting"
  T0807 = "Command-Line Interface"
  T0823 = "Graphical User Interface"
  T0871 = "Execution through API"
  T0874 = "Hooking"
  T0863 = "User Execution"
  T0821 = "Modify Controller Tasking"
  T0827 = "Loss of Control"
  T0837 = "Loss of Protection"
  T0832 = "Manipulation of View"
  T0828 = "Loss of Productivity and Revenue"
  T0829 = "Loss of View"
  T0882 = "Theft of Operational Information"
  T0880 = "Loss of Safety"
  T0813 = "Denial of Control"
  T0815 = "Denial of View"
  T0879 = "Damage to Property"
  T0826 = "Loss of Availability"
  T0831 = "Manipulation of Control"
  T0806 = "Brute Force I/O"
  T0839 = "Module Firmware"
  T0838 = "Modify Alarm Settings"
  T0805 = "Block Serial COM"
  T0881 = "Service Stop"
  T0835 = "Manipulate I/O Image"
  T0800 = "Activate Firmware Update Mode"
  T0809 = "Data Destruction"
  T0803 = "Block Command Message"
  T0816 = "Device Restart/Shutdown"
  T0814 = "Denial of Service"
  T0878 = "Alarm Suppression"
  T0864 = "Transient Cyber Asset"
  T0817 = "Drive-by Compromise"
  T0860 = "Wireless Compromise"
  T0848 = "Rogue Master"
  T0859 = "Valid Accounts"
  T0847 = "Replication Through Removable Media"
  T0866 = "Exploitation of Remote Services"
  T0862 = "Supply Chain Compromise"
  T0819 = "Exploit Public-Facing Application"
  T0822 = "External Remote Services"
  T0886 = "Remote Services"
  T0865 = "Spearphishing Attachment"
  T0883 = "Internet Accessible Device"
  T0812 = "Default Credentials"
  T0867 = "Lateral Tool Transfer"
  T0889 = "Modify Program"
  T0873 = "Project File Infection"
  T0890 = "Exploitation for Privilege Escalation"
}

$techniqueDescriptionHash = @{
  T1595 = "Adversaries may execute active reconnaissance scans to gather information that can be used during targeting. Active scans are those where the adversary probes victim infrastructure via network traffic, as opposed to other forms of reconnaissance that do not involve direct interaction.Adversaries may perform different forms of active scanning depending on what information they seek to gather."
  T1592 = "Adversaries may gather information about the victim's hosts that can be used during targeting. Information about hosts may include a variety of details, including administrative data (ex= name, assigned IP, functionality, etc.) as well as specifics regarding its configuration (ex= operating system, language, etc.)"
  T1589 = "Adversaries may gather information about the victim's identity that can be used during targeting. Information about identities may include a variety of details, including personal data (ex= employee names, email addresses, etc.) as well as sensitive details such as credentials."
  T1590 = "Adversaries may gather information about the victim's networks that can be used during targeting. Information about networks may include a variety of details, including administrative data (ex= IP ranges, domain names, etc.) as well as specifics regarding its topology and operations."
  T1591 = "Adversaries may gather information about the victim's organization that can be used during targeting. Information about an organization may include a variety of details, including the names of divisions/departments, specifics of business operations, as well as the roles and responsibilities of key employees.Adversaries may gather this information in various ways, such as direct elicitation via Phishing for Information."
  T1598 = "Adversaries may send phishing messages to elicit sensitive information that can be used during targeting. Phishing for information is an attempt to trick targets into divulging information, frequently credentials or other actionable information. Phishing for information is different from Phishing in that the objective is gathering data from the victim rather than executing malicious code."
  T1597 = "Adversaries may search and gather information about victims from closed sources that can be used during targeting. Information about victims may be available for purchase from reputable private sources and databases, such as paid subscriptions to feeds of technical/threat intelligence data. Adversaries may also purchase information from less-reputable sources such as dark web or cybercrime blackmarkets."
  T1596 = "Adversaries may search freely available technical databases for information about victims that can be used during targeting. Information about victims may be available in online databases and repositories, such as registrations of domains/certificates as well as public collections of network data/artifacts gathered from traffic and/or scans.Adversaries may search in different open databases depending on what information they seek to gather."
  T1593 = "Adversaries may search freely available websites and/or domains for information about victims that can be used during targeting. Information about victims may be available in various online sites, such as social media, new sites, or those hosting information about business operations such as hiring or requested/rewarded contracts.Adversaries may search in different online sites depending on what information they seek to gather."
  T1594 = "Adversaries may search websites owned by the victim for information that can be used during targeting. Victim-owned websites may contain a variety of details, including names of departments/divisions, physical locations, and data about key employees such as names, roles, and contact info (ex= Email Addresses). These sites may also have details highlighting business operations and relationships."
  T1583 = "Adversaries may buy, lease, or rent infrastructure that can be used during targeting. A wide variety of infrastructure exists for hosting and orchestrating adversary operations. Infrastructure solutions include physical or cloud servers, domains, and third-party web services."
  T1586 = "Adversaries may compromise accounts with services that can be used during targeting. For operations incorporating social engineering, the utilization of an online persona may be important. Rather than creating and cultivating accounts."
  T1584 = "Adversaries may compromise third-party infrastructure that can be used during targeting. Infrastructure solutions include physical or cloud servers, domains, and third-party web services. Instead of buying, leasing, or renting infrastructure an adversary may compromise infrastructure and use it during other phases of the adversary lifecycle."
  T1587 = "Adversaries may build capabilities that can be used during targeting. Rather than purchasing, freely downloading, or stealing capabilities, adversaries may develop their own capabilities in-house. This is the process of identifying development requirements and building solutions such as malware, exploits, and self-signed certificates."
  T1585 = "Adversaries may create and cultivate accounts with services that can be used during targeting. Adversaries can create accounts that can be used to build a persona to further operations. Persona development consists of the development of public information, presence, history and appropriate affiliations."
  T1588 = "Adversaries may buy and/or steal capabilities that can be used during targeting. Rather than developing their own capabilities in-house, adversaries may purchase, freely download, or steal them. Activities may include the acquisition of malware, software (including licenses), exploits, certificates, and information relating to vulnerabilities."
  T1608 = "Adversaries may upload, install, or otherwise set up capabilities that can be used during targeting. To support their operations, an adversary may need to take capabilities they developed (Develop Capabilities) or obtained (Obtain Capabilities) and stage them on infrastructure under their control. These capabilities may be staged on infrastructure that was previously purchased/rented by the adversary (Acquire Infrastructure) or was otherwise compromised by them (Compromise Infrastructure)."
  T1189 = "Adversaries may gain access to a system through a user visiting a website over the normal course of browsing. With this technique, the user's web browser is typically targeted for exploitation, but adversaries may also use compromised websites for non-exploitation behavior such as acquiring Application Access Token.Multiple ways of delivering exploit code to a browser exist, including=A legitimate website is compromised where adversaries have injected some form of malicious code such as JavaScript, iFrames, and cross-site scripting."
  T1190 = "Adversaries may attempt to take advantage of a weakness in an Internet-facing computer or program using software, data, or commands in order to cause unintended or unanticipated behavior. The weakness in the system can be a bug, a glitch, or a design vulnerability. These applications are often websites, but can include databases (like SQL), standard services (like SMB or SSH), network device administration and management protocols (like SNMP and Smart Install), and any other applications with Internet accessible open sockets, such as web servers and related services."
  T1133 = "Adversaries may leverage external-facing remote services to initially access and/or persist within a network. Remote services such as VPNs, Citrix, and other access mechanisms allow users to connect to internal enterprise network resources from external locations. There are often remote service gateways that manage connections and credential authentication for these services."
  T1200 = "Adversaries may introduce computer accessories, computers, or networking hardware into a system or network that can be used as a vector to gain access. While public references of usage by threat actors are scarce, many red teams/penetration testers leverage hardware additions for initial access. Commercial and open source products can be leveraged with capabilities such as passive network tapping , network traffic modification (i."
  T1566 = "Adversaries may send phishing messages to gain access to victim systems. All forms of phishing are electronically delivered social engineering. Phishing can be targeted, known as spearphishing."
  T1091 = "Adversaries may move onto systems, possibly those on disconnected or air-gapped networks, by copying malware to removable media and taking advantage of Autorun features when the media is inserted into a system and executes. In the case of Lateral Movement, this may occur through modification of executable files stored on removable media or by copying malware and renaming it to look like a legitimate file to trick users into executing it on a separate system. In the case of Initial Access, this may occur through manual manipulation of the media, modification of systems used to initially format the media, or modification to the media's firmware itself."
  T1195 = "Adversaries may manipulate products or product delivery mechanisms prior to receipt by a final consumer for the purpose of data or system compromise.Supply chain compromise can take place at any stage of the supply chain including=Manipulation of development toolsManipulation of a development environmentManipulation of source code repositories (public or private)Manipulation of source code in open-source dependenciesManipulation of software update/distribution mechanismsCompromised/infected system images (multiple cases of removable media infected at the factory)   Replacement of legitimate software with modified versionsSales of modified/counterfeit products to legitimate distributorsShipment interdictionWhile supply chain compromise can impact any component of hardware or software, attackers looking to gain execution have often focused on malicious additions to legitimate software in software distribution or update channels.    Targeting may be specific to a desired victim set  or malicious software may be distributed to a broad set of consumers but only move on to additional tactics on specific victims."
  T1199 = "Adversaries may breach or otherwise leverage organizations who have access to intended victims. Access through trusted third party relationship exploits an existing connection that may not be protected or receives less scrutiny than standard mechanisms of gaining access to a network.Organizations often grant elevated access to second or third-party external providers in order to allow them to manage internal systems as well as cloud-based environments."
  T1078 = "Adversaries may obtain and abuse credentials of existing accounts as a means of gaining Initial Access, Persistence, Privilege Escalation, or Defense Evasion. Compromised credentials may be used to bypass access controls placed on various resources on systems within the network and may even be used for persistent access to remote systems and externally available services, such as VPNs, Outlook Web Access and remote desktop. Compromised credentials may also grant an adversary increased privilege to specific systems or access to restricted areas of the network."
  T1059 = "Adversaries may abuse command and script interpreters to execute commands, scripts, or binaries. These interfaces and languages provide ways of interacting with computer systems and are a common feature across many different platforms. Most systems come with some built-in command-line interface and scripting capabilities, for example, macOS and Linux distributions include some flavor of Unix Shell while Windows installations include the Windows Command Shell and PowerShell."
  T1609 = "Adversaries may abuse a container administration service to execute commands within a container. A container administration service such as the Docker daemon, the Kubernetes API server, or the kubelet may allow remote management of containers within an environment.In Docker, adversaries may specify an entrypoint during container deployment that executes a script or command, or they may use a command such as docker exec to execute a command within a running container."
  T1610 = "Adversaries may deploy a container into an environment to facilitate execution or evade defenses. In some cases, adversaries may deploy a new container to execute processes associated with a particular image or deployment, such as processes that execute or download malware. In others, an adversary may deploy a new container configured without network rules, user limitations, etc."
  T1203 = "Adversaries may exploit software vulnerabilities in client applications to execute code. Vulnerabilities can exist in software due to unsecure coding practices that can lead to unanticipated behavior. Adversaries can take advantage of certain vulnerabilities through targeted exploitation for the purpose of arbitrary code execution."
  T1559 = "Adversaries may abuse inter-process communication (IPC) mechanisms for local code or command execution. IPC is typically used by processes to share data, communicate with each other, or synchronize execution. IPC is also commonly used to avoid situations such as deadlocks, which occurs when processes are stuck in a cyclic waiting pattern."
  T1106 = "Adversaries may interact with the native OS application programming interface (API) to execute behaviors. Native APIs provide a controlled means of calling low-level OS services within the kernel, such as those involving hardware/devices, memory, and processes. These native APIs are leveraged by the OS during system boot (when other system components are not yet initialized) as well as carrying out tasks and requests during routine operations."
  T1053 = "Adversaries may abuse task scheduling functionality to facilitate initial or recurring execution of malicious code. Utilities exist within all major operating systems to schedule programs or scripts to be executed at a specified date and time. A task can also be scheduled on a remote system, provided the proper authentication is met (ex= RPC and file and printer sharing in Windows environments)."
  T1129 = "Adversaries may execute malicious payloads via loading shared modules. The Windows module loader can be instructed to load DLLs from arbitrary local paths and arbitrary Universal Naming Convention (UNC) network paths. This functionality resides in NTDLL."
  T1072 = "Adversaries may gain access to and use third-party software suites installed within an enterprise network, such as administration, monitoring, and deployment systems, to move laterally through the network. Third-party applications and software deployment systems may be in use in the network environment for administration purposes."
  T1569 = "Adversaries may abuse system services or daemons to execute commands or programs. Adversaries can execute malicious content by interacting with or creating services either locally or remotely. Many services are set to run at boot, which can aid in achieving persistence (Create or Modify System Process), but adversaries can also abuse services for one-time or temporary execution."
  T1204 = "An adversary may rely upon specific actions by a user in order to gain execution. Users may be subjected to social engineering to get them to execute malicious code by, for example, opening a malicious document file or link. These user actions will typically be observed as follow-on behavior from forms of Phishing."
  T1047 = "Adversaries may abuse Windows Management Instrumentation (WMI) to execute malicious commands and payloads. WMI is an administration feature that provides a uniform environment to access Windows system components. The WMI service enables both local and remote access, though the latter is facilitated by Remote Services such as Distributed Component Object Model (DCOM) and Windows Remote Management (WinRM)."
  T1098 = "Adversaries may manipulate accounts to maintain access to victim systems. Account manipulation may consist of any action that preserves adversary access to a compromised account, such as modifying credentials or permission groups. These actions could also include account activity designed to subvert security policies, such as performing iterative password updates to bypass password duration policies and preserve the life of compromised credentials."
  T1197 = "Adversaries may abuse BITS jobs to persistently execute or clean up after malicious payloads. Windows Background Intelligent Transfer Service (BITS) is a low-bandwidth, asynchronous file transfer mechanism exposed through Component Object Model (COM). BITS is commonly used by updaters, messengers, and other applications preferred to operate in the background (using available idle bandwidth) without interrupting other networked applications."
  T1547 = "Adversaries may configure system settings to automatically execute a program during system boot or logon to maintain persistence or gain higher-level privileges on compromised systems. Operating systems may have mechanisms for automatically running a program on system boot or account logon. These mechanisms may include automatically executing programs that are placed in specially designated directories or are referenced by repositories that store configuration information, such as the Windows Registry."
  T1037 = "Adversaries may use scripts automatically executed at boot or logon initialization to establish persistence. Initialization scripts can be used to perform administrative functions, which may often execute other programs or send information to an internal logging server. These scripts can vary based on operating system and whether applied locally or remotely."
  T1176 = "Adversaries may abuse Internet browser extensions to establish persistent access to victim systems. Browser extensions or plugins are small programs that can add functionality and customize aspects of Internet browsers. They can be installed directly or through a browser's app store and generally have access and permissions to everything that the browser can access."
  T1554 = "Adversaries may modify client software binaries to establish persistent access to systems. Client software enables users to access services provided by a server. Common client software types are SSH clients, FTP clients, email clients, and web browsers."
  T1136 = "Adversaries may create an account to maintain access to victim systems. With a sufficient level of access, creating such accounts may be used to establish secondary credentialed access that do not require persistent remote access tools to be deployed on the system.Accounts may be created on the local system or within a domain or cloud tenant."
  T1543 = "Adversaries may create or modify system-level processes to repeatedly execute malicious payloads as part of persistence. When operating systems boot up, they can start processes that perform background system functions. On Windows and Linux, these system processes are referred to as services."
  T1546 = "Adversaries may establish persistence and/or elevate privileges using system mechanisms that trigger execution based on specific events. Various operating systems have means to monitor and subscribe to events such as logons or other user activity such as running specific applications/binaries. Adversaries may abuse these mechanisms as a means of maintaining persistent access to a victim via repeatedly executing malicious code."
  T1574 = "Adversaries may execute their own malicious payloads by hijacking the way operating systems run programs. Hijacking execution flow can be for the purposes of persistence, since this hijacked execution may reoccur over time. Adversaries may also use these mechanisms to elevate privileges or evade defenses, such as application control or other restrictions on execution."
  T1525 = "Adversaries may implant cloud or container images with malicious code to establish persistence after gaining access to an environment. Amazon Web Services (AWS) Amazon Machine Images (AMIs), Google Cloud Platform (GCP) Images, and Azure Images as well as popular container runtimes such as Docker can be implanted or backdoored. Unlike Upload Malware, this technique focuses on adversaries implanting an image in a registry within a victim's environment."
  T1556 = "Adversaries may modify authentication mechanisms and processes to access user credentials or enable otherwise unwarranted access to accounts. The authentication process is handled by mechanisms, such as the Local Security Authentication Server (LSASS) process and the Security Accounts Manager (SAM) on Windows, pluggable authentication modules (PAM) on Unix-based systems, and authorization plugins on MacOS systems, responsible for gathering, storing, and validating credentials. By modifying an authentication process, an adversary may be able to authenticate to a service or system without using Valid Accounts."
  T1137 = "Adversaries may leverage Microsoft Office-based applications for persistence between startups. Microsoft Office is a fairly common application suite on Windows-based operating systems within an enterprise network. There are multiple mechanisms that can be used with Office for persistence when an Office-based application is started, this can include the use of Office Template Macros and add-ins."
  T1542 = "Adversaries may abuse Pre-OS Boot mechanisms as a way to establish persistence on a system. During the booting process of a computer, firmware and various startup services are loaded before the operating system. These programs control flow of execution before the operating system takes control."
  T1505 = "Adversaries may abuse legitimate extensible development features of servers to establish persistent access to systems. Enterprise server applications may include features that allow developers to write and install software or scripts to extend the functionality of the main application. Adversaries may install malicious components to extend and abuse server applications."
  T1205 = "Adversaries may use traffic signaling to hide open ports or other malicious functionality used for persistence or command and control. Traffic signaling involves the use of a magic value or sequence that must be sent to a system to trigger a special response, such as opening a closed port or executing a malicious task. This may take the form of sending a series of packets with certain characteristics before a port will be opened that the adversary can use for command and control."
  T1548 = "Adversaries may circumvent mechanisms designed to control elevate privileges to gain higher-level permissions. Most modern systems contain native elevation control mechanisms that are intended to limit privileges that a user can perform on a machine. Authorization has to be granted to specific users in order to perform tasks that can be considered of higher risk."
  T1134 = "Adversaries may modify access tokens to operate under a different user or system security context to perform actions and bypass access controls. Windows uses access tokens to determine the ownership of a running process. A user can manipulate access tokens to make a running process appear as though it is the child of a different process or belongs to someone other than the user that started the process."
  T1484 = "Adversaries may modify the configuration settings of a domain to evade defenses and/or escalate privileges in domain environments. Domains provide a centralized means of managing how computer resources (ex= computers, user accounts) can act, and interact with each other, on a network. The policy of the domain also includes configuration settings that may apply between domains in a multi-domain/forest environment."
  T1611 = "Adversaries may break out of a container to gain access to the underlying host. This can allow an adversary access to other containerized resources from the host level or to the host itself. In principle, containerized resources should provide a clear separation of application functionality and be isolated from the host environment."
  T1068 = "Adversaries may exploit software vulnerabilities in an attempt to elevate privileges. Exploitation of a software vulnerability occurs when an adversary takes advantage of a programming error in a program, service, or within the operating system software or kernel itself to execute adversary-controlled code. Security constructs such as permission levels will often hinder access to information and use of certain techniques, so adversaries will likely need to perform privilege escalation to include use of software exploitation to circumvent those restrictions."
  T1055 = "Adversaries may inject code into processes in order to evade process-based defenses as well as possibly elevate privileges. Process injection is a method of executing arbitrary code in the address space of a separate live process. Running code in the context of another process may allow access to the process's memory, system/network resources, and possibly elevated privileges."
  T1612 = "Adversaries may build a container image directly on a host to bypass defenses that monitor for the retrieval of malicious images from a public registry. A remote build request may be sent to the Docker API that includes a Dockerfile that pulls a vanilla base image, such as alpine, from a public or local registry and then builds a custom image upon it.An adversary may take advantage of that build API to build a custom image on the host that includes malware downloaded from their C2 server, and then they then may utilize Deploy Container using that custom image."
  T1140 = "Adversaries may use Obfuscated Files or Information to hide artifacts of an intrusion from analysis. They may require separate mechanisms to decode or deobfuscate that information depending on how they intend to use it. Methods for doing that include built-in functionality of malware or by using utilities present on the system."
  T1006 = "Adversaries may directly access a volume to bypass file access controls and file system monitoring. Windows allows programs to have direct access to logical volumes. Programs with direct access may read and write files directly from the drive by analyzing file system data structures."
  T1480 = "Adversaries may use execution guardrails to constrain execution or actions based on adversary supplied and environment specific conditions that are expected to be present on the target. Guardrails ensure that a payload only executes against an intended target and reduces collateral damage from an adversary's campaign. Values an adversary can provide about a target system or environment to use as guardrails may include specific network share names, attached physical devices, files, joined Active Directory (AD) domains, and local/external IP addresses."
  T1211 = "Adversaries may exploit a system or application vulnerability to bypass security features. Exploitation of a software vulnerability occurs when an adversary takes advantage of a programming error in a program, service, or within the operating system software or kernel itself to execute adversary-controlled code. Vulnerabilities may exist in defensive security software that can be used to disable or circumvent them."
  T1222 = "Adversaries may modify file or directory permissions/attributes to evade access control lists (ACLs) and access protected files. File and directory permissions are commonly managed by ACLs configured by the file or directory owner, or users with the appropriate permissions. File and directory ACL implementations vary by platform, but generally explicitly designate which users or groups can perform which actions (read, write, execute, etc."
  T1564 = "Adversaries may attempt to hide artifacts associated with their behaviors to evade detection. Operating systems may have features to hide various artifacts, such as important system files and administrative task execution, to avoid disrupting user work environments and prevent users from changing files or features on the system. Adversaries may abuse these features to hide artifacts such as files, directories, user accounts, or other system activity to evade detection."
  T1562 = "Adversaries may maliciously modify components of a victim environment in order to hinder or disable defensive mechanisms. This not only involves impairing preventative defenses, such as firewalls and anti-virus, but also detection capabilities that defenders can use to audit activity and identify malicious behavior. This may also span both native defenses as well as supplemental capabilities installed by users and administrators."
  T1070 = "Adversaries may delete or alter generated artifacts on a host system, including logs or captured files such as quarantined malware. Locations and format of logs are platform or product-specific, however standard operating system logs are captured as Windows events or Linux/macOS files such as Bash History and /var/log/*.These actions may interfere with event collection, reporting, or other notifications used to detect intrusion activity."
  T1202 = "Adversaries may abuse utilities that allow for command execution to bypass security restrictions that limit the use of command-line interpreters. Various Windows utilities may be used to execute commands, possibly without invoking cmd. For example, Forfiles, the Program Compatibility Assistant (pcalua."
  T1036 = "Adversaries may attempt to manipulate features of their artifacts to make them appear legitimate or benign to users and/or security tools. Masquerading occurs when the name or location of an object, legitimate or malicious, is manipulated or abused for the sake of evading defenses and observation. This may include manipulating file metadata, tricking users into misidentifying the file type, and giving legitimate task or service names."
  T1578 = "An adversary may attempt to modify a cloud account's compute service infrastructure to evade defenses. A modification to the compute service infrastructure can include the creation, deletion, or modification of one or more components such as compute instances, virtual machines, and snapshots.Permissions gained from the modification of infrastructure components may bypass restrictions that prevent access to existing infrastructure."
  T1112 = "Adversaries may interact with the Windows Registry to hide configuration information within Registry keys, remove information as part of cleaning up, or as part of other techniques to aid in persistence and execution.Access to specific areas of the Registry depends on account permissions, some requiring administrator-level access. The built-in Windows command-line utility Reg may be used for local or remote Registry modification."
  T1601 = "Adversaries may make changes to the operating system of embedded network devices to weaken defenses and provide new capabilities for themselves.  On such devices, the operating systems are typically monolithic and most of the device functionality and capabilities are contained within a single file.To change the operating system, the adversary typically only needs to affect this one file, replacing or modifying it."
  T1599 = "Adversaries may bridge network boundaries by compromising perimeter network devices. Breaching these devices may enable an adversary to bypass restrictions on traffic routing that otherwise separate trusted and untrusted networks.Devices such as routers and firewalls can be used to create boundaries between trusted and untrusted networks."
  T1027 = "Adversaries may attempt to make an executable or file difficult to discover or analyze by encrypting, encoding, or otherwise obfuscating its contents on the system or in transit. This is common behavior that can be used across different platforms and the network to evade defenses. Payloads may be compressed, archived, or encrypted in order to avoid detection."
  T1207 = "Adversaries may register a rogue Domain Controller to enable manipulation of Active Directory data. DCShadow may be used to create a rogue Domain Controller (DC). DCShadow is a method of manipulating Active Directory (AD) data, including objects and schemas, by registering (or reusing an inactive registration) and simulating the behavior of a DC."
  T1014 = "Adversaries may use rootkits to hide the presence of programs, files, network connections, services, drivers, and other system components. Rootkits are programs that hide the existence of malware by intercepting/hooking and modifying operating system API calls that supply system information.  Rootkits or rootkit enabling functionality may reside at the user or kernel level in the operating system or lower, to include a hypervisor, Master Boot Record, or System Firmware."
  T1218 = "Adversaries may bypass process and/or signature-based defenses by proxying execution of malicious content with signed binaries. Binaries signed with trusted digital certificates can execute on Windows systems protected by digital signature validation. Several Microsoft signed binaries that are default on Windows installations can be used to proxy execution of other files."
  T1216 = "Adversaries may use scripts signed with trusted certificates to proxy execution of malicious files. Several Microsoft signed scripts that are default on Windows installations can be used to proxy execution of other files. This behavior may be abused by adversaries to execute malicious files that could bypass application control and signature validation on systems."
  T1553 = "Adversaries may undermine security controls that will either warn users of untrusted activity or prevent execution of untrusted programs. Operating systems and security products may contain mechanisms to identify programs or websites as possessing some level of trust. Examples of such features would include a program being allowed to run because it is signed by a valid code signing certificate, a program prompting the user with a warning because it has an attribute set from being downloaded from the Internet, or getting an indication that you are about to connect to an untrusted site."
  T1221 = "Adversaries may create or modify references in Office document templates to conceal malicious code or force authentication attempts. Microsoft's Office Open XML (OOXML) specification defines an XML-based format for Office documents (.docx, xlsx, ."
  T1127 = "Adversaries may take advantage of trusted developer utilities to proxy execution of malicious payloads. There are many utilities used for software development related tasks that can be used to execute code in various forms to assist in development, debugging, and reverse engineering. These utilities may often be signed with legitimate certificates that allow them to execute on a system and proxy execution of malicious code through a trusted process that effectively bypasses application control solutions."
  T1535 = "Adversaries may create cloud instances in unused geographic service regions in order to evade detection. Access is usually obtained through compromising accounts used to manage cloud infrastructure.Cloud service providers often provide infrastructure throughout the world in order to improve performance, provide redundancy, and allow customers to meet compliance requirements."
  T1550 = "Adversaries may use alternate authentication material, such as password hashes, Kerberos tickets, and application access tokens, in order to move laterally within an environment and bypass normal system access controls. Authentication processes generally require a valid identity (e.g."
  T1497 = "Adversaries may employ various means to detect and avoid virtualization and analysis environments. This may include changing behaviors based on the results of checks for the presence of artifacts indicative of a virtual machine environment (VME) or sandbox. If the adversary detects a VME, they may alter their malware to disengage from the victim or conceal the core functions of the implant."
  T1600 = "Adversaries may compromise a network device's encryption capability in order to bypass encryption that would otherwise protect data communications. Encryption can be used to protect transmitted network traffic to maintain its confidentiality (protect against unauthorized disclosure) and integrity (protect against unauthorized changes). Encryption ciphers are used to convert a plaintext message to ciphertext and can be computationally intensive to decipher without the associated decryption key."
  T1220 = "Adversaries may bypass application control and obscure execution of code by embedding scripts inside XSL files. Extensible Stylesheet Language (XSL) files are commonly used to describe the processing and rendering of data within XML files. To support complex operations, the XSL standard includes support for embedded scripting in various languages."
  T1110 = "Adversaries may use brute force techniques to gain access to accounts when passwords are unknown or when password hashes are obtained. Without knowledge of the password for an account or set of accounts, an adversary may systematically guess the password using a repetitive or iterative mechanism. Brute forcing passwords can take place via interaction with a service that will check the validity of those credentials or offline against previously acquired credential data, such as password hashes."
  T1555 = "Adversaries may search for common password storage locations to obtain user credentials. Passwords are stored in several places on a system, depending on the operating system or application holding the credentials. There are also specific applications that store passwords to make it easier for users manage and maintain."
  T1212 = "Adversaries may exploit software vulnerabilities in an attempt to collect credentials. Exploitation of a software vulnerability occurs when an adversary takes advantage of a programming error in a program, service, or within the operating system software or kernel itself to execute adversary-controlled code. Credentialing and authentication mechanisms may be targeted for exploitation by adversaries as a means to gain access to useful credentials or circumvent the process to gain access to systems."
  T1187 = "Adversaries may gather credential material by invoking or forcing a user to automatically provide authentication information through a mechanism in which they can intercept.The Server Message Block (SMB) protocol is commonly used in Windows networks for authentication and communication between systems for access to resources and file sharing. When a Windows system attempts to connect to an SMB resource it will automatically attempt to authenticate and send credential information for the current user to the remote system."
  T1606 = "Adversaries may forge credential materials that can be used to gain access to web applications or Internet services. Web applications and services (hosted in cloud SaaS environments or on-premise servers) often use session cookies, tokens, or other materials to authenticate and authorize user access.Adversaries may generate these credential materials in order to gain access to web resources."
  T1056 = "Adversaries may use methods of capturing user input to obtain credentials or collect information. During normal system usage, users often provide credentials to various different locations, such as login pages/portals or system dialog boxes. Input capture mechanisms may be transparent to the user (e."
  T1557 = "Adversaries may attempt to position themselves between two or more networked devices using an adversary-in-the-middle (AiTM) technique to support follow-on behaviors such as Network Sniffing or Transmitted Data Manipulation. By abusing features of common networking protocols that can determine the flow of network traffic (e.g."
  T1040 = "Adversaries may sniff network traffic to capture information about an environment, including authentication material passed over the network. Network sniffing refers to using the network interface on a system to monitor or capture information sent over a wired or wireless connection. An adversary may place a network interface into promiscuous mode to passively access data in transit over the network, or use span ports to capture a larger amount of data."
  T1003 = "Adversaries may attempt to dump credentials to obtain account login and credential material, normally in the form of a hash or a clear text password, from the operating system and software. Credentials can then be used to perform Lateral Movement and access restricted information.Several of the tools mentioned in associated sub-techniques may be used by both adversaries and professional security testers."
  T1528 = "Adversaries can steal user application access tokens as a means of acquiring credentials to access remote systems and resources. This can occur through social engineering and typically requires user action to grant access.Application access tokens are used to make authorized API requests on behalf of a user and are commonly used as a way to access resources in cloud-based applications and software-as-a-service (SaaS)."
  T1558 = "Adversaries may attempt to subvert Kerberos authentication by stealing or forging Kerberos tickets to enable Pass the Ticket. Kerberos is an authentication protocol widely used in modern Windows domain environments. In Kerberos environments, referred to as 'realms' there are three basic participants= client, service, and Key Distribution Center (KDC)"
  T1539 = "An adversary may steal web application or service session cookies and use them to gain access to web applications or Internet services as an authenticated user without needing credentials. Web applications and services often use session cookies as an authentication token after a user has authenticated to a website.Cookies are often valid for an extended period of time, even if the web application is not actively used."
  T1111 = "Adversaries may target two-factor authentication mechanisms, such as smart cards, to gain access to credentials that can be used to access systems, services, and network resources. Use of two or multi-factor authentication (2FA or MFA) is recommended and provides a higher level of security than user names and passwords alone, but organizations should be aware of techniques that could be used to intercept and bypass these security mechanisms. If a smart card is used for two-factor authentication, then a keylogger will need to be used to obtain the password associated with a smart card during normal use."
  T1552 = "Adversaries may search compromised systems to find and obtain insecurely stored credentials. These credentials can be stored and/or misplaced in many locations on a system, including plaintext files (e.g."
  T1087 = "Adversaries may attempt to get a listing of accounts on a system or within an environment. This information can help adversaries determine which accounts exist to aid in follow-on behavior."
  T1010 = "Adversaries may attempt to get a listing of open application windows. Window listings could convey information about how the system is used or give context to information collected by a keylogger."
  T1217 = "Adversaries may enumerate browser bookmarks to learn more about compromised hosts. Browser bookmarks may reveal personal information about users (ex= banking sites, interests, social media, etc.) as well as details about internal network resources such as servers, tools/dashboards, or other related infrastructure."
  T1580 = "An adversary may attempt to discover resources that are available within an infrastructure-as-a-service (IaaS) environment. This includes compute service resources such as instances, virtual machines, and snapshots as well as resources of other services including the storage and database services.Cloud providers offer methods such as APIs and commands issued through CLIs to serve information about infrastructure."
  T1538 = "An adversary may use a cloud service dashboard GUI with stolen credentials to gain useful information from an operational cloud environment, such as specific services, resources, and features. For example, the GCP Command Center can be used to view all assets, findings of potential security risks, and to run additional queries, such as finding public IP addresses and open ports.Depending on the configuration of the environment, an adversary may be able to enumerate more information via the graphical dashboard than an API."
  T1526 = "An adversary may attempt to enumerate the cloud services running on a system after gaining access. These methods can differ from platform-as-a-service (PaaS), to infrastructure-as-a-service (IaaS), or software-as-a-service (SaaS). Many services exist throughout the various cloud providers and can include Continuous Integration and Continuous Delivery (CI/CD), Lambda Functions, Azure AD, etc."
  T1613 = "Adversaries may attempt to discover containers and other resources that are available within a containers environment. Other resources may include images, deployments, pods, nodes, and other information such as the status of a cluster.These resources can be viewed within web applications such as the Kubernetes dashboard or can be queried via the Docker and Kubernetes APIs."
  T1482 = "Adversaries may attempt to gather information on domain trust relationships that may be used to identify lateral movement opportunities in Windows multi-domain/forest environments. Domain trusts provide a mechanism for a domain to allow access to resources based on the authentication procedures of another domain. Domain trusts allow the users of the trusted domain to access resources in the trusting domain."
  T1083 = "Adversaries may enumerate files and directories or may search in specific locations of a host or network share for certain information within a file system. Adversaries may use the information from File and Directory Discovery during automated discovery to shape follow-on behaviors, including whether or not the adversary fully infects the target and/or attempts specific actions.Many command shell utilities can be used to obtain this information."
  T1046 = "Adversaries may attempt to get a listing of services running on remote hosts, including those that may be vulnerable to remote software exploitation. Methods to acquire this information include port scans and vulnerability scans using tools that are brought onto a system. Within cloud environments, adversaries may attempt to discover services running on other cloud hosts."
  T1135 = "Adversaries may look for folders and drives shared on remote systems as a means of identifying sources of information to gather as a precursor for Collection and to identify potential systems of interest for Lateral Movement. Networks often contain shared network drives and folders that enable users to access file directories on various systems across a network. File sharing over a Windows network occurs over the SMB protocol."
  T1201 = "Adversaries may attempt to access detailed information about the password policy used within an enterprise network or cloud environment. Password policies are a way to enforce complex passwords that are difficult to guess or crack through Brute Force. This information may help the adversary to create a list of common passwords and launch dictionary and/or brute force attacks which adheres to the policy (e."
  T1120 = "Adversaries may attempt to gather information about attached peripheral devices and components connected to a computer system. Peripheral devices could include auxiliary resources that support a variety of functionalities such as keyboards, printers, cameras, smart card readers, or removable storage. The information may be used to enhance their awareness of the system and network environment or may be used for further actions."
  T1069 = "Adversaries may attempt to find group and permission settings. This information can help adversaries determine which user accounts and groups are available, the membership of users in particular groups, and which users and groups have elevated permissions."
  T1057 = "Adversaries may attempt to get information about running processes on a system. Information obtained could be used to gain an understanding of common software/applications running on systems within the network. Adversaries may use the information from Process Discovery during automated discovery to shape follow-on behaviors, including whether or not the adversary fully infects the target and/or attempts specific actions."
  T1012 = "Adversaries may interact with the Windows Registry to gather information about the system, configuration, and installed software.The Registry contains a significant amount of information about the operating system, configuration, software, and security. Information can easily be queried using the Reg utility, though other means to access the Registry exist."
  T1018 = "Adversaries may attempt to get a listing of other systems by IP address, hostname, or other logical identifier on a network that may be used for Lateral Movement from the current system. Functionality could exist within remote access tools to enable this, but utilities available on the operating system could also be used such as  Ping or net view using Net. Adversaries may also use local host files (ex= C=\\Windows\\System32\\Drivers\\etc\\hosts or /etc/hosts) in order to discover the hostname to IP address mappings of remote systems."
  T1518 = "Adversaries may attempt to get a listing of software and software versions that are installed on a system or in a cloud environment. Adversaries may use the information from Software Discovery during automated discovery to shape follow-on behaviors, including whether or not the adversary fully infects the target and/or attempts specific actions.Adversaries may attempt to enumerate software for a variety of reasons, such as figuring out what security measures are present or if the compromised system has a version of software that is vulnerable to Exploitation for Privilege Escalation."
  T1082 = "An adversary may attempt to get detailed information about the operating system and hardware, including version, patches, hotfixes, service packs, and architecture. Adversaries may use the information from System Information Discovery during automated discovery to shape follow-on behaviors, including whether or not the adversary fully infects the target and/or attempts specific actions.Tools such as Systeminfo can be used to gather detailed system information."
  T1614 = "Adversaries may gather information in an attempt to calculate the geographical location of a victim host. Adversaries may use the information from System Location Discovery during automated discovery to shape follow-on behaviors, including whether or not the adversary fully infects the target and/or attempts specific actions.Adversaries may attempt to infer the location of a system using various system checks, such as time zone, keyboard layout, and/or language settings."
  T1016 = "Adversaries may look for details about the network configuration and settings, such as IP and/or MAC addresses, of systems they access or through information discovery of remote systems. Several operating system administration utilities exist that can be used to gather this information. Examples include Arp, ipconfig/ifconfig, nbtstat, and route."
  T1049 = "Adversaries may attempt to get a listing of network connections to or from the compromised system they are currently accessing or from remote systems by querying for information over the network. An adversary who gains access to a system that is part of a cloud-based environment may map out Virtual Private Clouds or Virtual Networks in order to determine what systems and services are connected. The actions performed are likely the same types of discovery techniques depending on the operating system, but the resulting information may include details about the networked cloud environment relevant to the adversary's goals."
  T1033 = "Adversaries may attempt to identify the primary user, currently logged in user, set of users that commonly uses a system, or whether a user is actively using the system. They may do this, for example, by retrieving account usernames or by using OS Credential Dumping. The information may be collected in a number of different ways using other Discovery techniques, because user and username details are prevalent throughout a system and include running process ownership, file/directory ownership, session information, and system logs."
  T1007 = "Adversaries may try to get information about registered services. Commands that may obtain information about services using operating system utilities are 'sc', 'tasklist /svc' using Tasklist, and 'net start' using Net, but adversaries may also use other tools as well. Adversaries may use the information from System Service Discovery during automated discovery to shape follow-on behaviors, including whether or not the adversary fully infects the target and/or attempts specific actions."
  T1124 = "An adversary may gather the system time and/or time zone from a local or remote system. The system time is set and stored by the Windows Time Service within a domain to maintain time synchronization between systems and services in an enterprise network.  System time information may be gathered in a number of ways, such as with Net on Windows by performing net time \\hostname to gather the system time on a remote system."
  T1210 = "Adversaries may exploit remote services to gain unauthorized access to internal systems once inside of a network. Exploitation of a software vulnerability occurs when an adversary takes advantage of a programming error in a program, service, or within the operating system software or kernel itself to execute adversary-controlled code. A common goal for post-compromise exploitation of remote services is for lateral movement to enable access to a remote system."
  T1534 = "Adversaries may use internal spearphishing to gain access to additional information or exploit other users within the same organization after they already have access to accounts or systems within the environment. Internal spearphishing is multi-staged attack where an email account is owned either by controlling the user's device with previously installed malware or by compromising the account credentials of the user. Adversaries attempt to take advantage of a trusted internal account to increase the likelihood of tricking the target into falling for the phish attempt."
  T1570 = "Adversaries may transfer tools or other files between systems in a compromised environment. Files may be copied from one system to another to stage adversary tools or other files over the course of an operation. Adversaries may copy files laterally between internal victim systems to support lateral movement using inherent file sharing protocols such as file sharing over SMB to connected network shares or with authenticated connections with SMB/Windows Admin Shares or Remote Desktop Protocol."
  T1563 = "Adversaries may take control of preexisting sessions with remote services to move laterally in an environment. Users may use valid credentials to log into a service specifically designed to accept remote connections, such as telnet, SSH, and RDP. When a user logs into a service, a session will be established that will allow them to maintain a continuous interaction with that service."
  T1021 = "Adversaries may use Valid Accounts to log into a service specifically designed to accept remote connections, such as telnet, SSH, and VNC. The adversary may then perform actions as the logged-on user.In an enterprise environment, servers and workstations can be organized into domains."
  T1080 = "Adversaries may deliver payloads to remote systems by adding content to shared storage locations, such as network drives or internal code repositories. Content stored on network drives or in other shared locations may be tainted by adding malicious programs, scripts, or exploit code to otherwise valid files. Once a user opens the shared tainted content, the malicious portion can be executed to run the adversary's code on a remote system."
  T1560 = "An adversary may compress and/or encrypt data that is collected prior to exfiltration. Compressing the data can help to obfuscate the collected data and minimize the amount of data sent over the network. Encryption can be used to hide information that is being exfiltrated from detection or make exfiltration less conspicuous upon inspection by a defender."
  T1123 = "An adversary can leverage a computer's peripheral devices (e.g., microphones and webcams) or applications (e."
  T1119 = "Once established within a system or network, an adversary may use automated techniques for collecting internal data. Methods for performing this technique could include use of a Command and Scripting Interpreter to search for and copy information fitting set criteria such as file type, location, or name at specific time intervals. This functionality could also be built into remote access tools."
  T1115 = "Adversaries may collect data stored in the clipboard from users copying information within or between applications. In Windows, Applications can access clipboard data by using the Windows API. OSX provides a native command, pbpaste, to grab clipboard contents."
  T1530 = "Adversaries may access data objects from improperly secured cloud storage.Many cloud service providers offer solutions for online data storage such as Amazon S3, Azure Storage, and Google Cloud Storage. These solutions differ from other storage solutions (such as SQL or Elasticsearch) in that there is no overarching application."
  T1602 = "Adversaries may collect data related to managed devices from configuration repositories. Configuration repositories are used by management systems in order to configure, manage, and control data on remote systems. Configuration repositories may also facilitate remote access and administration of devices."
  T1213 = "Adversaries may leverage information repositories to mine valuable information. Information repositories are tools that allow for storage of information, typically to facilitate collaboration or information sharing between users, and can store a wide variety of data that may aid adversaries in further objectives, or direct access to the target information. Adversaries may also abuse external sharing features to share sensitive documents with recipients outside of the organization."
  T1005 = "Adversaries may search local system sources, such as file systems or local databases, to find files of interest and sensitive data prior to Exfiltration.Adversaries may do this using a Command and Scripting Interpreter, such as cmd, which has functionality to interact with the file system to gather information. Some adversaries may also use Automated Collection on the local system."
  T1039 = "Adversaries may search network shares on computers they have compromised to find files of interest. Sensitive data can be collected from remote systems via shared network drives (host shared directory, network file server, etc.) that are accessible from the current system prior to Exfiltration."
  T1025 = "Adversaries may search connected removable media on computers they have compromised to find files of interest. Sensitive data can be collected from any removable media (optical disk drive, USB memory, etc.) connected to the compromised system prior to Exfiltration."
  T1074 = "Adversaries may stage collected data in a central location or directory prior to Exfiltration. Data may be kept in separate files or combined into one file through techniques such as Archive Collected Data. Interactive command shells may be used, and common functionality within cmd and bash may be used to copy data into a staging location."
  T1114 = "Adversaries may target user email to collect sensitive information. Emails may contain sensitive data, including trade secrets or personal information, that can prove valuable to adversaries. Adversaries can collect or forward email from mail servers or clients."
  T1185 = "Adversaries may take advantage of security vulnerabilities and inherent functionality in browser software to change content, modify user-behaviors, and intercept information as part of various browser session hijacking techniques.A specific example is when an adversary injects software into a browser that allows them to inherit cookies, HTTP sessions, and SSL client certificates of a user then use the browser as a way to pivot into an authenticated intranet. Executing browser-based behaviors such as pivoting may require specific process permissions, such as SeDebugPrivilege and/or high-integrity/administrator rights."
  T1113 = "Adversaries may attempt to take screen captures of the desktop to gather information over the course of an operation. Screen capturing functionality may be included as a feature of a remote access tool used in post-compromise operations. Taking a screenshot is also typically possible through native utilities or API calls, such as CopyFromScreen, xwd, or screencapture."
  T1125 = "An adversary can leverage a computer's peripheral devices (e.g., integrated cameras or webcams) or applications (e."
  T1071 = "Adversaries may communicate using application layer protocols to avoid detection/network filtering by blending in with existing traffic. Commands to the remote system, and often the results of those commands, will be embedded within the protocol traffic between the client and server. Adversaries may utilize many different protocols, including those used for web browsing, transferring files, electronic mail, or DNS."
  T1092 = "Adversaries can perform command and control between compromised hosts on potentially disconnected networks using removable media to transfer commands from system to system. Both systems would need to be compromised, with the likelihood that an Internet-connected system was compromised first and the second through lateral movement by Replication Through Removable Media. Commands and files would be relayed from the disconnected system to the Internet-connected system to which the adversary has direct access."
  T1132 = "Adversaries may encode data to make the content of command and control traffic more difficult to detect. Command and control (C2) information can be encoded using a standard data encoding system. Use of data encoding may adhere to existing protocol specifications and includes use of ASCII, Unicode, Base64, MIME, or other binary-to-text and character encoding systems."
  T1001 = "Adversaries may obfuscate command and control traffic to make it more difficult to detect. Command and control (C2) communications are hidden (but not necessarily encrypted) in an attempt to make the content more difficult to discover or decipher and to make the communication less conspicuous and hide commands from being seen. This encompasses many methods, such as adding junk data to protocol traffic, using steganography, or impersonating legitimate protocols."
  T1568 = "Adversaries may dynamically establish connections to command and control infrastructure to evade common detections and remediations. This may be achieved by using malware that shares a common algorithm with the infrastructure the adversary uses to receive the malware's communications. These calculations can be used to dynamically adjust parameters such as the domain name, IP address, or port number the malware uses for command and control."
  T1573 = "Adversaries may employ a known encryption algorithm to conceal command and control traffic rather than relying on any inherent protections provided by a communication protocol. Despite the use of a secure algorithm, these implementations may be vulnerable to reverse engineering if secret keys are encoded and/or generated within malware samples/configuration files."
  T1008 = "Adversaries may use fallback or alternate communication channels if the primary channel is compromised or inaccessible in order to maintain reliable command and control and to avoid data transfer thresholds."
  T1105 = "Adversaries may transfer tools or other files from an external system into a compromised environment. Files may be copied from an external adversary controlled system through the command and control channel to bring tools into the victim network or through alternate protocols with another tool such as FTP. Files can also be copied over on Mac and Linux with native tools like scp, rsync, and sftp."
  T1104 = "Adversaries may create multiple stages for command and control that are employed under different conditions or for certain functions. Use of multiple stages may obfuscate the command and control channel to make detection more difficult.Remote access tools will call back to the first-stage command and control server for instructions."
  T1095 = "Adversaries may use a non-application layer protocol for communication between host and C2 server or among infected hosts within a network. The list of possible protocols is extensive. Specific examples include use of network layer protocols, such as the Internet Control Message Protocol (ICMP), transport layer protocols, such as the User Datagram Protocol (UDP), session layer protocols, such as Socket Secure (SOCKS), as well as redirected/tunneled protocols, such as Serial over LAN (SOL)."
  T1571 = "Adversaries may communicate using a protocol and port paring that are typically not associated. For example, HTTPS over port  or port  as opposed to the traditional port 443. Adversaries may make changes to the standard port used by a protocol to bypass filtering or muddle analysis/parsing of network data."
  T1572 = "Adversaries may tunnel network communications to and from a victim system within a separate protocol to avoid detection/network filtering and/or enable access to otherwise unreachable systems. Tunneling involves explicitly encapsulating a protocol within another. This behavior may conceal malicious traffic by blending in with existing traffic and/or provide an outer layer of encryption (similar to a VPN)."
  T1090 = "Adversaries may use a connection proxy to direct network traffic between systems or act as an intermediary for network communications to a command and control server to avoid direct connections to their infrastructure. Many tools exist that enable traffic redirection through proxies or port redirection, including HTRAN, ZXProxy, and ZXPortMap.  Adversaries use these types of proxies to manage command and control communications, reduce the number of simultaneous outbound network connections, provide resiliency in the face of connection loss, or to ride over existing trusted communications paths between victims to avoid suspicion."
  T1219 = "An adversary may use legitimate desktop support and remote access software, such as Team Viewer, Go2Assist, LogMein, AmmyyAdmin, etc, to establish an interactive command and control channel to target systems within networks. These services are commonly used as legitimate technical support software, and may be allowed by application control within a target environment. Remote access tools like VNC, Ammyy, and Teamviewer are used frequently when compared with other legitimate software commonly used by adversaries."
  T1102 = "Adversaries may use an existing, legitimate external Web service as a means for relaying data to/from a compromised system. Popular websites and social media acting as a mechanism for C2 may give a significant amount of cover due to the likelihood that hosts within a network are already communicating with them prior to a compromise. Using common services, such as those offered by Google or Twitter, makes it easier for adversaries to hide in expected noise."
  T1020 = "Adversaries may exfiltrate data, such as sensitive documents, through the use of automated processing after being gathered during Collection. When automated exfiltration is used, other exfiltration techniques likely apply as well to transfer the information out of the network, such as Exfiltration Over C2 Channel and Exfiltration Over Alternative Protocol."
  T1030 = "An adversary may exfiltrate data in fixed size chunks instead of whole files or limit packet sizes below certain thresholds. This approach may be used to avoid triggering network data transfer threshold alerts."
  T1048 = "Adversaries may steal data by exfiltrating it over a different protocol than that of the existing command and control channel. The data may also be sent to an alternate network location from the main command and control server.  Alternate protocols include FTP, SMTP, HTTP/S, DNS, SMB, or any other network protocol not being used as the main command and control channel."
  T1041 = "Adversaries may steal data by exfiltrating it over an existing command and control channel. Stolen data is encoded into the normal communications channel using the same protocol as command and control communications."
  T1011 = "Adversaries may attempt to exfiltrate data over a different network medium than the command and control channel. If the command and control network is a wired Internet connection, the exfiltration may occur, for example, over a WiFi connection, modem, cellular data connection, Bluetooth, or another radio frequency (RF) channel.Adversaries may choose to do this if they have sufficient access or proximity, and the connection might not be secured or defended as well as the primary Internet-connected channel because it is not routed through the same enterprise network."
  T1052 = "Adversaries may attempt to exfiltrate data via a physical medium, such as a removable drive. In certain circumstances, such as an air-gapped network compromise, exfiltration could occur via a physical medium or device introduced by a user. Such media could be an external hard drive, USB drive, cellular phone, MP3 player, or other removable storage and processing device."
  T1567 = "Adversaries may use an existing, legitimate external Web service to exfiltrate data rather than their primary command and control channel. Popular Web services acting as an exfiltration mechanism may give a significant amount of cover due to the likelihood that hosts within a network are already communicating with them prior to compromise. Firewall rules may also already exist to permit traffic to these services."
  T1029 = "Adversaries may schedule data exfiltration to be performed only at certain times of day or at certain intervals. This could be done to blend traffic patterns with normal activity or availability.When scheduled exfiltration is used, other exfiltration techniques likely apply as well to transfer the information out of the network, such as Exfiltration Over C2 Channel or Exfiltration Over Alternative Protocol."
  T1537 = "Adversaries may exfiltrate data by transferring the data, including backups of cloud environments, to another cloud account they control on the same service to avoid typical file transfers/downloads and network-based exfiltration detection.A defender who is monitoring for large transfers to outside the cloud environment through normal file transfers or over command and control channels may not be watching for data transfers to another account within the same cloud provider. Such transfers may utilize existing cloud provider APIs and the internal address space of the cloud provider to blend into normal traffic or avoid data transfers over external network interfaces."
  T1531 = "Adversaries may interrupt availability of system and network resources by inhibiting access to accounts utilized by legitimate users. Accounts may be deleted, locked, or manipulated (ex= changed credentials) to remove access to accounts.Adversaries may also subsequently log off and/or reboot boxes to set malicious changes into place."
  T1485 = "Adversaries may destroy data and files on specific systems or in large numbers on a network to interrupt availability to systems, services, and network resources. Data destruction is likely to render stored data irrecoverable by forensic techniques through overwriting files or data on local and remote drives. Common operating system file deletion commands such as del and rm often only remove pointers to files without wiping the contents of the files themselves, making the files recoverable by proper forensic methodology."
  T1486 = "Adversaries may encrypt data on target systems or on large numbers of systems in a network to interrupt availability to system and network resources. They can attempt to render stored data inaccessible by encrypting files or data on local and remote drives and withholding access to a decryption key. This may be done in order to extract monetary compensation from a victim in exchange for decryption or a decryption key (ransomware) or to render data permanently inaccessible in cases where the key is not saved or transmitted."
  T1565 = "Adversaries may insert, delete, or manipulate data in order to manipulate external outcomes or hide activity. By manipulating data, adversaries may attempt to affect a business process, organizational understanding, or decision making.The type of modification and the impact it will have depends on the target application and process as well as the goals and objectives of the adversary."
  T1491 = "Adversaries may modify visual content available internally or externally to an enterprise network. Reasons for Defacement include delivering messaging, intimidation, or claiming (possibly false) credit for an intrusion. Disturbing or offensive images may be used as a part of Defacement in order to cause user discomfort, or to pressure compliance with accompanying messages."
  T1561 = "Adversaries may wipe or corrupt raw disk data on specific systems or in large numbers in a network to interrupt availability to system and network resources. With direct write access to a disk, adversaries may attempt to overwrite portions of disk data. Adversaries may opt to wipe arbitrary portions of disk data and/or wipe disk structures like the master boot record (MBR)."
  T1499 = "Adversaries may perform Endpoint Denial of Service (DoS) attacks to degrade or block the availability of services to users. Endpoint DoS can be performed by exhausting the system resources those services are hosted on or exploiting the system to cause a persistent crash condition. Example services include websites, email services, DNS, and web-based applications."
  T1495 = "Adversaries may overwrite or corrupt the flash memory contents of system BIOS or other firmware in devices attached to a system in order to render them inoperable or unable to boot. Firmware is software that is loaded and executed from non-volatile memory on hardware devices in order to initialize and manage device functionality. These devices could include the motherboard, hard drive, or video cards."
  T1490 = "Adversaries may delete or remove built-in operating system data and turn off services designed to aid in the recovery of a corrupted system to prevent recovery. Operating systems may contain features that can help fix corrupted systems, such as a backup catalog, volume shadow copies, and automatic repair features. Adversaries may disable or delete system recovery features to augment the effects of Data Destruction and Data Encrypted for Impact."
  T1498 = "Adversaries may perform Network Denial of Service (DoS) attacks to degrade or block the availability of targeted resources to users. Network DoS can be performed by exhausting the network bandwidth services rely on. Example resources include specific websites, email services, DNS, and web-based applications."
  T1496 = "Adversaries may leverage the resources of co-opted systems in order to solve resource intensive problems which may impact system and/or hosted service availability. One common purpose for Resource Hijacking is to validate transactions of cryptocurrency networks and earn virtual currency. Adversaries may consume enough system resources to negatively impact and/or cause affected machines to become unresponsive."
  T1489 = "Adversaries may stop or disable services on a system to render those services unavailable to legitimate users. Stopping critical services or processes can inhibit or stop response to an incident or aid in the adversary's overall objectives to cause damage to the environment. Adversaries may accomplish this by disabling individual services of high importance to an organization, such as MSExchangeIS, which will make Exchange content inaccessible ."
  T1529 = "Adversaries may shutdown/reboot systems to interrupt access to, or aid in the destruction of, those systems. Operating systems may contain commands to initiate a shutdown/reboot of a machine. In some cases, these commands may also be used to initiate a shutdown/reboot of a remote computer."
  T806  = "Adversaries may repetitively or successively change I/O point values to perform an action. Brute Force I/O may be achieved by changing either a range of I/O point values or a single point value repeatedly to manipulate a process function. The adversary's goal and the information they have about the target environment will influence which of the options they choose."
  T836  = "Adversaries may modify parameters used to instruct industrial control system devices. These devices operate via programs that dictate how and when to perform actions based on such parameters. Such parameters can determine the extent to which an action is performed and may specify additional options."
  T0839 = "Adversaries may install malicious or vulnerable firmware onto modular hardware devices. Control system devices often contain modular hardware devices. These devices may have their own set of firmware that is separate from the firmware of the main control system equipment."
  T0856 = "Adversaries may spoof reporting messages in control system environments for evasion and to impair process control. In control systems, reporting messages contain telemetry data (e.g."
  T0855 = "Adversaries may send unauthorized command messages to instruct control system assets to perform actions outside of their intended functionality, or without the logical preconditions to trigger their expected function. Command messages are used in ICS networks to give direct instructions to control systems devices. If an adversary can send an unauthorized command message to a control system, then it can instruct the control systems device to perform an action outside the normal bounds of the device's actions."
  T0800 = "Adversaries may activate firmware update mode on devices to prevent expected response functions from engaging in reaction to an emergency or process malfunction. For example, devices such as protection relays may have an operation mode designed for firmware installation. This mode may halt process monitoring and related functions to allow new firmware to be loaded."
  T0878 = "Adversaries may target protection function alarms to prevent them from notifying operators of critical conditions. Alarm messages may be a part of an overall reporting system and of particular interest for adversaries. Disruption of the alarm system does not imply the disruption of the reporting system as a whole."
  T0803 = "Adversaries may block a command message from reaching its intended target to prevent command execution. In OT networks, command messages are sent to provide instructions to control system devices. A blocked command message can inhibit response functions from correcting a disruption or unsafe condition."
  T0804 = "Adversaries may block or prevent a reporting message from reaching its intended target. In control systems, reporting messages contain telemetry data (e.g."
  T0805 = "Adversaries may block access to serial COM to prevent instructions or configurations from reaching target devices. Serial Communication ports (COM) allow communication with control system devices. Devices can receive command and configuration messages over such serial COM."
  T0809 = "Adversaries may perform data destruction over the course of an operation. The adversary may drop or create malware, tools, or other non-native files on a target system to accomplish this, potentially leaving behind traces of malicious activities. Such non-native files and other data may be removed over the course of an intrusion to maintain a small footprint or as a standard part of the post-intrusion cleanup process."
  T0814 = "Adversaries may perform Denial-of-Service (DoS) attacks to disrupt expected device functionality. Examples of DoS attacks include overwhelming the target device with a high volume of requests in a short time period and sending the target device a request it does not know how to handle. Disrupting device state may temporarily render it unresponsive, possibly lasting until a reboot can occur."
  T0816 = "Adversaries may forcibly restart or shutdown a device in an ICS environment to disrupt and potentially negatively impact physical processes. Methods of device restart and shutdown exist in some devices as built-in, standard functionalities. These functionalities can be executed using interactive device web interfaces, CLIs, and network protocol commands."
  T0835 = "Adversaries may manipulate the I/O image of PLCs through various means to prevent them from functioning as expected. Methods of I/O image manipulation may include overriding the I/O table via direct memory manipulation or using the override function used for testing PLC programs.1 During the scan cycle, a PLC reads the status of all inputs and stores them in an image table."
  T0838 = "Adversaries may modify alarm settings to prevent alerts that may inform operators of their presence or to prevent responses to dangerous and unintended scenarios. Reporting messages are a standard part of data acquisition in control systems. Reporting messages are used as a way to transmit system state information and acknowledgements that specific actions have occurred."
  T0851 = "Adversaries may deploy rootkits to hide the presence of programs, files, network connections, services, drivers, and other system components. Rootkits are programs that hide the existence of malware by intercepting and modifying operating-system API calls that supply system information. Rootkits or rootkit-enabling functionality may reside at the user or kernel level in the operating system, or lower."
  T0881 = "Adversaries may stop or disable services on a system to render those services unavailable to legitimate users. Stopping critical services can inhibit or stop response to an incident or aid in the adversary's overall objectives to cause damage to the environment.1."
  T0857 = "System firmware on modern assets is often designed with an update feature. Older device firmware may be factory installed and require special reprograming equipment. When available, the firmware update feature enables vendors to remotely patch bugs and perform upgrades."
  T0836 = "Adversaries may modify parameters used to instruct industrial control system devices. These devices operate via programs that dictate how and when to perform actions based on such parameters. Such parameters can determine the extent to which an action is performed and may specify additional options."
  T0830 = "Adversaries with privileged network access may seek to modify network traffic in real time using man-in-the-middle (MITM) attacks.1 This type of attack allows the adversary to intercept traffic to and/or from a particular device on the network. If a MITM attack is established, then the adversary has the ability to block, log, modify, or inject traffic into the communication stream."
  T0868 = "Adversaries may gather information about a PLC's or controller's current operating mode. Operating modes dictate what change or maintenance functions can be manipulated and are often controlled by a key switch on the PLC (e.g."
  T0861 = "Adversaries may collect point and tag values to gain a more comprehensive understanding of the process environment. Points may be values such as inputs, memory locations, outputs or other process specific variables.1 Tags are the identifiers given to points for operator convenience."
  T0834 = "Adversaries may directly interact with the native OS application programming interface (API) to access system functions. Native APIs provide a controlled means of calling low-level OS services within the kernel, such as those involving hardware/devices, memory, and processes.1 These native APIs are leveraged by the OS during system boot (when other system components are not yet initialized) as well as carrying out tasks and requests during routine operations."
  T0802 = "Adversaries may automate collection of industrial environment information using tools or scripts. This automated collection may leverage native control protocols and tools available in the control systems environment. For example, the OPC protocol may be used to enumerate and gather information."
  T0852 = "Adversaries may attempt to perform screen capture of devices in the control system environment. Screenshots may be taken of workstations, HMIs, or other devices that display environment-relevant process, device, reporting, alarm, or related data. These device displays may reveal information regarding the ICS process, layout, control, and related schematics."
  T0801 = "Adversaries may gather information about the physical process state. This information may be used to gain more information about the process itself or used as a trigger for malicious actions. The sources of process state information may vary such as, OPC tags, historian data, specific PLC block information, or network traffic."
  T0843 = "Adversaries may perform a program download to transfer a user program to a controller."
  T0811 = "Adversaries may target and collect data from information repositories. This can include sensitive data such as specifications, schematics, or diagrams of control system layouts, devices, and processes. Examples of information repositories include reference databases or local machines in the process environment, as well as workstations and databases in the corporate network that might contain information about the ICS."
  T0877 = "Adversaries may seek to capture process values related to the inputs and outputs of a PLC. During the scan cycle, a PLC reads the status of all inputs and stores them in an image table.1 The image table is the PLC's internal storage location where values of inputs/outputs for one scan are stored while it executes the user program."
  T0887 = "Adversaries may seek to capture radio frequency (RF) communication used for remote control and reporting in distributed environments. RF communication frequencies vary between 3 kHz to 300 GHz, although are commonly between 300 MHz to 6 GHz.1  The wavelength and frequency of the signal affect how the signal propagates through open air, obstacles (e."
  T0845 = "Adversaries may attempt to upload a program from a PLC to gather information about an industrial process. Uploading a program may allow them to acquire and study the underlying logic. Methods of program upload include vendor software, which enables the user to upload and read a program running on a PLC."
  T0885 = "Adversaries may communicate over a commonly used port to bypass firewalls or network detection systems and to blend in with normal network activity, to avoid more detailed inspection. They may use the protocol associated with the port, or a completely different protocol. They may use commonly open ports, such as the examples provided below."
  T0869 = "Adversaries may establish command and control capabilities over commonly used application layer protocols such as HTTP(S), OPC, RDP, telnet, DNP3, and modbus. These protocols may be used to disguise adversary actions as benign network traffic. Standard protocols may be seen on their associated port or in some cases over a non-standard port."
  T0884 = "Adversaries may use a connection proxy to direct network traffic between systems or act as an intermediary for network communications."
  T0846 = "Adversaries may attempt to get a listing of other systems by IP address, hostname, or other logical identifier on a network that may be used for subsequent Lateral Movement or Discovery techniques. Functionality could exist within adversary tools to enable this, but utilities available on the operating system or vendor software could also be used.1."
  T0842 = "Network sniffing is the practice of using a network interface on a computer system to monitor or capture information1 regardless of whether it is the specified destination for the information."
  T0888 = "An adversary may attempt to get detailed information about remote systems and their peripherals, such as make/model, role, and configuration. Adversaries may use information from Remote System Information Discovery to aid in targeting and shaping follow-on behaviors. For example, the system's operational role and model information can dictate whether it is a relevant target for the adversary's operational objectives."
  T0840 = "Adversaries may perform network connection enumeration to discover information about device communication patterns. If an adversary can inspect the state of a network connection with tools, such as netstat, in conjunction with System Firmware, then they can determine the role of certain devices on the network 1. The adversary can also use Network Sniffing to watch network traffic for details about the source, destination, protocol, and content."
  T0858 = "Adversaries may change the operating mode of a controller to gain additional access to engineering functions such as Program Download."
  T0849 = "Adversaries may use masquerading to disguise a malicious application or executable as another file, to avoid operator and engineer suspicion. Possible disguises of these masquerading files can include commonly found programs, expected vendor executables and configuration files, and other commonplace application and naming conventions. By impersonating expected and vendor-relevant files and applications, operators and engineers may not notice the presence of the underlying malicious content and possibly end up running those masquerading as legitimate functions."
  T0872 = "Adversaries may attempt to remove indicators of their presence on a system in an effort to cover their tracks. In cases where an adversary may feel detection is imminent, they may try to overwrite, delete, or cover up changes they have made to the device."
  T0820 = "Adversaries may exploit a software vulnerability to take advantage of a programming error in a program, service, or within the operating system software or kernel itself to evade detection. Vulnerabilities may exist in software that can be used to disable or circumvent security features."
  T0821 = "Adversaries may modify the tasking of a controller to allow for the execution of their own programs. This can allow an adversary to manipulate the execution flow and behavior of a controller."
  T0874 = "Adversaries may hook into application programming interface (API) functions used by processes to redirect calls for execution and privilege escalation means. Windows processes often leverage these API functions to perform tasks that require reusable system resources. Windows API functions are typically stored in dynamic-link libraries (DLLs) as exported functions."
  T0863 = "Adversaries may rely on a targeted organizations' user interaction for the execution of malicious code. User interaction may consist of installing applications, opening email attachments, or granting higher permissions to documents."
  T0853 = "Adversaries may use scripting languages to execute arbitrary code in the form of a pre-written script or in the form of user-supplied code to an interpreter. Scripting languages are programming languages that differ from compiled languages, in that scripting languages use an interpreter, instead of a compiler. These interpreters read and compile part of the source code just before it is executed, as opposed to compilers, which compile each and every line of code to an executable file."
  T0871 = "Adversaries may attempt to leverage Application Program Interfaces (APIs) used for communication between control software and the hardware. Specific functionality is often coded into APIs which can be called by software to engage specific functions on a device or other software."
  T0823 = "Adversaries may attempt to gain access to a machine via a Graphical User Interface (GUI) to enhance execution capabilities. Access to a GUI allows a user to interact with a computer in a more visual manner than a CLI. A GUI allows users to move a cursor and click on interface objects, with a mouse and keyboard as the main input devices, as opposed to just using the keyboard."
  T0807 = "Adversaries may utilize command-line interfaces (CLIs) to interact with systems and execute commands. CLIs provide a means of interacting with computer systems and are a common feature across many types of platforms and devices within control systems environments.1 Adversaries may also use CLIs to install and run new software, including malicious tools that may be installed over the course of an operation."
  T0813 = "Adversaries may cause a denial of control to temporarily prevent operators and engineers from interacting with process controls. An adversary may attempt to deny process control access to cause a temporary loss of communication with the control device or to prevent operator adjustment of process controls. An affected process may still be operating during the period of control loss, but not necessarily in a desired state."
  T0827 = "Adversaries may seek to achieve a sustained loss of control or a runaway condition in which operators cannot issue any commands even if the malicious interference has subsided.123."
  T0829 = "Adversaries may cause a sustained or permanent loss of view where the ICS equipment will require local, hands-on operator intervention, for instance, a restart or manual operation. By causing a sustained reporting or visibility loss, the adversary can effectively hide the present state of operations. This loss of view can occur without affecting the physical processes themselves."
  T0831 = "Adversaries may manipulate physical process control within the industrial environment. Methods of manipulating control can include changes to set point values, tags, or other parameters. Adversaries may manipulate control systems devices or possibly leverage their own, to communicate with and command physical control processes."
  T0832 = "Adversaries may attempt to manipulate the information reported back to operators or controllers. This manipulation may be short term or sustained. During this time the process itself could be in a much different state than what is reported."
  T0882 = "Adversaries may steal operational information on a production environment as a direct mission outcome for personal gain or to inform future operations. This information may include design documents, schedules, rotational data, or similar artifacts that provide insight on operations."
  T0815 = "Adversaries may cause a denial of view in attempt to disrupt and prevent operator oversight on the status of an ICS environment. This may manifest itself as a temporary communication failure between a device and its control source, where the interface recovers and becomes available once the interference ceases.123."
  T0826 = "Adversaries may attempt to disrupt essential components or systems to prevent owner and operator from delivering products or services.123."
  T0837 = "Adversaries may compromise protective system functions designed to prevent the effects of faults and abnormal conditions. This can result in equipment damage, prolonged process disruptions and hazards to personnel."
  T0828 = "Adversaries may cause loss of productivity and revenue through disruption and even damage to the availability and integrity of control system operations, devices, and related processes. This technique may manifest as a direct effect of an ICS-targeting attack or tangentially, due to an IT-targeting attack against non-segregated environments."
  T0880 = "Adversaries may compromise safety system functions designed to maintain safe operation of a process when unacceptable or dangerous conditions occur. Safety systems are often composed of the same elements as control systems but have the sole purpose of ensuring the process fails in a predetermined safe manner."
  T0879 = "Adversaries may cause damage and destruction of property to infrastructure, equipment, and the surrounding environment when attacking control systems. This technique may result in device and operational equipment breakdown, or represent tangential damage from other techniques used in an attack. Depending on the severity of physical damage and disruption caused to control processes and systems, this technique may result in Loss of Safety."
  T0806 = "Adversaries may repetitively or successively change I/O point values to perform an action. Brute Force I/O may be achieved by changing either a range of I/O point values or a single point value repeatedly to manipulate a process function. The adversary's goal and the information they have about the target environment will influence which of the options they choose."
  T0822 = "Adversaries may leverage external remote services as a point of initial access into your network. These services allow users to connect to internal network resources from external locations. Examples are VPNs, Citrix, and other access mechanisms."
  T0883 = "Adversaries may gain access into industrial environments through systems exposed directly to the internet for remote access rather than through External Remote Services. Internet Accessible Devices are exposed to the internet unintentionally or intentionally without adequate protections. This may allow for adversaries to move directly into the control system network."
  T0817 = "Adversaries may gain access to a system during a drive-by compromise, when a user visits a website as part of a regular browsing session.With this technique, the user's web browser is targeted and exploited simply by visiting the compromised website."
  T0847 = "Adversaries may move onto systems, such as those separated from the enterprise network, by copying malware to removable media which is inserted into the control systems environment. The adversary may rely on unknowing trusted third parties, such as suppliers or contractors with access privileges, to introduce the removable media. This technique enables initial access to target devices that never connect to untrusted networks, but are physically accessible."
  T0865 = "Adversaries may use a spearphishing attachment, a variant of spearphishing, as a form of a social engineering attack against specific targets. Spearphishing attachments are different from other forms of spearphishing in that they employ malware attached to an email. All forms of spearphishing are electronically delivered and target a specific individual, company, or industry."
  T0848 = "Adversaries may setup a rogue master to leverage control server functions to communicate with outstations. A rogue master can be used to send legitimate control messages to other control system devices, affecting processes in unintended ways. It may also be used to disrupt network communications by capturing and receiving the network traffic meant for the actual master."
  T0819 = "Adversaries may leverage weaknesses to exploit internet-facing software for initial access into an industrial network. Internet-facing software may be user applications, underlying networking implementations, an assets operating system, weak defenses, etc. Targets of this technique may be intentionally exposed for the purpose of remote management and visibility."
  T0859 = "Adversaries may steal the credentials of a specific user or service account using credential access techniques. In some cases, default credentials for control system devices may be publicly available. Compromised credentials may be used to bypass access controls placed on various resources on hosts and within the network, and may even be used for persistent access to remote systems."
  T0862 = "Adversaries may perform supply chain compromise to gain control systems environment access by means of infected products, software, and workflows. Supply chain compromise is the manipulation of products, such as devices or software, or their delivery mechanisms before receipt by the end consumer. Adversary compromise of these products and mechanisms is done for the goal of data or system compromise, once infected products are introduced to the target environment."
  T0860 = "Adversaries may perform wireless compromise as a method of gaining communications and unauthorized access to a wireless network. Access to a wireless network may be gained through the compromise of a wireless device.12 Adversaries may also utilize radios and other wireless communication devices on the same frequency as the wireless network."
  T0866 = "Adversaries may exploit a software vulnerability to take advantage of a programming error in a program, service, or within the operating system software or kernel itself to enable remote service abuse. A common goal for post-compromise exploitation of remote services is for initial access into and lateral movement throughout the ICS environment to enable access to targeted systems.1."
  T0864 = "Adversaries may target devices that are transient across ICS networks and external networks. Normally, transient assets are brought into an environment by authorized personnel and do not remain in that environment on a permanent basis.1 Transient assets are commonly needed to support management functions and may be more common in systems where a remotely managed asset is not feasible, external connections for remote access do not exist, or 3rd party contractor/vendor access is required."
  T0886 = "Adversaries may leverage remote services to move between assets and network segments. These services are often used to allow operators to interact with systems remotely within the network, some examples are RDP, SMB, SSH, and other similar mechanisms.123."
  T0889 = "Adversaries may modify or add a program on a controller to affect how it interacts with the physical process, peripheral devices and other hosts on the network. Modification to controller programs can be accomplished using a Program Download in addition to other types of program modification such as online edit and program append."
  T0812 = "Adversaries may leverage manufacturer or supplier set default credentials on control system devices. These default credentials may have administrative permissions and may be necessary for initial configuration of the device. It is general best practice to change the passwords for these accounts as soon as possible, but some manufacturers may have devices that have passwords or usernames that cannot be changed."
  T0867 = "Adversaries may transfer tools or other files from one system to another to stage adversary tools or other files over the course of an operation.1 Copying of files may also be performed laterally between internal victim systems to support Lateral Movement with remote Execution using inherent file sharing protocols such as file sharing over SMB to connected network shares.1."
  T0873 = "Adversaries may attempt to infect project files with malicious code. These project files may consist of objects, program organization units, variables such as tags, documentation, and other configurations needed for PLC programs to function.1 Using built in functions of the engineering software, adversaries may be able to download an infected program to a PLC in the operating environment enabling further execution and persistence techniques."
  T0890 = "Adversaries may exploit software vulnerabilities in an attempt to elevate privileges. Exploitation of a software vulnerability occurs when an adversary takes advantage of a programming error in a program, service, or within the operating system software or kernel itself to execute adversary-controlled code. Security constructs such as permission levels will often hinder access to information and use of certain techniques, so adversaries will likely need to perform privilege escalation to include use of software exploitation to circumvent those restrictions."
} 
Function Export-AzSentineMITREtoCSV ($workspaceName, $resourceGroupName, $filename, $includeDisabled, $ShowZeroSimulatedRuleTemplates, $ShowAllSimulatedRuleTemplates) {

  #Setup the Authentication header needed for the REST calls
  $context = Get-AzContext
  $Profile = [Microsoft.Azure.Commands.Common.Authentication.Abstractions.AzureRmProfileProvider]::Instance.Profile
  $profileClient = New-Object -TypeName Microsoft.Azure.Commands.ResourceManager.Common.RMProfileClient -ArgumentList ($Profile)
  $token = $profileClient.AcquireAccessToken($context.Subscription.TenantId)
  $authHeader = @{
    'Content-Type'  = 'application/json' 
    'Authorization' = 'Bearer ' + $token.AccessToken 
  }
    
  $subscriptionId = (Get-AzContext).Subscription.Id

  #Load the templates so that we can copy the information as needed
  $url = "https://management.azure.com/subscriptions/$($subscriptionId)/resourceGroups/$($resourceGroupName)/providers/Microsoft.OperationalInsights/workspaces/$($workspaceName)/providers/Microsoft.SecurityInsights/alertrules?api-version=2021-10-01-preview"
  $results = (Invoke-RestMethod -Method "Get" -Uri $url -Headers $authHeader ).value

  foreach ($tactic in $tacticHash.keys) {
    foreach ($technique in $tacticHash[$tactic]) {
      $count = 0
      #Do we want to include disabled rules?  If so, then no need to check if the rule is disabled or not.
      if ($includeDisabled) {
        $count = ($results.properties | Where-Object { ($_.techniques -eq $technique) -and ($_.tactics -eq $tactic) }).count
      }
      else {
        $count = ($results.properties | Where-Object { ($_.techniques -eq $technique) -and ($_.tactics -eq $tactic) -and ($_.enabled -eq $true) }).count
      }
     
      #[void]$outputObject.add([pscustomobject]@{"Tactic" = $tactic; "Technique" = $technique; "Name"=$techniqueNameHash[$technique]; "Count" = $count; "Description" = $techniqueDescriptionHash[$technique] })
      $newRow = $outputObject.NewRow()
      $newRow.Tactic = $tactic
      $newRow.Technique = $technique
      $newRow.Name = $techniqueNameHash[$technique]
      $newRow.Count = $count
      $newRow.Description = $techniqueDescriptionHash[$technique]

      [void]$outputObject.Rows.Add( $newRow )
    }
  }
  if ($ShowZeroSimulatedRuleTemplates) {
    Export-ZeroCoveredSimulatedRuleTemplates $authHeader $subscriptionId $resourceGroupName $workspaceName $filename $outputObject
  }
  elseif ($ShowAllSimulatedRuleTemplates) {
    Export-AllCoveredSimulatedRuleTemplates $authHeader $subscriptionId $resourceGroupName $workspaceName $filename $outputObject
  }
  else {
    $outputObject |  Export-Csv -QuoteFields "Description" -Path $filename
  }
}

Function Export-ZeroCoveredSimulatedRuleTemplates ($authHeader, $subscriptionId, $resourceGroupName, $workspaceName, $filename, $tacticCountObject ) {
  $url = "https://management.azure.com/subscriptions/$($subscriptionId)/resourceGroups/$($resourceGroupName)/providers/Microsoft.OperationalInsights/workspaces/$($workspaceName)/providers/Microsoft.SecurityInsights/alertruletemplates?api-version=2021-10-01-preview"
  $ruleTemplateResults = (Invoke-RestMethod -Method "Get" -Uri $url -Headers $authHeader ).value
  foreach ($tacticRow in ($tacticCountObject | Where-Object { $_.count -eq 0 })) {
    foreach ($ruleTemplate in ($ruleTemplateResults | Where-Object { ($_.properties.techniques -eq $tacticRow.technique) -and ($_.properties.tactics -eq $tacticRow.tactic) }) ) {
      $newRow = $simulatedOutput.NewRow()
      $newRow.Tactic = $tacticRow.tactic
      $newRow.Technique = $tacticRow.technique
      $newRow.Name = $tacticRow.Name
      $newRow.RuleName = $ruleTemplate.properties.displayName

      [void]$simulatedOutput.Rows.Add( $newRow )
    }
  }
  $simulatedOutput |  Export-Csv -QuoteFields "RuleName" -Path $filename
}


Function Export-AllCoveredSimulatedRuleTemplates ($authHeader, $subscriptionId, $resourceGroupName, $workspaceName, $filename, $tacticCountObject ) {
  $url = "https://management.azure.com/subscriptions/$($subscriptionId)/resourceGroups/$($resourceGroupName)/providers/Microsoft.OperationalInsights/workspaces/$($workspaceName)/providers/Microsoft.SecurityInsights/alertruletemplates?api-version=2021-10-01-preview"
  $ruleTemplateResults = (Invoke-RestMethod -Method "Get" -Uri $url -Headers $authHeader ).value
  foreach ($tacticRow in ($tacticCountObject )) {
    #We only want those rule templates that have not been used, hence the check against alertRulesCreatedByTemplateCount
    foreach ($ruleTemplate in ($ruleTemplateResults | Where-Object { ($_.properties.techniques -eq $tacticRow.technique) -and ($_.properties.tactics -eq $tacticRow.tactic) -and ($_.properties.alertRulesCreatedByTemplateCount -eq 0) }) ) {
      $newRow = $simulatedOutput.NewRow()
      $newRow.Tactic = $tacticRow.tactic
      $newRow.Technique = $tacticRow.technique
      $newRow.Name = $tacticRow.Name
      $newRow.RuleName = $ruleTemplate.properties.displayName

      [void]$simulatedOutput.Rows.Add( $newRow )
    }
  }
  $simulatedOutput |  Export-Csv -QuoteFields "RuleName" -Path $filename
}


#Execute the code
if (! $Filename.EndsWith(".csv")) {
  $FileName += ".csv"
}
Export-AzSentineMITREtoCSV $WorkSpaceName $ResourceGroupName $FileName $IncludeDisabled $ShowZeroSimulatedRuleTemplates $ShowAllSimulatedRuleTemplates
