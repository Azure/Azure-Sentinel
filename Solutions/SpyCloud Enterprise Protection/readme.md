# SpyCloud Enterprise Solution


## Table of Contents

1. [Overview](#overview)
2. [Feed](#feed)
3. [Enrichment](#enrichment)
4. [SpyCloud Enterprise Deployment Instructions](#deployorder)


<a name="overview">

## Overview
Cybercriminals continue to utilize stolen corporate credentials as the number one technique for account takeover (ATO). In fact, the FBI estimated that this resulted in estimated losses totaling more than $2.7 billion in 2022. SpyCloud helps prevent account takeover and ransomware attacks by identifying exposed credentials related to a company’s domains, IP addresses and emails. Through this integration, breach and malware data from SpyCloud can be loaded into Sentinel. 

This solution contains the following:

- Eight playbooks,

- Two analytics rules, and 

- One custom connector. 

By identifying exposed assets that are available to criminals, enterprises can protect exposed accounts before criminals have a chance to use them for follow-on attacks These playbooks and actions are designed to meet several use cases.

<a name="feed"></a>
## Feed Usecase
| Playbook | Description |
| --------- | -------------- |
| **SpyCloud-Monitor-Watchlist-Data** | This playbook runs on a daily basis, and fetches all the watchlist data from the SpyCloud Enterprise Protection API, parses the data, and saves the data into the custom logs table. |

This solution provides the following rules which monitor the custom log table created from the above playbook.

### Analytics Rules
| Analytic Rule | Description |
| --------- | -------------- |
| **SpyCloud-Malware-Rule** | This scheduled rule monitors the custom log table, and checks for any new malware records(severity=25). If a record is found, this analytic rule will create an incident with High Priority. |
| **SpyCloud-Breach-Rule** | This scheduled rule monitors the custom log table, and checks for any new breach records(severity=20). If a record is found, this analytic rule will create an incident with High Priority. |

Many actions are available when a malware incident is created from the "SpyCloud Malware Rule." It can:

- Check if the hostname is a managed asset. If no hostname exists in the record it will skip this check.
- Pull all the additional records for the specific machine ID from the appropriate endpoint and add them to the incident, if you have access to SpyCloud Compass data. 
- Escalate the incident for someone to handle the malware infection. 

This solution also provides a "SpyCloud Malware Playbook" template that can be used to achieve the above use case. You can add this playbook to the "SpyCloud Malware Rule" automation section.

The following actions can be taken when a breach incident is created from the "SpyCloud Breach Rule."

- Check if breached password length is >= minimum required by the organization. If not, exit the playbook. 
- Check if the user is currently an active employee. If not, exit the playbook. 
- Check if the exposed password is in use on the network (check AD, check Okta, check Ping, check G-Suite, etc. 
- If the password is in use in one of the checked systems, perform a password reset, raise an incident, etc. 

This solution also provides a "SpyCloud Breach Playbook" template that can be used to achieve the above use case. You can add this playbook to the "SpyCloud Breach Rule" automation section.

<a name="enrichment"></a>
## Enrichment Usecase   

| Playbook | Description |
| --------- | -------------- |
| **SpyCloud-Malware-Playbook** | This playbook runs on an incident trigger created by the "SpyCloud Malware Rule," fetches all the entities associated with the incident, and does further investigation. |
| **SpyCloud-Breach-Playbook** | This playbook runs on an incident trigger created by the "SpyCloud Breach Rule," fetches all the entities associated with the incident, and allows for further investigation.|
| **SpyCloud-Get-Domain-Breach-Data-Playbook** | This playbook runs on an incident trigger, fetches all the domains(DNS Entity) from the incident, retrieves the breach data information from the SpyCloud API for each Domain, and then adds the breach data information to incident comments for further investigation. |
| **SpyCloud-Get-IP-Breach-Data-Playbook** | This playbook runs on an incident trigger, fetches all the IP addresses (IP Entity) from the incident, retrieves the breach data information from the SpyCloud API for each IP, and then adds the breach data information to incident comments for further investigation. |
| **SpyCloud-Get-Email-Breach-Data-Playbook** | This playbook runs on an incident trigger, fetches all the Email addresses (Account Entity) from the incident, retrieves the breach data information from the SpyCloud API for each email address, and then adds the breach data information to the incident comments for further investigation. |
| **SpyCloud-Get-Username-Breach-Data-Playbook** | This playbook runs on an incident trigger, fetches all the usernames (Account Entity) from the incident, retrieves the breach data information from the SpyCloud API for each username, and then adds the breach data information to incident comments for further investigation. |
| **SpyCloud-Get-Password-Breach-Data-Playbook** | This playbook takes a password as the input and identifies the breach data for that password from the SpyCloud API. The results are then processed in a tabular format as the final step. You can use this data for further investigation. |

Please refer to the documentation pages for each playbook for more information.


<a name="deployorder"></a>
## Deployment Instructions

Please follow the following order while installing the solution.

1. CustomConnector
2. SpyCloud Monitor Watchlist Data Playbook
3. SpyCloud Malware Playbook
4. SpyCloud Breach Playbook
5. Analytics Rules
6. Domain Breach Data Playbook
7. Email Breach Data Playbook
8. IP Address Breach Data Playbook
9. Username Breach Data Playbook
10. Password Breach Data Playbook
