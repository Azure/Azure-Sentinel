import json
import yaml
import sys
import os
import uuid
import numpy

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
| distinct SourceSpecificParser);
let builtInDisabled=toscalar(DisabledParsers has_any ('${exclude}${built_in_name}', '${exclude}${name}', 'Any'))
union isfuzzy=true
${related_parsers}
'''

SECONDARY_MAIN_FUNCTION_QUERY_TEMPLATE = '''union isfuzzy=true
    ${related_parsers}
'''

def create_parser_name_for_disable_parameter(parser_name):
    return "'"+ EXCLUDE_PREFIX + parser_name + "'"

def create_function_name_from_parser_name_and_version(parser_name, version=''):
    version_without_dots = version.replace('.', '')
    return parser_name + "V" + version_without_dots


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
                "'${default}'", str(param['Default']))
        if (param['Type'] == "table"):
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
        self.create_query_file(self.name_with_version, self.query)
        paramsKey = PARSER_PARAMS.replace('${kind}', self.kind)
        if(paramsKey in parsed_yaml):
            self.parameters = parsed_yaml[paramsKey]

    def create_query_file(self, name, query):
        for parserName in PARSERS_NAMES.keys():
            
            query = query.replace(parserName, PARSERS_NAMES[parserName])
            if (parserName == "ASimDnsMicrosoftNXLog"):
                print("----ggg--")
                print("------")
                print(parserName)
                print(PARSERS_NAMES[parserName])
                print("------")
                print("------")
            
            if (PARSERS_NAMES[parserName] == "_ASim_DnsMicrosoftNXLog"):
                print("------")
                print("------")
                print(parserName)
                print(PARSERS_NAMES[parserName])
                print("------")
                print("------")

        with open(name + '.kql', 'w') as file:
            file.write(query)

    def create_la_function(self, name=''):
        function_name = self.name if name == '' else name
        function_body = json.loads(FUNCTION_TEMPLATE)
        function_body['id'] = str(uuid.uuid5(uuid.NAMESPACE_OID, function_name))
        function_body['name'] = function_name
        function_body['description'] = self.description
        function_body['solutions'] = ["SecurityInsights"]
        function_body['parameters'] = create_function_parameters(
            self.parameters, True)
        function_body['bodyFilePath'] = "KQL/" + self.schema + "/" + function_name + ".kql" if self.kind == "Parser"  else "KQL/Common/" + function_name + ".kql"
               
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
    def __init__(self, name, directory, relative_path = "Parsers", kind = "Parser"):
        self.parsers_relative_path = relative_path
        self.name = name
        self.directory = directory
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

                if (name == "ASimDnsMicrosoftNXLog"):
                    print("----ggg--")
                    print("------")
                    print(name)
                    print(PARSERS_NAMES[name])
                    print("------")
                    print("------")
            
                if (PARSERS_NAMES[name] == "_ASim_DnsMicrosoftNXLog"):
                    print("------")
                    print("------")
                    print(name)
                    print(PARSERS_NAMES[name])
                    print("------")
                    print("------")

        return PARSERS_NAMES

        

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
        self.parsers.append(parser)

    def init_main_parser(self, file):
        main_parser = Main_Parser(self.name, self.parsers_relative_path + "/" + file)
        self.get_main_parser_parsers(main_parser)
        main_parser.init_parser()

        main_parser.create_query_file(
            main_parser.secondary_main_name, main_parser.secondary_main_query)
        main_parser.create_query_file(
            main_parser.name, main_parser.query)  # is built in function

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

        with open(self.directory + "/" + self.name + '_functions.json', 'w') as file:
            file.write(FUNCTIONS_LIST_TEMPLATE.replace(
                '${values}', ',\n'.join(dump_functions)))

def main():
    global PARSERS_NAMES
    PARSERS_NAMES = {"key": "value"}
    schemas = [Schema("Dns", "ASimDns"), Schema("NetworkSession", "ASimNetworkSession"), Schema("WebSession", "ASimWebSession"), Schema("ProcessEvent", "ASimProcessEvent"), Schema("ASim", "../ASIM", "Library/Functions", "Function")]

    for schema in schemas:
       schema.get_all_schema_parsers().keys()

        
    for schema in schemas:
        schema.init_parsers()
        schema.create_functions()

if __name__ == '__main__':
    main()
