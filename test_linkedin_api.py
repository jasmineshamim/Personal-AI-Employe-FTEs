#!/usr/bin/env python3
"""Test LinkedIn API posting."""

import sys
sys.path.insert(0, 'scripts')

from linkedin_api_poster import LinkedInAPIPoster

# Test post
poster = LinkedInAPIPoster('AI_Employee_Vault')

# Load credentials from .env
if poster.load_credentials():
    print("[OK] Credentials loaded")
    
    # Try to post
    if poster.load_token() or poster.access_token:
        print("[OK] Token available")
        
        # Post
        result = poster.create_post("Test post from AI Employee! #SilverTier #Hackathon2026")
        
        if result:
            print("\n[SUCCESS] Post created!")
        else:
            print("\n[FAILED] Post failed")
    else:
        print("[FAILED] No token - need to authenticate")
        print("Run: python scripts/linkedin_api_poster.py --auth")
else:
    print("[FAILED] Could not load credentials")
