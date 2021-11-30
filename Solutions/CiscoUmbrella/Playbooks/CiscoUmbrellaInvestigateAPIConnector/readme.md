# Cisco Umbrella Investigate API Logic Apps Custom connector

This Custom Connector is used for connection to Cisco Umbrella Investigate API.

### Authentication methods supported by this connector

* API Key authentication

### Prerequisites in Cisco Umbrella

To get Cisco Umbrella Investigate API credentials follow the instructions:

1. Login to your Cisco Umbrella dashboard.
2. Navigate to Investigate > API Keys.
3. To create your first API access token, click Create New Token.
4. Give the token a name, then click Create.

## Actions supported by Cisco Umbrella Investigate API custom connector

| **Component** | **Description** |
| --------- | -------------- |
| **Get domain security data** | The security information API method contains multiple scores or security features, each of which can be used to determine relevant datapoints to build insight on the reputation or security risk posed by the site. |
| **Get risk score for a domain** | The Umbrella Investigate Risk Score is based on an analysis of the lexical characteristics of the domain name and patterns in queries and requests to the domain. The score is scaled from 0 to 100, with 100 being the highest risk and 0 being no risk at all. Periodically Umbrella updates this score based on additional inputs. A domain blocked by Umbrella receives the score of 100. |
| **Get domain status and categorization** | Returns the domain status which is the quickest and easiest way to know whether a domain has been flagged as malicious by the Cisco Security Labs team (score of -1 for status). If the domain is believed to be safe (score of 1), or if it has yet to be given a status (score of 0). This method also returns the security categories and content categories of a domain. |
| **Get co-occurrences for a domain** | This API method returns a list of co-occurences for the specified domain. A co-occurrence is when two or more domains are accessed by the same users within a small period of time. |
| **Get Related Domains** | This API method returns a list of domain names that have been frequently requested during a defined period of time (up to 60 seconds before or after) as the given domain name, but are not frequently associated with other domain names. |

### Deployment instructions

1. To deploy Custom Connector, click the Deploy to Azure button. This will launch the ARM Template deployment wizard.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCiscoUmbrella%2FPlaybooks%2FCiscoUmbrellaInvestigateAPIConnector%2Fazuredeploy.json) [![Deploy to Azure](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCiscoUmbrella%2FPlaybooks%2FCiscoUmbrellaInvestigateAPIConnector%2Fazuredeploy.json)