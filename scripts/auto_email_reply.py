#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Email Reply - Automatically reply to emails in Needs_Action folder.

This script reads email action files and sends replies via MCP Email Server.

Usage:
    python scripts\auto_email_reply.py AI_Employee_Vault
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from mcp_email_server import EmailMCPServer


def extract_email_info(filepath: Path) -> dict:
    """Extract email information from action file."""
    content = filepath.read_text(encoding='utf-8')
    
    info = {
        'from': '',
        'subject': '',
        'content': '',
        'type': 'unknown'
    }
    
    # Parse frontmatter
    if '---' in content:
        parts = content.split('---')
        if len(parts) >= 2:
            frontmatter = parts[1]
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key in info:
                        info[key] = value
    
    # Extract content from markdown
    if '## Email Content' in content:
        content_part = content.split('## Email Content')[1]
        if '##' in content_part:
            content_part = content_part.split('##')[0]
        info['content'] = content_part.strip()
    elif '## Message Content' in content:
        content_part = content.split('## Message Content')[1]
        if '##' in content_part:
            content_part = content_part.split('##')[0]
        info['content'] = content_part.strip()
    
    return info


def generate_reply(email_info: dict) -> str:
    """Generate appropriate reply based on email content."""
    from_email = email_info.get('from', '')
    subject = email_info.get('subject', '')
    content = email_info.get('content', '')
    
    # Check for invoice request
    if 'invoice' in subject.lower() or 'invoice' in content.lower():
        return f"""Dear {from_email.split('@')[0]},

Thank you for your email regarding the invoice request.

We have received your request and are processing it. The invoice will be sent to you within 24 hours.

If you have any urgent questions, please don't hesitate to contact us.

Best regards,
AI Employee
Automated Response System"""
    
    # Check for security email (Google, etc.)
    if 'security' in subject.lower() or 'google' in from_email.lower():
        return f"""Thank you for the security notification.

We have reviewed the security alert and will take appropriate action if needed.

Best regards,
AI Employee"""
    
    # Default reply
    return f"""Dear {from_email.split('@')[0]},

Thank you for your email.

We have received your message and will respond shortly.

Best regards,
AI Employee
Automated Response System"""


def auto_reply_emails(vault_path: str):
    """Process all email files and send replies."""
    vault = Path(vault_path)
    done = vault / 'Done'
    logs = vault / 'Logs'
    
    # Ensure folders exist
    done.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    
    # Initialize email service
    email_service = EmailMCPServer(str(vault))
    
    print("=" * 70)
    print("AUTO EMAIL REPLY")
    print("=" * 70)
    print()
    
    # Authenticate
    print("Step 1: Authenticating with Gmail...")
    if not email_service.authenticate():
        print("[FAILED] Authentication failed")
        return 0
    
    print("[OK] Authenticated")
    print()
    
    # Get all email files in Done folder (already moved by orchestrator)
    # For first run, also check Needs_Action
    email_files = list((vault / 'Needs_Action').glob('EMAIL_*.md'))
    if not email_files:
        email_files = list((vault / 'Done').glob('EMAIL_*.md'))
    
    if not email_files:
        print("No email files found.")
        return 0
    
    print(f"Found {len(email_files)} email(s) to process")
    print()
    
    replied_count = 0
    
    for email_file in email_files:
        print(f"Processing: {email_file.name}")
        
        try:
            # Extract email info
            email_info = extract_email_info(email_file)
            
            print(f"  From: {email_info['from']}")
            print(f"  Subject: {email_info['subject']}")
            
            # Generate reply
            reply = generate_reply(email_info)
            
            # Send reply
            print("  Sending reply...")
            result = email_service.send_email(
                to=email_info['from'],
                subject=f"Re: {email_info['subject']}",
                body=reply
            )
            
            if result.get('status') == 'success':
                print(f"  [OK] Reply sent! Message ID: {result.get('message_id')}")
                replied_count += 1
                
                # Log the reply
                log_reply(logs, email_file.name, email_info['from'], result.get('message_id'))
            else:
                print(f"  [FAILED] {result.get('message')}")
            
            print()
            
        except Exception as e:
            print(f"  [ERROR] {e}")
            print()
    
    print("=" * 70)
    print(f"Replied to {replied_count}/{len(email_files)} email(s)")
    print("=" * 70)
    
    return replied_count


def log_reply(logs_dir: Path, email_file: str, recipient: str, message_id: str):
    """Log email reply to JSONL."""
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = logs_dir / f'{today}.jsonl'
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action_type': 'email_reply_sent',
        'email_file': email_file,
        'recipient': recipient,
        'message_id': message_id,
        'actor': 'auto_email_reply'
    }
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f'{log_entry}\n')


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts\\auto_email_reply.py <vault_path>")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    vault = Path(vault_path)
    
    if not vault.exists():
        print(f"Error: Vault path does not exist: {vault}")
        sys.exit(1)
    
    count = auto_reply_emails(str(vault))
    
    if count > 0:
        print(f"\n[SUCCESS] Sent {count} reply email(s)!")
    else:
        print("\n[INFO] No replies sent.")


if __name__ == '__main__':
    main()
