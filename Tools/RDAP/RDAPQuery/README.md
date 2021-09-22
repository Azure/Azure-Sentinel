# Whois/Registration Data Access Protocol (RDAP) Query Azure Function
----
As top level domains (and domains in general) have increased, there is a need to be able to lookup information about domains such as when they were registered, who owns them, etc.  This project is designed to solve this need (in an albeit limited use case for now) by retrieving domain(s) from Azure Sentinel / Log Analytics, querying the RDAP network for registration information, and then writing that resolution information back in to Azure Sentinel / Log Analytics.  

RDAPQuery is an Azure Function written in c# that runs on a timer (default 10 minutes) and executes a query against your Azure Sentinel environment (GetDomainsForRDAP) to retrieve a list of the domains that have recently been seen in your environment.
