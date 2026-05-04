#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator - Master process for the AI Employee.

The orchestrator:
1. Monitors the Needs_Action folder for new items
2. Generates plans for multi-step tasks (Silver Tier)
3. Triggers Qwen Code to process pending items
4. Manages approval workflow (Silver Tier)
5. Updates the Dashboard.md with current status

Usage:
    python orchestrator.py /path/to/vault

For continuous operation:
    python orchestrator.py /path/to/vault --continuous
"""

import sys
import subprocess
import shutil
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import Silver Tier components
sys.path.insert(0, str(Path(__file__).parent))
try:
    from plan_generator import PlanGenerator
    PLAN_GENERATOR_AVAILABLE = True
except ImportError:
    PLAN_GENERATOR_AVAILABLE = False


class Orchestrator:
    """Main orchestrator for the AI Employee system."""
    
    def __init__(self, vault_path: str):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.logs = self.vault_path / 'Logs'
        
        # Initialize Silver Tier components
        if PLAN_GENERATOR_AVAILABLE:
            self.plan_generator = PlanGenerator(str(vault_path))
        else:
            self.plan_generator = None
        
        # Ensure directories exist
        for folder in [self.needs_action, self.done, self.plans, 
                       self.pending_approval, self.approved, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
    
    def get_pending_items(self) -> list[Path]:
        """Get list of pending action files."""
        if not self.needs_action.exists():
            return []
        return sorted([
            f for f in self.needs_action.iterdir() 
            if f.is_file() and f.suffix == '.md'
        ])
    
    def get_pending_approvals(self) -> list[Path]:
        """Get list of pending approval requests."""
        if not self.pending_approval.exists():
            return []
        return sorted([
            f for f in self.pending_approval.iterdir() 
            if f.is_file() and f.suffix == '.md'
        ])
    
    def update_dashboard(self):
        """Update the Dashboard.md with current status."""
        pending_items = self.get_pending_items()
        pending_approvals = self.get_pending_approvals()
        
        # Count items
        pending_count = len(pending_items)
        approval_count = len(pending_approvals)
        
        # Get recent activity from logs
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.jsonl'
        completed_today = 0
        
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get('action_type') == 'moved_to_done':
                            completed_today += 1
                    except json.JSONDecodeError:
                        continue
        
        # Build dashboard content
        pending_list = ""
        if pending_items:
            for item in pending_items[-5:]:  # Last 5 items
                pending_list += f"- {item.name}\n"
        else:
            pending_list = "*No items requiring action*\n"
        
        approval_list = ""
        if pending_approvals:
            for item in pending_approvals:
                approval_list += f"- {item.name}\n"
        else:
            pending_list = "*No items awaiting approval*\n"
        
        # Get recent activity (last 5 done items)
        recent_activity = ""
        if self.done.exists():
            done_items = sorted(
                [f for f in self.done.iterdir() if f.is_file()],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )[:5]
            for item in done_items:
                mtime = datetime.fromtimestamp(item.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                recent_activity += f"- [{mtime}] {item.name}\n"
        else:
            recent_activity = "*No recent activity*\n"
        
        content = f'''---
last_updated: {datetime.now().isoformat()}
status: active
---

# AI Employee Dashboard

## Quick Status

| Metric | Value |
|--------|-------|
| Pending Tasks | {pending_count} |
| Awaiting Approval | {approval_count} |
| Completed Today | {completed_today} |
| Revenue MTD | $0 |

---

## Inbox Summary

*Check /Inbox folder for new file drops*

---

## Needs Action

{pending_list}

---

## Pending Approvals

{approval_list if approval_list else "*No items awaiting approval*"}

---

## Recent Activity

{recent_activity if recent_activity else "*No recent activity*"}

---

## Active Projects

| Project | Due Date | Status |
|---------|----------|--------|
| - | - | - |

---

## Quick Commands

```bash
# Process all files in Needs_Action
qwen --prompt "Process all files in /Needs_Action folder"

# Generate weekly briefing
qwen --prompt "Generate weekly business briefing"

# Check pending approvals
qwen --prompt "Review all pending approvals"
```

---

## System Health

- [x] Vault structure initialized
- [ ] Watcher scripts running
- [ ] Qwen Code configured
- [ ] MCP servers connected

---

*Last generated by AI Employee v0.1 (Bronze Tier)*
'''
        
        self.dashboard.write_text(content, encoding='utf-8')
    
    def process_items(self, qwen_path: str = "qwen"):
        """
        Process all pending items using Qwen Code.

        Args:
            qwen_path: Path or command to run Qwen Code
        """
        pending_items = self.get_pending_items()

        if not pending_items:
            print("No pending items to process.")
            return

        print(f"Found {len(pending_items)} pending item(s) to process.")
        
        # Silver Tier: Generate plans for all pending items
        if self.plan_generator:
            print("\nGenerating plans for pending items...")
            for item in pending_items:
                self.plan_generator.generate_from_action_file(item)
            print("Plans generated.\n")

        # Build the prompt for Qwen
        prompt = f"""You are an AI Employee assistant. Process all files in the /Needs_Action folder.

For each file:
1. Read and understand what action is needed
2. Check the Company_Handbook.md for rules and guidelines
3. Review the Plan.md in /Plans if one exists
4. Execute the required actions (within your capabilities)
5. If human approval is needed, create a file in /Pending_Approval
6. Move the processed file to /Done when complete

Current pending files:
{chr(10).join([f'- {f.name}' for f in pending_items])}

Start by reading the first file and determining what needs to be done."""

        # Build Qwen Code command
        # Qwen Code uses -p for prompt, -y for YOLO mode (auto-approve)
        cmd = [
            qwen_path,
            "-p", prompt,
            "-y"  # YOLO mode - auto-approve file operations
        ]

        print(f"Running: {' '.join(cmd)}")
        print("---")

        # Execute Qwen Code
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.vault_path),
                capture_output=False,
                text=True
            )
            print("---")
            print(f"Qwen Code exited with code {result.returncode}")
        except FileNotFoundError:
            print(f"Error: Qwen Code not found at '{qwen_path}'")
            print("Make sure Qwen Code is installed and in your PATH.")
        except Exception as e:
            print(f"Error running Qwen Code: {e}")

        # After Qwen processes, move files to Done
        print("\nMoving processed files to Done...")
        self._move_processed_files()

        # Update dashboard after processing
        self.update_dashboard()
    
    def _move_processed_files(self):
        """Move all files from Needs_Action to Done (simple move after Qwen processing)."""
        files = list(self.needs_action.glob('*.md'))
        
        if not files:
            print("No files to move.")
            return
        
        moved_count = 0
        for file in files:
            try:
                dest = self.done / file.name
                if dest.exists():
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    dest = self.done / f'{timestamp}_{file.name}'
                
                shutil.move(str(file), str(dest))
                print(f"  [OK] Moved: {file.name}")
                
                # Log the move
                self._log_move(file.name, str(dest))
                moved_count += 1
            except Exception as e:
                print(f"  [FAILED] Could not move {file.name}: {e}")
        
        print(f"Moved {moved_count} file(s) to Done.")
    
    def _create_approval_request(self, email_file: Path, email_info: dict) -> Path:
        """Create an approval request file for email reply."""
        pending_approval = self.vault_path / 'Pending_Approval'
        pending_approval.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"APPROVAL_EMAIL_{timestamp}_{email_file.stem}.md"
        filepath = pending_approval / filename
        
        # Generate reply content
        subject = email_info.get('subject', 'No Subject')
        from_email = email_info.get('from', 'unknown')
        content = email_info.get('content', '')
        
        # Smart reply generation
        reply_subject = f"Re: {subject}"
        
        if 'invoice' in subject.lower() or 'invoice' in content.lower():
            reply_body = f"""Dear {from_email.split('@')[0]},

Thank you for your email regarding the invoice request.

We have received your request and are processing it. The invoice will be sent to you within 24 hours.

If you have any urgent questions, please don't hesitate to contact us.

Best regards,
AI Employee
Automated Response System"""
        elif 'security' in subject.lower() or 'google' in from_email.lower():
            reply_body = f"""Thank you for the security notification.

We have reviewed the security alert and will take appropriate action if needed.

Best regards,
AI Employee"""
        else:
            reply_body = f"""Dear {from_email.split('@')[0]},

Thank you for your email.

We have received your message and will respond shortly.

Best regards,
AI Employee
Automated Response System"""
        
        approval_content = f'''---
type: email_reply_approval
action: send_email
to: {from_email}
subject: {reply_subject}
original_file: {email_file.name}
created: {datetime.now().isoformat()}
status: pending
priority: normal
---

# Email Reply Approval Request

## Original Email

- **From:** {from_email}
- **Subject:** {subject}

---

## Proposed Reply

**To:** {from_email}
**Subject:** {reply_subject}

---

## Email Content

{reply_body}

---

## To Approve

**Option 1: Move this file to /Approved folder**
```bash
move {filepath} AI_Employee_Vault\\Approved\\
```

**Option 2: Use approval manager**
```bash
python scripts\\approval_manager.py AI_Employee_Vault --approve {filename}
```

## To Reject

**Move this file to /Rejected folder**

---
*Generated by AI Employee Orchestrator v0.2 (Silver Tier)*
'''
        
        filepath.write_text(approval_content, encoding='utf-8')
        
        # Log the approval request
        self._log_approval_request(email_file.name, str(filepath), from_email)
        
        return filepath
    
    def _log_approval_request(self, original_file: str, approval_file: str, recipient: str):
        """Log approval request creation."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.jsonl'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': 'approval_request_created',
            'original_file': original_file,
            'approval_file': approval_file,
            'recipient': recipient,
            'actor': 'orchestrator'
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f'{log_entry}\n')
    
    def _log_move(self, source: str, dest: str):
        """Log file move to JSONL."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.jsonl'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': 'moved_to_done',
            'source': source,
            'destination': dest,
            'actor': 'orchestrator'
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f'{log_entry}\n')
    
    def _extract_email_info(self, filepath: Path) -> dict:
        """Extract email information from action file."""
        content = filepath.read_text(encoding='utf-8')
        
        info = {
            'from': '',
            'subject': '',
            'content': '',
            'type': 'email'
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
        
        # Extract content
        if '## Email Content' in content:
            content_part = content.split('## Email Content')[1]
            if '##' in content_part:
                content_part = content_part.split('##')[0]
            info['content'] = content_part.strip()
        
        return info
    
    def process_emails_with_approval(self):
        """Process emails and create approval requests for replies."""
        pending_items = self.get_pending_items()
        
        if not pending_items:
            print("No pending emails to process.")
            return
        
        print(f"Found {len(pending_items)} email(s) to process")
        print()
        
        approval_count = 0
        
        for item in pending_items:
            if item.name.startswith('EMAIL_'):
                print(f"Processing: {item.name}")
                
                # Extract email info
                email_info = self._extract_email_info(item)
                
                print(f"  From: {email_info['from']}")
                print(f"  Subject: {email_info['subject']}")
                
                # Create approval request
                approval_file = self._create_approval_request(item, email_info)
                
                print(f"  [OK] Approval request created: {approval_file.name}")
                approval_count += 1
        
        print()
        print(f"Created {approval_count} approval request(s)")
        print()
        print("Next steps:")
        print("  1. Review files in Pending_Approval/")
        print("  2. Move to Approved/ to send email")
        print("  3. Approved Email Watcher will send automatically")
        print()
    
    def check_approvals(self):
        """Check for approved items and log them."""
        approved_items = self.get_pending_approvals()
        
        # Note: In Bronze tier, we just log approvals
        # Actual execution happens in higher tiers
        if approved_items:
            print(f"Found {len(approved_items)} approved item(s) awaiting execution.")
            print("Note: Bronze tier requires manual execution of approved actions.")
        else:
            print("No approved items pending.")
    
    def status(self):
        """Print current system status."""
        self.update_dashboard()
        
        pending = self.get_pending_items()
        approvals = self.get_pending_approvals()
        
        print("=" * 50)
        print("AI Employee Status - Bronze Tier")
        print("=" * 50)
        print(f"Vault: {self.vault_path}")
        print(f"Pending items: {len(pending)}")
        print(f"Pending approvals: {len(approvals)}")
        print()
        
        if pending:
            print("Pending Files:")
            for item in pending:
                print(f"  - {item.name}")
        else:
            print("No pending items.")
        
        print()
        print(f"Dashboard: {self.dashboard}")
        print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description='AI Employee Orchestrator - Bronze Tier'
    )
    parser.add_argument(
        'vault_path',
        help='Path to the Obsidian vault root'
    )
    parser.add_argument(
        '--continuous', '-c',
        action='store_true',
        help='Run in continuous mode (check every 60 seconds)'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--qwen',
        default='C:\\Users\\Dell\\AppData\\Roaming\\npm\\qwen.cmd',
        help='Qwen Code command or path (default: C:\\Users\\Dell\\AppData\\Roaming\\npm\\qwen.cmd)'
    )
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='Show current status and exit'
    )
    parser.add_argument(
        '--process', '-p',
        action='store_true',
        help='Process pending items now'
    )
    parser.add_argument(
        '--generate-plans',
        action='store_true',
        help='Generate plans for all pending items (Silver Tier)'
    )
    
    args = parser.parse_args()
    
    # Validate vault path
    vault = Path(args.vault_path)
    if not vault.exists():
        print(f"Error: Vault path does not exist: {vault}")
        sys.exit(1)
    
    if not (vault / 'Dashboard.md').exists():
        print(f"Error: Dashboard.md not found. Is this a valid AI Employee vault?")
        sys.exit(1)
    
    # Create orchestrator
    orchestrator = Orchestrator(str(vault))
    
    # Handle commands
    if args.status:
        orchestrator.status()
    elif args.process:
        orchestrator.process_items(args.qwen)
    elif args.generate_plans:
        if orchestrator.plan_generator:
            count = orchestrator.plan_generator.generate_all_plans()
            print(f"Generated {count} plan(s).")
        else:
            print("Plan Generator not available. Install Silver Tier components.")
    elif args.continuous:
        print(f"Starting continuous mode (interval: {args.interval}s)")
        print("Press Ctrl+C to stop.")
        try:
            while True:
                orchestrator.update_dashboard()
                orchestrator.process_items(args.qwen)
                import time
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nStopped by user.")
    else:
        # Default: show status
        orchestrator.status()
        print("\nUse --process to process pending items")
        print("Use --generate-plans to create plans for pending items")
        print("Use --continuous for continuous operation")


if __name__ == '__main__':
    main()
