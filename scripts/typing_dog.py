import sys
LINES = ["Senior Backend & AI Engineer", "LLM Agents • RAG • Evals",
         "Cloud-native backends & data", "Engenheiro de Software & IA"]
W, H, FS = 760, 76, 24
CW = FS * 0.6           # forced char width via textLength
BASE = 50               # text baseline
TYPE, HOLD, ERASE, GAP = 0.075, 1.6, 0.5, 0.3
PX = 4                  # dog pixel size

# timeline
segs, t = [], 0.0
for s in LINES:
    n = len(s); w = n * CW; x0 = (W - w) / 2
    segs.append(dict(s=s, n=n, w=w, x0=x0, t0=t, t1=t + n*TYPE, t2=t + n*TYPE + HOLD, t3=t + n*TYPE + HOLD + ERASE))
    t = segs[-1]['t3'] + GAP
T = t
pc = lambda v: f"{v / T * 100:.3f}%"
esc = lambda s: s.replace("&", "&amp;")

css, body = [], []
dog_kf = []
for i, g in enumerate(segs):
    cid = f"c{i}"
    kf = [f"0%{{width:0}}", f"{pc(g['t0'])}{{width:0;animation-timing-function:steps({g['n']},end)}}",
          f"{pc(g['t1'])}{{width:{g['w']+2:.1f}px}}", f"{pc(g['t2'])}{{width:{g['w']+2:.1f}px;animation-timing-function:steps({g['n']},end)}}",
          f"{pc(g['t3'])}{{width:0}}", "100%{width:0}"]
    css.append(f"@keyframes k{i}{{{''.join(kf)}}} #r{i}{{animation:k{i} {T:.2f}s infinite}}")
    body.append(f'<clipPath id="{cid}"><rect id="r{i}" x="{g["x0"]:.1f}" y="0" width="0" height="{H}"/></clipPath>')
    body.append(f'<text clip-path="url(#{cid})" x="{g["x0"]:.1f}" y="{BASE}" textLength="{g["w"]:.1f}" lengthAdjust="spacingAndGlyphs" class="t">{esc(g["s"])}</text>')
    st = f"animation-timing-function:steps({g['n']},end)"
    dog_kf += [f"{pc(g['t0'])}{{transform:translateX({g['x0']:.1f}px);{st}}}",
               f"{pc(g['t1'])}{{transform:translateX({g['x0']+g['w']:.1f}px)}}",
               f"{pc(g['t2'])}{{transform:translateX({g['x0']+g['w']:.1f}px);{st}}}",
               f"{pc(g['t3'])}{{transform:translateX({g['x0']:.1f}px)}}"]
first, last = segs[0], segs[-1]
dog_kf = [f"0%{{transform:translateX({first['x0']:.1f}px)}}"] + dog_kf + [f"100%{{transform:translateX({first['x0']:.1f}px)}}"]
# between lines the dog hops instantly to the next start
css.append("@keyframes dog{" + "".join(dog_kf) + "} #dog{animation:dog %.2fs infinite}" % T)

# rico's cavalier, front-facing pixel sprite extracted from their art
import json, os
CAV = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "cavalier.json")))
PX = 2
cw = max(c[0] for c in CAV) + 1; ch = max(c[1] for c in CAV) + 1
dy = BASE - ch * PX + 4
dog = [f'<g id="dog"><g transform="translate(6,{dy})"><g class="bob" shape-rendering="crispEdges">']
dog += [f'<rect x="{x*PX}" y="{y*PX}" width="{PX}" height="{PX}" fill="{c}"/>' for x, y, c in CAV]
dog += ['</g></g></g>']
css.append("""
.t{font:600 %dpx 'JetBrains Mono','Fira Code',Consolas,Menlo,monospace;fill:#58a6ff}
.bob{animation:bob .36s steps(1) infinite}
@keyframes bob{0%%{transform:translateY(0)}50%%{transform:translateY(-2px)}}
@media (prefers-reduced-motion:reduce){*{animation-duration:0s!important}}
""" % FS)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(" / ".join(LINES))}">
<style>{"".join(css)}</style>
<defs>{"".join(b for b in body if b.startswith("<clipPath"))}</defs>
{"".join(b for b in body if b.startswith("<text"))}
{"".join(dog)}
</svg>'''
open(sys.argv[1], "w").write(svg)
print(f"cycle {T:.1f}s, {len(svg)} bytes")
