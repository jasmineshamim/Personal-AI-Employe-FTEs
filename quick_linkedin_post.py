#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Quick Auto Post - Direct posting using .env credentials.
No OAuth setup - just works with your existing token!

Usage:
    python quick_linkedin_post.py "Your message here"
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime


def load_env():
    """Load credentials from .env file."""
    env_file = Path.cwd() / '.env'
    
    if not env_file.exists():
        print(f"[ERROR] .env file not found")
        return None
    
    creds = {}
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                creds[key.strip()] = value.strip()
    
    return creds


def post_to_linkedin(message):
    """Post to LinkedIn using API."""
    print("=" * 70)
    print("LINKEDIN AUTO POST - AI Employee")
    print("=" * 70)
    print(f"Message: {message}")
    print()
    
    # Load credentials
    creds = load_env()
    
    if not creds:
        print("[ERROR] Could not load .env file")
        return False
    
    # Get access token
    access_token = creds.get('LINKEDIN_ACCESS_TOKEN')
    company_urn = creds.get('COMPANY_URN')
    
    if not access_token:
        print("[ERROR] No LINKEDIN_ACCESS_TOKEN in .env")
        return False
    
    print("[OK] Access token loaded")
    if company_urn:
        print(f"[OK] Company Page: {company_urn}")
    print()
    
    # Try different API endpoints
    endpoints_to_try = [
        # Method 1: UGC Posts API
        {
            'url': 'https://api.linkedin.com/v2/ugcPosts',
            'payload': {
                "author": f"urn:li:person:{company_urn.replace('urn:li:organization:', '') if company_urn else 'me'}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": message
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
        },
        # Method 2: Shares API (for company)
        {
            'url': 'https://api.linkedin.com/v2/shares',
            'payload': {
                "owner": company_urn if company_urn else "urn:li:person:me",
                "text": {
                    "text": message
                },
                "distribution": {
                    "feedDistribution": "MAIN_FEED",
                    "targetEntities": [],
                    "thirdPartyDistributionChannels": []
                }
            } if company_urn else {}
        },
        # Method 3: Legacy Posts API
        {
            'url': 'https://api.linkedin.com/v2/posts',
            'payload': {
                "author": company_urn if company_urn else "urn:li:person:me",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": message
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
        }
    ]
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0',
        'Content-Type': 'application/json',
        'LinkedIn-Version': '202402'
    }
    
    # Try each endpoint
    for i, endpoint in enumerate(endpoints_to_try, 1):
        print(f"Trying Method {i}: {endpoint['url']}")
        
        if not endpoint['payload']:
            print("  [SKIP] Empty payload for this method")
            continue
        
        try:
            response = requests.post(
                endpoint['url'],
                headers=headers,
                json=endpoint['payload'],
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                post_id = result.get('id', result.get('activity', 'unknown'))
                
                print()
                print("[SUCCESS] POST PUBLISHED!")
                print(f"Post ID: {post_id}")
                
                # Log
                log_post(message, post_id)
                
                print("=" * 70)
                return True
                
            else:
                error = response.json() if response.text else {}
                print(f"  [FAILED] Status {response.status_code}: {error.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"  [ERROR] {e}")
    
    print()
    print("=" * 70)
    print("[FAILED] All methods failed")
    print()
    print("Your token doesn't have API posting permission.")
    print("You need to:")
    print("  1. Create a new LinkedIn app at: https://www.linkedin.com/developers/")
    print("  2. Enable 'w_member_social' permission")
    print("  3. Get new access token")
    print("=" * 70)
    
    return False


def log_post(content, post_id):
    """Log post to file."""
    logs_dir = Path.cwd() / 'AI_Employee_Vault' / 'Logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = logs_dir / 'linkedin_auto_posts.jsonl'
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'content': content,
        'post_id': post_id,
        'status': 'success'
    }
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + '\n')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python quick_linkedin_post.py \"Your message\"")
        print()
        print("Example:")
        print('  python quick_linkedin_post.py "Hello from AI Employee!"')
        sys.exit(1)
    
    message = sys.argv[1]
    
    if post_to_linkedin(message):
        print("\n[OK] Done! Check LinkedIn.")
        sys.exit(0)
    else:
        print("\n[FAILED] Could not post.")
        sys.exit(1)
