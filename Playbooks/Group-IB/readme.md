# Ingest Group-IB TI Feeds and Indicators Collections
Author: Hesham Saad

Group-IB Azure Sentinel playbooks designed by Group-IB team and supported by Microsoft team to ingest TI feeds and indicators from multiple Group-IB data collections and writes them to Microsoft Security Graph API to be listed under Azure Sentinel ThreatIntelligenceIndicators table and custom log tables as well for adversaries, threat actors,...etc

There are a number of pre-configuration steps required before deploying the playbooks.

## Group-IB Sentinel Playbooks Collections Detailed Description

1. "GIBTIA_APT_Threats" Playbook
a. Collection: apt/threat
b. Has Indicators: Yes
c. Indicators Content: 
GIB APT Threat Indicator(IPv4)
GIB APT Threat Indicator(domain)
GIB APT Threat Indicator(url)
GIB APT Threat Indicator(md5)
GIB APT Threat Indicator(sha256)
GIB APT Threat Indicator(sha1)
d. Description:
Group-IB continuously monitors activities undertaken by hacker groups, investigate, collect, and analyze information about all emerging and ongoing attacks. Based on this information, we provide IOC's related to APT Groups Attacks.

2. "GIBTIA_APT_ThreatActor" Playbook
a. Collection: apt/threat_actor
b. Has Indicators: No
c. Indicators Content: N/A
d. Description:
This collection contains APT groups’ info, with detailed descriptions.

3. "GIBTIA_Attacks_ddos" Playbook
a. Collection: attacks/ddos
b. Has Indicators: Yes
c. Indicators Content:
GIB DDoS Attack(IPv4)
d. Description:
The "DDoS attacks" collection contains a DDoS Attacks targets and C2 indicators.

4. "GIBTIA_Attacks_deface" Playbook
a. Collection: attacks/deface
b. Has Indicators: Yes
c. Indicators Content:
GIB Attack Deface(url)
d. Description:
The “Deface” collection contains information about online resources that have become subject to defacement attacks (the visual content of a website being substituted or modified).

5. "GIBTIA_Attacks_phishing" Playbook
a. Collection: attacks/phishing
b. Has Indicators: Yes
c. Indicators Content:
GIB Phishing Domain(domain)
GIB Phishing IP(IPv4)
GIB Phishing URL(url)
d. Description:
The “Attacks Phishing" collection provides information about various phishing resources (including URLs, Domains and IPs.).

6. "GIBTIA_Attacks_phishing_kit" Playbook
a. Collection: attacks/phishing_kit
b. Has Indicators: Yes
c. Indicators Content:
GIB Phishing Kit Email(email)
d. Description:
The “Atacks Phishing Kits” collection contains information about the archives of phishing kits. Emails gotten from kits can be obtained as indicators.

7. "GIBTIA_BP_phishing" Playbook
a. Collection: bp/phishing
b. Has Indicators: Yes
c. Indicators Content:
GIB Phishing Domain(domain)
GIB Phishing IP(IPv4)
GIB Phishing URL(url)
d. Description:
The "BP Phishing" collection provides events related to clients company.

8. "GIBTIA_BP_phishing_kit" Playbook
a. Collection: bp/phishing_kit
b. Has Indicators: Yes
c. Indicators Content:
GIB Phishing Kit Email(email)
d. Description:
The "BP Phishing Kit" collection provides phishing kits related to clients company.

9. "GIBTIA_Compromised_account" Playbook
a. Collection: compromised/account
b. Has Indicators: Yes
c. Indicators Content:
GIB Compromised Account CNC(url)
GIB Compromised Account CNC(domain)
GIB Compromised Account CNC(IPv4)
d. Description:
This collection contains credentials collected from various phishing resources, botnets, command-and-control (C&C) servers used by hackers.

10. "GIBTIA_Compromised_card" Playbook
a. Collection: compromised/card
b. Has Indicators: Yes
c. Indicators Content:
GIB Compromised Card CNC URL(url)
GIB Compromised Card CNC Domain(domain)
GIB Compromised Card CNC IP(IPv4)
d. Description:
This collection contains information about compromised bank cards. This includes data collected from card shops, specialized forums, and public sources.

11. "GIBTIA_Compromised_imei" Playbook
a. Collection: compromised/imei
b. Has Indicators: Yes
c. Indicators Content:
GIB Compromised IMEI CNC Domain(domain)
GIB Compromised IMEI CNC URL(url)
GIB Compromised IMEI CNC IP(IPv4)
d. Description:
The section contains data on infected mobile devices, which is obtained by analyzing mobile botnets. It does not contain personal data and is available to all system users.

12. "GIBTIA_Compromised_mule" Playbook
a. Collection: compromised/mule
b. Has Indicators: Yes
c. Indicators Content:
GIB Compromised Mule CNC Domain(domain)
GIB Compromised Mule CNC URL(url)
GIB Compromised Mule CNC IP(IPv4)
d. Description:
This section contains information about bank accounts to which threat actors have transferred or plan to transfer stolen money. Man-in-the-Browser (MITB) attacks, mobile Trojans, and phishing kits allow fraudsters to make money transfers automatically. Playbook provides C2 data related to compromitation.

13. "GIBTIA_HI_Threats" Playbook
a. Collection: hi/threat
b. Has Indicators: Yes
c. Indicators Content:
GIB HI Threat Indicator(domain)
d. Description:
Group-IB continuously monitors activities undertaken by hacker groups, investigate, collect, and analyze information about all emerging and ongoing attacks. Based on this information, we provide IOC's related to Hackers Attacks.

14. "GIBTIA_HI_ThreatActor" Playbook
a. Collection: hi/threat_actor
b. Has Indicators: No
c. Indicators Content: N/A
d. Description:
This collection contains non-APT groups’  and Individual hackers info, with detailed descriptions.

15. "GIBTIA_Malware_cnc" Playbook
a. Collection: malware/cnc
b. Has Indicators: Yes
c. Indicators Content:
GIB Malware CNC Domain(domain)
GIB Malware CNC URL(url)
GIB Malware CNC IP(IPv4)
d. Description:
The "Malware" collection contains Malwares C2 detected by group IB. 

16. "GIBTIA_Malware_Targeted_Malware" Playbook
a. Collection: malware/targeted_malware
b. Has Indicators: Yes
c. Indicators Content:
GIB Malware Targeted Malware(md5)
GIB Malware Targeted Malware(sha1)
GIB Malware Targeted Malware(sha256)
GIB Malware Targeted Malware Inject(md5)
d. Description:
The “Targeted Trojans” section contains information about malicious programs targeting the client's infrastructure. Information is collected by examining a multitude of malicious files and investigating various incidents.

17. "GIBTIA_OSI_GitLeak" Playbook
a. Collection: osi/git_leak
b. Has Indicators: No
c. Indicators Content: N/A
d. Description:
Open-source repositories such as GitHub contain codes that anyone can search for. They are often used by threat actors planning to attack a specific company. The “Git Leaks” section contains the above data in code repositories.

18. "GIBTIA_OSI_PublicLeak" Playbook
a. Collection: osi/public_leak
b. Has Indicators: No
c. Indicators Content: N/A
d. Description:
The “Public leaks” collection contains the leaked clinets data collected on popular file-sharing resources or text/information exchange websites.

19. "GIBTIA_OSI_Vulnerability" Playbook
a. Collection: osi/vulnerability
b. Has Indicators: No
c. Indicators Content: N/A
d. Description:
The “Vulnerabilities” collection displays information about vulnerabilities detected in the software by version.

20. "GIBTIA_Suspicious_ip_open_proxy" Playbook
a. Collection: suspicious_ip/open_proxy
b. Has Indicators: Yes
c. Indicators Content:
GIB Open Proxy Address(IPv4)
d. Description:
The “Open proxy” collection proviedes information about lists of proxy servers that are publicly available on various online resources related to anonymity. In addition, proxy servers may be configured as open proxies intentionally or as a result of misconfiguration or breaches.

21. "GIBTIA_Suspicious_ip_socks_proxy" Playbook
a. Collection: suspicious_ip/socks_proxy
b. Has Indicators: Yes
c. Indicators Content:
GIB Socks Proxy Address(IPv4)
d. Description:
The “Socks proxy” collection providess information about addresses where malware that turns infected computers into SOCKS proxies has been installed. Such computers (bots) are rented out and used in various attacks to ensure the attacker as much anonymity as possible.

22. "GIBTIA_Suspicious_ip_tor_node" Playbook
a. Collection: suspicious_ip/tor_node
b. Has Indicators: Yes
c. Indicators Content:
GIB Tor Node Address(IPv4)
d. Description:
The “Tor Node” collection displays information about Tor exit nodes, which are the final Tor relays in the circuit. The nodes act as a medium between a Tor client and public Internet.


## Deployment Steps
1. Deploy GIBIndicatorsProcessor playbook first
2. Deploy Required collections Playbooks and configure the following parameters:
a. GIB Username - is a login to access GIB TI&A Web Interface
b. Save only indicators - set to true if only indicators enrichment is required, otherwise, an additional table in Workspace with full event content will be created
Note: Some collections provide no indicators, so do not have this parameter configurable and add GIB TI&A events only in Log Workspace
c. GIB <Indicator Description> Action - This is an action required to set in a particular indicator type provided through the current collection.(The action to apply if the indicator is matched from within the targetProduct security tool. Possible values are: unknown, allow, block, alert)
d. GIB API URL - is an GIB TI&A API URL
e. Configure API Key variable. API Key can be generated in the Profile Section in Group-IB TI&A Web Interface

## Register an Azure AD App for TI Indicators Graph API Write Access
1. Go to Azure Active Directory / App Registrations
2. Create +New Registration
3. Give it a name.  Click Register.
4. Click API Permissions Blade.
5. Click Add a Permission.  
6. Click Microsoft Graph.
7. Click Appplication Permissions
8. Check permissions for ThreatIndicators (ThreatIndicators.ReadWrite.OwnedBy).  Click Add permissions.
9. Click grant admin consent for domain.com
10. Click Certificates and Secrets
11. Click New Client Secret
12. Enter a description, select never.  Click Add.
13. IMPORTANT.  Click copy next to the new secret and paste it somewhere temporaily.  You can not come back to get the secret once you leave the blade.
14. Copy the client Id from the application properties and paste it somewhere.
15. Also copy the tenant Id from the AAD directory properties blade.

## Deploy the Logic App template

1. GIBIndicatorsProcessor Playbook:
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBIndicatorsProcessor%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBIndicatorsProcessor%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

2. Required collections Playbooks:

GIBTIA_Suspicious_ip_tor_node Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Suspicious_ip_tor_node%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Suspicious_ip_tor_node%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_Suspicious_ip_socks_proxy Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Suspicious_ip_socks_proxy%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Suspicious_ip_socks_proxy%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_Suspicious_ip_open_proxy Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Suspicious_ip_open_proxy%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Suspicious_ip_open_proxy%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_OSI_Vulnerability Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_OSI_Vulnerability%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_OSI_Vulnerability%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_OSI_PublicLeak Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_OSI_PublicLeak%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_OSI_PublicLeak%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_OSI_GitLeak Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_OSI_GitLeak%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_OSI_GitLeak%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_Malware_Targeted_Malware Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Malware_Targeted_Malware%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Malware_Targeted_Malware%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_Malware_cnc Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Malware_cnc%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Malware_cnc%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_HI_Threat_Actor Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_HI_Threat_Actor%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_HI_Threat_Actor%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_HI_Threat Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_HI_Threat%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_HI_Threat%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_Compromised_mule Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Compromised_mule%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Compromised_mule%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_Compromised_imei Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Compromised_imei%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Compromised_imei%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_Compromised_card Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Compromised_card%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Compromised_card%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_Compromised_account Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Compromised_account%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Compromised_account%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_BP_phishing_kit Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_BP_phishing_kit%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_BP_phishing_kit%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_BP_phishing Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_BP_phishing%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_BP_phishing%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_Attacks_phishing_kit Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Attacks_phishing_kit%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Attacks_phishing_kit%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_Attacks_phishing Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Attacks_phishing%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Attacks_phishing%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_Attacks_deface Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Attacks_deface%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Attacks_deface%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_Attacks_ddos Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Attacks_ddos%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_Attacks_ddos%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_APT_Threats Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_APT_Threats%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_APT_Threats%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>

GIBTIA_APT_ThreatActor Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_APT_ThreatActor%2Fazuredeploy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGIBTIA_APT_ThreatActor%2Fazuredeploy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>