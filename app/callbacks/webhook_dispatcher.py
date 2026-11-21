"""
HMAC Signed Webhook Dispatcher
Secures asynchronous event delivery to CRM receipt endpoints using HMAC-SHA256
signature headers, idempotency tracking, and retry backoffs.
"""

import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional, Tuple


class WebhookDispatcher:
    def __init__(self, secret_key: str = "xeno_default_shared_secret", max_retries: int = 3, timeout_sec: int = 5):
        self.secret_key = secret_key.encode("utf-8")
        self.max_retries = max_retries
        self.timeout_sec = timeout_sec
        # Set of delivered event IDs to guarantee idempotency
        self.dispatched_event_ids = set()

    def generate_signature(self, payload: Dict[str, Any], timestamp: int) -> str:
        """
        Generates HMAC-SHA256 signature over timestamp.serialized_payload.
        Standard Stripe-style webhook signing.
        """
        payload_str = json.dumps(payload, sort_keys=True)
        to_sign = f"{timestamp}.{payload_str}".encode("utf-8")
        return hmac.new(self.secret_key, to_sign, hashlib.sha256).hexdigest()

    def verify_signature(self, payload: Dict[str, Any], timestamp: int, signature: str, tolerance_sec: int = 300) -> bool:
        """
        Verifies received webhook signature within acceptable timestamp drift window.
        """
        current_time = int(time.time())
        if abs(current_time - timestamp) > tolerance_sec:
            return False  # Expired or replay attack

        expected = self.generate_signature(payload, timestamp)
        return hmac.compare_digest(expected, signature)

    def prepare_headers(self, payload: Dict[str, Any], event_id: str) -> Dict[str, str]:
        """Prepares request headers including timestamp, signature, and idempotency key."""
        timestamp = int(time.time())
        sig = self.generate_signature(payload, timestamp)
        return {
            "Content-Type": "application/json",
            "X-Timestamp": str(timestamp),
            "X-Signature": sig,
            "X-Idempotency-Key": event_id
        }

    def dispatch_event(self, event_id: str, payload: Dict[str, Any], transport_call: Any) -> Tuple[bool, str]:
        """
        Dispatches payload via callable transport with idempotency deduplication.
        """
        if event_id in self.dispatched_event_ids:
            return True, "Deduplicated: event previously dispatched"

        headers = self.prepare_headers(payload, event_id)
        attempts = 0

        while attempts < self.max_retries:
            attempts += 1
            try:
                success = transport_call(payload, headers)
                if success:
                    self.dispatched_event_ids.add(event_id)
                    return True, f"Dispatched successfully on attempt {attempts}"
            except Exception as e:
                if attempts >= self.max_retries:
                    return False, f"Delivery failed after {attempts} attempts: {str(e)}"
                time.sleep(0.01 * attempts)

        return False, f"Delivery failed after {attempts} attempts"
