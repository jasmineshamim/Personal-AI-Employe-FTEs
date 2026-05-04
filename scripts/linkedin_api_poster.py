#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn API Auto Poster - Official LinkedIn API integration.

Uses LinkedIn's official API for reliable automated posting.
No browser automation - uses REST API directly.

Setup:
    1. Go to https://www.linkedin.com/developers/
    2. Create an app
    3. Get Client ID and Client Secret
    4. Enable 'w_member_social' permission
    5. Copy credentials to linkedin_api_credentials.json

Usage:
    # First-time authentication
    python scripts\\linkedin_api_poster.py --auth

    # Auto post
    python scripts\\linkedin_api_poster.py --autopost "Your post content here"

    # Post with image
    python scripts\\linkedin_api_poster.py --autopost "Content" --image path\\to\\image.jpg
"""

import sys
import json
import argparse
import webbrowser
import http.server
import socketserver
from pathlib import Path
from datetime import datetime
from typing import Optional
from urllib.parse import parse_qs, urlparse

# LinkedIn API imports
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class LinkedInAPIPoster:
    """Post to LinkedIn using official API."""
    
    API_BASE = 'https://api.linkedin.com/v2'
    AUTH_BASE = 'https://www.linkedin.com/oauth/v2'
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logs = self.vault_path / 'Logs'
        self.logs.mkdir(parents=True, exist_ok=True)
        
        # Credentials file
        self.creds_file = self.vault_path.parent / 'linkedin_api_credentials.json'
        self.token_file = self.vault_path / '.linkedin_api_token.json'
        
        self.client_id = None
        self.client_secret = None
        self.access_token = None
        self.person_urn = None
        self.redirect_uri = 'http://localhost:8080'  # ✅ FIX: Default redirect_uri
    
    def load_credentials(self) -> bool:
        """Load API credentials from .env file or credentials.json."""
        # Try loading from .env file first
        env_file = Path(__file__).parent.parent / '.env'
        
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            if key == 'LINKEDIN_CLIENT_ID':
                                self.client_id = value
                            elif key == 'LINKEDIN_CLIENT_SECRET':
                                self.client_secret = value
                            elif key == 'LINKEDIN_ACCESS_TOKEN':
                                self.access_token = value
                            elif key == 'LINKEDIN_REDIRECT_URI':  # ✅ FIX: .env se bhi le sakta hai
                                self.redirect_uri = value
                
                if self.client_id and self.client_secret:
                    print("[OK] Credentials loaded from .env")
                    return True
                elif self.access_token:
                    print("[OK] Access token loaded from .env")
                    return True
                    
            except Exception as e:
                print(f"Error reading .env file: {e}")
        
        # Fallback to credentials.json
        if not self.creds_file.exists():
            print(f"Error: Credentials file not found: {self.creds_file}")
            print("\nSetup instructions:")
            print("1. Go to https://www.linkedin.com/developers/")
            print("2. Create an app")
            print("3. Get Client ID and Client Secret")
            print("4. Enable 'w_member_social' permission")
            print("5. Create file linkedin_api_credentials.json:")
            print('   {"client_id": "your_id", "client_secret": "your_secret", "redirect_uri": "http://localhost:8080"}')
            return False
        
        try:
            with open(self.creds_file, 'r', encoding='utf-8') as f:
                creds = json.load(f)
            
            self.client_id = creds.get('client_id')
            self.client_secret = creds.get('client_secret')
            self.redirect_uri = creds.get('redirect_uri', 'http://localhost:8080')
            
            if not all([self.client_id, self.client_secret]):
                print("Error: Invalid credentials file")
                return False
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in credentials file: {e}")
            print("The file is empty or has invalid format")
            print("Delete the file and use .env instead, or add valid credentials")
            return False
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return False
    
    def load_token(self) -> bool:
        """Load existing access token."""
        if not self.token_file.exists():
            return False
        
        with open(self.token_file, 'r') as f:
            data = json.load(f)
        
        self.access_token = data.get('access_token')
        self.person_urn = data.get('person_urn')
        
        # Check if token is expired (tokens last 60 days)
        expires_at = data.get('expires_at', 0)
        if datetime.now().timestamp() > expires_at:
            print("Token expired, need to re-authenticate")
            return False
        
        return True
    
    def save_token(self, access_token: str, person_urn: str, expires_in: int):
        """Save access token to file."""
        data = {
            'access_token': access_token,
            'person_urn': person_urn,
            'expires_at': datetime.now().timestamp() + expires_in - 300  # 5 min buffer
        }
        
        with open(self.token_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Token saved (expires in {expires_in // 86400} days)")
    
    def authenticate(self) -> bool:
        """Perform OAuth 2.0 authentication."""
        if not self.load_credentials():
            return False
        
        print("=" * 60)
        print("LINKEDIN API AUTHENTICATION")
        print("=" * 60)
        print()
        print("Step 1: Opening browser for authorization...")
        print()
        
        # Build authorization URL
        auth_url = (
            f"{self.AUTH_BASE}/authorization?"
            f"response_type=code&"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"scope=w_member_social"
        )
        
        print(f"Opening: {auth_url[:80]}...")
        webbrowser.open(auth_url)
        
        print()
        print("Step 2: Please authorize the application in your browser.")
        print("After authorization, you'll be redirected to localhost.")
        print()
        print("Waiting for redirect with authorization code...")
        print("(Press Ctrl+C to cancel)")
        print()
        
        # Start local server to catch redirect
        auth_code = self._catch_auth_code()
        
        if not auth_code:
            print("Failed to get authorization code")
            return False
        
        print(f"Got authorization code: {auth_code[:20]}...")
        print()
        print("Step 3: Exchanging code for access token...")
        
        # Exchange code for token
        token_data = self._exchange_code_for_token(auth_code)
        
        if not token_data:
            print("Failed to get access token")
            return False
        
        self.access_token = token_data['access_token']
        
        # Get person URN
        self.person_urn = self._get_person_urn()
        
        if not self.person_urn:
            print("Failed to get person URN")
            return False
        
        # Save token
        self.save_token(
            token_data['access_token'],
            self.person_urn,
            token_data.get('expires_in', 5184000)
        )
        
        print()
        print("=" * 60)
        print("AUTHENTICATION SUCCESSFUL")
        print(f"Person URN: {self.person_urn}")
        print("=" * 60)
        
        return True
    
    def _catch_auth_code(self, port: int = 8080, timeout: int = 120) -> Optional[str]:
        """Catch authorization code from local server."""
        auth_code = None
        
        class AuthHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                nonlocal auth_code
                if self.path.startswith('/?code='):
                    auth_code = parse_qs(self.path[2:])['code'][0]
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'''
                        <html>
                        <body>
                            <h1>LinkedIn Authorization Successful!</h1>
                            <p>You can close this window and return to the terminal.</p>
                        </body>
                        </html>
                    ''')
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                pass  # Suppress logging
        
        try:
            with socketserver.TCPServer(("", port), AuthHandler) as httpd:
                httpd.settimeout(timeout)
                try:
                    httpd.handle_request()
                except socketserver.TimeoutError:
                    pass
        except OSError as e:
            print(f"Could not start local server: {e}")
            print(f"Make sure port {port} is not in use")
            return None
        
        return auth_code
    
    def _exchange_code_for_token(self, code: str) -> Optional[dict]:
        """Exchange authorization code for access token."""
        url = f"{self.AUTH_BASE}/accessToken"
        
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Token exchange failed: {e}")
            return None
    
    def _get_person_urn(self) -> Optional[str]:
        """Get the authenticated user's person URN."""
        url = f"{self.API_BASE}/me"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get('id')
        except requests.RequestException as e:
            print(f"Failed to get person URN: {e}")
            return None
    
    def create_post(self, content: str, image_path: Optional[str] = None) -> bool:
        """
        Create a post on LinkedIn using API.
        
        Args:
            content: Post text content
            image_path: Optional path to image
            
        Returns:
            True if successful
        """
        if not self.access_token:
            if not self.load_token():
                print("Not authenticated. Run: python linkedin_api_poster.py --auth")
                return False
        
        print(f"Creating LinkedIn post via API...")
        print(f"Content: {content[:100]}...")
        
        url = f"{self.API_BASE}/posts"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json',
            'LinkedIn-Version': '202402'
        }
        
        # Build post payload
        if image_path:
            payload = self._build_image_post_payload(content, image_path)
        else:
            payload = {
                "author": f"urn:li:person:{self.person_urn}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            post_id = result.get('id', 'unknown')
            
            print(f"✓ Post created successfully!")
            print(f"Post ID: {post_id}")
            print(f"URL: https://www.linkedin.com/feed/update/{post_id.replace('urn:li:share:', '')}")
            
            self._log_post(content, image_path, 'posted', post_id)
            
            return True
            
        except requests.RequestException as e:
            print(f"✗ Post failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return False
    
    def _build_image_post_payload(self, content: str, image_path: str) -> dict:
        """Build payload for post with image."""
        print("Note: Image upload requires additional API setup.")
        print("Posting text-only version for now...")
        
        return {
            "author": f"urn:li:person:{self.person_urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
    
    def _log_post(self, content: str, image_path: Optional[str], status: str, post_id: str):
        """Log post to JSONL file."""
        log_file = self.logs / 'linkedin_api_posts.jsonl'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'content': content,
            'image': image_path,
            'status': status,
            'post_id': post_id
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')


def main():
    if not REQUESTS_AVAILABLE:
        print("Error: requests library not installed")
        print("Install with: pip install requests")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description='LinkedIn API Auto Poster - Official API integration'
    )
    parser.add_argument(
        'vault_path',
        nargs='?',
        default='AI_Employee_Vault',
        help='Path to the Obsidian vault root'
    )
    parser.add_argument(
        '--auth', '-a',
        action='store_true',
        help='Authenticate with LinkedIn API'
    )
    parser.add_argument(
        '--autopost',
        type=str,
        help='Auto post content using API'
    )
    parser.add_argument(
        '--image', '-i',
        type=str,
        help='Path to image to attach'
    )
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='Show authentication status'
    )
    
    args = parser.parse_args()
    
    vault = Path(args.vault_path)
    if not vault.exists():
        print(f"Error: Vault path does not exist: {vault}")
        sys.exit(1)
    
    poster = LinkedInAPIPoster(str(vault))
    
    if args.auth:
        if poster.authenticate():
            print("\n✓ Authentication complete!")
            print("\nYou can now post with:")
            print(f"  python scripts\\linkedin_api_poster.py {args.vault_path} --autopost \"Your content\"")
        else:
            print("\n✗ Authentication failed.")
            sys.exit(1)
    
    elif args.autopost:
        if poster.load_token() or poster.authenticate():
            if poster.create_post(args.autopost, args.image):
                print("\n✓ Auto post SUCCESSFUL!")
            else:
                print("\n✗ Auto post FAILED.")
                sys.exit(1)
        else:
            print("Not authenticated. Run: python linkedin_api_poster.py --auth")
            sys.exit(1)
    
    elif args.status:
        if poster.load_token():
            print("✓ Authenticated")
            print(f"Person URN: {poster.person_urn}")
        else:
            print("✗ Not authenticated")
            print("Run: python linkedin_api_poster.py --auth")
    
    else:
        parser.print_help()
        print("\n" + "=" * 60)
        print("Quick Start:")
        print("  1. Setup credentials (see setup instructions above)")
        print("  2. Authenticate: python linkedin_api_poster.py --auth")
        print("  3. Auto post: python linkedin_api_poster.py --autopost \"Content\"")
        print("=" * 60)


if __name__ == '__main__':
    main()