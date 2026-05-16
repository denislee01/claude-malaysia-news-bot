# Claude Singapore News Bot — Project Status

## What We Built

An **automated Instagram carousel bot** that runs fully on its own — no daily input needed. It wakes up twice a day, scrapes the latest AI news relevant to Singapore, writes and designs a 10-slide carousel using Claude AI, and posts it to [@claudesingaporeofficial](https://www.instagram.com/claudesingaporeofficial/) on Instagram.

---

## How It Works (End to End)

```
GitHub Actions (runs at 6am + 10am SGT)
    ↓
scraper.py     — Scrapes 20+ news sources for Singapore AI news
    ↓
selector.py    — Claude Haiku scores stories; Claude Sonnet writes 10-slide content
    ↓
image_gen.py   — Fetches real article photo (og:image) for cover; Pexels for inner slides
    ↓
builder.py     — Renders HTML carousel, exports 10 PNGs via Playwright
    ↓
poster.py      — Uploads to ImgBB → posts carousel to Instagram via Graph API
    ↓
logger.py      — Saves posted URLs to posted_urls.json to prevent duplicates
    ↓
GitHub Actions — Commits posted_urls.json back to repo
```

---

## Current State

| Item | Status |
|---|---|
| Bot running automatically | ✅ Live |
| Posting to @claudesingaporeofficial | ✅ Working |
| Scheduled 2x/day (6am + 10am SGT) | ✅ Active (GitHub Actions may delay slightly) |
| Dedup (no repeat stories) | ✅ Working via posted_urls.json |
| Real article images on cover slide | ✅ Implemented |
| Pexels photos for inner slides | ✅ Randomised per run |
| Conversational writing style | ✅ Updated prompts |

**Instagram account:** [@claudesingaporeofficial](https://www.instagram.com/claudesingaporeofficial/)
- 3+ posts live
- Creator account, connected to Facebook Page

---

## Tech Stack & Costs

| Service | Purpose | Cost |
|---|---|---|
| GitHub Actions | Scheduler + pipeline runner | Free |
| Anthropic API (Claude) | Story scoring + carousel writing | ~$1–3/month |
| Pexels API | Background photos for slides | Free |
| ImgBB | Hosts finished PNGs publicly for IG API | Free |
| Instagram Graph API | Posts carousel to Instagram | Free |
| Playwright (headless Chrome) | Renders HTML → PNG slides | Free |

**Total monthly cost: ~$1–3 USD** (Anthropic API only)

---

## File Reference

| File | Role |
|---|---|
| `pipeline.py` | Main orchestrator — runs all steps in order |
| `scraper.py` | Scrapes Google News, HackerNews, Reddit, GitHub, AI blogs |
| `selector.py` | Claude scores stories + writes 10-slide carousel content |
| `image_gen.py` | Fetches images (og:image + Pexels), generates gradient fallback |
| `builder.py` | Builds HTML carousel, exports PNGs via Playwright |
| `poster.py` | Uploads to ImgBB, posts to Instagram via Graph API |
| `logger.py` | Reads/writes posted_urls.json for dedup |
| `config.json` | Country-specific settings (Singapore) |
| `posted_urls.json` | Running log of all posted story URLs |
| `.github/workflows/ai-news-carousel.yml` | GitHub Actions schedule + pipeline trigger |

---

## GitHub Secrets Required

| Secret | What It Is |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API key (console.anthropic.com) |
| `PEXELS_API_KEY` | Pexels image search (pexels.com/api) |
| `IMGBB_API_KEY` | ImgBB image hosting (api.imgbb.com) |
| `IG_USER_ID` | Instagram account ID (from Meta Graph API Explorer) |
| `IG_ACCESS_TOKEN` | Long-lived IG access token (expires every 60 days) |

---

## Known Limitations

1. **GitHub Actions scheduling delay** — Free tier runs can be delayed by minutes to hours. Posts still go out, just not always at exactly 6am/10am SGT.
2. **IG Access Token expiry** — Must be manually renewed every 60 days via Meta Graph API Explorer. Set a calendar reminder.
3. **New account warmup** — Account created recently. Instagram may limit reach until it builds posting history and engagement.

---

## Next Steps

### Short Term (1–2 weeks)
- [ ] Monitor which posts get the most engagement (views, likes, saves)
- [ ] Adjust scoring prompts in `selector.py` to favour topics that perform best
- [ ] Let account build posting history before connecting any third-party tools

### Medium Term (3–4 weeks)
- [ ] **ManyChat setup** — Automate DM replies when users comment "CLAUDE" (converts comments → community members)
- [ ] **Community setup** — WhatsApp group or website landing page for community link
- [ ] **Blotato integration** — Once account is warmed up (~4 weeks), switch poster to Blotato to eliminate 60-day token renewal

### Longer Term
- [ ] Expand to other platforms (LinkedIn, Facebook) using same carousel content
- [ ] A/B test headline styles based on engagement data
- [ ] Consider replicating bot for other countries (Malaysia, Indonesia, Philippines)

---

## Improvement History

| Date | Change |
|---|---|
| Initial | Basic pipeline with gradient placeholder images |
| Week 1 | Added Pexels API for real background photos |
| Week 1 | Fixed Malaysia→Singapore references in builder.py |
| Week 1 | Fixed scrim balance (photo visible + text readable) |
| Week 1 | Randomised Pexels photo selection (no repeated images) |
| Week 1 | Fixed neutral Pexels queries (no wrong-country photos) |
| Week 1 | Added og:image extraction for real article cover photos |
| Week 1 | Rewrote writing prompts for conversational, number-driven style |
