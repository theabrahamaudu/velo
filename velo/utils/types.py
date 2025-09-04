from pydantic import BaseModel
from typing import Literal, Optional, List, Dict


class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    thinking: Optional[str] = None
    images: Optional[List[str]] = None
    tool_calls: Optional[List[Dict]] = None
    tool_name: Optional[str] = None
