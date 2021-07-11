# Whois/Registration Data Access Protocol (RDAP) Query Azure Function
----
As top level domains (and domains in general) have increased, there is a need to be able to lookup information about domains.  This project is designed to solve this need (in an albeit limited use case for now) by retrieving domain(s) from Azure Sentinel / Log Analytics, querying the RDAP network for registration information, and then writing that resolution information back in to Azure Sentinel / Log Analytics.  
