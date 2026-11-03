"""Rebuild the clickable project cards for the profile README.

Reads the public repos from the GitHub API, draws one card per repo into
assets/cards/<repo>.svg, writes the grouped card grid into the README (between
the PROJECTS markers) and refreshes the project count and badge (COUNT, BADGE).
Run by .github/workflows/update-profile.yml.

Local test without the API:  python scripts/build_profile.py --local repos.json
"""

import hashlib
import json
import os
import re
import sys
import textwrap
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

USER = os.environ.get("PROFILE_USER", "judie-paul")
ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "assets" / "cards"
README = ROOT / "README.md"

# Repos to leave out (duplicates / empty repos).
EXCLUDE = {"Airtable-contractor-App", "Airtable-contractor-application-"}

# Card text for each repo: (display name, one-line pitch). New repos fall back to
# their GitHub name and description.
CARD_TEXT = {
    "rubricops": ("RubricOps", "Versioned rubrics, independent scoring, reviewer audits and adjudication, with Cohen's kappa and overturn rates."),
    "judgecheck": ("JudgeCheck", "How far can LLM judges be trusted? Agreement, position bias and verbosity bias against MT-Bench experts."),
    "labellint": ("LabelLint", "Offline annotation audit that flags contradictions, duplicate rationales and speed anomalies, with evidence."),
    "patchbench": ("PatchBench", "SWE-bench-style runner: does a patch fix the issue without breaking tests? Checked in isolated Docker."),
    "reference-based-revision-tool": ("Revision Tool", "Answers past exam questions from your own notes first, and checks every cited quote against the page."),
    "citewise-ai": ("CiteWise AI", "Finds real academic references via Crossref and OpenAlex and formats APA 7 or Harvard. Never invents a DOI."),
    "github-resume-generator": ("GitHub → Resume", "Turns a public GitHub profile into an editable, ATS-friendly resume with validated AI output and PDF export."),
    "shoebox": ("Shoebox", "Single-vendor shoe store in one Go binary: filters, size and colour stock, cart, checkout, vendor dashboard."),
    "school-management-system": ("School Management", "Self-contained web app for students, exam results and fees, with staff and parent access."),
    "contractor-application": ("Contractor Application", "Airtable-backed pipeline for collecting and processing contractor applications."),
}

GROUP = {
    "rubricops": "eval", "judgecheck": "eval", "labellint": "eval", "patchbench": "eval",
    "reference-based-revision-tool": "ai", "citewise-ai": "ai", "github-resume-generator": "ai",
    "shoebox": "app", "school-management-system": "app", "contractor-application": "app",
}
GROUPS = [  # key, heading, accent, gradient end
    ("eval", "🧪 AI evaluation & data quality", "#c4a7ff", "#8b6cf0"),
    ("ai", "📚 Grounded AI apps", "#f0abfc", "#c026d3"),
    ("app", "🛠️ Web apps", "#a5b4fc", "#6366f1"),
]
EVAL_WORDS = re.compile(r"\b(evaluat\w*|judge\w*|rubric\w*|annotat\w*|label\w*|bench\w*|agreement)\b", re.I)
AI_WORDS = re.compile(r"\b(ai|llm|llms|claude|gemini|openai|gpt)\b", re.I)
LANG_COLORS = {"Python": "#3572A5", "Go": "#00ADD8", "TypeScript": "#3178c6",
               "JavaScript": "#f1e05a", "HTML": "#e34c26", "CSS": "#563d7c"}
FONT = "'Segoe UI',-apple-system,'Helvetica Neue',Arial,sans-serif"
CARD_W, WIDE_W, CH = 420, 856, 150


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


def card_svg(repo, accent, deep, index, wide=False):
    CW = WIDE_W if wide else CARD_W
    title, pitch = CARD_TEXT.get(repo["name"], (repo["name"], repo.get("description") or ""))
    lines = textwrap.wrap(pitch, 118 if wide else 58)[:3]
    lang = repo.get("language") or ""
    desc = "".join(
        f'<text x="24" y="{76 + i * 19}" fill="#c3b6e6" font-size="13">{escape(l)}</text>'
        for i, l in enumerate(lines))
    lang_el = ""
    if lang:
        lang_el = (f'<circle cx="30" cy="{CH - 22}" r="5" fill="{LANG_COLORS.get(lang, "#8b8ba7")}"/>'
                   f'<text x="42" y="{CH - 18}" fill="#a99cc8" font-size="12">{escape(lang)}</text>')
    live = ""
    if repo.get("homepage"):
        live = (f'<circle class="lv" cx="{CW - 92}" cy="{CH - 22}" r="4" fill="{accent}"/>'
                f'<text x="{CW - 82}" y="{CH - 18}" fill="{accent}" font-size="12">live demo</text>')
    delay = -(index * 1.3)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}" font-family="{FONT}" role="img" aria-label="{escape(title)}">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16102e"/><stop offset="1" stop-color="#0f0b1e"/></linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{accent}"/><stop offset="1" stop-color="{deep}"/></linearGradient>
<linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="{accent}" stop-opacity="0"/><stop offset=".5" stop-color="{accent}" stop-opacity=".9"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></linearGradient>
<clipPath id="c"><rect width="{CW}" height="{CH}" rx="14"/></clipPath>
</defs>
<style>
.s{{animation:mv 6s ease-in-out {delay:.1f}s infinite}}
@keyframes mv{{0%{{transform:translateX(-160px)}}60%,100%{{transform:translateX({CW + 20}px)}}}}
.lv{{animation:pu 2s ease-in-out infinite}}
@keyframes pu{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
</style>
<g clip-path="url(#c)">
<rect width="{CW}" height="{CH}" fill="url(#bg)"/>
<rect width="4" height="{CH}" fill="url(#edge)"/>
<rect class="s" x="0" y="0" width="140" height="2" fill="url(#sh)"/>
</g>
<rect x=".5" y=".5" width="{CW - 1}" height="{CH - 1}" rx="14" fill="none" stroke="#3b2a6b"/>
<text x="24" y="42" fill="#ede7ff" font-size="19" font-weight="700">{escape(title)}</text>
<text x="{CW - 24}" y="42" fill="{accent}" font-size="16" text-anchor="end">↗</text>
{desc}
{lang_el}{live}
</svg>
'''


def build(repos):
    """Write every card and return the README HTML for the grid."""
    CARDS.mkdir(parents=True, exist_ok=True)
    for old in CARDS.glob("*.svg"):
        old.unlink()
    html, index = [], 0
    for key, heading, accent, deep in GROUPS:
        order = list(CARD_TEXT)
        group = sorted((r for r in repos if group_of(r) == key),
                       key=lambda r: order.index(r["name"]) if r["name"] in order else len(order))
        if not group:
            continue
        html.append(f"\n**{heading}**\n\n<p align=\"center\">")
        for n, repo in enumerate(group):
            index += 1
            # An odd card at the end of a group spans the full row instead of sitting alone
            wide = len(group) % 2 == 1 and n == len(group) - 1
            svg = card_svg(repo, accent, deep, index, wide)
            path = CARDS / f'{repo["name"]}.svg'
            path.write_text(svg, encoding="utf-8")
            v = hashlib.sha1(svg.encode()).hexdigest()[:7]  # new address when a card changes
            title = CARD_TEXT.get(repo["name"], (repo["name"],))[0]
            html.append(f'  <a href="https://github.com/{USER}/{repo["name"]}"><img src="assets/cards/{repo["name"]}.svg?v={v}" '
                        f'width="{"98.8%" if wide else "49%"}" alt="{escape(title)}" /></a>')
        html.append("</p>\n")
    return "\n".join(html)


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
    grid = build(repos)

    text = README.read_text(encoding="utf-8")
    text = replace_between(text, "PROJECTS", grid)
    text = replace_between(text, "COUNT", str(len(repos)))
    badge = (
        f'<a href="https://github.com/{USER}?tab=repositories"><img src="https://img.shields.io/badge/'
        f'projects-{len(repos)}_public-5b3fa0?style=flat-square&labelColor=0f0b1e" /></a>'
    )
    text = replace_between(text, "BADGE", badge)
    README.write_text(text, encoding="utf-8")
    print(f"Built cards for {len(repos)} repos.")


if __name__ == "__main__":
    main()
