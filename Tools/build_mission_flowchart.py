"""Create an editable vector mission flowchart and matching print PNG.

This is a code-authored concept diagram, not an inferred map or game capture.
"""
from pathlib import Path
from html import escape
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Docs/Proposal/Visuals"
W, H, SCALE = 1300, 405, 2
canvas = Image.new("RGB", (W*SCALE, H*SCALE), "white")
draw = ImageDraw.Draw(canvas)
font_dir = Path("/System/Library/Fonts/Supplemental")
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
       '<title id="title">Paris Street Combat staged mission flow</title>',
       '<desc id="desc">Proposed flow: start or resume, pursue a current Reach or Clear objective until its condition passes, advance progress and save at selected safe boundaries if configured, then continue to the next objective or complete. Player death leads to retry from the latest checkpoint or the start when none exists. Objective order, map locations and checkpoint sites remain open. Saving does not automatically heal, refill or revive.</desc>',
       '<rect width="1300" height="405" fill="white"/>']

def text(x, y, value, size=23, bold=False, color="#142636"):
    font = ImageFont.truetype(str(font_dir / ("Arial Bold.ttf" if bold else "Arial.ttf")), int(size*SCALE))
    draw.text((x*SCALE, y*SCALE), value, font=font, fill=color, anchor="mm")
    svg.append(f'<text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="central" font-family="Arial, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{escape(value)}</text>')

def box(x, y, w, h, heading, details, fill="#F0F5FA", stroke="#557A99"):
    draw.rounded_rectangle((x*SCALE,y*SCALE,(x+w)*SCALE,(y+h)*SCALE),radius=10*SCALE,fill=fill,outline=stroke,width=2*SCALE)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    text(x+w/2,y+27,heading,23 if heading == "START / RESUME" else 26,True)
    for i,line in enumerate(details):
        text(x+w/2,y+61+i*27,line,22)

def arrow(points, color="#455665", width=3):
    scaled=[(int(x*SCALE),int(y*SCALE)) for x,y in points]
    draw.line(scaled,fill=color,width=width*SCALE,joint="curve")
    svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"/>')
    x,y=points[-1]; px,py=points[-2]
    if abs(x-px)>abs(y-py):
        s=1 if x>px else -1
        tri=[(x,y),(x-10*s,y-6),(x-10*s,y+6)]
    else:
        s=1 if y>py else -1
        tri=[(x,y),(x-6,y-10*s),(x+6,y-10*s)]
    draw.polygon([(int(a*SCALE),int(b*SCALE)) for a,b in tri],fill=color)
    svg.append('<polygon points="'+' '.join(f'{a},{b}' for a,b in tri)+f'" fill="{color}"/>')

text(650,20,"Proposed flow: objective order, locations and checkpoint sites remain open",23)
box(25,53,215,112,"START / RESUME",["Initial or saved","mission state"])
box(285,53,340,112,"CURRENT OBJECTIVE",["Reach location or clear group","Continue until condition passes"])
box(670,53,305,112,"PROGRESS UPDATE",["Advance objective","Save if configured"],"#FFF6E2","#B48A33")
box(1030,53,240,112,"COMPLETE",["Final objective passed"],"#EAF5EF","#53856A")
for a,b in [(240,285),(625,670),(975,1030)]:
    arrow([(a,109),(b,109)])
arrow([(820,165),(820,210),(455,210),(455,165)])
text(641,191,"More objectives: continue",22)

box(140,265,310,88,"PLAYER DIES",["At any active objective"],"#FFF1EF","#AD625A")
box(535,265,600,88,"RETRY",["Restore latest checkpoint; start if none"])
arrow([(450,309),(535,309)],"#9C554D")
arrow([(835,353),(835,388),(9,388),(9,109),(25,109)])
svg.append('</svg>')
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'paris-mission-flowchart.svg').write_text('\n'.join(svg)+'\n',encoding='utf-8')
canvas.save(OUT/'paris-mission-flowchart.png')
(OUT/'paris-mission-flowchart.mmd').write_text('''flowchart LR
    Start([Start or resume initial or saved state]) --> Current[Current objective: Reach or Clear]
    Current --> Check{Current condition passed}
    Check -->|No| Current
    Check -->|Yes| Progress[Advance progress; save at selected safe boundary if configured]
    Progress --> More{More objectives}
    More -->|Yes| Current
    More -->|No| Success([Mission complete])
    Active[Any active objective] -->|Player dies| Retry[Retry latest checkpoint or start if none]
    Retry --> Start
    Success -->|New mission| New[Restore initial configured state]
    New --> Start
''',encoding='utf-8')
print(OUT/'paris-mission-flowchart.png')
