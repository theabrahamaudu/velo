from pydantic import BaseModel, Field
from typing import Any, Literal, Optional, List, Dict
from datetime import datetime


# tool call
class FunctionToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]


class ToolCall(BaseModel):
    function: FunctionToolCall


# ollama message
class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    thinking: Optional[str] = None
    images: Optional[List[str]] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_name: Optional[str] = None


# stable diffusion message
class SDMessage(BaseModel):
    prompt: str = Field(max_length=300)
    negative_prompt: str = Field(max_length=300)
    width: int = 768
    height: int = 512


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
class AdCopy(BaseModel):
    channel: str
    content: str


class Email(BaseModel):
    title: str
    body: str


class SocialPost(BaseModel):
    platform: str
    post: str


class ContentGenOut(BaseModel):
    ad_copies: List[AdCopy] = Field(min_length=2, max_length=2)
    emails: List[Email] = Field(min_length=2, max_length=2)
    social_posts: List[SocialPost] = Field(min_length=2, max_length=2)


# schedule creation output
class Schedule(BaseModel):
    platform: str
    content_type: Literal["ad_copy", "email", "social_post"]
    datetime: datetime
    content_idx: int = Field(lt=2)


class ScheduleGenOut(BaseModel):
    schedule: List[Schedule]


# scheduled content
class ScheduledContent(BaseModel):
    platform: str
    content_type: str
    datetime: datetime
    content_title: str
    content_body: str
