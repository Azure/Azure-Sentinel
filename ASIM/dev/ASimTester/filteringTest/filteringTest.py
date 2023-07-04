__unittest = True #prevents stacktrace during most assertions

import unittest
import os
import sys
import yaml
import contextlib
import argparse
from datetime import datetime, timedelta, timezone
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from schemasParameters import all_schemas_parameters


DUMMY_VALUE = "\'!not_REAL_vAlUe\'"


argparse_parser = argparse.ArgumentParser()
argparse_parser.add_argument("ws_id", help = "workspace ID")
argparse_parser.add_argument("parser_file_relative_path", help = "relative path to the parser file")
argparse_parser.add_argument("days_delta", default = 1, type = int, help = "number of days to query over ,default is set to  1", nargs='?')
args = argparse_parser.parse_args()
ws_id = args.ws_id
parser_file_path = args.parser_file_relative_path
days_delta = args.days_delta


end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days = days_delta)


def attempt_to_connect(credential):
    try:
        with contextlib.redirect_stderr(None):
            client = LogsQueryClient(credential)
            empty_query = ""
            response = client.query_workspace(
                    workspace_id = ws_id, 
                    query = empty_query,
                    timespan = timedelta(days = 1)
                    )
            if response.status == LogsQueryStatus.PARTIAL or response.status == LogsQueryStatus.FAILURE:
                raise Exception()
            else:
                return client
    except Exception as e:
        return None
    

# Authenticating the user
client = attempt_to_connect(DefaultAzureCredential(exclude_interactive_browser_credential = False))
if client is None:
    client = attempt_to_connect(DefaultAzureCredential(exclude_interactive_browser_credential = False, exclude_shared_token_cache_credential = True))
    if client is None:
        print("Couldn't connect to workspace")
        sys.exit()


def get_parser(parser_path):
    try:
        with open(parser_path, 'r') as file_stream:
            return yaml.safe_load(file_stream)
    except:
        raise Exception()


# Creating a string of the parameters of a parser. 
# Example: for a parser with two parameters: (Name: eventtype, Type: string, Default: 'Query'), (Name: disabled, Type: bool, Default: false)
# The output will be: eventtype:string='Query',disabled:bool=False
def create_parameters_string(parser_file):
    paramsList = []
    for param in parser_file['ParserParams']:
        paramDefault = f"\'{param['Default']}\'" if param['Type']=="string" else param['Default']
        paramsList.append(f"{param['Name']}:{param['Type']}={paramDefault}")
    return ','.join(paramsList)


# Taking the query string from a parser file and returning a string with a definition of a KQL function
def create_query_definition_string(parser_file):
    params_str = create_parameters_string(parser_file) 
    query_from_yaml = parser_file['ParserQuery']
    return f"let query= ({params_str}) {{ {query_from_yaml} }};\n"


# Returning a string representing a call for a KQL function without parameters
def create_execution_string_without_parameters(column_name):
    return f"query() | summarize count() by {column_name}\n" 


# Returning a string representing a call for a KQL function with one parameter
def create_execution_strings_with_one_parameter(parameter, value, column_name):
    return f"query({parameter}={value}) | summarize count() by {column_name}\n"


class FilteringTest(unittest.TestCase):
    # "Main" function which opens the parser file, checks if it has all the required fields, checks if there is data in the provided workspace and then initiates the tests for each parameter in the parser.
    def tests_main_func(self):
        if not os.path.exists(parser_file_path):
            self.fail(f"File path does not exist: {parser_file_path}")
        if not parser_file_path.endswith('.yaml'): 
            self.fail(f"Not a yaml file: {parser_file_path}")
        try:
            parser_file = get_parser(parser_file_path)
        except:
            self.fail(f"Cannot open file: {parser_file_path}")
        self.check_required_fields(parser_file)
        query_definition = create_query_definition_string(parser_file)
        self.check_data_in_workspace(query_definition)
        columns_in_answer = self.get_columns_of_parser_answer(query_definition)
        schema_of_parser = parser_file['Normalization']['Schema']
        if schema_of_parser not in all_schemas_parameters:
            self.fail(f"Schema: {schema_of_parser} - Not an existing schema or not supported by the validations script")
        param_to_column_mapping = all_schemas_parameters[schema_of_parser]
        for param in parser_file['ParserParams']:
            param_name = param['Name']
            with self.subTest():
                if param_name not in param_to_column_mapping:
                    self.fail(f"parameter: {param_name} - No such parameter in {schema_of_parser} schema")
                column_name_in_table = param_to_column_mapping[param_name]
                self.send_param_to_test(param, query_definition, columns_in_answer, column_name_in_table)            


    def send_param_to_test(self, param, query_definition, columns_in_answer, column_name_in_table):
        """
        Sending parameters to the suitable test according to the parameter type  

        Parameters
        ----------
        param : A parameter field from the parser yaml file
        query_definition : A string with a definition of the parser's query
        columns_in_answer : Set of column names that will be in the response from the query call
        column_name_in_table : The name of the column in the query response on which the parameter performs filtering
        """
        param_name = param['Name']
        param_type = param['Type']
        # pack parameter is not checked by the validations
        if (param_name == "pack"):
            return 
        if (param_name == "disabled"):
            self.disabled_test(query_definition)
        elif  column_name_in_table not in columns_in_answer:
            return
        elif (param_type == "datetime"):
            pass #TODO add test for datetime
        elif (param_type == "dynamic"):
            pass #TODO add tests for dynamic
        else:
            self.scalar_test(param, query_definition, column_name_in_table)

    
    # Checking if the provided workspace has some data
    def check_data_in_workspace(self, query_definition):
        check_data_response = self.send_query(query_definition + "query() | take 5")
        if len(check_data_response.tables[0].rows) == 0:
            self.fail("No data in the provided workspace")
          

    # Checking if all fields from "required_fields" array are in the yaml file.
    def check_required_fields(self, parser_file):
        required_fields = ["ParserParams", "ParserQuery", "Normalization.Schema" ]
        missing_fields = []
        for full_field in required_fields:
            file = parser_file
            fields = full_field.split('.')
            for field_name in fields:
                if field_name not in file:
                    missing_fields.append(full_field)
                    break
                file = file[field_name]
        if len(missing_fields) != 0:
            self.fail(f"The following fields are missing in the file:\n{missing_fields}")
    

    def scalar_test(self, param, query_definition, column_name_in_table):
        """
        Test for parameter which are not datetime,dynamic or disabled  

        Parameters
        ----------
        param : A parameter field from the parser yaml file
        query_definition : A definition of the parser's query
        column_name_in_table : The name of the column in the query response on which the parameter performs filtering
        """
        param_name = param['Name']
        no_filter_query = query_definition + create_execution_string_without_parameters(column_name_in_table)
        no_filter_response = self.send_query(no_filter_query)
        self.assertNotEqual(len(no_filter_response.tables[0].rows) , 0 , f"No data for parameter:{param_name}")
        with  self.subTest():
            self.assertNotEqual(len(no_filter_response.tables[0].rows), 1, f"Only one value exists for parameter: {param_name} - validations for this parameter are partial" )
        # Taking the first value returned in the response
        selected_value = no_filter_response.tables[0].rows[0][0]
        value_to_filter = f"\'{selected_value}\'" if param['Type']=="string" else selected_value
        query_with_filter = query_definition + create_execution_strings_with_one_parameter(param_name, value_to_filter, column_name_in_table)
        if selected_value=="":
            query_with_filter = query_definition + f"query() | where isempty({column_name_in_table}) | summarize count() by {column_name_in_table}\n"
        
        # Performing a filtering by the first value returned in the first response
        self.scalar_test_check_filtering(param_name, query_with_filter, value_to_filter)

        # Performing a query with a non-existing value, expecting to return no results
        self.scalar_test_check_fictive_value(param_name, query_definition, column_name_in_table )


    def scalar_test_check_filtering(self, param_name, query_with_filter, value_to_filter ):
        filtered_response = self.send_query(query_with_filter)
        with self.subTest():
            self.assertNotEqual(0, len(filtered_response.tables[0].rows), f"Parameter: {param_name} - Got no results at all after filtering, while results where expected. Filtered by value: {value_to_filter}")
        with self.subTest():
            self.assertEqual(1, len(filtered_response.tables[0].rows), f"Parameter: {param_name} - Expected to have results for only one value after filtering. Filtered by value: {value_to_filter}")
        

    def scalar_test_check_fictive_value(self, param_name, query_definition, column_name_in_table):
        no_results_query = query_definition + create_execution_strings_with_one_parameter(param_name, DUMMY_VALUE, column_name_in_table)
        no_results_response = self.send_query(no_results_query)
        with self.subTest():
            self.assertEqual(0, len(no_results_response.tables[0].rows), f"Parameter: {param_name} - Returned results for non existing filter value. Filtered by value: {DUMMY_VALUE}")

        
    def disabled_test(self, query_definition):
        """
        Test for "disabled" parameter. The two checked values for this parameter are True and False.

        Parameters
        ----------
        query_definition : A string with a definition of the parser's query
        """
        disabled_true_query = query_definition + f"query(disabled=true) | summarize count()\n"
        disabled_true_response = self.send_query(disabled_true_query)
        self.assertEqual(0, disabled_true_response.tables[0].rows[0][0], "Expected to return 0 results for disabled=true")

        disabled_false_query = query_definition + f"query(disabled=false) | summarize count()\n"
        disabled_false_response = self.send_query(disabled_false_query)
        self.assertNotEqual(0, disabled_false_response.tables[0].rows[0][0], "Expected to return results for disabled=false")


    # Return a set of the columns that will appear in a response of a query call
    def get_columns_of_parser_answer(self, query_definition):
        response = self.send_query(query_definition + f"query() | getschema\n")
        columns_set = set()
        for row in response.tables[0].rows:
            columns_set.add(row['ColumnName'])
        return columns_set


    def send_query(self, query_str):
        """
        Sending a query to the workspace with the id provided by the user.
        If the query call was successful' the method returns the response to the query.

        Parameters
        ----------
        query_str : A string with the KQL query that will be sent to the workspace.
        """
        try:
            response = client.query_workspace(
                workspace_id = ws_id,
                query = query_str,
                timespan = (start_time, end_time)
                )
            if response.status == LogsQueryStatus.PARTIAL:
                self.fail("Query failed")
            elif response.status == LogsQueryStatus.FAILURE:
                self.fail(f"The following query failed:\n{query_str}")
            elif response.tables == None or len(response.tables) == 0:
                self.fail("No data tables were returned in the response for the query")
            else:
                return response
        except HttpResponseError as err:
            self.fail("Query failed")


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(FilteringTest)
    runner = unittest.TextTestRunner()
    runner.run(suite)