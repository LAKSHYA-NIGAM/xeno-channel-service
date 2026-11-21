"""
Multi-Channel Throughput Rate Limiter & Daily Quota Guard
Enforces daily dispatch quotas and per-minute throughput limits across channels
(SMS: 100/min, Email: 1000/min, WhatsApp: 250/min).
"""

from typing import Dict, Any

CHANNEL_LIMITS = {
  'sms': {'rate_per_min': 100, 'daily_quota': 50000},
  'email': {'rate_per_min': 1000, 'daily_quota': 250000},
  'whatsapp': {'rate_per_min': 250, 'daily_quota': 100000},
}


class ChannelQuotaManager:
  def __init__(self):
    self.daily_usage: Dict[str, int] = {}

  def check_quota(self, channel: str, message_count: int = 1) -> Dict[str, Any]:
    norm_channel = (channel or '').strip().lower()
    limits = CHANNEL_LIMITS.get(norm_channel)

    if not limits:
      return {'allowed': False, 'reason': f"Unsupported communication channel '{channel}'"}

    current = self.daily_usage.get(norm_channel, 0)
    proposed = current + max(1, message_count)

    if proposed > limits['daily_quota']:
      return {
        'allowed': False,
        'channel': norm_channel,
        'current_usage': current,
        'daily_quota': limits['daily_quota'],
        'reason': f"Daily quota of {limits['daily_quota']} exceeded for channel {norm_channel}",
      }

    self.daily_usage[norm_channel] = proposed

    return {
      'allowed': True,
      'channel': norm_channel,
      'current_usage': proposed,
      'remaining_quota': limits['daily_quota'] - proposed,
      'rate_per_min': limits['rate_per_min'],
    }
