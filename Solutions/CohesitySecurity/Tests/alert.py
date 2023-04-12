#!/usr/bin/env python3
import json


class Alert:
    """
    A class for extracting data from a JSON string representing an alert.
    """

    def __init__(self, json_str):
        data = json.loads(json_str)
        self.job_id = None
        self.cluster_id = str(data["clusterId"])
        self.cluster_incarnation_id = None
        for prop in data["propertyList"]:
            if prop["key"] == "jobId":
                self.job_id = prop["value"]
            elif prop["key"] == "clusterIncarnationId":
                self.cluster_incarnation_id = prop["value"]
        if self.job_id is None:
            raise ValueError("jobId is not present in the propertyList")
        if self.cluster_incarnation_id is None:
            raise ValueError(
                "clusterIncarnationId is not present in the propertyList"
            )
        self.protection_group_id = (
            f"{self.cluster_id}:{self.cluster_incarnation_id}:{self.job_id}"
        )

    def get_job_id(self):
        return self.job_id

    def get_cluster_id(self):
        return self.cluster_id

    def get_cluster_incarnation_id(self):
        return self.cluster_incarnation_id

    def get_protection_group_id(self):
        return self.protection_group_id
