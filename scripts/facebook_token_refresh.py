"""
Facebook Long-Lived Token Generator

Generates a 60-day valid token from short-lived token
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def generate_long_lived_token():
    """Generate 60-day Facebook token"""
    
    app_id = os.getenv('FACEBOOK_APP_ID')
    app_secret = os.getenv('FACEBOOK_APP_SECRET')
    current_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    
    if not all([app_id, app_secret, current_token]):
        print("❌ Missing credentials in .env file")
        print("   Add: FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, FACEBOOK_ACCESS_TOKEN")
        return None
    
    # Exchange token
    url = 'https://graph.facebook.com/oauth/access_token'
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': current_token
    }
    
    response = requests.get(url, params=params)
    result = response.json()
    
    if 'access_token' in result:
        long_lived_token = result['access_token']
        expires_in = result.get('expires_in', 5184000)
        days = expires_in // 86400
        
        print("="*60)
        print("  LONG-LIVED TOKEN GENERATED")
        print("="*60)
        print()
        print(f"✅ Token: {long_lived_token[:50]}...")
        print(f"⏰ Expires in: {days} days ({expires_in} seconds)")
        print()
        print("Update your .env file:")
        print(f"FACEBOOK_ACCESS_TOKEN={long_lived_token}")
        print()
        
        return long_lived_token
    else:
        print(f"❌ Error: {result}")
        return None


if __name__ == '__main__':
    generate_long_lived_token()
