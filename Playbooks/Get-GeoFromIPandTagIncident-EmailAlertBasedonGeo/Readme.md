Author: Rudi Jubran

Based on original playbook by: Nicholas DiCola [(Get-GeoFromIPAndTagIncident)](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/Get-GeoFromIpAndTagIncident)

This playbook will take the IP address entities from the Incident and query a Geo-IP API to geo-locate the IP Address. It will then write the City, Country, and Account entites to tags on the Incident. Then, these tags are compared to a user-defined condition, and unexpected City/Country/User become alerts. Expected incidents are closed.

In summary, according to Incident tags, the playbook will either:

1. Close the incident (If incident matches expected country/city/user)
2. Set the Incident to "In Progress", and email an alert containing the user, IP, geo tag and timestamp. (If incident does not match defined country/city/user)

**Configure the following via Logic App Designer**:

_Define expected tags:_

![image](https://user-images.githubusercontent.com/60908383/102939747-d67bc080-447c-11eb-840e-bdc4a1a51903.png)

_Define "to" address for alerts:_

![image](https://user-images.githubusercontent.com/60908383/102939800-f1e6cb80-447c-11eb-8f12-9402ab76306a.png)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Frjubran%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-GeoFromIPandTagIncident-EmailAlertBasedonGeo%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Frjubran%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FGet-GeoFromIPandTagIncident-EmailAlertBasedonGeo%2Fazuredeploy.json)