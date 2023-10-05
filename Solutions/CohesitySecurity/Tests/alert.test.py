#!/usr/bin/env python3

"""
This module defines unit tests for the Alert.
"""

import json
import unittest
from alert import Alert
import os


class TestAlert(unittest.TestCase):
    def setUp(self):
        with open("./Data/alert.json") as f:
            self.json_str = json.load(f)
        self.alert = Alert(json.dumps(self.json_str))

    def test_get_job_id(self):
        print("Starting test_get_job_id...")
        self.assertEqual(self.alert.get_job_id(), "9183")
        print("test_get_job_id finished successfully.")

    def test_get_cluster_id(self):
        print("Starting test_get_cluster_id...")
        self.assertEqual(self.alert.get_cluster_id(), "3576457995024682")
        print("test_get_cluster_id finished successfully.")

    def test_get_cluster_incarnation_id(self):
        print("Starting test_get_cluster_incarnation_id...")
        self.assertEqual(
            self.alert.get_cluster_incarnation_id(), "1674247199596"
        )
        print("test_get_cluster_incarnation_id finished successfully.")

    def test_get_protection_group_id(self):
        print("Starting test_get_protection_group_id...")
        self.assertEqual(
            self.alert.get_protection_group_id(),
            "3576457995024682:1674247199596:9183",
        )
        print("test_get_protection_group_id finished successfully.")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    unittest.main()
