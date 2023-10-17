__unittest = True #prevents stacktrace during most assertions

import unittest
import os
import sys
import yaml
import contextlib
import argparse
import re
from datetime import datetime, timedelta, timezone
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError


DUMMY_VALUE = "\'!not_REAL_vAlUe\'"
MAX_FILTERING_PARAMETERS = 2

# Negative value as it is cannot be a port number and less likely to be an ID of some event. Also, the absolute value is greater than the maximal possible port number.
INT_DUMMY_VALUE = -967799
# The index of the column with the value from a query response.
COLUMN_INDEX_IN_ROW = 0

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


# Creating a string of the values in the list with commas between them
# Example: for a list: ['ab', 'cd', 'ef'] the output will be: "'ab','cd','ef'"
def create_values_string(values_list):
    joined_string = ','.join([f"'{val}'" for val in values_list])
    return joined_string
    

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


def get_substring_or_default(default, substring, rows, current_list):
    '''
    Returning the substring of a string if this substring is not in the list ("current_list") and if this substring is not contained in all of the values in rows.
    If the substring is not in the list and not contained in all of the values in rows, the substring is returned.
    If the substring is in the list or contained in all of the values in rows, the default value is returned.
    '''
    if substring in current_list:
        return default
    # This prefix is the only possible prefix and thus, it is returned
    if len(rows) == 1:
        return substring
    # Checking if there is at least one value in rows that the substring is not contained in.
    for row in rows:
        value = row[COLUMN_INDEX_IN_ROW]
        if substring not in value:
            return substring
    return default


def get_prefix(str, rows, current_list, delimiter):
    '''
    Returns the prefix of a string until its last occurrence of the delimiter, under certain conditions:
    - The prefix is not present in the 'current_list'.
    - The prefix is not contained in all of the values in rows.
    If the string does not contain the delimiter or fails to meet the conditions above, the original string is returned.
    Example:
        delimiter = '.'
        str = "example.com.subdomain"
        output = "example.com"
    '''
    last_delimiter_index = str.rfind(delimiter)
    # If there is no delimiter in the string, return the string
    if last_delimiter_index == -1:
        return str
    
    substring = str[:last_delimiter_index]
    return get_substring_or_default(str, substring, rows, current_list)


def get_postfix(str, rows, current_list, delimiter):
    '''
    Returns the postfix of a string following the first occurrence of the delimiter, under certain conditions:
    - The postfix is not present in the 'current_list'.
    - The postfix is not contained in all of the values in rows.
    If the string does not contain the delimiter or fails to meet the conditions above, the original string is returned.
    Example:
        delimiter = '.'
        str = "example.com.subdomain"
        output = "com.subdomain"
    '''
    first_delimiter_index = str.find(delimiter)
    # If there is no delimiter in the string, return the string
    if first_delimiter_index == -1:
        return str
    
    substring = str[first_delimiter_index + 1:]
    return get_substring_or_default(str, substring, rows, current_list)


def get_frequent_non_word_character_from_rows(rows):
    '''
    Returns the most frequent non-word character from the first 5 values in rows.
    Example:
        rows = ["123.456.4.1/4" , "44-55.5.1293", "11/33.99.13.12"]
        output = '.' (as '.' appearers in the values of rows more than '/' and '-')
    '''
    character_count = {}
    number_of_rows_to_check = 5
    # Counting each occurrence of a non-word character
    for index, row in enumerate(rows):
        if index == number_of_rows_to_check:
            break
        value = row[COLUMN_INDEX_IN_ROW]
        # Getting a list of all non-word characters in value using regex
        non_words_characters_list = re.findall(r'\W', value)
        # Incrementing the count for each non-word character by one
        for character in non_words_characters_list:
            character_count[character] = character_count.get(character, 0) + 1

    # Return the character with maximal count. If no non-word character was found return space by default.
    return max(character_count, key=character_count.get) if len(character_count) > 0 else ' '


def get_splitted_parts_of_string(values_list):
    '''
    The function finds the first string in values_list list which can be split by a non-word character into two substrings.
    The function returns those two substrings or a tuple of None if no string in values_list can be split by a non-word character.
    Example:
        values_list = ["1235ab6" , "44-55.5.1293", "11/33.99.13.12"]
        output = ("44-", "55.5.1293")
    '''
    for value in values_list:
        for i, char in enumerate(value):
            # Splitting the value if the i-th character is non-word and return the substrings
            if not char.isalnum():
                return (value[:i+1], value[i+1:])
    return (None, None)


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
            self.dynamic_test(param, query_definition, column_name_in_table)
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
        self.scalar_test_check_fictive_value(param_name, query_definition, column_name_in_table, param['Type'])


    def scalar_test_check_filtering(self, param_name, query_with_filter, value_to_filter ):
        filtered_response = self.send_query(query_with_filter)
        with self.subTest():
            self.assertNotEqual(0, len(filtered_response.tables[0].rows), f"Parameter: {param_name} - Got no results at all after filtering, while results where expected. Filtered by value: {value_to_filter}")
        with self.subTest():
            self.assertEqual(1, len(filtered_response.tables[0].rows), f"Parameter: {param_name} - Expected to have results for only one value after filtering. Filtered by value: {value_to_filter}")
        

    def scalar_test_check_fictive_value(self, parameter_name, query_definition, column_name_in_table, parameter_type):
        fictive_value = INT_DUMMY_VALUE if parameter_type == "int" else DUMMY_VALUE
        no_results_query = query_definition + create_execution_strings_with_one_parameter(parameter_name, fictive_value, column_name_in_table)
        no_results_response = self.send_query(no_results_query)
        with self.subTest():
            self.assertEqual(0, len(no_results_response.tables[0].rows), f"Parameter: {parameter_name} - Returned results for non existing filter value. Filtered by value: {fictive_value}")

        
    # Return an array of at most two values from rows. Each string in the returned array is not a substring of all values in rows.
    def get_values_for_dynamic_tests(self, rows):
        # If rows has only one row, return the value in that row if it is not an empty string
        if len(rows) == 1:
            return [] if rows[0][0] == "" else [rows[0][0]]
        values = []
        # Searching values in rows which are not contained in at least one other value
        for row in rows:
            # if we already found two values that satisfy the conditions we can return them 
            if len(values) == MAX_FILTERING_PARAMETERS:
                break

            value = row[COLUMN_INDEX_IN_ROW]
            # if the value in an empty string we want to skip it
            if value == "":
                continue
                
            for row_to_compare_with in rows:
                value_to_compare_with = row_to_compare_with[0]
                if value not in value_to_compare_with:
                    values.append(value)
                    # if we found one value that satisfy the condition, we can continue to the next one
                    break
        return values
    

    def get_response_for_query_with_parameters(self, parameter_name, query_definition, column_name_in_table, values_list):
        '''
        The function Send a query with parameters. It return the response for the query and the string of the parameters used for filtering in the query.

        Parameters
        ----------
        parameter_name : Name of a parser's parameter
        query_definition : A definition of the parser's query
        column_name_in_table : The name of the column in the query response on which the parameter performs filtering
        values_list : List of values that will be used to perform filtering.
        '''
        filter_parameters = create_values_string(values_list)
        query_with_filter = query_definition + create_execution_strings_with_one_parameter(parameter_name,f"dynamic([{filter_parameters}])" ,column_name_in_table)

        query_response = self.send_query(query_with_filter)
        return (query_response, filter_parameters)
    

    # The function Send a query with one parameter. Refer to get_response_for_query_with_parameters for more details.
    def get_response_for_query_with_one_parameter(self, parameter_name, query_definition, column_name_in_table, values_list):
        filtering_with_one_value_list = [values_list[0]]
        return self.get_response_for_query_with_parameters(parameter_name, query_definition, column_name_in_table, filtering_with_one_value_list)


    def dynamic_tests_assertions(self, parameter_name, num_of_rows_with_filter_in_query, filter_parameters, num_of_rows_when_no_filters_in_query):
        """
        Performing assertions for dynamic tests with parameter filtering.
        
        Parameters
        ----------
        parameter_name : Name of a parser's parameter
        num_of_rows_with_filter_in_query : The number of rows in a response of parser's query with filtering.
        filter_parameters : A string of the values passed to the parameter separated by commas between them
        num_of_rows_when_no_filters_in_query : The number of rows in a response of parser's query without performing any filtering.
        """
        with self.subTest():
            self.assertNotEqual(0, num_of_rows_with_filter_in_query, f"Parameter: {parameter_name} - Got no results at all after filtering. Filtered by value: {filter_parameters}")  
        with self.subTest():
            if (num_of_rows_when_no_filters_in_query == 1):
                self.assertEqual(1, num_of_rows_when_no_filters_in_query,  f"Parameter: {parameter_name} - Expected to have one result after filtering. Filtered by value: {filter_parameters}")
            else:
                self.assertLess(num_of_rows_with_filter_in_query, num_of_rows_when_no_filters_in_query,  f"Parameter: {parameter_name} - Expected to have less results after filtering. Filtered by value: {filter_parameters}")


    # Failing the test with corresponding message if values list is empty
    def fail_if_values_list_is_empty(self, values_list,parameter_name, test_type):
        if len(values_list) == 0:
            self.fail(f"Parameter: {parameter_name} - Unable to find values to perform {test_type} tests")


    def dynamic_tests_helper(self, parameter_name, query_definition, num_of_rows_when_no_filters_in_query, column_name_in_table, values_list, test_type):
        """
        Performing filtering with one and two values (if possible) for dynamic parameters.

        Parameters
        ----------
        parameter_name : Name of a parser's parameter
        query_definition : A definition of the parser's query
        num_of_rows_when_no_filters_in_query : The number of rows in a response of parser's query without performing any filtering. With filtering, we expect to have less rows.
        column_name_in_table : The name of the column in the query response on which the parameter performs filtering
        values_list : List of at most two values that will be used to perform filtering.
        test_type : Name of the specific tests performed. It can be default testing or specific testing for  has_any/has_any_prefix parameters
        """
        self.fail_if_values_list_is_empty(values_list, parameter_name, test_type)

        # Performing filtering with one value
        filtering_with_one_value_response, one_value_string = self.get_response_for_query_with_one_parameter(parameter_name, query_definition, column_name_in_table, values_list)
        num_of_rows_with_one_parameter_in_query = len(filtering_with_one_value_response.tables[0].rows)
        self.dynamic_tests_assertions(parameter_name, num_of_rows_with_one_parameter_in_query, one_value_string, num_of_rows_when_no_filters_in_query)

        # Performing filtering with two values if possible
        if len(values_list) == 1 or num_of_rows_when_no_filters_in_query <= MAX_FILTERING_PARAMETERS:
            self.fail(f"Parameter: {parameter_name} - Not enough data to perform two values {test_type} tests")
        filtering_response, values_string = self.get_response_for_query_with_parameters(parameter_name, query_definition, column_name_in_table, values_list)
        num_of_rows_with_parameters_in_query = len(filtering_response.tables[0].rows)
        self.dynamic_tests_assertions(parameter_name, num_of_rows_with_parameters_in_query, values_string, num_of_rows_when_no_filters_in_query)

        # Performing a query with a non-existing value, expecting to return no results
        self.dynamic_tests_check_fictive_value(parameter_name, query_definition, column_name_in_table)
    

    # Performing filtering for dynamic parameters with values which taken from no_filter_rows. Refer to has_any_test function for parameters description.
    # These tests can be suitable for many dynamic parameters such as parameters that end with "has_any" or "has_any_prefix" but are not mandatory. 
    def dynamic_common_tests(self, parameter_name, query_definition, no_filter_rows, column_name_in_table):
        selected_values = self.get_values_for_dynamic_tests(no_filter_rows)
        with self.subTest():
            self.dynamic_tests_helper(parameter_name, query_definition, len(no_filter_rows), column_name_in_table, selected_values, "default")


    # Performing a query with a non-existing value, expecting to return no results. Refer to has_any_test function for parameters description.
    def dynamic_tests_check_fictive_value(self, parameter_name, query_definition, column_name_in_table):
        no_results_query = query_definition + create_execution_strings_with_one_parameter(parameter_name,f"dynamic([{DUMMY_VALUE}])" ,column_name_in_table)
        no_results_response = self.send_query(no_results_query)
        with self.subTest():
            self.assertEqual(0, len(no_results_response.tables[0].rows), f"Parameter: {parameter_name} - Returned results for non existing filter value. Filtered by value: {DUMMY_VALUE}")


    def get_substrings_list(self, rows, num_of_substrings, delimiter):
        '''
        The function return a list with at most "num_of_substrings" substrings of values from "rows" to substrings_list.
        A substring of a value will be either its postfix from after the first occurrence of delimiter in the value or its prefix until the last occurrence of delimiter in the value.
        '''
        substrings_list = []
        # Looking for values with substrings that can be appended to the list
        for row in rows:
            if len(substrings_list) == num_of_substrings:
                break

            value = row[COLUMN_INDEX_IN_ROW]
            post = get_postfix(value, rows, substrings_list, delimiter)
            # Post will equal value if: value dont contain the delimiter, post is in the list, post is contained in an item in the list.
            if post != value:
                substrings_list.append(post)
            else:
                pre = get_prefix(value, rows, substrings_list, delimiter)
                # pre will equal value if: value dont contain the delimiter, pre is in the list, pre is contained in an item in the list.
                if pre != value:
                    substrings_list.append(pre)
            
        return substrings_list
        

    def has_any_test(self, parameter_name, query_definition, no_filter_rows, column_name_in_table):
        """
        Test for dynamic parameters with a name that ends with "has_any". Filtering is made with substrings of values from no_filter_rows.   
        
        Parameters
        ----------
        parameter_name : Name of a parser's parameter
        query_definition : A definition of the parser's query
        no_filter_rows : The rows from a response for the parser query with no filter applied
        column_name_in_table : The name of the column in the query response on which the parameter performs filtering
        """
        self.dynamic_common_tests(parameter_name, query_definition, no_filter_rows, column_name_in_table)
        delimiter = get_frequent_non_word_character_from_rows(no_filter_rows)
        # Getting substrings that will be the values of the filtering parameters
        selected_substrings = self.get_substrings_list(no_filter_rows, MAX_FILTERING_PARAMETERS, delimiter)
        with self.subTest():
            self.dynamic_tests_helper(parameter_name, query_definition, len(no_filter_rows), column_name_in_table, selected_substrings, "has_any")
        

    def has_all_test(self, parameter_name, query_definition, no_filter_rows, column_name_in_table):
        """
        Test for dynamic parameters with a name that ends with "has_all". Filtering is made with prefixes of values from no_filter_rows.   
        
        Parameters
        ----------
        parameter_name : Name of a parser's parameter
        query_definition : A definition of the parser's query
        no_filter_rows : The rows from a response for the parser query with no filter applied
        column_name_in_table : The name of the column in the query response on which the parameter performs filtering
        """
        values_list = self.get_values_for_dynamic_tests(no_filter_rows)
        self.fail_if_values_list_is_empty(values_list, parameter_name, "has_all")

        # Performing filtering with one value
        filtering_with_one_value_response, one_value_string = self.get_response_for_query_with_one_parameter(parameter_name, query_definition, column_name_in_table, values_list)
        num_of_rows_when_no_filters_in_query = len (no_filter_rows)
        num_of_rows_with_one_parameter_in_query = len(filtering_with_one_value_response.tables[0].rows)
        self.dynamic_tests_assertions(parameter_name, num_of_rows_with_one_parameter_in_query, one_value_string, num_of_rows_when_no_filters_in_query)

        # Performing filtering with two values if possible
        first_part_of_a_value , second_part_of_a_value = get_splitted_parts_of_string(values_list)
        if first_part_of_a_value is None:
            self.fail(f"Parameter: {parameter_name} - has_all tests performed for only one filtering value")
        splitted_parts_list = [first_part_of_a_value , second_part_of_a_value]
        filtering_response, values_string = self.get_response_for_query_with_parameters(parameter_name, query_definition, column_name_in_table, splitted_parts_list)
        num_of_rows_with_parameters_in_query = len(filtering_response.tables[0].rows)
        self.dynamic_tests_assertions(parameter_name, num_of_rows_with_parameters_in_query, values_string, num_of_rows_when_no_filters_in_query)

        # Performing a query with a non-existing value, expecting to return no results
        self.dynamic_tests_check_fictive_value(parameter_name, query_definition, column_name_in_table)


    def get_prefix_list(self, rows, num_of_prefixes, delimiter):
        '''
        The function return a list with at most "num_of_prefixes" prefixes of values from "rows" to "prefix_list".
        A prefix of a value will be the prefix until the first dot in the value (including the dot).
        '''
        prefix_list = []
        # Looking for values with prefix that can be appended to the list
        for row in rows:
            if len(prefix_list) == num_of_prefixes:
                break
    
            value = row[COLUMN_INDEX_IN_ROW]
            pre = get_prefix(value, rows, prefix_list, delimiter)
            # pre will equal value if: value dont contain a dot, pre is in the list, pre is contained in an item in the list.
            if pre != value:
                prefix_list.append(f"{pre}.")
    
        return prefix_list


    def has_any_prefix_test(self, parameter_name, query_definition, no_filter_rows, column_name_in_table):
        """
        Test for dynamic parameters with a name that ends with "has_any_prefix". Filtering is made with prefixes of values from no_filter_rows.   
        
        Parameters
        ----------
        parameter_name : Name of a parser's parameter
        query_definition : A definition of the parser's query
        no_filter_rows : The rows from a response for the parser query with no filter applied
        column_name_in_table : The name of the column in the query response on which the parameter performs filtering
        """
        self.dynamic_common_tests(parameter_name, query_definition, no_filter_rows, column_name_in_table)
        # Getting prefixes that will be the values of the filtering parameters
        selected_prefixes = self.get_prefix_list(no_filter_rows, MAX_FILTERING_PARAMETERS, '.')
        with self.subTest():
            self.dynamic_tests_helper(parameter_name, query_definition, len(no_filter_rows), column_name_in_table, selected_prefixes, "has_any_prefix")
            

    def dynamic_test(self, parameter, query_definition, column_name_in_table):
        """
        Test for dynamic parameters. Dynamic parameter receive as value an array of strings.

        Parameters
        ----------
        param : A parameter field from the parser yaml file
        query_definition : A definition of the parser's query
        column_name_in_table : The name of the column in the query response on which the parameter performs filtering
        """
        parameter_name = parameter['Name']
        no_filter_query = query_definition + create_execution_string_without_parameters(column_name_in_table)
        no_filter_response = self.send_query(no_filter_query)
        no_filter_rows = no_filter_response.tables[0].rows
        self.assertNotEqual(len(no_filter_rows) , 0 , f"No data for parameter:{parameter_name}")
        with  self.subTest():
            self.assertNotEqual(len(no_filter_rows), 1, f"Only one value exists for parameter: {parameter_name} - validations for this parameter are partial" )

        # Specific tests parameters with certain suffixes 
        if parameter_name.endswith('has_any'):
            self.has_any_test(parameter_name, query_definition,no_filter_rows, column_name_in_table)
        elif parameter_name.endswith('has_any_prefix'):
            self.has_any_prefix_test(parameter_name, query_definition, no_filter_rows, column_name_in_table)
        elif parameter_name.endswith('has_all'):
            self.has_all_test(parameter_name, query_definition, no_filter_rows, column_name_in_table)
        else:
            self.dynamic_common_tests(parameter_name, query_definition, no_filter_rows, column_name_in_table)


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
        failed_query_message = f"The following query failed:\n{query_str}"
        try:
            response = client.query_workspace(
                workspace_id = ws_id,
                query = query_str,
                timespan = (start_time, end_time)
                )
            if response.status == LogsQueryStatus.PARTIAL:
                self.fail(f"Got partial response for the following query:\n{query_str}")
            elif response.status == LogsQueryStatus.FAILURE:
                self.fail(failed_query_message)
            elif response.tables == None or len(response.tables) == 0:
                self.fail("No data tables were returned in the response for the query")
            else:
                return response
        except HttpResponseError as err:
            self.fail(failed_query_message)


##############################################################################################################################

# For each schema supported by the test there is a mapping between each of the schema's parameter to the column that the parameter filters.
all_schemas_parameters = {
    "AuditEvent" :
    {
		"actorusername_has_any" : "ActorUsername",
        "disabled" : "",
        "endtime" : "EventEndTime",
        "eventresult" : "EventResult",
		"eventtype_in" : "EventType",
        "newvalue_has_any" : "NewValue",
        "object_has_any" : "Object",
        "operation_has_any" : "Operation",
        "srcipaddr_has_any_prefix" : "SrcIpAddr",
        "starttime" : "EventStartTime",
    },
    "Authentication" : 
    {
        "disabled" : "",
        "endtime" : "EventEndTime",
        "starttime" : "EventStartTime",
        "targetusername_has" : "TargetUsername"
    },
    "Dns" : 
    {
        "disabled" : "",
        "domain_has_any" : "Domain",
        "eventtype" : "EventType",
        "endtime" : "EventEndTime",
        "response_has_any_prefix" : "DnsResponseName",
        "response_has_ipv4" : "DnsResponseName",
        "responsecodename" : "DnsResponseCodeName",
        "srcipaddr" : "SrcIpAddr",
        "starttime" : "EventStartTime"
    },
    "NetworkSession" :
    {
        "disabled" : "",
        "dstipaddr_has_any_prefix" : "DstIpAddr",
        "dstportnumber" : "DstPortNumber",
        "dvcaction" : "DvcAction",
        "endtime" : "EventEndTime",
        "eventresult" : "EventResult",
        "hostname_has_any" : "Hostname",
        "ipaddr_has_any_prefix" : "IpAddr",
        "srcipaddr_has_any_prefix" : "SrcIpAddr",
        "starttime" : "EventStartTime"
    },
	"ProcessEvent" :
	{
		"actingprocess_has_any" : "ActingProcessName",
		"actorusername" : "ActorUsername",
		"actorusername_has" : "ActorUsername",
		"commandline_has_all" : "CommandLine",
		"commandline_has_any" : "CommandLine",
		"commandline_has_any_ip_prefix" : "CommandLine",
		"disabled" : "",
		"dvchostname_has_any" : "DvcHostname",
		"dvcipaddr_has_any_prefix" : "DvcIpAddr",
		"dvcname_has_any" : "",
		"endtime" : "EventEndTime",
        "eventtype" : "EventType",
		"hashes_has_any" : "Hash",
		"parentprocess_has_any" : "ParentProcessName",
		"starttime" : "EventStartTime",
		"targetprocess_has_any" : "TargetProcessName",
		"targetusername" : "TargetUsername",
		"targetusername_has" : "TargetUsername"
	},
    "WebSession" :
    {
        "disabled" : "",
        "endtime" : "EventEndTime",
        "eventresult" : "EventResult",
        "eventresultdetails_in" : "EventResultDetails",
        "httpuseragent_has_any" : "HttpUserAgent",
        "ipaddr_has_any_prefix" : "IpAddr",
        "srcipaddr_has_any_prefix" : "SrcIpAddr",
        "starttime" : "EventStartTime",
        "url_has_any" : "Url"
    }
}

##############################################################################################################################


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(FilteringTest)
    runner = unittest.TextTestRunner()
    runner.run(suite)