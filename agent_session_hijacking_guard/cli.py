"""CLI for agent-session-hijacking-guard."""
import sys
import argparse
import hmac
import hashlib
from .guard import SessionHijackingGuard

def main():
    parser = argparse.ArgumentParser(description="Agent Session Hijacking Guard CLI")
    parser.add_argument("--demo", action="store_true", help="Run session hijacking guard demo")
    args = parser.parse_args()

    if args.demo:
        guard = SessionHijackingGuard()
        ticket = guard.create_session("sess_101", "agent_worker", "fp_host_abc", "secret_pass_123")
        payload = "task=summarize"
        sig = hmac.new(ticket.secret_key, f"1:{payload}".encode("utf-8"), hashlib.sha256).hexdigest()
        ok1, msg1 = guard.validate_request("sess_101", "fp_host_abc", 1, payload, sig)
        print(f"[+] Request 1: ok={ok1}, msg='{msg1}'")
        # Attacker tries replay with nonce 1
        ok2, msg2 = guard.validate_request("sess_101", "fp_host_abc", 1, payload, sig)
        print(f"[!] Replay attempt: ok={ok2}, msg='{msg2}'")
    else:
        parser.print_help()
    sys.exit(0)

if __name__ == "__main__":
    main()
