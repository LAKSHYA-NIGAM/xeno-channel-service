import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.dlq_retry import compute_retry_delay


class TestDlqRetry(unittest.TestCase):
    def test_exponential_backoff_progression(self):
        r0 = compute_retry_delay(0, base_delay_sec=1.0)
        self.assertTrue(r0['should_retry'])
        self.assertFalse(r0['is_dlq_eligible'])
        self.assertGreaterEqual(r0['delay_seconds'], 0.5)

        r3 = compute_retry_delay(3, base_delay_sec=1.0, max_delay_sec=60.0)
        self.assertTrue(r3['should_retry'])
        self.assertGreaterEqual(r3['delay_seconds'], 4.0)

    def test_exceeding_max_retries_escalates_to_dlq(self):
        r5 = compute_retry_delay(5, max_retries=5)
        self.assertFalse(r5['should_retry'])
        self.assertTrue(r5['is_dlq_eligible'])
        self.assertIn('Escalated to DLQ', r5['reason'])


if __name__ == '__main__':
    unittest.main()
