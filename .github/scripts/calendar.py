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
        "bg": "#0f0b1e", "text": "#a99cc8", "title": "#ede7ff", "future": "#3a3054",
        "levels": ["#1c1630", "#3b2a6b", "#5b3fa0", "#8b6cf0", "#c4a7ff"],
    },
    "light": {
        "bg": "#ffffff", "text": "#57606a", "title": "#1f2328", "future": "#d0d7de",
        "levels": ["#ebedf0", "#e4d9ff", "#c4a7ff", "#9f7aea", "#6b46c1"],
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
    all_days = {}
    for year, prefix in ((today.year, "calendar"), (today.year - 1, "calendar-prev")):
        if "--fake" in sys.argv:
            total, days = fake(year, today)
        else:
            total, days = fetch(os.environ["GITHUB_USER"], os.environ["GITHUB_TOKEN"], year)
        all_days.update(days)
        for theme, suffix in (("light", ""), ("dark", "-dark")):
            with open(os.path.join(OUT_DIR, f"{prefix}{suffix}.svg"), "w", encoding="utf-8") as f:
                f.write(render(year, total, days, today, theme))
        print(f"{year}: {total} contributions")
    for theme, suffix in (("light", ""), ("dark", "-dark")):
        with open(os.path.join(OUT_DIR, f"training{suffix}.svg"), "w", encoding="utf-8") as f:
            f.write(render_training(all_days, today, theme))
    print("training panel written")


# ---------------------------------------------------------------- training-run panel
TRAIN = {
    "dark": {"bg0": "#0f0b1e", "bg1": "#1b1238", "card": "#16102e", "line": "#3b2a6b", "grid": "#2a2050",
             "lav": "#c4a7ff", "orchid": "#e879f9", "pink": "#f0abfc", "soft": "#c3b6e6", "dim": "#a99cc8",
             "title": "#ede7ff", "bar": "#5b3fa0"},
    "light": {"bg0": "#ffffff", "bg1": "#f6f1ff", "card": "#f3edff", "line": "#d9ccf5", "grid": "#ece4fb",
              "lav": "#7c5ce6", "orchid": "#c026d3", "pink": "#a21caf", "soft": "#4b3f6b", "dim": "#6e6390",
              "title": "#1f1535", "bar": "#c4a7ff"},
}
WINDOW = 90  # days shown in the chart


def streaks(counts):
    """counts: list of daily counts, oldest first, ending today. Returns (current, longest, longest_end_index)."""
    longest = run = 0
    end = -1
    for i, n in enumerate(counts):
        run = run + 1 if n else 0
        if run > longest:
            longest, end = run, i
    cur = 0
    i = len(counts) - 1
    if counts and counts[-1] == 0:  # today not counted yet: streak still alive from yesterday
        i -= 1
    while i >= 0 and counts[i]:
        cur += 1
        i -= 1
    return cur, longest, end


def render_training(days, today, theme):
    c = TRAIN[theme]
    W, H = 1000, 395
    # full daily history (for totals and streaks) and the chart window
    first = min((dt.date.fromisoformat(k) for k, v in days.items() if v["contributionCount"]), default=today)
    span = (today - first).days + 1
    hist = [days.get((first + dt.timedelta(i)).isoformat(), {"contributionCount": 0})["contributionCount"]
            for i in range(span)]
    total = sum(hist)
    active = sum(1 for n in hist if n)
    cur, longest, _ = streaks(hist)
    # Chart window: up to WINDOW days, starting a little before the first activity in that range
    start = today - dt.timedelta(days=WINDOW - 1)
    recent = [start + dt.timedelta(i) for i in range(WINDOW)
              if days.get((start + dt.timedelta(i)).isoformat(), {"contributionCount": 0})["contributionCount"]]
    if recent:
        start = max(start, min(recent[0] - dt.timedelta(days=10), today - dt.timedelta(days=29)))
    n_days = (today - start).days + 1
    win = [days.get((start + dt.timedelta(i)).isoformat(), {"contributionCount": 0})["contributionCount"]
           for i in range(n_days)]
    before = total - sum(win)
    cum, run = [], before
    for n in win:
        run += n
        cum.append(run)
    gained = sum(win)
    peak_i = max(range(n_days), key=lambda i: win[i])

    # chart geometry
    cx0, cy0, cw, ch = 60, 96, 600, 190
    ymin, ymax = before, max(cum[-1], before + 1)
    pad = (ymax - ymin) * .08 or 1
    ymax += pad

    def X(i):
        return cx0 + i * cw / (n_days - 1)

    def Y(v):
        return cy0 + ch - (v - ymin) / (ymax - ymin) * ch

    line = " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(cum))
    area = line + f" L{X(n_days - 1):.1f},{cy0 + ch} L{X(0):.1f},{cy0 + ch} Z"
    bar_max = max(win) or 1

    css = (
        "@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
        ".ln{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 2.4s cubic-bezier(.4,.1,.2,1) .3s forwards}"
        "@keyframes fade{from{opacity:0}to{opacity:1}}"
        ".ar{opacity:0;animation:fade 1.2s ease-out 1.6s forwards}"
        "@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}"
        ".br{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .5s ease-out forwards}"
        "@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}"
        ".up{opacity:0;animation:up .6s ease-out forwards}"
        "@keyframes ping{0%{r:5;opacity:1}100%{r:16;opacity:0}}"
        ".pg{animation:ping 1.6s ease-out 2.7s infinite;opacity:0}"
        ".dt{opacity:0;animation:fade .3s ease-out 2.6s forwards}"
    )
    mono = "'JetBrains Mono','Fira Code',Consolas,monospace"
    sans = "'Segoe UI',-apple-system,'Helvetica Neue',Arial,sans-serif"

    def tx(x, y, s, size=12, fill=None, weight=400, font=sans, anchor="start", extra=""):
        return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill or c["soft"]}" '
                f'font-weight="{weight}" text-anchor="{anchor}" {extra}>{s}</text>')

    p = [f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c["bg0"]}"/>'
         f'<stop offset="1" stop-color="{c["bg1"]}"/></linearGradient>'
         f'<linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["lav"]}" stop-opacity=".45"/>'
         f'<stop offset="1" stop-color="{c["lav"]}" stop-opacity="0"/></linearGradient>'
         f'<linearGradient id="stroke" x1="0" x2="1"><stop offset="0" stop-color="{c["lav"]}"/>'
         f'<stop offset="1" stop-color="{c["orchid"]}"/></linearGradient></defs>',
         f'<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{c["line"]}"/>',
         tx(30, 44, "&gt; training_run --model judy.v2026", 16, c["lav"], 700, mono),
         tx(cx0 + cw, 44, f"{fmt(start)} – {fmt(today)}, {today.year}", 12, c["dim"], font=mono, anchor="end"),
         tx(cx0, 76, "total contributions (cumulative)", 12, c["dim"], font=mono)]

    # gridlines with labels
    for k in range(5):
        v = ymin + (ymax - ymin) * k / 4
        y = Y(v)
        p.append(f'<line x1="{cx0}" y1="{y:.1f}" x2="{cx0 + cw}" y2="{y:.1f}" stroke="{c["grid"]}"/>')
        p.append(tx(cx0 - 10, y + 4, f"{round(v)}", 10, c["dim"], font=mono, anchor="end"))
    # month ticks
    base = cy0 + ch + 44  # baseline of the daily bars, below the chart
    for i in range(n_days):
        d = start + dt.timedelta(i)
        near_month = any((d + dt.timedelta(k)).day == 1 for k in range(-3, 4)) or i < 4
        if d.day == 1 or i == 0 or (n_days <= 45 and d.weekday() == 0 and not near_month):
            lab = d.strftime("%b") if (d.day == 1 or i == 0) else f"{d.day}"
            p.append(tx(X(i), base + 18, lab, 10.5, c["dim"], font=mono, anchor="middle" if i else "start"))
    p.append(tx(cx0 - 10, base - 8, "daily", 9.5, c["dim"], font=mono, anchor="end"))

    # daily bars along the bottom (activity), then the cumulative curve
    bh = 30
    for i, n in enumerate(win):
        if n:
            h = max(3, n / bar_max * bh)
            p.append(f'<rect class="br" x="{X(i) - 3:.1f}" y="{base - h:.1f}" width="6" height="{h:.1f}" rx="2" '
                     f'fill="{c["bar"]}" style="animation-delay:{.3 + i * 2.4 / n_days:.2f}s"/>')
    p.append(f'<line x1="{cx0}" y1="{base}" x2="{cx0 + cw}" y2="{base}" stroke="{c["line"]}"/>')
    p.append(f'<path class="ar" d="{area}" fill="url(#fill)"/>')
    p.append(f'<path class="ln" d="{line}" pathLength="1" fill="none" stroke="url(#stroke)" stroke-width="3" '
             f'stroke-linecap="round" stroke-linejoin="round"/>')
    ex, ey = X(n_days - 1), Y(cum[-1])
    p.append(f'<circle class="pg" cx="{ex:.1f}" cy="{ey:.1f}" r="5" fill="none" stroke="{c["orchid"]}" stroke-width="2"/>')
    p.append(f'<circle class="dt" cx="{ex:.1f}" cy="{ey:.1f}" r="5" fill="{c["orchid"]}"/>')
    if gained:
        p.append(f'<g class="dt">' + tx(ex - 10, ey - 14, f"+{gained} in {n_days} days", 12, c["pink"], 700, mono, "end") + "</g>")
        if win[peak_i]:
            px = X(peak_i)
            p.append(f'<g class="dt">' + tx(px, base - max(3, win[peak_i] / bar_max * bh) - 6,
                                            f"peak day: {win[peak_i]}", 9.5, c["dim"], font=mono, anchor="middle") + "</g>")

    # stat tiles
    tiles = [(f"{total:,}", "contributions", f"since {fmt(first)}, {first.year}"),
             (f"{active}", "active days", "with a contribution"),
             (f"{cur}", "current streak", f"day{'s' if cur != 1 else ''} · and counting"),
             (f"{longest}", "longest streak", f"day{'s' if longest != 1 else ''} · personal best")]
    tx0, ty0, tw, th, g = 696, 70, 138, 138, 14
    for k, (num, l1, l2) in enumerate(tiles):
        x = tx0 + (k % 2) * (tw + g)
        y = ty0 + (k // 2) * (th + g)
        p.append(f'<g class="up" style="animation-delay:{.4 + k * .18:.2f}s">'
                 f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="14" fill="{c["card"]}" stroke="{c["line"]}"/>'
                 + tx(x + 16, y + 56, num, 34, c["lav"] if k % 2 == 0 else c["orchid"], 800)
                 + tx(x + 16, y + 84, l1, 12, c["title"], 600)
                 + tx(x + 16, y + 104, l2, 10.5, c["dim"]) + "</g>")

    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Training run: {total} contributions, {active} active days, current streak {cur}, longest streak {longest}">'
            f'<style>{css}</style>{"".join(p)}</svg>\n')


if __name__ == "__main__":
    main()
