import json
import yaml
import sys
import os
import uuid
from functools import partial
import re

PARSER_PARAMS = "${kind}Params"

EXCLUDE_PREFIX = "Exclude"

FUNCTIONS_LIST_TEMPLATE = '''[
${values}
]
'''

FUNCTION_TEMPLATE = '''{
    "id": "",
    "name": "",
    "parameters": "",
    "description": "",
    "bodyFilePath": "",
    "solutions": [],
    "tags": { 
    },  
    "properties": {
    }
}
'''

FUNCTION_PARAMETERS_TEMPLATE = "${name}= ${name}"
FUNCTION_PARAMETERS_TEMPLATE_WITHOUT_DEFAULT = "${name}:${type}"
FUNCTION_PARAMETERS_TEMPLATE_WITH_DEFAULT = "${name}:${type} = '${default}'"

MAIN_FUNCTION_QUERY_TEMPLATE = '''union isfuzzy=true
_${name}BuiltIn${params},
${name}Solutions${params},
${name}Custom${params}
'''

SECONDARY_MAIN_FUNCTION_QUERY_TEMPLATE_V2 = '''let DisabledParsers=materialize(_GetWatchlist('ASimDisabledParsers') 
| where SearchKey in ('Any', '${exclude}${name}') 
| extend SourceSpecificParser=column_ifexists('SourceSpecificParser','') 
| where isnotempty(SourceSpecificParser) 
| summarize list = make_set(SourceSpecificParser));
let builtInDisabled = 0 != array_length(set_intersect(toscalar(DisabledParsers),dynamic(['${exclude}${built_in_name}', '${exclude}${name}', 'Any'])));
union isfuzzy=true
${related_parsers}
'''

SECONDARY_MAIN_FUNCTION_QUERY_TEMPLATE = '''union isfuzzy=true
    ${related_parsers}
'''

KQL_DIRECTORY = "content/NGSchemas/SentinelAsim/KQL"

def create_parser_name_for_disable_parameter(parser_name):
    return "'"+ EXCLUDE_PREFIX + parser_name + "'"

def create_function_name_from_parser_name_and_version(parser_name, version=''):
    version_array = version.split('.')
    return parser_name + "V" + version_array[0] + version_array[1]


def create_function_parameters(parameters, with_default=False):
    return_params = []
    for param in parameters:
        hasDefault = 'Default' in param
        param_string = FUNCTION_PARAMETERS_TEMPLATE_WITH_DEFAULT.replace(
            '${name}', param['Name']).replace('${type}', param['Type'])
        if(with_default == False):
            param_string = FUNCTION_PARAMETERS_TEMPLATE.replace('${name}', param['Name'])
        elif(hasDefault == False):
            param_string = FUNCTION_PARAMETERS_TEMPLATE_WITHOUT_DEFAULT.replace('${name}', param['Name']).replace('${type}', param['Type'])
        elif((param['Type'] == "string")):
            param_string = param_string.replace('${default}', param['Default'])
        else:
            param_string = param_string.replace(
                "'${default}'", str(param['Default']).lower())
        if (param['Type'] == "table:(*)"):
            param_string = param_string.replace(':table', "")
        return_params.append(param_string)
    return ', '.join(return_params)

class Parser:
    def __init__(self, schema, parameters_file, kind = "Parser"):
        self.parameters_file = parameters_file
        self.schema = schema
        self.kind = kind
        self.name_with_version = ''
        self.description = ''
        self.ignoreTimespanOnDimensionTables = ''
        self.parameters = []
        self.query = ''

    # pass parameters in the __init__ phase and remove this
    def init_parser(self):
        with open(self.parameters_file, 'r') as stream:
            parsed_yaml = yaml.safe_load(stream)
        self.name = parsed_yaml["EquivalentBuiltIn" + self.kind]
        version = parsed_yaml[self.kind]["Version"]
        self.name_with_version = create_function_name_from_parser_name_and_version(self.name, version) if self.kind == "Parser"  else self.name                           
        self.description = parsed_yaml[self.kind]["Title"].rstrip()
        self.query = parsed_yaml[self.kind + "Query"]
        self.ignoreTimespanOnDimensionTables = parsed_yaml.get("IgnoreTimespanOnDimensionTables", "")
        paramsKey = PARSER_PARAMS.replace('${kind}', self.kind)
        if(paramsKey in parsed_yaml):
            self.parameters = parsed_yaml[paramsKey]


    def create_query_file(self, name, query, subfolder_path):
        def helper(dic, match):
            word = match.group(0)
            return dic.get(word, word)
        word_re = re.compile(r'\b[0-9a-zA-Z_]+\b')
        query = word_re.sub(partial(helper, PARSERS_NAMES), query)
        current_dir = os.getcwd()
        base_folder = sys.argv[1]
        path = base_folder + '/' + subfolder_path
        if not os.path.exists(path):
             os.makedirs(path)
        os.chdir(path)

        with open(name + '.kql', 'w') as file:
            file.write(query)
        os.chdir(current_dir)


    def create_la_function(self, name=''):
        function_name = self.name if name == '' else name
        function_body = json.loads(FUNCTION_TEMPLATE)
        function_body['id'] = str(uuid.uuid5(uuid.NAMESPACE_OID, function_name))
        function_body['name'] = function_name
        function_body['description'] = self.description if self.description.endswith(".") else self.description + "."
        if (function_name.endswith("BuiltIn")):
            function_body['description'] = function_body['description'].replace("ASIM parser", "ASIM built-in union parser").replace("ASIM filtering parser", "ASIM built-in union parser")
        function_body['solutions'] = ["SecurityInsights"]
        if (self.ignoreTimespanOnDimensionTables != ""):
            function_body['ignoreTimespanOnDimensionTables'] = self.ignoreTimespanOnDimensionTables
        function_body['parameters'] = create_function_parameters(
            self.parameters, True)
        if (self.kind == "Function"):
            function_body['bodyFilePath'] = "KQL/Common/" + function_name + ".kql"
        else:
            function_body['bodyFilePath'] =  "KQL/" + self.schema + "/" + function_name + ".kql"
               
        return function_body

class Main_Parser(Parser):
    def __init__(self, schema, parameters_file):
        Parser.__init__(self, schema, parameters_file)
        self.parsers_names = []
        self.parsers = []
        self.secondary_main_name = ''
        self.secondary_main_query = ''
        self.description = ''
        self.kind = "Parser"
    
    def set_parsers(self, parsers):
        self.parsers = parsers

    def init_parser(self):
        with open(self.parameters_file, 'r') as stream:
            parsed_yaml = yaml.safe_load(stream)

        self.name = parsed_yaml["EquivalentBuiltInParser"]
        self.secondary_main_name = self.name + "BuiltIn"
        self.description = parsed_yaml["Parser"]["Title"].rstrip()

        paramsKey = PARSER_PARAMS.replace('${kind}', self.kind)
        if(paramsKey in parsed_yaml):
            self.parameters = parsed_yaml[paramsKey]

        self.parsers_names = parsed_yaml["Parsers"]
        self.create_query()
        self.create_secondary_main_query()

    def create_query(self):
        parameters = '' if self.parameters == [
        ] else '(' + create_function_parameters(self.parameters) + ')'
        self.query = MAIN_FUNCTION_QUERY_TEMPLATE.replace(
            '${name}', self.name[1:]).replace('${params}', parameters)

    def create_secondary_main_query(self):
        parsers = [
            parser.name_with_version + self.get_parser_parameters_query(parser.name, parser.parameters) for parser in self.parsers]
        self.secondary_main_query = SECONDARY_MAIN_FUNCTION_QUERY_TEMPLATE_V2.replace("${name}", self.name).replace("${exclude}", EXCLUDE_PREFIX).replace("${built_in_name}",self.secondary_main_name).replace('${related_parsers}', ",\n".join(parsers))
    
    def get_parser_parameters_query(self, parser_name, parameters):
        disabled_parameter = "disabled= (builtInDisabled or(" + create_parser_name_for_disable_parameter(parser_name) + " in (DisabledParsers)))"
        return '' if parameters == [] else ('(' + create_function_parameters(parameters) + ')').replace('disabled= disabled', disabled_parameter)   

class Schema:
    def __init__(self, name, directory, kql_target, manifest_target, relative_path = "Parsers", kind = "Parser"):
        self.parsers_relative_path = relative_path
        self.name = name
        self.directory = directory
        self.kql_target = kql_target
        self.manifest_target = manifest_target
        self.kind = kind
        self.main_parsers = []
        self.parsers = []
        self.allParsers = []
    
    """
        fetch all files in the schema directory that ends with .yaml
        an init them, we determine if a parser is a main parser
        and we init the main parser post the others
    """
    def get_all_schema_parsers(self):
        all_parsers_files = [f for f in os.listdir(self.directory + "/" + self.parsers_relative_path) if f.endswith('.yaml')]       
        for f in all_parsers_files:
            with open(self.directory + "/" + self.parsers_relative_path + "/" + f, 'r') as stream:
                parsed_yaml = yaml.safe_load(stream)
                equivalentBuiltIn = parsed_yaml["EquivalentBuiltIn" + self.kind]
                name = parsed_yaml[self.kind + "Name"]
                PARSERS_NAMES[name] = equivalentBuiltIn

        
    def init_parsers(self):
        current_dir = os.getcwd()
        main_parser_names = []
        all_parsers_files = [f for f in os.listdir(self.directory + "/" + self.parsers_relative_path) if f.endswith('.yaml')]
        os.chdir(self.directory)
        for f in all_parsers_files:
            if(self.is_main_parser(f)):
                main_parser_names.append(f)
            else:
                self.init_parser(f)

        for name in main_parser_names:
            self.init_main_parser(name)
                
        os.chdir(current_dir)

    def is_main_parser(self, file):
        with open(self.parsers_relative_path + "/" + file, 'r') as stream:
            parsed_yaml = yaml.safe_load(stream)
        return "Parsers" in parsed_yaml

    def init_parser(self, file):
        parser = Parser(self.name, self.parsers_relative_path + "/" + file, self.kind)
        parser.init_parser()
        parser.create_query_file(parser.name_with_version, parser.query , self.kql_target)
        self.parsers.append(parser)

    def init_main_parser(self, file):
        main_parser = Main_Parser(self.name, self.parsers_relative_path + "/" + file)
        self.get_main_parser_parsers(main_parser)
        main_parser.init_parser()

        main_parser.create_query_file(
            main_parser.secondary_main_name, main_parser.secondary_main_query , self.kql_target)
        main_parser.create_query_file(
            main_parser.name, main_parser.query , self.kql_target)  # is built in function

        self.main_parsers.append(main_parser)

    def get_main_parser_parsers(self, main_parser):
        with open(main_parser.parameters_file, 'r') as stream:
            parsed_yaml = yaml.safe_load(stream)
        parser_names = parsed_yaml["Parsers"]
        parsers = [parser for parser in self.parsers if parser.name in parser_names]

        main_parser.set_parsers(parsers)


    def create_functions(self):
        dump_functions = []
        for parser in self.parsers:
            dump_functions.append(json.dumps(parser.create_la_function(parser.name_with_version)))

        for main_parser in self.main_parsers:
            dump_functions.append(json.dumps(main_parser.create_la_function()))
            dump_functions.append(json.dumps(
                main_parser.create_la_function(main_parser.secondary_main_name)))

        object = json.loads(FUNCTIONS_LIST_TEMPLATE.replace(
                '${values}', ',\n'.join(dump_functions)))
        self.merge_manifests(object)


    def merge_manifests (self, new_functions):
        base_folder = sys.argv[1]
        path = f"{base_folder}/{self.manifest_target}"
        manifest_file = open(path)
        manifest_json = json.load(manifest_file)
        existing_functions = manifest_json['functions']
        id_list = [function['id'] for function in new_functions]
        for func in existing_functions:
            if func['id'] not in id_list:
                new_functions.append(func)
        manifest_json['functions'] = sorted(new_functions, key = lambda func: func['name']) 
        with open(path, 'w') as file:
                    file.write(json.dumps(manifest_json, indent=4))


def main():
    global PARSERS_NAMES
    PARSERS_NAMES = {}
    schemas = [Schema("Dns", "ASimDns", f"{KQL_DIRECTORY}/DNS", "content/NGSchemas/SentinelAsim/Dns.manifest.json"),
               Schema("NetworkSession", "ASimNetworkSession", f"{KQL_DIRECTORY}/NetworkSession", "content/NGSchemas/SentinelAsim/NetworkSession.manifest.json"),
               Schema("WebSession", "ASimWebSession", f"{KQL_DIRECTORY}/WebSession", "content/NGSchemas/SentinelAsim/WebSession.manifest.json") ,
               Schema("AuditEvent", "AsimAuditEvent", f"{KQL_DIRECTORY}/AuditEvent", "content/NGSchemas/SentinelAsim/AuditEvent.manifest.json"),
               Schema("ASim", "../ASIM", f"{KQL_DIRECTORY}/Common", "content/NGSchemas/SentinelAsim/ASimFunctions.manifest.json", "lib/Functions", "Function")]

    for schema in schemas:
       schema.get_all_schema_parsers()

        
    for schema in schemas:
        schema.init_parsers()
        schema.create_functions()

if __name__ == '__main__':
    main()
