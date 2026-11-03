"""Generate the model-card artwork: hero header, benchmark odometers and footer.

Writes assets/hero.svg, assets/metrics.svg and assets/footer.svg.
Run:  python scripts/build_art.py
"""
import random
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

BG0, BG1, CARD, LINE = "#0f0b1e", "#1b1238", "#16102e", "#3b2a6b"
LAV, ORCHID, PINK, SOFT, DIM, TITLE = "#c4a7ff", "#e879f9", "#f0abfc", "#c3b6e6", "#a99cc8", "#ede7ff"
MONO = "'JetBrains Mono','Fira Code',Consolas,monospace"
SANS = "'Segoe UI',-apple-system,'Helvetica Neue',Arial,sans-serif"


def t(x, y, s, size=12, fill=SOFT, weight=400, font=SANS, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}" {extra}>{s}</text>')


# ---------------------------------------------------------------- hero
def hero():
    W, H = 1000, 340
    css = [
        "@keyframes up{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}",
        ".up{opacity:0;animation:up .7s ease-out forwards}",
        "@keyframes load{from{transform:scaleX(0)}to{transform:scaleX(1)}}",
        ".load{transform-box:fill-box;transform-origin:left center;transform:scaleX(0);animation:load 2.2s cubic-bezier(.3,.7,.2,1) .4s forwards}",
        "@keyframes done{0%,90%{opacity:0}100%{opacity:1}}",
        ".done{opacity:0;animation:done 2.7s linear forwards}",
        "@keyframes tw{0%,100%{opacity:.15}50%{opacity:1}}",
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}",
        ".pulse{animation:pulse 1.8s ease-in-out infinite}",
        "@keyframes drift{from{transform:translateX(0)}to{transform:translateX(-40px)}}",
        ".grid{animation:drift 8s linear infinite}",
    ]
    p = [f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/>'
         f'<stop offset="1" stop-color="{BG1}"/></linearGradient>'
         f'<linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{LINE}"/><stop offset="1" stop-color="{LAV}"/></linearGradient>'
         f'<pattern id="g" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{LAV}" stroke-opacity=".06"/></pattern>'
         f'<clipPath id="clip"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>',
         f'<g clip-path="url(#clip)"><rect width="{W}" height="{H}" fill="url(#bg)"/>'
         f'<rect class="grid" width="{W + 80}" height="{H}" fill="url(#g)"/></g>',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{LINE}"/>']

    # breadcrumb, like a model hub page
    p.append(f'<g class="up" style="animation-delay:.1s">'
             + t(40, 48, f'models <tspan fill="{LINE}">/</tspan> judie-paul <tspan fill="{LINE}">/</tspan> '
                 f'<tspan fill="{LAV}" font-weight="700">judy.v2026</tspan>', 14, DIM, font=MONO) + "</g>")
    p.append(f'<g class="up" style="animation-delay:.25s">' + t(40, 118, "Judy Ndungu", 58, TITLE, 800) + "</g>")
    p.append(f'<g class="up" style="animation-delay:.4s">'
             + t(42, 152, "A human model card · AI evaluation &amp; data quality", 18, SOFT) + "</g>")

    # tag chips
    chips = [("Task", "AI evaluation"), ("Task", "data quality"), ("Task", "grounded generation"),
             ("Lang", "Python · Go · TS"), ("License", "open to work")]
    x, y = 40, 176
    for i, (k, v) in enumerate(chips):
        label = f"{k}: {v}"
        w = len(label) * 7.4 + 22
        if x + w > 640:  # wrap before the parameter grid
            x, y = 40, y + 34
        color = ORCHID if k == "License" else LAV
        p.append(f'<g class="up" style="animation-delay:{.6 + i * .12:.2f}s">'
                 f'<rect x="{x}" y="{y}" width="{w:.0f}" height="26" rx="13" fill="{CARD}" stroke="{color}" stroke-opacity=".6"/>'
                 + t(x + 11, y + 17, f'<tspan fill="{DIM}">{k}:</tspan> {v}', 12, color, 600, MONO) + "</g>")
        x += w + 8

    # loading bar
    p.append(t(40, 270, "loading checkpoint", 12, DIM, font=MONO))
    p.append(f'<rect x="40" y="280" width="520" height="8" rx="4" fill="{LINE}" fill-opacity=".5"/>')
    p.append(f'<rect class="load" x="40" y="280" width="520" height="8" rx="4" fill="url(#bar)"/>')
    p.append(f'<g class="done">' + t(560, 270, "100% · ready ✓", 12, PINK, 700, MONO, "end") + "</g>")
    p.append(t(40, 314, '<tspan class="pulse" fill="#4ade80">●</tspan> online · last trained today · weights: curious', 12, DIM, font=MONO))

    # "parameters" grid that twinkles
    random.seed(7)
    gx, gy, n, s = 712, 76, 11, 20
    p.append(t(gx + n * s / 2 - 4, 54, "parameters", 12, DIM, font=MONO, anchor="middle"))
    for r in range(n):
        for c in range(n):
            d = random.uniform(0, 4)
            dur = random.uniform(2.2, 4.5)
            hue = random.choice([LAV, LAV, LAV, ORCHID, PINK])
            p.append(f'<rect x="{gx + c * s}" y="{gy + r * s}" width="{s - 6}" height="{s - 6}" rx="3" fill="{hue}" '
                     f'style="opacity:.15;animation:tw {dur:.1f}s ease-in-out {-d:.1f}s infinite"/>')
    p.append(t(gx + n * s / 2 - 4, gy + n * s + 18, "121 of 121 curious", 11, DIM, font=MONO, anchor="middle"))

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="Judy Ndungu: a human model card for AI evaluation and data quality">'
           f'<style>{"".join(css)}</style>{"".join(p)}</svg>\n')
    (ASSETS / "hero.svg").write_text(svg, encoding="utf-8")


# ---------------------------------------------------------------- odometer metrics
METRICS = [  # (prefix, number, suffix, label line 1, label line 2)
    ("~", "3.3", "k", "MT-Bench expert votes", "checked in JudgeCheck"),
    ("", "92", "", "tests behind", "JudgeCheck"),
    ("", "97", "%", "test coverage", "in LabelLint"),
    ("", "5", "", "checkpoints in the", "trust pipeline"),
    ("", "10", "", "public projects", "and counting"),
]


def metrics(projects=None):
    rows = [m if m[3] != "public projects" or projects is None else (m[0], str(projects), *m[2:]) for m in METRICS]
    W, H = 1000, 170
    tile_w, gap = 184, 20
    digit_h, size = 46, 40
    css = ["@keyframes roll{from{transform:translateY(0)}}",
           "@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}",
           ".up{opacity:0;animation:up .6s ease-out forwards}"]
    p = [f'<rect width="{W}" height="{H}" rx="18" fill="{BG0}"/>',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{LINE}"/>']
    x0 = (W - (len(rows) * tile_w + (len(rows) - 1) * gap)) / 2
    k = 0
    for i, (pre, num, suf, l1, l2) in enumerate(rows):
        x = x0 + i * (tile_w + gap)
        p.append(f'<rect x="{x}" y="18" width="{tile_w}" height="{H - 36}" rx="14" fill="{CARD}" stroke="{LINE}"/>')
        digit_w = size * 0.62
        total_w = (sum(digit_w if c.isdigit() else digit_w * .45 for c in num)
                   + (size * .6 if pre else 0) + (size * .55 if suf else 0))
        cx = x + tile_w / 2 - total_w / 2
        top = 34
        if pre:
            p.append(t(cx, top + digit_h - 10, pre, size, LAV, 800, SANS))
            cx += size * .6
        for j, ch in enumerate(num):
            if not ch.isdigit():  # decimal point or comma: drawn still
                p.append(t(cx, top + digit_h - 10, ch, size, LAV, 800, SANS))
                cx += digit_w * .45
                continue
            d = int(ch)
            k += 1
            cid = f"dc{k}"
            spins = 10 + d  # roll through a full 0-9 cycle first
            strip = "".join(t(cx + digit_w / 2, top + digit_h - 10 + n * digit_h, str(n % 10), size, LAV, 800, SANS, "middle")
                            for n in range(spins + 1))
            delay = .3 + i * .25 + j * .12
            p.append(f'<clipPath id="{cid}"><rect x="{cx}" y="{top}" width="{digit_w}" height="{digit_h}"/></clipPath>'
                     f'<g clip-path="url(#{cid})"><g style="transform:translateY({-spins * digit_h}px);'
                     f'animation:roll {1.6 + j * .2:.1f}s cubic-bezier(.2,.8,.2,1) {delay:.2f}s both">{strip}</g></g>')
            cx += digit_w
        if suf:
            p.append(t(cx + 2, top + digit_h - 10, suf, size * .7, ORCHID, 800, SANS))
        p.append(f'<g class="up" style="animation-delay:{.8 + i * .2:.1f}s">'
                 + t(x + tile_w / 2, 112, l1, 13, TITLE, 600, SANS, "middle")
                 + t(x + tile_w / 2, 130, l2, 12, DIM, 400, SANS, "middle") + "</g>")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="Benchmark highlights: about 3,300 MT-Bench expert votes, 92 tests, 97% coverage, 5 pipeline checkpoints, 10 public projects">'
           f'<style>{"".join(css)}</style>{"".join(p)}</svg>\n')
    (ASSETS / "metrics.svg").write_text(svg, encoding="utf-8")


# ---------------------------------------------------------------- footer
def footer():
    W, H = 1000, 90
    css = ["@keyframes sweep{from{transform:translateX(-300px)}to{transform:translateX(1100px)}}",
           ".sw{animation:sweep 4s ease-in-out infinite}",
           "@keyframes blink{0%,50%{opacity:1}51%,100%{opacity:0}}", ".bl{animation:blink 1s steps(1) infinite}"]
    p = [f'<defs><linearGradient id="s" x1="0" x2="1"><stop offset="0" stop-color="{LAV}" stop-opacity="0"/>'
         f'<stop offset=".5" stop-color="{ORCHID}"/><stop offset="1" stop-color="{LAV}" stop-opacity="0"/></linearGradient></defs>',
         f'<rect x="0" y="14" width="{W}" height="2" fill="{LINE}"/>',
         f'<rect class="sw" x="0" y="13" width="260" height="4" rx="2" fill="url(#s)"/>',
         t(W / 2, 54, f'■ end of model card <tspan fill="{LINE}">·</tspan> judy.v2026 '
           f'<tspan fill="{LINE}">·</tspan> <tspan fill="{PINK}">checkpoint saved ✓</tspan>', 14, DIM, 600, MONO, "middle"),
         t(W / 2, 78, f'evaluated honestly, shipped tested<tspan class="bl" fill="{LAV}"> ▍</tspan>', 12, DIM, 400, MONO, "middle")]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="End of model card">'
           f'<style>{"".join(css)}</style>{"".join(p)}</svg>\n')
    (ASSETS / "footer.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    hero()
    metrics()
    footer()
    print("Wrote hero.svg, metrics.svg, footer.svg")
