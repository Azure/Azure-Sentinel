# Guide to build ASIM parsers for Microsoft Sentinel 

## ASIM Parser development guidelines 
This guide provides an overview of the [Advance Security Information Model (ASIM)](https://learn.microsoft.com/azure/sentinel/normalization) parser development that contributors can follow to build and deliver parsers based on the ASIM normalization schema in Microsoft Sentinel. This guide provides specific focus on build, validation steps and submission process. Delivering ASIM parsers enables providers to completely unlock the value of their integration in Microsoft Sentinel and leverage the ASIM-based OOTB (out-of-the-box) content to extend coverage for their integration automatically.
Learn more about [ASIM-based OOTB content and solutions](https://learn.microsoft.com/azure/sentinel/domain-based-essential-solutions)

## Build your ASIM parser

![Microsoft Sentinel solutions build process](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Images/ASIM_Parser_Steps.png)

	
## Identify Data Source 

As ASIM solutions does not have a connector of its own it is important to see if there is already an [connector / solution](https://learn.microsoft.com/azure/sentinel/data-connectors-reference) available in Microsoft Sentinel for the identified data source. Check the [Microsoft Sentinel Content hub catalog](https://learn.microsoft.com/azure/sentinel/sentinel-solutions-catalog) to determine if an OOTB connector already exists, If there is no OOTB solution / connector available, [follow the-data connector build guideline](https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/ReadMe.md) to build the OOTB data connector and get the [solution shipped](https://github.com/Azure/Azure-Sentinel/tree/master/Solutions#guide-to-building-microsoft-sentinel-solutions) to appear in the Microsoft sentinel content hub. This guide is to help build ASIM parsers for different vendor products where we have OOTB source specific solutions available or land a new solution as part of integration.
  
* Step 1 - Check if OOTB data connector exists in a solution in content hub.
* Step 2.a - If OOTB data connector exists, build ASIM parser(s) for that source(s)
* Step 2.b - If OOTB data connector does not exist, build data connector (solution) first before building ASIM parser(s) for that source(s)

## ASIM Schema mapping 

An [ASIM](https://learn.microsoft.com/azure/sentinel/normalization) schema provides a set of structured property sets that enables normalization of commonly used properties in Microsoft Sentinel. Learn more about [ASIM Normalized Schema](https://learn.microsoft.com/azure/sentinel/normalization#normalized-schemas) in Microsoft Sentinel. Using the fields from a normalized schema in a query ensures that the query will work with every normalized source.
	
To understand how schemas fit within the ASIM architecture, refer to the [ASIM architecture diagram](https://learn.microsoft.com/azure/sentinel/normalization#asim-components)
 
It is important to understand how Asim Schemas are structured before exploring the field mapping. Each schema consists of one or more sections as below:

1.	**Event Fields** - These are mandatory fields associated with the source product, vendor, and event represented.
2.	**Dvc Fields** - This contains information about the device from which the event in question was generated.
3.	**Entity based fields** - A schema might have different entities based on the flow of event. These can broadly be categorized into the following:
	* 	Actor - The user who has performed the event which is getting reported.
	* 	Application - The app which is either the agent to initiate the event or serves as the target of the same.
	* 	System - The system used by the Actor to initiate the event or target results for.
	* 	Process - Information of the process used by the actor.
	* 	User - The account which was leveraged to define the result (or target).
4.	**Inspection Fields** - These fields are not applicable to all the schemas. Wherever necessary, this set of fields record Threat information related to the event.
5.	**Alias Fields** - As the name suggests, these fields are only aliases to the already existing fields, making the reference to the normalized fields, more accessible.
6.	**Schema specific fields** - The section of fields which are required essentially to shape the schema of a specific domain. It is best to provide maximum information in this section  as normalized content would heavily sit upon them.

For each ASIM Schema, the following are the different types of fields that one can expect to map source information.

**Based on importance class**:
1.	**Mandatory** - It is necessary to have appropriate information mapped to each field in this category. 
	* This section contains an important field, *EventType* which has enumerated values in respective schemas. 
2.	**Recommended** - It is good to have maximum fields populated in this category based on the data available from the source.
3.	**Optional** - As the name suggests, it is not essential to populate all of the fields in this category but increasing the coverage as much as possible would ensure better results for the normalized content.

**Based on type of values**:

1.	**Static value fields** - The values in this category are static in nature and will remain the same throughout the rows. This can include *EventProduct, EventVendor, EventProductVersion,* etc.
2.	**Enumerated value fields** - To ensure the data is normalized, most of the filtering fields are designed to have set of expected values. Parser should enable the mapping between the values coming from the source to the expected enumerated type. Best practice is to use lookup function to perform this operation wherever possible.
	* Original value fields - Because the values are mapped to enumerated types, it is essential to keep the originals intact. To help with the same, original value fields are present in the schema for direct mapping.
3.	**Mapped fields** - These fields do not require any additional manipulation to the data and can directly be mapped from the source to the normalized fields. It is important to ensure that datatype of the normalized field is considered.
4.	**Derived fields** - Based on the values already populated in the above fields, it is required to fill the derived fields as well. 
	* Associated fields - For example, device hostname is closely associated with device domain and device FQDN. If information is present for device hostname, the other two can be derived from it.
	* Type fields - Because we are dealing with a variety of sources, it is essential to determine the type of value which is getting populated. For more information, please refer to the [entity list](https://learn.microsoft.com/azure/sentinel/normalization-about-schemas#entities)
	
Based on the guidance provided above, before developing the Asim Parser, ensure that field mapping is ready to assist.
Based on the identified data source map it to one or multiple ASIM schemas. It is important to cover the mapping for all the possible ASIM [schemas](https://learn.microsoft.com/azure/sentinel/normalization-about-schemas) the source logs can fit in

## Build and Validate Parser  
First look at the list of [available parsers](https://learn.microsoft.com/azure/sentinel/normalization-parsers-list) to make sure there is no parser already available that might match the requirement. 
Once the schema mapping is done, start **building** the parser by relating the source log fields with the ASIM schema fields. [Follow the guidance](https://learn.microsoft.com/azure/sentinel/normalization-develop-parsers#custom-asim-parser-development-process) to build the parser.

Once done with the testing and validation covered under the above build document 'Read the [contributing guidelines](https://github.com/Azure/Azure-Sentinel#contributing) to clone the Microsoft Sentinel GitHub repository and raise a PR to submit the parser.
- Add to the PR your parsers YAML files to the ASIM parser folders (*/Parsers/ASim\<schema>\/Parsers*)
- Add representative sample data and test results to the sample data folder (*/Sample Data/ASIM*), please follow the [sample data contribution](https://github.com/Azure/Azure-Sentinel/tree/master/Sample%20Data#sample-data-contribution-guidance) and [test result submission](https://learn.microsoft.com/azure/sentinel/normalization-develop-parsers#test-results-submission-guidelines) guidelines for the same.

## Parser Ships 
Microsoft team will review the parser and if everything is matching the expected standards then we will deploy the parser in Log analytic workspace so that it will be available to all Microsoft customers.


