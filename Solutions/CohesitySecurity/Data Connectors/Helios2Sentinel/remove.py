#!/usr/bin/env python3

import json
import subprocess
import sys


def get_function_names_by_prefix(funNamePrefix):
    query = "[?contains(name,'" + funNamePrefix + "')]"
    result = subprocess.run(['az', 'functionapp', 'list', '--query', query], stdout=subprocess.PIPE)
    jsObjs = json.loads(result.stdout)
    return [jsobj["id"].split("/")[-1] for jsobj in jsObjs]


def remove_functions_by_prefix(funNamePrefix, resourceGroup):
    functions = get_function_names_by_prefix(funNamePrefix)
    for function in functions:
        print("function to remove --> %s" % function)
        subprocess.run(['az', 'functionapp', 'delete', '--name', function, '--resource-group', resourceGroup])
    functions = get_function_names_by_prefix(funNamePrefix)
    print("functions after removing --> %s" % functions)


remove_functions_by_prefix(sys.argv[1], sys.argv[2])
