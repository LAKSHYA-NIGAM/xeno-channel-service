"""
Dead-Letter Queue (DLQ) Retry Coordinator
Calculates exponential backoff delay with full jitter for failed message delivery attempts,
enforcing maximum retry caps before escalating to persistent DLQ.
"""

import random
from typing import Dict, Any


def compute_retry_delay(
  attempt: int,
  base_delay_sec: float = 1.0,
  max_delay_sec: float = 60.0,
  max_retries: int = 5,
) -> Dict[str, Any]:
  if attempt >= max_retries:
    return {
      'should_retry': False,
      'delay_seconds': 0.0,
      'is_dlq_eligible': True,
      'reason': f"Max retry threshold ({max_retries}) exceeded. Escalated to DLQ.",
    }

  # Exponential backoff: min(max_delay, base_delay * 2^attempt)
  raw_backoff = min(max_delay_sec, base_delay_sec * (2 ** attempt))

  # Full Jitter: random uniform between 0 and raw_backoff
  jittered_delay = round(random.uniform(raw_backoff * 0.5, raw_backoff), 2)

  return {
    'should_retry': True,
    'delay_seconds': jittered_delay,
    'attempt_number': attempt + 1,
    'max_retries': max_retries,
    'is_dlq_eligible': False,
  }
