"""
Facebook & Instagram Watcher for AI Employee - Gold Tier

Monitors Facebook Page and Instagram Business account for:
- New messages
- Comments on posts
- Mentions
- Engagement metrics

Creates action files in Needs_Action folder for Claude to process.
"""

import os
import sys
import time
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.user import User
from facebook_business.adobjects.photo import Photo
from facebook_business.exceptions import FacebookRequestError

from base_watcher import BaseWatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FacebookWatcher(BaseWatcher):
    """Watcher for Facebook Page and Instagram Business"""
    
    def __init__(
        self,
        vault_path: str,
        check_interval: int = 300,  # 5 minutes
        keywords: Optional[List[str]] = None
    ):
        super().__init__(vault_path, check_interval)
        
        # Initialize Facebook credentials from environment
        self.app_id = os.getenv('FACEBOOK_APP_ID')
        self.app_secret = os.getenv('FACEBOOK_APP_SECRET')
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.page_id = os.getenv('FACEBOOK_PAGE_ID')
        self.instagram_account_id = os.getenv('INSTAGRAM_ACCOUNT_ID')
        
        # Keywords to prioritize
        self.keywords = keywords or ['urgent', 'asap', 'invoice', 'payment', 'help', 'question']
        
        # Track processed items to avoid duplicates
        self.processed_messages = set()
        self.processed_comments = set()
        
        # Session file for persistence
        self.session_file = self.vault_path / '.facebook_session' / 'state.json'
        self._load_session()
        
        # Initialize Facebook API
        self._init_api()
    
    def _init_api(self):
        """Initialize Facebook Ads API"""
        if not all([self.app_id, self.app_secret, self.access_token]):
            logger.warning("Facebook credentials not found. Set FACEBOOK_* environment variables.")
            self.api_initialized = False
            return
        
        try:
            FacebookAdsApi.init(
                app_id=self.app_id,
                app_secret=self.app_secret,
                access_token=self.access_token
            )
            self.api_initialized = True
            logger.info("Facebook API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Facebook API: {e}")
            self.api_initialized = False
    
    def _load_session(self):
        """Load session state from file"""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    state = json.load(f)
                    self.processed_messages = set(state.get('processed_messages', []))
                    self.processed_comments = set(state.get('processed_comments', []))
                logger.info(f"Loaded session: {len(self.processed_messages)} messages, {len(self.processed_comments)} comments tracked")
            except Exception as e:
                logger.error(f"Failed to load session: {e}")
        else:
            logger.info("No existing session found, starting fresh")
    
    def _save_session(self):
        """Save session state to file"""
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.session_file, 'w') as f:
                json.dump({
                    'processed_messages': list(self.processed_messages),
                    'processed_comments': list(self.processed_comments)
                }, f)
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """Check for new messages and comments"""
        if not self.api_initialized:
            return []
        
        updates = []
        
        try:
            # Check for new messages
            messages = self._get_new_messages()
            updates.extend(messages)
            
            # Check for new comments
            comments = self._get_new_comments()
            updates.extend(comments)
            
            # Check for mentions
            mentions = self._get_new_mentions()
            updates.extend(mentions)
            
        except FacebookRequestError as e:
            logger.error(f"Facebook API error: {e}")
            # Token might be expired
            if e.api_error_code() == 190:
                logger.error("Facebook access token expired. Please refresh.")
        except Exception as e:
            logger.error(f"Error checking Facebook updates: {e}")
        
        return updates
    
    def _get_new_messages(self) -> List[Dict[str, Any]]:
        """Get new messages from Facebook Page"""
        messages = []
        
        try:
            page = Page(self.page_id)
            
            # Get conversations with messages (requires pages_messaging permission)
            try:
                conversations = page.get_conversations(fields=['messages{from,message,created_time,id}'])
                
                for conversation in conversations:
                    convo_messages = conversation.get_messages(limit=10)
                    for msg in convo_messages:
                        msg_id = msg.get('id')
                        if msg_id and msg_id not in self.processed_messages:
                            message_data = {
                                'type': 'facebook_message',
                                'id': msg_id,
                                'from': msg.get('from', {}).get('name', 'Unknown'),
                                'message': msg.get('message', ''),
                                'created_time': msg.get('created_time'),
                                'conversation_id': conversation.get('id'),
                                'priority': self._calculate_priority(msg.get('message', ''))
                            }
                            messages.append(message_data)
                            self.processed_messages.add(msg_id)
            except Exception as e:
                # Skip messages if permission not available
                logger.debug(f"Messages not accessible: {e}")
        
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
        
        return messages
    
    def _get_new_comments(self) -> List[Dict[str, Any]]:
        """Get new comments on Facebook posts"""
        comments = []
        
        try:
            page = Page(self.page_id)
            
            # Get recent posts - use params instead of keyword argument
            try:
                posts = page.get_feed(params={'limit': 5})
            except Exception as e:
                logger.debug(f"Feed not accessible: {e}")
                return comments
            
            for post in posts:
                try:
                    post_comments = post.get_comments(fields=['from,message,created_time,id'])
                    for comment in post_comments:
                        comment_id = comment.get('id')
                        if comment_id and comment_id not in self.processed_comments:
                            comment_data = {
                                'type': 'facebook_comment',
                                'id': comment_id,
                                'from': comment.get('from', {}).get('name', 'Unknown'),
                                'message': comment.get('message', ''),
                                'created_time': comment.get('created_time'),
                                'post_id': post.get('id'),
                                'priority': self._calculate_priority(comment.get('message', ''))
                            }
                            comments.append(comment_data)
                            self.processed_comments.add(comment_id)
                except Exception as e:
                    logger.debug(f"Error getting comments for post: {e}")
        
        except Exception as e:
            logger.error(f"Error getting comments: {e}")
        
        return comments
    
    def _get_new_mentions(self) -> List[Dict[str, Any]]:
        """Get new mentions of the page"""
        mentions = []
        
        try:
            page = Page(self.page_id)
            
            # Get tagged posts
            tagged_posts = page.get_tagged(fields=['from,message,created_time,id'])
            
            for post in tagged_posts:
                mention_data = {
                    'type': 'facebook_mention',
                    'id': post.get('id'),
                    'from': post.get('from', {}).get('name', 'Unknown'),
                    'message': post.get('message', ''),
                    'created_time': post.get('created_time'),
                    'priority': 'high'  # Mentions are always high priority
                }
                mentions.append(mention_data)
        
        except Exception as e:
            logger.error(f"Error getting mentions: {e}")
        
        return mentions
    
    def _calculate_priority(self, text: str) -> str:
        """Calculate message priority based on keywords"""
        text_lower = text.lower()
        
        # High priority keywords
        high_priority = ['urgent', 'asap', 'emergency', 'help', 'complaint', 'angry', 'refund']
        if any(kw in text_lower for kw in high_priority):
            return 'high'
        
        # Medium priority keywords
        medium_priority = ['invoice', 'payment', 'price', 'cost', 'question', 'how', 'when']
        if any(kw in text_lower for kw in medium_priority):
            return 'medium'
        
        return 'normal'
    
    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """Create action file in Needs_Action folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        item_type = item.get('type', 'unknown')
        safe_name = item.get('from', 'Unknown').replace(' ', '_')
        
        filename = f"{item_type.upper()}_{safe_name}_{timestamp}.md"
        filepath = self.needs_action / 'Facebook' / filename
        
        # Ensure Facebook subfolder exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        priority = item.get('priority', 'normal')
        priority_emoji = {'high': '🔴', 'medium': '🟡', 'normal': '🟢'}.get(priority, '⚪')
        
        content = f"""---
type: {item.get('type', 'unknown')}
from: {item.get('from', 'Unknown')}
received: {item.get('created_time', datetime.now().isoformat())}
priority: {priority}
status: pending
platform: facebook
{f"conversation_id: {item.get('conversation_id')}" if item.get('conversation_id') else ""}
{f"post_id: {item.get('post_id')}" if item.get('post_id') else ""}
---

# {priority_emoji} {item.get('type', 'Facebook Interaction').replace('_', ' ').title()}

**From:** {item.get('from', 'Unknown')}
**Received:** {item.get('created_time', 'Unknown')}
**Priority:** {priority}

## Message Content

{item.get('message', 'No content')}

## Suggested Actions

- [ ] Review message
- [ ] Draft response
- [ ] Get approval if needed
- [ ] Send response via Facebook MCP
- [ ] Archive after processing

## Notes

<!-- Add any additional context or notes here -->

---
*Created by Facebook Watcher - Gold Tier AI Employee*
"""
        
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created action file: {filepath}")
        
        # Save session after processing
        self._save_session()
        
        return filepath


class InstagramWatcher(BaseWatcher):
    """Watcher for Instagram Business account"""
    
    def __init__(
        self,
        vault_path: str,
        check_interval: int = 300,
        keywords: Optional[List[str]] = None
    ):
        super().__init__(vault_path, check_interval)
        
        # Instagram uses same Facebook API
        self.app_id = os.getenv('FACEBOOK_APP_ID')
        self.app_secret = os.getenv('FACEBOOK_APP_SECRET')
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.instagram_account_id = os.getenv('INSTAGRAM_ACCOUNT_ID')
        
        self.keywords = keywords or ['urgent', 'dm', 'message', 'question', 'price']
        self.processed_messages = set()
        
        self.session_file = self.vault_path / '.facebook_session' / 'instagram_state.json'
        self._load_session()
        self._init_api()
    
    def _init_api(self):
        """Initialize Facebook Ads API for Instagram"""
        if not all([self.app_id, self.app_secret, self.access_token]):
            logger.warning("Instagram credentials not found.")
            self.api_initialized = False
            return
        
        try:
            FacebookAdsApi.init(
                app_id=self.app_id,
                app_secret=self.app_secret,
                access_token=self.access_token
            )
            self.api_initialized = True
            logger.info("Instagram API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Instagram API: {e}")
            self.api_initialized = False
    
    def _load_session(self):
        """Load session state"""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    state = json.load(f)
                    self.processed_messages = set(state.get('processed_messages', []))
            except Exception as e:
                logger.error(f"Failed to load session: {e}")
    
    def _save_session(self):
        """Save session state"""
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.session_file, 'w') as f:
                json.dump({
                    'processed_messages': list(self.processed_messages)
                }, f)
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """Check for new Instagram messages and comments"""
        if not self.api_initialized or not self.instagram_account_id:
            return []
        
        updates = []
        
        try:
            # Get Instagram conversations
            conversations = self._get_conversations()
            updates.extend(conversations)
            
            # Get Instagram comments
            comments = self._get_comments()
            updates.extend(comments)
            
        except Exception as e:
            logger.error(f"Error checking Instagram updates: {e}")
        
        return updates
    
    def _get_conversations(self) -> List[Dict[str, Any]]:
        """Get Instagram direct messages"""
        messages = []
        
        try:
            from facebook_business.adobjects.instagramuser import InstagramUser
            
            ig_user = InstagramUser(self.instagram_account_id)
            
            # Get conversations
            conversations = ig_user.get_conversations()
            
            for convo in conversations:
                convo_messages = convo.get_messages()
                for msg in convo_messages:
                    msg_id = msg.get('id')
                    if msg_id and msg_id not in self.processed_messages:
                        message_data = {
                            'type': 'instagram_message',
                            'id': msg_id,
                            'from': msg.get('from', {}).get('username', 'Unknown'),
                            'message': msg.get('text', ''),
                            'created_time': msg.get('timestamp'),
                            'priority': self._calculate_priority(msg.get('text', ''))
                        }
                        messages.append(message_data)
                        self.processed_messages.add(msg_id)
        
        except Exception as e:
            logger.error(f"Error getting Instagram messages: {e}")
        
        return messages
    
    def _get_comments(self) -> List[Dict[str, Any]]:
        """Get Instagram media comments"""
        comments = []
        
        try:
            from facebook_business.adobjects.instagramuser import InstagramUser
            
            ig_user = InstagramUser(self.instagram_account_id)
            
            # Get recent media
            media = ig_user.get_media(limit=5)
            
            for item in media:
                item_comments = item.get_comments()
                for comment in item_comments:
                    comment_id = comment.get('id')
                    if comment_id and comment_id not in self.processed_messages:
                        comment_data = {
                            'type': 'instagram_comment',
                            'id': comment_id,
                            'from': comment.get('from', {}).get('username', 'Unknown'),
                            'message': comment.get('text', ''),
                            'created_time': comment.get('timestamp'),
                            'media_id': item.get('id'),
                            'priority': self._calculate_priority(comment.get('text', ''))
                        }
                        comments.append(comment_data)
                        self.processed_messages.add(comment_id)
        
        except Exception as e:
            logger.error(f"Error getting Instagram comments: {e}")
        
        return comments
    
    def _calculate_priority(self, text: str) -> str:
        """Calculate priority"""
        text_lower = text.lower()
        
        high_priority = ['urgent', 'asap', 'help', 'question', 'price', 'cost']
        if any(kw in text_lower for kw in high_priority):
            return 'high'
        
        return 'normal'
    
    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """Create action file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        item_type = item.get('type', 'unknown')
        safe_name = item.get('from', 'Unknown').replace(' ', '_')
        
        filename = f"{item_type.upper()}_{safe_name}_{timestamp}.md"
        filepath = self.needs_action / 'Facebook' / filename
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        priority = item.get('priority', 'normal')
        priority_emoji = {'high': '🔴', 'medium': '🟡', 'normal': '🟢'}.get(priority, '⚪')
        
        content = f"""---
type: {item.get('type', 'unknown')}
from: {item.get('from', 'Unknown')}
received: {item.get('created_time', datetime.now().isoformat())}
priority: {priority}
status: pending
platform: instagram
---

# {priority_emoji} {item.get('type', 'Instagram Interaction').replace('_', ' ').title()}

**From:** {item.get('from', 'Unknown')}
**Received:** {item.get('created_time', 'Unknown')}
**Priority:** {priority}

## Content

{item.get('message', 'No content')}

## Suggested Actions

- [ ] Review interaction
- [ ] Draft response
- [ ] Send via Instagram/Facebook MCP
- [ ] Archive

---
*Created by Instagram Watcher - Gold Tier AI Employee*
"""
        
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created Instagram action file: {filepath}")
        
        self._save_session()
        
        return filepath


def main():
    """Main entry point for Facebook/Instagram watcher"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Facebook & Instagram Watcher')
    parser.add_argument('vault_path', type=str, help='Path to Obsidian vault')
    parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds')
    parser.add_argument('--keywords', type=str, help='Comma-separated keywords to prioritize')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--setup', action='store_true', help='Run setup wizard')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    if args.setup:
        print("\n=== Facebook/Instagram Watcher Setup ===\n")
        print("Please ensure you have:")
        print("1. Created a Facebook App at developers.facebook.com")
        print("2. Enabled Facebook Login product")
        print("3. Generated a Page Access Token")
        print("4. (Optional) Connected Instagram Business account")
        print("\nAdd these to your .env file:")
        print("  FACEBOOK_APP_ID=your_app_id")
        print("  FACEBOOK_APP_SECRET=your_app_secret")
        print("  FACEBOOK_ACCESS_TOKEN=your_access_token")
        print("  FACEBOOK_PAGE_ID=your_page_id")
        print("  INSTAGRAM_ACCOUNT_ID=your_instagram_id (optional)")
        return
    
    keywords = args.keywords.split(',') if args.keywords else None
    
    # Create Facebook watcher
    fb_watcher = FacebookWatcher(
        vault_path=str(vault_path),
        check_interval=args.interval,
        keywords=keywords
    )
    
    # Create Instagram watcher
    ig_watcher = InstagramWatcher(
        vault_path=str(vault_path),
        check_interval=args.interval,
        keywords=keywords
    )
    
    logger.info("Starting Facebook & Instagram Watcher...")
    
    if args.once:
        # Run once
        logger.info("Running single check...")
        fb_updates = fb_watcher.check_for_updates()
        ig_updates = ig_watcher.check_for_updates()
        
        for update in fb_updates + ig_updates:
            fb_watcher.create_action_file(update)
        
        logger.info(f"Found {len(fb_updates) + len(ig_updates)} updates")
    else:
        # Run continuously
        try:
            while True:
                fb_updates = fb_watcher.check_for_updates()
                ig_updates = ig_watcher.check_for_updates()
                
                for update in fb_updates + ig_updates:
                    fb_watcher.create_action_file(update)
                
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("Watcher stopped by user")


if __name__ == '__main__':
    main()
