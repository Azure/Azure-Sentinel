author: Rudi Jubran

based on original playbook by: Nicholas DiCola [(Get-GeoFromIPAndTagIncident)](https://github.com/Azure/Azure-Sentinel/tree/master/Playbooks/Get-GeoFromIpAndTagIncident)

This playbook will take the IP address entities from the Incident and query a Geo-IP API to geo-locate the IP Address. It will write the City, Country, and related Account entites to a tag on the Incident. Then, based on user defined tag conditions, this playbook will either:

1. Close the incident (expected country/city/user combination)
2. Set the Incident to "In Progress", and email an alert containing the user, IP, geo tag and timestamp. (unexpected country/city/user combination)

Tag conditions can be set via Logic app designer, found under "For each 4".

