from tenable.io import TenableIO as BaseIO
from tenable.io.exports import ExportsAPI
from enum import Enum
import os

class ExportsAPIExtended(ExportsAPI):
    def vulns(self, **kwargs) -> str:
        return super().vulns(**kwargs).uuid

    def assets(self, **kwargs) -> str:
        return super().assets(**kwargs).uuid

    def status(self, export_type: str, uuid: str) -> dict:
        return self._api.get(
            f'{export_type}/export/{uuid}/status'
        ).json()

    def chunk(self, export_type: str, uuid: str, chunk: int) -> list:
        return self._api.get(
            f'{export_type}/export/{uuid}/chunks/{chunk}'
        ).json()


class TenableIO(BaseIO):
    def __init__(self, **kwargs):
        kwargs['vendor'] = os.getenv('PyTenableUAVendor', 'Microsoft')
        kwargs['product'] = os.getenv('PyTenableUAProduct', 'Azure Sentinel')
        kwargs['build'] = os.getenv('PyTenableUABuild', '0.0.1')
        super().__init__(**kwargs)

    @property
    def exports(self):
        return ExportsAPIExtended(self)


class TenableStatus(Enum):
    finished = 'FINISHED'
    failed = 'FAILED'
    no_job = 'NO_JOB_FOUND'
    processing = 'PROCESSING'
    sending_to_queue = 'SENDING_TO_QUEUE'
    sent_to_queue = 'SENT_TO_QUEUE'
    sent_to_sub_orchestrator = 'SENT_TO_SUB_ORCHESTRATOR'

class TenableExportType(Enum):
    asset = 'ASSET_EXPORT_JOB'
    vuln = 'VULN_EXPORT_JOB'