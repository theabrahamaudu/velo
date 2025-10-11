from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime


class CreateArtifact(BaseModel):
    task_id: int
    type: Literal["text", "image"]
    file_path: Optional[str]
    version: int


class ReadArtifact(BaseModel):
    id: int
    task_id: int
    type: Literal["text", "image"]
    file_path: Optional[str]
    version: int
    created_at: datetime
