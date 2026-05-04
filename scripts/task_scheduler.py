#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task Scheduler - Windows Task Scheduler integration for AI Employee.

Creates scheduled tasks for:
- Daily briefing generation
- Periodic watcher health checks
- Weekly business audits

Usage:
    # Install all scheduled tasks
    python scripts/task_scheduler.py AI_Employee_Vault --install

    # List scheduled tasks
    python scripts/task_scheduler.py AI_Employee_Vault --list

    # Remove all scheduled tasks
    python scripts/task_scheduler.py AI_Employee_Vault --uninstall

    # Run daily briefing manually
    python scripts/task_scheduler.py AI_Employee_Vault --run-daily-briefing
"""

import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


class TaskScheduler:
    """Manages Windows Task Scheduler integration."""
    
    def __init__(self, vault_path: str):
        """
        Initialize the task scheduler.
        
        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.scripts_dir = Path(__file__).parent
        self.python_exe = sys.executable
        
        # Task names
        self.task_prefix = "AI_Employee"
        self.tasks = {
            'daily_briefing': f"{self.task_prefix}_Daily_Briefing",
            'health_check': f"{self.task_prefix}_Health_Check",
            'weekly_audit': f"{self.task_prefix}_Weekly_Audit"
        }
    
    def _run_schtasks(self, args: list, check: bool = True) -> subprocess.CompletedProcess:
        """Run schtasks command."""
        cmd = ['schtasks'] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error running schtasks: {e}")
            return e
    
    def install_daily_briefing(self) -> bool:
        """
        Install daily briefing task (runs at 8:00 AM daily).
        
        Returns:
            True if installation successful
        """
        task_name = self.tasks['daily_briefing']
        
        # Command to run
        script = self.scripts_dir / 'orchestrator.py'
        cmd = f'"{self.python_exe}" "{script}" "{self.vault_path}" --process'
        
        # Create task
        args = [
            '/Create',
            '/TN', task_name,
            '/TR', cmd,
            '/SC', 'DAILY',
            '/ST', '08:00',
            '/RL', 'HIGHEST',
            '/F'  # Force overwrite if exists
        ]
        
        result = self._run_schtasks(args, check=False)
        
        if result.returncode == 0:
            print(f"✓ Installed: {task_name}")
            print(f"  Schedule: Daily at 8:00 AM")
            return True
        else:
            print(f"✗ Failed: {task_name}")
            print(f"  Error: {result.stderr}")
            return False
    
    def install_health_check(self) -> bool:
        """
        Install health check task (runs every hour).
        
        Returns:
            True if installation successful
        """
        task_name = self.tasks['health_check']
        
        # Command to run - just check status
        script = self.scripts_dir / 'orchestrator.py'
        cmd = f'"{self.python_exe}" "{script}" "{self.vault_path}" --status'
        
        # Create task
        args = [
            '/Create',
            '/TN', task_name,
            '/TR', cmd,
            '/SC', 'HOURLY',
            '/RL', 'HIGHEST',
            '/F'
        ]
        
        result = self._run_schtasks(args, check=False)
        
        if result.returncode == 0:
            print(f"✓ Installed: {task_name}")
            print(f"  Schedule: Every hour")
            return True
        else:
            print(f"✗ Failed: {task_name}")
            print(f"  Error: {result.stderr}")
            return False
    
    def install_weekly_audit(self) -> bool:
        """
        Install weekly audit task (runs Monday at 7:00 AM).
        
        Returns:
            True if installation successful
        """
        task_name = self.tasks['weekly_audit']
        
        # Command to run
        script = self.scripts_dir / 'orchestrator.py'
        cmd = f'"{self.python_exe}" "{script}" "{self.vault_path}" --weekly-audit'
        
        # Create task - every Monday at 7 AM
        args = [
            '/Create',
            '/TN', task_name,
            '/TR', cmd,
            '/SC', 'WEEKLY',
            '/D', 'MON',
            '/ST', '07:00',
            '/RL', 'HIGHEST',
            '/F'
        ]
        
        result = self._run_schtasks(args, check=False)
        
        if result.returncode == 0:
            print(f"✓ Installed: {task_name}")
            print(f"  Schedule: Every Monday at 7:00 AM")
            return True
        else:
            print(f"✗ Failed: {task_name}")
            print(f"  Error: {result.stderr}")
            return False
    
    def install_all(self) -> bool:
        """
        Install all scheduled tasks.
        
        Returns:
            True if all installations successful
        """
        print("=" * 60)
        print("Installing AI Employee Scheduled Tasks")
        print("=" * 60)
        print()
        
        results = [
            self.install_daily_briefing(),
            self.install_health_check(),
            self.install_weekly_audit()
        ]
        
        print()
        print("=" * 60)
        if all(results):
            print("✓ All tasks installed successfully!")
            return True
        else:
            print("✗ Some tasks failed to install.")
            return False
    
    def uninstall_all(self) -> bool:
        """
        Remove all scheduled tasks.
        
        Returns:
            True if all removals successful
        """
        print("=" * 60)
        print("Removing AI Employee Scheduled Tasks")
        print("=" * 60)
        print()
        
        all_success = True
        
        for task_name in self.tasks.values():
            args = ['/Delete', '/TN', task_name, '/F']
            result = self._run_schtasks(args, check=False)
            
            if result.returncode == 0:
                print(f"✓ Removed: {task_name}")
            else:
                print(f"✗ Failed to remove: {task_name}")
                all_success = False
        
        print()
        print("=" * 60)
        if all_success:
            print("✓ All tasks removed successfully!")
        else:
            print("✗ Some tasks failed to remove.")
        return all_success
    
    def list_tasks(self):
        """List all AI Employee scheduled tasks."""
        print("=" * 60)
        print("AI Employee Scheduled Tasks")
        print("=" * 60)
        print()
        
        for task_name in self.tasks.values():
            # Query task
            args = ['/Query', '/TN', task_name, '/V', '/FO', 'LIST']
            result = self._run_schtasks(args, check=False)
            
            if result.returncode == 0:
                print(f"Task: {task_name}")
                print(f"Status: Enabled")
                print(f"Details:\n{result.stdout}")
                print("-" * 40)
            else:
                print(f"Task: {task_name}")
                print(f"Status: Not found or disabled")
                print("-" * 40)
    
    def run_daily_briefing(self):
        """Run daily briefing manually."""
        print("Running daily briefing...")
        
        script = self.scripts_dir / 'orchestrator.py'
        cmd = [self.python_exe, str(script), str(self.vault_path), '--process']
        
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✓ Daily briefing completed.")
        else:
            print(f"\n✗ Daily briefing failed with code {result.returncode}")
    
    def run_weekly_audit(self):
        """Run weekly audit manually."""
        print("Running weekly audit...")
        
        # Generate weekly audit report
        audit_file = self.vault_path / 'Briefings' / f"Weekly_Audit_{datetime.now().strftime('%Y-%m-%d')}.md"
        audit_file.parent.mkdir(parents=True, exist_ok=True)
        
        content = f'''---
type: weekly_audit
generated: {datetime.now().isoformat()}
period: Weekly
---

# Weekly Business Audit

## Summary

*To be filled by AI Employee*

## Tasks Completed This Week

*Check /Done folder*

## Revenue Summary

*Check accounting records*

## Bottlenecks Identified

*Analysis needed*

## Recommendations

*AI-generated suggestions*

---
*Generated by Task Scheduler v0.1 (Silver Tier)*
'''
        
        audit_file.write_text(content, encoding='utf-8')
        print(f"Weekly audit created: {audit_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Task Scheduler - Windows Task Scheduler integration'
    )
    parser.add_argument(
        'vault_path',
        help='Path to the Obsidian vault root'
    )
    parser.add_argument(
        '--install', '-i',
        action='store_true',
        help='Install all scheduled tasks'
    )
    parser.add_argument(
        '--uninstall', '-u',
        action='store_true',
        help='Remove all scheduled tasks'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List scheduled tasks'
    )
    parser.add_argument(
        '--run-daily-briefing',
        action='store_true',
        help='Run daily briefing manually'
    )
    parser.add_argument(
        '--run-weekly-audit',
        action='store_true',
        help='Run weekly audit manually'
    )
    
    args = parser.parse_args()
    
    vault = Path(args.vault_path)
    if not vault.exists():
        print(f"Error: Vault path does not exist: {vault}")
        sys.exit(1)
    
    scheduler = TaskScheduler(str(vault))
    
    if args.install:
        scheduler.install_all()
    
    elif args.uninstall:
        scheduler.uninstall_all()
    
    elif args.list:
        scheduler.list_tasks()
    
    elif args.run_daily_briefing:
        scheduler.run_daily_briefing()
    
    elif args.run_weekly_audit:
        scheduler.run_weekly_audit()
    
    else:
        parser.print_help()
        print("\n" + "=" * 60)
        print("Quick Start:")
        print("  --install    : Create all scheduled tasks")
        print("  --list       : View scheduled tasks")
        print("  --uninstall  : Remove all scheduled tasks")
        print("=" * 60)


if __name__ == '__main__':
    main()
