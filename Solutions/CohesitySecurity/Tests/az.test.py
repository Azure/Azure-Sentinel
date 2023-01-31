#!/usr/bin/env python3

import json
from az import *
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
f = open('../cohesity.json',)
data = json.load(f)
resource_group = data['resource_group']
workspace_name = data['workspace_name']
playbook_name = data['playbook_name']
apiKey = data['apiKey']
f.close()

assert has_dup_incidents(resource_group, workspace_name) == False
