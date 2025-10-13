from pydantic import BaseModel
from typing import Literal, Optional, Dict, List
from datetime import datetime
from velo.types.artifact import ReadArtifact


class CreateTask(BaseModel):
    campaign_id: int
    tool_name: str
    status: Literal["pending", "success", "error"]
    output_json: Optional[dict]


class ReadTask(BaseModel):
    id: int
    campaign_id: int
    tool_name: str
    status: Literal["pending", "success", "error"]
    output_json: Optional[Dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ReadFullTask(BaseModel):
    id: int
    campaign_id: int
    tool_name: str
    status: Literal["pending", "success", "error"]
    output_json: Optional[Dict] = None
    artifacts: List[ReadArtifact]
    created_at: datetime
    updated_at: Optional[datetime] = None
