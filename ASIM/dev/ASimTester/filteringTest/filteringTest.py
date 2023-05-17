import unittest
import os
import sys
import yaml
import contextlib
import pandas as pd
from datetime import datetime, timedelta
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from schemasParameters import Dns_params


class Schema:
    def __init__(self, name, directory):
        self.name = name
        self.directory = directory


KQL_FILES_FOLDER = "/Parsers"
REPO_PATH = "C:/One/ASI/Azure-Sentinel/Parsers/" #TODO - change when decided on final location

schemas = [Schema("Dns", "ASimDns")]
ws_id = sys.argv[1]

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


# Returning all parser files of a specific schema
def get_parsers(schema):
    files_path = f"{REPO_PATH}{schema.directory}{KQL_FILES_FOLDER}"
    parser_files = []
    for file_name in os.listdir(files_path):
        if not file_name.endswith('.yaml'):
            continue
        with open(f"{files_path}/{file_name}") as file_stream:
            parser_files.append(yaml.safe_load(file_stream))
    return parser_files


# Creating a string of the parameters of a parser
def create_parameters_string(parser_file):
    if "ParserParams" not in parser_file: # TODO check for FunctionParams for functions 
        return ""
    paramsList = []
    for param in parser_file['ParserParams']:
        paramDefault = f"\'{param['Default']}\'" if param['Type']=="string" else param['Default']
        paramsList.append(f"{param['Name']}:{param['Type']}={paramDefault}")
    return ','.join(paramsList)
    

def create_query_without_call(parser_file):
    params_str = create_parameters_string(parser_file) 
    query_from_yaml = "" 
    if "FunctionQuery" in parser_file:
        query_from_yaml = parser_file['FunctionQuery']
    elif "ParserQuery" in parser_file:
        query_from_yaml = parser_file['ParserQuery']
    return f"let query= ({params_str}) {{ {query_from_yaml} }};\n"
    

def send_query(query_str):
    try:
        response = client.query_workspace(
            workspace_id = ws_id,
            query = query_str,
            timespan=timedelta(days = 730)
            )
        if response.status == LogsQueryStatus.PARTIAL:
            error = response.partial_error
            data = response.partial_data
            #print(error)
        elif response.status == LogsQueryStatus.SUCCESS:
            data = response.tables
        for table in data:
            df = pd.DataFrame(data=table.rows, columns=table.columns)
            print(df)
    except HttpResponseError as err:
        #print("something fatal happened")
        #print (err)
        pass


class FilteringTest(unittest.TestCase):
    def tests_main_func(self):
        for schema in schemas:
            parser_files = get_parsers(schema)
            for parser in parser_files:
                with self.subTest(parser = parser):
                    self.handle_parser(parser)

    
    def handle_parser(self, parser_file):
        no_call_query = create_query_without_call(parser_file)
        for param in parser_file['ParserParams']:
            with self.subTest(param = param):
                self.handle_param(param, no_call_query)
                      #paramDefault = f"\'{param['Default']}\'" if param['Type']=="string" else param['Default']
                      
        
    def handle_param(self, param, no_call_query):
        param_name = param['Name']
        if (param_name == "pack"):
            return
        no_filter_result = no_call_query + f"query() | summarize count() by {Dns_params[param_name]}"    
        #TODO SEND QUERY


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(FilteringTest)
    runner = unittest.TextTestRunner()
    runner.run(suite)