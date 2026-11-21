import unittest
from unittest.mock import patch
from fastapi import BackgroundTasks
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAPIEndpoints(unittest.TestCase):
    def test_health_check_endpoint(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "xeno-channel-service")
        self.assertIn("supported_channels", data)
        self.assertIn("whatsapp", data["supported_channels"])

    def test_send_valid_batch_accepted(self):
        payload = {
            "campaign_id": "cmp_12345",
            "channel": "email",
            "messages": [
                {
                    "recipient_id": "rec_001",
                    "destination": "user@example.com",
                    "message": "Hello from Xeno CRM!",
                    "metadata": {"campaign_recipient_id": "cr_001"}
                }
            ]
        }
        with patch.object(BackgroundTasks, "add_task") as mock_add_task:
            response = client.post("/send", json=payload)
            self.assertEqual(response.status_code, 202)
            data = response.json()
            self.assertTrue(data["accepted"])
            self.assertEqual(data["message_count"], 1)
            self.assertTrue(data["batch_id"].startswith("batch_"))
            mock_add_task.assert_called_once()

    def test_send_unsupported_channel_rejected(self):
        payload = {
            "campaign_id": "cmp_12345",
            "channel": "carrier_pigeon",
            "messages": [
                {
                    "recipient_id": "rec_001",
                    "destination": "user@example.com",
                    "message": "Hello!",
                    "metadata": {"campaign_recipient_id": "cr_001"}
                }
            ]
        }
        response = client.post("/send", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_send_empty_messages_rejected(self):
        payload = {
            "campaign_id": "cmp_12345",
            "channel": "whatsapp",
            "messages": []
        }
        response = client.post("/send", json=payload)
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
