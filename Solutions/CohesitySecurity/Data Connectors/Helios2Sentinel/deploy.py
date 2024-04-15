#!/usr/bin/env python3

import json
import subprocess
import sys


def get_function_name_by_prefix(funNamePrefix):
    query = "[?contains(name,'" + funNamePrefix + "')]"
    result = subprocess.run(
        ["az", "functionapp", "list", "--query", query], stdout=subprocess.PIPE
    )
    jsObj = json.loads(result.stdout)
    vid = jsObj[0]["id"]
    function_name = vid.split("/")[-1]
    return function_name


def publish_function_name_by_prefix(funNamePrefix, subFolder):
    function_name = get_function_name_by_prefix(funNamePrefix)
    subprocess.run(["dotnet", "clean"], cwd=subFolder)
    subprocess.run(
        ["func", "azure", "functionapp", "publish", function_name, "--force"],
        cwd=subFolder,
    )


publish_function_name_by_prefix(sys.argv[1], sys.argv[2])
