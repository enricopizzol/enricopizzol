"""Render the contribution walk: the cavalier strolls under the contribution
graph and each week lights up as it passes.

Usage: python scripts/dog_walk.py <login> <out.svg>
Needs GITHUB_TOKEN for the GraphQL API; set DEMO=1 to use random data.
"""
import json, os, random, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CELL, GAP, PX = 11, 3, 2
STEP = CELL + GAP
SHADES = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
WALK, HOLD = 9.0, 4.0  # seconds walking across, seconds admiring the result

QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{contributionLevel weekday}}}}}}"""


def fetch(login):
    if os.environ.get("DEMO"):
        rnd = random.Random(7)
        weeks = [[min(4, max(0, int(rnd.gauss(1.2, 1.4)))) for _ in range(7)] for _ in range(53)]
        return weeks, sum(map(sum, weeks)) * 3
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = []
    for w in cal["weeks"]:
        col = [None] * 7
        for d in w["contributionDays"]:
            col[d["weekday"]] = LEVELS[d["contributionLevel"]]
        weeks.append(col)
    return weeks, cal["totalContributions"]


def render(weeks, total):
    dog = json.loads((ROOT / "assets" / "cavalier.json").read_text())
    dw = (max(c[0] for c in dog) + 1) * PX
    dh = (max(c[1] for c in dog) + 1) * PX
    n = len(weeks)
    ox, oy = 24, 34
    gw = n * STEP
    W = ox * 2 + gw
    ground = oy + 7 * STEP + 8
    H = ground + dh + 16
    T = WALK + HOLD
    pct = lambda s: f"{s / T * 100:.2f}%"

    css = [f"""
.lbl{{font:600 13px -apple-system,'Segoe UI',Helvetica,Arial,sans-serif;fill:#8b949e}}
.c{{fill:{SHADES[0]}}}
.bob{{animation:bob .3s steps(1) infinite}}
@keyframes bob{{0%{{transform:translateY(0)}}50%{{transform:translateY(-2px)}}}}
#dog{{animation:walk {T}s linear infinite}}
@keyframes walk{{0%{{transform:translateX({ox - dw}px)}}{pct(WALK)}{{transform:translateX({W}px)}}100%{{transform:translateX({W}px)}}}}
.paw{{fill:#30363d;opacity:0}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.paw{{opacity:1}}}}"""]
    cells, paws = [], []
    for i, col in enumerate(weeks):
        # the week lights up when the dog's nose reaches it
        t = max(0.0, (ox + i * STEP + CELL - (ox - dw) - dw) / (gw + dw) * WALK)
        css.append(f"@keyframes w{i}{{0%,{pct(t)}{{opacity:0}}{pct(t + 0.15)},99%{{opacity:1}}100%{{opacity:0}}}}"
                   f".w{i}{{animation:w{i} {T}s infinite}}")
        lit = []
        for d, lvl in enumerate(col):
            if lvl is None:
                continue
            x, y = ox + i * STEP, oy + d * STEP
            cells.append(f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2"/>')
            if lvl:
                lit.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{SHADES[lvl]}"/>')
        if lit:
            cells.append(f'<g class="w{i}">{"".join(lit)}</g>')
        if i % 2 == 0:
            px, py = ox + i * STEP + 3, ground + dh - 4 - (i // 2 % 2) * 5
            paws.append(f'<g class="paw w{i}"><ellipse cx="{px}" cy="{py}" rx="3" ry="2.4"/>'
                        f'<circle cx="{px - 3}" cy="{py - 3.5}" r="1.2"/><circle cx="{px}" cy="{py - 4.5}" r="1.2"/>'
                        f'<circle cx="{px + 3}" cy="{py - 3.5}" r="1.2"/></g>')
    sprite = "".join(f'<rect x="{x * PX}" y="{y * PX}" width="{PX}" height="{PX}" fill="{c}"/>' for x, y, c in dog)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{total} contributions in the last year, walked by a cavalier">
<style>{"".join(css)}</style>
<text class="lbl" x="{ox}" y="20">{total:,} contributions in the last year</text>
{"".join(cells)}
{"".join(paws)}
<g id="dog"><g transform="translate(0,{ground})"><g class="bob" shape-rendering="crispEdges">{sprite}</g></g></g>
</svg>'''


if __name__ == "__main__":
    login, out = sys.argv[1], sys.argv[2]
    weeks, total = fetch(login)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(render(weeks, total))
    print(f"wrote {out}: {len(weeks)} weeks, {total} contributions")
