
# Sample rule - Vulnerability on High Value Assest 

This sample rule leverages one of the "High Value Assest" built-in templates as a lookup list to compare with query results of vulnerability data ingested from Microsoft Defender for Endpoint using a logic app and based on a custom query defined in the app.


```
    let watchlst=(_GetWatchlist('HighValueAssets')) //extract watchlist contents and store in variable -> watchlst 
        | project SearchKey;   // specify the searchkey
    let secalert=(SecurityAlert //extract hosts from alert and append domain name to match Asset FQDN SearhKey format in the    Watchlist
        | where TimeGenerated > ago(14d)
        | where AlertName contains "Installed software with public exploit detected" 
        | where Entities has "HostName"
        | extend entities = todynamic(Entities)
        | mv-apply Entity = entities on (
           where Entity.Type == "host"
        | extend HostName = Entity.HostName)
        | extend AppendDom=strcat(HostName, ".contoso.com"));
    secalert
    | extend HostName=tostring(HostName)
    | join MDE_TVM_PublicExploits_CL on $left.HostName == $right.DeviceName_s // confirm presence of hosts in vulnerability data snapshot 
    | where TimeGenerated > ago(14d)
    | where VulnerabilitySeverityLevel_s == "High" and AppendDom in~ (watchlst) //match hosts with high severity vulnerabilities and presence in HVA watchlist based on SearchKey
    | distinct DeviceName_s, VulnerabilitySeverityLevel_s, VulnerabilityDescription_s
```






