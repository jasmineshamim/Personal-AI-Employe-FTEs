#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test MCP Email Server - Send a test email.

Usage:
    python scripts\test_mcp_email.py recipient@example.com
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp_email_server import EmailMCPServer


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts\\test_mcp_email.py recipient@example.com")
        sys.exit(1)
    
    recipient = sys.argv[1]
    
    print("=" * 70)
    print("MCP EMAIL SERVER - TEST")
    print("=" * 70)
    print(f"To: {recipient}")
    print()
    
    # Initialize email service
    email_service = EmailMCPServer()
    
    # Authenticate
    print("Step 1: Authenticating with Gmail...")
    if not email_service.authenticate():
        print("[FAILED] Authentication failed")
        sys.exit(1)
    
    print("[OK] Authenticated")
    print()
    
    # Send test email
    print("Step 2: Sending test email...")
    result = email_service.send_email(
        to=recipient,
        subject="Test Email from AI Employee MCP Server",
        body="This is a test email sent from the AI Employee MCP Email Server.\n\nIf you receive this, the MCP server is working correctly!\n\nBest regards,\nAI Employee"
    )
    
    if result.get('status') == 'success':
        print()
        print("[SUCCESS] Email sent!")
        print(f"Message ID: {result.get('message_id')}")
        print(f"Thread ID: {result.get('thread_id')}")
    else:
        print()
        print("[FAILED] Email not sent")
        print(f"Error: {result.get('message')}")
        sys.exit(1)
    
    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
