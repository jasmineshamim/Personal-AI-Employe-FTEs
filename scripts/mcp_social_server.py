"""
Social Media MCP Server for AI Employee - Gold Tier

Unified MCP server for Facebook, Instagram, and Twitter/X operations.
Provides standardized interface for Claude Code to interact with social platforms.

Platforms supported:
- Facebook Pages
- Instagram Business
- Twitter/X
"""

import os
import sys
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Import platform-specific modules
try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.page import Page
    FACEBOOK_AVAILABLE = True
except ImportError:
    FACEBOOK_AVAILABLE = False

try:
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SocialMediaMCP:
    """Unified Social Media MCP Server"""
    
    def __init__(self):
        # Facebook credentials
        self.fb_app_id = os.getenv('FACEBOOK_APP_ID')
        self.fb_app_secret = os.getenv('FACEBOOK_APP_SECRET')
        self.fb_access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.fb_page_id = os.getenv('FACEBOOK_PAGE_ID')
        self.instagram_account_id = os.getenv('INSTAGRAM_ACCOUNT_ID')
        
        # Twitter credentials
        self.twitter_api_key = os.getenv('TWITTER_API_KEY')
        self.twitter_api_secret = os.getenv('TWITTER_API_SECRET')
        self.twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.twitter_access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        # Initialize clients
        self.fb_client = None
        self.twitter_client = None
        
        self._init_facebook()
        self._init_twitter()
    
    def _init_facebook(self):
        """Initialize Facebook API"""
        if not FACEBOOK_AVAILABLE:
            logger.warning("facebook-business not installed")
            return
        
        if not all([self.fb_app_id, self.fb_app_secret, self.fb_access_token]):
            logger.warning("Facebook credentials not configured")
            return
        
        try:
            FacebookAdsApi.init(
                app_id=self.fb_app_id,
                app_secret=self.fb_app_secret,
                access_token=self.fb_access_token
            )
            self.fb_client = Page(self.fb_page_id)
            logger.info(f"Facebook initialized for page: {self.fb_page_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Facebook: {e}")
    
    def _init_twitter(self):
        """Initialize Twitter API"""
        if not TWITTER_AVAILABLE:
            logger.warning("tweepy not installed")
            return
        
        if not all([self.twitter_api_key, self.twitter_api_secret, 
                   self.twitter_access_token, self.twitter_access_token_secret]):
            logger.warning("Twitter credentials not configured")
            return
        
        try:
            self.twitter_client = tweepy.Client(
                consumer_key=self.twitter_api_key,
                consumer_secret=self.twitter_api_secret,
                access_token=self.twitter_access_token,
                access_token_secret=self.twitter_access_token_secret,
                return_type=dict
            )
            self.me = self.twitter_client.get_me()
            logger.info(f"Twitter initialized as @{self.me['data']['username']}")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter: {e}")
    
    # Facebook Methods
    
    def facebook_create_post(self, message: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        """Create Facebook post"""
        if not self.fb_client:
            return {'error': 'Facebook not initialized'}
        
        try:
            if image_path:
                # Photo post
                from facebook_business.adobjects.photo import Photo
                photo = Photo(parent_id=self.fb_client.get_id())
                photo[Photo.Field.source] = image_path
                photo[Photo.Field.message] = message
                photo.remote_create()
                return {'success': True, 'post_id': photo.get_id(), 'type': 'photo'}
            else:
                # Text post
                post = self.fb_client.get_feed().create_post({
                    Page.Field.MESSAGE: message,
                })
                return {'success': True, 'post_id': post.get_id(), 'type': 'text'}
        except Exception as e:
            return {'error': str(e)}
    
    def facebook_get_insights(self) -> Dict[str, Any]:
        """Get Facebook page insights"""
        if not self.fb_client:
            return {}
        
        try:
            insights = self.fb_client.get_insights(
                metric=['page_impressions', 'page_engaged_users', 'page_post_engagements']
            )
            return {
                'impressions': insights[0]['values'][0]['value'] if insights else 0,
                'engaged_users': insights[1]['values'][0]['value'] if len(insights) > 1 else 0,
                'post_engagements': insights[2]['values'][0]['value'] if len(insights) > 2 else 0,
            }
        except Exception as e:
            return {'error': str(e)}
    
    # Twitter Methods
    
    def twitter_create_tweet(self, text: str, reply_to: Optional[str] = None) -> Dict[str, Any]:
        """Create tweet"""
        if not self.twitter_client:
            return {'error': 'Twitter not initialized'}
        
        try:
            if reply_to:
                result = self.twitter_client.create_tweet(text=text, in_reply_to_tweet_id=reply_to)
            else:
                result = self.twitter_client.create_tweet(text=text)
            return {'success': True, 'tweet_id': result['data']['id']}
        except Exception as e:
            return {'error': str(e)}
    
    def twitter_get_mentions(self, limit: int = 10) -> Dict[str, Any]:
        """Get recent mentions"""
        if not self.twitter_client:
            return {'error': 'Twitter not initialized'}
        
        try:
            me = self.twitter_client.get_me()
            user_id = me['data']['id']
            
            mentions = self.twitter_client.get_users_mentions(
                id=user_id,
                max_results=limit,
                tweet_fields=['created_at', 'text', 'author_id', 'public_metrics'],
                expansions=['author_id'],
                user_fields=['username', 'name']
            )
            
            return {'mentions': mentions.get('data', [])}
        except Exception as e:
            return {'error': str(e)}
    
    # MCP Tool Definitions
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools"""
        return [
            {
                'name': 'facebook_create_post',
                'description': 'Create a Facebook page post',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string', 'description': 'Post content'},
                        'image_path': {'type': 'string', 'description': 'Path to image'}
                    },
                    'required': ['message']
                }
            },
            {
                'name': 'facebook_get_insights',
                'description': 'Get Facebook page insights',
                'inputSchema': {
                    'type': 'object',
                    'properties': {}
                }
            },
            {
                'name': 'twitter_create_tweet',
                'description': 'Create a tweet',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'text': {'type': 'string', 'description': 'Tweet content'},
                        'reply_to': {'type': 'string', 'description': 'Tweet ID to reply to'}
                    },
                    'required': ['text']
                }
            },
            {
                'name': 'twitter_get_mentions',
                'description': 'Get recent Twitter mentions',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'limit': {'type': 'integer', 'description': 'Number of mentions'}
                    }
                }
            }
        ]
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool"""
        try:
            if tool_name == 'facebook_create_post':
                return self.facebook_create_post(**arguments)
            elif tool_name == 'facebook_get_insights':
                return self.facebook_get_insights()
            elif tool_name == 'twitter_create_tweet':
                return self.twitter_create_tweet(**arguments)
            elif tool_name == 'twitter_get_mentions':
                return self.twitter_get_mentions(**arguments)
            else:
                return {'error': f'Unknown tool: {tool_name}'}
        except Exception as e:
            return {'error': str(e)}


def main():
    """Main entry point for MCP server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Social Media MCP Server')
    parser.add_argument('--list-tools', action='store_true', help='List available tools')
    parser.add_argument('--call-tool', type=str, help='Call tool (JSON: name|args)')
    parser.add_argument('--test', action='store_true', help='Test connections')
    parser.add_argument('--setup', action='store_true', help='Show setup instructions')
    
    args = parser.parse_args()
    
    mcp = SocialMediaMCP()
    
    if args.setup:
        print("\n=== Social Media MCP Server Setup ===\n")
        print("Add to your .env file:\n")
        print("# Facebook")
        print("FACEBOOK_APP_ID=your_app_id")
        print("FACEBOOK_APP_SECRET=your_app_secret")
        print("FACEBOOK_ACCESS_TOKEN=your_access_token")
        print("FACEBOOK_PAGE_ID=your_page_id")
        print("INSTAGRAM_ACCOUNT_ID=your_instagram_id (optional)")
        print("\n# Twitter")
        print("TWITTER_API_KEY=your_api_key")
        print("TWITTER_API_SECRET=your_api_secret")
        print("TWITTER_ACCESS_TOKEN=your_access_token")
        print("TWITTER_ACCESS_TOKEN_SECRET=your_token_secret")
        return
    
    if args.test:
        print("\n=== Social Media MCP Test ===\n")
        if mcp.fb_client:
            print("✅ Facebook connected")
        else:
            print("❌ Facebook not connected")
        
        if mcp.twitter_client:
            print("✅ Twitter connected")
        else:
            print("❌ Twitter not connected")
        return
    
    if args.list_tools:
        tools = mcp.list_tools()
        print("\n=== Available Social Media Tools ===\n")
        for tool in tools:
            print(f"**{tool['name']}**")
            print(f"   {tool['description']}")
            print()
        return
    
    if args.call_tool:
        parts = args.call_tool.split('|', 1)
        tool_name = parts[0]
        arguments = json.loads(parts[1]) if len(parts) > 1 else {}
        
        result = mcp.call_tool(tool_name, arguments)
        print(json.dumps(result, indent=2))
        return
    
    # Default: show help
    parser.print_help()


if __name__ == '__main__':
    main()
