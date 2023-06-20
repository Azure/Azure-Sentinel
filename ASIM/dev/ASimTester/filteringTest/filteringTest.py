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
required_fields = ["ParserParams", "ParserQuery", "Normalization.Schema" ]


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


# Creating a string of the parameters of a parser
def create_parameters_string(parser_file):
    paramsList = []
    for param in parser_file['ParserParams']:
        paramDefault = f"\'{param['Default']}\'" if param['Type']=="string" else param['Default']
        paramsList.append(f"{param['Name']}:{param['Type']}={paramDefault}")
    return ','.join(paramsList)
    

def create_query_without_call(parser_file):
    params_str = create_parameters_string(parser_file) 
    query_from_yaml = parser_file['ParserQuery']
    return f"let query= ({params_str}) {{ {query_from_yaml} }};\n"


def create_call_without_parameter(column_name):
    return f"query() | summarize count() by {column_name}\n" 


def create_call_with_parameter(parameter, value, column_name):
    return f"query({parameter}={value}) | summarize count() by {column_name}\n"


class FilteringTest(unittest.TestCase):
    # "Main" function which runs initiates the validations 
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
        no_call_query = create_query_without_call(parser_file)
        self.check_data_in_workspace(no_call_query)
        columns_in_answer = self.get_columns_of_parser_answer(no_call_query)
        if parser_file['Normalization']['Schema'] not in all_schemas_parameters:
            self.fail(f"Schema: {parser_file['Normalization']['Schema']} - is not supported")
        param_to_column_mapping = all_schemas_parameters[parser_file['Normalization']['Schema']]
        for param in parser_file['ParserParams']:
            with self.subTest():
                if param['Name'] not in param_to_column_mapping:
                    self.fail(f"parameter: {param['Name']} - is not a valid parameter")
                column_name_in_table = param_to_column_mapping[param['Name']]
                self.handle_param(param, no_call_query, columns_in_answer, column_name_in_table)            
                      
    # Sending a parameters to the suitable test according to the parameter type    
    def handle_param(self, param, no_call_query, columns_in_answer, column_name_in_table):
        param_name = param['Name']
        param_type = param['Type']
        if (param_name == "pack"):
            return 
        if (param_name == "disabled"):
            self.disabled_test(param, no_call_query)
        elif  column_name_in_table not in columns_in_answer:
            return
        elif (param_type == "datetime"):
            pass
        elif (param_type == "dynamic"):
            pass
        else:
            self.scalar_test(param, no_call_query, column_name_in_table)

    
    # Checking if the provided workspace has some data
    def check_data_in_workspace(self, no_call_query):
        check_data_response = self.send_query(no_call_query + "query() | take 5")
        if len(check_data_response.tables[0].rows) == 0:
            self.fail("No data in the provided workspace")
          

    # Checking if all fields from "required_fields" array are in the yaml file.
    def check_required_fields(self, parser_file):
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
    

    # Test for parameter which are not datetime,dynamic or disabled
    def scalar_test(self, param, no_call_query, column_name_in_table):
        param_name = param['Name']
        no_filter_query = no_call_query + create_call_without_parameter(column_name_in_table)
        no_filter_response = self.send_query(no_filter_query)
        self.assertNotEqual(len(no_filter_response.tables[0].rows) , 0 , f"No data for parameter:{param_name}")
        with  self.subTest():
            self.assertNotEqual(len(no_filter_response.tables[0].rows), 1, f"Only one value exists for parameter: {param_name} - validations for this parameter are partial" )
        # Taking the first value returned in the response
        selected_value = no_filter_response.tables[0].rows[0][0]
        value_to_filter = f"\'{selected_value}\'" if param['Type']=="string" else selected_value

        # Performing a filtering by the first value returned in the first response
        query_with_filter = no_call_query + create_call_with_parameter(param_name, value_to_filter, column_name_in_table)
        if selected_value=="":
            query_with_filter = no_call_query + f"query() | where isempty({column_name_in_table}) | summarize count() by {column_name_in_table}\n"
        filtered_response = self.send_query(query_with_filter)
        with self.subTest():
            self.assertNotEqual(0, len(filtered_response.tables[0].rows), f"Parameter: {param_name} - Got no results at all after filtering. Filtered by value: {value_to_filter}")
        with self.subTest():
            self.assertEqual(1, len(filtered_response.tables[0].rows), f"Parameter: {param_name} - Expected to have results for only one value after filtering. Filtered by value: {value_to_filter}")

        # Performing a query with a non-existing value, expecting to return no results
        no_results_query = no_call_query + create_call_with_parameter(param_name, DUMMY_VALUE, column_name_in_table)
        no_results_response = self.send_query(no_results_query)
        with self.subTest():
            self.assertEqual(0, len(no_results_response.tables[0].rows), f"Parameter: {param_name} - Returned results for non existing filter value. Filtered by value: {DUMMY_VALUE}")
        

        
    def disabled_test(self, param, no_call_query):
        disabled_true_query = no_call_query + f"query(disabled=true) | summarize count()\n"
        disabled_true_response = self.send_query(disabled_true_query)
        self.assertEqual(0, disabled_true_response.tables[0].rows[0][0], "Expected to return 0 results for disabled=true")

        disabled_false_query = no_call_query + f"query(disabled=false) | summarize count()\n"
        disabled_false_response = self.send_query(disabled_false_query)
        self.assertNotEqual(0, disabled_false_response.tables[0].rows[0][0], "Expected to return results for disabled=false")


    # Return a set of the columns that will appear in a response of a query call
    def get_columns_of_parser_answer(self, no_call_query):
        response = self.send_query(no_call_query + f"query() | getschema\n")
        columns_set = set()
        for row in response.tables[0].rows:
            columns_set.add(row['ColumnName'])
        return columns_set


    def send_query(self, query_str):
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
            else:
                return response
        except HttpResponseError as err:
            self.fail("Query failed")


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(FilteringTest)
    runner = unittest.TextTestRunner()
    runner.run(suite)