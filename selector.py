"""Use Claude API to score stories and write 10-slide carousel content."""
import os
import json
import re
from pathlib import Path
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Load country config
_cfg_path = Path(__file__).parent / "config.json"
with open(_cfg_path) as f:
    _CFG = json.load(f)

COUNTRY        = _CFG.get("country", "Malaysia")
ACCOUNT_HANDLE = _CFG.get("account_handle", "@claudemalaysiaofficial")
COMMUNITY_NAME = _CFG.get("community_name", "Claude Malaysia")
COMMUNITY_URL  = _CFG.get("community_url", "claudemalaysia.com/join")
CURRENCY       = _CFG.get("currency", "Ringgit (RM)")
GOV_BODIES     = _CFG.get("government_bodies", "NAIO, MDEC")
LANDMARKS      = _CFG.get("local_landmarks", "KLCC, Putrajaya")
LOCAL_CONTEXT  = _CFG.get("local_context", "local founders and businesses")
FLAG_EMOJI     = _CFG.get("flag_emoji", "🇲🇾")

SCORE_PROMPT = f"""You are a viral social media editor for {ACCOUNT_HANDLE} — {COUNTRY}'s #1 AI news hub on Instagram.

Score each story 0-100 for Instagram carousel potential. Use this rubric (from Horizon's proven scoring system):
- 90-100: Groundbreaking — major breakthrough, landmark announcement, {COUNTRY}-specific shocking news
- 70-89: High value — novel AI tool/model, clear {COUNTRY} angle, community-validated (high HN/Reddit score)
- 50-69: Interesting — incremental AI news, can be localised for {COUNTRY}
- 30-49: Low priority — minor update, promotional
- 0-29: Skip — off-topic, noise, already covered

Weighted scoring factors:
1. {COUNTRY} relevance (3x weight):
   - 10: Story IS about {COUNTRY} ({GOV_BODIES}, local politician, local startup, {LANDMARKS})
   - 7: Regional story with direct {COUNTRY} impact
   - 5: Global with obvious "what this means for {COUNTRY}" angle
   - 2: Pure global, no local hook
2. Community validation (2x weight) — USE THE SIGNALS PROVIDED:
   - HN score 500+ = score 10, 300+ = 8, 150+ = 6
   - Reddit score 500+ = 10, 200+ = 8, 60+ = 5
   - GitHub stars 1000+ = 8, 500+ = 6
   - No signals = 3
3. Shock/novelty (2x): Surprising stat, contrarian take, controversy, "nobody is talking about this"
4. Visual drama (1x): Can Gemini make a cinematic image for this?
5. Community bait (1x): Will {COUNTRY} readers comment/share/tag friends?

Also assign the best Peng Joon hook angle (1-8) for each story:
1=Against The Grain, 2=Controversial, 3=Trending, 4=Celebrity, 5=Small Change Big Difference, 6=Well Known Little Understood, 7=Uncommon/Weird, 8=Numbers

Return ONLY a compact JSON array — no explanation outside the array, no markdown fences. Keep reason under 8 words.
[{{"index": 0, "score": 85, "category": "local", "angle": 2, "reason": "shocking local data centre deal"}}]

Stories (with community signals):
{{stories}}"""

WRITE_PROMPT = f"""You are a viral carousel writer for {ACCOUNT_HANDLE} — {COUNTRY}'s #1 AI news hub on Instagram.

Write a 10-slide Instagram carousel for this story.

## STEP 1: Pick the single best hook angle (Peng Joon's 8 angles)

1. AGAINST THE GRAIN — Contradicts common belief. Use when the story challenges what most people think.
   Cover: "Why [common belief] Is Dead Wrong" / "Why [popular advice] Is Keeping {COUNTRY} Behind"
   Example: "Why Saving on AI Tools Is Keeping {COUNTRY} Businesses Poor"

2. CONTROVERSIAL — Polarising, sparks debate. Use when the story has two strong opposing camps.
   Cover: "Is [X] a Scam?" / "Should People in {COUNTRY} Even Bother With [X]?"
   Example: "Is {COUNTRY}'s AI Bet a Waste of Money?"

3. TRENDING / TIMELY — Newsjack a current event. Best for breaking announcements.
   Cover: "What [current event] Reveals About [deeper truth for {COUNTRY}]"
   Example: "What Claude 4's Launch Reveals About {COUNTRY}'s AI Gap"

4. CELEBRITY / AUTHORITY — Borrow a known name. Best when a public figure is involved.
   Cover: "What [public figure]'s [action] Teaches Everyone in {COUNTRY} About [topic]"
   Example: "What This Leader Understands About AI That Most CEOs Don't"

5. SMALL CHANGE, BIG DIFFERENCE — High result, low effort. Best for tool/productivity stories.
   Cover: "One [tool/habit/move] That Changed How People in {COUNTRY} Are Using AI"
   Example: "This One Claude Prompt Saved {COUNTRY} Founders 3 Hours a Day"

6. WELL KNOWN, LITTLE UNDERSTOOD — Surface knowledge vs mastery. Best for complex topics.
   Cover: "Everyone Knows [X]. Few People in {COUNTRY} Understand What It Actually Means."
   Example: "Everyone Knows {COUNTRY} Is Building Data Centres. Few Understand Why That's Dangerous."

7. UNCOMMON / WEIRD — Novelty and surprise. Best when the story has a counterintuitive angle.
   Cover: "The Weird Way [entity] Is Using AI Nobody Talks About"
   Example: "3 Weird AI Tools {COUNTRY} SMEs Are Using to Beat MNCs"

8. NUMBERS — Specificity = credibility. Best when the story has strong data.
   Cover: "[X]% of People in {COUNTRY} [surprising fact]" / "[Number] Things About [topic] That Will Shock You"
   Example: "73% of Companies in {COUNTRY} Are Using AI Wrong. Here's the Data."

## STEP 2: Write the full carousel

Writing rules — study these carefully:
- Write like a smart friend explaining news over WhatsApp. Not a journalist. Not a presenter.
- Cover headline: Use Title Case (not ALLCAPS). Include a SPECIFIC number or name if the story has one. Max 10 words per line, 2-3 lines. Make someone stop scrolling.
  GOOD: "Someone Built a $32 Device That Shows Your AI Usage in Real Time"
  GOOD: "Malaysia Just Secured a $10 Billion AI Deal Nobody Saw Coming"
  BAD: "WHAT THIS MEANS FOR SINGAPORE'S AI FUTURE"
- Every slide headline must be a specific, conversational statement — not a generic label.
  GOOD: "Google just offered SpaceX $1.5 billion to launch satellites into orbit"
  BAD: "What the experts are saying"
- Amber line: the single most jaw-dropping stat or fact. Put the NUMBER in it if there is one.
  GOOD: **"This model runs 48x faster than GPT-4 — on a single laptop GPU."**
  BAD: **"This is a major development for the AI industry."**
- Body text: MAX 2 short sentences. Each sentence is one punchy idea — treat it like a tweet. No corporate speak. No "it is worth noting".
- Slide 3 MUST localise to {COUNTRY}. Name real companies, government bodies ({GOV_BODIES}), or professionals affected.
- Caption: Start with a provocative 1-line hook. Then 2-3 short lines expanding it. End with Comment CLAUDE.
- Write EXACTLY 8 slides (num 2 through 9). Do NOT write a slide 10 — the CTA is generated automatically.
- cover_badge: Pick one — BREAKING (major new announcement), MALAYSIA (local story), AI NEWS (global AI), EXCLUSIVE (insider/first), VIRAL (meme/funny).
- meme_text: Only for funny/ironic/meme stories. Max 2 short lines, written like a screenshot of someone's shocked reaction or a tweet. Empty string for straight news.

Return valid JSON only:
{{
  "angle": 3,
  "angle_name": "TRENDING",
  "cover_formula": 3,
  "cover_headline": "Someone Built a $32 Device\\nThat Shows Your Claude Code\\nUsage in Real Time",
  "cover_subheadline": "AI usage tracking just went physical. And it only costs $32.",
  "cover_badge": "BREAKING",
  "meme_text": "Optional. For meme-worthy stories only (AI behaving weirdly, funny reversals, ironic stats): 1-2 lines of witty commentary shown as a chat bubble on the cover. Write it like a tweet reaction. Leave empty string for straight news.",
  "caption": "A $32 gadget is now more useful than most $2,000 AI dashboards.\\n\\nHere's what it does — and why developers in {COUNTRY} are already copying it.\\n\\nSwipe to see the full breakdown ➡️\\n\\nComment \\"CLAUDE\\" to join {COMMUNITY_NAME} {FLAG_EMOJI}\\n→ {COMMUNITY_URL}\\n\\n#ai #malaysia #claudeai #aitools #technews",
  "cover_image_prompt": "A dramatic, high-quality photographic portrait. Prefer: a well-known tech CEO or entrepreneur relevant to this story (e.g. Sam Altman, Sundar Pichai, Elon Musk, local Malaysian entrepreneur), OR a cinematic real-world scene (aerial city night, storm clouds, server room blue glow). Full-bleed portrait orientation. No logos, no flat graphics, no text. Dark and bold.",
  "slides": [
    {{
      "num": 2,
      "label": "WHAT HAPPENED",
      "headline": "Write a specific 8-10 word headline describing the actual news event",
      "amber_line": "**Include the most shocking specific number or fact from this story.**",
      "body": "3 short sentences max. What happened, who did it, why it matters. Write like texting a friend.",
      "image_prompt": "Dark tech concept relevant to the story, no text, portrait"
    }},
    {{
      "num": 3,
      "label": "{COUNTRY.upper()} ANGLE",
      "headline": "Write how this directly affects someone living and working in {COUNTRY}",
      "amber_line": "**The most direct impact on {COUNTRY} professionals or businesses — with a number if possible.**",
      "body": "3 short sentences. Name real {COUNTRY} companies, sectors ({GOV_BODIES}), or use {CURRENCY} amounts. Be specific.",
      "image_prompt": "Kuala Lumpur city skyline or relevant local scene, dark moody, no text"
    }},
    {{
      "num": 4,
      "label": "THE NUMBER",
      "headline": "Write the specific stat or data point as a surprising statement",
      "amber_line": "**The exact figure — e.g. $7.3 billion, 48x faster, 73% of companies.**",
      "body": "3 sentences. What the number means, how it compares to something familiar, why it changes things.",
      "image_prompt": "Abstract data visualisation, dark background, amber highlights, no text"
    }},
    {{
      "num": 5,
      "label": "MOST PEOPLE DON'T KNOW",
      "headline": "Write the counterintuitive truth this story reveals",
      "amber_line": "**The thing that surprises even people who follow AI closely.**",
      "body": "3 sentences. Common assumption vs reality. Be direct and a little provocative.",
      "image_prompt": "Contrast concept, light vs dark, modern vs old, no text"
    }},
    {{
      "num": 6,
      "label": "EXPERT TAKE",
      "headline": "Write what a credible person or organisation actually said about this",
      "amber_line": "**A direct quote or specific claim from a named expert, company, or researcher.**",
      "body": "3 sentences. Who said it, what they said, why it matters for {COUNTRY}.",
      "image_prompt": "Professional speaker or conference scene, spotlight, dark background, no text"
    }},
    {{
      "num": 7,
      "label": "HOW WE GOT HERE",
      "headline": "Write the key turning point or backstory in one specific statement",
      "amber_line": "**The single event or year that made today's news inevitable.**",
      "body": "3 sentences. Quick timeline of 2-3 key moments. Keep it punchy.",
      "image_prompt": "Timeline or milestone concept, dark background, glowing points, no text"
    }},
    {{
      "num": 8,
      "label": "WHAT TO DO NOW",
      "headline": "Write a specific actionable move someone in {COUNTRY} can take today",
      "amber_line": "**The one thing early movers in {COUNTRY} are doing that others aren't.**",
      "body": "3 sentences. Concrete steps, tools, or decisions. Name the actual thing — not generic advice.",
      "image_prompt": "Person working on laptop at night, city lights, focused, no text"
    }},
    {{
      "num": 9,
      "label": "WATCH OUT FOR",
      "headline": "Write the specific trap or overhyped claim people in {COUNTRY} are falling for",
      "amber_line": "**The exact thing that is not worth your time or {CURRENCY} right now.**",
      "body": "3 sentences. Be specific about the mistake. Call it out directly. No softening.",
      "image_prompt": "Warning or caution concept, red amber light, dramatic shadows, no text"
    }}
  ]
}}

IMPORTANT: You MUST return valid JSON no matter what. If the article text is limited or missing, use the headline and your knowledge of this topic to fill in the gaps intelligently. Never refuse or explain — just write the carousel and return JSON.

Story to write about:
Headline: {{headline}}
Summary: {{summary}}
Full text: {{raw_text}}
Category: {{category}}"""


def score_stories(stories: list[dict]) -> list[dict]:
    """Score all stories and return sorted list."""
    def _signal_str(s: dict) -> str:
        parts = []
        if s.get("hn_score", 0) >= 150:
            parts.append(f"HN:{s['hn_score']}pts")
        if s.get("reddit_score", 0) >= 60:
            parts.append(f"Reddit:{s['reddit_score']}↑")
        if s.get("gh_stars", 0) >= 100:
            parts.append(f"GH:{s['gh_stars']}★")
        return " | " + " ".join(parts) if parts else ""

    stories_text = "\n".join(
        f"[{i}] {s['headline']} | {s['source']} | {s['category']}{_signal_str(s)}"
        for i, s in enumerate(stories)
    )

    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=8000,
        messages=[{"role": "user", "content": SCORE_PROMPT.replace("{stories}", stories_text)}]
    )
    text = resp.content[0].text.strip()
    # Strip markdown code fences if present
    text = re.sub(r"```(?:json)?\s*", "", text).strip()
    # Extract JSON array
    start = text.find("[")
    end = text.rfind("]") + 1
    if start == -1 or end == 0:
        print(f"[selector] Score parse failed — raw response:\n{text[:300]}")
        # Return stories with default score 50
        for s in stories:
            s.setdefault("score", 50)
            s.setdefault("suggested_angle", 3)
        return stories
    scores = json.loads(text[start:end])

    for s in scores:
        idx = s["index"]
        if idx < len(stories):
            stories[idx]["score"] = s["score"]
            stories[idx]["score_reason"] = s.get("reason", "")
            stories[idx]["suggested_angle"] = s.get("angle", 3)

    return sorted(stories, key=lambda x: x.get("score", 0), reverse=True)


def write_carousel(story: dict) -> dict:
    """Write full 10-slide carousel content for a story."""
    prompt = (WRITE_PROMPT
        .replace("{headline}", story["headline"])
        .replace("{summary}", story.get("summary", ""))
        .replace("{raw_text}", story.get("raw_text", "")[:2000])
        .replace("{category}", story.get("category", "global_ai"))
    )

    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    text = resp.content[0].text.strip()
    # Strip markdown code fences
    text = re.sub(r"```(?:json)?\s*", "", text).strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"[selector] write_carousel parse failed:\n{text[:300]}")
    return json.loads(text[start:end])


def run(stories: list[dict], posted_urls: set) -> tuple[dict, dict]:
    """Select top stories and write carousels. Retries next story if write fails."""
    # Filter already posted
    fresh = [s for s in stories if s["url"] not in posted_urls]
    print(f"[selector] {len(fresh)} fresh stories to score (removed {len(stories)-len(fresh)} already posted)")

    scored = score_stories(fresh)

    # Pick best Malaysia local + best global as primary picks
    local = next((s for s in scored if s.get("category") == "malaysia_local"), None)
    global_ = next((s for s in scored if s.get("category") != "malaysia_local"), None)

    picks = [s for s in [local, global_] if s][:2]
    if not picks:
        picks = scored[:2]

    # Build a fallback pool — all scored stories not already in picks
    pick_urls = {s["url"] for s in picks}
    fallback_pool = [s for s in scored if s["url"] not in pick_urls]

    results = []
    for story in picks:
        print(f"[selector] Writing carousel for: {story['headline'][:60]}... (score: {story.get('score')})")
        try:
            carousel = write_carousel(story)
            results.append((story, carousel))
        except Exception as e:
            print(f"[selector] write_carousel failed: {e}")
            print(f"[selector] Trying next story from fallback pool...")
            # Try fallback stories one by one until one succeeds
            for fallback in fallback_pool:
                if fallback["url"] in {r[0]["url"] for r in results}:
                    continue
                print(f"[selector] Fallback: {fallback['headline'][:60]}...")
                try:
                    carousel = write_carousel(fallback)
                    results.append((fallback, carousel))
                    fallback_pool.remove(fallback)
                    break
                except Exception as e2:
                    print(f"[selector] Fallback also failed: {e2}")
                    continue

    return results


if __name__ == "__main__":
    import scraper
    stories = scraper.run()
    pairs = run(stories, set())
    for story, carousel in pairs:
        print(f"\n=== {story['headline']} ===")
        print(f"Cover: {carousel.get('cover_headline')}")
        print(f"Caption preview: {carousel.get('caption','')[:100]}")
