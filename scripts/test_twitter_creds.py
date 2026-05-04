"""
Test Twitter Credentials (Fixed)
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("="*60)
print("  Twitter Credentials Test")
print("="*60)
print()

# Check credentials
api_key = os.getenv('TWITTER_API_KEY')
api_secret = os.getenv('TWITTER_API_SECRET')
access_token = os.getenv('TWITTER_ACCESS_TOKEN')
access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

print("Credentials from .env:")
print(f"  API Key: {api_key[:20] if api_key else 'None'}...")
print(f"  API Secret: {api_secret[:20] if api_secret else 'None'}...")
print(f"  Access Token: {access_token[:20] if access_token else 'None'}...")
print(f"  Access Token Secret: {access_token_secret[:20] if access_token_secret else 'None'}...")
print()

# Check if all present
if all([api_key, api_secret, access_token, access_token_secret]):
    print("✅ All credentials present!")
else:
    print("❌ Some credentials missing!")
print()

# Try to connect
try:
    import tweepy
    
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )
    
    me = client.get_me()
    
    # Handle different response types
    if hasattr(me, 'data'):
        username = me.data['username']
    elif isinstance(me, dict):
        username = me['data']['username']
    else:
        username = str(me)
        
    print(f"✅ Twitter connected as @{username}")
    print()
    print("🎉 Twitter is ready for posting!")
    
except Exception as e:
    print(f"❌ Twitter connection failed: {e}")
