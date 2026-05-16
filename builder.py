"""Build HTML carousel from story data + images, then export 10 PNGs via Playwright."""
import asyncio
import os
import json
import base64
from pathlib import Path

# Load country config
_cfg_path = Path(__file__).parent / "config.json"
with open(_cfg_path) as f:
    _CFG = json.load(f)
ACCOUNT_HANDLE = _CFG.get("account_handle", "@claudemalaysiaofficial")
COMMUNITY_URL  = _CFG.get("community_url", "claudemalaysia.com/join")
COMMUNITY_NAME = _CFG.get("community_name", "Claude Malaysia")
FLAG_EMOJI     = _CFG.get("flag_emoji", "🇲🇾")

SLIDE_W = 1080
SLIDE_H = 1350
VIEWPORT_W = 540
VIEWPORT_H = 675
SCALE = SLIDE_W / VIEWPORT_W  # = 2.0


def _img_to_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _amber_line(text: str) -> str:
    """Wrap **bolded** text in amber span."""
    import re
    return re.sub(r"\*\*(.*?)\*\*", r'<span class="amber">\1</span>', text)


def build_html(carousel: dict, image_paths: list[str], out_path: str) -> str:
    """Build the full 10-slide HTML file and return its path."""
    slides_html = []

    # — Slide 1: Cover —
    cover_img = _img_to_b64(image_paths[0]) if image_paths else ""
    slides_html.append(f"""
    <div class="slide cover-slide" style="background-image:url('data:image/jpeg;base64,{cover_img}')">
      <div class="scrim-cover"></div>
      <div class="slide-inner cover-inner">
        <div class="handle">{ACCOUNT_HANDLE}</div>
        <div class="cover-tag">{FLAG_EMOJI} AI NEWS</div>
        <h1 class="cover-h1">{carousel.get('cover_headline','AI NEWS')}</h1>
        <p class="cover-sub">{carousel.get('cover_subheadline','')}</p>
        <div class="swipe-cta">[ SWIPE → ]</div>
        <div class="dots">{_dots(10, 0)}</div>
      </div>
      <div class="arr">›</div>
      <div class="progress-bar" style="width:10%"></div>
    </div>""")

    # — Slides 2–9: Inner —
    inner_slides = carousel.get("slides", [])
    for i, slide in enumerate(inner_slides):
        img_idx = i + 1
        img_b64 = _img_to_b64(image_paths[img_idx]) if img_idx < len(image_paths) else ""
        body = _amber_line(slide.get("body", ""))
        amber = _amber_line(slide.get("amber_line", ""))
        slide_num = slide.get("num", i + 2)
        slide_num_str = f"{slide_num:02d}"
        slides_html.append(f"""
    <div class="slide inner-slide" style="background-image:url('data:image/jpeg;base64,{img_b64}')">
      <div class="scrim-inner"></div>
      <div class="slide-num-bg">{slide_num_str}</div>
      <div class="inner-layout">
        <div class="inner-top">
          <div class="handle-inner">{ACCOUNT_HANDLE}</div>
        </div>
        <div class="inner-mid">
          <div class="label-row">
            <div class="label-bar"></div>
            <div class="slide-label">{slide.get('label','')}</div>
          </div>
          <h2 class="inner-h2">{slide.get('headline','')}</h2>
          <div class="amber-box">{amber}</div>
          <div class="divider"></div>
          <p class="inner-body">{body}</p>
        </div>
        <div class="inner-bot">
          <div class="progress-bar" style="width:{(slide_num/10)*100:.0f}%"></div>
        </div>
      </div>
      <div class="arr">›</div>
    </div>""")

    # — Slide 10: CTA —
    cta_img = _img_to_b64(image_paths[-1]) if len(image_paths) >= 10 else ""
    slides_html.append(f"""
    <div class="slide cta-slide" style="background-image:url('data:image/jpeg;base64,{cta_img}')">
      <div class="scrim-cta"></div>
      <div class="slide-inner cta-inner">
        <div class="handle">{ACCOUNT_HANDLE}</div>
        <div class="cta-flag">{FLAG_EMOJI}</div>
        <h2 class="cta-h2">WANT MORE<br>STORIES LIKE THIS?</h2>
        <div class="cta-btn">Comment <span class="amber">CLAUDE</span></div>
        <p class="cta-desc">Join the {COMMUNITY_NAME} community<br>Get AI news straight to your DMs</p>
        <div class="cta-url">{COMMUNITY_URL}</div>
      </div>
      <div class="progress-bar" style="width:100%"></div>
    </div>""")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#000; font-family:'Plus Jakarta Sans','Inter',sans-serif; overflow:hidden; }}

  .viewport {{ width:{VIEWPORT_W}px; height:{VIEWPORT_H}px; overflow:hidden; position:relative; }}
  .track {{ display:flex; width:{10*VIEWPORT_W}px; transition:transform 0.3s ease; }}

  .slide {{
    width:{VIEWPORT_W}px; height:{VIEWPORT_H}px; flex-shrink:0;
    background-size:cover; background-position:center; position:relative; overflow:hidden;
  }}

  /* ── Scrims ── */
  .scrim-cover {{
    position:absolute; inset:0;
    background:linear-gradient(to top, rgba(0,0,0,0.97) 0%, rgba(0,0,0,0.50) 40%, rgba(0,0,0,0.15) 70%, rgba(0,0,0,0.10) 100%);
  }}
  .scrim-inner {{
    position:absolute; inset:0;
    /* Photo visible at top, darkens in the middle where text lives */
    background:linear-gradient(
      to bottom,
      rgba(0,0,0,0.20) 0%,
      rgba(0,0,0,0.60) 30%,
      rgba(0,0,0,0.78) 60%,
      rgba(0,0,0,0.82) 100%
    );
  }}
  .scrim-cta {{
    position:absolute; inset:0;
    background:rgba(0,0,0,0.85);
  }}

  /* ── Cover ── */
  .slide-inner {{
    position:relative; z-index:2; height:100%;
    display:flex; flex-direction:column; padding:18px 20px 24px;
  }}
  .cover-inner {{ justify-content:flex-end; }}
  .handle {{ font-size:9px; color:rgba(255,255,255,0.40); letter-spacing:0.5px; margin-bottom:auto; }}
  .cover-tag {{
    font-size:10px; font-weight:700; letter-spacing:2px; text-transform:uppercase;
    color:#D97706; background:rgba(217,119,6,0.15); padding:4px 10px; border-radius:20px;
    width:fit-content; margin-bottom:10px;
  }}
  .cover-h1 {{
    font-size:38px; font-weight:800; color:#F5F0E8; line-height:1.08;
    text-transform:uppercase; letter-spacing:-0.5px; margin-bottom:10px;
    text-shadow:0 2px 12px rgba(0,0,0,0.9);
  }}
  .cover-sub {{
    font-size:14px; font-weight:400; color:rgba(255,255,255,0.88);
    line-height:1.5; font-style:italic; margin-bottom:14px;
    text-shadow:0 1px 6px rgba(0,0,0,0.8);
  }}
  .swipe-cta {{
    font-size:10px; font-weight:600; letter-spacing:3px; color:rgba(255,255,255,0.50);
    text-transform:uppercase; margin-bottom:8px;
  }}
  .dots {{ display:flex; gap:4px; }}
  .dot {{ width:5px; height:5px; border-radius:50%; background:rgba(255,255,255,0.3); }}
  .dot.active {{ background:#D97706; width:14px; border-radius:3px; }}

  /* ── Inner slides ── */
  .inner-slide {{ /* no brightness filter */ }}

  /* Big decorative slide number */
  .slide-num-bg {{
    position:absolute; right:-4px; top:10px; z-index:1;
    font-size:120px; font-weight:900; color:rgba(255,255,255,0.06);
    line-height:1; letter-spacing:-4px; pointer-events:none; user-select:none;
  }}

  /* Inner layout — 3 zones: top / mid / bot */
  .inner-layout {{
    position:relative; z-index:2;
    height:100%; display:flex; flex-direction:column;
    padding:16px 22px 0 22px;
  }}
  .inner-top {{
    flex:0 0 auto; margin-bottom:0;
  }}
  .handle-inner {{
    font-size:9px; color:rgba(255,255,255,0.35); letter-spacing:0.5px;
  }}
  .inner-mid {{
    flex:1; display:flex; flex-direction:column; justify-content:center;
    padding:16px 0 12px 0;
  }}
  .inner-bot {{
    flex:0 0 auto; position:relative; height:3px; margin-bottom:0;
  }}

  /* Label row with left accent bar */
  .label-row {{
    display:flex; align-items:center; gap:8px; margin-bottom:12px;
  }}
  .label-bar {{
    width:3px; height:14px; background:#D97706; border-radius:2px; flex-shrink:0;
  }}
  .slide-label {{
    font-size:11px; font-weight:700; letter-spacing:2.5px; text-transform:uppercase;
    color:#F59E0B; text-shadow:0 1px 4px rgba(0,0,0,0.8);
  }}

  /* Headline */
  .inner-h2 {{
    font-size:30px; font-weight:800; color:#fff; line-height:1.18;
    margin-bottom:14px; letter-spacing:-0.3px;
    text-shadow:0 2px 8px rgba(0,0,0,0.9);
  }}

  /* Amber highlight box — dark solid bg so amber text pops on any photo */
  .amber-box {{
    font-size:16px; font-weight:700; color:#FCD34D;
    line-height:1.5; margin-bottom:14px;
    padding:12px 14px; border-left:4px solid #F59E0B;
    background:rgba(0,0,0,0.65); border-radius:0 8px 8px 0;
  }}
  .amber {{ color:#FCD34D; }}

  .divider {{ width:32px; height:2px; background:rgba(255,255,255,0.30); margin-bottom:14px; border-radius:1px; }}

  .inner-body {{
    font-size:16px; font-weight:400; color:rgba(255,255,255,0.92);
    line-height:1.70; text-shadow:0 1px 4px rgba(0,0,0,0.7);
  }}

  /* Progress bar (inside inner-bot) */
  .inner-layout .progress-bar {{
    position:absolute; bottom:0; left:-22px;
    height:2.5px; background:#D97706; z-index:3;
    border-radius:0 2px 2px 0;
  }}

  /* ── CTA slide ── */
  .cta-inner {{ justify-content:center; align-items:center; text-align:center; gap:14px; }}
  .cta-flag {{ font-size:36px; }}
  .cta-h2 {{ font-size:28px; font-weight:800; color:#fff; line-height:1.2; text-shadow:0 2px 8px rgba(0,0,0,0.9); }}
  .cta-btn {{
    font-size:16px; font-weight:800; color:#fff;
    background:rgba(217,119,6,0.25); border:2px solid #F59E0B;
    padding:10px 28px; border-radius:25px; width:fit-content;
  }}
  .cta-desc {{ font-size:13px; color:rgba(255,255,255,0.80); line-height:1.6; }}
  .cta-url {{ font-size:13px; font-weight:700; color:#FCD34D; letter-spacing:0.3px; }}

  /* ── Arrow + global progress bar ── */
  .arr {{
    position:absolute; right:12px; bottom:36px;
    width:34px; height:34px; border-radius:50%;
    background:#D97706; color:#fff; font-size:18px;
    display:flex; align-items:center; justify-content:center;
    z-index:3; box-shadow:0 2px 10px rgba(217,119,6,0.5);
  }}
  /* Cover + CTA progress bar */
  .cover-slide .progress-bar,
  .cta-slide .progress-bar {{
    position:absolute; bottom:0; left:0; height:2.5px;
    background:#D97706; z-index:3; border-radius:0 2px 2px 0;
  }}
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
        f'<div class="dot{"" if i != active else " active"}"></div>'
        for i in range(total)
    )


async def _export_pngs(html_path: str, out_dir: str, n_slides: int = 10) -> list[str]:
    """Use Playwright to export each slide as a PNG."""
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
        await page.wait_for_timeout(1500)

        vp = await page.query_selector(".viewport")
        for i in range(n_slides):
            await page.evaluate(f"go({i})")
            await page.wait_for_timeout(400)
            out_path = f"{out_dir}/slide_{i+1:02d}.png"
            await vp.screenshot(path=out_path)
            paths.append(out_path)
            print(f"[builder] Exported slide {i+1}: {out_path}")

        await browser.close()

    return paths


def export_pngs(html_path: str, out_dir: str, n_slides: int = 10) -> list[str]:
    return asyncio.run(_export_pngs(html_path, out_dir, n_slides))


def run(carousel: dict, image_paths: list[str], run_id: str) -> list[str]:
    """Full build: carousel dict + images → 10 exported PNGs."""
    html_out = f"/tmp/cm_{run_id}.html"
    png_dir = os.path.expanduser(f"~/Downloads/carousels/cm-{run_id}")

    build_html(carousel, image_paths, html_out)
    png_paths = export_pngs(html_out, png_dir)
    print(f"[builder] Done — {len(png_paths)} PNGs in {png_dir}")
    return png_paths
