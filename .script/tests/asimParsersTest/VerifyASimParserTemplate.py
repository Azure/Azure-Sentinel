import sys
import os

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Remove the script's directory from sys.path to avoid importing local malicious modules
if script_dir in sys.path:
    sys.path.remove(script_dir)

import requests
import yaml
import re
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

def get_user_input_for_local_validation():
    # Get ASim parser file path
    while True:
        asim_parser_path = input("Enter the path to your ASim parser YAML file: ").strip()
        
        # Handle quoted paths
        if asim_parser_path.startswith('"') and asim_parser_path.endswith('"'):
            asim_parser_path = asim_parser_path[1:-1]
        
        if not asim_parser_path:
            print("Please enter a valid file path")
            continue
        if not os.path.exists(asim_parser_path):
            print(f"File not found: {asim_parser_path}")
            continue
        if not asim_parser_path.endswith('.yaml'):
            print("Parser file must be a YAML file")
            continue
        break
    
    # Extract base folder path
    base_folder_path = extract_base_folder_path(asim_parser_path)
    if base_folder_path:
        print(f"{GREEN}Base folder path detected: {base_folder_path}{RESET}")
        relative_asim_path = get_relative_parser_path(asim_parser_path, base_folder_path)
        print(f"{YELLOW}Relative ASim parser path: {relative_asim_path}{RESET}")
    else:
        print(f"{YELLOW}Warning: Could not detect 'Parsers' directory in path{RESET}")
        base_folder_path = os.path.dirname(asim_parser_path)

    # Get vim parser file path
    while True:
        vim_parser_path = input("Enter the path to your vim parser YAML file (or press Enter to skip): ").strip()
        
        # Handle quoted paths
        if vim_parser_path.startswith('"') and vim_parser_path.endswith('"'):
            vim_parser_path = vim_parser_path[1:-1]
        
        if not vim_parser_path:
            # User pressed Enter - will skip vim validation
            vim_parser_path = None
            break
        if not os.path.exists(vim_parser_path):
            print(f"File not found: {vim_parser_path}")
            continue
        if not vim_parser_path.endswith('.yaml'):
            print("Parser file must be a YAML file")
            continue
        break
    # Get sample data csv file path
    while True:
        sampleDataFilePath = input("Enter the path to your Sample Data csv file (or press Enter to skip): ").strip()
        
        # Handle quoted paths
        if sampleDataFilePath.startswith('"') and sampleDataFilePath.endswith('"'):
            sampleDataFilePath = sampleDataFilePath[1:-1]
        
        if not sampleDataFilePath:
            # User pressed Enter - will skip vim validation
            sampleDataFilePath = None
            break
        if not os.path.exists(sampleDataFilePath):
            print(f"File not found: {sampleDataFilePath}")
            continue
        if not sampleDataFilePath.endswith('.csv'):
            print("Parser file must be a CSV file")
            continue
        break
    return True, asim_parser_path, vim_parser_path, sampleDataFilePath, base_folder_path

def remove_leading_separators(path):
    """Remove leading forward slashes and backslashes from a string"""
    return path.lstrip('\\/')

def run():
    """Main function to execute the script logic."""
    print(f"{GREEN}Make sure that column in your parser named EventVendor, EventProduct and Schema are present and Name your sample data file as `EventVendor_EventProduct_Schema_IngestedLogs.csv`.{RESET}")
    # Check if running locally
    local_mode, asim_parser_file, vim_parser_file, sampleDataFilePath, base_folder_path = get_user_input_for_local_validation()
    local_mode = False
    if local_mode:
        print(f"{GREEN}Running local validation mode{RESET}")
        print(f"{YELLOW}ASim parser file: {asim_parser_file}{RESET}")
        if vim_parser_file:
            print(f"{YELLOW}vim parser file: {vim_parser_file}{RESET}")
        else:
            print(f"{YELLOW}vim parser file: Will be skipped{RESET}")
        
        print("=" * 80)
        
        # Validate ASim parser
        print(f"{GREEN}Validating ASim parser...{RESET}")
        asim_success = run_local_validation("", asim_parser_file, "ASim")
        
        # Validate vim parser if provided
        vim_success = True
        if vim_parser_file:
            print(f"{GREEN}Validating vim parser...{RESET}")
            vim_success = run_local_validation("", vim_parser_file, "vim")
        
        # Summary
        print("=" * 80)
        print(f"{GREEN}Validation Summary:{RESET}")
        if asim_success:
            print(f"{GREEN}✅ ASim parser validation passed{RESET}")
        else:
            print(f"{RED}❌ ASim parser validation failed{RESET}")
        
        if vim_parser_file:
            if vim_success:
                print(f"{GREEN}✅ vim parser validation passed{RESET}")
            else:
                print(f"{RED}❌ vim parser validation failed{RESET}")
        else:
            print(f"{YELLOW}⚠️ vim parser validation skipped{RESET}")
        
        if asim_success and vim_success:
            print(f"{GREEN}🎉 All validations completed successfully!{RESET}")
        else:
            print(f"{RED}💥 Some validations failed. Please fix the issues above.{RESET}")
        
        return
    
    # Continue with GitHub workflow mode
    # current_directory = os.path.dirname(os.path.abspath(__file__))
    # modified_files = get_modified_files(current_directory)
    # commit_number = get_current_commit_number()

    parser_yaml_files = []
    parser_yaml_files.append(asim_parser_file)
    parser_yaml_files.append(vim_parser_file)
    sample_data_url = sampleDataFilePath #f'{SENTINEL_REPO_RAW_URL}/{commit_number}/{SAMPLE_DATA_PATH}'
    #parser_yaml_files = filter_yaml_files(modified_files)
    print(f"{GREEN}Following files were found to be modified:{RESET}")
    for file in parser_yaml_files:
        print(f"{YELLOW}{file}{RESET}")
    
    base_folder_path_with_backslashes = base_folder_path.replace('/', '\\')
    for parser1 in parser_yaml_files:
        parser = parser1.replace(base_folder_path, "").replace(base_folder_path_with_backslashes, "")
        parser = remove_leading_separators(parser)
        print(f"{YELLOW}Processing parser file: {parser}{RESET}")
        #parser = "ASimRegistryEvent"
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
        asim_parser_url = f'{base_folder_path}/{parser}' #f'{SENTINEL_REPO_RAW_URL}/{commit_number}/{parser}'
        print(f'{YELLOW}Constructed parser raw url:  {asim_parser_url}{RESET}') # uncomment for debugging
        asim_union_parser_url = f'{base_folder_path}/ASim{schema_name}/Parsers/ASim{schema_name}.yaml'
        print(f'{YELLOW}Constructed union parser raw url:  {asim_union_parser_url}{RESET}') # uncomment for debugging
        asim_parser = read_yaml_file(asim_parser_url) #read_github_yaml(asim_parser_url)
        asim_union_parser = read_yaml_file(asim_union_parser_url) #read_github_yaml(asim_union_parser_url)
        # Both ASim and union parser files should be present to proceed with the tests
        if not (check_parser_found(asim_parser, asim_parser_url) and check_parser_found(asim_union_parser, asim_union_parser_url)):
            continue
        print_test_header(asim_parser.get('EquivalentBuiltInParser'))
        results = extract_and_check_properties(asim_parser, asim_union_parser, "ASim", asim_parser_url, sample_data_url)
        print_results_table(results)

        check_test_failures(results, asim_parser, base_folder_path)

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
        Parser_file (dict): The YAML file to extract properties from.
        Union_Parser__file (dict): The YAML file to check for the existence of properties.
        FileType (str): Type of parser file (ASim, vim, etc.)
        ParserUrl (str): URL of the parser file
        ASIMSampleDataURL (str): URL for sample data

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
    elif equivalent_built_in_parser and equivalent_built_in_parser.endswith('_Native'):
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
    elif equivalent_built_in_parser and equivalent_built_in_parser.endswith('_Native'):
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
            results.append((f'{RED}{parser_name}{RESET}', f'{RED}Parser entry not found in union parser under "ParserQuery" property{RESET}', f'{RED}Fail{RESET}'))

    # Check if equivalent_built_in_parser exists in another_yaml_file's 'Parsers'
    if equivalent_built_in_parser:
        if equivalent_built_in_parser in Union_Parser__file.get('Parsers', []):
            results.append((equivalent_built_in_parser, 'Parser entry exists in union parser under "Parsers" property', 'Pass'))
        else:
            results.append((f'{RED}{equivalent_built_in_parser}{RESET}', f'{RED}Parser entry not found in union parser under "Parsers" property{RESET}', f'{RED}Fail{RESET}'))

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
            results.append((f'{RED}{version}{RESET}', f'{RED}The parser version should be in a three-digit format, e.g., 0.1.0{RESET}', f'{RED}Fail{RESET}'))
    else:
        results.append((f'{RED}Version{RESET}', f'{RED}Parser version not found in parser YAML{RESET}', f'{RED}Fail{RESET}'))

    # Check if last_updated exists in yaml_file's 'Parser'->'LastUpdated' and matches the format MMM DD YY
    if last_updated:
        try:
            datetime.strptime(last_updated, '%b %d, %Y')
            results.append((last_updated, 'This value exist in LastUpdated property', 'Pass'))
        except ValueError:
            results.append((f'{RED}{last_updated}{RESET}', f'{RED}"LastUpdated" property exists but is not correct format. The expected format is, for example, "Jun 29, 2024"{RESET}', f'{RED}Fail{RESET}'))
    else:
        results.append((f'{RED}LastUpdated{RESET}', f'{RED}LastUpdated not found in parser YAML{RESET}', f'{RED}Fail{RESET}'))
    
    # Check if schema exists in yaml_file's 'Normalization'->'Schema' and matches with our SchemaInfo
    if schema:
        schema_found = False
        for info in SCHEMA_INFO:
            if info['SchemaName'] == schema:
                results.append((schema, f'ASIM schema name "{schema}" is correct', 'Pass'))
                schema_found = True
                break
        if not schema_found:
            results.append((f'{RED}{schema}{RESET}', f'{RED}ASIM schema name "{schema}" is incorrect. Please re-check Schema name{RESET}', f'{RED}Fail{RESET}'))
    else:
        results.append((f'{RED}Schema{RESET}', f'{RED}ASIM schema name not found in parser YAML{RESET}', f'{RED}Fail{RESET}'))
    
    # Check if Schema Version exists in yaml_file's 'Normalization'->'Schema' and matches with our SchemaInfo
    if schemaVersion:
        version_found = False
        for info in SCHEMA_INFO:
            if schema == info.get('SchemaName'):
                if info['SchemaVersion'] == schemaVersion and info['SchemaName'] == schema:
                    schema_name = info.get('SchemaName')
                    results.append((schemaVersion, f'ASIM schema {schema_name} version is correct', 'Pass'))
                    version_found = True
                    break
                else:
                    schema_version = info['SchemaVersion']
                    results.append((f'{RED}{schemaVersion}{RESET}', f'{RED}ASIM schema "{schema}" version "{schemaVersion}" is incorrect. The correct version for ASIM schema "{schema}" is "{schema_version}"{RESET}', f'{RED}Fail{RESET}'))
                    version_found = True
                    break
        if not version_found:
            results.append((f'{RED}Version{RESET}', f'{RED}ASIM schema {schema} version not found in parser YAML{RESET}', f'{RED}Fail{RESET}'))
    else:
        results.append((f'{RED}Version{RESET}', f'{RED}ASIM schema version not found in parser YAML{RESET}', f'{RED}Fail{RESET}'))

    # Check if references exist in yaml_file's 'References'
    if references:
        for ref in references:
            ref_title = ref.get('Title')
            link = ref.get('Link')

            ref_found = False
            for info in SCHEMA_INFO:
                titleSchemaInfo = info.get('SchemaTitle')
                linkSchemaInfo = info.get('SchemaLink')
                if schema == info.get('SchemaName'):
                    if ref_title == titleSchemaInfo and link == linkSchemaInfo:
                        results.append((ref_title, 'Schema specific reference link matching', 'Pass'))
                        ref_found = True
                    elif ref_title == 'ASIM' and link == 'https://aka.ms/AboutASIM':
                        results.append((ref_title, 'ASim doc reference link matching', 'Pass'))
                        ref_found = True
                    elif ref_title != 'ASIM' and ref_title != titleSchemaInfo:
                        results.append((ref_title, 'Product specific reference title exist. Please access URL manually to confirm it is a valid link', 'Pass'))
                        ref_found = True
                    break
            
            if not ref_found and ref_title:
                results.append((f'{RED}{ref_title}{RESET}', f'{RED}Reference title or link not matching. Please check reference information{RESET}', f'{RED}Fail{RESET}'))
    else:
        results.append((f'{RED}References{RESET}', f'{RED}References not found in parser YAML{RESET}', f'{RED}Fail{RESET}'))

    # Check if ParserName exists in yaml_file and matches the format ASIMAuditEvent<ProductName>
    if parser_name:
        if re.match(rf'{FileType}{schema}', parser_name):
            results.append((parser_name, 'ParserName is in correct format', 'Pass'))
        else:
            if "vim" in parser_name:
                parser_name_with_asim = parser_name.replace("vim", "ASim", 1)
                if not re.match(rf'{FileType}{schema}', parser_name_with_asim):
                    results.append((f'{RED}{parser_name}{RESET}', f'{RED}ParserName is not in correct format{RESET}', f'{RED}Fail{RESET}'))
            else:
                results.append((f'{RED}{parser_name}{RESET}', f'{RED}ParserName is not in correct format{RESET}', f'{RED}Fail{RESET}'))
    else:
        results.append((f'{RED}ParserName{RESET}', f'{RED}ParserName not found{RESET}', f'{RED}Fail{RESET}'))

    # Check if EquivalentBuiltInParser exists in yaml_file and matches the format _ASIM_<Schema><ProductName>
    file_type_adjusted = "Im" if FileType == "vim" else FileType
    if equivalent_built_in_parser:
        if re.match(rf'_{file_type_adjusted}_{schema}_', equivalent_built_in_parser):
            results.append((equivalent_built_in_parser, 'EquivalentBuiltInParser is in correct format', 'Pass'))
        else:
            if not "_Im_" in equivalent_built_in_parser:
                results.append((f'{RED}{equivalent_built_in_parser}{RESET}', f'{RED}EquivalentBuiltInParser is not in correct format. The correct format is "_{file_type_adjusted}_{schema}_ProductName"{RESET}', f'{RED}Fail{RESET}'))
            else:
                results.append((f'{RED}{equivalent_built_in_parser}{RESET}', f'{RED}EquivalentBuiltInParser is not in correct format. The correct format is "_{file_type_adjusted}_{schema}_ProductName"{RESET}', f'{RED}Fail{RESET}'))
    else:
        results.append((f'{RED}EquivalentBuiltInParser{RESET}', f'{RED}"EquivalentBuiltInParser" property not found in parser{RESET}', f'{RED}Fail{RESET}'))
    
    # Check if sample data files exists or not (Only applicable for ASim FileType)
    if FileType == "ASim" and ASIMSampleDataURL:
        # construct filename
        SampleDataFile = f'{event_vendor}_{event_product}_{schema}_IngestedLogs.csv'
        
        if SampleDataFile.lower() in ASIMSampleDataURL.lower():
            print("{SampleDataFile} is present in the sample data URL {ASIMSampleDataURL}")
        else:
            print(f"{RED}Sample data file {SampleDataFile} is not present in the sample data URL {ASIMSampleDataURL}. Expected Sample Data file name is {SampleDataFile}{RESET}")
            results.append((f'{RED}Expected sample file not found{RESET}', f'{RED}Sample data file does not exist or may not be named correctly. Please include sample data file "{event_vendor}_{event_product}_{schema}_IngestedLogs.csv"{RESET}', f'{RED}Fail{RESET}'))
            #exit(1)
        
        # SampleDataUrl = ASIMSampleDataURL + SampleDataFile
        # # check if file exists
        # try:
        #     response = requests.get(SampleDataUrl)
        #     if response.status_code == 200:
        #         results.append((SampleDataFile, 'Sample data file exists', 'Pass'))
        #     else:
        #         results.append((f'{RED}Expected sample file not found{RESET}', f'{RED}Sample data file does not exist or may not be named correctly. Please include sample data file "{event_vendor}_{event_product}_{schema}_IngestedLogs.csv"{RESET}', f'{RED}Fail{RESET}'))
        # except Exception as e:
        #     results.append((f'{RED}Sample data check failed{RESET}', f'{RED}Could not check sample data file: {str(e)}{RESET}', f'{RED}Fail{RESET}'))
    
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


def extract_base_folder_path(file_path):
    """
    Extract the base folder path from the start up to 'Parsers' directory.
    
    Args:
        file_path (str): Full file path
        
    Returns:
        str: Base folder path up to 'Parsers' directory, or None if 'Parsers' not found
    """
    # Normalize the path separators
    normalized_path = file_path.replace('\\', '/')
    
    # Find the index of 'Parsers' in the path
    parsers_index = normalized_path.find('/Parsers/')
    
    if parsers_index != -1:
        # Extract everything up to and including 'Parsers'
        base_path = normalized_path[:parsers_index + len('/Parsers')]
        return base_path
    else:
        # If 'Parsers' directory not found, try alternative patterns
        parsers_index = normalized_path.find('\\Parsers\\')
        if parsers_index != -1:
            base_path = normalized_path[:parsers_index + len('\\Parsers')]
            return base_path.replace('\\', '/')
    
    return None

def get_relative_parser_path(file_path, base_folder_path):
    """
    Get the relative path from the base folder.
    
    Args:
        file_path (str): Full file path
        base_folder_path (str): Base folder path
        
    Returns:
        str: Relative path from base folder
    """
    normalized_file_path = file_path.replace('\\', '/')
    normalized_base_path = base_folder_path.replace('\\', '/')
    
    if normalized_file_path.startswith(normalized_base_path):
        # Remove the base path and leading slash
        relative_path = normalized_file_path[len(normalized_base_path):].lstrip('/')
        return relative_path
    
    return file_path

def extract_schema_name(parser):
    parser = parser.replace('\\', '/')
    match = re.search(r'ASim(\w+)/', parser)
    return match.group(1) if match else None

def read_yaml_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    return data

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

def check_test_failures(results, parser, base_folder_path=None):
    if any(result[-1] == f'{RED}Fail{RESET}' for result in results):
        print("Some tests failed for Parser. Please check the results above.")
        try:
            base_root_folder_path = base_folder_path.replace('Parsers/', '')
            exclusion_list = read_exclusion_list_from_csv()
            parser_name = parser.get('EquivalentBuiltInParser') if parser else 'Unknown'
            if parser_name in exclusion_list:
                print(f"The parser {parser_name} is listed in the exclusions file, so this validation will show as warning only.")
                print(f"To allow this parser to trigger a failure, please remove its name from the exclusions list file located at: {parser_exclusion_file_path}")
                return True  # Return True to indicate warning only
            else:
                return False  # Return False to indicate failure
        except Exception as e:
            print(f"Could not read exclusion list: {e}")
            return False
    else:
        print(f"{GREEN}All tests successfully passed for this parser.{RESET}")
        return True

def check_parser_found(asim_parser,parser_url):
    if asim_parser is None:
        print(f"Parser file not found. Please check the URL and try again: {parser_url}")
        return False
    else:
        return True

def get_vim_parsers(asim_parser_url, asim_union_parser_url, asim_parser):
    asim_parser_url = asim_parser_url.replace('\\', '/')
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
    vim_parser = read_yaml_file(vim_parser_url) #read_github_yaml(vim_parser_url)
    vim_union_parser = read_yaml_file(vim_union_parser_url) #read_github_yaml(vim_union_parser_url)
    return vim_parser, vim_union_parser

# Function to read Exclusion list for ASim Parser test from a CSV file
def read_exclusion_list_from_csv():
    exclusion_list = []
    try:
        if os.path.exists(parser_exclusion_file_path):
            with open(parser_exclusion_file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row:  # Check if row is not empty
                        exclusion_list.append(row[0])
        else:
            print(f"Exclusion file not found: {parser_exclusion_file_path}")
    except Exception as e:
        print(f"Error reading exclusion file: {e}")
    return exclusion_list

# Add new function for local validation
def run_local_validation(sample_file_path, parser_file_path=None, parser_type="ASim"):
    """Function to run validation locally with provided file paths."""
    print()
    print(f"{GREEN}Running {parser_type} parser validation{RESET}")
    
    if parser_file_path and os.path.exists(parser_file_path):
        print(f"{GREEN}Using parser file: {parser_file_path}{RESET}")
        
        # Read parser file
        with open(parser_file_path, 'r', encoding='utf-8') as file:
            parser_content = yaml.safe_load(file)
        
        # Create mock union parser for local testing
        union_parser = {
            'ParserQuery': parser_content.get('ParserName', ''),
            'Parsers': [parser_content.get('EquivalentBuiltInParser', '')]
        }
        
        print_test_header(f"{parser_content.get('EquivalentBuiltInParser')} ({parser_type})")
        
        # Perform actual validation instead of skipping
        results = extract_and_check_properties(parser_content, union_parser, parser_type, parser_file_path, "")
        
        # Add local-specific validations
        local_results = perform_local_specific_validations(parser_content, parser_file_path, parser_type)
        results.extend(local_results)
        
        print_results_table(results)
        
        # Check for failures but don't exit
        failures = [result for result in results if result[-1] == f'{RED}Fail{RESET}']
        warnings = [result for result in results if result[-1] == 'Warning']
        
        if failures:
            print(f"{RED}❌ {parser_type} parser validation failed with {len(failures)} error(s){RESET}")
            print(f"{RED}Issues found:{RESET}")
            for failure in failures:
                print(f"  - {failure[1]}")
            return False
        elif warnings:
            print(f"{YELLOW}⚠️ {parser_type} parser validation completed with {len(warnings)} warning(s){RESET}")
            print(f"{GREEN}✅ No critical errors found{RESET}")
            return True
        else:
            print(f"{GREEN}✅ All {parser_type} parser validations passed{RESET}")
            return True
    else:
        print(f"{YELLOW}No {parser_type} parser file provided or file not found{RESET}")
        return True

def perform_local_specific_validations(parser_content, parser_file_path, parser_type):
    """Perform additional local validations that don't require Azure connectivity"""
    results = []
    
    # Add parser type-specific validations
    results.append((f'{GREEN}Parser Type{RESET}', f'Validating {parser_type} parser', 'Pass'))
    
    # Validate naming conventions specific to parser type
    parser_name = parser_content.get('ParserName', '')
    if parser_name:
        if parser_type == "ASim":
            if parser_name.startswith('ASim'):
                results.append((f'{GREEN}ASim Naming{RESET}', 'ASim parser name follows naming convention', 'Pass'))
            else:
                results.append((f'{RED}ASim Naming{RESET}', f'{RED}ASim parser name should start with "ASim"{RESET}', f'{RED}Fail{RESET}'))
        elif parser_type == "vim":
            if parser_name.startswith('vim'):
                results.append((f'{GREEN}vim Naming{RESET}', 'vim parser name follows naming convention', 'Pass'))
            else:
                results.append((f'{RED}vim Naming{RESET}', f'{RED}vim parser name should start with "vim"{RESET}', f'{RED}Fail{RESET}'))
    
    # Validate EquivalentBuiltInParser naming
    equiv_parser = parser_content.get('EquivalentBuiltInParser', '')
    if equiv_parser:
        if parser_type == "ASim":
            if equiv_parser.startswith('_ASim_'):
                results.append((f'{GREEN}ASim BuiltIn Naming{RESET}', 'ASim EquivalentBuiltInParser follows naming convention', 'Pass'))
            else:
                results.append((f'{RED}ASim BuiltIn Naming{RESET}', f'{RED}ASim EquivalentBuiltInParser should start with "_ASim_"{RESET}', f'{RED}Fail{RESET}'))
        elif parser_type == "vim":
            if equiv_parser.startswith('_Im_'):
                results.append((f'{GREEN}vim BuiltIn Naming{RESET}', 'vim EquivalentBuiltInParser follows naming convention', 'Pass'))
            else:
                results.append((f'{RED}vim BuiltIn Naming{RESET}', f'{RED}vim EquivalentBuiltInParser should start with "_Im_"{RESET}', f'{RED}Fail{RESET}'))
    
    # Validate KQL query syntax
    parser_query = parser_content.get('ParserQuery', '')
    if parser_query:
        kql_results = validate_kql_syntax(parser_query, parser_type)
        results.extend(kql_results)
    
    # Validate file structure
    file_results = validate_file_structure(parser_content, parser_file_path)
    results.extend(file_results)
    
    # Validate ASIM compliance
    asim_results = validate_asim_compliance(parser_content)
    results.extend(asim_results)
    
    return results

def validate_kql_syntax(query, parser_type):
    """Validate basic KQL syntax and structure"""
    results = []
    
    if not query or query.strip() == '':
        results.append((f'{RED}Empty Query{RESET}', f'{RED}{parser_type} parser query is empty{RESET}', f'{RED}Fail{RESET}'))
        return results
    
    # Check for basic KQL structure
    if '|' in query:
        results.append((f'{GREEN}KQL Structure{RESET}', f'{parser_type} query contains pipe operators (valid KQL structure)', 'Pass'))
    else:
        results.append((f'{YELLOW}KQL Structure{RESET}', f'{parser_type} query may not contain pipe operators', 'Warning'))
    
    # Check for common KQL functions
    kql_functions = ['where', 'project', 'extend', 'summarize', 'join', 'union']
    found_functions = [func for func in kql_functions if func in query.lower()]
    
    if found_functions:
        results.append((f'{GREEN}KQL Functions{RESET}', f'{parser_type} query found KQL functions: {", ".join(found_functions)}', 'Pass'))
    else:
        results.append((f'{YELLOW}KQL Functions{RESET}', f'{parser_type} query - no common KQL functions found', 'Warning'))
    
    # Check for ASIM required fields in query
    required_fields = ['TimeGenerated', 'EventProduct', 'EventVendor']
    missing_fields = []
    
    for field in required_fields:
        if field not in query:
            missing_fields.append(field)
    
    if not missing_fields:
        results.append((f'{GREEN}Required Fields{RESET}', f'{parser_type} query - all required ASIM fields found', 'Pass'))
    else:
        results.append((f'{YELLOW}Required Fields{RESET}', f'{parser_type} query - some required fields may be missing: {", ".join(missing_fields)}', 'Warning'))
    
    # Check query length (complexity indicator)
    if len(query) > 100:
        results.append((f'{GREEN}Query Complexity{RESET}', f'{parser_type} query has reasonable complexity ({len(query)} characters)', 'Pass'))
    else:
        results.append((f'{YELLOW}Query Complexity{RESET}', f'{parser_type} query seems simple ({len(query)} characters)', 'Warning'))
    
    return results

def validate_file_structure(parser_content, file_path):
    """Validate the overall file structure and required properties"""
    results = []
    
    # Check for required top-level properties
    required_props = ['ParserName', 'EquivalentBuiltInParser', 'Parser', 'Normalization', 'ParserQuery']
    
    for prop in required_props:
        if prop in parser_content:
            results.append((f'{GREEN}{prop}{RESET}', f'Required property {prop} is present', 'Pass'))
        else:
            results.append((f'{RED}{prop}{RESET}', f'{RED}Required property {prop} is missing{RESET}', f'{RED}Fail{RESET}'))
    
    # Validate nested Parser properties
    parser_section = parser_content.get('Parser', {})
    parser_props = ['Title', 'Version', 'LastUpdated']
    
    for prop in parser_props:
        if prop in parser_section:
            results.append((f'{GREEN}Parser.{prop}{RESET}', f'Parser property {prop} is present', 'Pass'))
        else:
            results.append((f'{RED}Parser.{prop}{RESET}', f'{RED}Parser property {prop} is missing{RESET}', f'{RED}Fail{RESET}'))
    
    # Validate Normalization properties
    normalization = parser_content.get('Normalization', {})
    norm_props = ['Schema', 'Version']
    
    for prop in norm_props:
        if prop in normalization:
            results.append((f'{GREEN}Normalization.{prop}{RESET}', f'Normalization property {prop} is present', 'Pass'))
        else:
            results.append((f'{RED}Normalization.{prop}{RESET}', f'{RED}Normalization property {prop} is missing{RESET}', f'{RED}Fail{RESET}'))
    
    return results

def validate_asim_compliance(parser_content):
    """Validate ASIM-specific compliance requirements"""
    results = []
    
    # Check parser naming convention
    parser_name = parser_content.get('ParserName', '')
    if parser_name:
        if re.match(r'^(ASim|vim)[A-Z]', parser_name):
            results.append((f'{GREEN}Naming Convention{RESET}', 'Parser name follows ASIM naming convention', 'Pass'))
        else:
            results.append((f'{YELLOW}Naming Convention{RESET}', 'Parser name may not follow ASIM naming convention', 'Warning'))
    
    # Check equivalent built-in parser naming
    equiv_parser = parser_content.get('EquivalentBuiltInParser', '')
    if equiv_parser:
        if re.match(r'^_(ASim|Im)_[A-Z]', equiv_parser):
            results.append((f'{GREEN}BuiltIn Parser Name{RESET}', 'EquivalentBuiltInParser follows naming convention', 'Pass'))
        else:
            results.append((f'{YELLOW}BuiltIn Parser Name{RESET}', 'EquivalentBuiltInParser may not follow naming convention', 'Warning'))
    
    # Check schema version format
    normalization = parser_content.get('Normalization', {})
    schema_version = normalization.get('Version', '')
    if schema_version:
        if re.match(r'^\d+\.\d+(\.\d+)?$', schema_version):
            results.append((f'{GREEN}Schema Version Format{RESET}', 'Schema version format is valid', 'Pass'))
        else:
            results.append((f'{RED}Schema Version Format{RESET}', f'{RED}Schema version format is invalid: {schema_version}{RESET}', f'{RED}Fail{RESET}'))
    
    return results

# Script starts here
if __name__ == "__main__":
    run()