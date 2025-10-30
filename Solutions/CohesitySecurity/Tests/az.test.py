#!/usr/bin/env python3

"""
This module defines unit tests for the Cohesity system.
"""

from az import *
from helios import *
from alert import Alert
import json
import numpy as np
import os
import subprocess
import time
import unittest
import re

# Constants for better readability
MICROSECS_IN_SEC = 1000000


class TestCohesity(unittest.TestCase):
    def setUp(self):
        """
        This method is called before each test case and is used to set up any
        necessary resources or configurations. In this case, the configuration
        for the Cohesity system is loaded from a JSON file, and the necessary
        playbooks are deployed.
        """
        # Load config from JSON file
        with open("../cohesity.json") as f:
            config = json.load(f)
            self.resource_group = config["resource_group"]
            self.workspace_name = config["workspace_name"]
            self.api_key = config["api_key"]
            self.alert_id = config["alert_id"]
            self.tenant_id = config["tenant_id"]
            self.client_id = config["client_id"]
            self.client_secret = config["client_secret"]
            self.resource_url = config["resource_url"]
            self.scope = config["scope"]
            self.subscription_id = config["subscription_id"]

        self.access_token = get_azure_access_token(
            self.tenant_id,
            self.client_id,
            self.client_secret,
            self.resource_url,
            self.scope,
        )

        # Verify that config values are not empty
        self.assertNotEqual(self.resource_group, "", "resource_group is empty")
        self.assertNotEqual(self.workspace_name, "", "workspace_name is empty")
        self.assertNotEqual(self.api_key, "", "api_key is empty")
        self.assertNotEqual(self.alert_id, "", "alert_id is empty")
        self.assertNotEqual(self.tenant_id, "", "tenant_id is empty")
        self.assertNotEqual(self.client_id, "", "client_id is empty")
        self.assertNotEqual(self.client_secret, "", "client_secret is empty")
        self.assertNotEqual(self.resource_url, "", "resource_url is empty")
        self.assertNotEqual(self.scope, "", "scope is empty")
        self.assertNotEqual(self.access_token, "", "access_token is empty")
        self.assertNotEqual(
            self.subscription_id, "", "subscription_id is empty"
        )

        # Deploy playbooks
        bash_command = "./deploy_playbooks.sh"
        process = subprocess.Popen(
            bash_command.split(), stdout=subprocess.PIPE
        )
        output, error = process.communicate()

        if output:
            print("output --> %s" % output.decode())

        if error:
            print("error --> %s" % error.decode())

    def test_cohesity_restore_from_last_snapshot(self):
        """
        Test the Cohesity_Restore_From_Last_Snapshot playbook.
        """
        print("Starting test_cohesity_restore_from_last_snapshot...")
        playbook_name = "Cohesity_Restore_From_Last_Snapshot"
        subscription_id = get_subscription_id()
        result = search_alert_id_in_incident(
            self.alert_id, self.resource_group, self.workspace_name
        )
        jsObj = result[0]

        # The expected format of jsObj["id"]:
        # /subscriptions/<subscription_id>/resourceGroups/<resource_group>/
        # providers/Microsoft.OperationalInsights/workspaces/<workspace>/
        # providers/Microsoft.SecurityInsights/Incidents/<incident_id>
        # Example:
        # /subscriptions/26c46499-1b17-43a7-8d18-024c79f09bc7/resourceGroups/
        # kishan-rg-3/providers/Microsoft.OperationalInsights/workspaces/
        # kishan-rg3-ws4/providers/ Microsoft.SecurityInsights/Incidents/
        # d7c70079-72e3-4122-a192-27944276c713

        incident_id = jsObj["id"].split("/")[-1]

        alert_details = get_alert_details(self.alert_id, self.api_key)
        alert = Alert(json.dumps(alert_details))
        protection_group_id = alert.get_protection_group_id()
        cluster_id = alert.get_cluster_id()

        query_range_usecs = 3 * 60 * MICROSECS_IN_SEC

        # Calculate the current time and subtract 3 minutes to get a start time
        # for the recovery.Only recoveries that start within the last 3 minutes
        # will be retrieved.
        current_time_usecs = int(time.time() * MICROSECS_IN_SEC)
        start_time_usecs = current_time_usecs - query_range_usecs

        recoveries = get_recoveries(cluster_id, self.api_key, start_time_usecs)

        assert (
            recoveries is not None
            and recoveries.get("recoveries")
            and not any(
                # Check if there are any objects with the same protection group
                # ID as the one obtained from the alert
                any(
                    obj["protectionGroupId"] == str(protection_group_id)
                    for obj in recovery["vmwareParams"]["objects"]
                )
                for recovery in recoveries["recoveries"]
            )
        )

        returncode = run_playbook(
            subscription_id,
            incident_id,
            self.resource_group,
            self.workspace_name,
            playbook_name,
            self.access_token,
        )
        self.assertEqual(returncode, 0)

        recoveries = get_recoveries(cluster_id, self.api_key, start_time_usecs)

        # Check that the data is not null or empty
        assert (
            recoveries is not None
            and recoveries.get("recoveries")
            and any(
                any(
                    obj["protectionGroupId"] == str(protection_group_id)
                    for obj in recovery["vmwareParams"]["objects"]
                )
                for recovery in recoveries["recoveries"]
            )
        )

        print(
            "test_cohesity_restore_from_last_snapshot finished successfully."
        )

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
            self.resource_group, self.workspace_name
        )

        alert_details = get_alert_details(alert_id, self.api_key)
        self.assertEqual(
            alert_details["alertState"], "kOpen", "Alert state is not kOpen"
        )
        # maybe we need to close incident after close helios alert, otherwise,
        # this assert might fail.
        returncode = run_playbook(
            subscription_id,
            incident_id,
            self.resource_group,
            self.workspace_name,
            playbook_name,
            self.access_token,
        )
        self.assertEqual(returncode, 0)

        alert_details = get_alert_details(alert_id, self.api_key)
        print("alert_id --> %s" % alert_id)
        print("api_key --> %s" % self.api_key)
        self.assertEqual(
            alert_details["alertState"],
            "kSuppressed",
            "Alert state is not kSuppressed",
        )
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
        """
        To exclude cohesity test alert
        """
        pattern = r"^\d+:\d+$"

        non_matching_alert_ids = [
            alert_id
            for alert_id in alert_ids
            if not re.match(pattern, alert_id)
        ]

        non_matching_alert_id = non_matching_alert_ids[0]
        self.assertIn(
            "This is a test incident that confirms that the Cohesity function",
            non_matching_alert_id,
            f"The non-matching alert_id does not contain the expected string.",
        )

        for alert_id in [
            alert_id for alert_id in alert_ids if re.match(pattern, alert_id)
        ]:
            self.assertIsNotNone(
                get_alert_details(alert_id, self.api_key),
                f"alert_id --> {alert_id} doesn't exist in helios.",
            )
        alerts_details = get_alerts_details(alert_ids, self.api_key)
        self.assertEqual(
            len(alert_ids),
            len(alerts_details),
            "Number of alerts does not match the number of incidents",
        )
        print("test_all_incidents_in_helios completed successfully")

    def test_no_dup_incidents(self):
        """
        This test case verifies that there are no duplicate incidents in the
        Sentinel workspace.
        """
        print("Starting test_no_dup_incidents")
        ids = get_incident_ids(self.resource_group, self.workspace_name)
        alert_ids = [alert_id for (incident_id, alert_id) in ids]
        assert len(alert_ids) != len(np.unique(np.array(alert_ids)))
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
                    alert_id, self.resource_group, self.workspace_name
                ),
                f"alert_id --> {alert_id} doesn't exist in sentinel.",
            )
            print("test_alerts_in_sentinel completed successfully")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    """
    unittest.main()
    """

    # Add all tests except the ones we want to skip
    # TODO: Remove this block once the tests are stable, and a typical test
    # workflow should be:
    # 1. Create a new workspace
    # 2. Install function apps
    # 3. Install playbooks
    # 4. Wait for the incidents to come in
    # 5. Run all these tests
    suite = unittest.TestSuite(
        [
            TestCohesity(test)
            for test in unittest.defaultTestLoader.getTestCaseNames(
                TestCohesity
            )
            if test in ("test_cohesity_restore_from_last_snapshot",)
        ]
    )

    unittest.TextTestRunner().run(suite)
