import uuid
import asyncio
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from app.simulator.engine import simulate_batch

router = APIRouter()


class Message(BaseModel):
    recipient_id: str
    destination: str
    message: str
    metadata: dict


class SendRequest(BaseModel):
    campaign_id: str
    channel: str
    messages: list[Message]


class SendResponse(BaseModel):
    accepted: bool
    batch_id: str
    message_count: int


@router.post("/send", response_model=SendResponse)
async def send_messages(request: SendRequest, background_tasks: BackgroundTasks):
    """
    Accepts a batch of messages from the CRM.
    Responds immediately with acceptance (batch_id).
    Runs simulation asynchronously in the background — CRM does not wait.
    This is the async callback pattern the assignment requires.
    """
    batch_id = f"batch_{uuid.uuid4().hex[:10]}"

    # Schedule simulation as background task — returns immediately
    background_tasks.add_task(
        simulate_batch,
        campaign_id=request.campaign_id,
        messages=[msg.dict() for msg in request.messages],
        channel=request.channel,
    )

    return SendResponse(
        accepted=True,
        batch_id=batch_id,
        message_count=len(request.messages),
    )
