"""Generate the observatory header and footer SVGs in img/. Run: python .github/scripts/make_art.py img"""
import random, sys
from pathlib import Path

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

SPACE, TWILIGHT, GROUND = "#0B1026", "#1E2A5A", "#070B1C"
GOLD, TEAL, VIOLET, MIST = "#F5C451", "#5EEAD4", "#C084FC", "#A5B4FC"
FONT = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"

STYLE = """
  <style>
    .tw { animation: tw 4s ease-in-out infinite; }
    @keyframes tw { 0%, 100% { opacity: .25 } 50% { opacity: 1 } }
    @media (prefers-reduced-motion: reduce) { .tw { animation: none; opacity: .8 } }
  </style>"""


def stars(rng, w, h, n, avoid=None):
    out = []
    for i in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        if avoid and avoid[0] < x < avoid[2] and avoid[1] < y < avoid[3]:
            continue
        r = rng.choice([0.6, 0.8, 0.8, 1.0, 1.2, 1.6])
        fill = GOLD if rng.random() < 0.12 else "#E2E8F0"
        cls = f' class="tw" style="animation-delay:{rng.uniform(0, 4):.2f}s"' if rng.random() < 0.35 else ""
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" opacity="{rng.uniform(.35, .9):.2f}"{cls}/>')
    return "\n    ".join(out)


def header():
    rng = random.Random(1106)
    w, h = 1200, 320
    # Cassiopeia's W, placed over the observatory.
    cas = [(870, 70), (925, 112), (972, 84), (1030, 120), (1082, 72)]
    line = " ".join(f"{x},{y}" for x, y in cas)
    cas_stars = "\n    ".join(
        f'<circle cx="{x}" cy="{y}" r="9" fill="url(#glow)"/><circle cx="{x}" cy="{y}" r="2.6" fill="{GOLD}"/>'
        for x, y in cas)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Abhishek Kr. Chauhan — DevOps and AI engineer in Bengaluru, India">{STYLE}
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{SPACE}"/>
      <stop offset="1" stop-color="{TWILIGHT}"/>
    </linearGradient>
    <radialGradient id="nebula" cx="0.82" cy="0.35" r="0.55">
      <stop offset="0" stop-color="{VIOLET}" stop-opacity=".30"/>
      <stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="aurora" cx="0.08" cy="0.9" r="0.6">
      <stop offset="0" stop-color="{TEAL}" stop-opacity=".16"/>
      <stop offset="1" stop-color="{TEAL}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="glow">
      <stop offset="0" stop-color="{GOLD}" stop-opacity=".55"/>
      <stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#sky)"/>
  <rect width="{w}" height="{h}" fill="url(#nebula)"/>
  <rect width="{w}" height="{h}" fill="url(#aurora)"/>
  <g>
    {stars(rng, w, 250, 130, avoid=(60, 80, 760, 230))}
  </g>
  <polyline points="{line}" fill="none" stroke="{GOLD}" stroke-opacity=".45" stroke-width="1.2" stroke-dasharray="3 5"/>
  <g>
    {cas_stars}
  </g>
  <text x="1090" y="150" text-anchor="end" font-family="{FONT}" font-size="13" fill="{GOLD}" fill-opacity=".6" letter-spacing="1">Cassiopeia</text>

  <text x="80" y="140" font-family="{FONT}" font-size="64" font-weight="700" fill="#F8FAFC" letter-spacing="-1">Abhishek Kr. Chauhan</text>
  <text x="82" y="184" font-family="{FONT}" font-size="24" fill="{MIST}">DevOps and AI engineer in Bengaluru, India</text>
  <rect x="82" y="204" width="56" height="3" rx="1.5" fill="{GOLD}"/>

  <!-- horizon, with the observatory -->
  <path d="M0 292 C 220 262 420 278 640 284 S 980 250 1200 268 L 1200 320 L 0 320 Z" fill="#0E1532"/>
  <path d="M0 304 C 260 288 520 300 760 298 S 1060 284 1200 292 L 1200 320 L 0 320 Z" fill="{GROUND}"/>
  <g fill="{GROUND}">
    <rect x="938" y="246" width="88" height="56"/>
    <path d="M934 248 A 48 48 0 0 1 1030 248 Z"/>
  </g>
  <path d="M975 202 L 989 202 L 991 248 L 973 248 Z" fill="{GOLD}" fill-opacity=".85"/>
  <rect x="962" y="262" width="12" height="14" rx="2" fill="{GOLD}" fill-opacity=".7"/>
</svg>
"""
    (OUT / "header.svg").write_text(svg, encoding="utf-8")


def footer():
    rng = random.Random(373)
    w, h = 1200, 140
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Thanks for stopping by. Clear skies.">{STYLE}
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{TWILIGHT}"/>
      <stop offset="1" stop-color="{SPACE}"/>
    </linearGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="url(#sky)"/>
  <g>
    {stars(rng, w, 90, 70, avoid=(380, 30, 820, 90))}
  </g>
  <text x="600" y="66" text-anchor="middle" font-family="{FONT}" font-size="20" fill="{MIST}">Thanks for stopping by. Clear skies.</text>
  <path d="M0 116 C 240 100 460 112 700 110 S 1040 98 1200 106 L 1200 140 L 0 140 Z" fill="{GROUND}"/>
</svg>
"""
    (OUT / "footer.svg").write_text(svg, encoding="utf-8")


header()
footer()
print("wrote", *sorted(p.name for p in OUT.iterdir()))
