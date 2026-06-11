import httpx
import json
import uuid
from datetime import datetime, timezone
from app.core.config import settings


async def emit_callback(
    campaign_recipient_id: str,
    provider_message_id: str,
    event_type: str,
    channel: str,
    max_retries: int = 3,
):
    """
    Posts a single delivery event to the CRM receipt endpoint.
    Retries up to 3 times with exponential backoff if the CRM is temporarily unavailable.
    dedupe_key ensures the CRM ignores duplicate callbacks.
    """
    payload = {
        "campaign_recipient_id": campaign_recipient_id,
        "provider_message_id": provider_message_id,
        "event_type": event_type,
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": {"channel": channel},
        "dedupe_key": f"{provider_message_id}:{event_type}",
    }

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.post(
                    settings.CRM_RECEIPT_URL,
                    json=payload,
                )
                response.raise_for_status()
                return  # Success
        except Exception as e:
            if attempt == max_retries - 1:
                # Final attempt failed — log and move on, never crash the simulator
                print(f"[Callback failed] {event_type} for {campaign_recipient_id}: {e}")
            else:
                # Exponential backoff: 1s, 2s, 4s
                import asyncio
                await asyncio.sleep(2 ** attempt)


async def emit_campaign_complete(campaign_id: str):
    """
    Notify the CRM that simulation for the campaign is complete.
    """
    url = settings.CRM_RECEIPT_URL.replace("/receipts", f"/campaigns/{campaign_id}/complete")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url)
            response.raise_for_status()
    except Exception as e:
        print(f"[Callback failed] Campaign complete notification failed for {campaign_id}: {e}")
