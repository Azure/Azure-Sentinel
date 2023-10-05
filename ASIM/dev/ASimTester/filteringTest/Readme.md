


  
  

# Filtering testing script

The purpose of the script is to validate the functionality of the parameters filtering in an ASIM parser.

  

## Prerequisites

- Python 3.7 or later.

- Azure Identity client library and Azure Monitor Query client library. These libraries can be installed with the following commands:

	```
	pip install azure-identity
	
	pip install azure-monitor-query
	```

	The script sends queries to your workspace to perform the validations. These libraries are needed in order to authenticate and perform the queries.

## Requirments

- A yaml file of an ASIM parser.

- A workspace with relevant data for the parser you need to test. Without enough data, the testing will be insufficient or impossible.

  

## Running the script

To run the test script, use the following command:

  

python ASimFilteringTest.py <workspace_id> <path_to_parser_file> <days_range_to_query_ws_over>

Arguments explanation:

1. workspace_id - ID of a workspace you have access to and has relevant data for the parser.

2. path_to_parser_file - A full or relative path to the yaml file of the parser.

3. days_range_to_query_ws_over - A number of days to query over the data in the workspace. A longer day range will lead to a longer run time of the script. On the other hand, a longer day range will provide more data which will enhance the quality of the test.

  

For example: To test the parser file `C:\parsers\vimDnsMicrosoftOMSfict.yaml` , on a workspace with id `123-456`, over the last `99` days use the command:

  

python ASimFilteringTest.py C:\parsers\vimDnsMicrosoftOMSfict.yaml 123-456 99

  

## Results

- If all the validations that the test script performed have passed you will receive an "ok" message:

	![enter image description here](https://github.com/Azure/Azure-Sentinel/assets/126081432/e3e130e1-6f73-4479-9e1f-2cdfd8023c45)

  

- If some validations have failed you will receive error messages with a description of the reason for the failures:
![enter image description here](https://github.com/Azure/Azure-Sentinel/assets/126081432/6957eaee-5eed-4abd-b701-06fef372cd59)
![enter image description here](https://github.com/Azure/Azure-Sentinel/assets/126081432/e724599c-a653-43b9-98f4-0cd24935e5fd)



- In order to carry out the tests, data within the workspace is necessary. Some error messages indicate a lack of data in the workspace rather than a problem with the parser:
![enter image description here](https://github.com/Azure/Azure-Sentinel/assets/126081432/4707b8db-743e-4c13-9db2-bd0d91b1abc7)