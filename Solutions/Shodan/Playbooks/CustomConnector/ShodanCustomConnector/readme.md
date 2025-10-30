# Shodan Logic App Custom Connector

This custom connector connects to Shodan endpoint to execute actions supported by Shodan and returns back response in JSON format.

### Authentication methods supported by this connector

* API Key Authentication

### Prerequisites to deploy Custom Connector 
- Have Shodan API Endpoint Url handy (Default: https://api.shodan.io)

### Deployment Instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.
2. Fill in the required parameters:
    - Connector Name: Enter the custom connector name (Default: ShodanCustomConnector)
    - Service Endpoint: Enter the Shodan API endpoint (Default: https://api.shodan.io)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FShodan%2FPlaybooks%2FCustomConnector%2FShodanCustomConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FShodan%2FPlaybooks%2FCustomConnector%2FShodanCustomConnector%2Fazuredeploy.json) 


## Actions supported by Shodan Logic App Connector
*Note: These Actions are build on free tier Shodan account, so not all action are supported.*
| **Component** | **Description** |
| --------- | -------------- |
| **Get Service Details For IP** | Returns all services that have been found on the given host IP. |
| **Get Host Search Count** | Search Shodan using the same query syntax as the website and use facets to get count for different properties. |
| **Search Host** | Search Shodan using the same query syntax as the website and use facets to get summary information for different properties. |
| **Get Domain Info** | Get all the subdomains and other DNS entries for the given domain. |
| **Resolve Domain Name** | Look up the IP address for the provided list of domain names. |
| **Resolve IP To Domain** | Look up the domain names that have been defined for the given list of IP addresses. |
| **Get My IP** | Get your current IP address as seen from the Internet. |
| **Get Account Details** | Returns information about the Shodan account linked to this API key. |
| **Get API Plan Info** | Returns information about the API plan belonging to the given API key. |
| **List Facets** | Returns a list of facets that can be used to get a breakdown of the top values for a property. |
| **List Filters** | Returns a list of search filters that can be used in the search query. |
| **List Ports** | Returns a list of port numbers that the crawlers are looking for. |
| **List Protocols** | Returns an object containing all the protocols that can be used when launching an Internet scan. |
| **Get Search Query Tokens** | Get the filters being used by the query string and parameters provided to the filters. |


#  References
 - [Shodan API Quick Reference](https://developer.shodan.io/api)
 - [Shodan Search Filters Reference](https://www.shodan.io/search/filters)
 - [Get Shodan API Key](https://developer.shodan.io/api/requirements)