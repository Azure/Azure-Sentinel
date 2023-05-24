import unittest
import os
import sys
import yaml
import contextlib
from datetime import datetime, timedelta, timezone
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from schemasParameters import all_schemas_parameters


REPO_PATH = f"{os.getcwd()}/../../../../"
DUMMY_VALUE = "\'!not_REAL_vAlUe\'"
DAYS_DELTA = 729


if len(sys.argv) == 3:
    ws_id = sys.argv[1]
    parser_file_relative_path = sys.argv[2]
else:
    print("Please provide the correct number of arguments")
    exit(-1)

end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(days = DAYS_DELTA)
no_test_list = [] # No data was found for testing
partial_test_list = [] # Parameters with only one value in their relevant column


# Authenticating the user
credential = DefaultAzureCredential(exclude_interactive_browser_credential = False)
try:
    with contextlib.redirect_stderr(None):
        client = LogsQueryClient(credential)
        empty_query = ""
        response = client.query_workspace(
                workspace_id = ws_id, 
                query = empty_query,
                timespan = timedelta(days = 1)
                )
        if response.status == LogsQueryStatus.PARTIAL:
            raise Exception()
except Exception as e:
    credential = DefaultAzureCredential(exclude_interactive_browser_credential = False, exclude_shared_token_cache_credential = True)
client = LogsQueryClient(credential)


def get_parser(parser_path):
    parser_full_path = f"{REPO_PATH}{parser_path}"
    if os.path.exists(parser_full_path) or not parser_full_path.endswith('.yaml'):
        try:
            with open(parser_full_path, 'r') as file_stream:
                return yaml.safe_load(file_stream)
        except:
            print(f"Cannot open file: {parser_path}")
    else:
        print(f"yml file does not exist: {parser_path}")


# Creating a string of the parameters of a parser
def create_parameters_string(parser_file):
    if "ParserParams" not in parser_file:
        return ""
    paramsList = []
    for param in parser_file['ParserParams']:
        paramDefault = f"\'{param['Default']}\'" if param['Type']=="string" else param['Default']
        paramsList.append(f"{param['Name']}:{param['Type']}={paramDefault}")
    return ','.join(paramsList)
    

def create_query_without_call(parser_file):
    params_str = create_parameters_string(parser_file) 
    query_from_yaml = parser_file['ParserQuery']
    return f"let query= ({params_str}) {{ {query_from_yaml} }};\n"


class FilteringTest(unittest.TestCase):
    def tests_main_func(self):
        parser_file = get_parser(parser_file_relative_path)
        with self.subTest():
            self.handle_parser(parser_file)

    
    def handle_parser(self, parser_file):
        no_call_query = create_query_without_call(parser_file)
        columns_in_answer = self.get_columns_of_parser_answer(no_call_query)
        param_to_column_mapping = all_schemas_parameters[parser_file['Normalization']['Schema']]
        for param in parser_file['ParserParams']:
            with self.subTest():
                self.handle_param(param, no_call_query, columns_in_answer, param_to_column_mapping)
                      
        
    def handle_param(self, param, no_call_query, columns_in_answer, param_to_column_mapping):
        param_name = param['Name']
        param_type = param['Type']
        if (param_name == "pack"):
            return 
        if (param_name == "disabled"):
            self.disabled_test(param, no_call_query)
        elif  param_to_column_mapping[param_name] not in columns_in_answer:
            return
        elif (param_type == "datetime"):
            pass
        elif (param_type == "dynamic"):
            pass
        else:
            self.scalar_test(param, no_call_query, param_to_column_mapping)

    
    # Test for parameter which are not datetime,dynamic or disabled
    def scalar_test(self, param, no_call_query, param_to_column_mapping):
        param_name = param['Name']
        no_filter_query = no_call_query + f"query() | summarize count() by {param_to_column_mapping[param_name]}\n"
        no_filter_response = self.send_query(no_filter_query)
        if len(no_filter_response.tables[0].rows) == 0:
            no_test_list.append(param_name)
            return
        # Taking the first value returned in the response
        selected_value = no_filter_response.tables[0].rows[0][0]
        value_to_filter = f"\'{selected_value}\'" if param['Type']=="string" else selected_value

        # Performing a query with a non-existing value, expecting to return no results
        no_results_query = no_call_query + f"query({param_name}={DUMMY_VALUE}) | summarize count() by {param_to_column_mapping[param_name]}\n"
        no_results_response = self.send_query(no_results_query)
        self.assertEqual(0, len(no_results_response.tables[0].rows), "Returned results for non existing filter value")

        # Performing a filtering by the first value returned in the first response
        query_with_filter = no_call_query + f"query({param_name}={value_to_filter}) | summarize count() by {param_to_column_mapping[param_name]}\n"
        if selected_value=="":
            query_with_filter = no_call_query + f"query() | where isempty({param_to_column_mapping[param_name]}) | summarize count() by {param_to_column_mapping[param_name]}\n"
        filtered_response = self.send_query(query_with_filter)
        self.assertEqual(1, len(filtered_response.tables[0].rows), "Expected to have results for only one value after filtering")
        if len(no_filter_response.tables[0].rows) == 1:
            partial_test_list.append(param_name)
        

        
    def disabled_test(self, param, no_call_query):
        no_filter_query = no_call_query + f"query() | summarize count()\n"
        no_filter_response = self.send_query(no_filter_query)
        if no_filter_response.tables[0].rows[0][0] == 0:
            no_test_list.append(param['Name'])
            return

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
                print(response.partial_error)
                self.fail("Query failed")
            elif response.status == LogsQueryStatus.SUCCESS:
                return response
        except HttpResponseError as err:
            print (err)
            self.fail("Query failed")


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(FilteringTest)
    runner = unittest.TextTestRunner()
    runner.run(suite)
    if len(no_test_list) != 0:
        print("The following parameters weren't tested because no data was found to test them:")
        print(no_test_list)
    if len(partial_test_list) != 0:
        print("The following parameters passed a partial test:")
        print(partial_test_list)