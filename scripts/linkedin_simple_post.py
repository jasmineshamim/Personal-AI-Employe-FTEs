#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Simple Poster - Posts to personal profile.

Usage:
    python scripts\\linkedin_simple_post.py "Your post message here"
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime


def load_env_credentials():
    env_file = Path.cwd() / '.env'
    if not env_file.exists():
        print(f"Error: .env file not found")
        return None
    creds = {}
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                creds[key.strip()] = value.strip()
    return creds


def get_person_urn(access_token):
    """Get person URN using userinfo endpoint (no special permissions needed)."""
    
    # Try userinfo endpoint first
    try:
        response = requests.get(
            "https://api.linkedin.com/v2/userinfo",
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            sub = data.get('sub')  # This is the person ID
            if sub:
                print(f"[OK] Person ID found: {sub[:10]}...")
                return f"urn:li:person:{sub}"
    except Exception:
        pass

    # Try introspect endpoint
    try:
        response = requests.get(
            "https://api.linkedin.com/v2/me",
            headers={
                'Authorization': f'Bearer {access_token}',
                'X-Restli-Protocol-Version': '2.0.0',
                'LinkedIn-Version': '202304'
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            person_id = data.get('id')
            if person_id:
                print(f"[OK] Person ID found!")
                return f"urn:li:person:{person_id}"
    except Exception:
        pass

    return None


def post_to_linkedin(text):
    print("=" * 70)
    print("LINKEDIN SIMPLE POST - Personal Profile")
    print("=" * 70)
    print(f"Content: {text[:100]}...")
    print()

    creds = load_env_credentials()
    if not creds:
        return False

    access_token = creds.get('LINKEDIN_ACCESS_TOKEN')
    if not access_token:
        print("[FAILED] No LINKEDIN_ACCESS_TOKEN in .env")
        return False

    print("[OK] Token loaded from .env")

    # Get person URN
    person_urn = get_person_urn(access_token)
    
    if not person_urn:
        # Try using saved URN from token file
        token_file = Path.cwd() / 'AI_Employee_Vault' / '.linkedin_api_token.json'
        if token_file.exists():
            with open(token_file, 'r') as f:
                data = json.load(f)
                saved_urn = data.get('person_urn')
                if saved_urn:
                    person_urn = f"urn:li:person:{saved_urn}"
                    print(f"[OK] Using saved URN: {person_urn[:25]}...")

    if not person_urn:
        print("[FAILED] Could not get person URN")
        print("Run: python scripts\\linkedin_api_poster.py AI_Employee_Vault --auth")
        return False

    # Post to LinkedIn
    payload = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0',
        'Content-Type': 'application/json'
    }

    print("Posting to LinkedIn...")

    try:
        response = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 201:
            result = response.json()
            post_id = result.get('id', 'unknown')
            print()
            print("[OK] POST SUCCESSFUL! 🎉")
            print(f"Post ID: {post_id}")
            log_post(text, post_id)
            print("=" * 70)
            return True
        else:
            print(f"[FAILED] Status {response.status_code}")
            print(f"Response: {response.text}")
            if response.status_code == 403:
                print("\nPermission issue. Token regenerate karo:")
                print("  python scripts\\linkedin_api_poster.py AI_Employee_Vault --auth")
            return False

    except requests.RequestException as e:
        print(f"[FAILED] Request failed: {e}")
        return False


def log_post(content, post_id):
    logs_dir = Path.cwd() / 'AI_Employee_Vault' / 'Logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / 'linkedin_simple_posts.jsonl'
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'content': content,
        'post_id': post_id
    }
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + '\n')


def main():
    if len(sys.argv) < 2:
        print('Usage: python scripts\\linkedin_simple_post.py "Your message here"')
        sys.exit(1)

    message = sys.argv[1]

    if post_to_linkedin(message):
        print("\n[OK] Done! Check your LinkedIn profile.")
    else:
        print("\n[FAILED] Post failed.")
        sys.exit(1)


if __name__ == '__main__':
    main()
