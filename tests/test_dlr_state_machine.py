import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.dlr_state_machine import transition_message_status


class TestDlrStateMachine(unittest.TestCase):
    def test_valid_forward_flow(self):
        # QUEUED -> SENT -> DELIVERED
        t1 = transition_message_status('QUEUED', 'SENT')
        self.assertTrue(t1['valid'])
        self.assertFalse(t1['is_terminal'])

        t2 = transition_message_status('SENT', 'DELIVERED')
        self.assertTrue(t2['valid'])
        self.assertTrue(t2['is_terminal'])

    def test_illegal_backward_or_skip_transition(self):
        # Cannot go DELIVERED -> SENT (terminal)
        t_bad1 = transition_message_status('DELIVERED', 'SENT')
        self.assertFalse(t_bad1['valid'])

        # Cannot jump QUEUED -> DELIVERED without being SENT
        t_bad2 = transition_message_status('QUEUED', 'DELIVERED')
        self.assertFalse(t_bad2['valid'])


if __name__ == '__main__':
    unittest.main()
