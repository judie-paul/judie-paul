"""Draw a dated GitHub contribution calendar as SVG (light + dark).

Runs inside GitHub Actions. Reads GITHUB_TOKEN and GITHUB_USER from the
environment, or a local JSON file passed as the first argument (for testing).
"""
import datetime as dt
import json
import os
import sys
import urllib.request

OUT_DIR = os.environ.get("OUT_DIR", "dist")

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}"""

THEMES = {
    "dark": {
        "bg": "#0d1117", "text": "#8b949e", "title": "#e6edf3",
        "levels": ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
    },
    "light": {
        "bg": "#ffffff", "text": "#57606a", "title": "#1f2328",
        "levels": ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
    },
}
LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
         "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

CELL, GAP = 11, 3
STEP = CELL + GAP
LEFT, TOP = 34, 48


def fetch(login, token):
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    if "errors" in data:
        sys.exit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(cal, theme):
    t = THEMES[theme]
    weeks = cal["weeks"]
    width = LEFT + len(weeks) * STEP + 10
    height = TOP + 7 * STEP + 34
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">',
        "<style>.c{opacity:0;animation:f .5s ease-out forwards}"
        "@keyframes f{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:scale(1)}}"
        "@media (prefers-reduced-motion: reduce){.c{animation:none;opacity:1}}</style>",
        f'<rect width="100%" height="100%" rx="8" fill="{t["bg"]}"/>',
        f'<text x="{LEFT}" y="22" font-size="14" font-weight="600" fill="{t["title"]}">'
        f'{cal["totalContributions"]:,} contributions in the last year</text>',
    ]

    # Month labels: where a week contains the 1st of a month (or the first week)
    last_month, last_x = None, -99
    for i, w in enumerate(weeks):
        first = dt.date.fromisoformat(w["contributionDays"][0]["date"])
        x = LEFT + i * STEP
        if first.month != last_month:
            last_month = first.month
            if x - last_x >= 3 * STEP and i < len(weeks) - 2:  # avoid overlapping labels
                out.append(f'<text x="{x}" y="{TOP - 8}" font-size="10" '
                           f'fill="{t["text"]}">{first.strftime("%b")}</text>')
                last_x = x

    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="2" y="{TOP + row * STEP + 9}" font-size="9" '
                   f'fill="{t["text"]}">{name}</text>')

    for i, w in enumerate(weeks):
        for d in w["contributionDays"]:
            day = dt.date.fromisoformat(d["date"])
            row = (day.weekday() + 1) % 7  # Sunday on top, like GitHub
            x, y = LEFT + i * STEP, TOP + row * STEP
            n = d["contributionCount"]
            label = f'{n} contribution{"s" if n != 1 else ""} on {day.strftime("%b %-d, %Y")}'
            fill = t["levels"][LEVEL.get(d["contributionLevel"], 0)]
            out.append(
                f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{fill}" style="animation-delay:{i * 0.02:.2f}s;'
                f'transform-origin:{x + CELL / 2}px {y + CELL / 2}px">'
                f'<title>{esc(label)}</title></rect>')

    # Legend
    ly = TOP + 7 * STEP + 14
    lx = width - 10 - 5 * STEP - 62
    out.append(f'<text x="{lx}" y="{ly + 9}" font-size="10" fill="{t["text"]}">Less</text>')
    for k, c in enumerate(t["levels"]):
        out.append(f'<rect x="{lx + 28 + k * STEP}" y="{ly}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
    out.append(f'<text x="{lx + 32 + 5 * STEP}" y="{ly + 9}" font-size="10" fill="{t["text"]}">More</text>')

    out.append("</svg>")
    return "\n".join(out)


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            cal = json.load(f)
    else:
        cal = fetch(os.environ["GITHUB_USER"], os.environ["GITHUB_TOKEN"])
    os.makedirs(OUT_DIR, exist_ok=True)
    for theme, name in (("light", "calendar.svg"), ("dark", "calendar-dark.svg")):
        with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as f:
            f.write(render(cal, theme))
    print(f"Wrote calendar for {cal['totalContributions']} contributions")


if __name__ == "__main__":
    main()
