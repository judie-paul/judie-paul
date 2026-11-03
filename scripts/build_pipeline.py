"""Generate assets/trust-pipeline.svg: an AI answer travelling through Judy's tools.

A packet (model_output.json) moves along a track and stops at five checkpoints.
Each checkpoint lights up, runs a small animated test, and shows its result.
At the end the packet is stamped TRUSTED, then the loop restarts.

Run:  python scripts/build_pipeline.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "trust-pipeline.svg"

W, H = 1000, 405
LOOP = 16.0                       # seconds per full run
TRACK_Y = 145
XS = [100, 255, 410, 565, 720]    # checkpoint centres
STAMP_X = 880
ARRIVE = [1.0 + i * 2.5 for i in range(5)]   # when the packet reaches each checkpoint
DWELL = 1.6
STAMP_T = 13.5
END_T = 15.3                      # everything fades back here

BG, CARD, LINE = "#0f0b1e", "#16102e", "#3b2a6b"
LAV, ORCHID, PINK, SOFT, DIM, TITLE = "#c4a7ff", "#e879f9", "#f0abfc", "#c3b6e6", "#a99cc8", "#ede7ff"
RED = "#fb7185"
MONO = "'JetBrains Mono','Fira Code',Consolas,monospace"
SANS = "'Segoe UI',-apple-system,'Helvetica Neue',Arial,sans-serif"

css = []


def pct(t):
    return f"{max(0.0, min(100.0, t / LOOP * 100)):.2f}%"


def keyframes(name, points):
    """points: list of (seconds, css declarations). Adds start/end frames if missing."""
    pts = sorted(points)
    if pts[0][0] > 0:
        pts.insert(0, (0, pts[0][1]))
    if pts[-1][0] < LOOP:
        pts.append((LOOP, pts[0][1]))
    body = "".join(f"{pct(t)}{{{d}}}" for t, d in pts)
    css.append(f"@keyframes {name}{{{body}}}")
    css.append(f".{name}{{animation:{name} {LOOP}s linear infinite}}")
    return name


def show_between(name, t_on, t_off=END_T, fade=0.25):
    return keyframes(name, [(0, "opacity:0"), (t_on, "opacity:0"), (t_on + fade, "opacity:1"),
                            (t_off, "opacity:1"), (t_off + fade, "opacity:0")])


def text(x, y, s, size=12, fill=SOFT, weight=400, font=MONO, anchor="start", cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<text{c} x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{s}</text>')


parts = []

# ---------- background, title, track ----------
parts.append(f'<rect width="{W}" height="{H}" rx="16" fill="{BG}"/>')
parts.append(f'<circle cx="26" cy="24" r="6" fill="#ff5f56"/><circle cx="46" cy="24" r="6" fill="#ffbd2e"/>'
             f'<circle cx="66" cy="24" r="6" fill="#27c93f"/>')
parts.append(text(28, 66, "&gt; trust_pipeline --input model_output.json", 16, LAV, 700))
parts.append(text(W - 28, 66, "every answer is checked before it is trusted", 12, DIM, anchor="end", font=SANS))

css.append("@keyframes flow{to{stroke-dashoffset:-28}} .flow{animation:flow 1.2s linear infinite}")
parts.append(f'<line x1="30" y1="{TRACK_Y}" x2="{W - 30}" y2="{TRACK_Y}" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>')
parts.append(f'<line class="flow" x1="30" y1="{TRACK_Y}" x2="{W - 30}" y2="{TRACK_Y}" stroke="{LAV}" '
             f'stroke-opacity=".55" stroke-width="2" stroke-dasharray="6 8"/>')

# ---------- checkpoints ----------
STATIONS = [
    ("Revision Tool · CiteWise", "verify citations", "✓ 3 / 3 quotes match"),
    ("LabelLint", "audit the labels", "✓ bad label caught"),
    ("RubricOps", "two independent scores", "✓ raters agree"),
    ("JudgeCheck", "swap A and B", "✓ no position flip"),
    ("PatchBench", "run tests in a sandbox", "✓ all tests pass"),
]
CW, CY, CHT = 140, 180, 190

for i, ((name, task, result), x, a) in enumerate(zip(STATIONS, XS, ARRIVE)):
    left = x - CW / 2
    # connector + node that lights up on arrival
    lit = keyframes(f"n{i}", [(0, f"fill:#2b2058;stroke:{LINE}"), (a, f"fill:#2b2058;stroke:{LINE}"),
                              (a + .2, f"fill:{LAV};stroke:{PINK}"), (END_T, f"fill:{LAV};stroke:{PINK}"),
                              (END_T + .3, f"fill:#2b2058;stroke:{LINE}")])
    halo = keyframes(f"h{i}", [(0, "opacity:0"), (a, "opacity:0"), (a + .2, "opacity:.9"),
                               (a + DWELL, "opacity:.35"), (END_T, "opacity:.35"), (END_T + .3, "opacity:0")])
    parts.append(f'<line x1="{x}" y1="{TRACK_Y + 14}" x2="{x}" y2="{CY}" stroke="{LINE}" stroke-width="2"/>')
    parts.append(f'<circle class="{halo}" cx="{x}" cy="{TRACK_Y}" r="22" fill="{LAV}" fill-opacity=".18"/>')
    parts.append(f'<circle class="{lit}" cx="{x}" cy="{TRACK_Y}" r="11" stroke-width="3"/>')
    parts.append(text(x, TRACK_Y - 26, f"0{i + 1}", 11, DIM, anchor="middle"))

    # card
    border = keyframes(f"b{i}", [(0, f"stroke:{LINE}"), (a, f"stroke:{LINE}"), (a + .2, f"stroke:{LAV}"),
                                 (a + DWELL, f"stroke:{LINE}")])
    parts.append(f'<rect class="{border}" x="{left}" y="{CY}" width="{CW}" height="{CHT}" rx="12" fill="{CARD}" stroke-width="1.5"/>')
    title_size = 11.5 if len(name) > 14 else 14
    parts.append(text(x, CY + 26, name, title_size, TITLE, 700, SANS, "middle"))
    parts.append(text(x, CY + 44, task, 10.5, DIM, anchor="middle", font=SANS))

    # result line
    res = show_between(f"r{i}", a + DWELL - .3)
    parts.append(text(x, CY + CHT - 16, result, 10.5, PINK, 700, SANS, "middle", res))

    # ---------- mini animation for each checkpoint (area y: CY+60 .. CY+150) ----------
    mx, my = left + 16, CY + 62
    if i == 0:      # three source lines get ticks one by one
        for j in range(3):
            y = my + 10 + j * 24
            parts.append(f'<rect x="{mx}" y="{y - 6}" width="78" height="6" rx="3" fill="{LINE}"/>')
            parts.append(text(mx, y + 11, f"“quote {j + 1}” → p.{3 + j * 4}", 8.5, DIM))
            tick = show_between(f"t0{j}", a + .25 + j * .35)
            parts.append(text(mx + 100, y + 4, "✓", 15, PINK, 700, SANS, cls=tick))
    elif i == 1:    # one of four labels turns red, gets an evidence tag, is fixed
        for j in range(4):
            y = my + 4 + j * 20
            if j == 2:
                chip = keyframes("chipbad", [(0, f"fill:{LINE}"), (a + .15, f"fill:{LINE}"), (a + .3, f"fill:{RED}"),
                                             (a + 1.25, f"fill:{RED}"), (a + 1.45, f"fill:{LINE}")])
                parts.append(f'<rect class="{chip}" x="{mx}" y="{y}" width="64" height="13" rx="6.5"/>')
                tag = keyframes("evtag", [(0, "opacity:0"), (a + .45, "opacity:0"), (a + .6, "opacity:1"),
                                          (END_T, "opacity:1"), (END_T + .25, "opacity:0")])
                parts.append(f'<g class="{tag}"><rect x="{mx + 70}" y="{y - 1}" width="38" height="15" rx="4" fill="none" stroke="{PINK}"/>'
                             + text(mx + 89, y + 10, "flag", 9, PINK, 700, anchor="middle") + "</g>")
            else:
                parts.append(f'<rect x="{mx}" y="{y}" width="64" height="13" rx="6.5" fill="{LINE}"/>')
            parts.append(text(mx + 6, y + 10, f"label {j + 1}", 8.5, TITLE))
    elif i == 2:    # two raters' bars fill, then an "=" links them
        for j, who in enumerate(("rater A", "rater B")):
            y = my + 8 + j * 30
            parts.append(text(mx, y, who, 9, DIM))
            parts.append(f'<rect x="{mx}" y="{y + 5}" width="100" height="9" rx="4.5" fill="{LINE}"/>')
            bar = keyframes(f"bar{j}", [(0, "transform:scaleX(0)"), (a + .1 + j * .25, "transform:scaleX(0)"),
                                        (a + .7 + j * .25, "transform:scaleX(.82)"), (END_T, "transform:scaleX(.82)"),
                                        (END_T + .3, "transform:scaleX(0)")])
            parts.append(f'<rect class="{bar}" x="{mx}" y="{y + 5}" width="100" height="9" rx="4.5" fill="{LAV}" '
                         f'style="transform-box:fill-box;transform-origin:left center"/>')
        agree = show_between("agree", a + 1.0)
        parts.append(text(mx + 54, my + 82, "A = B", 11, PINK, 700, anchor="middle", cls=agree))
    elif i == 3:    # answers A and B swap places; the verdict stays on A
        y = my + 10
        for j, (lab, dx) in enumerate((("A", 1), ("B", -1))):
            bx = mx + 4 + j * 62
            sw = keyframes(f"sw{j}", [(0, "transform:translateX(0)"), (a + .2, "transform:translateX(0)"),
                                      (a + .8, f"transform:translateX({dx * 62}px)"),
                                      (END_T, f"transform:translateX({dx * 62}px)"), (END_T + .3, "transform:translateX(0)")])
            parts.append(f'<g class="{sw}"><rect x="{bx}" y="{y}" width="42" height="32" rx="6" fill="{LINE}" '
                         f'stroke="{LAV if lab == "A" else LINE}"/>'
                         + text(bx + 21, y + 21, lab, 13, TITLE, 700, anchor="middle") + "</g>")
        parts.append(text(mx + 54, y + 58, "verdict: A", 10, DIM, anchor="middle"))
        held = show_between("held", a + 1.0)
        parts.append(text(mx + 54, y + 76, "same after swap", 9, PINK, 700, anchor="middle", font=SANS, cls=held))
    else:           # sandbox box: four tests turn on one by one
        parts.append(f'<rect x="{mx + 6}" y="{my + 6}" width="96" height="58" rx="6" fill="none" stroke="{LAV}" stroke-dasharray="4 3"/>')
        parts.append(text(mx + 54, my + 20, "docker sandbox", 8.5, DIM, anchor="middle"))
        for j in range(4):
            dot = keyframes(f"dot{j}", [(0, f"fill:{LINE}"), (a + .2 + j * .25, f"fill:{LINE}"),
                                        (a + .35 + j * .25, f"fill:{LAV}"), (END_T, f"fill:{LAV}"),
                                        (END_T + .3, f"fill:{LINE}")])
            parts.append(f'<circle class="{dot}" cx="{mx + 24 + j * 20}" cy="{my + 44}" r="6"/>')
        parts.append(text(mx + 54, my + 84, "test_1 … test_4", 8.5, DIM, anchor="middle"))

# ---------- end stamp ----------
stamp = keyframes("stamp", [(0, "opacity:0;transform:scale(1.8) rotate(-8deg)"),
                            (STAMP_T, "opacity:0;transform:scale(1.8) rotate(-8deg)"),
                            (STAMP_T + .25, "opacity:1;transform:scale(1) rotate(-8deg)"),
                            (END_T, "opacity:1;transform:scale(1) rotate(-8deg)"),
                            (END_T + .3, "opacity:0;transform:scale(1) rotate(-8deg)")])
sy = CY + 70
parts.append(f'<g class="{stamp}" style="transform-box:fill-box;transform-origin:center">'
             f'<rect x="{STAMP_X - 62}" y="{sy}" width="124" height="62" rx="8" fill="none" stroke="{ORCHID}" stroke-width="3"/>'
             + text(STAMP_X, sy + 30, "TRUSTED", 20, ORCHID, 800, SANS, "middle")
             + text(STAMP_X, sy + 48, "judy.v2026", 10, PINK, 700, anchor="middle") + "</g>")
parts.append(text(STAMP_X, CY + 26, "result", 12, DIM, anchor="middle", font=SANS))
parts.append(f'<line x1="{STAMP_X}" y1="{TRACK_Y + 14}" x2="{STAMP_X}" y2="{CY + 8}" stroke="{LINE}" stroke-width="2" stroke-dasharray="3 4"/>')

# ---------- packet ----------
moves = [(0, -90)]
for x, a in zip(XS, ARRIVE):
    moves += [(a - .9, moves[-1][1]), (a, x), (a + DWELL, x)]
moves += [(STAMP_T - .9, XS[-1]), (STAMP_T, STAMP_X), (END_T, STAMP_X)]
pts = []
for t, x in moves:
    pts.append((t, f"transform:translateX({x}px);opacity:1"))
pts.append((END_T + .3, f"transform:translateX({STAMP_X}px);opacity:0"))
pts.append((END_T + .31, "transform:translateX(-90px);opacity:0"))
pts.append((LOOP, "transform:translateX(-90px);opacity:1"))
# dedupe identical times (keep last)
seen = {}
for t, d in pts:
    seen[round(t, 3)] = d
keyframes("pk", list(seen.items()))
css.append(".pk{animation-timing-function:ease-in-out}")
parts.append(f'<g class="pk"><rect x="-62" y="{TRACK_Y - 15}" width="124" height="30" rx="15" fill="#2b2058" '
             f'stroke="{LAV}" stroke-width="2"/>'
             + text(0, TRACK_Y + 4, "model_output.json", 10.5, TITLE, 700, anchor="middle") + "</g>")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
       f'aria-label="Animated trust pipeline: an AI answer passes citation, label, rater, judge-bias and test checks before it is stamped trusted">'
       f'<style>{"".join(css)}</style>' + "".join(parts) + "</svg>\n")
OUT.write_text(svg, encoding="utf-8")
print(f"Wrote {OUT} ({len(svg):,} bytes)")
