#!/usr/bin/env python3

import json
import os
import subprocess


def get_function_names_by_prefix(funNamePrefix):
    query = "[?contains(name,'" + funNamePrefix + "')]"
    result = subprocess.run(
        ["az", "functionapp", "list", "--query", query], stdout=subprocess.PIPE
    )
    print(result)
    jsObjs = json.loads(result.stdout)
    return [jsobj["id"].split("/")[-1] for jsobj in jsObjs]


def remove_functions_by_prefix(funNamePrefix, resourceGroup):
    functions = get_function_names_by_prefix(funNamePrefix)
    for function in functions:
        print("function to remove --> %s" % function)
        subprocess.run(
            [
                "az",
                "functionapp",
                "delete",
                "--name",
                function,
                "--resource-group",
                resourceGroup,
            ]
        )
    functions = get_function_names_by_prefix(funNamePrefix)
    print("functions after removing --> %s" % functions)


os.chdir(os.path.dirname(os.path.abspath(__file__)))
configFile = "../../cohesity.json"
with open(configFile) as f:
    data = json.load(f)
    resource_group = data["resource_group"]
    producer_fun_prefix = data["producer_fun_prefix"]
    consumer_fun_prefix = data["consumer_fun_prefix"]

remove_functions_by_prefix(consumer_fun_prefix, resource_group)
remove_functions_by_prefix(producer_fun_prefix, resource_group)
