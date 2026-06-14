import asyncio
import random
import uuid
from datetime import datetime, timezone
from app.simulator.probabilities import CHANNEL_PROBABILITIES, EVENT_DELAYS
from app.callbacks.emitter import emit_callback, emit_campaign_complete


def decide_events(channel: str) -> list[str]:
    """
    Decide which events this recipient will receive based on channel probabilities.
    Events are progressive — a recipient cannot get 'read' without 'delivered' first.
    Always starts with 'sent'.
    """
    probs = CHANNEL_PROBABILITIES.get(channel, CHANNEL_PROBABILITIES["email"])
    events = ["sent"]

    if channel == "whatsapp":
        if random.random() < probs["delivered"]:
            events.append("delivered")
            if random.random() < probs["read"]:
                events.append("read")
                if random.random() < probs["clicked"]:
                    events.append("clicked")
        else:
            events.append("failed")

    elif channel == "email":
        if random.random() < probs["delivered"]:
            events.append("delivered")
            if random.random() < probs["opened"]:
                events.append("opened")
                if random.random() < probs["clicked"]:
                    events.append("clicked")
        else:
            events.append("failed")

    elif channel == "sms":
        if random.random() < probs["delivered"]:
            events.append("delivered")
            if random.random() < probs["clicked"]:
                events.append("clicked")
        else:
            events.append("failed")

    return events


# Concurrency limit to prevent exhausting HTTP connection pools and ports on free hosting tiers
SIMULATION_SEMAPHORE = asyncio.Semaphore(15)


async def simulate_message(
    campaign_recipient_id: str,
    channel: str,
    provider_message_id: str,
):
    """
    Simulates the full delivery lifecycle for a single message.
    Fires each event after a realistic delay via asyncio.sleep.
    Each event is sent to the CRM receipt endpoint as an async callback.
    """
    async with SIMULATION_SEMAPHORE:
        events = decide_events(channel)

        for event_type in events:
            delay_min, delay_max = EVENT_DELAYS.get(event_type, (2, 5))
            await asyncio.sleep(random.uniform(delay_min, delay_max))

            await emit_callback(
                campaign_recipient_id=campaign_recipient_id,
                provider_message_id=provider_message_id,
                event_type=event_type,
                channel=channel,
            )


async def simulate_batch(campaign_id: str, messages: list[dict], channel: str):
    """
    Runs simulation for all messages in a batch concurrently.
    Each message gets its own asyncio task so delays are independent.
    """
    tasks = []
    for msg in messages:
        provider_message_id = f"msg_{uuid.uuid4().hex[:12]}"
        task = asyncio.create_task(
            simulate_message(
                campaign_recipient_id=msg["metadata"]["campaign_recipient_id"],
                channel=channel,
                provider_message_id=provider_message_id,
            )
        )
        tasks.append(task)

    # Await all tasks concurrently in the background task context
    if tasks:
        await asyncio.gather(*tasks)

    # Notify CRM that all simulation tasks are complete
    await emit_campaign_complete(campaign_id)
