import time
import unittest
from app.callbacks.webhook_dispatcher import WebhookDispatcher


class TestWebhookDispatcher(unittest.TestCase):
    def setUp(self):
        self.secret = "test_shared_secret_123"
        self.dispatcher = WebhookDispatcher(secret_key=self.secret, max_retries=3)
        self.payload = {
            "campaign_recipient_id": "cr_test_99",
            "status": "delivered",
            "channel": "whatsapp"
        }

    def test_signature_generation_deterministic(self):
        ts = 1700000000
        sig1 = self.dispatcher.generate_signature(self.payload, ts)
        sig2 = self.dispatcher.generate_signature(self.payload, ts)
        self.assertEqual(sig1, sig2)
        self.assertEqual(len(sig1), 64)  # SHA-256 hex length

    def test_signature_verification_success(self):
        ts = int(time.time())
        sig = self.dispatcher.generate_signature(self.payload, ts)
        is_valid = self.dispatcher.verify_signature(self.payload, ts, sig)
        self.assertTrue(is_valid)

    def test_tampered_payload_rejected(self):
        ts = int(time.time())
        sig = self.dispatcher.generate_signature(self.payload, ts)
        tampered = dict(self.payload)
        tampered["status"] = "failed"
        is_valid = self.dispatcher.verify_signature(tampered, ts, sig)
        self.assertFalse(is_valid)

    def test_expired_timestamp_rejected_for_replay_protection(self):
        expired_ts = int(time.time()) - 1000  # 1000s in the past (> 300s tolerance)
        sig = self.dispatcher.generate_signature(self.payload, expired_ts)
        is_valid = self.dispatcher.verify_signature(self.payload, expired_ts, sig, tolerance_sec=300)
        self.assertFalse(is_valid)

    def test_idempotent_deduplication(self):
        calls = []

        def mock_transport(payload, headers):
            calls.append(payload)
            return True

        ok1, msg1 = self.dispatcher.dispatch_event("evt_1", self.payload, mock_transport)
        self.assertTrue(ok1)
        self.assertEqual(len(calls), 1)

        # Re-dispatching exact same event_id is skipped and flagged deduplicated
        ok2, msg2 = self.dispatcher.dispatch_event("evt_1", self.payload, mock_transport)
        self.assertTrue(ok2)
        self.assertIn("Deduplicated", msg2)
        self.assertEqual(len(calls), 1)  # transport was not invoked a 2nd time


if __name__ == "__main__":
    unittest.main()
