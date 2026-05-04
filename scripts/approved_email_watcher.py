#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Approved Email Watcher - Watches Approved folder and sends emails via MCP.

This script monitors the Approved/ folder for approved email replies
and automatically sends them using the MCP Email Server.

Usage:
    python scripts\approved_email_watcher.py AI_Employee_Vault

Or run continuously:
    python scripts\approved_email_watcher.py AI_Employee_Vault --watch
"""

import sys
import time
import json
import shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from mcp_email_server import EmailMCPServer


class ApprovedEmailWatcher:
    """Watches Approved folder and sends emails via MCP."""
    
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self.approved = self.vault / 'Approved'
        self.done = self.vault / 'Done'
        self.logs = self.vault / 'Logs'
        
        # Ensure folders exist
        for folder in [self.approved, self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files
        self.processed_files = set()
        
        # Email service
        self.email_service = None
    
    def initialize_email_service(self) -> bool:
        """Initialize MCP Email Server."""
        if self.email_service is None:
            self.email_service = EmailMCPServer(str(self.vault))
        
        print("Initializing MCP Email Server...")
        if not self.email_service.authenticate():
            print("[FAILED] Authentication failed")
            return False
        
        print("[OK] MCP Email Server ready")
        return True
    
    def extract_email_info(self, filepath: Path) -> dict:
        """Extract email information from approval file."""
        content = filepath.read_text(encoding='utf-8')
        
        info = {
            'to': '',
            'subject': '',
            'body': '',
            'type': 'approval_request',
            'status': 'pending'
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
                        if key in ['to', 'subject', 'body', 'type', 'status']:
                            info[key] = value
        
        # Extract email body from content
        if '## Email Content' in content:
            body_part = content.split('## Email Content')[1]
            if '##' in body_part:
                body_part = body_part.split('##')[0]
            info['body'] = body_part.strip()
        elif '## Reply Content' in content:
            body_part = content.split('## Reply Content')[1]
            if '##' in body_part:
                body_part = body_part.split('##')[0]
            info['body'] = body_part.strip()
        
        # Check if approved
        if 'approved: true' in content or 'status: approved' in content:
            info['status'] = 'approved'
        
        return info
    
    def process_approved_file(self, filepath: Path) -> bool:
        """Process a single approved email file."""
        print(f"\nProcessing: {filepath.name}")
        
        try:
            # Extract email info
            email_info = self.extract_email_info(filepath)
            
            print(f"  To: {email_info['to']}")
            print(f"  Subject: {email_info['subject']}")
            
            # Check if already processed
            if filepath.name in self.processed_files:
                print("  [SKIP] Already processed")
                return False
            
            # Check if approved
            if email_info['status'] != 'approved':
                print("  [SKIP] Not approved yet")
                return False
            
            # Send email
            print("  Sending email via MCP...")
            result = self.email_service.send_email(
                to=email_info['to'],
                subject=email_info['subject'],
                body=email_info['body']
            )
            
            if result.get('status') == 'success':
                message_id = result.get('message_id', 'unknown')
                print(f"  [OK] Email sent! Message ID: {message_id}")
                
                # Log the send
                self.log_send(filepath.name, email_info['to'], message_id)
                
                # Mark as processed
                self.processed_files.add(filepath.name)
                
                # Move to Done
                dest = self.done / filepath.name
                if dest.exists():
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    dest = self.done / f'{timestamp}_{filepath.name}'
                
                shutil.move(str(filepath), str(dest))
                print(f"  [OK] Moved to Done: {dest.name}")
                
                return True
            else:
                print(f"  [FAILED] {result.get('message')}")
                return False
            
        except Exception as e:
            print(f"  [ERROR] {e}")
            return False
    
    def check_and_send(self) -> int:
        """Check Approved folder and send emails."""
        if not self.approved.exists():
            return 0
        
        # Get all .md files in Approved folder
        files = [f for f in self.approved.glob('*.md') if f.is_file()]
        
        if not files:
            return 0
        
        # Initialize email service if needed
        if self.email_service is None:
            if not self.initialize_email_service():
                return 0
        
        sent_count = 0
        
        for file in files:
            if self.process_approved_file(file):
                sent_count += 1
        
        return sent_count
    
    def log_send(self, filename: str, recipient: str, message_id: str):
        """Log email send to JSONL."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.jsonl'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': 'approved_email_sent',
            'file': filename,
            'recipient': recipient,
            'message_id': message_id,
            'actor': 'approved_email_watcher'
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f'{log_entry}\n')
    
    def watch(self, check_interval: int = 10):
        """Continuously watch Approved folder."""
        print("=" * 70)
        print("APPROVED EMAIL WATCHER")
        print("=" * 70)
        print(f"Vault: {self.vault}")
        print(f"Monitoring: {self.approved}")
        print(f"Check interval: {check_interval}s")
        print()
        print("Workflow:")
        print("  1. Qwen Code creates approval request in Pending_Approval/")
        print("  2. Human reviews and moves to Approved/")
        print("  3. This watcher detects and sends email via MCP")
        print("  4. File moved to Done/")
        print()
        print("Press Ctrl+C to stop")
        print("=" * 70)
        print()
        
        # Initialize email service
        if not self.initialize_email_service():
            print("[ERROR] Failed to initialize email service")
            return
        
        try:
            while True:
                sent = self.check_and_send()
                
                if sent > 0:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Sent {sent} email(s)")
                
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            print("\n\nStopped by user")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts\\approved_email_watcher.py <vault_path> [--watch]")
        print()
        print("Options:")
        print("  --watch, -w    Run continuously (default: check once)")
        print("  --interval, -i Check interval in seconds (default: 10)")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    vault = Path(vault_path)
    
    if not vault.exists():
        print(f"Error: Vault path does not exist: {vault}")
        sys.exit(1)
    
    # Parse options
    watch_mode = '--watch' in sys.argv or '-w' in sys.argv
    interval = 10
    
    if '--interval' in sys.argv or '-i' in sys.argv:
        try:
            idx = sys.argv.index('--interval') if '--interval' in sys.argv else sys.argv.index('-i')
            interval = int(sys.argv[idx + 1])
        except (ValueError, IndexError):
            pass
    
    watcher = ApprovedEmailWatcher(str(vault))
    
    if watch_mode:
        watcher.watch(check_interval=interval)
    else:
        # Run once
        print("=" * 70)
        print("APPROVED EMAIL CHECK")
        print("=" * 70)
        print()
        
        sent = watcher.check_and_send()
        
        print()
        print("=" * 70)
        print(f"Sent {sent} email(s)")
        print("=" * 70)


if __name__ == '__main__':
    main()
