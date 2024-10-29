# MDTI Actor Lookup

Welcome to the **MDTI Actor Lookup** project! This repository focuses on using the MDTI API, a function app, and a logic app together to automate Threat Infrastructure Chaining, also Copilot for Security assists us with detailed actor group information.

## Table of Contents

1. Introduction
2. Features
3. Getting Started
4. Deployment
5. Usage


## Introduction

The MDTI Actor Lookup project leverages the MDTI API, a function app, and a logic app to automate the process of Threat Infrastructure Chaining. This automation helps in identifying and linking threat actors and their infrastructure efficiently.  There are a few requirements to be aware of before we begin:

- The base requirements to use the function app will be the code, a working function app plan (in our case we're using consumption) and an MDTI API license.
- To use the Logic App, you will need Sentinel to be deployed and generating incidents (or you could change the trigger).
- A Copilot for Security SCU or as many as the organization requires.

- **Deploying the MDTI API** - https://review.learn.microsoft.com/en-us/graph/api/resources/security-threatintelligence-overview?branch=main&branchFallbackFrom=pr-en-us-21547&view=graph-rest-1.0
- **Choosing a Function Apps plan** - https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale
- **Deploy Copilot SCUs** - https://learn.microsoft.com/en-us/copilot/security/get-started-security-copilot

Seems like a lot right?  But most of these items are deployed within your environment if you're an existing Sentinel customer.

**The function app will perform the following tasks:**

1. For a given IOC (IP/Domain) the app will iterate through associated pdns information, for as long as the IP has been active.
2. The MDTI reputation endpoint will provide an output of a score but also indicate if we have actor attribution to the IOC
3. If an actor group is found, a list of the actor name(s) and the associated domain/ip will be provided.

**The Logic app will perform the following tasks:**

1. Take any found actor group, remove the domains and create an array
2. Pass the groups to Copilot for Security and ask for a summary
3. Copilot will write out a comment for each group containing a detailed summary of the group as well as look at Threat Analytics (for MDE customers) to show affected machines based on known vulnerabilities
4. The incident will be changed to high severity and Active status.  Also the LA will add tags of the actor group name to the incident

## Why did you make this?

Good question!  Organizations struggle to operationalize threat intel, meaning how do they take the wealth of knowledge provided by a solution like MDTI and automate it into their business processes?  It's not easy to develop scripts and automations while putting out fires all over the place so I wanted to create something that defenders could use in the background all day long that did the heavy lifting of infrastructure chaining.  The aim of this project is to allow defenders to operationlize TI within minutes instead of hours/days/weeks/never and provide a solution that ensures higher fidelity of alerts than just ingestings a STIX/TAXII feed.

## Features

- **Automated Threat Infrastructure Chaining**: Streamlines the process of identifying and linking threat actors.
- **Integration with MDTI API**: Utilizes the MDTI API for data retrieval and processing.
- **Azure Deployment**: Easily deployable to Azure for seamless integration and operation.

## Getting Started

To get started with the MDTI Actor Lookup project, you'll need to have an Azure account and the necessary permissions to deploy resources.  Also this playbook will use Copilot for Security to provide threat actor summaries.  The MDTI API is a licensed feature, if you do not have the license please reach out to your account representative for purchase info and/or trial assistance.

You can however just use the MDTI API and the function app and hook them into whichever system you'd like.  You'll lose the SOAR functionality but you'll stil get the benefit of lightning fast infra chaining.  Also you could use Copilot for more enrichment also, consider also adding a teams card or an email to alert your internal groups that an actor group has been found.

There is no current condition to limit the history of the lookup, this is because if you're too recent you might miss that you had some interaction months ago, as well you'd not be able to link groups together like in this video - 

## Deployment of the Function App

Follow these steps to deploy the application to Azure:

1. Deploy a function app using the Azure Portal or VSCode (Recommended) - https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python
2. Download the MDTIAFunc.zip file and extract the files.
3. Open extracted folder in VSCode and modify the section in function_app.py for your MDTI client, client secret and tenant ID.
4. In VSCode, publish to your function app and verify that you see the trigger working.
5. Note the code to connect to your function app, you'll want to add this to a keyvault to avoid connecting in plaintext

Why no arm template?  Well the function_app.py trigger will fail because the API information is not prefilled, which will mean you have to essentially do everything I mention above anyway to fill it and then republish so I'm saving you the headache of troubleshooting :D

## Deployment of the Logic App

1. Once your function app is deployed, first deploy the Content Hub solution called "Microsoft Defender Threat Intelligence"
2. Configure the playbook MDTI-Base with your client id, client secret and publish the playbook
3. Run the deployment arm template from the button below
4. Whenever you deploy a logic app from template you have to establish the connections for Sentinel/Copilot and your keyvault, just click on the items and set the account
5. Test your playbook by running it on any incident with an external IP/domain

<a href="https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FMrSharpBones%2FMDTI%2Frefs%2Fheads%2Fmain%2FMDTI%2520Actor%2520Lookup%2FLogic%2520App%2Fazuredeploy.json" target="_blank">
  <img src="https://aka.ms/deploytoazurebutton"/>
</a>


## Usage

Once deployed, you can attach the playbook to any/all Sentinel playbooks, Copilot will only be invoked should an actor group show up on in the results.  The MDTI API allows for unlimited (but throttled) API queries, so you can use this as much as you want without the worry of overage fees.  This could run tens of thousands of API queries a day, without creating any noise without a hit(s)



