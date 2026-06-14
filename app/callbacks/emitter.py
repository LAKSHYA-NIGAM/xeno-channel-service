import httpx
import asyncio
import json
from datetime import datetime, timezone
from app.core.config import settings


async def emit_callback(
    campaign_recipient_id: str,
    provider_message_id: str,
    event_type: str,
    channel: str,
    max_retries: int = 3,
):
    payload = {
        "campaign_recipient_id": campaign_recipient_id,
        "provider_message_id": provider_message_id,
        "event_type": event_type,
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": {"channel": channel},
        "dedupe_key": f"{provider_message_id}:{event_type}",
    }

    print(f"[EMIT] Firing {event_type} to {settings.CRM_RECEIPT_URL}")

    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    settings.CRM_RECEIPT_URL,
                    json=payload,
                )
                print(f"[EMIT] Response {response.status_code}: {response.text[:100]}")
                if response.status_code == 200:
                    return
        except Exception as e:
            print(f"[EMIT] Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)

    print(f"[EMIT] All retries failed for {event_type} — {campaign_recipient_id}")


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
