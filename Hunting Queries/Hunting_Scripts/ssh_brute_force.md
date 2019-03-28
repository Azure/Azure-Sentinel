# SSH Brute Force 
## Technique ID
T1110


## Description
Adversaries may use brute force techniques to attempt access to accounts when passwords are unknown or when password hashes are obtained.

Credential Dumping to obtain password hashes may only get an adversary so far when Pass the Hash is not an option. Techniques to systematically guess the passwords used to compute hashes are available, or the adversary may use a pre-computed rainbow table. Cracking hashes is usually done on adversary-controlled systems outside of the target network. 

Adversaries may attempt to brute force logins without knowledge of passwords or hashes during an operation either with zero knowledge or by attempting a list of known or possible passwords. This is a riskier option because it could cause numerous authentication failures and account lockouts, depending on the organization's login failure policies. 

A related technique called password spraying uses one password, or a small list of passwords, that matches the complexity policy of the domain and may be a commonly used password. Logins are attempted with that password and many different accounts on a network to avoid account lockouts that would normally occur when brute forcing a single account with many passwords.


## Hypothesis
Adversaries are able to gain access and are moving laterally within my network through SSH connections. 


## Examples

|Script  |Short Description | 
|:-------|:-----------------|
| [SSH](https://attack.mitre.org/software/S0220/)| Chaos is Linux malware that compromises systems by brute force attacks against SSH services. Once installed, it provides a reverse shell to its controllers, triggered by unsolicited packets |


## Recommended Data Sources

| Data Source | Event Log |
|---------|---------|
|Network Security Group Logs (NSG)| AzureNetworkAnalytics_CL|
|Ubutu|Syslog| 


## Sample Hunting Script
```
// Start with the ML-Based SSH Alert detections
SecurityAlert
| where TimeGenerated >= ago(14d)
| where DisplayName == "Anomalous SSH login detected"

// *** Search for host across logs *** //
// Lets search over all of our data using that host name
// Replace HOST_NAME with the name of the host from the first above query
search "HOST_NAME"
| where TimeGenerated >= ago(14d)
| summarize count() by $table
| order by count_ desc

// *** Search for host across logs *** //
// Lets search over all of our data using that host name
// Replace HOST_NAME with the name of the host from the first above query
search in (AzureNetworkAnalytics_CL) "HOST_NAME"
| where TimeGenerated >= ago(1d)
| extend Host = replace(@'"]',@'',substring(toupper(tostring(split(VirtualMachine_s, "/",1))),2))
| where SubType_s == "Topology"
| where strlen(Host) > 0 and isnotnull(Host)
| project MACAddress_s, PrivateIPAddress=PrivateIPAddresses_s, PublicIPAddress=PublicIPAddresses_s, Host
| summarize by MACAddress_s, PrivateIPAddress, PublicIPAddress, Host

// ************************************************** 
// INVESTIGATE THE HOST                                         
// Replace "IPs" with the IPs generated from the queries above                            
// name private and public ips from the first query                        
// ************************************************* 

// Lets return to the 2 ip address in the original alert
// One is a public Internet facing IP address and the other is private IP address
// Since there also could be some traffic going through a public facing lP, and 
// it doesn't cost us much, lets use both ip addresses
search ("IPs" or "IPs")
| where TimeGenerated >= ago(14d)
| summarize count() by $table
| order by count_ desc

// *** Visualize network traffic *** //
// We are not confined to looking at raw tabular data
// here is a quick example of the flows by the hour:
search in (AzureNetworkAnalytics_CL)  ("IPs" or "IPs")
| where TimeGenerated >= ago(14d)
| order by TimeGenerated desc


// *** Visualize network traffic *** //
// We are not confined to looking at raw tabular data
// here is a quick example of the flows by the hour:
search in (AzureNetworkAnalytics_CL)  ("IPs" or "IPs")
| where TimeGenerated >= ago(14d)
| order by TimeGenerated desc
| summarize sum(FlowCount_d) by bin(TimeGenerated, 1h)
| render timechart 

// *** Filter network traffic on inbound traffic only *** //
// While inbound and outbound are both relevant, lets start with the inbound data
// This query will filter on only accepted traffic as well as inbound only traffic
search in (AzureNetworkAnalytics_CL)  ("IPs" or "IPs")
| where TimeGenerated >= ago(14d)
| order by TimeGenerated desc
| where FlowDirection_s == "I" 
| where FlowStatus_s <> "D" 
| where strlen(tostring(SrcIP_s)) > 0
| project SrcIP_s 
| summarize count() by SrcIP_s
| order by count_ desc

// *** Search for over administrative events *** //
// Returns any administrative activity related to these IP addresses
search in (AzureActivity)  ("IPs" or "IPs")
| where TimeGenerated >= ago(14d)
| order by TimeGenerated desc 

// *** Search for over threat intel events *** //
// Lets dig into that data a little more
// This query will display the raw network events
search in (ThreatIntelligenceIndicator )  ("IPs" or "IPs")
| where TimeGenerated >= ago(14d)
| order by TimeGenerated desc

// ************************************************** 
//     INVESTIGATE THE SOURCE OF THE TRAFFIC                                       
// Replace "IPs" with the IPs generated from the queries above                          
// name private and public ips from the first query                        
// ************************************************* 

// *** Find any instances of network traffic between this and anything else  *** //
// Lets search for that ip address that is suspicious
search ("IPs" or "IPs")
| where TimeGenerated >= ago(14d)
| summarize count() by Type
| order by count_ desc

// *** Find any instances of network traffic between this and other machines  *** //
search in (AzureNetworkAnalytics_CL)("IPs" or "IPs")
| where TimeGenerated >= ago(14d)
| order by TimeGenerated desc
| where FlowDirection_s == "I" 
| where FlowStatus_s <> "D"

// *** Find any instances of network traffic between this machine and Office *** //
search in (OfficeActivity) ("IPs" or "IPs")
| where TimeGenerated >= ago(14d)
| where RecordType == "SharePointFileOperation"
| order by TimeGenerated desc
```

