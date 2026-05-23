"""Build HTML carousel from story data + images, then export 10 PNGs via Playwright."""
import asyncio
import os
import json
import base64
from pathlib import Path

_cfg_path = Path(__file__).parent / "config.json"
with open(_cfg_path) as f:
    _CFG = json.load(f)
ACCOUNT_HANDLE = _CFG.get("account_handle", "@claudemalaysiaofficial")
COMMUNITY_URL  = _CFG.get("community_url", "claudemalaysia.com/join")
COMMUNITY_NAME = _CFG.get("community_name", "Claude Malaysia")
FLAG_EMOJI     = _CFG.get("flag_emoji", "🇲🇾")

SLIDE_W    = 1080
SLIDE_H    = 1350
VIEWPORT_W = 540
VIEWPORT_H = 675
SCALE      = SLIDE_W / VIEWPORT_W  # 2.0


def _img_to_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _accent_line(text: str) -> str:
    import re
    return re.sub(r"\*\*(.*?)\*\*", r'<span class="acc">\1</span>', text)

_amber_line = _accent_line  # backward-compat


def build_html(carousel: dict, image_paths: list[str], out_path: str) -> str:
    slides_html = []

    # ── Slide 1: Cover ──────────────────────────────────────────────────────
    cover_b64 = _img_to_b64(image_paths[0]) if image_paths else ""
    slides_html.append(f"""
    <div class="slide cover-slide">
      <div class="photo" style="background-image:url('data:image/jpeg;base64,{cover_b64}')"></div>
      <div class="cover-glow"></div>
      <div class="top-line"></div>
      <div class="cover-inner">
        <span class="handle">{ACCOUNT_HANDLE}</span>
        <div class="cover-body">
          <div class="cover-tag"><span class="tag-dash"></span>{FLAG_EMOJI} AI NEWS</div>
          <h1 class="cover-h1">{carousel.get('cover_headline', 'AI NEWS')}</h1>
          <p class="cover-sub">{carousel.get('cover_subheadline', '')}</p>
          <div class="swipe-hint">SWIPE TO EXPLORE →</div>
          <div class="dots">{_dots(10, 0)}</div>
        </div>
      </div>
      <div class="prog-track"><div class="prog-fill" style="width:10%"></div></div>
    </div>""")

    # ── Slides 2–9: Inner ───────────────────────────────────────────────────
    for i, slide in enumerate(carousel.get("slides", [])):
        idx       = i + 1
        img_b64   = _img_to_b64(image_paths[idx]) if idx < len(image_paths) else ""
        callout   = _accent_line(slide.get("amber_line", ""))
        body      = _accent_line(slide.get("body", ""))
        num       = slide.get("num", i + 2)
        pct       = int((num / 10) * 100)
        slides_html.append(f"""
    <div class="slide inner-slide">
      <div class="photo photo-dim" style="background-image:url('data:image/jpeg;base64,{img_b64}')"></div>
      <div class="top-line"></div>
      <div class="slide-num">{num:02d}<span class="num-total"> /10</span></div>
      <div class="inner-layout">
        <span class="handle">{ACCOUNT_HANDLE}</span>
        <div class="inner-body">
          <div class="label">{slide.get('label', '')}</div>
          <h2 class="inner-h2">{slide.get('headline', '')}</h2>
          <div class="callout">{callout}</div>
          <p class="body-text">{body}</p>
        </div>
      </div>
      <div class="arr">›</div>
      <div class="prog-track"><div class="prog-fill" style="width:{pct}%"></div></div>
    </div>""")

    # ── Slide 10: CTA ───────────────────────────────────────────────────────
    cta_b64 = _img_to_b64(image_paths[-1]) if len(image_paths) >= 10 else ""
    slides_html.append(f"""
    <div class="slide cta-slide">
      <div class="photo" style="background-image:url('data:image/jpeg;base64,{cta_b64}')"></div>
      <div class="cta-glow"></div>
      <div class="top-line"></div>
      <div class="cta-inner">
        <span class="handle">{ACCOUNT_HANDLE}</span>
        <div class="cta-body">
          <div class="cta-flag">{FLAG_EMOJI}</div>
          <h2 class="cta-h2">WANT MORE<br>STORIES LIKE THIS?</h2>
          <div class="cta-btn">Comment <span class="acc">CLAUDE</span></div>
          <p class="cta-desc">Join the {COMMUNITY_NAME} community<br>Get AI news straight to your DMs</p>
          <div class="cta-url">{COMMUNITY_URL}</div>
        </div>
      </div>
      <div class="prog-track"><div class="prog-fill" style="width:100%"></div></div>
    </div>""")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,600;0,700;0,800;1,400&display=swap" rel="stylesheet">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#000; font-family:'Inter',system-ui,sans-serif; overflow:hidden; }}

  :root {{
    --bg:      #090909;
    --acc:     #C8714A;
    --text:    #F0EDE8;
    --dim:     rgba(240,237,232,0.52);
    --muted:   rgba(240,237,232,0.22);
    --border:  rgba(240,237,232,0.07);
  }}

  .viewport {{ width:{VIEWPORT_W}px; height:{VIEWPORT_H}px; overflow:hidden; position:relative; }}
  .track    {{ display:flex; width:{10 * VIEWPORT_W}px; transition:transform .3s ease; }}

  /* ── Base slide ── */
  .slide {{
    width:{VIEWPORT_W}px; height:{VIEWPORT_H}px; flex-shrink:0;
    background:var(--bg); position:relative; overflow:hidden;
  }}
  /* Dot grid texture */
  .slide::after {{
    content:''; position:absolute; inset:0; z-index:1; pointer-events:none;
    background-image: radial-gradient(circle, rgba(240,237,232,0.04) 1px, transparent 1px);
    background-size: 24px 24px;
  }}

  /* Subtle photo texture (used on all slides) */
  .photo {{
    position:absolute; inset:0; z-index:2;
    background-size:cover; background-position:center;
    opacity:.07;
  }}
  .photo-dim {{ opacity:.04; }}

  /* Orange accent rule at slide top */
  .top-line {{
    position:absolute; top:0; left:0; right:0; height:1.5px;
    background:var(--acc); z-index:10;
  }}

  /* Progress bar at slide bottom */
  .prog-track {{
    position:absolute; bottom:0; left:0; right:0; height:1.5px;
    background:var(--border); z-index:10;
  }}
  .prog-fill {{ height:100%; background:var(--acc); }}

  /* Shared handle */
  .handle {{
    font-size:9px; color:var(--muted); letter-spacing:1px; text-transform:lowercase;
  }}

  /* ── Cover ────────────────────────────────────────────────────────────── */
  .cover-glow {{
    position:absolute; inset:0; z-index:3;
    background: radial-gradient(ellipse at 20% 100%, rgba(200,113,74,.22) 0%, transparent 56%);
  }}
  .cover-inner {{
    position:relative; z-index:4; height:100%;
    padding:22px 30px 28px;
    display:flex; flex-direction:column;
  }}
  .cover-body {{ margin-top:auto; }}

  .cover-tag {{
    font-size:9px; font-weight:700; letter-spacing:3.5px; text-transform:uppercase;
    color:var(--acc); display:flex; align-items:center; gap:8px; margin-bottom:14px;
  }}
  .tag-dash {{ display:inline-block; width:18px; height:1.5px; background:var(--acc); flex-shrink:0; }}

  .cover-h1 {{
    font-size:40px; font-weight:800; color:var(--text);
    line-height:1.06; letter-spacing:-1.5px; text-transform:uppercase;
    margin-bottom:14px;
  }}
  .cover-sub {{
    font-size:13px; color:var(--dim); line-height:1.58;
    margin-bottom:20px; max-width:94%;
  }}
  .swipe-hint {{
    font-size:8.5px; letter-spacing:3.5px; color:var(--muted);
    text-transform:uppercase; margin-bottom:10px;
  }}
  .dots {{ display:flex; gap:4px; align-items:center; }}
  .dot {{ width:5px; height:5px; border-radius:50%; background:rgba(240,237,232,.15); }}
  .dot.on {{ background:var(--acc); width:18px; border-radius:2px; }}

  /* ── Inner slides ─────────────────────────────────────────────────────── */
  .slide-num {{
    position:absolute; top:16px; right:22px; z-index:5;
    font-size:11px; color:var(--muted); letter-spacing:.5px;
    font-variant-numeric:tabular-nums;
  }}
  .num-total {{ opacity:.45; font-size:10px; }}

  .inner-layout {{
    position:relative; z-index:4; height:100%;
    padding:20px 30px 24px; display:flex; flex-direction:column;
  }}
  .inner-body {{
    flex:1; display:flex; flex-direction:column; justify-content:center;
    padding-bottom:18px;
  }}
  .label {{
    font-size:9px; font-weight:700; letter-spacing:3px; text-transform:uppercase;
    color:var(--acc); display:flex; align-items:center; gap:8px; margin-bottom:16px;
  }}
  .label::before {{
    content:''; width:14px; height:1.5px; background:var(--acc);
    display:block; flex-shrink:0;
  }}
  .inner-h2 {{
    font-size:30px; font-weight:800; color:var(--text);
    line-height:1.18; letter-spacing:-.5px; margin-bottom:18px;
  }}
  .callout {{
    border-left:2px solid var(--acc);
    padding:4px 0 4px 14px; margin-bottom:16px;
    font-size:14px; font-weight:600; color:var(--text); line-height:1.55;
  }}
  .acc {{ color:var(--acc); }}
  .body-text {{
    font-size:13px; color:var(--dim); line-height:1.72;
  }}
  .arr {{
    position:absolute; right:18px; bottom:22px; z-index:5;
    font-size:20px; color:var(--acc); opacity:.55; line-height:1;
  }}

  /* ── CTA ──────────────────────────────────────────────────────────────── */
  .cta-glow {{
    position:absolute; inset:0; z-index:3;
    background: radial-gradient(ellipse at 50% 85%, rgba(200,113,74,.18) 0%, transparent 60%);
  }}
  .cta-inner {{
    position:relative; z-index:4; height:100%;
    padding:22px 30px 28px; display:flex; flex-direction:column;
  }}
  .cta-body {{
    flex:1; display:flex; flex-direction:column;
    align-items:center; justify-content:center; text-align:center;
  }}
  .cta-flag   {{ font-size:26px; margin-bottom:16px; }}
  .cta-h2     {{ font-size:26px; font-weight:800; color:var(--text);
                 line-height:1.18; letter-spacing:-.5px; margin-bottom:22px; }}
  .cta-btn    {{ font-size:13px; font-weight:700; color:var(--text);
                 border:1.5px solid var(--acc); padding:10px 28px;
                 border-radius:30px; margin-bottom:20px; letter-spacing:.3px; }}
  .cta-desc   {{ font-size:12px; color:var(--dim); line-height:1.65; margin-bottom:14px; }}
  .cta-url    {{ font-size:11px; font-weight:700; color:var(--acc); letter-spacing:.8px; }}
</style>
</head>
<body>
<div class="viewport">
  <div class="track" id="track">
{''.join(slides_html)}
  </div>
</div>
<script>
let cur=0;
function go(n){{
  cur=Math.max(0,Math.min(9,n));
  document.getElementById('track').style.transform=`translateX(-${{cur*{VIEWPORT_W}}}px)`;
}}
</script>
</body>
</html>"""

    with open(out_path, "w") as f:
        f.write(html)
    print(f"[builder] HTML written: {out_path}")
    return out_path


def _dots(total: int, active: int) -> str:
    return "".join(
        f'<div class="dot{"" if i != active else " on"}"></div>'
        for i in range(total)
    )


async def _export_pngs(html_path: str, out_dir: str, n_slides: int = 10) -> list[str]:
    from playwright.async_api import async_playwright

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    paths = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
            device_scale_factor=SCALE,
        )
        abs_path = os.path.abspath(html_path)
        await page.goto(f"file://{abs_path}", wait_until="networkidle")
        await page.wait_for_timeout(2000)  # allow font render

        vp = await page.query_selector(".viewport")
        for i in range(n_slides):
            await page.evaluate(f"go({i})")
            await page.wait_for_timeout(400)
            out = f"{out_dir}/slide_{i+1:02d}.png"
            await vp.screenshot(path=out)
            paths.append(out)
            print(f"[builder] Exported slide {i+1}: {out}")

        await browser.close()

    return paths


def export_pngs(html_path: str, out_dir: str, n_slides: int = 10) -> list[str]:
    return asyncio.run(_export_pngs(html_path, out_dir, n_slides))


def run(carousel: dict, image_paths: list[str], run_id: str) -> list[str]:
    html_out = f"/tmp/cm_{run_id}.html"
    png_dir  = os.path.expanduser(f"~/Downloads/carousels/cm-{run_id}")

    build_html(carousel, image_paths, html_out)
    png_paths = export_pngs(html_out, png_dir)
    print(f"[builder] Done — {len(png_paths)} PNGs in {png_dir}")
    return png_paths
