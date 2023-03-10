import sys
import yamale
import json
import os
import copy
from pathlib import Path
import argparse
import logging
import urllib.parse

sys.tracebacklimit = 0

# SETUP
# -- Get directories
scriptdir = os.path.dirname(os.path.realpath(__file__))
cwd = os.getcwd()

# -- Parsing Command Line Arguments
parser = argparse.ArgumentParser(description='Generates ARM templates from a folder of KQL function YAML files.')
parser.add_argument('-m', '--mode', type=str, default='files', metavar='package, file or asim', dest='mode',
                    help='Select the mode:\n "files" to translate each input YAML files to an ARM template. "package" to create a full deployment package including readme files and a full deployment template. "asim" to create a full package using ASIM specific templates. "asimdev" to create a test ASIM package. Defaults to "files".')
parser.add_argument(
        'folders', nargs='*',  type=str, metavar='files and folders',   
        help='List of YAML files and folders to process. For folders, each YAML file in the folder will be converted.'
)
parser.add_argument('-d', '--dest', type=str, default='ARM', metavar='destination folder', dest='dest',
                    help='The output folder. Defaults to the ARM subdirectory of the current working directory.')
parser.add_argument('-t', '--templates', type=str, default=scriptdir, metavar='templates folder', dest='templates_dir',
                    help='The path of the templates for ARM templates and readme files. Defaults to the script directory')
parser.add_argument('-b', '--branch', type=str, default='#', metavar='branch', dest='branch',
                    help='For asim mode, the ARM templates links in the full deployment and readme files point to this github branch. The Github repository itself is embedded in the template files. Defaults to "master".')
parser.add_argument('-u', '--uri', type=str, default='#', metavar='uri', dest='uri',
                    help='For package mode, the based uri under which the package will be available. Used to generate the full deployment and readme files. If using package mode, this field is mandatory and has no default.')
parser.add_argument('-l', '--loglevel', default="warning",  metavar='debug', dest='loglevel', help='Specify the logging level.Defaults to warning.')
args = parser.parse_args()
dest = os.path.join (cwd, args.dest)
templates_dir = os.path.abspath(args.templates_dir)
Uri = args.uri
Branch = args.branch

# -- Set mode and related parameters
modes = {
    'package': True,
    'files': False,
    'asim': True,
    'asimdev': True
}
package_type = args.mode.lower()
package_mode = modes.get(package_type)
if package_mode is None:
    raise SystemExit(f"Error: The node {args.mode} is not valid. Must be one of: {' | '.join(modes.keys())}")

if Uri == "#" and package_type == "package":
    raise SystemExit("Error: Specifying a uri is mandatory in package mode")

if Uri != "#" and package_type != "package":
    raise SystemExit("Error: The uri parameter should be used only in package mode")

encoded_uri = urllib.parse.quote(Uri, safe='')

if Branch != "#" and package_type not in ["asim", "asimdev"]:
        raise SystemExit("Error: The branch parameter should be used only in the asim or asimdev modes")

if Branch == "#":
        Branch = "master"

encoded_branch = urllib.parse.quote(Branch, safe='')

# -- Set logging level
levels = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warn': logging.WARNING,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}
level = levels.get(args.loglevel.lower())
if level is None:
    raise SystemExit(f"Error: The logging level {args.loglevel} is not valid. Must be one of: {' | '.join(levels.keys())}")
logging.basicConfig(level=level)
logger = logging.getLogger(__name__)
if level == logging.DEBUG:
    sys.tracebacklimit = 1

logging.info (f'Template directory is {templates_dir}.')

# -- Generate file list from file and folder parameters
folders = args.folders

if len(folders) == 0: # -- use current working directory as default if not files are listed
    folders = [cwd]

files = []
logging.info (f'Inspecting files and folders {folders}.')
for f in folders:
    f = os.path.abspath(f)
    if Path(f).is_file():
        logging.debug (f'Adding file {f}.')      
        if not(f.endswith('.yaml')):
            logging.debug (f'{f} is not a YAML file.')
        else:
            files.append(f)
    elif Path(f).exists():
        logging.debug (f'Adding folder {f}.')      
        for file in os.listdir(f):
            file = os.path.join (f, file)
            logging.debug (f'Adding file {file}.')  
            if Path(file).is_file():
                if not(file.endswith('.yaml')):
                    logging.debug (f'{file} is not a YAML file.')
                else:
                    files.append(file)
    else:
        logging.warning (f'File or folder "{f}" does not exist.')

files = sorted(list(dict.fromkeys(files))) # -- remove duplicates

if len(files) == 0:
    raise SystemExit ('No files to process.')

# -- Read and prepare templates
func_arm_template = json.load(open(os.path.join(templates_dir, 'func_arm_template.json'), 'r'))
if package_mode:
    package_arm_template = json.load(open(os.path.join(templates_dir, f'{package_type}_arm_template.json'), 'r'))
    generic_element_template = (package_arm_template['resources']).pop()
    template_uri = generic_element_template['properties']['templateLink']['uri']

# -- Loop through files to generate ARM
package_schema = ""

logging.info (f'Destination folder is: {dest}')
for f in files:
    logging.info (f'Converting YAML file: {f}')

    try:
        [folder, f] = os.path.split(f)
        fname = f[:-5]

        logging.debug ('Parsing XML')
        # parse the YAML file
        parserYaml = yamale.make_data(os.path.join(folder, f))
        try:
            Title = parserYaml[0][0]["Parser"]["Title"]
        except:
            try:
                FunctionMode = True
                Title = parserYaml[0][0]["Function"]["Title"]
            except:
                 raise SystemExit (f"Error: file {f} does not specify a parser or function title.")

        try:
            Alias = parserYaml[0][0]["ParserName"]
        except:
            try:
                Alias = parserYaml[0][0]["FunctionName"]
            except:
                 raise SystemExit (f"Error: file {f} does not specify a parser or function name.")
           
        try:
             Query = parserYaml[0][0]["ParserQuery"]
        except:
            try:
                 Query = parserYaml[0][0]["FunctionQuery"]
            except:
                 raise SystemExit (f"Error: file {f} does not specify a parser or function query.")
        
        try:
             Product = parserYaml[0][0]["Product"]["Name"]
        except:
            Product = ""
            if not(FunctionMode):
                raise SystemExit (f"Error: file {f} does not specify a parser product name.")
       
        try:
            Description = parserYaml[0][0]["Description"]
        except:
            raise SystemExit (f"Error: file {f} does not specify a description.")

        try:
            Schema = parserYaml[0][0]["Normalization"]["Schema"]
        except:
            Schema = ""
            logging.info (f"No schema in YAML file {f}.")

        try:
            Category = parserYaml[0][0]["Category"]
        except:
            Category = "ASIM" # -- should not be hardcoded
    
        if Schema != "":
            if package_type == 'asim' and package_schema != "" and package_schema != Schema:
                raise SystemExit(f"Error: schema in file {f} is inconsistent with asim package schema.")
            package_schema = Schema

        params = parserYaml[0][0].get("ParserParams")
        if not(params):
            params = parserYaml[0][0].get("FunctionParams")            

        logging.debug ('Generating ARM template')
        # generate the ARM template
        armTemplate = copy.deepcopy(func_arm_template)
        armTemplate['resources'][0]['resources'][0]['name'] = Alias
        armTemplate['resources'][0]['resources'][0]['properties']['query'] = Query
        armTemplate['resources'][0]['resources'][0]['properties']['category'] = Category
        if params:
            Parameters = ""
            for param in params:
                logging.debug("Param: " + str(param))
                if param['Type'].startswith('table:'):
                    ParamString = f'{param["Name"]}:{param["Type"].split(":",1)[1]}'
                else:
                    try:
                        Default = param["Default"] 
                        if param['Type']=='string':
                            Default = f"\'{Default}\'"
                        ParamString = f'{param["Name"]}:{param["Type"]}={Default}'
                    except:
                        ParamString = f'{param["Name"]}:{param["Type"]}'
                if Parameters != "":
                    Parameters = f'{Parameters},'
                Parameters = Parameters + ParamString
            armTemplate['resources'][0]['resources'][0]['properties']['functionParameters'] =  Parameters
        armTemplate['resources'][0]['resources'][0]['properties']['FunctionAlias'] = Alias
        armTemplate['resources'][0]['resources'][0]['properties']['displayName'] = Title

        logging.debug ('Writing ARM template')
        # Write template
        if package_mode:
            output_folder = os.path.join(dest, fname)
        else:
            output_folder = dest
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        output_filename = os.path.join(output_folder, f'{fname}.json')
        logging.info (f'Writing json file: {fname}.json')
        with open(os.path.join(output_folder, output_filename), 'w') as jf:
            json.dump(armTemplate, jf, indent=2)

        if package_mode:
            logging.debug ('Generating readme (folder mode only)')
            # generate readme
            readme = open(os.path.join(templates_dir, f'{package_type}_func_readme.md'), 'r').read()
            with open(os.path.join(output_folder, 'README.md'), 'w') as rmf:
                    rmf.write(readme.format(branch=encoded_branch, schema=Schema, filename=fname, product=Product, description=Description, uri=encoded_uri, title=Title))

            logging.debug ('Appending to full deployment (folder mode only)')
            # Add to full deployment 
            genericTemplate_element = copy.deepcopy(generic_element_template)
            genericTemplate_element['name'] = f'linked{fname}'
            formated_uri = template_uri.format(branch=Branch, schema='{schema}', filename=fname, uri=Uri)
            genericTemplate_element['properties']['templateLink']['uri'] =  formated_uri
            package_arm_template['resources'].append(genericTemplate_element)

    except Exception as E:
        raise SystemExit(f'Convertion of {f} failed:{E}')

if package_mode:
    if package_schema == "NA":
        package_schema = "Package"
    logging.debug (f'Generating full deployment for schema {package_schema} (folder mode only)')
    json_txt = json.dumps(package_arm_template, indent=2)
    with open(os.path.join(dest, f'FullDeployment{package_schema}.json'), 'w') as jf:
        jf.write(json_txt.replace('{schema}', package_schema))

    logging.debug ('Generating full deployment readme (folder mode only)')
    with open(os.path.join(templates_dir, f'{package_type}_readme.md'), 'r') as fdr:
        package_readme = fdr.read().format (schema=package_schema, uri=encoded_uri, branch=encoded_branch)
        with open(os.path.join(dest, 'README.md'), 'w') as rm:
            rm.write(package_readme)