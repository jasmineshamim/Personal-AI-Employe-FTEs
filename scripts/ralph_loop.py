"""
Ralph Wiggum Loop Implementation for AI Employee - Gold Tier

Implements the "Ralph Wiggum" pattern - a Stop hook that keeps Claude Code
iterating until tasks are complete. This enables autonomous multi-step
task completion without manual intervention.

The pattern:
1. Create a state file with the task
2. Claude works on the task
3. Claude tries to exit
4. Stop hook checks: Is task complete?
5. YES → Allow exit
6. NO → Block exit, re-inject prompt (loop continues)
"""

import os
import sys
import time
import logging
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RalphWiggumLoop:
    """Ralph Wiggum autonomous task loop"""
    
    def __init__(
        self,
        vault_path: str,
        task: str,
        max_iterations: int = 10,
        completion_promise: Optional[str] = None,
        check_file_movement: bool = True
    ):
        self.vault_path = Path(vault_path)
        self.task = task
        self.max_iterations = max_iterations
        self.completion_promise = completion_promise or "TASK_COMPLETE"
        self.check_file_movement = check_file_movement
        
        # State tracking
        self.current_iteration = 0
        self.task_complete = False
        self.state_file: Optional[Path] = None
        self.output_log: List[Dict[str, Any]] = []
        
        # Folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.ralph_state = self.vault_path / '.ralph_state'
        
        # Ensure state folder exists
        self.ralph_state.mkdir(parents=True, exist_ok=True)
    
    def create_state_file(self) -> Path:
        """Create initial state file for the task"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"RALPH_TASK_{timestamp}.md"
        self.state_file = self.ralph_state / filename
        
        content = f"""---
type: ralph_wiggum_task
task: {self.task}
created: {datetime.now().isoformat()}
iteration: 0
max_iterations: {self.max_iterations}
status: pending
completion_promise: {self.completion_promise}
---

# 🔄 Ralph Wiggum Autonomous Task

**Task:** {self.task}

**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

**Max Iterations:** {self.max_iterations}

**Current Iteration:** 0

---

## Task Description

{self.task}

---

## Completion Criteria

The task is complete when:
1. All subtasks are completed
2. Output includes: `{self.completion_promise}`
3. OR relevant files moved to /Done folder

---

## Iteration Log

"""
        
        self.state_file.write_text(content, encoding='utf-8')
        logger.info(f"Created Ralph Wiggum state file: {self.state_file}")
        
        return self.state_file
    
    def check_completion(self, claude_output: str) -> bool:
        """Check if task is complete"""
        
        # Check for completion promise in output
        if self.completion_promise and self.completion_promise in claude_output:
            logger.info(f"Completion promise detected: {self.completion_promise}")
            return True
        
        # Check for file movement to Done
        if self.check_file_movement:
            # Check if any files were moved to Done in last minute
            done_files = list(self.done.glob('*.md'))
            for f in done_files:
                if f.stat().st_mtime > time.time() - 60:
                    logger.info(f"File moved to Done: {f.name}")
                    return True
        
        # Check state file for completion marker
        if self.state_file and self.state_file.exists():
            content = self.state_file.read_text(encoding='utf-8')
            if 'status: complete' in content:
                logger.info("State file marked as complete")
                return True
        
        return False
    
    def update_state_file(self, iteration: int, claude_output: str):
        """Update state file with iteration progress"""
        if not self.state_file or not self.state_file.exists():
            return
        
        content = self.state_file.read_text(encoding='utf-8')
        
        # Update iteration count
        content = content.replace(
            f'**Current Iteration:** {iteration - 1}',
            f'**Current Iteration:** {iteration}'
        )
        
        # Add to iteration log
        log_entry = f"""
### Iteration {iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Status:** In Progress

**Output Summary:**
{claude_output[:500]}...

---
"""
        
        # Find iteration log section and append
        if '## Iteration Log' in content:
            content = content.replace('## Iteration Log', f'## Iteration Log\n{log_entry}')
        else:
            content += f'\n## Iteration Log\n{log_entry}'
        
        self.state_file.write_text(content, encoding='utf-8')
    
    def mark_complete(self):
        """Mark task as complete"""
        if self.state_file and self.state_file.exists():
            content = self.state_file.read_text(encoding='utf-8')
            content = content.replace('status: pending', 'status: complete')
            content += f"\n\n## ✅ Task Complete\n\nCompleted at: {datetime.now().isoformat()}\n"
            self.state_file.write_text(content, encoding='utf-8')
        
        self.task_complete = True
        logger.info("Task marked as complete")
    
    def run_loop(self, claude_command: Optional[str] = None):
        """
        Run the Ralph Wiggum loop
        
        Args:
            claude_command: Optional custom Claude command
        """
        logger.info(f"Starting Ralph Wiggum Loop for task: {self.task}")
        logger.info(f"Max iterations: {self.max_iterations}")
        
        # Create initial state file
        self.create_state_file()
        
        # Build Claude command
        if not claude_command:
            claude_command = f'claude --prompt "{self.task}"'
        
        while self.current_iteration < self.max_iterations and not self.task_complete:
            self.current_iteration += 1
            logger.info(f"\n{'='*50}")
            logger.info(f"Iteration {self.current_iteration}/{self.max_iterations}")
            logger.info(f"{'='*50}")
            
            # Run Claude
            try:
                result = subprocess.run(
                    claude_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout per iteration
                )
                
                claude_output = result.stdout + result.stderr
                
                # Log output
                self.output_log.append({
                    'iteration': self.current_iteration,
                    'timestamp': datetime.now().isoformat(),
                    'output_length': len(claude_output),
                    'exit_code': result.returncode
                })
                
                # Update state file
                self.update_state_file(self.current_iteration, claude_output)
                
                # Check for completion
                if self.check_completion(claude_output):
                    logger.info("✅ Task completion detected!")
                    self.mark_complete()
                    break
                
                # Check if Claude wants to exit
                if result.returncode == 0 and 'exit' in claude_output.lower():
                    logger.info("Claude attempted to exit - re-injecting prompt...")
                    # Loop continues - this is the Ralph Wiggum magic!
                
            except subprocess.TimeoutExpired:
                logger.warning(f"Iteration {self.current_iteration} timed out")
                self.output_log.append({
                    'iteration': self.current_iteration,
                    'timestamp': datetime.now().isoformat(),
                    'error': 'timeout'
                })
            except Exception as e:
                logger.error(f"Error in iteration {self.current_iteration}: {e}")
                self.output_log.append({
                    'iteration': self.current_iteration,
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                })
        
        # Final status
        if self.task_complete:
            logger.info(f"\n✅ Task completed in {self.current_iteration} iterations")
        else:
            logger.warning(f"\n⚠️ Task incomplete after {self.max_iterations} iterations")
        
        # Generate summary
        self._generate_summary()
        
        return self.task_complete
    
    def _generate_summary(self):
        """Generate loop summary"""
        summary_file = self.ralph_state / f"RALPH_SUMMARY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        content = f"""---
type: ralph_wiggum_summary
task: {self.task}
completed: {self.task_complete}
iterations: {self.current_iteration}
generated: {datetime.now().isoformat()}
---

# Ralph Wiggum Loop Summary

**Task:** {self.task}

**Status:** {'✅ Complete' if self.task_complete else '⚠️ Incomplete'}

**Iterations Used:** {self.current_iteration}/{self.max_iterations}

**Completed At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Execution Summary

"""
        
        for entry in self.output_log:
            content += f"- **Iteration {entry['iteration']}** ({entry['timestamp']}): "
            if 'error' in entry:
                content += f"Error: {entry['error']}\n"
            else:
                content += f"Output: {entry['output_length']} chars\n"
        
        content += f"""
---

## State File

Location: `{self.state_file}`

---

*Generated by Ralph Wiggum Loop - Gold Tier AI Employee*
"""
        
        summary_file.write_text(content, encoding='utf-8')
        logger.info(f"Summary generated: {summary_file}")


def main():
    """Main entry point for Ralph Wiggum Loop"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ralph Wiggum Autonomous Task Loop')
    parser.add_argument('vault_path', type=str, help='Path to Obsidian vault')
    parser.add_argument('task', type=str, help='Task description')
    parser.add_argument('--max-iterations', type=int, default=10, help='Maximum iterations')
    parser.add_argument('--promise', type=str, default='TASK_COMPLETE', help='Completion promise')
    parser.add_argument('--command', type=str, help='Custom Claude command')
    parser.add_argument('--demo', action='store_true', help='Run demo mode')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    if args.demo:
        print("\n=== Ralph Wiggum Loop Demo ===\n")
        print("The Ralph Wiggum pattern keeps Claude Code iterating until a task is complete.")
        print("\nHow it works:")
        print("1. Create a state file with the task")
        print("2. Run Claude with the task prompt")
        print("3. Check if task is complete (completion promise or file movement)")
        print("4. If NOT complete → Re-inject prompt (loop continues)")
        print("5. If complete → Allow exit")
        print("\nExample usage:")
        print(f'  python scripts/ralph_loop.py {vault_path} "Process all pending invoices" --max-iterations 5')
        return
    
    loop = RalphWiggumLoop(
        vault_path=str(vault_path),
        task=args.task,
        max_iterations=args.max_iterations,
        completion_promise=args.promise
    )
    
    success = loop.run_loop(args.command)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
