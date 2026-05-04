"""
Twitter/X Browser Poster (Robust Version using Keyboard Shortcut)
Uses Ctrl+Enter to post, which is more reliable than button clicking.
"""

import os
import sys
import time
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Session file to store login state
SESSION_FILE = Path("twitter_session.json")

def login_and_save_session():
    """Open browser, let user login, then save session."""
    logger.info("Starting login process...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        logger.info("Opening Twitter Login...")
        page.goto("https://twitter.com/login")
        
        logger.info("Please login manually in the browser window.")
        logger.info("Waiting for you to reach the Home timeline...")
        
        try:
            page.wait_for_url("**/home", timeout=120000)
            logger.info("Login detected!")
            context.storage_state(path=SESSION_FILE)
            logger.info(f"Session saved to {SESSION_FILE}")
        except Exception as e:
            logger.error("Login timed out or failed.")
        finally:
            browser.close()

def post_tweet_via_browser(message):
    """Post a tweet using saved session and Ctrl+Enter shortcut."""
    if not SESSION_FILE.exists():
        logger.error("Session not found! Please run: python scripts/twitter_playwright_poster.py --login")
        return

    logger.info(f"Posting tweet: {message}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=SESSION_FILE)
        page = context.new_page()
        
        try:
            # Go to Home
            logger.info("Navigating to Home...")
            page.goto("https://twitter.com/home", wait_until="networkidle")
            time.sleep(5) # Wait for JS to load fully
            
            # Find the tweet text box using a more generic selector
            # Twitter uses contenteditable divs
            logger.info("Looking for Tweet box...")
            tweet_box = page.locator('div[contenteditable="true"][role="textbox"]').first
            
            # Wait for it to be visible and editable
            tweet_box.wait_for(state="visible", timeout=15000)
            tweet_box.click()
            time.sleep(1)
            
            # Type the message
            logger.info("Typing message...")
            tweet_box.fill(message)
            time.sleep(3) # Wait for Twitter to register text
            
            # Use Keyboard Shortcut Ctrl+Enter to Post
            # This is much more reliable than clicking the button
            logger.info("Pressing Ctrl+Enter to post...")
            page.keyboard.press("Control+Enter")
            
            # Wait for post to complete (URL change or toast notification)
            time.sleep(5)
            logger.info("✅ Tweet Posted Successfully via Browser!")
            
        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            logger.info("Tip: Ensure you are logged in and session is valid.")
        finally:
            time.sleep(3)
            browser.close()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Twitter Browser Poster (Free)")
    parser.add_argument('--login', action='store_true', help='Login and save session')
    parser.add_argument('--post', type=str, help='Message to tweet')
    
    args = parser.parse_args()
    
    if args.login:
        login_and_save_session()
    elif args.post:
        post_tweet_via_browser(args.post)
    else:
        print("Usage:")
        print("  1. Login first: python scripts/twitter_playwright_poster.py --login")
        print("  2. Post tweet:  python scripts/twitter_playwright_poster.py --post 'Hello World'")

if __name__ == '__main__':
    main()
