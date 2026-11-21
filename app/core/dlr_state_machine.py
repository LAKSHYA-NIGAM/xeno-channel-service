"""
Delivery Status Receipt (DLR) State Machine
Enforces valid forward status transitions for asynchronous message dispatching:
QUEUED -> SENT -> DELIVERED (terminal)
               -> FAILED (terminal)
               -> UNDELIVERED (terminal)
"""

from typing import Dict, Any, Set

VALID_TRANSITIONS: Dict[str, Set[str]] = {
  'QUEUED': {'SENT', 'FAILED'},
  'SENT': {'DELIVERED', 'UNDELIVERED', 'FAILED'},
  'DELIVERED': set(),
  'FAILED': set(),
  'UNDELIVERED': set(),
}


def transition_message_status(current_status: str, new_status: str) -> Dict[str, Any]:
  curr = (current_status or 'QUEUED').strip().upper()
  nxt = (new_status or '').strip().upper()

  allowed_next = VALID_TRANSITIONS.get(curr, set())

  if nxt not in allowed_next:
    return {
      'valid': False,
      'current_status': curr,
      'requested_status': nxt,
      'reason': f"Illegal status transition from '{curr}' to '{nxt}'. Allowed: {list(allowed_next)}",
    }

  return {
    'valid': True,
    'current_status': nxt,
    'is_terminal': len(VALID_TRANSITIONS.get(nxt, set())) == 0,
  }
