#!/usr/bin/env python3

import time
from az import *
from helios import *

resource_group = 'ying-test-resource-group'
workspace_name = 'auto-deploy-workspace-01-24-23-v3'
playbook_name = 'Cohesity_Close_Helios_Incident'
apiKey = '33e44eac-ce99-46df-7f4e-9ac39446a66e'

subscriptionId = get_subscriptionId()
vid, alert_id = get_one_incident_id(resource_group, workspace_name)

alert_details = get_alert_details(alert_id, apiKey)
assert alert_details['alertState'] == "kOpen" # maybe we need to close incident after close helios alert, otherwise, this assert might fail.
returncode = run_playbook(subscriptionId, vid, resource_group, workspace_name, playbook_name)

time.sleep(30)  # Sleep for 30 seconds

alert_details = get_alert_details(alert_id, apiKey)
assert alert_details['alertState'] == "kSuppressed"
