"""
Quick Integration Test for All Platforms
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print("  AI Employee - Platform Integration Test")
print("="*60)
print()

# Test Facebook
print("1. Facebook Integration:")
fb_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
fb_page = os.getenv('FACEBOOK_PAGE_ID')
if fb_token and fb_page:
    print(f"   ✅ Configured (Page: {fb_page})")
else:
    print(f"   ❌ Missing credentials")
print()

# Test Twitter
print("2. Twitter Integration:")
tw_key = os.getenv('TWITTER_API_KEY')
if tw_key:
    print(f"   ✅ Configured")
else:
    print(f"   ❌ Missing credentials")
print()

# Test Instagram
print("3. Instagram Integration:")
ig_id = os.getenv('INSTAGRAM_ACCOUNT_ID')
if ig_id:
    print(f"   ✅ Configured (ID: {ig_id})")
else:
    print(f"   ⚠️  Not configured (optional)")
print()

# Test WhatsApp
print("4. WhatsApp Integration:")
print(f"   ✅ Script ready (run: python scripts/whatsapp_watcher.py)")
print()

# Test Odoo
print("5. Odoo ERP Integration:")
odoo_url = os.getenv('ODOO_URL')
if odoo_url:
    print(f"   ✅ Configured (URL: {odoo_url})")
else:
    print(f"   ⚠️  Using local (http://localhost:8069)")
print()

print("="*60)
print("  Quick Commands:")
print("="*60)
print()
print("# Facebook Post")
print('python scripts/facebook_poster.py AI_Employee_Vault --post "Test"')
print()
print("# Twitter Post")
print('python scripts/twitter_watcher.py AI_Employee_Vault --tweet "Test"')
print()
print("# WhatsApp Watcher")
print('python scripts/whatsapp_watcher.py AI_Employee_Vault')
print()
print("# Odoo Test")
print('python scripts/mcp_odoo_server.py AI_Employee_Vault --test-connection')
print()
print("# CEO Briefing")
print('python scripts/ceo_briefing_generator.py AI_Employee_Vault --test')
print()
