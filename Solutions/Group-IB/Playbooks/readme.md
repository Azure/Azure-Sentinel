# Ingest Group-IB Threat Intelligence & Attribution Feeds and Indicators Collections
Author: Hesham Saad

Group-IB Azure Sentinel playbooks designed by Group-IB team and supported by Microsoft team to ingest Threat Intelligence & Attribution feeds and indicators from multiple Group-IB data collections and writes them to Microsoft Security Graph API to be listed under Azure Sentinel ThreatIntelligenceIndicators table and custom log tables as well for adversaries, threat actors,...etc

There are a number of pre-configuration steps required before deploying the playbooks.

## Group-IB Sentinel Playbooks Collections Detailed Description

1. "GIBTIA_APT_Threats" Playbook<br>
a. Collection: apt/threat<br>
b. Has Indicators: Yes<br>
c. Indicators Content: <br>
GIB APT Threat Indicator(IPv4)<br>
GIB APT Threat Indicator(domain)<br>
GIB APT Threat Indicator(url)<br>
GIB APT Threat Indicator(md5)<br>
GIB APT Threat Indicator(sha256)<br>
GIB APT Threat Indicator(sha1)<br>
d. Description:<br>
Group-IB continuously monitors activities undertaken by hacker groups, investigate, collect, and analyze information about all emerging and ongoing attacks. Based on this information, we provide IOC's related to APT Groups Attacks.

2. "GIBTIA_APT_ThreatActor" Playbook<br>
a. Collection: apt/threat_actor<br>
b. Has Indicators: No<br>
c. Indicators Content: N/A<br>
d. Description:<br>
This collection contains APT groups’ info, with detailed descriptions.

3. "GIBTIA_Attacks_ddos" Playbook<br>
a. Collection: attacks/ddos<br>
b. Has Indicators: Yes<br>
c. Indicators Content:<br>
GIB DDoS Attack(IPv4)<br>
d. Description:<br>
The "DDoS attacks" collection contains a DDoS Attacks targets and C2 indicators.

4. "GIBTIA_Attacks_deface" Playbook<br>
a. Collection: attacks/deface<br>
b. Has Indicators: Yes<br>
c. Indicators Content:<br>
GIB Attack Deface(url)<br>
d. Description:<br>
The “Deface” collection contains information about online resources that have become subject to defacement attacks (the visual content of a website being substituted or modified).

5. "GIBTIA_Attacks_phishing" Playbook<br>
a. Collection: attacks/phishing<br>
b. Has Indicators: Yes<br>
c. Indicators Content:<br>
GIB Phishing Domain(domain)<br>
GIB Phishing IP(IPv4)<br>
GIB Phishing URL(url)<br>
d. Description:<br>
The “Attacks Phishing" collection provides information about various phishing resources (including URLs, Domains and IPs.).

6. "GIBTIA_Attacks_phishing_kit" Playbook<br>
a. Collection: attacks/phishing_kit<br>
b. Has Indicators: Yes<br>
c. Indicators Content:<br>
GIB Phishing Kit Email(email)<br>
d. Description:<br>
The “Atacks Phishing Kits” collection contains information about the archives of phishing kits. Emails gotten from kits can be obtained as indicators.

7. "GIBTIA_BP_phishing" Playbook<br>
a. Collection: bp/phishing<br>
b. Has Indicators: Yes<br>
c. Indicators Content:<br>
GIB Phishing Domain(domain)<br>
GIB Phishing IP(IPv4)<br>
GIB Phishing URL(url)<br>
d. Description:<br>
The "BP Phishing" collection provides events related to clients company.

8. "GIBTIA_BP_phishing_kit" Playbook<br>
a. Collection: bp/phishing_kit<br>
b. Has Indicators: Yes<br>
c. Indicators Content:<br>
GIB Phishing Kit Email(email)<br>
d. Description:<br>
The "BP Phishing Kit" collection provides phishing kits related to clients company.

9. "GIBTIA_Compromised_account" Playbook<br>
a. Collection: compromised/account<br>
b. Has Indicators: Yes<br>
c. Indicators Content:<br>
GIB Compromised Account CNC(url)<br>
GIB Compromised Account CNC(domain)<br>
GIB Compromised Account CNC(IPv4)<br>
d. Description:<br>
This collection contains credentials collected from various phishing resources, botnets, command-and-control (C&C) servers used by hackers.

10. "GIBTIA_Compromised_card" Playbook<br>
a. Collection: compromised/card<br>
b. Has Indicators: Yes<br>
c. Indicators Content:<br>
GIB Compromised Card CNC URL(url)<br>
GIB Compromised Card CNC Domain(domain)<br>
GIB Compromised Card CNC IP(IPv4)<br>
d. Description:<br>
This collection contains information about compromised bank cards. This includes data collected from card shops, specialized forums, and public sources.

11. "GIBTIA_Compromised_imei" Playbook<br>
a. Collection: compromised/imei<br>
b. Has Indicators: Yes<br>
c. Indicators Content:<br>
GIB Compromised IMEI CNC Domain(domain)<br>
GIB Compromised IMEI CNC URL(url)<br>
GIB Compromised IMEI CNC IP(IPv4)<br>
d. Description:<br>
The section contains data on infected mobile devices, which is obtained by analyzing mobile botnets. It does not contain personal data and is available to all system users.

12. "GIBTIA_Compromised_mule" Playbook<br>
a. Collection: compromised/mule<br>
b. Has Indicators: Yes<br>
c. Indicators Content:<br>
GIB Compromised Mule CNC Domain(domain)<br>
GIB Compromised Mule CNC URL(url)<br>
GIB Compromised Mule CNC IP(IPv4)<br>
d. Description:<br>
This section contains information about bank accounts to which threat actors have transferred or plan to transfer stolen money. Man-in-the-Browser (MITB) attacks, mobile Trojans, and phishing kits allow fraudsters to make money transfers automatically. Playbook provides C2 data related to compromitation.

13. "GIBTIA_HI_Threats" Playbook <br>
a. Collection: hi/threat <br>
b. Has Indicators: Yes <br>
c. Indicators Content: <br>
GIB HI Threat Indicator(domain) <br>
d. Description: <br>
Group-IB continuously monitors activities undertaken by hacker groups, investigate, collect, and analyze information about all emerging and ongoing attacks. Based on this information, we provide IOC's related to Hackers Attacks.

14. "GIBTIA_HI_ThreatActor" Playbook <br>
a. Collection: hi/threat_actor <br>
b. Has Indicators: No <br>
c. Indicators Content: N/A <br>
d. Description: <br>
This collection contains non-APT groups’  and Individual hackers info, with detailed descriptions.

15. "GIBTIA_Malware_cnc" Playbook <br>
a. Collection: malware/cnc <br>
b. Has Indicators: Yes <br>
c. Indicators Content: <br>
GIB Malware CNC Domain(domain) <br>
GIB Malware CNC URL(url) <br>
GIB Malware CNC IP(IPv4) <br>
d. Description: <br>
The "Malware" collection contains Malwares C2 detected by group IB. 

16. "GIBTIA_Malware_Targeted_Malware" Playbook <br>
a. Collection: malware/targeted_malware <br>
b. Has Indicators: Yes <br>
c. Indicators Content: <br>
GIB Malware Targeted Malware(md5) <br>
GIB Malware Targeted Malware(sha1) <br>
GIB Malware Targeted Malware(sha256) <br>
GIB Malware Targeted Malware Inject(md5) <br>
d. Description: <br>
The “Targeted Trojans” section contains information about malicious programs targeting the client's infrastructure. Information is collected by examining a multitude of malicious files and investigating various incidents.

17. "GIBTIA_OSI_GitLeak" Playbook <br>
a. Collection: osi/git_leak <br>
b. Has Indicators: No <br>
c. Indicators Content: N/A <br>
d. Description: <br>
Open-source repositories such as GitHub contain codes that anyone can search for. They are often used by threat actors planning to attack a specific company. The “Git Leaks” section contains the above data in code repositories.

18. "GIBTIA_OSI_PublicLeak" Playbook <br>
a. Collection: osi/public_leak <br>
b. Has Indicators: No <br>
c. Indicators Content: N/A <br>
d. Description: <br>
The “Public leaks” collection contains the leaked clinets data collected on popular file-sharing resources or text/information exchange websites.

19. "GIBTIA_OSI_Vulnerability" Playbook <br>
a. Collection: osi/vulnerability <br>
b. Has Indicators: No <br>
c. Indicators Content: N/A <br>
d. Description: <br>
The “Vulnerabilities” collection displays information about vulnerabilities detected in the software by version.

20. "GIBTIA_Suspicious_ip_open_proxy" Playbook <br>
a. Collection: suspicious_ip/open_proxy <br>
b. Has Indicators: Yes <br>
c. Indicators Content: <br>
GIB Open Proxy Address(IPv4) <br>
d. Description: <br>
The “Open proxy” collection proviedes information about lists of proxy servers that are publicly available on various online resources related to anonymity. In addition, proxy servers may be configured as open proxies intentionally or as a result of misconfiguration or breaches.

21. "GIBTIA_Suspicious_ip_socks_proxy" Playbook <br>
a. Collection: suspicious_ip/socks_proxy <br>
b. Has Indicators: Yes <br>
c. Indicators Content: <br>
GIB Socks Proxy Address(IPv4) <br>
d. Description: <br>
The “Socks proxy” collection providess information about addresses where malware that turns infected computers into SOCKS proxies has been installed. Such computers (bots) are rented out and used in various attacks to ensure the attacker as much anonymity as possible.

22. "GIBTIA_Suspicious_ip_tor_node" Playbook <br>
a. Collection: suspicious_ip/tor_node <br>
b. Has Indicators: Yes <br>
c. Indicators Content: <br>
GIB Tor Node Address(IPv4) <br>
d. Description: <br>
The “Tor Node” collection displays information about Tor exit nodes, which are the final Tor relays in the circuit. The nodes act as a medium between a Tor client and public Internet.


## Deployment Steps
1. Deploy GIBIndicatorsProcessor playbook first
2. Deploy Required collections Playbooks and configure the following parameters: <br>
a. GIB Username - is a login to access GIB TI&A Web Interface <br>
b. Save only indicators - set to true if only indicators enrichment is required, otherwise, an additional table in Workspace with full event content will be created <br>
Note: Some collections provide no indicators, so do not have this parameter configurable and add GIB TI&A events only in Log Workspace
c. GIB <Indicator Description> Action - This is an action required to set in a particular indicator type provided through the current collection.(The action to apply if the indicator is matched from within the targetProduct security tool. Possible values are: unknown, allow, block, alert) <br>
d. GIB API URL - is an GIB TI&A API URL <br>
e. Configure API Key variable. API Key can be generated in the Profile Section in Group-IB TI&A Web Interface, it's highly recommended to use Azure Key Vault Playbook Get Secret control

Note:
<br>
- In case if you faced an issue while deploying one of the Playbooks via the ARM template's option, please refer to the Playbook json file and do a manual copy & paste activity to a blank Playbook (Logic App).
- Please ensure keeping the default value of PlaybookName as is since there is a dependencies at other playbooks for the messages batching process on the names, ensure that GIBIndicatorsProcessor playbook be installed first then deploy any other needed playbook (Collection) and ensure that all PLaybooks have the same resource group region.
<br>
- Based on the Playbooks (Logic App) selected region (East US, UAE North, West Europe,...etc) please ensure validating the Logic APP region outbound IPs list are been whitelisted with Group-IB, for more details: https://docs.microsoft.com/en-us/azure/logic-apps/logic-apps-limits-and-config#outbound-ip-addresses

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
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBIndicatorsProcessor.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBIndicatorsProcessor.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

2. GIBTIA_Suspicious_ip_tor_node Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Suspicious_ip_tor_node.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Suspicious_ip_tor_node.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  
  
3. GIBTIA_Suspicious_ip_socks_proxy Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Suspicious_ip_socks_proxy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Suspicious_ip_socks_proxy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

4. GIBTIA_Suspicious_ip_open_proxy Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Suspicious_ip_open_proxy.json" target="_blank">
    <img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Suspicious_ip_open_proxy.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

5. GIBTIA_OSI_Vulnerability Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_OSI_Vulnerability.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_OSI_Vulnerability.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

6. GIBTIA_OSI_PublicLeak Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_OSI_PublicLeak.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_OSI_PublicLeak.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

7. GIBTIA_OSI_GitLeak Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_OSI_GitLeak.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_OSI_GitLeak.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

8. GIBTIA_Malware_Targeted_Malware Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Malware_Targeted_Malware.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Malware_Targeted_Malware.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

9. GIBTIA_Malware_cnc Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Malware_cnc.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Malware_cnc.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

10. GIBTIA_HI_Threat_Actor Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_HI_Threat_Actor.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_HI_Threat_Actor.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  
 
11. GIBTIA_HI_Threat Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_HI_Threat.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_HI_Threat.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

12. GIBTIA_Compromised_mule Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Compromised_mule.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Compromised_mule.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

13. GIBTIA_Compromised_imei Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Compromised_imei.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Compromised_imei.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

14. GIBTIA_Compromised_card Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Compromised_card.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Compromised_card.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

15. GIBTIA_Compromised_account Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Compromised_account.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Compromised_account.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

16. GIBTIA_BP_phishing_kit Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_BP_phishing_kit.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_BP_phishing_kit.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

17. GIBTIA_BP_phishing Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_BP_phishing.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_BP_phishing.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

18. GIBTIA_Attacks_phishing_kit Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Attacks_phishing_kit.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Attacks_phishing_kit" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  
                                                                                                                                     
19. GIBTIA_Attacks_phishing Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Attacks_phishing.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Attacks_phishing.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

20. GIBTIA_Attacks_deface Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Attacks_deface.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2Fazuredeploy-GIBTIA_Attacks_deface.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

21. GIBTIA_Attacks_ddos Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2FPlaybooks%2Fazuredeploy-GIBTIA_Attacks_ddos.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2FPlaybooks%2Fazuredeploy-GIBTIA_Attacks_ddos.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

22. GIBTIA_APT_Threats Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2FPlaybooks%2Fazuredeploy-GIBTIA_APT_Threats.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2FPlaybooks%2Fazuredeploy-GIBTIA_APT_Threats.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  

23. GIBTIA_APT_ThreatActor Playbook
<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2FPlaybooks%2Fazuredeploy-GIBTIA_APT_ThreatActor.json" target="_blank">
<img src="https://aka.ms/deploytoazurebutton""/>
</a>
<a href="https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmaster%2FSolutions%2FGroup-IB%2FPlaybooks%2FPlaybooks%2Fazuredeploy-GIBTIA_APT_ThreatActor.json" target="_blank">
<img src="https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png"/>
</a>  
