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
SENTINEL_REPO_RAW_URL = f'https://raw.githubusercontent.com/Azure/Azure-Sentinel'
SAMPLE_DATA_PATH = 'Sample%20Data/ASIM/'
parser_exclusion_file_path = '.script/tests/asimParsersTest/ExclusionListForASimTests.csv'
# Sentinel Repo URL
SentinelRepoUrl = f"https://github.com/Azure/Azure-Sentinel.git"
SCHEMA_INFO = [
    {"SchemaName": "AlertEvent", "SchemaVersion": "0.1", "SchemaTitle":"ASIM Alert Event Schema", "SchemaLink": "https://aka.ms/ASimAlertEventDoc"},
    {"SchemaName": "AuditEvent", "SchemaVersion": "0.1", "SchemaTitle":"ASIM Audit Event Schema", "SchemaLink": "https://aka.ms/ASimAuditEventDoc"},
    {"SchemaName": "Authentication", "SchemaVersion": "0.1.3","SchemaTitle":"ASIM Authentication Schema","SchemaLink": "https://aka.ms/ASimAuthenticationDoc"},
    {"SchemaName": "Dns", "SchemaVersion": "0.1.7", "SchemaTitle":"ASIM Dns Schema","SchemaLink": "https://aka.ms/ASimDnsDoc"},
    {"SchemaName": "DhcpEvent", "SchemaVersion": "0.1", "SchemaTitle":"ASIM Dhcp Schema","SchemaLink": "https://aka.ms/ASimDhcpEventDoc"},
    {"SchemaName": "FileEvent", "SchemaVersion": "0.2.1", "SchemaTitle":"ASIM File Schema","SchemaLink": "https://aka.ms/ASimFileEventDoc"},
    {"SchemaName": "NetworkSession", "SchemaVersion": "0.2.6", "SchemaTitle":"ASIM Network Session Schema","SchemaLink": "https://aka.ms/ASimNetworkSessionDoc"},
    {"SchemaName": "ProcessEvent", "SchemaVersion": "0.1.4", "SchemaTitle":"ASIM Process Schema","SchemaLink": "https://aka.ms/ASimProcessEventDoc"},
    {"SchemaName": "RegistryEvent", "SchemaVersion": "0.1.2", "SchemaTitle":"ASIM Registry Schema","SchemaLink": "https://aka.ms/ASimRegistryEventDoc"},
    {"SchemaName": "UserManagement", "SchemaVersion": "0.1.1", "SchemaTitle":"ASIM User Management Schema","SchemaLink": "https://aka.ms/ASimUserManagementDoc"},
    {"SchemaName": "WebSession", "SchemaVersion": "0.2.6", "SchemaTitle":"ASIM Web Session Schema","SchemaLink": "https://aka.ms/ASimWebSessionDoc"}
    # Add more schemas as needed
]

# Global array to store results
results = []
# Global variable to store if test failed
failed = 0

# ANSI escape sequences for colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'  # Reset to default color

def run():
    """Main function to execute the script logic."""
    current_directory = os.path.dirname(os.path.abspath(__file__))
    modified_files = get_modified_files(current_directory)
    commit_number = get_current_commit_number()
    sample_data_url = f'{SENTINEL_REPO_RAW_URL}/{commit_number}/{SAMPLE_DATA_PATH}'
    parser_yaml_files = filter_yaml_files(modified_files)
    print(f"{GREEN}Following files were found to be modified:{RESET}")
    for file in parser_yaml_files:
        print(f"{YELLOW}{file}{RESET}")
    
    for parser in parser_yaml_files:
        
        schema_name = extract_schema_name(parser)
        if parser.endswith((f'ASim{schema_name}.yaml', f'im{schema_name}.yaml', f'vim{schema_name}Empty.yaml')):
            print(f"{YELLOW}Skipping '{parser}' as this is a union or empty parser file. This file won't be tested.{RESET}")
            continue
        # Skip vim parser file if the corresponding ASim parser file is not present
        elif parser.split('/')[-1].startswith('vim'):
             # Check if ASim parser file is present in the changed files list. If not present, replace vim with ASim.
             # This could the case where only vim parser file is being updated and ASim parser file is not updated.
             # But we should be testing both ASim and vim parser files.
             if parser.replace('vim', 'ASim') not in parser_yaml_files:
                 parser = parser.replace('vim', 'ASim')
             else :
                 # Skip the vim parser file as the corresponding ASim parser file is present and vim files will be tested with ASim files in upcoming steps.
                 continue 
        asim_parser_url = f'{SENTINEL_REPO_RAW_URL}/{commit_number}/{parser}'
        print(f'{YELLOW}Constructed parser raw url:  {asim_parser_url}{RESET}') # uncomment for debugging
        asim_union_parser_url = f'{SENTINEL_REPO_RAW_URL}/{commit_number}/Parsers/ASim{schema_name}/Parsers/ASim{schema_name}.yaml'
        print(f'{YELLOW}Constructed union parser raw url:  {asim_union_parser_url}{RESET}') # uncomment for debugging
        asim_parser = read_github_yaml(asim_parser_url)
        asim_union_parser = read_github_yaml(asim_union_parser_url)
        # Both ASim and union parser files should be present to proceed with the tests
        if not (check_parser_found(asim_parser, asim_parser_url) and check_parser_found(asim_union_parser, asim_union_parser_url)):
            continue
        print_test_header(asim_parser.get('EquivalentBuiltInParser'))
        results = extract_and_check_properties(asim_parser, asim_union_parser, "ASim", asim_parser_url, sample_data_url)
        print_results_table(results)

        check_test_failures(results, asim_parser)

        vim_parser, vim_union_parser = get_vim_parsers(asim_parser_url, asim_union_parser_url, asim_parser)
        # Both vim and union parser files should be present to proceed with the tests
        if not (check_parser_found(vim_parser, asim_parser_url) and check_parser_found(vim_union_parser, asim_union_parser_url)):
            continue
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
        results.append((event_product, '"EventProduct" field is mapped in parser', 'Pass'))
    # if equivalent_built_in_parser end with Native, then use 'EventProduct' as SchemaName + 'NativeTable'
    elif equivalent_built_in_parser.endswith('_Native'):
        event_product = 'NativeTable'
        results.append((event_product, '"EventProduct" field is not required since this is a native table parser. Static value will be used for "EventProduct".', 'Pass'))
    # If 'EventProduct' was not found in the KQL query, add to results
    else:
        results.append((f'{RED}EventProduct{RESET}', f'{RED}"EventProduct" field not mapped in parser. Please map it in parser query.{RESET}', f'{RED}Fail{RESET}'))

    # Use a regular expression to find 'EventVendor' in the KQL query
    match = re.search(r'EventVendor\s*=\s*[\'"]([^\'"]+)[\'"]', parser_query)

    # If 'EventVendor' was found in the KQL query, extract its value
    if match:
        event_vendor = match.group(1)
        results.append((event_vendor, '"EventVendor" field is mapped in parser', 'Pass'))
    # if equivalent_built_in_parser end with Native, then use 'EventVendor' as 'Microsoft'
    elif equivalent_built_in_parser.endswith('_Native'):
        event_vendor = 'Microsoft'
        results.append((event_vendor, '"EventVendor" field is not required since this is a native table parser. Static value will be used for "EventVendor".', 'Pass'))
    # If 'EventVendor' was not found in the KQL query, add to results
    else:
        results.append((f'{RED}EventVendor{RESET}', f'{RED}"EventVendor" field not mapped in parser. Please map it in parser query.{RESET}', f'{RED}Fail{RESET}'))

    # Check if parser_name exists in another_yaml_file's 'ParserQuery'
    if parser_name:
        if parser_name in Union_Parser__file.get('ParserQuery', ''):
            results.append((parser_name, 'Parser entry exists in union parser under "ParserQuery" property', 'Pass'))
        else:
            results.append(( f'{RED}' + parser_name + f'{RESET}', f'{RED}Parser entry not found in union parser under "ParserQuery" property{RESET}', f'{RED}Fail{RESET}'))

    # Check if equivalent_built_in_parser exists in another_yaml_file's 'Parsers'
    if equivalent_built_in_parser:
        if equivalent_built_in_parser in Union_Parser__file.get('Parsers', []):
            results.append((equivalent_built_in_parser, 'Parser entry exists in union parser under "Parsers" property', 'Pass'))
        else:
            results.append((f'{RED}' + str(equivalent_built_in_parser) + f'{RESET}', f'{RED}Parser entry not found in union parser under "Parsers" property{RESET}', f'{RED}Fail{RESET}'))

    # Check if title exists in yaml_file's 'Parser'->'Title'       
    if title:
        results.append((title, 'This value exists in Title property', 'Pass'))
    else:
        results.append((f'{RED}Title{RESET}', f'{RED}Title not found in parser YAML{RESET}', f'{RED}Fail{RESET}'))
    # Check if version exists in yaml_file's 'Parser'->'Version' and matches the format X.X.X
    if version:
        if re.match(r'^\d+\.\d+\.\d+$', version):
            results.append((version, 'This value exist in the parser version property', 'Pass'))
        else:
            results.append((f'{RED}' + str(version) + f'{RESET}', f'{RED}The parser version should be in a three-digit format, e.g., 0.1.0{RESET}', f'{RED}Fail{RESET}'))
    else:
        results.append((f'{RED}Version{RESET}', 'f{RED}Parser version not found in parser YAML{RESET}', f'{RED}Fail{RESET}'))

    # Check if last_updated exists in yaml_file's 'Parser'->'LastUpdated' and matches the format MMM DD YY
    if last_updated:
        try:
            datetime.strptime(last_updated, '%b %d, %Y')
            results.append((last_updated, 'This value exist in LastUpdated property', 'Pass'))
        except ValueError:
            results.append((f'{RED}' + str(last_updated) + f'{RESET}', f'{RED}"LastUpdated" property exists but is not correct format. The expected format is, for example, "Jun 29, 2024"{RESET}', f'{RED}Fail{RESET}'))
    else:
        results.append((f'{RED}LastUpdated{RESET}', f'{RED}LastUpdated not found in parser YAML{RESET}', f'{RED}Fail{RESET}'))
    
    # Check if schema exists in yaml_file's 'Normalization'->'Schema' and matches with our SchemaInfo
    if schema:
        for info in SCHEMA_INFO:
            if info['SchemaName'] == schema:
                results.append((schema, f'ASIM schema name "{schema}" is correct', 'Pass'))
                break
        else:
            results.append((f'{RED}' + str(schema) + f'{RESET}', f'{RED}ASIM schema name "{schema}" is incorrect. Please re-check Schema name{RESET}.', f'{RED}Fail{RESET}'))
    else:
        results.append((f'{RED}Schema{RESET}', f'{RED}ASIM schema name {info['SchemaName']} not found in parser YAML{RESET}', f'{RED}Fail{RESET}'))
    
    # Check if Schema Version exists in yaml_file's 'Normalization'->'Schema' and matches with our SchemaInfo
    if schemaVersion:
        for info in SCHEMA_INFO:
            if schema == info.get('SchemaName'):
                if info['SchemaVersion'] == schemaVersion and info['SchemaName'] == schema:
                    results.append((schemaVersion, f'ASIM schema {info.get('SchemaName')} version is correct', 'Pass'))
                    break
                else:
                    results.append((f'{RED}' + str(schemaVersion) + f'{RESET}', f'{RED}ASIM schema "{schema}" version "{schemaVersion}" is incorrect. The correct version for ASIM schema "{schema}" is "{info['SchemaVersion']}"{RESET}', f'{RED}Fail{RESET}'))
    else:
        results.append((f'{RED}Version{RESET}', f'{RED}ASIM schema {schema} version not found in parser YAML{RESET}', f'{RED}Fail{RESET}'))

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
                        results.append((title, 'Schema specific reference link matching', 'Pass'))
                    elif title == 'ASIM' and link == 'https://aka.ms/AboutASIM':
                        results.append((title, 'ASim doc reference link matching', 'Pass'))
                    elif title != 'ASIM' and title != titleSchemaInfo:
                        results.append((title, 'Product specific reference title exist. Please access URL manually to confirm it is a valid link', 'Pass'))
                    else:
                        results.append((f'{RED}' + str(title) + f'{RESET}', f'{RED}Reference title or link not matching. Please use title as "{titleSchemaInfo}" and link as "{linkSchemaInfo}"{RESET}', f'{RED}Fail{RESET}'))
    else:
        results.append((f'{RED}References{RESET}', f'{RED}References{RESET}', f'{RED}Fail{RESET}'))

    # Check if ParserName exists in yaml_file and matches the format ASIMAuditEvent<ProductName>
    if parser_name:
        if re.match(rf'{FileType}{schema}', parser_name):
            results.append((parser_name, 'ParserName is in correct format', 'Pass'))
        else:
            results.append((f'{RED}' + str(parser_name) + f'{RESET}', f'{RED}ParserName is not in correct format{RESET}', f'{RED}Fail{RESET}'))
    else:
        results.append((f'{RED}ParserName{RESET}', f'{RED}ParserName not found{RESET}', f'{RED}Fail{RESET}'))

    # Check if EquivalentBuiltInParser exists in yaml_file and matches the format _ASIM_<Schema><ProductName>
    FileType = "Im" if FileType == "vim" else FileType
    if equivalent_built_in_parser:
        if re.match(rf'_{FileType}_{schema}_', equivalent_built_in_parser):
            results.append((equivalent_built_in_parser, 'EquivalentBuiltInParser is in correct format', 'Pass'))
        else:
            results.append((f'{RED}' + str(equivalent_built_in_parser) + f'{RESET}', f'{RED}EquivalentBuiltInParser is not in correct format. The correct format is "_{FileType}_{schema}_ProductName"{RESET}', f'{RED}Fail{RESET}'))
    else:
        results.append((f'{RED}EquivalentBuiltInParser{RESET}', f'{RED}"EquivalentBuiltInParser" property not found in parser{RESET}', f'{RED}Fail{RESET}'))
    
    # Check if sample data files exists or not (Only applicable for ASim FileType)
    
    if FileType == "ASim":
        # construct filename
        SampleDataFile = f'{event_vendor}_{event_product}_{schema}_IngestedLogs.csv'
        SampleDataUrl = ASIMSampleDataURL+SampleDataFile
        # check if file exists
        response = requests.get(SampleDataUrl)
        if response.status_code == 200:
            results.append((SampleDataFile, 'Sample data file exists', 'Pass'))
        else:
            results.append((f'{RED}Expected sample file not found{RESET}', f'{RED}Sample data file does not exist or may not be named correctly. Please include sample data file "{event_vendor}_{event_product}_{schema}_IngestedLogs.csv"{RESET}', f'{RED}Fail{RESET}'))
    return results

def filter_yaml_files(modified_files):
    # Take only the YAML files
    return [line for line in modified_files if line.endswith('.yaml')]

def get_modified_files(current_directory):

    # Add upstream remote if not already present
    git_remote_command = "git remote"
    remote_result = subprocess.run(git_remote_command, shell=True, text=True, capture_output=True, check=True)
    if 'upstream' not in remote_result.stdout.split():
        git_add_upstream_command = f"git remote add upstream '{SentinelRepoUrl}'"
        subprocess.run(git_add_upstream_command, shell=True, text=True, capture_output=True, check=True)
    # Fetch from upstream
    git_fetch_upstream_command = "git fetch upstream"
    subprocess.run(git_fetch_upstream_command, shell=True, text=True, capture_output=True, check=True)
    cmd = f"git diff --name-only upstream/master {current_directory}/../../../Parsers/"
    try:
        return subprocess.check_output(cmd, shell=True).decode().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"::error::Error occurred while executing the command: {e}")
        return []

def get_current_commit_number():
    cmd = "git rev-parse HEAD"
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except subprocess.CalledProcessError as e:
        print(f"::error::Error occurred while executing the command: {e}")
        return None

def extract_schema_name(parser):
    match = re.search(r'ASim(\w+)/', parser)
    return match.group(1) if match else None

def read_github_yaml(url):
    try:
        response = requests.get(url)
    except Exception as e:
        print(f"::error::An error occurred while trying to get content of YAML file located at {url}: {e}")
    return yaml.safe_load(response.text) if response.status_code == 200 else None

def print_test_header(parser_name):
    print("***********************************")
    print(f"{GREEN}Performing tests for Parser: {parser_name}{RESET}")
    print("***********************************")

def print_results_table(results):
    table = [[index + 1] + list(result) for index, result in enumerate(results)]
    print(tabulate(table, headers=['S.No', 'Test Value', 'Test Name', 'Result'], tablefmt="grid"))

def check_test_failures(results, parser):
    if any(result[-1] == f'{RED}Fail{RESET}' for result in results):
        print("::error::Some tests failed for Parser. Please check the results above.")
        exclusion_list = read_exclusion_list_from_csv()
        if parser.get('EquivalentBuiltInParser') in exclusion_list:
            print(f"::warning::The parser {parser.get('EquivalentBuiltInParser')} is listed in the exclusions file, so this workflow run will not fail because of it. To allow this parser to trigger a workflow failure, please remove its name from the exclusions list file located at: {parser_exclusion_file_path}")
        else:
            exit(1)
    else:
        print(f"{GREEN}All tests successfully passed for this parser.{RESET}")

def check_parser_found(asim_parser,parser_url):
    if asim_parser is None:
        print(f"::error::Parser file not found. Please check the URL and try again: {parser_url}")
        exit(1) # Uncomment this line to fail the workflow if parser file not found.
    else:
        return True

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
    with open(parser_exclusion_file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            exclusion_list.append(row[0])
    return exclusion_list

# Script starts here
if __name__ == "__main__":
    run()