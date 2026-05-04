#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File System Watcher - Monitors a drop folder for new files.

This is the simplest watcher implementation for the Bronze tier.
When files are added to the Inbox folder, it creates corresponding
action files in Needs_Action for Claude Code to process.

Usage:
    python filesystem_watcher.py /path/to/vault

Or run continuously:
    python filesystem_watcher.py /path/to/vault --interval 30
"""

import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher


class DropFolderHandler(FileSystemEventHandler):
    """Handles file system events for the drop folder."""
    
    def __init__(self, watcher):
        """
        Initialize the handler.
        
        Args:
            watcher: The FilesystemWatcher instance
        """
        super().__init__()
        self.watcher = watcher
    
    def on_created(self, event):
        """Called when a file or directory is created."""
        if event.is_directory:
            return
        
        self.watcher.logger.info(f'File detected: {event.src_path}')
        try:
            self.watcher.process_file(Path(event.src_path))
        except Exception as e:
            self.watcher.logger.error(f'Error processing file: {e}')


class FilesystemWatcher(BaseWatcher):
    """Watches the Inbox folder for new files."""
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        """
        Initialize the filesystem watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (for polling fallback)
        """
        super().__init__(vault_path, check_interval)
        
        # Drop folder is the Inbox
        self.drop_folder = self.inbox
        self.observer = None
    
    def file_hash(self, filepath: Path) -> str:
        """Calculate a hash for the file to track processed files."""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return str(filepath.stat().st_mtime)
    
    def process_file(self, filepath: Path):
        """
        Process a newly detected file.
        
        Args:
            filepath: Path to the new file
        """
        # Skip if already processed
        file_id = self.file_hash(filepath)
        if file_id in self.processed_ids:
            self.logger.debug(f'File already processed: {filepath.name}')
            return
        
        # Create action file
        self.create_action_file({
            'filepath': filepath,
            'filename': filepath.name,
            'size': filepath.stat().st_size,
            'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
        })
        
        # Mark as processed
        self.processed_ids.add(file_id)
    
    def check_for_updates(self) -> list:
        """
        Check for new files in the drop folder.
        
        This is called periodically but the main detection happens
        via the FileSystemEventHandler.
        
        Returns:
            Empty list (files are processed via event handler)
        """
        # Initial scan for existing files
        if hasattr(self, '_initial_scan') and not self._initial_scan:
            self._initial_scan = True
            for filepath in self.drop_folder.iterdir():
                if filepath.is_file() and not filepath.name.startswith('.'):
                    file_id = self.file_hash(filepath)
                    if file_id not in self.processed_ids:
                        self.process_file(filepath)
        return []
    
    def create_action_file(self, item) -> Path:
        """
        Create a .md action file in Needs_Action folder.
        
        Args:
            item: Dictionary with file information
            
        Returns:
            Path to the created file
        """
        filepath = item['filepath']
        filename = item['filename']
        
        # Generate unique action file name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        action_filename = f'FILE_{timestamp}_{filename}.md'
        action_path = self.needs_action / action_filename
        
        # Read file content if it's a text file
        content_preview = ""
        try:
            if filepath.suffix.lower() in ['.txt', '.md', '.json', '.csv', '.py', '.js']:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content_preview = f.read(500)  # First 500 chars
        except Exception:
            pass
        
        # Create action file content
        content = f'''---
type: file_drop
source: {filename}
original_path: {filepath}
size: {item['size']} bytes
detected: {datetime.now().isoformat()}
priority: normal
status: pending
---

# File Drop for Processing

## File Information

- **Original Name:** {filename}
- **Size:** {item['size']} bytes
- **Detected:** {item['modified']}
- **Source:** Inbox folder

## Content Preview

```
{content_preview if content_preview else "[Binary file or unable to read]"}
```

## Suggested Actions

- [ ] Review file content
- [ ] Determine required action
- [ ] Process and move to /Done
- [ ] Archive if no action needed

## Notes

*Add any notes or context for processing this file*

---
*Generated by FilesystemWatcher v0.1*
'''
        
        action_path.write_text(content, encoding='utf-8')
        
        self.log_action('file_drop_processed', {
            'original_file': str(filepath),
            'action_file': str(action_path),
            'size': item['size']
        })
        
        return action_path
    
    def run(self):
        """Run the watcher with event-driven file detection."""
        self.logger.info(f'Starting FilesystemWatcher')
        self.logger.info(f'Watching folder: {self.drop_folder}')
        
        # Set initial scan flag
        self._initial_scan = False
        
        # Set up the observer
        event_handler = DropFolderHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.drop_folder), recursive=False)
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info('FilesystemWatcher stopped by user')
            self.observer.stop()
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            self.observer.stop()
        
        self.observer.join()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='File System Watcher - Monitor drop folder for new files'
    )
    parser.add_argument(
        'vault_path',
        help='Path to the Obsidian vault root'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=30,
        help='Check interval in seconds (default: 30)'
    )
    
    args = parser.parse_args()
    
    # Validate vault path
    vault = Path(args.vault_path)
    if not vault.exists():
        print(f"Error: Vault path does not exist: {vault}")
        sys.exit(1)
    
    if not (vault / 'Needs_Action').exists():
        print(f"Error: Vault missing 'Needs_Action' folder. Is this a valid AI Employee vault?")
        sys.exit(1)
    
    # Start watcher
    watcher = FilesystemWatcher(str(vault), args.interval)
    watcher.run()
