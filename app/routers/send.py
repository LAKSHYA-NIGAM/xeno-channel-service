import uuid
import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, List
from app.simulator.engine import simulate_batch
from app.simulator.probabilities import CHANNEL_PROBABILITIES

router = APIRouter()

SUPPORTED_CHANNELS = set(CHANNEL_PROBABILITIES.keys())


class Message(BaseModel):
    recipient_id: str = Field(..., description="Unique CRM recipient identifier")
    destination: str = Field(..., description="Phone number or email destination")
    message: str = Field(..., description="Rendered text body")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata including campaign_recipient_id")

    @field_validator("recipient_id", "destination", "message")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only")
        return v.strip()


class SendRequest(BaseModel):
    campaign_id: str
    channel: str
    messages: List[Message]

    @field_validator("channel")
    @classmethod
    def validate_channel(cls, v: str) -> str:
        clean = v.strip().lower()
        if clean not in SUPPORTED_CHANNELS:
            raise ValueError(f"Unsupported channel '{v}'. Allowed channels: {sorted(SUPPORTED_CHANNELS)}")
        return clean

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v: List[Message]) -> List[Message]:
        if not v:
            raise ValueError("Message batch cannot be empty")
        return v


class SendResponse(BaseModel):
    accepted: bool
    batch_id: str
    message_count: int


@router.post("/send", response_model=SendResponse, status_code=status.HTTP_202_ACCEPTED)
async def send_messages(request: SendRequest, background_tasks: BackgroundTasks):
    """
    Accepts a batch of messages from the CRM.
    Responds immediately with HTTP 202 Accepted and a unique batch_id.
    Executes message delivery simulation asynchronously in the background.
    """
    batch_id = f"batch_{uuid.uuid4().hex[:10]}"

    # Schedule simulation as background task
    background_tasks.add_task(
        simulate_batch,
        campaign_id=request.campaign_id,
        messages=[msg.model_dump() if hasattr(msg, "model_dump") else msg.dict() for msg in request.messages],
        channel=request.channel,
    )

    return SendResponse(
        accepted=True,
        batch_id=batch_id,
        message_count=len(request.messages),
    )
