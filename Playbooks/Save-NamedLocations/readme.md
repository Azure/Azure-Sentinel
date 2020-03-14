# Save-NamedLocations
author: Thijs Lecomte

This Playbook will retrieve the Named Locations from Azure Active Directory Conditional Access and save them in Log Analytics.
These named locations can be used in hunting queries.

An app registration should be created with permissions: Policy.Read.All.
The API Connection to the Log Analytics Workspace should be updated with the Workspace ID and key after deploying this.

This playbook uses an Azure Function to convert CIDR ranges to IP-addresses.