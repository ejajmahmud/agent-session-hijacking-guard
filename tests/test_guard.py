"""Unit tests for agent-session-hijacking-guard."""
import unittest
import hmac
import hashlib
from agent_session_hijacking_guard.guard import SessionHijackingGuard

class TestSessionGuard(unittest.TestCase):
    def setUp(self):
        self.guard = SessionHijackingGuard()
        self.ticket = self.guard.create_session("s1", "a1", "fp1", "key123")

    def test_valid_sequential_requests(self):
        sig = hmac.new(self.ticket.secret_key, b"1:data", hashlib.sha256).hexdigest()
        ok, msg = self.guard.validate_request("s1", "fp1", 1, "data", sig)
        self.assertTrue(ok)

    def test_fingerprint_mismatch_revokes(self):
        sig = hmac.new(self.ticket.secret_key, b"1:data", hashlib.sha256).hexdigest()
        ok, msg = self.guard.validate_request("s1", "attacker_fp", 1, "data", sig)
        self.assertFalse(ok)
        self.assertTrue(self.ticket.is_revoked)

    def test_replay_attack_rejected(self):
        sig1 = hmac.new(self.ticket.secret_key, b"1:data", hashlib.sha256).hexdigest()
        self.guard.validate_request("s1", "fp1", 1, "data", sig1)
        ok, msg = self.guard.validate_request("s1", "fp1", 1, "data", sig1)
        self.assertFalse(ok)
        self.assertIn("Replay detected", msg)

if __name__ == "__main__":
    unittest.main()
