# Guide to building Microsoft Sentinel solutions

This guide provides an overview of Microsoft Sentinel solutions, and how to build and publish a solution for Microsoft Sentinel.

Microsoft Sentinel solutions provide an in-product experience for central discoverability, single-step deployment, and enablement of end-to-end product, domain, and/or vertical scenarios in Microsoft Sentinel. This experience is powered by:

- [Azure Marketplace](https://azuremarketplace.microsoft.com/marketplace/) for solution discoverability, deployment, and enablement
- The [Microsoft Partner Center](https://learn.microsoft.com/en-us/partner-center/enroll/overview) for solution authoring and publishing

Providers and partners can deliver combined product, domain, or vertical value via solutions in Microsoft Sentinel in order to productize investments. More details are covered in the [Microsoft Sentinel documentation](https://aka.ms/azuresentinelsolutionsdoc). Review the [catalog](https://aka.ms/sentinelsolutionscatalog) for complete list of out-of-the-box Microsoft Sentinel solutions. 

Microsoft Sentinel solutions include packaged content, integrations, or service offerings for Microsoft Sentinel. This guide focuses on how to build packaged content into solutions, including combinations of data connectors, workbooks, analytic rules, playbooks, hunting queries, parsers, watchlists, and more for Microsoft Sentinel. Reach out to the [Microsoft Sentinel Solutions Onboarding Team](mailto:AzureSentinelPartner@microsoft.com) if you are planning or building another type of integration or service offering, or want to include other types of content in your solution that isn't listed here.

The following image shows the steps in the solution building process, including content creation, packaging, and publishing:

![Microsoft Sentinel solutions build process](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Images/solutions_steps.png)

## Step 1 – Develop a SIEM solution for Microsoft Sentinel

For a detailed walkthrough of how to develop a SIEM solution for Microsoft Sentinel, please refer to the following link - https://learn.microsoft.com/en-us/azure/sentinel/isv/develop-siem-solutions-overview

Use the following instructions when storing sample data and submitting a PR:

1. Store sample data in the [sample data folder](https://github.com/Azure/Azure-Sentinel/tree/master/Sample%20Data), within the relevant content type folder, depending on your data connector type.

2. Submit a PR with all of your solution content. The PR will go through automated GitHub validation. [Address potential errors](https://github.com/Azure/Azure-Sentinel/wiki#test-your-contribution) as needed. 

After your content has been successfully validated, the Microsoft Sentinel team will review your PR and reply with any feedback as needed. You can expect an initial response within five business days.

The PR will be approved and merged after any feedback has been incorporated and the full review is successful.

## Step 2 – Publish your solution

For a detailed walkthrough of how to publish your solutions, please refer to the following links - 

1. Publish solutions to Microsoft Sentinel - https://learn.microsoft.com/en-us/azure/sentinel/publish-sentinel-solutions

2. Solution tracking after publishing in the Microsoft Partner Center - https://learn.microsoft.com/en-us/azure/sentinel/sentinel-solutions-post-publish-tracking


### Certification FAQs:

+ #### What Search keyword must be present for Sentinel solutions? 
&emsp;&emsp;&emsp; The Search keyword must contain the Sentinel GUID: **f1de974b-f438-4719-b423-8bf704ba2aef**. 

+ #### Is the text 'Azure Sentinel' allowed in offers or packages? 
&emsp;&emsp;&emsp; No. The text 'Azure Sentinel' must not appear anywhere. The correct branding is 'Microsoft Sentinel'. 

+ #### Should package name and package version match? 
&emsp;&emsp;&emsp; Yes. Package name and package version mentioned in Partner Center must be the same. For instance if package version is 3.0.1 then the package name should be 3.0.1.zip.

+ #### Where should the version number match? 
&emsp;&emsp;&emsp; The version number must match across Partner Center, Solution Metadata, and mainTemplate.json. 

+ #### Is ARM-TTK validation required? 
&emsp;&emsp;&emsp; Yes. ARM-TTK must pass successfully. Any failures should result in rejection with details. 

+ #### What image and logo checks are required? 
&emsp;&emsp;&emsp; Ensure images load correctly and logos referenced to master branch, not PR links or private branch links. 

+ #### Should DARSy zip content match GitHub repository content? 
&emsp;&emsp;&emsp; Yes. The package submitted to certification must exactly match GitHub master repository files. To ensure this, the Pull Request must be approved and merged prior to publishing the offer.

+ #### Why should short-links be verified? 
&emsp;&emsp;&emsp; All links, especially short-links, must resolve correctly. Broken links are grounds for rejection. 

+ #### Are release notes mandatory? 
&emsp;&emsp;&emsp; Yes. Release notes must be present and properly added. Missing release notes will cause rejection. 

+ #### Are support information mandatory?
&emsp;&emsp;&emsp; Yes. Support information including name, email, tier and link is mandatory.


## Feedback

[Email Microsoft Sentinel Solutions Onboarding Team](mailto:AzureSentinelPartner@microsoft.com) with any feedback on this process, for new scenarios not covered in this guide, or with any constraints you may encounter. 

## FAQs

### CSP (Cloud Solution Provider)

#### What is CSP?
Microsoft Azure Customers may purchase their Azure Subscriptions either directly from Microsoft, or via an Azure Reseller who is part of the Microsoft Cloud Solution Provider (CSP) program.  Microsoft Sentinel Solutions are valid for both subscription purchase paths.   

#### Why is there a “CSP Opt-in” option on Microsoft Sentinel solution offers?
“CSP Opt-in” is a general feature of the Azure Marketplace and applies to multiple offer types, including the Azure App offer type used by Microsoft Sentinel solutions.  For some publishers, there is occasionally a desire to restrict individual offers to only be deployable in subscriptions that were purchased directly through Microsoft.   This is controllable via the “CSP opt-in” flag for each individual offer.  

#### Is Microsoft Sentinel available to customers who purchased their Azure subscription from a CSP Reseller partner?
Yes.  There are many customers purchasing directly from Microsoft, via a CSP Reseller and even some who purchase Azure via both programs.

#### What happens when you enable “CSP opt-in” for your Microsoft Sentinel solution offer?
Quite simply, it permits your Microsoft Sentinel solution to be deployed into Microsoft Sentinel Workspaces regardless of how the customer acquired it. It is more of a pro-active stance to eliminate an error message for your customers who are trying to deploy your Microsoft Sentinel Solution into a CSP purchase subscription.

#### What does **not** happen when you enable “CSP opt-in” for your Microsoft Sentinel solution offer?
You are **not** joining the CSP program.  Each offer is individually enabled or disabled for deployability in CSP sourced subscriptions, and setting this flag for your Microsoft Sentinel solution does not affect any other offer in your Marketplace publishing account.

#### What will happen if you do not enable “CSP opt-in” for your Microsoft Sentinel solution offer?
If the customer who wants to deploy your solution offer, purchased their subscription from a CSP Reseller partner, the solution will not deploy and the customer will get an error message about why. 
