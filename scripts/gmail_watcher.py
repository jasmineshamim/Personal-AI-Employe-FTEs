#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher - Monitors Gmail for new important emails.

Uses Gmail API to fetch unread emails and creates action files
in the Needs_Action folder for Claude Code to process.

Usage:
    # First-time authentication
    python scripts/gmail_watcher.py AI_Employee_Vault --authenticate

    # Start watching
    python scripts/gmail_watcher.py AI_Employee_Vault

    # Custom interval
    python scripts/gmail_watcher.py AI_Employee_Vault --interval 60
"""

import sys
import os
import pickle
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

# Gmail API imports (optional - will fail gracefully if not installed)
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False


class GmailWatcher(BaseWatcher):
    """Watches Gmail for new important emails."""
    
    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(
        self, 
        vault_path: str, 
        credentials_path: str = 'credentials.json',
        token_path: str = 'token.json',
        check_interval: int = 120,
        keywords: List[str] = None
    ):
        """
        Initialize the Gmail watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            credentials_path: Path to Gmail OAuth credentials JSON
            token_path: Path to store/load authentication token
            check_interval: Seconds between checks (default: 120)
            keywords: List of keywords to filter important emails
        """
        if not GMAIL_AVAILABLE:
            raise ImportError(
                "Gmail API libraries not installed. "
                "Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            )
        
        super().__init__(vault_path, check_interval)
        
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.keywords = keywords or ['urgent', 'asap', 'invoice', 'payment', 'help']
        self.service = None
        self.label_ids = ['INBOX']
    
    def authenticate(self) -> bool:
        """
        Perform OAuth authentication with Gmail.
        
        Returns:
            True if authentication successful
        """
        creds = None
        
        # Load existing token
        if self.token_path.exists():
            with open(self.token_path, 'rb') as f:
                creds = pickle.load(f)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    self.logger.error(f"Credentials file not found: {self.credentials_path}")
                    self.logger.error("Download from Google Cloud Console")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save token for future use
            with open(self.token_path, 'wb') as f:
                pickle.dump(creds, f)
        
        # Build service
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Gmail authentication successful")
        return True
    
    def check_for_updates(self) -> list:
        """
        Check for new unread important emails.
        
        Returns:
            List of message data dictionaries
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        messages = []
        
        try:
            # Search for unread emails in inbox
            # Can customize query: is:unread is:important from:someone@example.com
            query = 'is:unread'
            
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                labelIds=self.label_ids,
                maxResults=10
            ).execute()
            
            message_list = results.get('messages', [])
            
            for msg in message_list:
                if msg['id'] not in self.processed_ids:
                    # Get full message details
                    message = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()
                    
                    # Check if email contains important keywords
                    snippet = message.get('snippet', '').lower()
                    if any(kw in snippet for kw in self.keywords):
                        messages.append(message)
                        self.processed_ids.add(msg['id'])
                    elif not self.keywords:
                        # No keywords set, process all unread
                        messages.append(message)
                        self.processed_ids.add(msg['id'])
        
        except HttpError as error:
            self.logger.error(f"Gmail API error: {error}")
            if error.resp.status == 401:
                # Token expired, force re-auth
                if self.token_path.exists():
                    self.token_path.unlink()
                self.service = None
        
        return messages
    
    def create_action_file(self, message) -> Path:
        """
        Create a .md action file in Needs_Action folder.
        
        Args:
            message: Gmail message data
            
        Returns:
            Path to the created file
        """
        # Extract headers
        headers = {h['name']: h['value'] for h in message['payload']['headers']}
        
        from_email = headers.get('From', 'Unknown')
        subject = headers.get('Subject', 'No Subject')
        date = headers.get('Date', '')
        
        # Get email body
        body = self._extract_body(message)
        
        # Determine priority based on keywords
        priority = 'normal'
        subject_lower = subject.lower()
        if any(kw in subject_lower for kw in ['urgent', 'asap', 'emergency']):
            priority = 'critical'
        elif any(kw in subject_lower for kw in ['invoice', 'payment', 'bill']):
            priority = 'high'
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_subject = "".join(c if c.isalnum() else '_' for c in subject[:30])
        filename = f"EMAIL_{timestamp}_{safe_subject}.md"
        filepath = self.needs_action / filename
        
        # Create action file content
        content = f'''---
type: email
from: {from_email}
subject: {subject}
received: {datetime.now().isoformat()}
date_sent: {date}
priority: {priority}
status: pending
message_id: {message['id']}
---

# Email Received

## Header Information

- **From:** {from_email}
- **Subject:** {subject}
- **Received:** {date}
- **Priority:** {priority}

---

## Email Content

{body}

---

## Suggested Actions

- [ ] Read and understand the email
- [ ] Draft a response (if needed)
- [ ] Take any required actions
- [ ] Mark email as read in Gmail
- [ ] Move this file to /Done when complete

---

## Notes

*Add any notes or context for handling this email*

---
*Generated by GmailWatcher v0.1 (Silver Tier)*
'''
        
        filepath.write_text(content, encoding='utf-8')
        
        self.log_action('email_processed', {
            'from': from_email,
            'subject': subject,
            'priority': priority,
            'action_file': str(filepath)
        })
        
        return filepath
    
    def _extract_body(self, message) -> str:
        """Extract the plain text body from a Gmail message."""
        try:
            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        import base64
                        body_data = base64.urlsafe_b64decode(part['body']['data'])
                        return body_data.decode('utf-8', errors='ignore')
            
            # Fallback to snippet if no plain text part
            return message.get('snippet', '[No content available]')
        
        except Exception as e:
            self.logger.error(f"Error extracting email body: {e}")
            return '[Error extracting content]'
    
    def mark_as_read(self, message_id: str):
        """Mark an email as read in Gmail."""
        if not self.service:
            return
        
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            self.logger.info(f"Marked message {message_id} as read")
        except HttpError as error:
            self.logger.error(f"Error marking as read: {error}")


def main():
    parser = argparse.ArgumentParser(
        description='Gmail Watcher - Monitor Gmail for important emails'
    )
    parser.add_argument(
        'vault_path',
        help='Path to the Obsidian vault root'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=120,
        help='Check interval in seconds (default: 120)'
    )
    parser.add_argument(
        '--credentials', '-c',
        default='credentials.json',
        help='Path to Gmail credentials JSON (default: credentials.json)'
    )
    parser.add_argument(
        '--token', '-t',
        default='token.json',
        help='Path to token file (default: token.json)'
    )
    parser.add_argument(
        '--keywords', '-k',
        default=None,
        help='Comma-separated keywords to filter (default: urgent,asap,invoice,payment,help)'
    )
    parser.add_argument(
        '--authenticate', '-a',
        action='store_true',
        help='Perform authentication only'
    )
    
    args = parser.parse_args()
    
    # Validate vault path
    vault = Path(args.vault_path)
    if not vault.exists():
        print(f"Error: Vault path does not exist: {vault}")
        sys.exit(1)
    
    # Validate credentials file
    creds_path = Path(args.credentials)
    if not creds_path.exists():
        print(f"Error: Credentials file not found: {creds_path}")
        print("Download from Google Cloud Console > API & Services > Credentials")
        sys.exit(1)
    
    # Parse keywords
    keywords = None
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(',')]
    
    # Create watcher
    try:
        watcher = GmailWatcher(
            str(vault),
            credentials_path=args.credentials,
            token_path=args.token,
            check_interval=args.interval,
            keywords=keywords
        )
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Handle authentication mode
    if args.authenticate:
        print("Starting Gmail authentication...")
        print("A browser window will open for you to grant access.")
        if watcher.authenticate():
            print("Authentication successful!")
            print(f"Token saved to: {watcher.token_path}")
        else:
            print("Authentication failed.")
            sys.exit(1)
        return
    
    # Start watching
    print(f"Starting Gmail Watcher...")
    print(f"Vault: {vault}")
    print(f"Check interval: {args.interval}s")
    print(f"Keywords: {keywords or 'all unread emails'}")
    print()
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    watcher.run()


if __name__ == '__main__':
    main()
