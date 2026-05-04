#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Email Server - Send emails via Gmail API.

This MCP server allows Qwen Code to send emails through Gmail.

Usage:
    python scripts/mcp_email_server.py

Configuration:
    - Set GMAIL_CREDENTIALS_PATH environment variable
    - Or use default: ./credentials.json
"""

import os
import sys
import json
import base64
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    import asyncio
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP library not installed. Install with: pip install mcp")
    sys.exit(1)

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("Gmail API libraries not installed. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


class EmailMCPServer:
    """MCP Server for Gmail operations."""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.credentials_path = self.vault_path.parent / 'credentials.json'
        self.token_path = self.vault_path / '.gmail_token.json'
        self.service = None
        self.authenticated = False
    
    def authenticate(self) -> bool:
        """Authenticate with Gmail API."""
        if not GMAIL_AVAILABLE:
            return False
        
        creds = None
        
        # Load existing token
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), self.SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    print(f"Credentials file not found: {self.credentials_path}")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save token for future use
            with open(self.token_path, 'w', encoding='utf-8') as f:
                f.write(creds.to_json())
        
        # Build service
        self.service = build('gmail', 'v1', credentials=creds)
        self.authenticated = True
        print("[OK] Gmail authenticated")
        return True
    
    def send_email(self, to: str, subject: str, body: str, 
                   from_email: str = "me", cc: str = None, 
                   bcc: str = None) -> dict:
        """
        Send an email via Gmail API.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            from_email: Sender email (default: "me")
            cc: CC email addresses (comma-separated)
            bcc: BCC email addresses (comma-separated)
            
        Returns:
            dict with status and message_id
        """
        if not self.authenticated:
            if not self.authenticate():
                return {"status": "error", "message": "Not authenticated"}
        
        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['from'] = from_email
            message['subject'] = subject
            
            if cc:
                message['cc'] = cc
            if bcc:
                message['bcc'] = bcc
            
            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                "status": "success",
                "message_id": sent_message.get('id'),
                "thread_id": sent_message.get('threadId')
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def mark_as_read(self, message_id: str) -> dict:
        """Mark an email as read."""
        if not self.authenticated:
            return {"status": "error", "message": "Not authenticated"}
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            return {
                "status": "success",
                "message_id": message_id
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# Create MCP server instance
server = Server("email-server")
email_service = None


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available email tools."""
    return [
        Tool(
            name="send_email",
            description="Send an email via Gmail. Use this to reply to emails or send new messages.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body text"
                    },
                    "cc": {
                        "type": "string",
                        "description": "CC email addresses (comma-separated)"
                    },
                    "bcc": {
                        "type": "string",
                        "description": "BCC email addresses (comma-separated)"
                    }
                },
                "required": ["to", "subject", "body"]
            }
        ),
        Tool(
            name="mark_email_read",
            description="Mark a Gmail message as read.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "Gmail message ID to mark as read"
                    }
                },
                "required": ["message_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    global email_service
    
    if email_service is None:
        email_service = EmailMCPServer()
    
    if name == "send_email":
        result = email_service.send_email(
            to=arguments.get("to"),
            subject=arguments.get("subject"),
            body=arguments.get("body"),
            cc=arguments.get("cc"),
            bcc=arguments.get("bcc")
        )
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    elif name == "mark_email_read":
        result = email_service.mark_as_read(
            message_id=arguments.get("message_id")
        )
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == '__main__':
    if not MCP_AVAILABLE:
        print("Error: MCP library not installed")
        sys.exit(1)
    
    asyncio.run(main())
