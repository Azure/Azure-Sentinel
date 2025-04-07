from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class ProjectState(str, Enum):
    """Enum for project state values"""
    CREATED = "CREATED"
    GENERATING = "GENERATING"
    DRAFT = "DRAFT"
    PUBLISHED_ALERT = "PUBLISHED_ALERT"
    PUBLISHED_BLOCK = "PUBLISHED_BLOCK"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


class ProjectAssignedVariable(BaseModel):
    """Schema for project assigned variables"""
    name: Optional[str] = ""
    value: Optional[str] = ""
    variable_type: Optional[str] = ""

class GuardicoreApplication(BaseModel):
    """Pydantic model for Guardicore Application/Project data"""
    sampling_timestamp: int
    id: str = Field(alias="_id")
    project_name: str
    project_template_id: Optional[str] = ""
    project_version: str
    api_version: str
    rulesets: Optional[List[str]] = []
    state: Optional[ProjectState] = None
    is_custom: Optional[bool] = False
    allow_only_rules: Optional[bool] = False
    some_rules_failed_validation: Optional[bool] = None
    assigned_variables: Optional[List[ProjectAssignedVariable]] = []
    targets: Optional[List[str]] = []
    user_request: Optional[Dict[str, Any]] = {}
    author_id: Optional[str] = ""
    creation_time: Optional[int] = None
    last_update_time: Optional[int] = None
    comments: Optional[str] = ""

    class Config:
        extra = "ignore"
        use_enum_values = True
