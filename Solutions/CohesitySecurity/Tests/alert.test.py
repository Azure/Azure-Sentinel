#!/usr/bin/env python3

"""
This module defines unit tests for the Alert.
"""

import unittest
from alert import *


class TestAlert(unittest.TestCase):
    def setUp(self):
        self.json_str = '''[
            {
                "id": "5461471069190603:1677650940946971",
                "alertCode": "CE01516011",
                "firstTimestampUsecs": 1677650940946971,
                "latestTimestampUsecs": 1677650940946971,
                "alertCategory": "kSecurity",
                "alertType": 16011,
                "severity": "kCritical",
                "alertState": "kOpen",
                "propertyList": [
                    {
                        "key": "entityId",
                        "value": "236"
                    },
                    {
                        "key": "object",
                        "value": "RansomwareVm-multi-vol-prod-canary"
                    },
                    {
                        "key": "parentId",
                        "value": "1"
                    },
                    {
                        "key": "source",
                        "value": "10.2.157.1"
                    },
                    {
                        "key": "cid",
                        "value": "3576457995024682"
                    },
                    {
                        "key": "clusterIncarnationId",
                        "value": "1674247199596"
                    },
                    {
                        "key": "cluster",
                        "value": "KishanPhysicalNode"
                    },
                    {
                        "key": "jobId",
                        "value": "9183"
                    },
                    {
                        "key": "jobName",
                        "value": "Kishan-RansomwareRRLP"
                    },
                    {
                        "key": "environment",
                        "value": "kVMware"
                    },
                    {
                        "key": "jobInstanceId",
                        "value": "9233"
                    },
                    {
                        "key": "jobStartTimeUsecs",
                        "value": "1677649169619901"
                    },
                    {
                        "key": "anomalyStrength",
                        "value": "90"
                    },
                    {
                        "key": "anomalousJobInstanceId",
                        "value": "9244"
                    },
                    {
                        "key": "anomalousJobStartTimeUsecs",
                        "value": "1677650940946971"
                    },
                    {
                        "key": "inlineSnapshotDiff",
                        "value": "True"
                    },
                    {
                        "key": "clusterPartitionId",
                        "value": "8"
                    }
                ],
                "dedupTimestamps": [
                    1677650940946971
                ],
                "dedupCount": 1,
                "alertDocument": {
                    "alertName": "DataIngestAnomalyAlert",
                    "alertDescription": "Anomalous change in file system detected on RansomwareVm-multi-vol-prod-canary, a symptom of potential ransomware attack on your primary environment",
                    "alertCause": "The recent protection run of Protection Group Kishan-RansomwareRRLP with job id 9183 has dramatic changes in the composition of files, which is a significant deviation from the previously observed protection runs",
                    "alertHelpText": "Use the latest clean snapshot taken at 01, Mar 2023 05:39 AM to perform Instant Recovery"
                },
                "clusterName": "KishanPhysicalNode",
                "clusterId": 3576457995024682,
                "eventSource": "kHelios",
                "alertTypeBucket": "kMaintenance"
            }
        ]'''

        self.alert = Alert(self.json_str)

    def test_get_job_id(self):
        print("Starting test_get_job_id...")
        self.assertEqual(self.alert.get_job_id(), "9183")
        print("test_get_job_id finished successfully.")

    def test_get_cluster_id(self):
        print("Starting test_get_cluster_id...")
        self.assertEqual(self.alert.get_cluster_id(), 3576457995024682)
        print("test_get_cluster_id finished successfully.")

    def test_get_cluster_incarnation_id(self):
        print("Starting test_get_cluster_incarnation_id...")
        self.assertEqual(self.alert.get_cluster_incarnation_id(), "1674247199596")
        print("test_get_cluster_incarnation_id finished successfully.")

    def test_get_protection_group_id(self):
        print("Starting test_get_protection_group_id...")
        self.assertEqual(self.alert.get_protection_group_id(), "3576457995024682:1674247199596:9183")
        print("test_get_protection_group_id finished successfully.")


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    unittest.main()
