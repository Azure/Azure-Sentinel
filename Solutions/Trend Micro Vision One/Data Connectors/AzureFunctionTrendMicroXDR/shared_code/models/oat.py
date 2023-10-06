from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel


class RiskLevel(str, Enum):
    UNDEFINED = 'undefined'
    INFO = 'info'
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class OATDetectionResult(BaseModel):
    total_count: int
    detections: List[Dict]
    search_api_post_data: List[Dict]
    next_batch_token: Optional[str]


class OATTaskMessage(BaseModel):
    clp_id: str
    token: Optional[str]
    start_time: str
    end_time: str
    task_id: Optional[str]


class OATFileMessage(BaseModel):
    clp_id: str
    token: Optional[str]
    package_id: str
    task_id: Optional[str]
    pipeline_id: str
