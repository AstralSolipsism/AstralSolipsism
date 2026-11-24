#!/usr/bin/env python3
"""Generate AstralSolipsism Planar Status HUD SVGs (Dark & Light) synced with live 12-month contributions."""
import json
import os
import sys
import urllib.request
from pathlib import Path


def fetch_contributions(username: str, token: str) -> int:
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
          }
        }
      }
    }
    """
    payload = json.dumps({"query": query, "variables": {"login": username}}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "AstralSolipsism-Status-Sync",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return int(data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"])


def render_segments(x0: int, y: int, filled: int, total: int, color: str, empty_color: str) -> str:
    parts = []
    for i in range(total):
        c = color if i < filled else empty_color
        parts.append(f'<rect x="{x0 + i * 13}" y="{y}" width="10" height="8" rx="1.2" fill="{c}"/>')
    return "".join(parts)


def build_status_svg(contributions: int, theme: str) -> str:
    dark = theme == "dark"
    bg = "#0d1117" if dark else "#ffffff"
    line = "rgba(240,203,122,0.38)" if dark else "rgba(156,105,20,0.40)"
    gold = "#f0cb7a" if dark else "#9c6914"
    tx = "#e6edf3" if dark else "#1b2230"
    mu = "#94a3b8" if dark else "#556070"
    teal = "#7dd3fc" if dark else "#0369a1"
    dash = "#273144" if dark else "#d8d0c3"
    bar_bg = "#1d273b" if dark else "#e3dccd"
    hp_col = "#4ade80" if dark else "#15803d"
    mp_col = "#7dd3fc" if dark else "#0284c7"
    exp_col = "#f0cb7a" if dark else "#b45309"

    exp_filled = min(14, max(4, round((contributions / 4000.0) * 14)))
    exp_text = f"EXP {contributions:,}"

    hp_segs = render_segments(674, 21, 13, 14, hp_col, bar_bg)
    mp_segs = render_segments(674, 47, 13, 14, mp_col, bar_bg)
    exp_segs = render_segments(674, 73, exp_filled, 14, exp_col, bar_bg)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 896 106" width="896" height="106" role="img" aria-label="Planar Status HUD">
  <style>
    .k{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:10.5px;font-weight:700;letter-spacing:1.3px}}
    .v{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;font-weight:600}}
    .m{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;font-weight:500}}
    .q{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;font-style:italic;font-weight:500}}
    .g{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11px;font-weight:700;letter-spacing:.6px}}
  </style>
  <rect width="896" height="106" fill="{bg}"/>
  <line x1="22" y1="6" x2="874" y2="6" stroke="{line}" stroke-width="1"/>
  <line x1="22" y1="100" x2="874" y2="100" stroke="{line}" stroke-width="1"/>
  <rect x="20" y="3.5" width="5" height="5" fill="{gold}" transform="rotate(45 22.5 6)"/>
  <rect x="871" y="3.5" width="5" height="5" fill="{gold}" transform="rotate(45 873.5 6)"/>
  <line x1="538" y1="18" x2="538" y2="88" stroke="{dash}" stroke-width="1" stroke-dasharray="3 3"/>

  <text x="40" y="31" fill="{gold}" class="k">CLASS</text>
  <text x="112" y="31" fill="{tx}" class="v">Builder · Systems &amp; AI</text>

  <text x="40" y="57" fill="{gold}" class="k">DOMAIN</text>
  <text x="112" y="57" fill="{mu}" class="m">Agents &amp; Practical Systems</text>

  <text x="40" y="83" fill="{gold}" class="k">MOTTO</text>
  <text x="112" y="83" fill="{teal}" class="q">"Build quietly, ship clearly."</text>

  <text x="558" y="29" fill="{hp_col}" class="g">HP  CRAFT</text>
  {hp_segs}

  <text x="558" y="55" fill="{mp_col}" class="g">MP  FOCUS</text>
  {mp_segs}

  <text x="558" y="81" fill="{exp_col}" class="g">{exp_text}</text>
  {exp_segs}
</svg>
'''


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    assets_dir = repo_root / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) >= 2 and sys.argv[1].isdigit():
        contributions = int(sys.argv[1])
    else:
        token = os.environ.get("GITHUB_TOKEN", "").strip()
        username = os.environ.get("GITHUB_USERNAME", os.environ.get("GITHUB_REPOSITORY_OWNER", "AstralSolipsism")).strip()
        if not token:
            raise SystemExit("Provide a numeric contribution count argument or set GITHUB_TOKEN.")
        contributions = fetch_contributions(username, token)

    for theme in ("dark", "light"):
        out = assets_dir / f"status-{theme}.svg"
        out.write_text(build_status_svg(contributions, theme), encoding="utf-8")
        print(f"Wrote {out} (contributions={contributions:,})")


if __name__ == "__main__":
    main()
