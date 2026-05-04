---
name: linkedin-poster
description: |
  Automate LinkedIn posting using Playwright. Create posts to generate sales
  and business visibility. Supports draft mode with human approval before posting.
  Uses browser automation to interact with LinkedIn's web interface.
---

# LinkedIn Poster Skill

Automate LinkedIn posts for business promotion and lead generation.

## ⚠️ Important Notice

- LinkedIn Terms of Service apply
- Use reasonable posting frequency (max 3-5 posts/day)
- Avoid spam-like behavior
- Consider using LinkedIn API for production use

## Setup

### 1. Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### 2. First-Time Login

```bash
python scripts/linkedin_poster.py --login
```

This opens a browser for you to log in to LinkedIn. Session is saved.

## Usage

### Create a Post

```bash
# Create draft post (requires approval)
python scripts/linkedin_poster.py --create "Excited to announce our new AI Employee automation service!"

# Post directly (use with caution)
python scripts/linkedin_poster.py --post "Your post content here"

# Create with image
python scripts/linkedin_poster.py --create "Post text" --image path/to/image.jpg
```

### Schedule Posts

Create a post file in `Inbox/linkedin_post_*.md`:

```markdown
---
type: linkedin_post
scheduled: 2026-02-28T09:00:00
status: draft
---

# LinkedIn Post

## Content

Excited to share our latest product update! 

#AI #Automation #Business

## Image (optional)

path/to/image.jpg
```

Then run:
```bash
python scripts/linkedin_poster.py --process-inbox
```

## Configuration

### Session Storage

```
AI_Employee_Vault/.linkedin_session/
```

**Never share this folder** - contains your LinkedIn session.

### Posting Rules

Edit `Company_Handbook.md` to set:
- Maximum posts per day
- Required hashtags
- Approval requirements

## Output Format

Posts are logged in `Logs/linkedin_posts.jsonl`:

```json
{
  "timestamp": "2026-02-28T10:30:00",
  "content": "Post text...",
  "status": "posted",
  "approval": "human_approved"
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login required every time | Session not saving - check permissions |
| Post fails | LinkedIn may have changed selectors |
| Rate limited | Reduce posting frequency |

## Security Notes

- Keep session folder private
- Don't commit session files to git
- Log out when not in use for extended periods
- Monitor for unusual account activity
