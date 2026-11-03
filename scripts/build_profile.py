"""Rebuild the floating-bubbles project graphic for the profile README.

Reads the public repos from the GitHub API, draws one bubble per repo into
assets/repo-bubbles.svg, and refreshes the project count and badge in the README
(between the COUNT and BADGE markers). Run by .github/workflows/update-profile.yml.

Local test without the API:  python scripts/build_profile.py --local repos.json
"""

import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

USER = os.environ.get("PROFILE_USER", "judie-paul")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "repo-bubbles.svg"
README = ROOT / "README.md"

# Repos to leave out of the graphic (duplicates / empty repos).
EXCLUDE = {"Airtable-contractor-App", "Airtable-contractor-application-"}

# Which group each repo goes in. New repos not listed here are sorted by keywords.
GROUP = {
    "rubricops": "eval", "judgecheck": "eval", "labellint": "eval", "patchbench": "eval",
    "reference-based-revision-tool": "ai", "citewise-ai": "ai", "github-resume-generator": "ai",
    "shoebox": "app", "school-management-system": "app", "contractor-application": "app",
}

# The small line under a repo's name.
SUBTITLES = {
    "rubricops": "rubrics · kappa",
    "judgecheck": "LLM-judge bias",
    "labellint": "label auditing",
    "patchbench": "patch evaluation",
    "reference-based-revision-tool": "cited exam answers",
    "citewise-ai": "real references",
    "github-resume-generator": "GitHub → resume",
    "shoebox": "Go · SQLite store",
    "school-management-system": "Go web app",
    "contractor-application": "Airtable pipeline",
}

EVAL_WORDS = re.compile(r"\b(evaluat\w*|judge\w*|rubric\w*|annotat\w*|label\w*|bench\w*|agreement)\b", re.I)
AI_WORDS = re.compile(r"\b(ai|llm|llms|claude|gemini|openai|gpt)\b", re.I)

GREEN, AQUA, VIOLET = "#c4a7ff", "#f0abfc", "#a5b4fc"
FONT = "'Segoe UI',-apple-system,'Helvetica Neue',Arial,sans-serif"
R, W = 72, 800
PER_ROW, GAP, ROW_H = 4, 180, 170
APP_PER_ROW, APP_GAP = 3, 210


def fetch_repos():
    """Public, non-fork, non-archived repos, most recently pushed first."""
    url = f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed"
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        repos = json.load(response)
    return [r for r in repos if not (r["fork"] or r["archived"] or r["private"]
                                     or r["name"] == USER or r["name"] in EXCLUDE)]


def group_of(repo):
    if repo["name"] in GROUP:
        return GROUP[repo["name"]]
    text = f'{repo["name"]} {repo.get("description") or ""} {" ".join(repo.get("topics", []))}'
    if EVAL_WORDS.search(text):
        return "eval"
    if AI_WORDS.search(text):
        return "ai"
    return "app"


def subtitle(repo):
    return SUBTITLES.get(repo["name"]) or repo.get("language") or ""


def name_lines(name, limit=16):
    parts = name.split("-")
    lines, current = [], ""
    for i, part in enumerate(parts):
        piece = part + ("-" if i < len(parts) - 1 else "")
        if current and len(current + piece) > limit:
            lines.append(current)
            current = piece
        else:
            current += piece
    lines.append(current)
    return lines


def rows(items, per_row, gap, y0):
    """Centre each row of items on the canvas; returns (item, x, y) tuples."""
    placed = []
    for r in range(0, len(items), per_row):
        chunk = items[r:r + per_row]
        start = W / 2 - gap * (len(chunk) - 1) / 2
        for i, item in enumerate(chunk):
            placed.append((item, round(start + i * gap), y0 + (r // per_row) * ROW_H))
    return placed


def bubble(index, repo, x, y, kind):
    ring, halo = {"eval": ("rG", "hG"), "ai": ("rA", "hA"), "app": ("rV", "hV")}[kind]
    lines = name_lines(repo["name"])
    sub = subtitle(repo)
    total = len(lines) * 17 + (21 if sub else 0)
    top = -total / 2
    text = "".join(
        f'<text x="0" y="{top + (j + 1) * 17 - 3:.1f}" text-anchor="middle" fill="#fff" font-size="14" font-weight="700">{escape(t)}</text>'
        for j, t in enumerate(lines)
    )
    if sub:
        text += f'<text x="0" y="{top + len(lines) * 17 + 19:.1f}" text-anchor="middle" fill="#c3b6e6" font-size="11">{escape(sub)}</text>'
    live = ""
    if repo.get("homepage"):
        live = f'<circle class="lv" cx="{R * 0.71:.0f}" cy="{-R * 0.71:.0f}" r="6" fill="{GREEN}" stroke="#0d0a1c" stroke-width="2.5"/>'
    css = f".b{index}{{animation:fl {6 + (index % 4) * 0.4:.1f}s ease-in-out {-index * 0.9:.1f}s infinite}}"
    shape = (
        f'<g transform="translate({x} {y})"><g class="b{index}">'
        f'<circle r="{R + 16}" fill="url(#{halo})"/>'
        f'<circle r="{R}" fill="url(#glass)" stroke="url(#{ring})" stroke-width="2.5"/>{text}{live}</g></g>'
    )
    return css, shape


def section(y, color, label):
    width = len(label) * 8.6 + 22
    return (
        f'<circle cx="46" cy="{y - 5}" r="5" fill="{color}"/>'
        f'<text x="60" y="{y}" fill="{color}" font-size="15" font-weight="700">{escape(label)}</text>'
        f'<line x1="{60 + width:.0f}" y1="{y - 5}" x2="760" y2="{y - 5}" stroke="#fff" stroke-opacity=".12"/>'
    )


def build_svg(repos):
    groups = {k: [r for r in repos if group_of(r) == k] for k in ("eval", "ai", "app")}
    live_total = sum(1 for r in repos if r.get("homepage"))
    css, shapes, labels = [], [], []
    y, index = 135, 0
    for kind, per_row, gap, color, title in (
        ("eval", PER_ROW, GAP, GREEN, "AI evaluation & data quality"),
        ("ai", APP_PER_ROW, APP_GAP, AQUA, "Grounded AI apps · no made-up sources"),
        ("app", APP_PER_ROW, APP_GAP, VIOLET, "Web apps"),
    ):
        group = groups[kind]
        if not group:
            continue
        labels.append(section(y, color, title))
        for repo, x, cy in rows(group, per_row, gap, y + 90):
            index += 1
            c, s = bubble(index, repo, x, cy, kind)
            css.append(c)
            shapes.append(s)
        y += 90 + ((len(group) - 1) // per_row) * ROW_H + 125
    height = y - 20
    sub = f"{len(repos)} public repos" + (f" · {live_total} live" if live_total else "")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" height="{height}" font-family="{FONT}" role="img" aria-label="{len(repos)} public repositories as floating bubbles">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d0a1c"/><stop offset="1" stop-color="#1d1540"/></linearGradient>
<radialGradient id="glass" cx=".32" cy=".25" r=".95"><stop offset="0" stop-color="#2b2058"/><stop offset="1" stop-color="#110c26"/></radialGradient>
<linearGradient id="rG" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e9ddff"/><stop offset="1" stop-color="#8b6cf0"/></linearGradient>
<linearGradient id="rA" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fbe2ff"/><stop offset="1" stop-color="#c026d3"/></linearGradient>
<linearGradient id="rV" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#dbe1ff"/><stop offset="1" stop-color="#6366f1"/></linearGradient>
<radialGradient id="hG"><stop offset=".7" stop-color="{GREEN}" stop-opacity=".16"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
<radialGradient id="hA"><stop offset=".7" stop-color="{AQUA}" stop-opacity=".16"/><stop offset="1" stop-color="{AQUA}" stop-opacity="0"/></radialGradient>
<radialGradient id="hV"><stop offset=".7" stop-color="{VIOLET}" stop-opacity=".18"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
</defs>
<style>
@keyframes fl{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-7px)}}}}
{chr(10).join(css)}
.lv{{animation:pu 2s ease-in-out infinite}}
@keyframes pu{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
@media (prefers-reduced-motion:reduce){{[class^="b"],.lv{{animation:none}}}}
</style>
<rect width="{W}" height="{height}" rx="22" fill="url(#bg)"/>
<text x="40" y="58" fill="#fff" font-size="28" font-weight="800">Projects</text>
<text x="40" y="82" fill="#c3b6e6" font-size="14">{escape(sub)}</text>
{chr(10).join(labels)}
{chr(10).join(shapes)}
</svg>
'''


def replace_between(text, marker, content):
    pattern = re.compile(rf"(<!-- {marker}:START -->)(.*?)(<!-- {marker}:END -->)", re.S)
    if not pattern.search(text):
        print(f"Note: README has no {marker} markers, skipping.")
        return text
    return pattern.sub(lambda m: m.group(1) + content + m.group(3), text)


def main():
    if "--local" in sys.argv:
        with open(sys.argv[sys.argv.index("--local") + 1], encoding="utf-8") as f:
            repos = [r for r in json.load(f) if r["name"] not in EXCLUDE]
    else:
        repos = fetch_repos()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build_svg(repos), encoding="utf-8")

    text = README.read_text(encoding="utf-8")
    text = replace_between(text, "COUNT", str(len(repos)))
    badge = (
        f'<a href="https://github.com/{USER}?tab=repositories"><img src="https://img.shields.io/badge/'
        f'projects-{len(repos)}_public-5b3fa0?style=flat-square&labelColor=0f0b1e" /></a>'
    )
    text = replace_between(text, "BADGE", badge)
    README.write_text(text, encoding="utf-8")
    print(f"Built bubbles for {len(repos)} repos.")


if __name__ == "__main__":
    main()
