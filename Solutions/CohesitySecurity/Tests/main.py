#!/usr/bin/env python3

import time
from az import *
from helios import *
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
f = open('../cohesity.json',)
data = json.load(f)
resource_group = data['resource_group']
workspace_name = data['workspace_name']
playbook_name = data['playbook_name']
apiKey = data['apiKey']
f.close()

subscriptionId = get_subscriptionId()
vid, alert_id = get_one_incident_id(resource_group, workspace_name)

alert_details = get_alert_details(alert_id, apiKey)
assert alert_details['alertState'] == "kOpen"  # maybe we need to close incident after close helios alert, otherwise, this assert might fail.
returncode = run_playbook(subscriptionId, vid, resource_group, workspace_name, playbook_name)
assert returncode == 0

time.sleep(30)  # Sleep for 30 seconds

alert_details = get_alert_details(alert_id, apiKey)
assert alert_details['alertState'] == "kSuppressed"
