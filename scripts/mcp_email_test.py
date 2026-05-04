#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manual MCP Email Test - Test sending email via MCP server.

Usage:
    python scripts\mcp_email_test.py recipient@example.com
"""

import sys
import json
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp_email_server import EmailMCPServer


async def test_mcp_email(recipient: str):
    """Test sending email via MCP."""
    print("=" * 70)
    print("MCP EMAIL TEST")
    print("=" * 70)
    print(f"To: {recipient}")
    print()
    
    # Initialize email service
    email_service = EmailMCPServer()
    
    # Authenticate
    print("Step 1: Authenticating...")
    if not email_service.authenticate():
        print("[FAILED] Authentication failed")
        return False
    
    print("[OK] Authenticated")
    print()
    
    # Send email
    print("Step 2: Sending email...")
    result = email_service.send_email(
        to=recipient,
        subject="Test Email from MCP Server",
        body="This is a test email sent via MCP (Model Context Protocol).\n\nThis demonstrates that the AI Employee can send emails automatically.\n\nBest regards,\nAI Employee"
    )
    
    print()
    if result.get('status') == 'success':
        print("[SUCCESS] Email sent via MCP!")
        print(f"Message ID: {result.get('message_id')}")
        return True
    else:
        print("[FAILED] Email not sent")
        print(f"Error: {result.get('message')}")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts\\mcp_email_test.py recipient@example.com")
        sys.exit(1)
    
    recipient = sys.argv[1]
    
    success = asyncio.run(test_mcp_email(recipient))
    
    print()
    print("=" * 70)
    if success:
        print("MCP EMAIL TEST PASSED")
    else:
        print("MCP EMAIL TEST FAILED")
    print("=" * 70)
