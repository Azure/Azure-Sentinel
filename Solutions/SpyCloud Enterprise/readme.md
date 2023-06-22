# SpyCloud Enterprise Solution


## Table of Contents

1. [Overview](#overview)
2. [Feed](#feed)
3. [Enrichment](#enrichment)
4. [SpyCloud Enterprise Deployment Instructions](#deployorder)


<a name="overview">

## Overview
Employee account takeover is a type of online fraud that occurs when attackers use stolen logins to gain access to corporate accounts. When employees reuse passwords across multiple online accounts, criminals can exploit credentials that have been exposed in third-party data breaches to access their corporate accounts.

SpyCloud Employee Account Takeover Prevention enables enterprises to stay ahead of account takeover and targeted attacks like ransomware by detecting and resetting compromised passwords early, before criminals have a chance to use them.

This solution contains the following
- 8 Playbooks
- 2 Analytics Rules
- 1 Custom Connector

There are many ways organizations can utilize SpyCloud Intelligence; the playbooks in this solution are just a quick introduction to some of those ways. These playbooks and actions are designed to meet the following use cases

<a name="feed"></a>
## Feed Usecase
| Playbook | Description |
| --------- | -------------- |
| **SpyCloud-Monitor-Watchlist-Data** | This playbook runs on a daily basis, fetches all the watchlist data from the SpyCloud API, parses the data, and saves the data into the custom logs table. |

This solution provides the following rules which monitor the custom log table created from the above playbook.

### Analytics Rules
| Analytic Rule | Description |
| --------- | -------------- |
| **SpyCloud-Malware-Rule** | This scheduled rule monitors the custom log table, and checks for any new malware records(severity=25). If a record is found, this analytic rule will create an incident with High Priority. |
| **SpyCloud-Breach-Rule** | This scheduled rule monitors the custom log table, and checks for any new breach records(severity=20). If a record is found, this analytic rule will create an incident with High Priority. |

When a malware incident is created from the "SpyCloud Malware Rule", we can do the following actions
- Check if the hostname is a managed asset. If no hostname exists in the record, skip this check. 
- For the specific Machine ID, and if the organization has access to compass data, pull all the additional records for the specific machine ID from the appropriate Compass endpoint and add them to the incident. 
- Escalate the incident for someone to handle the malware infection. 

This solution provides a "SpyCloud Malware Playbook" template, that can be used to achieve the above use-case. Please add this playbook to the "SpyCloud Malware Rule" automation section.

When a breach incident is created from the "SpyCloud Breach Rule", we can do the following actions
- Check if breached password length is >= minimum required by the organization. If not, exit the playbook. 
- Check if the user is currently an active employee. If not, exit the playbook. 
- Check if the exposed password is in use on the network (check AD, check Okta, check Ping, check G-Suite, etc. 
- If the password is in use in one of the checked systems, perform a password reset, raise an incident, etc. 

This solution provides a "SpyCloud Breach Playbook" template, that can be used to achieve the above use case. Please add this playbook to the "SpyCloud Breach Rule" automation section.

<a name="enrichment"></a>
## Enrichment Usecase   

| Playbook | Description |
| --------- | -------------- |
| **SpyCloud-Malware-Playbook** | This playbook runs on an incident trigger created by the "SpyCloud Malware Rule", fetches all the entities associated with the incident, and does further investigation. |
| **SpyCloud-Breach-Playbook** | This playbook runs on an incident trigger created by the "SpyCloud Breach Rule", fetches all the entities associated with the incident, and does further investigation.|
| **SpyCloud-Get-Domain-Breach-Data-Playbook** | This playbook runs on an incident trigger, fetches all the domains(DNS Entity) from the incident, retrieves the breach data information from the SpyCloud API for each Domain, and adds the breach data information to incident comments for further investigation. |
| **SpyCloud-Get-IP-Breach-Data-Playbook** | This playbook runs on an incident trigger, fetches all the IP addresses(IP Entity) from the incident, retrieves the breach data information from the SpyCloud API for each IP, and adds the breach data information to incident comments for further investigation. |
| **SpyCloud-Get-Email-Breach-Data-Playbook** | This playbook runs on an incident trigger, fetches all the Email addresses(Account Entity) from the incident, retrieves the breach data information from the SpyCloud API for each Email, and adds the breach data information to the incident comments for further investigation. |
| **SpyCloud-Get-Username-Breach-Data-Playbook** | This playbook runs on an incident trigger, fetches all the Usernames(Account Entity) from the incident, retrieves the breach data information from the SpyCloud API for each Username, and adds the breach data information to incident comments for further investigation. |
| **SpyCloud-Get-Password-Breach-Data-Playbook** | This playbook takes a password as the input and gets the breach data for that password from the SpyCloud API. The results are then processed in a tabular format as the final step. You can use this data for further investigation. |

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
