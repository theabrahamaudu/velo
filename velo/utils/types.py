from pydantic import BaseModel, Field
from typing import Any, Literal, Optional, List, Dict


# tool call
class FunctionToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]


class ToolCall(BaseModel):
    function: FunctionToolCall


# message
class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    thinking: Optional[str] = None
    images: Optional[List[str]] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_name: Optional[str] = None


# tool type set
class Property(BaseModel):
    type: Literal["string", "integer", "boolean", "array"]
    description: str | None = None
    items: Dict | None = None


class Parameters(BaseModel):
    type: str = "object"
    properties: Dict[str, Property]
    required: List[str]


class Function(BaseModel):
    name: str
    description: str
    parameters: Parameters


class Tool(BaseModel):
    type: Literal["function", "agent"]
    function: Function


# audience research output
class AudienceResearchOut(BaseModel):
    keywords: List[str]
    interests: List[str]
    pain_points: List[str]


# content generation output
class ContentGenOut(BaseModel):
    ad_copies: List[str] = Field(max_length=2)
    emails: List[str] = Field(max_length=2)
    social_posts: List[str] = Field(max_length=2)
