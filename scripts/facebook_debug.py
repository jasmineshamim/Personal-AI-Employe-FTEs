"""
Facebook Token Permission Debugger
Check what permissions your token actually has
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def debug_token():
    """Debug Facebook access token permissions"""
    
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    page_id = os.getenv('FACEBOOK_PAGE_ID')
    
    if not access_token:
        print("❌ FACEBOOK_ACCESS_TOKEN not found in .env")
        return
    
    if not page_id:
        print("❌ FACEBOOK_PAGE_ID not found in .env")
        return
    
    print("="*60)
    print("  FACEBOOK TOKEN DEBUGGER")
    print("="*60)
    print()
    
    # Step 1: Check token info
    print("1. Checking token info...")
    token_info_url = f"https://graph.facebook.com/debug_token?input_token={access_token}&access_token={access_token}"
    response = requests.get(token_info_url)
    token_data = response.json()
    
    if 'data' in token_data:
        data = token_data['data']
        print(f"   App ID: {data.get('app_id', 'N/A')}")
        print(f"   User ID: {data.get('user_id', 'N/A')}")
        print(f"   Expires: {data.get('expires_at', 'N/A')}")
        print(f"   Valid: {data.get('is_valid', False)}")
        print()
        
        # Check permissions
        print("2. Token Permissions:")
        permissions = data.get('scopes', [])
        required = ['pages_manage_posts', 'pages_read_engagement', 'pages_show_list']
        
        for perm in required:
            status = "✅" if perm in permissions else "❌"
            print(f"   {status} {perm}")
        print()
    else:
        print(f"   ❌ Error: {token_data}")
        print()
    
    # Step 2: Check Page permissions
    print("3. Checking Page permissions...")
    page_url = f"https://graph.facebook.com/v25.0/{page_id}?fields=page_token&access_token={access_token}"
    response = requests.get(page_url)
    page_data = response.json()
    
    if 'error' in page_data:
        print(f"   ⚠️ Page access issue: {page_data['error'].get('message', 'Unknown')}")
    else:
        print(f"   ✅ Page accessible: {page_id}")
    print()
    
    # Step 3: Test posting (dry run)
    print("4. Testing post creation (dry run)...")
    test_url = f"https://graph.facebook.com/v25.0/{page_id}/feed"
    test_params = {
        'message': 'Test post from debugger',
        'access_token': access_token
    }
    response = requests.post(test_url, data=test_params)
    result = response.json()
    
    if response.status_code == 200:
        print(f"   ✅ POST SUCCESSFUL! Post ID: {result.get('id')}")
    else:
        print(f"   ❌ POST FAILED")
        print(f"   Error: {result.get('error', {}).get('message', 'Unknown')}")
        print(f"   Error Code: {result.get('error', {}).get('error_subcode', 'N/A')}")
    print()
    
    # Step 4: Check if user is page admin
    print("5. Checking Page Admin status...")
    admin_url = f"https://graph.facebook.com/v25.0/{page_id}?fields=can_post,likes&access_token={access_token}"
    response = requests.get(admin_url)
    admin_data = response.json()
    
    if 'can_post' in admin_data:
        print(f"   Can Post: {admin_data.get('can_post')}")
    else:
        print(f"   ⚠️ Could not check admin status: {admin_data}")
    print()
    
    # Summary
    print("="*60)
    print("  SUMMARY & RECOMMENDATIONS")
    print("="*60)
    print()
    
    issues = []
    
    if not token_data.get('data', {}).get('is_valid', False):
        issues.append("❌ Token is INVALID - Generate new token")
    
    if 'pages_manage_posts' not in token_data.get('data', {}).get('scopes', []):
        issues.append("❌ Missing pages_manage_posts permission")
    
    if 'pages_read_engagement' not in token_data.get('data', {}).get('scopes', []):
        issues.append("❌ Missing pages_read_engagement permission")
    
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"   {issue}")
        print()
        print("SOLUTION:")
        print("   1. Go to: https://developers.facebook.com/tools/explorer/")
        print("   2. Select your app")
        print("   3. Click: Get Token → Get Page Access Token")
        print("   4. CHECK: pages_manage_posts, pages_read_engagement")
        print("   5. Select your Page")
        print("   6. Copy new token and update .env file")
        print("   7. Restart terminal and try again")
    else:
        print("✅ All checks passed! Token should work.")
        print("   If posting still fails, try generating a fresh token.")
    
    print()


if __name__ == '__main__':
    debug_token()
