# Save-NamedLocations
author: Thijs Lecomte

This Playbook will retrieve the Named Locations from Azure Active Directory Conditional Access and save them in Log Analytics.
These named locations can be used in hunting queries.

An app registration should be created with permissions: Policy.Read.All.

This playbook uses an Azure Function to convert CIDR ranges to IP-addresses.
The function is deployed from the zip file which can be found in this repo.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)]("https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FSave-NamedLocations%2Fazuredeploy.json)
[![Deploy to Azure Gov](https://aka.ms/deploytoazuregovbutton)]("https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2FAzure-Sentinel%2Fmaster%2FPlaybooks%2FSave-NamedLocations%2Fazuredeploy.json)