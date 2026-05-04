"""
Twitter/X Watcher and Poster for AI Employee - Gold Tier

Monitors Twitter/X for:
- Mentions
- Direct messages
- Replies to your tweets
- Keyword mentions

Posts to Twitter/X:
- Single tweets
- Tweet threads
- Replies
- Scheduled tweets (draft mode with approval)

Uses Twitter API v2 with tweepy library.
"""

import os
import sys
import time
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import tweepy
from tweepy import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from base_watcher import BaseWatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TwitterWatcher(BaseWatcher):
    """Watcher for Twitter/X mentions and messages"""
    
    def __init__(
        self,
        vault_path: str,
        check_interval: int = 300,  # 5 minutes
        keywords: Optional[List[str]] = None
    ):
        super().__init__(vault_path, check_interval)
        
        # Twitter API credentials
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Keywords to prioritize
        self.keywords = keywords or ['urgent', 'help', 'question', 'invoice', 'payment']
        
        # Track processed items
        self.processed_tweets = set()
        self.processed_dms = set()
        
        # Session file
        self.session_file = self.vault_path / '.twitter_session' / 'state.json'
        self._load_session()
        
        # Initialize Twitter client
        self.client = None
        self.me = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Twitter API v2 client"""
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            logger.warning("Twitter credentials not configured")
            self.api_initialized = False
            return
        
        try:
            # Initialize client with OAuth 1.0a User Context
            self.client = Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                return_type=dict
            )
            
            # Get authenticated user info
            self.me = self.client.get_me()
            self.user_id = self.me['data']['id']
            self.username = self.me['data']['username']
            
            self.api_initialized = True
            logger.info(f"Twitter API initialized as @{self.username}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {e}")
            self.api_initialized = False
    
    def _load_session(self):
        """Load session state"""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    state = json.load(f)
                    self.processed_tweets = set(state.get('processed_tweets', []))
                    self.processed_dms = set(state.get('processed_dms', []))
                logger.info(f"Loaded Twitter session: {len(self.processed_tweets)} tweets tracked")
            except Exception as e:
                logger.error(f"Failed to load session: {e}")
    
    def _save_session(self):
        """Save session state"""
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.session_file, 'w') as f:
                json.dump({
                    'processed_tweets': list(self.processed_tweets),
                    'processed_dms': list(self.processed_dms)
                }, f)
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """Check for new Twitter activity"""
        if not self.api_initialized:
            return []
        
        updates = []
        
        try:
            # Check for mentions
            mentions = self._get_mentions()
            updates.extend(mentions)
            
            # Check for DMs (requires elevated access)
            dms = self._get_dms()
            updates.extend(dms)
            
        except tweepy.TweepException as e:
            logger.error(f"Twitter API error: {e}")
            if e.api_codes and 89 in e.api_codes:  # Invalid/expired token
                logger.error("Twitter token expired. Please refresh credentials.")
        except Exception as e:
            logger.error(f"Error checking Twitter updates: {e}")
        
        return updates
    
    def _get_mentions(self) -> List[Dict[str, Any]]:
        """Get recent mentions"""
        mentions = []
        
        try:
            # Get mentions timeline
            mentions_data = self.client.get_users_mentions(
                id=self.user_id,
                max_results=10,
                tweet_fields=['created_at', 'text', 'author_id', 'public_metrics'],
                expansions=['author_id'],
                user_fields=['username', 'name']
            )
            
            if 'data' in mentions_data:
                users = {u['id']: u for u in mentions_data.get('includes', {}).get('users', [])}
                
                for tweet in mentions_data['data']:
                    tweet_id = tweet['id']
                    
                    if tweet_id not in self.processed_tweets:
                        author = users.get(tweet['author_id'], {})
                        
                        mention_data = {
                            'type': 'twitter_mention',
                            'id': tweet_id,
                            'text': tweet['text'],
                            'from_username': author.get('username', 'unknown'),
                            'from_name': author.get('name', 'Unknown'),
                            'created_at': tweet['created_at'],
                            'metrics': tweet.get('public_metrics', {}),
                            'priority': self._calculate_priority(tweet['text'])
                        }
                        mentions.append(mention_data)
                        self.processed_tweets.add(tweet_id)
        
        except Exception as e:
            logger.error(f"Error getting mentions: {e}")
        
        return mentions
    
    def _get_dms(self) -> List[Dict[str, Any]]:
        """Get direct messages (requires elevated access)"""
        dms = []
        
        try:
            # Note: DM access requires elevated API access
            # This is a placeholder for standard API users
            logger.debug("DM checking requires elevated API access")
            
        except Exception as e:
            logger.debug(f"DM check not available: {e}")
        
        return dms
    
    def _calculate_priority(self, text: str) -> str:
        """Calculate tweet priority based on content"""
        text_lower = text.lower()
        
        high_priority = ['urgent', 'help', 'asap', 'emergency', 'complaint', 'issue', 'problem']
        if any(kw in text_lower for kw in high_priority):
            return 'high'
        
        medium_priority = ['question', 'how', 'when', 'what', 'invoice', 'payment', 'price']
        if any(kw in text_lower for kw in medium_priority):
            return 'medium'
        
        return 'normal'
    
    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """Create action file in Needs_Action folder"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        item_type = item.get('type', 'unknown')
        safe_name = item.get('from_username', 'unknown').replace(' ', '_')
        
        filename = f"{item_type.upper()}_{safe_name}_{timestamp}.md"
        filepath = self.needs_action / 'Twitter' / filename
        
        # Ensure Twitter subfolder exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        priority = item.get('priority', 'normal')
        priority_emoji = {'high': '🔴', 'medium': '🟡', 'normal': '🟢'}.get(priority, '⚪')
        
        metrics = item.get('metrics', {})
        
        content = f"""---
type: {item.get('type', 'unknown')}
tweet_id: {item.get('id')}
from: {item.get('from_name', 'Unknown')} (@{item.get('from_username', 'unknown')})
received: {item.get('created_at', datetime.now().isoformat())}
priority: {priority}
status: pending
platform: twitter
---

# {priority_emoji} Twitter Mention

**From:** {item.get('from_name', 'Unknown')} (@{item.get('from_username', 'unknown')})
**Received:** {item.get('created_at', 'Unknown')}
**Priority:** {priority}

## Tweet Content

{item.get('text', 'No content')}

## Engagement Metrics

- Retweets: {metrics.get('retweet_count', 0)}
- Likes: {metrics.get('like_count', 0)}
- Replies: {metrics.get('reply_count', 0)}
- Quotes: {metrics.get('quote_count', 0)}

## Suggested Actions

- [ ] Review mention
- [ ] Draft response
- [ ] Get approval if needed
- [ ] Post reply via Twitter MCP
- [ ] Archive after processing

## Notes

<!-- Add any additional context or notes here -->

---
*Created by Twitter Watcher - Gold Tier AI Employee*
"""
        
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created Twitter action file: {filepath}")
        
        # Save session
        self._save_session()
        
        return filepath


class TwitterPoster:
    """Post to Twitter/X with approval workflow"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        
        # Twitter credentials
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        # Session file
        self.session_file = self.vault_path / '.twitter_session' / 'poster_state.json'
        
        # Initialize client
        self.client = None
        self.me = None
        self._init_client()
    
    def _init_client(self):
        """Initialize Twitter client"""
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            logger.warning("Twitter credentials not configured")
            self.api_initialized = False
            return
        
        try:
            self.client = Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
                return_type=dict
            )
            
            self.me = self.client.get_me()
            self.api_initialized = True
            logger.info(f"Twitter Poster initialized as @{self.me['data']['username']}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter Poster: {e}")
            self.api_initialized = False
    
    def create_draft_tweet(
        self,
        text: str,
        thread: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
        scheduled_time: Optional[datetime] = None
    ) -> Path:
        """
        Create a draft tweet for approval
        
        Args:
            text: Tweet content (max 280 chars)
            thread: Optional list of tweets for thread
            reply_to: Optional tweet ID to reply to
            scheduled_time: Optional scheduled time
        
        Returns:
            Path to draft file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"TWITTER_DRAFT_{timestamp}.md"
        filepath = self.pending_approval / filename
        
        # Ensure folders exist
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        self.vault_path.joinpath('.twitter_session').mkdir(parents=True, exist_ok=True)
        
        # Build metadata
        metadata = {
            'type': 'social_media_post',
            'platform': 'twitter',
            'text': text,
            'thread': thread,
            'reply_to': reply_to,
            'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
            'created': datetime.now().isoformat(),
            'status': 'pending_approval'
        }
        
        # Save metadata
        self._save_draft_metadata(filename, metadata)
        
        # Create approval file
        is_thread = thread is not None and len(thread) > 1
        tweet_type = "Thread" if is_thread else ("Reply" if reply_to else "Tweet")
        scheduled_str = scheduled_time.strftime('%Y-%m-%d %H:%M') if scheduled_time else 'Immediate'
        
        thread_content = ""
        if thread:
            for i, tweet in enumerate(thread, 1):
                thread_content += f"\n**Tweet {i}:**\n{tweet}\n"
        
        content = f"""---
type: approval_request
action: twitter_post
post_type: {tweet_type.lower()}
created: {datetime.now().isoformat()}
scheduled: {scheduled_str}
status: pending
draft_file: {filename}
---

# 🐦 Twitter {tweet_type} - Approval Required

## Post Details

**Type:** {tweet_type}
**Scheduled:** {scheduled_str}
{f"**Replying to:** {reply_to}" if reply_to else ""}

## Content

{text}

{thread_content if thread_content else ""}

## To Approve

1. Review the content above
2. Move this file to `/Approved` folder to publish
3. Or move to `/Rejected` to cancel

## Metadata

- Draft file: `{filename}`
- Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- Status: Pending Approval

---
*Created by Twitter Poster - Gold Tier AI Employee*
"""
        
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created Twitter draft: {filepath}")
        
        return filepath
    
    def _save_draft_metadata(self, filename: str, metadata: Dict[str, Any]):
        """Save draft metadata"""
        metadata_file = self.vault_path / '.twitter_session' / f'{filename}.meta.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _load_draft_metadata(self, filename: str) -> Dict[str, Any]:
        """Load draft metadata"""
        metadata_file = self.vault_path / '.twitter_session' / f'{filename}.meta.json'
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def publish_approved_tweet(self, approval_file: Path) -> bool:
        """Publish an approved tweet"""
        if not self.api_initialized:
            logger.error("Twitter API not initialized")
            return False
        
        content = approval_file.read_text(encoding='utf-8')
        metadata = self._parse_frontmatter(content)
        draft_file = metadata.get('draft_file', '')
        
        if draft_file:
            post_metadata = self._load_draft_metadata(draft_file)
        else:
            post_metadata = metadata
        
        text = post_metadata.get('text', '')
        thread = post_metadata.get('thread')
        reply_to = post_metadata.get('reply_to')
        
        try:
            results = []
            
            if thread:
                # Post thread
                tweet_ids = []
                for i, tweet_text in enumerate(thread):
                    if i == 0:
                        # First tweet
                        if reply_to:
                            result = self.client.create_tweet(text=tweet_text, in_reply_to_tweet_id=reply_to)
                        else:
                            result = self.client.create_tweet(text=tweet_text)
                    else:
                        # Subsequent tweets
                        result = self.client.create_tweet(text=tweet_text, in_reply_to_tweet_id=tweet_ids[-1])
                    
                    tweet_ids.append(result['data']['id'])
                    results.append(('tweet', result['data']['id']))
            else:
                # Single tweet
                if reply_to:
                    result = self.client.create_tweet(text=text, in_reply_to_tweet_id=reply_to)
                else:
                    result = self.client.create_tweet(text=text)
                
                results.append(('tweet', result['data']['id']))
            
            # Log success
            self._log_post(results, post_metadata)
            
            # Move to Done
            done_file = self.done / approval_file.name
            done_file.write_text(content + "\n\n## ✅ Published Successfully\n", encoding='utf-8')
            
            # Clean up metadata
            if draft_file:
                meta_file = self.vault_path / '.twitter_session' / f'{draft_file}.meta.json'
                if meta_file.exists():
                    meta_file.unlink()
            
            logger.info("Tweet published successfully")
            return True

        except tweepy.TweepyException as e:
            logger.error(f"Twitter API error: {e}")
            self._log_error(approval_file.name, str(e))
            return False
        except Exception as e:
            logger.error(f"Error publishing tweet: {e}")
            self._log_error(approval_file.name, str(e))
            return False
    
    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter"""
        import re
        
        match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return {}
        
        metadata = {}
        lines = match.group(1).strip().split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                
                if value.startswith('[') and value.endswith(']'):
                    value = [v.strip() for v in value[1:-1].split(',')]
                
                metadata[key] = value
        
        return metadata
    
    def _log_post(self, results: List[tuple], metadata: Dict[str, Any]):
        """Log successful post"""
        log_file = self.logs / f"twitter_{datetime.now().strftime('%Y-%m-%d')}.json"
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'twitter_post',
            'results': results,
            'metadata': metadata,
            'status': 'success'
        }
        
        logs = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def _log_error(self, filename: str, error: str):
        """Log error"""
        error_file = self.logs / f"twitter_errors_{datetime.now().strftime('%Y-%m-%d')}.json"
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'file': filename,
            'error': error,
            'status': 'failed'
        }
        
        logs = []
        if error_file.exists():
            with open(error_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        with open(error_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def get_analytics(self, tweet_id: Optional[str] = None) -> Dict[str, Any]:
        """Get tweet analytics (requires elevated access)"""
        if not self.api_initialized:
            return {}
        
        try:
            if tweet_id:
                metrics = self.client.get_tweet(
                    id=tweet_id,
                    tweet_fields=['public_metrics']
                )
                return metrics.get('data', {}).get('public_metrics', {})
            else:
                # Get user's recent tweets analytics
                tweets = self.client.get_users_tweets(
                    id=self.me['data']['id'],
                    max_results=5,
                    tweet_fields=['public_metrics']
                )
                
                analytics = []
                for tweet in tweets.get('data', []):
                    analytics.append({
                        'tweet_id': tweet['id'],
                        'text': tweet['text'][:50] + '...',
                        'metrics': tweet.get('public_metrics', {})
                    })
                
                return {'recent_tweets': analytics}
                
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {}


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Twitter Watcher & Poster')
    parser.add_argument('vault_path', type=str, help='Path to Obsidian vault')
    parser.add_argument('--watch', action='store_true', help='Start watching for mentions')
    parser.add_argument('--tweet', type=str, help='Create draft tweet')
    parser.add_argument('--thread', type=str, nargs='+', help='Create draft thread')
    parser.add_argument('--publish', type=str, help='Publish approved tweet')
    parser.add_argument('--analytics', action='store_true', help='Get analytics')
    parser.add_argument('--setup', action='store_true', help='Show setup instructions')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    
    if args.setup:
        print("\n=== Twitter/X Integration Setup ===\n")
        print("1. Go to https://developer.twitter.com/")
        print("2. Create a project and app")
        print("3. Get your API credentials:")
        print("   - API Key")
        print("   - API Secret")
        print("   - Access Token")
        print("   - Access Token Secret")
        print("\nAdd to your .env file:")
        print("  TWITTER_API_KEY=your_api_key")
        print("  TWITTER_API_SECRET=your_api_secret")
        print("  TWITTER_ACCESS_TOKEN=your_access_token")
        print("  TWITTER_ACCESS_TOKEN_SECRET=your_token_secret")
        return
    
    if args.analytics:
        poster = TwitterPoster(str(vault_path))
        analytics = poster.get_analytics()
        print("\n=== Twitter Analytics ===\n")
        if 'recent_tweets' in analytics:
            for tweet in analytics['recent_tweets']:
                print(f"  {tweet['text']}")
                print(f"    Likes: {tweet['metrics'].get('like_count', 0)}")
                print(f"    Retweets: {tweet['metrics'].get('retweet_count', 0)}")
                print()
        return
    
    if args.publish:
        approval_file = Path(args.publish)
        if not approval_file.exists():
            print(f"Error: File not found: {approval_file}")
            return
        
        poster = TwitterPoster(str(vault_path))
        success = poster.publish_approved_tweet(approval_file)
        
        if success:
            print("✅ Tweet published successfully!")
        else:
            print("❌ Failed to publish tweet")
        return
    
    if args.tweet or args.thread:
        poster = TwitterPoster(str(vault_path))
        
        if args.thread:
            draft_file = poster.create_draft_tweet(
                text=args.thread[0],
                thread=args.thread
            )
        else:
            draft_file = poster.create_draft_tweet(text=args.tweet)
        
        print(f"✅ Draft created: {draft_file}")
        print("Move to /Approved to publish")
        return
    
    if args.watch or True:  # Default to watch mode
        watcher = TwitterWatcher(str(vault_path))
        
        if not watcher.api_initialized:
            print("❌ Twitter API not initialized. Run with --setup for instructions.")
            return
        
        logger.info("Starting Twitter Watcher...")
        
        try:
            while True:
                updates = watcher.check_for_updates()
                
                for update in updates:
                    watcher.create_action_file(update)
                
                time.sleep(watcher.check_interval)
        except KeyboardInterrupt:
            logger.info("Watcher stopped by user")


if __name__ == '__main__':
    main()
