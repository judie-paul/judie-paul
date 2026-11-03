"""Draw GitHub contribution calendars by calendar year, as SVG (light + dark).

Writes, into OUT_DIR:
  calendar.svg / calendar-dark.svg            -> this year (Jan 1 to Dec 31)
  calendar-prev.svg / calendar-prev-dark.svg  -> last year

Runs inside GitHub Actions with GITHUB_TOKEN and GITHUB_USER set.
For a local test without the API, run:  python calendar.py --fake
"""
import datetime as dt
import json
import os
import random
import sys
import urllib.error
import urllib.request

OUT_DIR = os.environ.get("OUT_DIR", "dist")

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}"""

THEMES = {
    "dark": {
        "bg": "#0d1117", "text": "#8b949e", "title": "#e6edf3", "future": "#30363d",
        "levels": ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
    },
    "light": {
        "bg": "#ffffff", "text": "#57606a", "title": "#1f2328", "future": "#d0d7de",
        "levels": ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
    },
}
LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
         "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

CELL, GAP = 11, 3
STEP = CELL + GAP
LEFT, TOP = 34, 48


def fetch(login, token, year):
    variables = {"login": login,
                 "from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"}
    body = json.dumps({"query": QUERY, "variables": variables}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"GitHub API returned HTTP {e.code}: {e.read().decode(errors='replace')[:500]}")
    if "errors" in data:
        sys.exit(f"GraphQL error: {data['errors']}")
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = {d["date"]: d for w in cal["weeks"] for d in w["contributionDays"]}
    return cal["totalContributions"], days


def fake(year, today):
    random.seed(year)
    days, total = {}, 0
    d = dt.date(year, 1, 1)
    lv = list(LEVEL)
    while d.year == year and d <= today:
        n = random.choice([0, 0, 0, 1, 2, 5, 9]) if d.month >= 8 else 0
        total += n
        days[d.isoformat()] = {"date": d.isoformat(), "contributionCount": n,
                               "contributionLevel": lv[min(4, (n + 2) // 3)]}
        d += dt.timedelta(1)
    return total, days


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt(d):
    return f"{d.strftime('%b')} {d.day}"


def render(year, total, days, today, theme):
    t = THEMES[theme]
    jan1, dec31 = dt.date(year, 1, 1), dt.date(year, 12, 31)
    grid_start = jan1 - dt.timedelta(days=(jan1.weekday() + 1) % 7)  # Sunday on/before Jan 1
    n_weeks = (dec31 - grid_start).days // 7 + 1
    width = LEFT + n_weeks * STEP + 10
    height = TOP + 7 * STEP + 34

    last_day = min(today, dec31)
    span = f"{fmt(jan1)} – {fmt(last_day)}, {year}"
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">',
        "<style>.c{opacity:0;animation:f .5s ease-out forwards}"
        "@keyframes f{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:scale(1)}}"
        "@media (prefers-reduced-motion: reduce){.c{animation:none;opacity:1}}</style>",
        f'<rect width="100%" height="100%" rx="8" fill="{t["bg"]}"/>',
        f'<text x="{LEFT}" y="22" font-size="14" font-weight="600" fill="{t["title"]}">'
        f'{total:,} contributions in {year}</text>',
        f'<text x="{width - 10}" y="22" font-size="11" text-anchor="end" fill="{t["text"]}">{span}</text>',
    ]

    # Month labels above the week that holds the 1st of each month
    for m in range(1, 13):
        first = dt.date(year, m, 1)
        col = (first - grid_start).days // 7
        if col < n_weeks - 1:
            out.append(f'<text x="{LEFT + col * STEP}" y="{TOP - 8}" font-size="10" '
                       f'fill="{t["text"]}">{first.strftime("%b")}</text>')

    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="2" y="{TOP + row * STEP + 9}" font-size="9" '
                   f'fill="{t["text"]}">{name}</text>')

    day = jan1
    while day <= dec31:
        col = (day - grid_start).days // 7
        row = (day.weekday() + 1) % 7  # Sunday on top, like GitHub
        x, y = LEFT + col * STEP, TOP + row * STEP
        if day > today:  # rest of the year: outlined, not filled
            out.append(f'<rect x="{x + .5}" y="{y + .5}" width="{CELL - 1}" height="{CELL - 1}" rx="2" '
                       f'fill="none" stroke="{t["future"]}" stroke-opacity=".6"/>')
        else:
            d = days.get(day.isoformat(), {"contributionCount": 0, "contributionLevel": "NONE"})
            n = d["contributionCount"]
            label = f'{n} contribution{"s" if n != 1 else ""} on {fmt(day)}, {year}'
            fill = t["levels"][LEVEL.get(d["contributionLevel"], 0)]
            out.append(
                f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{fill}" style="animation-delay:{col * 0.02:.2f}s;'
                f'transform-origin:{x + CELL / 2}px {y + CELL / 2}px">'
                f'<title>{esc(label)}</title></rect>')
        day += dt.timedelta(1)

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
    today = dt.datetime.now(dt.timezone.utc).date()
    os.makedirs(OUT_DIR, exist_ok=True)
    for year, prefix in ((today.year, "calendar"), (today.year - 1, "calendar-prev")):
        if "--fake" in sys.argv:
            total, days = fake(year, today)
        else:
            total, days = fetch(os.environ["GITHUB_USER"], os.environ["GITHUB_TOKEN"], year)
        for theme, suffix in (("light", ""), ("dark", "-dark")):
            with open(os.path.join(OUT_DIR, f"{prefix}{suffix}.svg"), "w", encoding="utf-8") as f:
                f.write(render(year, total, days, today, theme))
        print(f"{year}: {total} contributions")


if __name__ == "__main__":
    main()
