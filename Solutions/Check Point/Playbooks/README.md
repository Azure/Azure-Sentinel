# Check Point Software Technologies Logic Apps Playbook
<br>
<br>
<p align="center">  
<img width="800" src="../images/check_point_logo.png"> </a>
</p>
<br>

# Table of Contents

1. [Overview](#overview)
1. [Deploy Playbook](#deploy)
1. [Test Playbook](#testplaybook)
1. [Key Playbook Components](#playbookdetail)

<br>

<a name="overview">

# Overview

The Check Point Logic App Playbook allow you to make changes to Check Point firewalls via Check PointManagement API.

<p align="left">  
<img width="800" src="../images/cp_integration_detail.png"> </a>
</p>

Common use cases include: 

  1. Enable operation teams to automate common security functions such as creating objects, updating security policies, and schedule security policy updates to gateways. 
  2. Fully integrate with any orchestration platforms for both on-prem or public cloud providers
  3. Integrate with all leading SIEM/SOAR providers such as Azure Sentinel

For more information see

[Check Point Management API](https://sc1.checkpoint.com/documents/latest/APIs/#introduction~v1.6%20)  
[Logic App Overview](https://azure.microsoft.com/services/logic-apps/) 



<a name="deploy">

# Deploy Playbook

## This package includes: 

This Playbook will create IP objects and add objects to group. 

As prerequisite you'll need to first deploy the Check Point Connector in your subscription before you can install this playbook. 

   [![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazure.svg)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fchkp-jguo%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2FPlaybooks%2Fadd-host-to-group%2FdeployCPplaybook.json)
   [![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fchkp-jguo%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2FPlaybooks%2Fadd-host-to-group%2FdeployCPplaybook.json)

<br>

<a name="deployinstr">

# Deployment instructions

1. Create an API key from Check Point management console

    <p align="left">  
    <img width="400" src="../images/cp_create_api_key.png"> </a>
    </p>

2. Launch the template

   [![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazure.svg)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fchkp-jguo%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2FPlaybooks%2Fadd-host-to-group%2FdeployCPplaybook.json)
   [![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazuregov.png)](https://portal.azure.us/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fchkp-jguo%2FAzure-Sentinel%2Fmaster%2FSolutions%2FCheck%2520Point%2FPlaybooks%2Fadd-host-to-group%2FdeployCPplaybook.json)

3. Fill in the template

    <p align="left">  
    <img width="400" src="../images/cp_logicapp_deploy.png"> </a>
    </p>

4. Update LogicApp Sentinel Connection

    <p align="left">  
    <img width="400" src="../images/cp_logicapp_sentinel.png"> </a>
    </p>

<br>

<a name="testplaybook"> 

# Test Playbook

* Dry run

    <p align="left">  
    <img width="400" src="../images/cp_logicapp_test.png"> </a>
    </p>
    
* Dry run result

    <p align="left">  
    <img width="400" src="../images/cp_logicapp_test_result.png"> </a>
    </p>

<a name="playbookdetail"> 

# Key Playbook Components
<br>

1. Trigger point - It can be scheduled, use HTTP post, or trigger point from a connector

    Example 1 - Scheduled tasks
    <p align="left">  
    <img width="400" src="../images/example1.png"> </a>
    </p>

    Example 2 - Azure Sentinel Alert
    <p align="left">  
    <img width="400" src="../images/example2.png"> </a>
    </p>

    Example 3 - HTTP post
    <p align="left">  
    <img width="400" src="../images/example3.png"> </a>
    </p>

2. Workflow - Logic App instructions

    Define the Check Point gateway and policy package
    <p align="left">  
    <img width="400" src="../images/workflow1.png"> </a>
    </p>

	Define the Check Point Management Station API Key or usr/pw
    <p align="left">  
    <img width="400" src="../images/workflow2.png"> </a>
    </p>

    Define what action to take, in this case, create and add each host to predefined group
    <p align="left">  
    <img width="400" src="../images/workflow3.png"> </a>
    </p>

    Publish and Install Security Policy
    <p align="left">  
    <img width="400" src="../images/workflow4.png"> </a>
    </p>
