# Guide to building ASIM parsers for Microsoft Sentinel 

## ASIM Parser development guidelines 
This guide provides an overview of the ASIM parser development that providers can build in Microsoft Sentinel for customers with specific focus on build, validation steps and publishing process. Furthermore, the document covers technical details on opportunities to build new ASIM parsers.
Build your ASIM parser. 
![Microsoft Sentinel solutions build process](https://github.com/Azure/Azure-Sentinel/blob/master/Solutions/Images/ASIM_parser.png)

	
## Identify Data Source – 

As ASIM solutions does not have a connector of its own it is important to see if there is already an [connector / solution] (https://learn.microsoft.com/en-us/azure/sentinel/data-connectors-reference) available for the identified data source. If there is no solution / connector available, we would recommend to follow this [data connector building guideline] (https://github.com/Azure/Azure-Sentinel/blob/master/DataConnectors/ReadMe.md) and building your connector and getting it shipped into the Microsoft sentinel content hub. This guide is to help in building ASIM parsers for vendor products where we have out of box source specific solutions available. We are not intending to support custom connectors that are not available as out of box content.
  
## ASIM Schema mapping – 

An Advanced Security Information Model [(ASIM)] (https://learn.microsoft.com/en-us/azure/sentinel/normalization) schema is a set of fields that represent an activity. Using the fields from a normalized schema in a query ensures that the query will work with every normalized source.
	
To understand how schemas fit within the ASIM architecture, refer to the [ASIM architecture diagram]. (https://learn.microsoft.com/en-us/azure/sentinel/normalization#asim-components)
 
It is important to understand how Asim Schemas are structured before exploring the field mapping. Each schema consists of one or more sections as below:

1.	Event Fields – These are mandatory fields associated with the source product, vendor, and event represented.
2.	Dvc Fields – This contains information about the device from which the event in question was generated.
3.	Entity based fields – There are different entities that a schema might have based on the flow of the event. These can broadly be categorized into the following:
	a.	Actor – The user who has performed the event which is getting reported.
	b.	Application – The app which is either the agent to initiate the event or serves as the target of the same.
	c.	System – The system used by the Actor to initiate the event or target results for.
	d.	Process – Information of the process used by the actor.
	e.	User – The account which was leveraged to define the result (or target).
4.	Inspection Fields – These fields are not applicable to all the schemas. Wherever necessary, this set of fields record Threat information related to the event.
5.	Alias Fields – As the name suggests, these fields are only aliases to the already existing fields, making the reference to the normalized fields, more accessible.
6.	Schema specific fields – The section of fields which are required essentially to shape the schema of a specific domain. It is best to provide maximum information in this    	section  as normalized content would heavily sit upon them.

For each ASIM Schema, the following are the different types of fields that one can expect to map source information.

**Based on importance class**:
1.	Mandatory – It is necessary to have appropriate information mapped to each field in this category. 
	a.	This section contains an important field, *EventType* which has enumerated values in respective schemas. 
2.	Recommended – It is good to have maximum fields populated in this category based on the data available from the source.
3.	Optional – As the name suggests, it is not essential to populate all of the fields in this category but increasing the coverage as much as possible would ensure better results for the normalized content.

**Based on type of values**:

1.	**Static value fields** – The values in this category are static in nature and will remain the same throughout the rows. This can include EventProduct, EventVendor, EventProductVersion, etc.
2.	**Enumerated value fields** – To ensure the data is normalized, most of the filtering fields are designed to have set of expected values. Parser should enable the mapping between the values coming from the source to the expected enumerated type. Best practice is to use lookup function to perform this operation wherever possible.
	a.	Original value fields – Because the values are mapped to enumerated types, it is essential to keep the originals intact. To help with the same, original value fields are present in the schema for direct mapping.
3.	**Mapped fields** – These fields do not require any additional manipulation to the data and can directly be mapped from the source to the normalized fields. It is important to ensure that datatype of the normalized field is considered.
4.	**Derived fields** – Based on the values already populated in the above fields, it is required to fill the derived fields as well. 
	a.	Associated fields – For example, device hostname is closely associated with device domain and device FQDN. If information is present for device hostname, the other two can be derived from it.
	b.	Type fields – Because we are dealing with a variety of sources, it is essential to determine the type of value which is getting populated. For more information, please refer to the [entity list].(https://learn.microsoft.com/en-us/azure/sentinel/normalization-about-schemas#entities)
	
Based on the guidance provided above, before developing the Asim Parser, ensure that field mapping is ready to assist.
Based on the identified data source map it to one or multiple ASIM schemas. It is important to cover the mapping for all the possible ASIM schemas the source logs can fit in

**Build and Validate Parser** – 
first look at the list of [available parsers] (https://learn.microsoft.com/en-us/azure/sentinel/normalization-parsers-list) to make sure there is no parser already available that might match the requirement. Once the schema mapping is done, start [building] (https://review.learn.microsoft.com/en-us/azure/sentinel/normalization-develop-parsers?branch=pr-en-us-229997) the parser by relating the source log fields with the ASIM schema fields. 
Once done with the testing and validation covered under the building document above raise a pull request against the  [Microsoft Sentinel GitHub repository] (https://github.com/Azure/Azure-Sentinel)
	- Add to the PR your parsers YAML files to the ASIM parser folders (**/Parsers/ASim<schema>/Parsers**)
	- Add representative sample data and test results to the sample data folder (/Sample Data/ASIM), please follow the [sample data contribution] (https://github.com/Azure/Azure-Sentinel/tree/master/Sample Data#sample-data-contribution-guidance) guidelines for the same. 
	-After running the test tool please submit the test results into (/Parsers/ASim<schema>/Parsers/Test results)
Parser Ships - Microsoft team will review the parser and if everything is matching the expected standards then we will deploy the parser in Log analytic workspace so that it will be available to all Microsoft customers.



