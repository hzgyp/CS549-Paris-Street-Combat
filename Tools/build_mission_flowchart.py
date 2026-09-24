"""Create an editable vector mission flowchart and matching print PNG.

This is a code-authored concept diagram, not an inferred map or game capture.
"""
from pathlib import Path
from html import escape
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Docs/Proposal/Visuals"
W, H, SCALE = 1300, 385, 2
canvas = Image.new("RGB", (W*SCALE, H*SCALE), "white")
draw = ImageDraw.Draw(canvas)
font_dir = Path("/System/Library/Fonts/Supplemental")
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
       '<title id="title">Paris Street Combat staged mission flow</title>',
       '<desc id="desc">Start loads the configured roster. Reach rally A, clear assigned group B once its roster is registered and no enemies survive, then reach endpoint C and succeed. A failed condition keeps its stage active. Player death during any active stage causes failure. Restart or replay resets the full mission. Six soldiers are the initial configuration, not a final cap.</desc>',
       '<rect width="1300" height="385" fill="white"/>']

def text(x, y, value, size=23, bold=False, color="#142636"):
    font = ImageFont.truetype(str(font_dir / ("Arial Bold.ttf" if bold else "Arial.ttf")), int(size*SCALE))
    draw.text((x*SCALE, y*SCALE), value, font=font, fill=color, anchor="mm")
    svg.append(f'<text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="central" font-family="Arial, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{escape(value)}</text>')

def box(x, y, w, h, heading, details, fill="#F0F5FA", stroke="#557A99"):
    draw.rounded_rectangle((x*SCALE,y*SCALE,(x+w)*SCALE,(y+h)*SCALE),radius=10*SCALE,fill=fill,outline=stroke,width=2*SCALE)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
    text(x+w/2,y+27,heading,26,True)
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

text(650,20,"Advance only when the current condition passes; otherwise continue that stage",23)
box(30,53,160,112,"START",["Load roster","Stage 1"])
box(235,53,205,112,"REACH A",["Player enters","rally trigger"])
box(485,53,280,112,"CLEAR AREA B",["Group registered","Living enemies = 0"],"#FFF6E2","#B48A33")
box(810,53,210,112,"REACH END C",["Player enters","exit trigger"])
box(1065,53,200,112,"SUCCESS",["Mission complete"],"#EAF5EF","#53856A")
for a,b in [(190,235),(440,485),(765,810),(1020,1065)]:
    arrow([(a,109),(b,109)])

box(120,230,295,88,"ANY ACTIVE STAGE",["Player dies"],"#FFF1EF","#AD625A")
box(490,230,195,88,"FAIL",["Stop mission"],"#FFF1EF","#AD625A")
box(760,230,360,88,"RESTART MISSION",["Reset roster and objectives"])
arrow([(415,274),(490,274)],"#9C554D")
arrow([(685,274),(760,274)])
arrow([(1165,165),(1165,205),(940,205),(940,230)])
text(1120,185,"Replay",21)
arrow([(940,318),(940,360),(9,360),(9,109),(30,109)])
svg.append('</svg>')
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'paris-mission-flowchart.svg').write_text('\n'.join(svg)+'\n',encoding='utf-8')
canvas.save(OUT/'paris-mission-flowchart.png')
(OUT/'paris-mission-flowchart.mmd').write_text('''flowchart LR
    Start([Start and load configured roster]) --> A[Reach rally A]
    A --> ACheck{Player in rally trigger}
    ACheck -->|No| A
    ACheck -->|Yes| B[Clear area B]
    B --> BCheck{Assigned nonempty group registered and alive count zero}
    BCheck -->|No| B
    BCheck -->|Yes| C[Reach endpoint C]
    C --> CCheck{Player in exit trigger}
    CCheck -->|No| C
    CCheck -->|Yes| Won([Mission success])
    Active[Any active mission stage] -->|Player dies| Lost([Mission failed])
    Lost --> Restart[Full mission restart]
    Won -->|Replay| Restart
    Restart -->|Reset roster and objectives| Start
''',encoding='utf-8')
print('Generated mission flowchart SVG, PNG and Mermaid source')

