#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plan Generator - Creates structured Plan.md files for Claude reasoning.

Silver Tier requirement: Claude reasoning loop that creates Plan.md files
for multi-step tasks before execution.

Usage:
    # Generate plan for a task
    python scripts/plan_generator.py AI_Employee_Vault --task "Process client invoice request"
    
    # Generate plans for all pending items
    python scripts/plan_generator.py AI_Employee_Vault --generate-all
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict


class PlanGenerator:
    """Generates structured Plan.md files for task execution."""
    
    def __init__(self, vault_path: str):
        """
        Initialize the plan generator.
        
        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path)
        self.plans = self.vault_path / 'Plans'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        
        # Ensure directories exist
        for folder in [self.plans, self.needs_action, self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
    
    def create_plan(
        self,
        task_name: str,
        objective: str,
        steps: List[Dict],
        source_file: Optional[str] = None,
        priority: str = "normal",
        requires_approval: bool = False
    ) -> Path:
        """
        Create a structured Plan.md file.
        
        Args:
            task_name: Short name for the task
            objective: What we're trying to accomplish
            steps: List of step dictionaries with 'action' and 'status'
            source_file: Optional source file that triggered this plan
            priority: Task priority (low, normal, high, critical)
            requires_approval: Whether plan needs human approval
            
        Returns:
            Path to the created plan file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = "".join(c if c.isalnum() or c in ' -_' else '_' for c in task_name[:40])
        filename = f"PLAN_{timestamp}_{safe_name}.md"
        filepath = self.plans / filename
        
        # Build steps markdown
        steps_md = ""
        for i, step in enumerate(steps, 1):
            action = step.get('action', 'Unknown action')
            status = step.get('status', 'pending')
            checkbox = "[ ]" if status == 'pending' else "[x]" if status == 'completed' else "[~]"
            steps_md += f"- {checkbox} **Step {i}:** {action}\n"
        
        # Determine approval section
        approval_section = ""
        if requires_approval:
            approval_section = f'''
## Approval Required

This plan requires human approval before execution.

**To Approve:**
- Move this file to /Approved folder
- Or run: python scripts/approval_manager.py {self.vault_path.name} --approve "{filename}"

**To Reject:**
- Move this file to /Rejected folder
'''
        
        # Create plan content
        content = f'''---
type: plan
task: {task_name}
created: {datetime.now().isoformat()}
status: pending
priority: {priority}
source: {source_file if source_file else 'manual'}
requires_approval: {str(requires_approval).lower()}
---

# Plan: {task_name}

## Objective

{objective}

---

## Steps

{steps_md}

---

## Resources

- Company Handbook: `/Company_Handbook.md`
- Business Goals: `/Business_Goals.md`
- Dashboard: `/Dashboard.md`

---

## Execution Log

| Step | Timestamp | Action | Result |
|------|-----------|--------|--------|
'''
        
        filepath.write_text(content, encoding='utf-8')
        
        # Log plan creation
        self._log_plan(task_name, str(filepath), priority)
        
        return filepath
    
    def _log_plan(self, task_name: str, filepath: str, priority: str):
        """Log plan creation."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'plans_{today}.jsonl'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'task': task_name,
            'file': filepath,
            'priority': priority
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def generate_from_action_file(self, action_file: Path) -> Optional[Path]:
        """
        Generate a plan by analyzing an action file.
        
        Args:
            action_file: Path to the action file in Needs_Action
            
        Returns:
            Path to created plan, or None if no plan needed
        """
        if not action_file.exists():
            return None
        
        content = action_file.read_text(encoding='utf-8')
        
        # Parse frontmatter
        task_type = "general"
        priority = "normal"
        
        if '---' in content:
            parts = content.split('---')
            if len(parts) >= 2:
                frontmatter = parts[1]
                if 'type: email' in frontmatter:
                    task_type = "email_response"
                elif 'type: whatsapp' in frontmatter:
                    task_type = "message_response"
                elif 'type: file_drop' in frontmatter:
                    task_type = "file_processing"
                if 'priority: high' in frontmatter or 'priority: critical' in frontmatter:
                    priority = "high"
        
        # Generate task-specific plans
        if task_type == "email_response":
            return self._create_email_plan(action_file, priority)
        elif task_type == "message_response":
            return self._create_message_plan(action_file, priority)
        elif task_type == "file_processing":
            return self._create_file_plan(action_file, priority)
        else:
            return self._create_general_plan(action_file, priority)
    
    def _create_email_plan(self, action_file: Path, priority: str) -> Path:
        """Create plan for email response task."""
        task_name = f"Email Response - {action_file.stem}"
        objective = "Read the email, determine appropriate response, draft reply if needed, and archive."
        
        steps = [
            {"action": "Read and understand the email content", "status": "pending"},
            {"action": "Check Company Handbook for response guidelines", "status": "pending"},
            {"action": "Determine if response is needed", "status": "pending"},
            {"action": "Draft response (if needed) or flag for human", "status": "pending"},
            {"action": "Move email action file to /Done", "status": "pending"}
        ]
        
        return self.create_plan(
            task_name=task_name,
            objective=objective,
            steps=steps,
            source_file=action_file.name,
            priority=priority
        )
    
    def _create_message_plan(self, action_file: Path, priority: str) -> Path:
        """Create plan for message response task."""
        task_name = f"Message Response - {action_file.stem}"
        objective = "Read the message, identify urgency, respond appropriately."
        
        steps = [
            {"action": "Read and understand the message", "status": "pending"},
            {"action": "Check for keywords indicating urgency", "status": "pending"},
            {"action": "Determine appropriate response action", "status": "pending"},
            {"action": "Respond via appropriate channel (may need human)", "status": "pending"},
            {"action": "Move message file to /Done", "status": "pending"}
        ]
        
        return self.create_plan(
            task_name=task_name,
            objective=objective,
            steps=steps,
            source_file=action_file.name,
            priority=priority
        )
    
    def _create_file_plan(self, action_file: Path, priority: str) -> Path:
        """Create plan for file processing task."""
        task_name = f"File Processing - {action_file.stem}"
        objective = "Process the dropped file, extract actionable information, take required actions."
        
        steps = [
            {"action": "Read and analyze the file content", "status": "pending"},
            {"action": "Identify what action is needed", "status": "pending"},
            {"action": "Execute required action or create sub-tasks", "status": "pending"},
            {"action": "Archive or store processed file", "status": "pending"},
            {"action": "Move file action to /Done", "status": "pending"}
        ]
        
        return self.create_plan(
            task_name=task_name,
            objective=objective,
            steps=steps,
            source_file=action_file.name,
            priority=priority
        )
    
    def _create_general_plan(self, action_file: Path, priority: str) -> Path:
        """Create general plan for unknown task type."""
        task_name = f"Task - {action_file.stem}"
        objective = "Analyze and complete the task described in the action file."
        
        steps = [
            {"action": "Read and understand the task requirements", "status": "pending"},
            {"action": "Check Company Handbook for relevant rules", "status": "pending"},
            {"action": "Break down into sub-tasks if complex", "status": "pending"},
            {"action": "Execute tasks or request approval if needed", "status": "pending"},
            {"action": "Move to /Done when complete", "status": "pending"}
        ]
        
        return self.create_plan(
            task_name=task_name,
            objective=objective,
            steps=steps,
            source_file=action_file.name,
            priority=priority
        )
    
    def generate_all_plans(self) -> int:
        """
        Generate plans for all action files without plans.
        
        Returns:
            Number of plans created
        """
        if not self.needs_action.exists():
            return 0
        
        created = 0
        
        for action_file in self.needs_action.glob('*.md'):
            # Check if plan already exists
            plan_name = f"PLAN_*_{action_file.stem}*"
            existing_plans = list(self.plans.glob(plan_name))
            
            if not existing_plans:
                plan = self.generate_from_action_file(action_file)
                if plan:
                    created += 1
                    print(f"Created plan: {plan.name}")
        
        return created


def main():
    parser = argparse.ArgumentParser(
        description='Plan Generator - Create structured plans for tasks'
    )
    parser.add_argument(
        'vault_path',
        help='Path to the Obsidian vault root'
    )
    parser.add_argument(
        '--task', '-t',
        type=str,
        help='Create a plan for a specific task'
    )
    parser.add_argument(
        '--objective', '-o',
        type=str,
        help='Task objective (used with --task)'
    )
    parser.add_argument(
        '--generate-all',
        action='store_true',
        help='Generate plans for all pending action files'
    )
    parser.add_argument(
        '--priority', '-p',
        choices=['low', 'normal', 'high', 'critical'],
        default='normal',
        help='Task priority (default: normal)'
    )
    
    args = parser.parse_args()
    
    vault = Path(args.vault_path)
    if not vault.exists():
        print(f"Error: Vault path does not exist: {vault}")
        sys.exit(1)
    
    generator = PlanGenerator(str(vault))
    
    if args.generate_all:
        count = generator.generate_all_plans()
        print(f"\nGenerated {count} plan(s).")
    
    elif args.task:
        objective = args.objective or "Complete the specified task."
        
        steps = [
            {"action": "Analyze task requirements", "status": "pending"},
            {"action": "Check Company Handbook for guidelines", "status": "pending"},
            {"action": "Execute task steps", "status": "pending"},
            {"action": "Verify completion", "status": "pending"}
        ]
        
        plan = generator.create_plan(
            task_name=args.task,
            objective=objective,
            steps=steps,
            priority=args.priority
        )
        print(f"Plan created: {plan}")
    
    else:
        # Default: generate all plans
        count = generator.generate_all_plans()
        print(f"Generated {count} plan(s).")
        print("\nUse --task to create a custom plan.")
        print("Use --generate-all to create plans for all pending items.")


if __name__ == '__main__':
    main()
