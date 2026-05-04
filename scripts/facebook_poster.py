"""
Facebook & Instagram Poster for AI Employee - Gold Tier

Handles posting to Facebook Pages and Instagram Business accounts.
Supports:
- Text posts
- Photo posts
- Story posts
- Scheduled posts
- Draft mode with approval

All sensitive actions require human approval before posting.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page
from facebook_business.adobjects.photo import Photo
from facebook_business.exceptions import FacebookRequestError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FacebookInstagramPoster:
    """Post to Facebook and Instagram with approval workflow"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        
        # Initialize Facebook credentials
        self.app_id = os.getenv('FACEBOOK_APP_ID')
        self.app_secret = os.getenv('FACEBOOK_APP_SECRET')
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.page_id = os.getenv('FACEBOOK_PAGE_ID')
        self.instagram_account_id = os.getenv('INSTAGRAM_ACCOUNT_ID')
        
        # Session file
        self.session_file = self.vault_path / '.facebook_session' / 'poster_state.json'
        
        # Initialize API
        self._init_api()
    
    def _init_api(self):
        """Initialize Facebook Ads API"""
        if not all([self.app_id, self.app_secret, self.access_token]):
            logger.warning("Facebook credentials not configured")
            self.api_initialized = False
            return
        
        try:
            FacebookAdsApi.init(
                app_id=self.app_id,
                app_secret=self.app_secret,
                access_token=self.access_token
            )
            self.api_initialized = True
            logger.info("Facebook API initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Facebook API: {e}")
            self.api_initialized = False
    
    def create_draft_post(
        self,
        message: str,
        image_path: Optional[str] = None,
        post_type: str = 'facebook',
        scheduled_time: Optional[datetime] = None,
        platforms: List[str] = None
    ) -> Path:
        """
        Create a draft post for approval
        
        Args:
            message: Post content
            image_path: Optional path to image
            post_type: 'facebook', 'instagram', 'story', or 'crosspost'
            scheduled_time: Optional scheduled publish time
            platforms: List of platforms to post to
        """
        if platforms is None:
            platforms = ['facebook']
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"SOCIAL_DRAFT_{post_type.upper()}_{timestamp}.md"
        filepath = self.pending_approval / filename
        
        # Ensure folders exist
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        self.vault_path.joinpath('.facebook_session').mkdir(parents=True, exist_ok=True)
        
        # Build post metadata
        metadata = {
            'type': 'social_media_post',
            'platforms': platforms,
            'message': message,
            'image_path': image_path,
            'post_type': post_type,
            'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
            'created': datetime.now().isoformat(),
            'status': 'pending_approval'
        }
        
        # Save metadata to session
        self._save_draft_metadata(filename, metadata)
        
        # Create approval request file
        platforms_str = ', '.join(platforms)
        scheduled_str = scheduled_time.strftime('%Y-%m-%d %H:%M') if scheduled_time else 'Immediate'
        
        content = f"""---
type: approval_request
action: social_media_post
platforms: {platforms_str}
post_type: {post_type}
created: {datetime.now().isoformat()}
scheduled: {scheduled_str}
status: pending
draft_file: {filename}
---

# 📱 Social Media Post - Approval Required

## Post Details

**Platforms:** {platforms_str}
**Type:** {post_type}
**Scheduled:** {scheduled_str}

## Content

{message}

{f"**Image:** {image_path}" if image_path else ""}

## To Approve

1. Review the content above
2. Move this file to `/Approved` folder to publish
3. Or move to `/Rejected` to cancel

## To Modify

1. Edit this file with changes
2. Move to `/Approved` when ready

## Metadata

- Draft file: `{filename}`
- Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- Status: Pending Approval

---
*Created by Facebook/Instagram Poster - Gold Tier AI Employee*
"""
        
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created draft post for approval: {filepath}")
        
        return filepath
    
    def _save_draft_metadata(self, filename: str, metadata: Dict[str, Any]):
        """Save draft metadata for later retrieval"""
        metadata_file = self.vault_path / '.facebook_session' / f'{filename}.meta.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _load_draft_metadata(self, filename: str) -> Dict[str, Any]:
        """Load draft metadata"""
        metadata_file = self.vault_path / '.facebook_session' / f'{filename}.meta.json'
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def publish_approved_post(self, approval_file: Path) -> bool:
        """
        Publish a post that has been approved

        Args:
            approval_file: Path to the approved approval file

        Returns:
            True if successful, False otherwise
        """
        if not self.api_initialized:
            logger.error("Facebook API not initialized")
            return False

        # Load metadata
        content = approval_file.read_text(encoding='utf-8')

        # Parse YAML frontmatter (simple parsing)
        metadata = self._parse_frontmatter(content)
        draft_file = metadata.get('draft_file', '')

        # First try to get message from draft metadata
        post_metadata = {}
        if draft_file:
            post_metadata = self._load_draft_metadata(draft_file)

        # If no message found, parse from approval file content
        message = post_metadata.get('message', '')

        if not message:
            # Extract message from ## Content section
            import re
            content_match = re.search(r'## Content\s*\n+(.*?)\n+##', content, re.DOTALL)
            if content_match:
                message = content_match.group(1).strip()

        # Fallback: try to get from frontmatter
        if not message:
            message = metadata.get('message', '')

        image_path = post_metadata.get('image_path')
        platforms = metadata.get('platforms', ['facebook'])
        post_type = metadata.get('post_type', 'feed')

        logger.info(f"Publishing post: {message[:50]}...")

        results = []

        try:
            page = Page(self.page_id)

            # Post to Facebook
            if 'facebook' in platforms:
                result = self._post_to_facebook(page, message, image_path, post_type)
                results.append(('facebook', result))

            # Post to Instagram
            if 'instagram' in platforms and post_type in ['instagram', 'crosspost']:
                result = self._post_to_instagram(message, image_path)
                results.append(('instagram', result))

            # Log success
            self._log_post(results, post_metadata)

            # Move approval file to Done
            done_file = self.done / approval_file.name
            done_file.write_text(content + "\n\n## ✅ Published Successfully\n", encoding='utf-8')

            # Clean up metadata
            if draft_file:
                meta_file = self.vault_path / '.facebook_session' / f'{draft_file}.meta.json'
                if meta_file.exists():
                    meta_file.unlink()

            logger.info(f"Post published successfully to {platforms}")
            return True
            
        except FacebookRequestError as e:
            logger.error(f"Facebook API error: {e}")
            self._log_error(approval_file.name, str(e))
            return False
        except Exception as e:
            logger.error(f"Error publishing post: {e}")
            self._log_error(approval_file.name, str(e))
            return False
    
    def _post_to_facebook(
        self,
        page: Page,
        message: str,
        image_path: Optional[str] = None,
        post_type: str = 'feed'
    ) -> Dict[str, Any]:
        """Post to Facebook Page using Graph API directly"""
        
        import requests
        
        # Build the API URL
        access_token = self.access_token
        page_id = self.page_id
        url = f'https://graph.facebook.com/v25.0/{page_id}/feed'
        
        params = {
            'message': message,
            'access_token': access_token,
        }
        
        # Add image if provided
        if image_path:
            # For image, we need to upload it
            photo_url = f'https://graph.facebook.com/v25.0/{page_id}/photos'
            photo_params = {
                'source': open(image_path, 'rb') if os.path.exists(image_path) else image_path,
                'caption': message,
                'access_token': access_token,
            }
            response = requests.post(photo_url, data=photo_params)
        else:
            # Text post
            response = requests.post(url, data=params)
        
        result = response.json()
        
        if response.status_code == 200 and 'id' in result:
            return {
                'success': True,
                'post_id': result['id'],
                'type': 'text'
            }
        else:
            error_msg = result.get('error', {}).get('message', 'Unknown error')
            
            # Check if user is not page admin
            if 'sufficient administrative permission' in error_msg:
                logger.error("❌ You are not an admin of this Page!")
                logger.error("   Solution:")
                logger.error("   1. Create your own page: https://www.facebook.com/pages/create/")
                logger.error("   2. Or get admin access from page owner")
                logger.error("   3. Generate new Page Access Token")
                logger.error("   4. Update .env with new Page ID and Token")
            
            logger.error(f"Facebook API error: {result}")
            return {
                'success': False,
                'error': error_msg
            }
    
    def _post_to_instagram(
        self,
        message: str,
        image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Post to Instagram Business account"""
        
        if not self.instagram_account_id:
            logger.warning("Instagram account ID not configured")
            return {'success': False, 'error': 'Instagram not configured'}
        
        # Instagram requires photo container creation first
        if image_path:
            # Create media container
            container = Page(self.page_id).create_instagram_container({
                'image_source': image_path,
                'caption': message,
            })
            
            # Publish container
            media_id = container.get_id()
            Page(self.page_id).create_publish_container({
                'creation_id': media_id,
            })
            
            return {
                'success': True,
                'media_id': media_id,
                'type': 'photo'
            }
        else:
            logger.warning("Instagram requires an image")
            return {'success': False, 'error': 'Image required for Instagram'}
    
    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Simple YAML frontmatter parser"""
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
                
                # Parse lists
                if value.startswith('[') and value.endswith(']'):
                    value = [v.strip() for v in value[1:-1].split(',')]
                
                metadata[key] = value
        
        return metadata
    
    def _log_post(self, results: List[tuple], metadata: Dict[str, Any]):
        """Log successful post"""
        log_file = self.logs / f"social_{datetime.now().strftime('%Y-%m-%d')}.json"
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'social_media_post',
            'platforms': results,
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
        error_file = self.logs / f"social_errors_{datetime.now().strftime('%Y-%m-%d')}.json"
        
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
    
    def get_insights(self) -> Dict[str, Any]:
        """Get Facebook Page insights"""
        if not self.api_initialized:
            return {}

        try:
            page = Page(self.page_id)

            # Fetch insights one by one (more reliable)
            result = {}
            
            # Get page impressions
            try:
                impressions_data = page.get_insights(params={
                    'metric': 'page_impressions'
                })
                if impressions_data:
                    result['impressions'] = impressions_data[0].get('values', [{}])[0].get('value', 0)
            except:
                result['impressions'] = 0
            
            # Get engaged users
            try:
                engaged_data = page.get_insights(params={
                    'metric': 'page_engaged_users'
                })
                if engaged_data:
                    result['engaged_users'] = engaged_data[0].get('values', [{}])[0].get('value', 0)
            except:
                result['engaged_users'] = 0
            
            # Get post engagements
            try:
                posts_data = page.get_insights(params={
                    'metric': 'page_post_engagements'
                })
                if posts_data:
                    result['post_engagements'] = posts_data[0].get('values', [{}])[0].get('value', 0)
            except:
                result['post_engagements'] = 0
            
            return result

        except Exception as e:
            logger.error(f"Error getting insights: {e}")
            return {}


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Facebook & Instagram Poster')
    parser.add_argument('vault_path', type=str, help='Path to Obsidian vault')
    parser.add_argument('--post', type=str, help='Create draft post with message')
    parser.add_argument('--image', type=str, help='Path to image for post')
    parser.add_argument('--platforms', type=str, default='facebook', help='Platforms: facebook,instagram')
    parser.add_argument('--type', type=str, default='feed', help='Post type: feed,story,crosspost')
    parser.add_argument('--schedule', type=str, help='Schedule time (YYYY-MM-DD HH:MM)')
    parser.add_argument('--publish', type=str, help='Publish approved file')
    parser.add_argument('--insights', action='store_true', help='Get page insights')
    parser.add_argument('--setup', action='store_true', help='Show setup instructions')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    poster = FacebookInstagramPoster(str(vault_path))
    
    if args.setup:
        print("\n=== Facebook/Instagram Poster Setup ===\n")
        print("Add to your .env file:")
        print("  FACEBOOK_APP_ID=your_app_id")
        print("  FACEBOOK_APP_SECRET=your_app_secret")
        print("  FACEBOOK_ACCESS_TOKEN=your_access_token")
        print("  FACEBOOK_PAGE_ID=your_page_id")
        print("  INSTAGRAM_ACCOUNT_ID=your_instagram_id (optional)")
        return
    
    if args.insights:
        insights = poster.get_insights()
        print("\n=== Facebook Page Insights ===")
        print(f"Impressions: {insights.get('impressions', 'N/A')}")
        print(f"Engaged Users: {insights.get('engaged_users', 'N/A')}")
        print(f"Post Engagements: {insights.get('post_engagements', 'N/A')}")
        return
    
    if args.publish:
        approval_file = Path(args.publish)
        if not approval_file.exists():
            print(f"Error: File not found: {approval_file}")
            return
        
        success = poster.publish_approved_post(approval_file)
        if success:
            print("✅ Post published successfully!")
        else:
            print("❌ Failed to publish post")
        return
    
    if args.post:
        platforms = [p.strip() for p in args.platforms.split(',')]
        
        scheduled_time = None
        if args.schedule:
            scheduled_time = datetime.strptime(args.schedule, '%Y-%m-%d %H:%M')
        
        draft_file = poster.create_draft_post(
            message=args.post,
            image_path=args.image,
            post_type=args.type,
            scheduled_time=scheduled_time,
            platforms=platforms
        )
        
        print(f"✅ Draft post created: {draft_file}")
        print("Move this file to /Approved to publish")


if __name__ == '__main__':
    main()
