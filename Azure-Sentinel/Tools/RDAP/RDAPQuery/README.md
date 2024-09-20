# Registration Data Access Protocol (RDAP) Query Engine
----
Author:  Matt Egen 

mattegen@microsoft.com

<a href="https://twitter.com/FlyingBlueMonki?ref_src=twsrc%5Etfw" class="twitter-follow-button" data-show-count="true">Follow @FlyingBlueMonki on Twitter</a>

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FTools%2FRDAP%2FRDAPQuery%2Fazuredeploy.json)

With the ever increasing number of new domains on the Internet as well as all of the new Top Level Domains (TLD), it's often hard to know if a user has gone to a potentially malicious new site that has just popped up online.  To help with this, a SOC team or analyst could track for users accessing newly registered domains.  One way to do this is to query the Registration Data Access Protocol (RDAP).  RDAP allows you to access domain name registration data (much like its predecesor the WHOIS protocol does today) but via an API call and with a better, more machine readable structure to the data.  This Azure Function queries an Azure Sentinel environment, finds domain names of interest, and then conducts an RDAP lookup to retrieve information about the domain for investigators and analysts.  There is also an Azure Sentinel Analytic rule that can then alert if evidence of a domain that was registered in the last 30 days should be found.  

Please note:  This version only stores the registration date of the domains successfully resolved, but you could modify it to store more information such as who registered the domain, address information, contact data etc.

Also note: Not all TLD's support RDAP.  The current version of the code does not account for this _except_ to ignore TLD's you specifiy.  A future version of this function is planned to support traditional WHOIS lookups as well if there is enough interest.

## Setup Steps
When deploying this Azure Function you will need some values to fill in the blanks for the Azure Resource Manager (ARM) Template:

### Function Name
The name you want to give the Azure Function.  The Default is "RDAPQuery".  A unique string will be attached to this in order to deconflict with any potential pre-existing functions you may have.  For example, the template may create a name like "rdapquerytbdem24sevgdq"

### Azure AD App Permissions
The Azure Function needs permission to read the Log Analytics Workspace that your Azure Sentinel instance is attached to.  For guidance on creating an Azure AD App Registration, please see [QuickStart: Register App](https://docs.microsoft.com/azure/active-directory/develop/quickstart-register-app).  For this application you will need the following permissions:  
````
Log Analytics API
Data.Read
````
After registering your application, you will need the Client ID and Client Secret for the ARM Template.


### Azure Tenant ID
To authenticate, the Azure Function will need to know your Tenant ID to call the proper Azure AD authentication end point

## Azure Log Analytics Resource Location
This value is used in building the Token to read data from your Log Analytics environment.  It specifies the service you're trying to access.  It is in the format of "https://[location].api.loganalytics.io".  For example, a resource in westus2 is "https://westus2.api.loganalytics.io".  You should specify the entire path (e.g. "https://westus2.api.loganalytics.io" not just "westus2"


### Workspace ID and Workspace Shared Key
The Azure Function will write data to the Log Analytics Workspace that your Azure Sentinel instance is attached to.  This data is available on the Agents Management page of your Log Analytics Workspace.  You can get to this page in Sentinel by going to Settings --> Workspace Settings --> Agents Management.  While there is only one Workspace ID, there are two possible keys for you to choose from, either one will work.

### Log Analytics Custom Log Name
The name you want to use for your resolved domains.  The default is ResolvedDomains.  Note:  Log Analytics will automatically append "\_CL" to the end of whatever string you enter here.



### Post Template Configuration
After deploying the ARM Template, you should go in to your Azure Sentinel instance and create the GetDomainsForRDAP function.  An example is included in this repo, but you can use any function you want so long as it returns a field named "Domain" that has the domain you are looking up information for.  

## Description and Workflow
----
RDAP Query Engine is comprised of two main components each of which has some subcomponents
### The Log Analytics Queries and Custom Tables
GetDomainsForRDAP - Log Analytics Function
Since we're looking for information about domains in our Azure Sentinel environment, we have to first get those domains.  For this version, I'm only searching in one table: DeviceNetworkEvents.  DeviceNetworkEvents is a table from M365 Defender and has the networking events that occurred on the enrolled devices in my environment.  To get the domains, I've created a function called GetDomainsForRDAP which looks like this:

````
// A dynamic list of domains and TLDs to not bother searching for
let ExcludedDomains = dynamic(["cn","io", "ms"]);
DeviceNetworkEvents
| where TimeGenerated >= ago(1h)
| where isnotempty(RemoteUrl)
// A little cleanup just in case
| extend parsedDomain = case(RemoteUrl contains "//", parse_url(RemoteUrl).Host, RemoteUrl)
| extend cleanDomain = split(parsedDomain,"/")[0]
| extend splitDomain = split(cleanDomain,".")
| extend Domain = tolower(strcat(splitDomain[array_length(splitDomain)-2],".",splitDomain[array_length(splitDomain)-1]))
| extend TLD = splitDomain[array_length(splitDomain)-1]
| where TLD !in(ExcludedDomains)
| where Domain !in(ExcludedDomains)
| summarize DistinctDomain = dcount(Domain) by Domain
| project Domain
// | join kind=leftanti (ResolvedDomains_CL | where TimeGenerated >= ago(90d)) on $left.Domain == $right.domainName_s //Uncomment this line after the FIRST run of the Azure Function.  Otherwise the query will throw an error until the ResolvedDomains_CL table is instantiated
````
This function extracts the domain values from the DeviceNetworkEvents table, de-duplicates them, and then does a leftanti join to the ResolvedDomains_CL table (leftanti meaning "show me everything in the left table (DeviceNetworkEvents) that's not in the right table (ResolvedDomains_CL)").  ResolvedDomains_CL is where the Azure Function stores its results.  Thus if we've already looked up this domain in the last 90 days (or longer depending on how long you want to retain the data) we don't bother looking it up again.  The resulting domains are used in the Azure Function to resolve their information in RDAP.  Note:  Using a Log Analytics function like this means that we can change the source data (include more / different sources) by just changing the function query without having to modify the RDAP Query Engine code itself.

### ResolvedDomains - Log Analytics Custom Log
This is the custom log where RDAP Query Engine writes its results to.  In my current implementation the tables consists of the domain name (domainName_s) and domain registration date (registrationDate_t).  There is a LOT more information available in an RDAP record, however for this particular case I merely wanted to know when a domain was registered so that if a user were to travel to a domain that was registered within the last 30 days I could raise an alert.  This is a configurable value.

### Newly Registered Domain Detected - Azure Sentinel Analytic Rule
This rule is based on the information contained in the ResolvedDomains_CL log table.  It runs once an hour and looks for any new records in the ResolvedDomains_CL table that have a registration date within the last 30 days
````
ResolvedDomains_CL
| where TimeGenerated >= ago(1h)
| where registrationDate_t >= ago(30d)
````
If so, it then raises an alert in Azure Sentinel for an analyst to investigate

## The Azure Function
Now that we understand where the source data is coming from, time to look at the Azure Function itself.  The basic Azure Function triggered every 30 minutes and the first thing it does is call into LogAnalytics and runs the GetDomainsForRDAP Function.  For each domain that is returned, it extracts the Top Level Domain (TLD) and calls the RDAP BootStrap server to find the server that handles that particular TLD.  For example, if the domain we're looking up is crazyfunnyhats.com the function extracts the TLD as "com", calls the bootstrap server (https://data.iana.org/rdap/dns.json) and discovers that the COM TLD is serviced by "https://rdap.verisign.com/com/v1/".  It then calls that service endpoint with the properly constructed URI ("https://rdap.verisign.com/com/v1/domain/crazyfunnyhats.com") parses the results and then calls the Log Analytics API to insert the registration data into the ResolvedDomains_CL table.

![Workflow Diagram](/Documentation/ProcessWorkflow.jpg)

## Gotchas / Issues / Bugs
----
The following are some issues I’ve run into on this project.  I am still working on more elegant solutions for them, but for now the workarounds (if available) seem to work.

##### GetDomainsForRDAP returns IP addresses (both IPv4 and IPv6) and they don't resolve
This is an artifact of the way that DeviceNetworkEvents returns data.  If the target was an IP address then DeviceNetworkEvents returns that information.  Since RDAP Query Engine doesn't process IP addresses at this time there are some remnants left in the GetDomainsForRDAP query.  These are ignored / error out in the subsequent RDAP query so they don't cause any issues.  Future plans are to clean up the GetDomainsForRDAP function to ignore these scenarios completely.





