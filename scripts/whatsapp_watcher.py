#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Watcher - Final Robust Version
(Fixed Name Extraction & Hanging)
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import logging

sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Configure logging to ensure we see output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class WhatsAppWatcher(BaseWatcher):
    WHATSAPP_URL = 'https://web.whatsapp.com'

    def __init__(
        self,
        vault_path: str,
        session_path: Optional[str] = None,
        check_interval: int = 30,
        keywords: Optional[List[str]] = None,
        headless: bool = False
    ):
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not installed.")

        super().__init__(vault_path, check_interval)

        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = self.vault_path / '.whatsapp_session'

        self.session_path.mkdir(parents=True, exist_ok=True)
        self.keywords = keywords or ['urgent', 'asap', 'invoice', 'payment', 'help']
        self.headless = headless
        self.processed_chats = set()

    def setup_session(self) -> bool:
        logger.info("Starting WhatsApp Web setup...")
        logger.info("Please scan QR code and wait for chats to load.")
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=False,
                viewport={'width': 1280, 'height': 720}
            )
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto(self.WHATSAPP_URL)
            try:
                page.wait_for_timeout(60000) # Wait 1 min for login
            except: pass
            browser.close()
        return True

    def check_for_updates(self) -> list:
        messages = []
        try:
            with sync_playwright() as p:
                logger.info("Launching browser...")
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=self.headless,
                    viewport={'width': 1280, 'height': 720}
                )
                page = browser.pages[0] if browser.pages else browser.new_page()

                try:
                    logger.info("Opening WhatsApp Web...")
                    # Use 'commit' to avoid waiting for all network connections (which keeps it open)
                    page.goto(self.WHATSAPP_URL, wait_until='commit', timeout=30000)
                    
                    # Wait for the chat list to appear
                    logger.info("Waiting for chat list...")
                    page.wait_for_selector('div[role="grid"]', timeout=15000)
                    
                    # Wait for chat items to render
                    page.wait_for_timeout(3000)
                    logger.info("Scanning chats...")

                    # Select chat rows
                    chat_rows = page.query_selector_all('div[role="gridcell"]')
                    
                    if not chat_rows:
                        # Try backup selector
                        chat_rows = page.query_selector_all('[data-testid="cell-frame-container"]')

                    if not chat_rows:
                        logger.warning("No chats found (Check if you are logged in).")
                        browser.close()
                        return []

                    logger.info(f"Found {len(chat_rows)} chats.")

                    for row in chat_rows:
                        try:
                            # 1. Get Text
                            chat_text = row.inner_text()
                            
                            # 2. Extract Name using robust split logic
                            parts = chat_text.split('|')
                            chat_name = "Unknown"
                            
                            # Logic to handle "2 unread messages | Name | ..."
                            if len(parts) > 1 and ("unread" in parts[0].lower() or parts[0].strip().isdigit()):
                                chat_name = parts[1].strip()
                            else:
                                chat_name = parts[0].strip()

                            # Skip if name is empty or just numbers (and not a phone number format)
                            if not chat_name or len(chat_name) < 2:
                                continue

                            # 3. Check Keywords
                            text_lower = chat_text.lower()
                            found_keyword = None
                            for kw in self.keywords:
                                if kw in text_lower:
                                    found_keyword = kw
                                    break

                            if found_keyword:
                                # Avoid duplicates
                                chat_key = f"{chat_name}:{chat_text[:30]}"
                                if chat_key not in self.processed_chats:
                                    messages.append({
                                        'chat_name': chat_name,
                                        'last_message': chat_text,
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    self.processed_chats.add(chat_key)
                                    logger.info(f"✅ Important message from: {chat_name} (Keyword: {found_keyword})")

                        except Exception as e:
                            logger.debug(f"Error processing one chat: {e}")
                            continue

                    browser.close()
                except PlaywrightTimeout:
                    logger.error("Timeout: WhatsApp Web did not load in time.")
                    browser.close()
                except Exception as e:
                    logger.error(f"WhatsApp Web Error: {e}")
                    browser.close()
        except Exception as e:
            logger.error(f"Browser Launch Error: {e}")

        return messages

    def create_action_file(self, message) -> Path:
        chat_name = message['chat_name']
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Clean filename
        safe_name = "".join(c if c.isalnum() else '_' for c in chat_name[:20])
        filename = f"WHATSAPP_{ts}_{safe_name}.md"
        filepath = self.needs_action / filename

        priority = 'normal'
        msg_lower = message['last_message'].lower()
        if any(kw in msg_lower for kw in ['urgent', 'asap', 'emergency']):
            priority = 'critical'
        elif any(kw in msg_lower for kw in ['invoice', 'payment', 'money']):
            priority = 'high'

        content = f'''---
type: whatsapp_message
from: {chat_name}
received: {message['timestamp']}
priority: {priority}
status: pending
---

# WhatsApp Message Received

- **From:** {chat_name}
- **Priority:** {priority}

## Message
{message['last_message']}

## Actions
- [ ] Review
- [ ] Reply
- [ ] Move to Done

---
*Generated by WhatsAppWatcher*
'''
        filepath.write_text(content, encoding='utf-8')
        return filepath


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('vault_path')
    parser.add_argument('--interval', type=int, default=30)
    parser.add_argument('--setup', action='store_true')
    args = parser.parse_args()

    vault = Path(args.vault_path)
    if not vault.exists():
        print(f"Error: {vault} not found")
        sys.exit(1)

    try:
        watcher = WhatsAppWatcher(str(vault), check_interval=args.interval)
    except ImportError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if args.setup:
        watcher.setup_session()
        return

    print("Starting WhatsApp Watcher...")
    watcher.run()

if __name__ == '__main__':
    main()
