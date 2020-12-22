author: Rudi Jubran

based on original playbook by: Nicholas DiCola [(Get-GeoFromIPAndTagIncident)](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/Get-GeoFromIpAndTagIncident)

This playbook will take the IP address entities from the Incident and query a Geo-IP API to geo-locate the IP Address. It will write the City, Country, and related Account entites to a tag on the Incident. Then, based on user defined tag conditions, this playbook will either:

1. Close the incident (If matches defined country/city/user)
2. Set the Incident to "In Progress", and email an alert containing the user, IP, geo tag and timestamp. (does not match defined country/city/user)

Config via Logic App Designer:

![image](https://user-images.githubusercontent.com/60908383/102939747-d67bc080-447c-11eb-840e-bdc4a1a51903.png)
![image](https://user-images.githubusercontent.com/60908383/102939800-f1e6cb80-447c-11eb-8f12-9402ab76306a.png)


