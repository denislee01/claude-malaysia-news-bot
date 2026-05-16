# Setup Guide — Claude AI News Instagram Bot
### For any country (Malaysia, Indonesia, Philippines, etc.)
> Use this guide with Claude Code. Each step tells you what to do and what to ask Claude to help with.

---

## What You're Building

A fully automated Instagram carousel bot that:
- Scrapes AI news daily from 20+ sources
- Uses Claude AI to write and score content
- Generates 10-slide carousels with real photos
- Posts automatically twice a day to Instagram
- Never posts the same story twice

**Time to set up: ~2–3 hours**
**Monthly cost: ~$1–3 USD** (Anthropic API only, everything else is free)

---

## Prerequisites — Accounts You Need First

Create accounts on all of these before starting. All are free unless noted.

| Service | URL | Notes |
|---|---|---|
| GitHub | github.com | Where the code lives and runs |
| Instagram | instagram.com | The account you'll post to |
| Meta for Developers | developers.facebook.com | Required to post to Instagram via API |
| Anthropic (Claude API) | console.anthropic.com | Needs a top-up (~$5 minimum) |
| Pexels | pexels.com/api | Free, instant API key |
| ImgBB | imgbb.com | Free image hosting, instant API key |

---

## PART 1 — Set Up the Code

### Step 1: Fork the Repository

1. Go to: `https://github.com/kingsleylow123/claudesingapore-news-bot`
2. Click **Fork** (top right) → Fork to your own GitHub account
3. Name it something like `claude-malaysia-news-bot`
4. Your repo URL will be: `https://github.com/YOUR_USERNAME/claude-malaysia-news-bot`

### Step 2: Clone It Locally

Open Claude Code in your project folder and run:
```bash
git clone https://github.com/YOUR_USERNAME/claude-malaysia-news-bot.git
cd claude-malaysia-news-bot
```

### Step 3: Customise config.json for Your Country

Open `config.json` and update every field for your target country. This is the only file you need to edit to localise the bot.

```json
{
  "country": "Malaysia",
  "account_handle": "@claudemalaysiaofficial",
  "community_name": "Claude Malaysia",
  "community_url": "claudemalaysia.com/join",
  "flag_emoji": "🇲🇾",
  "currency": "Ringgit (RM)",
  "government_bodies": "NAIO, MDEC, MOSTI",
  "local_landmarks": "KLCC, Putrajaya, Penang, Johor Bahru",
  "local_context": "Malaysian founders, SMEs, and professionals",
  "google_news_queries": [
    "Malaysia AI artificial intelligence",
    "Malaysia digital economy 2025",
    "MDEC AI Malaysia",
    "Kuala Lumpur tech startup AI",
    "Malaysia data centre investment",
    "artificial intelligence Southeast Asia Malaysia",
    "Claude AI Malaysia",
    "ChatGPT Malaysia business",
    "Malaysia AI policy government",
    "Malaysia automation workforce",
    "generative AI Malaysia enterprise",
    "Malaysia fintech AI banking",
    "Malaysian startup funding AI",
    "AI tools Malaysia SME",
    "Malaysia smart city AI",
    "Iskandar Malaysia AI investment",
    "Malaysia AI healthcare",
    "Malaysia education AI university",
    "AI Malaysia jobs employment",
    "NAIO Malaysia national AI office"
  ]
}
```

> **Ask Claude Code:** "Update config.json for Malaysia with these values" — paste the JSON above and Claude will handle it.

---

## PART 2 — Set Up Instagram

### Step 4: Create the Instagram Account

1. Create a new Instagram account (e.g. `@claudemalaysiaofficial`)
2. Use a professional profile photo (your logo or AI-themed image)
3. Write a bio: `Malaysia's No.1 AI news hub 🇲🇾 Daily AI news, tools & insights.`

### Step 5: Convert to Creator or Business Account

Instagram's API only works with Creator or Business accounts.

1. Go to Instagram app → **Settings** (top right ≡)
2. **Account** → **Switch to Professional Account**
3. Choose **Creator** or **Business** (either works)
4. Select a category — use **News & Media Website**
5. Complete the setup (skip optional steps)

### Step 6: Create a Facebook Page

Meta requires a Facebook Page linked to your Instagram for API access.

1. Go to [facebook.com/pages/create](https://facebook.com/pages/create)
2. Choose **Business or Brand**
3. Name it the same as your Instagram (e.g. "Claude Malaysia")
4. Category: **Media/News company**
5. Complete basic setup — no need to customise it fully

### Step 7: Connect Instagram to Facebook Page

1. In Instagram app → **Settings** → **Account** → **Linked Accounts**
2. Connect to your Facebook Page
   OR
1. In Facebook → your Page → **Settings** → **Linked Accounts** → Instagram → Connect

---

## PART 3 — Set Up Meta Developer API

This gives you the credentials to post to Instagram programmatically.

> ⚠️ **Note:** Meta's developer UI changes frequently. The steps below reflect the working flow as of 2025. If your screen looks slightly different, look for equivalent options — the goal is to reach the **Instagram API → API setup with Instagram login** page.

### Step 8: Create a Meta Developer App

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Click **My Apps** → **Create App**
3. When prompted for a use case, look for an **Instagram** or **Instagram Business** option and select it → **Next**
4. Give your app a name: e.g. `ClaudeSingaporeBot`
5. Click **Create App**

### Step 9: Add Your Instagram Account as a Tester

Before generating a token, you need to give your Instagram account the Tester role.

1. In your app dashboard → left sidebar → **Roles** → **Roles**
2. Scroll down to **Instagram Testers** → click **Add Instagram Testers**
3. Search for your Instagram username (e.g. `claudesingaporeofficial`)
4. Send the invite

### Step 10: Accept the Tester Invite on Instagram

1. Open the Instagram app → **Settings** → **Website Permissions** → **Apps and Websites**
2. Find the pending tester invite → **Accept**

### Step 11: Add Required Permissions

1. In your app dashboard → left sidebar → **Use cases** → click **Customize** next to Instagram API
2. Click **Permissions and features** in the left sub-menu
3. Find and click **Add** next to each of these permissions:
   - `instagram_business_basic`
   - `instagram_manage_comments`
   - `instagram_business_manage_messages`
   - `instagram_content_publish` ← **required for posting**

### Step 12: Get Your IG User ID and Access Token

This is done directly inside the Meta developer dashboard — **not** via Graph API Explorer.

1. In the left sub-menu → click **API setup with Instagram login**
2. You'll see three sections. Skip Section 1 (permissions already done) and Section 3 (webhooks — skip entirely)
3. Expand **Section 2: Generate access tokens**
4. Click **Add account** → log in with your Instagram account
5. Once added, your account appears in the table with two columns:
   - The number shown under your username is your **`IG_USER_ID`** — copy it
   - Click **Generate token** → follow the prompts → copy the token — this is your **`IG_ACCESS_TOKEN`**

> ⚠️ **Important:** This token expires every 60 days. Set a calendar reminder to come back to this exact page, click **Generate token** again, and update the `IG_ACCESS_TOKEN` secret in GitHub.

---

## PART 4 — Get Your API Keys

### Step 13: Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Go to **API Keys** → **Create Key**
4. Copy the key (starts with `sk-ant-...`)
5. Go to **Billing** → top up a minimum of $5

> Note: Your Claude.ai subscription is separate from the API. You need API credits.

### Step 14: Pexels API Key

1. Go to [pexels.com/api](https://www.pexels.com/api/)
2. Sign up → click **Get Started**
3. Fill in your app name and purpose
4. Copy your API key instantly

### Step 15: ImgBB API Key

1. Go to [api.imgbb.com](https://api.imgbb.com/)
2. Log in or sign up
3. Your API key is shown on the page — copy it

---

## PART 5 — Configure GitHub

### Step 16: Add All Secrets to GitHub

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** for each of these:

| Secret Name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `PEXELS_API_KEY` | Your Pexels API key |
| `IMGBB_API_KEY` | Your ImgBB API key |
| `IG_USER_ID` | Your Instagram User ID (numbers only) |
| `IG_ACCESS_TOKEN` | Your long-lived access token |

### Step 17: Enable GitHub Actions

1. Go to your repo → **Actions** tab
2. If Actions is disabled, click **Enable Actions**
3. You should see **Singapore AI News Carousel** (or your renamed workflow) in the left sidebar

### Step 18: Rename the Workflow for Your Country

In `.github/workflows/ai-news-carousel.yml`, update line 1:
```yaml
name: Malaysia AI News Carousel
```

> **Ask Claude Code:** "Rename the workflow name in the yml file to Malaysia AI News Carousel"

---

## PART 6 — Test the Bot

### Step 19: Run a Manual Test

1. Go to **Actions** tab in your GitHub repo
2. Click your workflow name in the left sidebar
3. Click **Run workflow** → **Run workflow** (green button)
4. Watch the steps run in real time (takes 4–5 minutes)

**What you should see in the logs:**
```
── STEP 1: SCRAPE ──
[scraper] Google News: 20 queries...
[scraper] Total unique stories: 45

── STEP 2: DEDUP CHECK ──
[pipeline] 0 already-posted URLs loaded

── STEP 3: SELECT + WRITE ──
[selector] Writing carousel for: ...

── STEP 4: IMAGE GENERATION ──
[image_gen] Cover: used real article image ✓
[image_gen] Pexels: 'artificial intelligence circuit dark' → ...

── STEP 5: BUILD CAROUSEL ──
[builder] HTML written
[builder] Exported slide 1 ... slide 10

── STEP 6: POST ──
[poster] Uploaded 10 slides to ImgBB
[poster] Published! post_id=...

── STEP 7: LOG ──
✓ DONE
```

### Step 20: Verify on Instagram

1. Open Instagram and go to your account
2. You should see the carousel post
3. Check all 10 slides look correct
4. Check the caption and hashtags

---

## PART 7 — The Bot Is Live

Once the manual test works, the bot runs automatically on schedule.

**Default schedule (UTC):**
```yaml
- cron: '0 22 * * *'   # 6:00 AM local time (SGT/MYT)
- cron: '0 2 * * *'    # 10:00 AM local time
```

> Adjust these times in `.github/workflows/ai-news-carousel.yml` for your timezone.
> Use [crontab.guru](https://crontab.guru) to convert times.

---

## Troubleshooting

### "KeyError" or JSON parse error in selector step
Claude's response had unexpected formatting. Re-run the workflow — it usually self-corrects.

### "400 Bad Request" from Instagram API
- Check that `IG_USER_ID` and `IG_ACCESS_TOKEN` secrets are correct (no extra spaces)
- Make sure you added `instagram_content_publish` permission to your token
- Make sure your Instagram account is Creator/Business type

### "401 Unauthorized" from Instagram API
Your token has expired. Go back to Meta Graph API Explorer and generate a new long-lived token. Update the `IG_ACCESS_TOKEN` GitHub Secret.

### "rejected — fetch first" error in git push step
Two runs happened close together. Already fixed with `git pull --rebase` in the workflow. Just re-run.

### Bot ran but no post on Instagram
Check the "Run pipeline" step logs. Look for `[pipeline] No fresh stories` — this means all scraped stories were already posted. Wait for the next scheduled run.

### Images look wrong or all black
Pexels API key might be missing or invalid. Check the `PEXELS_API_KEY` secret. The bot will use dark gradient fallbacks if Pexels fails — this is safe but less visually appealing.

---

## Maintenance Schedule

| Task | Frequency | How |
|---|---|---|
| Refresh IG Access Token | Every 60 days | Meta Graph API Explorer → generate new token → update GitHub Secret |
| Review top performing posts | Weekly | Check Instagram Insights on the posts |
| Update google_news_queries | Monthly | Edit config.json to add/remove search terms |
| Check API spending | Monthly | console.anthropic.com → Usage |

---

## Next Steps After Launch

### Week 1–2: Monitor & Learn
- Check which posts get the most views and comments
- Note what topics, hooks, and headlines work best
- Don't change anything yet — build a baseline

### Week 3–4: Set Up ManyChat
ManyChat automates DM replies when users comment "CLAUDE". Every carousel ends with this CTA already. ManyChat closes the loop.

1. Sign up at [manychat.com](https://manychat.com)
2. Connect your Instagram account
3. Create a **Keyword Trigger**: when someone comments `CLAUDE` → send them a DM with your community link
4. Cost: ~$15/month (worth it once you have engagement)

### Month 2+: Consider Blotato
Once your account has 4+ weeks of posting history:
1. Sign up at [my.blotato.com](https://my.blotato.com)
2. Connect Instagram via their UI (no Meta developer setup needed)
3. Get your Blotato API key
4. Replace `poster.py` with Blotato API calls
5. Remove `IG_USER_ID` and `IG_ACCESS_TOKEN` from GitHub Secrets
6. Add `BLOTATO_API_KEY` instead
7. No more 60-day token renewal

> **Ask Claude Code:** "Rewrite poster.py to use Blotato API instead of Instagram Graph API"

---

## Replicating for Another Country

To spin up a second bot (e.g. Claude Indonesia after Claude Malaysia):

1. Fork the repo again with a new name
2. Edit `config.json` with Indonesia-specific values
3. Create a new Instagram account
4. Repeat PART 2, 3, 4, 5, 6 above
5. Each country bot runs in its own GitHub repo with its own secrets

The only shared cost is Anthropic API — and since usage is low, running 2–3 country bots together costs ~$3–8/month total.

---

*Built with Claude Code · Runs on GitHub Actions · Posts via Instagram Graph API*
