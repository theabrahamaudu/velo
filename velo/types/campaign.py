from pydantic import BaseModel
from typing import List
from datetime import datetime
from velo.types.task import ReadTask, ReadArtifact


class CreateCampaign(BaseModel):
    chat_id: int
    request_text: str


class ReadCampaign(BaseModel):
    id: int
    chat_id: int
    request_text: str
    created_at: datetime


class ReadFullCampaign(BaseModel):
    id: int
    chat_id: int
    request_text: str
    tasks: List[ReadTask]
    artifacts: List[ReadArtifact]
    created_at: datetime
