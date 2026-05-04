#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Approval Manager - Human-in-the-Loop approval workflow.

Manages the approval process for sensitive actions:
- Monitors Pending_Approval folder
- Moves approved files to Approved folder
- Tracks approval history
- Sends notifications for pending approvals

Usage:
    # Check pending approvals
    python scripts/approval_manager.py AI_Employee_Vault --status

    # Approve a specific file
    python scripts/approval_manager.py AI_Employee_Vault --approve FILENAME.md

    # Reject a specific file
    python scripts/approval_manager.py AI_Employee_Vault --reject FILENAME.md

    # Run approval watcher (continuous)
    python scripts/approval_manager.py AI_Employee_Vault --watch
"""

import sys
import shutil
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List


class ApprovalManager:
    """Manages human-in-the-loop approval workflow."""
    
    def __init__(self, vault_path: str):
        """
        Initialize the approval manager.
        
        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs = self.vault_path / 'Logs'
        
        # Ensure directories exist
        for folder in [self.pending_approval, self.approved, self.rejected, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
    
    def get_pending_items(self) -> List[Path]:
        """Get list of pending approval files."""
        if not self.pending_approval.exists():
            return []
        return sorted([
            f for f in self.pending_approval.iterdir()
            if f.is_file() and f.suffix == '.md'
        ])
    
    def approve(self, filename: str, reason: str = "") -> bool:
        """
        Approve a pending item.
        
        Args:
            filename: Name of the file to approve
            reason: Optional approval reason
            
        Returns:
            True if approval successful
        """
        source = self.pending_approval / filename
        if not source.exists():
            print(f"File not found: {source}")
            return False
        
        # Read the file to get metadata
        content = source.read_text(encoding='utf-8')
        
        # Move to Approved folder
        dest = self.approved / filename
        shutil.move(str(source), str(dest))
        
        # Update file with approval metadata
        approval_info = f'''
---
approved: true
approved_at: {datetime.now().isoformat()}
approved_by: human
approval_reason: {reason if reason else 'Manual approval'}
---

'''
        # Prepend approval info
        new_content = approval_info + content
        dest.write_text(new_content, encoding='utf-8')
        
        # Log the approval
        self._log_approval(filename, 'approved', reason)
        
        print(f"Approved: {filename}")
        print(f"Moved to: {dest}")
        
        return True
    
    def reject(self, filename: str, reason: str = "") -> bool:
        """
        Reject a pending item.
        
        Args:
            filename: Name of the file to reject
            reason: Optional rejection reason
            
        Returns:
            True if rejection successful
        """
        source = self.pending_approval / filename
        if not source.exists():
            print(f"File not found: {source}")
            return False
        
        # Read the file to get metadata
        content = source.read_text(encoding='utf-8')
        
        # Move to Rejected folder
        dest = self.rejected / filename
        shutil.move(str(source), str(dest))
        
        # Update file with rejection metadata
        rejection_info = f'''
---
rejected: true
rejected_at: {datetime.now().isoformat()}
rejected_by: human
rejection_reason: {reason if reason else 'Manual rejection'}
---

'''
        # Prepend rejection info
        new_content = rejection_info + content
        dest.write_text(new_content, encoding='utf-8')
        
        # Log the rejection
        self._log_approval(filename, 'rejected', reason)
        
        print(f"Rejected: {filename}")
        print(f"Moved to: {dest}")
        
        return True
    
    def _log_approval(self, filename: str, action: str, reason: str):
        """Log approval/rejection action."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'approvals_{today}.jsonl'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'file': filename,
            'action': action,
            'reason': reason
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def status(self, verbose: bool = False):
        """Print current approval status."""
        pending = self.get_pending_items()
        
        print("=" * 60)
        print("APPROVAL MANAGER STATUS")
        print("=" * 60)
        print(f"Pending approvals: {len(pending)}")
        print()
        
        if pending:
            print("Pending Items:")
            print("-" * 40)
            for item in pending:
                stat = item.stat()
                age = datetime.now() - datetime.fromtimestamp(stat.st_mtime)
                print(f"  • {item.name}")
                print(f"    Created: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')}")
                print(f"    Age: {age.seconds // 60} minutes ago")
                
                if verbose:
                    # Show first few lines of content
                    content = item.read_text(encoding='utf-8')
                    lines = content.split('\n')[:10]
                    print(f"    Preview: {' '.join(lines[:3])}...")
                print()
        else:
            print("No pending approvals.")
        
        print("=" * 60)
        
        # Show recent approvals
        approved_count = len(list(self.approved.glob('*.md'))) if self.approved.exists() else 0
        rejected_count = len(list(self.rejected.glob('*.md'))) if self.rejected.exists() else 0
        
        print(f"Total approved: {approved_count}")
        print(f"Total rejected: {rejected_count}")
        print("=" * 60)
    
    def watch(self, check_interval: int = 30):
        """
        Watch for approved files (moved by human).
        
        In Silver Tier, humans approve by moving files manually.
        This watcher detects when files appear in /Approved folder.
        
        Args:
            check_interval: Seconds between checks
        """
        print(f"Watching for approved files...")
        print(f"Check interval: {check_interval}s")
        print()
        print("Human approval workflow:")
        print(f"  1. Review files in /Pending_Approval")
        print(f"  2. Move to /Approved to approve")
        print(f"  3. Move to /Rejected to reject")
        print()
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        import time
        
        last_approved = set()
        if self.approved.exists():
            last_approved = set(f.name for f in self.approved.glob('*.md'))
        
        try:
            while True:
                # Check for new approved files
                if self.approved.exists():
                    current_approved = set(f.name for f in self.approved.glob('*.md'))
                    new_approvals = current_approved - last_approved
                    
                    for filename in new_approvals:
                        print(f"\n[NEW APPROVAL] {filename}")
                        print("  Action required: Process this approved item")
                        # In Silver Tier, we just log - actual execution is manual
                        self._log_approval(filename, 'detected', '')
                    
                    last_approved = current_approved
                
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            print("\nStopped by user.")


def main():
    parser = argparse.ArgumentParser(
        description='Approval Manager - Human-in-the-Loop workflow'
    )
    parser.add_argument(
        'vault_path',
        help='Path to the Obsidian vault root'
    )
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='Show pending approvals status'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed information'
    )
    parser.add_argument(
        '--approve', '-a',
        type=str,
        metavar='FILE',
        help='Approve a specific file'
    )
    parser.add_argument(
        '--reject', '-r',
        type=str,
        metavar='FILE',
        help='Reject a specific file'
    )
    parser.add_argument(
        '--reason',
        type=str,
        default='',
        help='Reason for approval/rejection'
    )
    parser.add_argument(
        '--watch', '-w',
        action='store_true',
        help='Run approval watcher (continuous)'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=30,
        help='Check interval in seconds (default: 30)'
    )
    
    args = parser.parse_args()
    
    vault = Path(args.vault_path)
    if not vault.exists():
        print(f"Error: Vault path does not exist: {vault}")
        sys.exit(1)
    
    manager = ApprovalManager(str(vault))
    
    if args.status:
        manager.status(verbose=args.verbose)
    
    elif args.approve:
        if manager.approve(args.approve, args.reason):
            print("Approval recorded.")
        else:
            sys.exit(1)
    
    elif args.reject:
        if manager.reject(args.reject, args.reason):
            print("Rejection recorded.")
        else:
            sys.exit(1)
    
    elif args.watch:
        manager.watch(args.interval)
    
    else:
        # Default: show status
        manager.status()
        print("\nUse --approve FILENAME to approve")
        print("Use --reject FILENAME to reject")
        print("Use --watch for continuous monitoring")


if __name__ == '__main__':
    main()
