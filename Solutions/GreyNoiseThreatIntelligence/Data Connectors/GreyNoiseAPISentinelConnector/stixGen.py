import datetime
import json
import uuid

from stix2 import Indicator

# https://stix2.readthedocs.io/en/latest/guide/custom.html#ID-Contributing-Properties-for-Custom-Cyber-Observables
# OASIS recommended Namespace for UUIDs
NAMESPACE_UUID = uuid.UUID('00abedb4-aa42-466c-9c01-fed23315a9b7')

class GreyNoiseStixGenerator:
    def __init__(self):
        self.stix_version = "2.1"
        self.pattern_type = "stix"
        self.name = "GreyNoise Internet Scanner IOC"
        self.valid_until = (datetime.datetime.utcnow() + datetime.timedelta(hours=24)).isoformat() + "Z"
        self.created_by_ref = "identity--90a30b13-e3e2-45e1-be2b-48a8b977ecbc"
        self.namespace_uuid = NAMESPACE_UUID

    @staticmethod
    def generate_id_for_ioc_value(ioc_value: str) -> str:
        """Generate a stix 2.1 id for an IOC value."""
        ioc_uuid = str(uuid.uuid5(namespace=NAMESPACE_UUID, name=ioc_value.lower()))
        return f'indicator--{ioc_uuid}'
    
    def generate_indicator(self, gnIndicator: dict):
        # Set confidence to 90 if spoofable, 100 if not
        if gnIndicator.get('spoofable') == True and gnIndicator.get('classification') != "benign":
            confidence = 90
        else:
            confidence = 100
        indicator = Indicator(
            id=self.generate_id_for_ioc_value(gnIndicator.get('ip')),
            type="indicator",
            spec_version=self.stix_version,
            name=self.name,
            description="GreyNoise Indicator",
            indicator_types=[gnIndicator.get('classification')],
            pattern="[ipv4-addr:value = '{}']".format(gnIndicator.get('ip')),
            pattern_type=self.pattern_type,
            valid_from=datetime.datetime.strptime(gnIndicator.get('first_seen'), "%Y-%m-%d").isoformat()+'Z',
            valid_until=self.valid_until,
            created_by_ref=self.created_by_ref,
            labels=gnIndicator.get('tags'),
            confidence=confidence,
        )

        # Convert to dict from Stix Incident Object
        return json.loads(indicator.serialize())
