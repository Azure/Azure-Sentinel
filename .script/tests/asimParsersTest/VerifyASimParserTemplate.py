import requests
import yaml
import re
import os
import subprocess
import csv
from datetime import datetime
from urllib.parse import urlparse
from tabulate import tabulate

# Constants
SENTINEL_REPO_URL = f'https://raw.githubusercontent.com/Azure/Azure-Sentinel'
SAMPLE_DATA_PATH = '/Sample%20Data/ASIM/'
SCHEMA_INFO = [
    {"SchemaName": "AuditEvent", "SchemaVersion": "0.1", "SchemaTitle":"ASIM Audit Event Schema", "SchemaLink": "https://aka.ms/ASimAuditEventDoc"},
    {"SchemaName": "Authentication", "SchemaVersion": "0.1.3","SchemaTitle":"ASIM Authentication Schema","SchemaLink": "https://aka.ms/ASimAuthenticationDoc"},
    {"SchemaName": "UserManagement", "SchemaVersion": "0.1.1", "SchemaTitle":"ASIM User Management Schema","SchemaLink": "https://aka.ms/ASimUserManagementDoc"},
    # Add more schemas as needed
]

# Global array to store results
results = []
# Global variable to store if test failed
failed = 0

def run():
    """Main function to execute the script logic."""
    current_directory = os.path.dirname(os.path.abspath(__file__))
    modified_files = get_modified_files(current_directory)
    commit_number = get_current_commit_number()
    sample_data_url = f'{SENTINEL_REPO_URL}/{commit_number}/{SAMPLE_DATA_PATH}'
    parser_yaml_files = filter_yaml_files(modified_files)
    
    for parser in parser_yaml_files:
        schema_name = extract_schema_name(parser)
        if not schema_name or parser.endswith(f'ASim{schema_name}.yaml'):
            continue
        asim_parser_url = f'{SENTINEL_REPO_URL}/{commit_number}/{parser}'
        asim_union_parser_url = f'{SENTINEL_REPO_URL}/{commit_number}/Parsers/ASim{schema_name}/Parsers/ASim{schema_name}.yaml'
        asim_parser = read_github_yaml(asim_parser_url)
        asim_union_parser = read_github_yaml(asim_union_parser_url)

        print_test_header(asim_parser.get('EquivalentBuiltInParser'))
        results = extract_and_check_properties(asim_parser, asim_union_parser, "ASim", asim_parser_url, sample_data_url)
        print_results_table(results)

        check_test_failures(results, asim_parser)

        vim_parser, vim_union_parser = get_vim_parsers(asim_parser_url, asim_union_parser_url, asim_parser)
        print_test_header(vim_parser.get('EquivalentBuiltInParser'))
        results = extract_and_check_properties(vim_parser, vim_union_parser, "vim", asim_parser_url, sample_data_url)
        print_results_table(results)

        check_test_failures(results, vim_parser)

def extract_and_check_properties(Parser_file, Union_Parser__file, FileType, ParserUrl, ASIMSampleDataURL):
    """
    Extracts properties from the given YAML files and checks if they exist in another YAML file.

    Args:
        yaml_file (dict): The YAML file to extract properties from.
        another_yaml_file (dict): The YAML file to check for the existence of properties.

    Returns:
        list: A list of tuples containing the property name, the property type, and a boolean indicating if the property exists in another_yaml_file.
    """
    results = []
    parser_name = Parser_file.get('ParserName')
    equivalent_built_in_parser = Parser_file.get('EquivalentBuiltInParser')
    parser = Parser_file.get('Parser', {})
    title = parser.get('Title')
    version = parser.get('Version')
    last_updated = parser.get('LastUpdated')
    normalization = Parser_file.get('Normalization', {})
    schema = normalization.get('Schema')
    schemaVersion = normalization.get('Version')
    references = Parser_file.get('References', [])

    # ParserQuery property is the KQL query extracted from the YAML file
    parser_query = Parser_file.get('ParserQuery', '')

    # Use a regular expression to find 'EventProduct' in the KQL query
    match = re.search(r'EventProduct\s*=\s*[\'"]([^\'"]+)[\'"]', parser_query)

    # If 'EventProduct' was found in the KQL query, extract its value
    if match:
        event_product = match.group(1)
        results.append((event_product, 'EventProduct found in parser query', True))
    # If 'EventProduct' was not found in the KQL query, add to results
    else:
        results.append(('\033[91mEventProduct\033[0m', '\033[91mEventProduct not found in Parser query\033[0m', '\033[91mFalse\033[0m'))

    # Use a regular expression to find 'EventVendor' in the KQL query
    match = re.search(r'EventVendor\s*=\s*[\'"]([^\'"]+)[\'"]', parser_query)

    # If 'EventVendor' was found in the KQL query, extract its value
    if match:
        event_vendor = match.group(1)
        results.append((event_vendor, 'EventVendor found in parser query', True))
    # If 'EventVendor' was not found in the KQL query, add to results
    else:
        results.append(('\033[91mEventVendor\033[0m', '\033[91mEventVendor not found in Parser query\033[0m', '\033[91mFalse\033[0m'))

    # Check if parser_name exists in another_yaml_file's 'ParserQuery'
    if parser_name:
        if parser_name in Union_Parser__file.get('ParserQuery', ''):
            results.append((parser_name, 'ParserName exist in union parser', True))
        else:
            results.append((parser_name, 'ParserName not found in union parser', False))

    # Check if equivalent_built_in_parser exists in another_yaml_file's 'Parsers'
    if equivalent_built_in_parser:
        if equivalent_built_in_parser in Union_Parser__file.get('Parsers', []):
            results.append((equivalent_built_in_parser, 'EquivalentBuiltInParser exist in union parser', True))
        else:
            results.append(('\033[91m' + str(equivalent_built_in_parser) + '\033[0m', '\033[91mEquivalentBuiltInParser not found in union parser\033[0m', '\033[91mFalse\033[0m'))

    # Check if title exists in yaml_file's 'Parser'->'Title'       
    if title:
        results.append((title, 'This value exist in Title property', True))
    else:
        results.append(('Title', 'Title not found in parser YAML', False))
    # Check if version exists in yaml_file's 'Parser'->'Version' and matches the format X.X.X
    if version:
        if re.match(r'^\d+\.\d+\.\d+$', version):
            results.append((version, 'This value exist in Version property', True))
        else:
            results.append(('\033[91m' + str(version) + '\033[0m', '\033[91mVersion exist but format is incorrect\033[0m', '\033[91mFalse\033[0m'))
    else:
        results.append(('Version', 'Version not found in parser YAML', False))

    # Check if last_updated exists in yaml_file's 'Parser'->'LastUpdated' and matches the format MMM DD YY
    if last_updated:
        try:
            datetime.strptime(last_updated, '%b %d, %Y')
            results.append((last_updated, 'This value exist in LastUpdated property', True))
        except ValueError:
            results.append(('\033[91m' + str(last_updated) + '\033[0m', '\033[91mLastUpdated exist but format is incorrect\033[0m', '\033[91mFalse\033[0m'))
    else:
        results.append(('\033[91mLastUpdated\033[0m', '\033[91mLastUpdated not found in parser YAML\033[0m', '\033[91mFalse\033[0m'))
    
    # Check if schema exists in yaml_file's 'Normalization'->'Schema' and matches with our SchemaInfo
    if schema:
        for info in SCHEMA_INFO:
            if info['SchemaName'] == schema:
                results.append((schema, 'Schema name is correct', True))
                break
        else:
            results.append(('\033[91m' + str(schema) + '\033[0m', '\033[91mSchema name is incorrect\033[0m', '\033[91mFalse\033[0m'))
    else:
        results.append(('Schema', 'Schema name not found in parser YAML', False))
    
    # Check if Schema Version exists in yaml_file's 'Normalization'->'Schema' and matches with our SchemaInfo
    if schemaVersion:
        for info in SCHEMA_INFO:
            if schema == info.get('SchemaName'):
                if info['SchemaVersion'] == schemaVersion and info['SchemaName'] == schema:
                    results.append((schemaVersion, 'Schema Version is correct', True))
                    break
                else:
                    results.append(('\033[91m' + str(schemaVersion) + '\033[0m', '\033[91mSchema Version is incorrect\033[0m', '\033[91mFalse\033[0m'))
    else:
        results.append(('Version', 'Schema Version not found in parser YAML', False))

    # Check if references exist in yaml_file's 'References'
    if references:
        for ref in references:
            title = ref.get('Title')
            link = ref.get('Link')

            for info in SCHEMA_INFO:
                titleSchemaInfo = info.get('SchemaTitle')
                linkSchemaInfo = info.get('SchemaLink')
                if schema == info.get('SchemaName'):
                    if title == titleSchemaInfo and link == linkSchemaInfo:
                        results.append((title, 'Schema specific reference link matching', True))
                    elif title == 'ASIM' and link == 'https:/aka.ms/AboutASIM':
                        results.append((title, 'ASim doc reference link matching', True))
                    else:
                        results.append(('\033[91m' + str(title) + '\033[0m', '\033[91mreference title or link not matching\033[0m', '\033[91mFalse\033[0m'))
    else:
        results.append(('\033[91mReferences\033[0m', '\033[91mReferences\033[0m', '\033[91mFalse\033[0m'))

    # Check if ParserName exists in yaml_file and matches the format ASIMAuditEvent<ProductName>
    if parser_name:
        if re.match(rf'{FileType}{schema}', parser_name):
            results.append((parser_name, 'ParserName is in correct format', True))
        else:
            results.append(('\033[91m' + str(parser_name) + '\033[0m', '\033[91mParserName is not in correct format\033[0m', '\033[91mFalse\033[0m'))
    else:
        results.append(('\033[91mParserName\033[0m', '\033[91mParserName not found\033[0m', '\033[91mFalse\033[0m'))

    # Check if EquivalentBuiltInParser exists in yaml_file and matches the format _ASIM_<Schema><ProductName>
    FileType = "Im" if FileType == "vim" else FileType
    if equivalent_built_in_parser:
        if re.match(rf'_{FileType}_{schema}_', equivalent_built_in_parser):
            results.append((equivalent_built_in_parser, 'EquivalentBuiltInParser is in correct format', True))
        else:
            results.append(('\033[91m' + str(equivalent_built_in_parser) + '\033[0m', '\033[91mEquivalentBuiltInParser is not in correct format\033[0m', '\033[91mFalse\033[0m'))
    else:
        results.append(('\033[91mEquivalentBuiltInParser\033[0m', '\033[91mEquivalentBuiltInParser not found\033[0m', '\033[91mFalse\033[0m'))

    # Multi-line comment
    '''
    # Check if tester files exists or not
    
    # Construct ASim DataTest.csv filename
    DataTestFileName = f'{event_vendor}_{event_product}_{FileType}{schema}_DataTest.csv'
    # Construct ASim SchemaTest.csv filename
    SchemaTestFileName = f'{event_vendor}_{event_product}_{FileType}{schema}_SchemaTest.csv'
    Testerfilenames = [DataTestFileName, SchemaTestFileName]
    # Parse the URL
    parsed_url = urlparse(ParserUrl)
    # Extract everything except the filename
    url_without_filename = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path.rsplit('/', 2)[0]
    for filename in Testerfilenames:
        # DataTest.csv full URL construct
        DataTestUrl = url_without_filename + "//Tests//" + filename
        response = requests.get(DataTestUrl)
        if response.status_code == 200:
            results.append((filename, 'Tester file exists', True))
        else:
            results.append(('\033[91m' + str(filename) + '\033[0m', '\033[91mTester file does not exist\033[0m', '\033[91mFalse\033[0m'))
    '''
    
    # Check if sample data files exists or not (Only applicable for ASim FileType)
    
    if FileType == "ASim":
        # construct filename
        SampleDataFile = f'{event_vendor}_{event_product}_{FileType}{schema}_IngestedLogs.csv'
        SampleDataUrl = ASIMSampleDataURL+SampleDataFile
        # check if file exists
        response = requests.get(SampleDataUrl)
        if response.status_code == 200:
            results.append((SampleDataFile, 'Sample data exists', True))
        else:
            results.append(('\033[91m' + str(SampleDataFile) + '\033[0m', '\033[91mSample data does not exist\033[0m', '\033[91mFalse\033[0m'))
    return results

def filter_yaml_files(modified_files):
    return [line for line in modified_files if line.split('/')[-1].startswith('ASim') and line.endswith('.yaml')]

def get_modified_files(current_directory):
    cmd = f"git diff --name-only origin/master {current_directory}/../../../Parsers/"
    try:
        return subprocess.check_output(cmd, shell=True).decode().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing the command: {e}")
        return []

def get_current_commit_number():
    cmd = "git rev-parse HEAD"
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing the command: {e}")
        return None

def extract_schema_name(parser):
    match = re.search(r'ASim(\w+)/', parser)
    return match.group(1) if match else None

def read_github_yaml(url):
    response = requests.get(url)
    return yaml.safe_load(response.text) if response.status_code == 200 else None

def print_test_header(parser_name):
    print("***********************************")
    print(f"Performing tests for Parser: {parser_name}")
    print("***********************************")

def print_results_table(results):
    table = [[index + 1] + list(result) for index, result in enumerate(results)]
    print(tabulate(table, headers=['S.No', 'Test Value', 'Test Name', 'Result'], tablefmt="grid"))

def check_test_failures(results, parser):
    if any(result[-1] is not True for result in results):
        print("::error::Some tests failed for Parser. Please check the results above.")
    exclusion_list = read_exclusion_list_from_csv()
    if parser.get('EquivalentBuiltInParser') in exclusion_list:
        print(f"::warning::{parser.get('EquivalentBuiltInParser')} is in the exclusion list. Ignoring error(s).")
        global failed
        failed = 0
    else:
        failed = 1

def get_vim_parsers(asim_parser_url, asim_union_parser_url, asim_parser):
    # Split the URL into parts
    parts = asim_parser_url.split('/')
    # Replace 'ASim' with 'vim' in the filename only
    parts[-1] = parts[-1].replace('ASim', 'vim', 1)
    # Join the parts back into a full URL for vim_parser_url
    vim_parser_url = '/'.join(parts)
    # Repeat the process for asim_union_parser_url
    parts_union = asim_union_parser_url.split('/')
    # Replace 'ASim' with 'im' in the filename only
    parts_union[-1] = parts_union[-1].replace('ASim', 'im', 1)
    # Join the parts back into a full URL for vim_union_parser_url
    vim_union_parser_url = '/'.join(parts_union)
    vim_parser = read_github_yaml(vim_parser_url)
    vim_union_parser = read_github_yaml(vim_union_parser_url)
    return vim_parser, vim_union_parser

# Function to read Exclusion list for ASim Parser test from a CSV file
def read_exclusion_list_from_csv():
    exclusion_list = []
    file_path = '.script/tests/asimParsersTest/ExclusionListForASimTests.csv'
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            exclusion_list.append(row[0])
    return exclusion_list

# Script starts here
if __name__ == "__main__":
    run()