"""Cryptographic agent session fingerprinting and anti-replay guard."""
import hmac
import hashlib
import time
from typing import Dict, List, Optional, Tuple, Any

class SessionTicket:
    def __init__(self, session_id: str, agent_id: str, fingerprint: str, secret_key: str):
        self.session_id = session_id
        self.agent_id = agent_id
        self.fingerprint = fingerprint
        self.secret_key = secret_key.encode("utf-8")
        self.last_nonce = 0
        self.is_revoked = False

class SessionHijackingGuard:
    """Guards multi-step agent sessions against hijacking and replays."""

    def __init__(self):
        self.sessions: Dict[str, SessionTicket] = {}

    def create_session(self, session_id: str, agent_id: str, fingerprint: str, secret_key: str) -> SessionTicket:
        ticket = SessionTicket(session_id, agent_id, fingerprint, secret_key)
        self.sessions[session_id] = ticket
        return ticket

    def validate_request(self, session_id: str, fingerprint: str, nonce: int, payload: str, signature: str) -> Tuple[bool, str]:
        ticket = self.sessions.get(session_id)
        if not ticket or ticket.is_revoked:
            return False, "Session does not exist or has been revoked"

        if ticket.fingerprint != fingerprint:
            ticket.is_revoked = True
            return False, "Fingerprint mismatch! Session hijacked and revoked."

        if nonce <= ticket.last_nonce:
            ticket.is_revoked = True
            return False, f"Replay detected: nonce {nonce} <= last {ticket.last_nonce}. Session revoked."

        # Verify signature
        expected = hmac.new(ticket.secret_key, f"{nonce}:{payload}".encode("utf-8"), hashlib.sha256).hexdigest()
        if expected != signature:
            return False, "Invalid signature: payload tampered"

        ticket.last_nonce = nonce
        return True, "Valid authenticated request"
