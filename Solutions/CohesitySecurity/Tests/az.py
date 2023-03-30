#!/usr/bin/env python3

import json
import numpy as np
import random
import random
import json
import subprocess


def get_subscriptionId():
    result = subprocess.run(['az', 'account', 'subscription', 'list'], stdout=subprocess.PIPE)
    jsObj = json.loads(result.stdout)
    subscriptionId = jsObj[0]["subscriptionId"]
    return subscriptionId


def incident_show(vid, resource_group, workspace_name):
    result = subprocess.run(['az', 'sentinel', 'incident', 'show', '--incident-id', vid, '--resource-group', resource_group, '--workspace-name', workspace_name], stdout=subprocess.PIPE)
    jsObj = json.loads(result.stdout)


def run_playbook(subscriptionId, vid, resource_group, workspace_name, playbook_name):
    result = subprocess.run(['az', 'sentinel', 'incident', 'run-playbook', '--incident-identifier', vid, '--resource-group', resource_group, '--workspace-name', workspace_name, '--logic-apps-resource-id', "/subscriptions/" + subscriptionId + "/resourceGroups/" + resource_group + "/providers/Microsoft.Logic/workflows/" + playbook_name], stdout=subprocess.PIPE)
    return result.returncode


def get_one_incident_id(resource_group, workspace_name):
    result = subprocess.run(['az', 'sentinel', 'incident', 'list', '--resource-group', resource_group, '--workspace-name', workspace_name], stdout=subprocess.PIPE)
    jsObj = random.choice(json.loads(result.stdout))
    alert_id = jsObj["description"].split("Helios ID: ")[-1]
    vid = jsObj["id"].split("/")[-1]
    return vid, alert_id


def has_dup_incidents(resource_group, workspace_name):
    ids = get_incident_ids(resource_group, workspace_name)
    alert_ids = [alert_id for (vid, alert_id) in ids]
    return len(alert_ids) != len(np.unique(np.array(alert_ids)))


def get_incident_ids(resource_group, workspace_name):
    result = subprocess.run(['az', 'sentinel', 'incident', 'list', '--resource-group', resource_group, '--workspace-name', workspace_name], stdout=subprocess.PIPE)
    return [(jsObj["id"].split("/")[-1], jsObj["description"].split("Helios ID: ")[-1]) for jsObj in json.loads(result.stdout)]
