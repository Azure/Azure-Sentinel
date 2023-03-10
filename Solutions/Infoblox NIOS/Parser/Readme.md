Infoblox Parser is divided into KQL functions, details of KQL functions are listed below- 
<h2>DNS specific KQL functions</h2>
Infoblox_dnszone</br>
Infoblox_dnsgss</br>
Infoblox_dnsclient</br>

<h2>DHCP specific KQL functions</h2>
Infoblox_dhcpsession</br>
Infoblox_dhcprequest</br>
Infoblox_dhcpremoved</br>
Infoblox_dhcprelease</br>
Infoblox_dhcpother</br>
Infoblox_dhcpoption</br>
Infoblox_dhcpoffer</br>
Infoblox_dhcpinform</br>
Infoblox_dhcpexpire</br>
Infoblox_dhcpdiscover</br>
Infoblox_dhcpbindupdate</br>
Infoblox_dhcpadded</br>
Infoblox_dhcpack</br>

<h2>Common functions</h2>
Infoblox_dhcp_consolidated</br>
Infoblox_dns_consolidated</br>
Infoblox_consolidated</br>
Infoblox_allotherlogTypes</br>
Infoblox_allotherdnsTypes</br>
Infoblox_allotherdhcpdTypes</br>

<h2> Deployment Steps</h2>
All KQL functions are deployed as part of solution. To create manually, please follow following steps:</br> 
1. Open Log Analytics/Microsoft Sentinel Logs blade. Copy the KQL query and paste into the Logs query window. </br>
2. Click the Save button above the query. A pane will appear on the right, select "as Function" from the drop down. Enter a Function Name.</br>
3. Function App usually take 10-15 minutes to activate. You can then use Function Alias for other queries</br>
