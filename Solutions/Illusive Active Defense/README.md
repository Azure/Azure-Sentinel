# Illusive Active Defense

<br>
<br>
<p align="center">  
<img width="800" height="300" src="./Images/Illusive.svg"> </a>
</p>
<br>

# Table of Contents

1. [Overview](#overview)
1. [Deploy Playbook templates](#deployall)
1. [Deployment instructions](#deployinstr)
1. [Test the playbook](#testplaybook)
<br>

<a name="overview">

# Overview

Use this playbook to enrich Sentinel security incidents originating from Illusive with Illusive incident and forensics information. 
Illusive continues to enrich relevant Sentinel incidents as new events are detected. This is done using the Illusive API resource. 

<p align="left">  
<img width="800" src="./Images/IncidentEnrichmentPlaybook.png"> </a>
</p>


For more information see:

[Illusive API]
[Logic App Overview](https://azure.microsoft.com/services/logic-apps/) 

<br>
<a name="deployall">

# Deploy Connector and Playbook templates

## This package includes: 

1. Analytic Rule used by the Playbooks
2. Playbook that will enrich Sentinel Incidents and isolate Hosts/Processes based on Illusive Incidents

<br>

<a name="deployinstr">

# Deployment instructions

## Generate an Illusive API Key from Illusive console

 1. In the Illusive Console, navigate to Settings>General>API Keys.
 2. Enter values in the following fields:

    <table>
        <tr>
            <td><b>Field</b></td>
            <td><b>Description and values</b></td>
        </tr>
        <tr>
            <td>Description</td>
            <td>Specify description of key.
                <br>
                    1. All Permissions
                    1. Create Event Read
                    1. Monitoring Data
            </td>
        </tr>
        <tr>
            <td>Permissions</td>
            <td>Select the permission:</td>
        </tr>
        <tr>
            <td>Restrict SourceIP</td>
            <td>Limit the API key to be used only from the specified source IP address. (optional)</td>
        </tr>
    </table>

 3. Click Add.The API Key is created and added to the list of keys shown.
 4. Copy the header containing the key to a text file and save it securely.
 5. The key is valid for one year to access the REST API on this Management Server only.


<a name="testplaybook"> 

# Test the playbook

* Dry run result

    <p align="left">  
    <img width="400" src="./Images/IncidentResponse1.png"> </a>
    </p>

    <p align="left">  
    <img width="400" src="./Images/IncidentResponse2.png"> </a>
    </p>

<br>
<br>
