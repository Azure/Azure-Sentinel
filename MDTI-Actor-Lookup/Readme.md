# MDTI Actor Lookup

Welcome to the **MDTI Actor Lookup** project! This repository focuses on using the MDTI API, a function app, and a logic app together to automate Threat Infrastructure Chaining, also Copilot for Security assists us with detailed actor group information.

## Table of Contents

1. Introduction
2. Features
3. Getting Started
4. Deployment
5. Usage
6. Contributing
7. License

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

You can however just use the MDTI API and the function app and hook them into whichever system you'd like.  You'll lose the SOAR functionality but you'll stil get the benefit of lightning fast infra chaining.

## Deployment of the Function App

Follow these steps to deploy the application to Azure:

1. Deploy using the button below.
2. Choose your regions for app services deployment, you might encounter an error with the API version (different regions support different versions), if so correct in the template and redeploy.
3. The files will be deployed but some settings in function_app.py will remain so you will need to edit the file. Fill in your client id, secret and tenant info and away you go.

## Deployment of the Logic App



## Usage

Once deployed, you can attach the playbook to any/all Sentinel playbooks, Copilot will only be invoked should an actor group show up on in the results.  The MDTI API allows for unlimited (but throttled) API queries, so you can use this as much as you want without the worry of overage fees.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

---

Happy coding! If you have any questions or need further assistance, feel free to reach out.

