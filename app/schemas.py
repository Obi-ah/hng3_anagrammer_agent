from uuid import uuid4

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any, TypeAlias
from datetime import datetime, timezone


# ---- Inner Data Structures ----

class InnerDataItem(BaseModel):
    kind: Literal["text"]
    text: str


class MessagePartData(BaseModel):
    kind: Literal["data"]
    data: List[InnerDataItem]


class MessagePartText(BaseModel):
    kind: Literal["text"]
    text: str


# ---- Metadata ----

class MessageMetadata(BaseModel):
    telex_user_id: str
    telex_channel_id: str
    org_id: str


# ---- Message ----

class A2AMessage(BaseModel):
    kind: Literal["message"] = 'message'
    role: Literal["user", "agent", "system"]
    parts: List[MessagePartText | MessagePartData]
    messageId: str = Field(default_factory=lambda: str(uuid4()))
    taskId: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# ---- Push Notification Config ----

class AuthenticationConfig(BaseModel):
    schemes: List[str]


class PushNotificationConfig(BaseModel):
    url: str
    token: Optional[str] = None
    authentication: Optional[AuthenticationConfig] = None


class MessageConfiguration(BaseModel):
    acceptedOutputModes: Optional[List[str]] = None
    historyLength: Optional[int] = 0
    pushNotificationConfig: Optional[PushNotificationConfig] = None
    blocking: Optional[bool] = True


class MessageParams(BaseModel):
    message: A2AMessage
    configuration: Optional[MessageConfiguration] = Field(default_factory=MessageConfiguration)


# ---- Main Request ----

class JSONRPCRequest(BaseModel):
    jsonrpc: Literal["2.0"]
    id: str
    method: Literal["message/send"]
    params: MessageParams




# Response
class TaskStatus(BaseModel):
    state: Literal["working", "completed", "input-required", "failed"]
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    message: Optional[A2AMessage] = None

class Artifact(BaseModel):
    artifactId: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    parts: List[MessagePartText]

class TaskResult(BaseModel):
    id: str
    contextId: str
    status: TaskStatus
    artifacts: List[Artifact] = []
    history: List[A2AMessage] = []
    kind: Literal["task"] = "task"

class JSONRPCResponse(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: str
    result: Optional[TaskResult] = None
    error: Optional[Dict[str, Any]] = None