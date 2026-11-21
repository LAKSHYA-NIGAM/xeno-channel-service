import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.channel_quota import ChannelQuotaManager


class TestChannelQuota(unittest.TestCase):
    def test_allocates_quota_within_limits(self):
        manager = ChannelQuotaManager()
        res = manager.check_quota('sms', 500)
        self.assertTrue(res['allowed'])
        self.assertEqual(res['current_usage'], 500)
        self.assertEqual(res['remaining_quota'], 49500)

    def test_rejects_exceeded_quota(self):
        manager = ChannelQuotaManager()
        # SMS quota is 50,000
        res = manager.check_quota('sms', 60000)
        self.assertFalse(res['allowed'])
        self.assertIn('Daily quota of 50000 exceeded', res['reason'])

    def test_unsupported_channel(self):
        manager = ChannelQuotaManager()
        res = manager.check_quota('carrier_pigeon')
        self.assertFalse(res['allowed'])


if __name__ == '__main__':
    unittest.main()
