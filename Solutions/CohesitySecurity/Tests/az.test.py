#!/usr/bin/env python3

"""
This module defines unit tests for the Cohesity system.
"""

from az import *
from helios import *
import json
import numpy as np
import os
import subprocess
import time
import unittest


class TestCohesity(unittest.TestCase):
    def setUp(self):
        """
        This method is called before each test case and is used to set up any
        necessary resources or configurations. In this case, the configuration
        for the Cohesity system is loaded from a JSON file, and the necessary
        playbooks are deployed.
        """
        # Load config from JSON file
        with open('../cohesity.json') as f:
            config = json.load(f)
            self.resource_group = config['resource_group']
            self.workspace_name = config['workspace_name']
            self.api_key = config['api_key']

        # Verify that config values are not empty
        self.assertNotEqual(self.resource_group, "", "resource_group is empty")
        self.assertNotEqual(self.workspace_name, "", "workspace_name is empty")
        self.assertNotEqual(self.api_key, "", "api_key is empty")

        # Deploy playbooks
        bash_command = "./deploy_playbooks.sh"
        process = subprocess.Popen(
            bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        if output:
            print("output --> %s" % output.decode())

        if error:
            print("error --> %s" % error.decode())

    def test_cohesity_close_helios_incident(self):
        """
        This test case verifies that the 'Cohesity_Close_Helios_Incident'
        playbook can successfully close a Helios incident. It first retrieves
        an incident ID and verifies that the corresponding Helios alert is in
        the 'kOpen' state. It then runs the playbook and waits for 30 seconds
        before verifying that the Helios alert is in the 'kSuppressed' state.
        """
        # self.skipTest("Skipping test_cohesity_close_helios_incident")
        print("Starting test_cohesity_close_helios_incident...")
        playbook_name = "Cohesity_Close_Helios_Incident"
        subscription_id = get_subscription_id()
        incident_id, alert_id = get_one_incident_id(
            self.resource_group, self.workspace_name)

        alert_details = get_alert_details(alert_id, self.api_key)
        self.assertEqual(
            alert_details['alertState'], "kOpen",
            "Alert state is not kOpen")
        # maybe we need to close incident after close helios alert, otherwise,
        # this assert might fail.
        returncode = run_playbook(
            subscription_id, incident_id, self.resource_group,
            self.workspace_name, playbook_name)
        self.assertEqual(returncode, 0)

        time.sleep(30)  # Sleep for 30 seconds

        alert_details = get_alert_details(alert_id, self.api_key)
        print("alert_id --> %s" % alert_id)
        print("api_key --> %s" % self.api_key)
        self.assertEqual(
            alert_details['alertState'], "kSuppressed",
            "Alert state is not kSuppressed")
        print("test_cohesity_close_helios_incident finished successfully.")


    def test_all_incidents_in_helios(self):
        """
        This test case verifies that all incidents in the Sentinel workspace
        have corresponding alerts in Helios, and that the number of alerts in
        Helios matches the number of incidents in the Sentinel workspace.
        """
        print("Starting test_all_incidents_in_helios")
        ids = get_incident_ids(self.resource_group, self.workspace_name)
        alert_ids = [alert_id for (incident_id, alert_id) in ids]
        for alert_id in alert_ids:
            self.assertIsNotNone(
                get_alert_details(alert_id, self.api_key),
                f"alert_id --> {alert_id} doesn't exist in helios.")
        alerts_details = get_alerts_details(alert_ids, self.api_key)
        self.assertEqual(
            len(alert_ids), len(alerts_details),
            "Number of alerts does not match the number of incidents")
        print("test_all_incidents_in_helios completed successfully")


    def test_no_dup_incidents(self):
        """
        This test case verifies that there are no duplicate incidents in the
        Sentinel workspace.
        """
        print("Starting test_no_dup_incidents")
        ids = get_incident_ids(self.resource_group, self.workspace_name)
        alert_ids = [alert_id for (incident_id, alert_id) in ids]
        return len(alert_ids) != len(np.unique(np.array(alert_ids)))
        print("test_no_dup_incidents completed successfully")


    def test_alerts_in_sentinel(self):
        """
        This test case verifies that all Helios alerts have corresponding
        incidents in the Sentinel workspace.
        """
        print("Starting test_alerts_in_sentinel")
        alert_ids = get_alerts(self.api_key, 30, 0)
        for alert_id in alert_ids:
            self.assertIsNotNone(
                search_alert_id_in_incident(
                    alert_id, self.resource_group, self.workspace_name),
                f"alert_id --> {alert_id} doesn't exist in sentinel.")
        print("test_alerts_in_sentinel completed successfully")


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    unittest.main()
