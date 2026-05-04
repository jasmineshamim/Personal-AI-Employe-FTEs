#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto File Mover - Automatically moves processed files to Done folder.

This script runs after Qwen Code processes files and moves them to Done.

Usage:
    python scripts\auto_file_mover.py AI_Employee_Vault
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime


def move_to_done(vault_path: str):
    """Move all processed files from Needs_Action to Done."""
    vault = Path(vault_path)
    needs_action = vault / 'Needs_Action'
    done = vault / 'Done'
    logs = vault / 'Logs'
    
    # Ensure Done folder exists
    done.mkdir(parents=True, exist_ok=True)
    
    # Get all .md files in Needs_Action
    files = list(needs_action.glob('*.md'))
    
    if not files:
        print("No files to move.")
        return 0
    
    moved_count = 0
    
    for file in files:
        try:
            # Create destination path
            dest = done / file.name
            
            # Add timestamp to avoid overwrites
            if dest.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                dest = done / f'{timestamp}_{file.name}'
            
            # Move file
            shutil.move(str(file), str(dest))
            print(f"[OK] Moved: {file.name}")
            
            # Log the move
            log_move(logs, file.name, str(dest))
            
            moved_count += 1
            
        except Exception as e:
            print(f"[FAILED] Could not move {file.name}: {e}")
    
    return moved_count


def log_move(logs_dir: Path, source: str, dest: str):
    """Log file move to JSONL."""
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = logs_dir / f'{today}.jsonl'
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action_type': 'moved_to_done',
        'source': source,
        'destination': dest,
        'actor': 'auto_file_mover'
    }
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f'{log_entry}\n')


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts\\auto_file_mover.py <vault_path>")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    vault = Path(vault_path)
    
    if not vault.exists():
        print(f"Error: Vault path does not exist: {vault}")
        sys.exit(1)
    
    print("=" * 70)
    print("AUTO FILE MOVER")
    print("=" * 70)
    print(f"Vault: {vault}")
    print()
    
    moved = move_to_done(vault_path)
    
    print()
    print("=" * 70)
    print(f"Moved {moved} file(s) to Done")
    print("=" * 70)


if __name__ == '__main__':
    main()
