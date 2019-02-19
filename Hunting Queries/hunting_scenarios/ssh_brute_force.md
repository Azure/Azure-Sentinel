# SSH Brute Force 
## Technique ID
T1110


## Description
Adversaries may use brute force techniques to attempt access to accounts when passwords are unknown or when password hashes are obtained.

Credential Dumping to obtain password hashes may only get an adversary so far when Pass the Hash is not an option. Techniques to systematically guess the passwords used to compute hashes are available, or the adversary may use a pre-computed rainbow table. Cracking hashes is usually done on adversary-controlled systems outside of the target network. 

Adversaries may attempt to brute force logins without knowledge of passwords or hashes during an operation either with zero knowledge or by attempting a list of known or possible passwords. This is a riskier option because it could cause numerous authentication failures and account lockouts, depending on the organization's login failure policies. 

A related technique called password spraying uses one password, or a small list of passwords, that matches the complexity policy of the domain and may be a commonly used password. Logins are attempted with that password and many different accounts on a network to avoid account lockouts that would normally occur when brute forcing a single account with many passwords.


## Hypothesis
Adversaries are moving laterally within my network through SSH connections. 


## Attack Simulation

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
// Start with the SSH Alert
// This is the query for the alert, so this is auto-generated
// Bookmark first row
SecurityAlert
| where TimeGenerated >= ago(3d)
| where AlertName contains "SSH Anomalous"
| extend IPAddress = tostring(parse_json(tostring(parse_json(Entities).[0])).["Address"])
| extend Host = toupper(tostring(parse_json(tostring(parse_json(Entities).[1])).["HostName"]))
| extend Account = tostring(parse_json(tostring(parse_json(Entities).[2])).["Name"])
| project TimeGenerated, AlertName, IPAddress, Host, Account
| join
(
    AzureNetworkAnalytics_CL
    | where TimeGenerated >= ago(3d)
    | extend Host = replace(@'"]',@'',substring(toupper(tostring(split(VirtualMachine_s, "/",1))),2))
    | where SubType_s == "Topology"
    | where strlen(Host) > 0 and isnotnull(Host)
    | project MACAddress_s, PrivateIPAddress=PrivateIPAddresses_s, PublicIPAddress=PublicIPAddresses_s, Host
)
on $left.Host == $right.Host
| extend SourceIP = IPAddress
| extend AccountCustomEntity = Account
| extend HostCustomEntity = Host
| extend IPCustomEntity = IPAddress
| extend Timestamp = TimeGenerated
| order by TimeGenerated desc

// *** Look at the data now returned from the alert query *** //
// You notice that it returned a host name
// Lets search over all of our data using that host name
// Replace HOST_NAME with the name of the host from the first above query
search "HOST_NAME"
| summarize count() by $table
| order by count_ desc

// ************************************************** //
// Replace "10.0.3.4" or "104.211.30.1" with the 
// name private and public ips from the first query
// ************************************************* //

// Lets return to the 2 ip address in the original alert
// One is a public Internet facing IP address and the other is private IP address
// Since there also could be some traffic going through a public facing lP, and 
// it doesn't cost us much, lets use both ip addresses
search ("10.0.3.4" or "104.211.30.1")
| where TimeGenerated >= ago(3d)
| summarize count() by $table
| order by count_ desc

// Interesting!  We see the logs in the network logs  
// Lets dig into that data a little more
// Action: Bookmark the first row
search in (AzureNetworkAnalytics_CL) ("10.0.3.4" or "104.211.30.1")
| where TimeGenerated >= ago(3d)
| order by TimeGenerated desc

// We are not confined to looking at raw tabular data
// here is a quick example of the flows by the hour:
search in (AzureNetworkAnalytics_CL) ("10.0.3.4" or "104.211.30.1")
| where TimeGenerated >= ago(3d)
| order by TimeGenerated desc
| summarize sum(FlowCount_d) by bin(TimeGenerated, 1h)
| render timechart 

// While inbound and outbound are both relevant, lets start with the inbound data
// You can see that it returns all of this nice data 
search in (AzureNetworkAnalytics_CL) ("10.0.3.4" or "104.211.30.1")
| where TimeGenerated >= ago(3d)
| order by TimeGenerated desc
| where FlowDirection_s == "I" 
| where FlowStatus_s <> "D" 
| project SrcIP_s 
| summarize count() by SrcIP_s
| order by count_ desc

// Bookmark this row:
search in (AzureNetworkAnalytics_CL) ("10.0.3.4" or "104.211.30.1")
| where TimeGenerated >= ago(3d)
| order by TimeGenerated desc
| where FlowDirection_s == "I" 
| where FlowStatus_s <> "D" 
| where SrcIP_s == "13.67.35.176"

// Bookmark the '23.97.60.214'
search in (AzureNetworkAnalytics_CL) ("10.0.3.4" or "104.211.30.1")
| where TimeGenerated >= ago(3d)
| order by TimeGenerated desc
| where FlowDirection_s == "I" 
| where FlowStatus_s <> "D"

// This query should look familiar
// Lets search for that ip address that is suspicious
search ("23.97.60.214")
| where TimeGenerated >= ago(3d)
| summarize count() by Type
| order by count_ desc

// Now lets search in the office activity
// Lets bookmark somce of those events
// Hm, I see a significant amount of downloading from sharepoint
// Action: Bookmark first row
// !! Make sure to highlight that you can see what file they are downloading !!
search in (OfficeActivity) "23.97.60.214"
| where TimeGenerated >= ago(3d)
| order by TimeGenerated desc
```
## Hunting Techniques Recommended

- [x] Grouping
- [x] Searching
- [ ] Clustering
- [ ] Stack Counting
- [ ] Scatter Plots
- [ ] Box Plots
- [ ] Isolation Forests
