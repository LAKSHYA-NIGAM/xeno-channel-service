import unittest
from unittest.mock import patch
from app.simulator.engine import decide_events
from app.simulator.probabilities import CHANNEL_PROBABILITIES, EVENT_DELAYS


class TestProbabilityEngine(unittest.TestCase):
    def test_supported_channels_configured(self):
        self.assertIn("whatsapp", CHANNEL_PROBABILITIES)
        self.assertIn("email", CHANNEL_PROBABILITIES)
        self.assertIn("sms", CHANNEL_PROBABILITIES)

        for channel, probs in CHANNEL_PROBABILITIES.items():
            self.assertIn("delivered", probs)
            self.assertTrue(0 < probs["delivered"] <= 1.0)

    def test_delays_configured_properly(self):
        for event, (min_d, max_d) in EVENT_DELAYS.items():
            self.assertGreater(min_d, 0, f"Min delay for {event} must be > 0")
            self.assertGreaterEqual(max_d, min_d, f"Max delay for {event} must be >= min delay")

    def test_events_always_start_with_sent(self):
        for channel in ["whatsapp", "email", "sms"]:
            for _ in range(50):
                events = decide_events(channel)
                self.assertGreater(len(events), 0)
                self.assertEqual(events[0], "sent")

    def test_whatsapp_progressive_events_success(self):
        # Force all random choices to return 0.0 (always trigger progressive steps)
        with patch("random.random", return_value=0.0):
            events = decide_events("whatsapp")
            self.assertEqual(events, ["sent", "delivered", "read", "clicked"])

    def test_whatsapp_failure_branch(self):
        # Force random choice to fail delivery (return 0.99 > 0.95)
        with patch("random.random", return_value=0.99):
            events = decide_events("whatsapp")
            self.assertEqual(events, ["sent", "failed"])

    def test_email_progressive_events_success(self):
        with patch("random.random", return_value=0.0):
            events = decide_events("email")
            self.assertEqual(events, ["sent", "delivered", "opened", "clicked"])

    def test_email_failure_branch(self):
        with patch("random.random", return_value=0.99):
            events = decide_events("email")
            self.assertEqual(events, ["sent", "failed"])

    def test_sms_progressive_events_success(self):
        with patch("random.random", return_value=0.0):
            events = decide_events("sms")
            self.assertEqual(events, ["sent", "delivered", "clicked"])

    def test_unknown_channel_defaults_to_email_logic(self):
        with patch("random.random", return_value=0.0):
            events = decide_events("custom_channel")
            self.assertEqual(events, ["sent", "delivered", "opened", "clicked"])


if __name__ == "__main__":
    unittest.main()
