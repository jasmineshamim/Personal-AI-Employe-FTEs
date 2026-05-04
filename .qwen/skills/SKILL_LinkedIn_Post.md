---
name: linkedin-post
description: |
  Post to LinkedIn using official LinkedIn API v2. Supports text posts,
  images, and article sharing. Requires LinkedIn Developer app credentials
  and OAuth 2.0 authentication. Use for automated business updates,
  lead generation posts, and content marketing.
---

# LinkedIn Post Skill

Post content to LinkedIn automatically using the official LinkedIn API.

## Prerequisites

### 1. LinkedIn Developer Account

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Sign in with your LinkedIn account
3. Click **"Create app"**

### 2. App Configuration

Fill in app details:
- **App name:** AI Employee (or your choice)
- **LinkedIn Page:** Select or create a page
- **Privacy Policy:** Your website or GitHub profile
- **User Agreement:** Your website or GitHub profile
- **Logo:** Optional (recommended)

### 3. Enable Permissions

In your app dashboard:
1. Click **"Permissions"** tab
2. Find **"Share on LinkedIn"** (`w_member_social`)
3. Click **"Request"** or **"Enable"**
4. Accept the terms

### 4. Get API Credentials

1. Click **"Auth"** tab
2. Copy:
   - **Client ID**
   - **Client Secret**
3. Click **"Edit"** on OAuth 2.0 Redirect URLs
4. Add: `http://localhost:8080`
5. Click **"Save"**

---

## Setup

### Step 1: Install Dependencies

```bash
pip install requests
```

### Step 2: Create Credentials File

Create `linkedin_api_credentials.json` in project root:

```json
{
  "client_id": "YOUR_CLIENT_ID_HERE",
  "client_secret": "YOUR_CLIENT_SECRET_HERE",
  "redirect_uri": "http://localhost:8080"
}
```

### Step 3: First-Time Authentication

```bash
python scripts/linkedin_post.py --auth
```

**What happens:**
1. Browser opens automatically
2. Sign in to LinkedIn (if not already)
3. Click **"Allow"** to authorize your app
4. Authorization code is captured
5. Access token is saved to `.linkedin_api_token.json`

**Token expires in 60 days** - re-authenticate when expired.

---

## Usage

### Post Text Update

```bash
python scripts/linkedin_post.py --post "Excited to share our new AI Employee automation! #AI #Automation"
```

### Post with Image

```bash
python scripts/linkedin_post.py --post "Check out our latest product!" --image path/to/image.jpg
```

### Check Authentication Status

```bash
python scripts/linkedin_post.py --status
```

### Re-authenticate (when token expires)

```bash
python scripts/linkedin_post.py --auth
```

---

## API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/oauth/v2/authorization` | GET | User authorization |
| `/oauth/v2/accessToken` | POST | Get access token |
| `/v2/me` | GET | Get user URN |
| `/v2/posts` | POST | Create post |

---

## Response Format

### Success Response

```json
{
  "id": "urn:li:share:7169123456789012345",
  "status": "created"
}
```

### Error Response

```json
{
  "serviceErrorCode": "INVALID_REQUEST",
  "message": "Invalid request",
  "status": 400
}
```

---

## Rate Limits

| Limit | Value |
|-------|-------|
| Posts per day | 50 |
| API calls per 15 min | 500 |
| Token validity | 60 days |

---

## Troubleshooting

### "Token expired"

```bash
python scripts/linkedin_post.py --auth
```

### "Invalid credentials"

Check `linkedin_api_credentials.json`:
- Client ID is correct (no spaces)
- Client Secret is correct
- Redirect URI matches (`http://localhost:8080`)

### "Permission denied"

1. Go to LinkedIn Developers → Your App
2. Enable `w_member_social` permission
3. Wait 5 minutes for propagation

### "Port 8080 already in use"

Edit `linkedin_api_credentials.json`:
```json
{
  "redirect_uri": "http://localhost:8081"
}
```

Then update the port in `linkedin_post.py` authentication handler.

---

## Security Notes

- **Never commit** `linkedin_api_credentials.json` to git
- **Never share** Client Secret
- **Keep token file private** (`.linkedin_api_token.json`)
- Add to `.gitignore`:
  ```
  linkedin_api_credentials.json
  .linkedin_api_token.json
  ```

---

## Integration with AI Employee

### Example: Auto-post after processing email

```python
# In orchestrator.py
if email_contains_keyword('product launch'):
    subprocess.run([
        'python', 'scripts/linkedin_post.py',
        '--post', f"New product alert! {email_subject}"
    ])
```

### Example: Scheduled business update

```python
# In task_scheduler.py
def daily_update():
    content = generate_business_update()
    subprocess.run([
        'python', 'scripts/linkedin_post.py',
        '--post', content
    ])
```

---

## Code Example

```python
from linkedin_post import LinkedInPoster

# Initialize
poster = LinkedInPoster()

# Load credentials and token
if not poster.load_token():
    poster.authenticate()

# Post to LinkedIn
poster.create_post("Hello LinkedIn! #AI")
```

---

## Resources

- [LinkedIn API Documentation](https://learn.microsoft.com/en-us/linkedin/marketing/)
- [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
- [OAuth 2.0 Guide](https://oauth.net/2/)
- [Share API v2](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/share-api)

---

*LinkedIn Post Skill v1.0*
*For AI Employee Silver Tier*
