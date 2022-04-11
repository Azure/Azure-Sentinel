from typing import Dict, List, Optional
from pydantic import BaseModel


class OATQueueMessage(BaseModel):
    clp_id: str
    detections: List[Dict]
    post_data: Dict


class OATDetectionResult(BaseModel):
    total_count: int
    detections: List[Dict]
    search_api_post_data: List[Dict]
    next_batch_token: Optional[str]
