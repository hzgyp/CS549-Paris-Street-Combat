"""Build the two current course proposals as DOCX and Markdown sources.

Run with the Codex managed Python runtime. Render DOCX with the documents
skill renderer, inspect every page, and copy the verified PDFs alongside them.
"""
from pathlib import Path
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Docs/Proposal"
IMAGE = OUT / "Visuals/paris-mission-flowchart.png"
MOCKUP_IMAGE = OUT / "Visuals/paris-six-character-concept.png"
FAB = "https://www.fab.com/listings/dae418da-1969-444a-821c-c1f30a3f21b6"
EPIC = "https://dev.epicgames.com/documentation/en-us/unreal-engine/"
SOURCES = [
    ("France Liberation asset", FAB),
    ("Animation Notifies", EPIC + "animation-notifies-in-unreal-engine"),
    ("Collision", EPIC + "collision-in-unreal-engine---overview"),
    ("Navigation", EPIC + "navigation-system-in-unreal-engine"),
    ("Behavior Trees", EPIC + "behavior-tree-in-unreal-engine---overview"),
    ("AI Perception", EPIC + "ai-perception-in-unreal-engine"),
    ("Event Dispatchers", EPIC + "event-dispatchers-in-unreal-engine"),
]

CONCEPT = [
    "We propose a single-player first-person squad mission through a connected part of Meshingun Studio's WW2 - France Liberation city, set during the August 1944 liberation period. Our earlier Normandy mission was too complex in scope because it combined sea, beach, and fortified terrain with different movement, combat, and environmental interactions. Reusing the existing city lets us focus on character interaction and NPC design. An Unreal editor survey of connectivity, collision, sightlines and travel time will determine the playable routes and objective locations.",
    "The initial configuration has six characters: one Allied player, two Allied NPCs, and three German NPCs. This is a development starting point, not a final population cap. We may add finite groups after evaluating pacing, navigation and performance. Allies accompany the player, regroup and use distinct support positions. Enemies guard, patrol on foot, react to visible targets and search near their last observed positions. Shared behavior definitions and individual state allow different soldiers to coordinate without copying one another's actions.",
    "Intermediate objectives guide progress through connected streets. Reaching a location and clearing an assigned enemy group are example objective types; the sequence and geography remain open. We propose checkpoints at selected safe objective boundaries. Retrying restores the saved objective, health, ammunition and relevant NPC state; a new mission restores the initial configuration. Saving does not itself heal, refill ammunition or replace casualties. Checkpoint locations, resupply and reinforcement rules will be selected through playtesting.",
    "The visual goal is coherent movement and combat within the purchased environment. Running and aiming should blend naturally, reload actions should agree with ammunition, and walls should block movement and gunfire. Allies must negotiate narrow passages without teleporting or overlapping, while enemies respond to sight rather than knowing unseen player positions. Health, ammunition and objective displays must reflect the same gameplay state. These interactions and coordinated NPC movement are the main integration challenge as the population grows.",
    "Licensed soldier/rifle assets and compatible motion clips provide visual content, while Unreal supplies rendering, navigation and physical simulation. We will configure these resources and build the gameplay, coordination and UI integration. A connected mission area provides the initial playable slice; not every city building must be enterable. Multiplayer, driving, ocean simulation, unrestricted destruction and detailed character modeling remain outside scope."
]

def xml(tag, **attrs):
    el = OxmlElement(tag)
    for k, v in attrs.items():
        el.set(qn(k), str(v))
    return el

def document(subtitle):
    d = Document()
    for style in d.styles:
        for border in style._element.xpath(".//w:pBdr"):
            border.getparent().remove(border)
    s = d.sections[0]
    s.page_width = Inches(8.5)
    s.page_height = Inches(11)
    s.top_margin = Inches(.58)
    s.bottom_margin = Inches(.58)
    s.left_margin = Inches(.7)
    s.right_margin = Inches(.7)
    s.header_distance = Inches(.2)
    s.footer_distance = Inches(.25)
    for name in ["Normal", "Title", "Subtitle", "Heading 1", "Heading 2", "Caption"]:
        st = d.styles[name]
        st.font.name = "Arial"
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.font.size = Pt(10.5)
        st.paragraph_format.space_after = Pt(5)
        st.paragraph_format.line_spacing = 1.05
    d.styles["Title"].font.size = Pt(23)
    d.styles["Title"].font.bold = True
    d.styles["Title"].paragraph_format.space_after = Pt(4)
    d.styles["Subtitle"].font.size = Pt(11)
    d.styles["Subtitle"].font.italic = False
    d.styles["Subtitle"].paragraph_format.space_after = Pt(10)
    for name in ["Heading 1", "Heading 2"]:
        st = d.styles[name]
        st.font.size = Pt(12 if name == "Heading 1" else 10.5)
        st.font.bold = True
        st.paragraph_format.space_before = Pt(8)
        st.paragraph_format.space_after = Pt(4)
        st.paragraph_format.keep_with_next = True
    d.styles["Caption"].font.size = Pt(9)
    d.styles["Caption"].font.italic = False
    d.core_properties.title = "Paris Street Combat " + subtitle
    d.core_properties.author = "Yupu Guo; Yuqi Pu; Jingdi Wu"
    d.core_properties.subject = "CS549 course project proposal"
    p = s.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = p.add_run("CS549  |  ")
    r.font.size = Pt(8)
    fld = xml("w:fldSimple", **{"w:instr": "PAGE"})
    p._p.append(fld)
    d.add_paragraph("Paris Street Combat", "Title")
    d.add_paragraph(subtitle, "Subtitle")
    return d

def para(d, text, style=None):
    p = d.add_paragraph(style=style)
    # Double asterisks delimit authored emphasis.
    for i, part in enumerate(text.split("**")):
        r = p.add_run(part)
        r.bold = bool(i % 2)
    return p

def table(d, headers, rows, widths):
    t = d.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    props = t._tbl.tblPr
    borders = xml("w:tblBorders")
    for side in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        borders.append(xml("w:" + side, **{"w:val":"single", "w:sz":"4", "w:color":"D9D9D9"}))
    props.append(borders)
    margins = xml("w:tblCellMar")
    for side in ["top", "bottom"]:
        margins.append(xml("w:" + side, **{"w:w":"75", "w:type":"dxa"}))
    for side in ["left", "right"]:
        margins.append(xml("w:" + side, **{"w:w":"100", "w:type":"dxa"}))
    props.append(margins)
    for c, w in zip(t.columns, widths):
        c.width = Inches(w)
    for ri, values in enumerate([headers] + rows):
        row = t.rows[0] if ri == 0 else t.add_row()
        row._tr.get_or_add_trPr().append(xml("w:cantSplit"))
        if ri == 0:
            row._tr.get_or_add_trPr().append(xml("w:tblHeader"))
        for ci, (cell, txt) in enumerate(zip(row.cells, values)):
            cell.width = Inches(widths[ci])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cell._tc.get_or_add_tcPr().append(xml("w:shd", **{"w:fill":"E5EAF0" if ri == 0 else "FFFFFF"}))
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.02
            if ci == 1 and headers[ci] == "NetID":
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(txt)
            r.font.size = Pt(10)
            r.bold = ri == 0
    return t

def hyperlink(p, label, url):
    rid = p.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    h = xml("w:hyperlink", **{"r:id": rid})
    r = xml("w:r")
    props = xml("w:rPr")
    props.append(xml("w:color", **{"w:val":"1F4D70"}))
    props.append(xml("w:sz", **{"w:val":"17"}))
    r.append(props)
    txt = xml("w:t")
    txt.text = label
    r.append(txt)
    h.append(r)
    p._p.append(h)

def sources(d, short=False, include_local=True, label="References"):
    p = d.add_paragraph()
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(label + "  ")
    r.font.size = Pt(8.5)
    selected = SOURCES[:1] if short else SOURCES
    for i, (label, url) in enumerate(selected):
        if i:
            r = p.add_run("  |  ")
            r.font.size = Pt(8.5)
        hyperlink(p, label if short else f"[{i + 1}] {label}", url)
    if include_local:
        p = d.add_paragraph("Local sources: Assignment 1 and Assignment 2; vendor documentation, printed pp. 9, 14, 23 and 70-75.")
        p.paragraph_format.space_after = Pt(0)
        for r in p.runs:
            r.font.size = Pt(8.5)

def picture(d, path, width, description):
    p = d.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Inches(width))
    for prop in p._p.xpath(".//wp:docPr"):
        prop.set("descr", description)

def mockup(d, width=6.3):
    picture(d, MOCKUP_IMAGE, width, "AI-generated first-person street concept based on official France Liberation appearance references: player rifle, two Allied NPCs and three German NPCs around a junction with streets continuing into the city. The initial six-character roster is expandable; geography is conceptual.")
    para(d, "AI-generated concept (OpenAI ImageGen), informed by official Meshingun Studio France Liberation references. Initial roster; illustrative layout, not implemented gameplay. [1]", "Caption")

def flowchart(d):
    picture(d, IMAGE, 7.1, "Proposed mission flow: start or resume, pursue a current Reach or Clear objective, advance when its condition passes, and complete after the final stage. Selected safe objective boundaries may save checkpoints. Player death leads to retry from the latest checkpoint, or the start when none exists. Final mission geography and checkpoint locations are undecided.")

def pillar_work_table(d, emphasize_pillars=False, include_proof=False):
    headers = ["Pillar", "Specific work", "Implementation route"]
    rows = [
        ["Animation", "Smooth idle/walk/run/aim; fire, reload, hit and death actions.", "Adapt clips to soldier skeletons; Blend Spaces blend movement, Montages play actions. Reload events transfer ammo once; interrupted actions cannot update it later. [2]"],
        ["Collision Detection", "Block movement at walls; identify the first object hit by gunfire.", "Capsules enclose moving characters. Trace from camera to aim, then muzzle to aim to detect cover. Apply one hit result; friendly-fire is a separate rule. [3]"],
        ["Pathfinding & Navigation", "Reach goals; follow/regroup; avoid crowding and recover from blocked paths.", "UE NavMesh finds walkable routes; MoveTo follows them. Assign distinct destinations, avoid nearby NPCs and replan on blockage. Custom tactical A* is optional. [4]"],
        ["NPC AI", "Guard, patrol on foot, engage visible enemies, search and regroup.", "Reuse a Behavior Tree with separate controller/Blackboard state per NPC. A squad coordinator assigns roles and support goals; perception drives individual decisions. [5, 6]"],
    ]
    t = table(d, headers, rows, [1.35, 2.15, 3.6])
    if emphasize_pillars:
        for row in t.rows[1:]:
            for paragraph in row.cells[0].paragraphs:
                for run in paragraph.runs:
                    run.bold = True

def save(d, name):
    path = OUT / (name + ".docx")
    d.save(path)
    # Body-order Markdown source allows simple review without an Office reader.
    from docx.text.paragraph import Paragraph
    from docx.table import Table
    lines = []
    for el in d.element.body:
        if el.tag == qn("w:p"):
            p = Paragraph(el, d)
            text = p.text.strip()
            if not text:
                if el.xpath(".//w:drawing"):
                    for blip in el.xpath(".//a:blip"):
                        part = d.part.related_parts[blip.get(qn("r:embed"))]
                        is_mockup = part.blob == MOCKUP_IMAGE.read_bytes()
                        label = "AI-generated street concept using official environment references" if is_mockup else "AI assisted staged mission flowchart"
                        filename = "paris-six-character-concept.png" if is_mockup else "paris-mission-flowchart.png"
                        lines.append(f"![{label}](Visuals/{filename})")
                continue
            prefix = "# " if p.style.name == "Title" else "## " if p.style.name.startswith("Heading") else ""
            lines.append(prefix + text)
        elif el.tag == qn("w:tbl"):
            t = Table(el, d)
            rows = []
            for i, row in enumerate(t.rows):
                rows.append("| " + " | ".join(c.text.replace("|", "\\|") for c in row.cells) + " |")
                if i == 0:
                    rows.append("| " + " | ".join("---" for _ in row.cells) + " |")
            lines.append("\n".join(rows))
    lines.append("\n" + "\n".join(f"- [{a}]({b})" for a, b in SOURCES))
    (OUT / (name + ".md")).write_text("\n\n".join(lines) + "\n", encoding="utf-8")
    print(path)

def assignment1():
    d = document("Assignment 1  Group Formation Pillars and Concept")
    d.add_heading("1. Group formation", 1)
    table(d, ["Group member", "NetID", "Proposed implementation responsibility"], [
        ["Yupu Guo (Group Leader)", "yg745", "Collision, gunplay and integration"],
        ["Yuqi Pu", "yp549", "Animation and character integration"],
        ["Jingdi Wu", "jw2046", "Navigation and NPC AI; environment setup"],
    ], [2.3, .7, 4.1])
    para(d, "Yupu submits for the group. Implementation roles will be agreed at kickoff, with integration support across pillars.", "Caption")
    d.add_heading("2. Project concept summary", 1)
    for text in CONCEPT:
        para(d, text)
    d.add_page_break()
    d.add_heading("3. Street concept and staged mission", 1)
    mockup(d)
    flowchart(d)
    para(d, "Initial roster: 1 player + 2 allies + 3 enemies, expandable after testing. Flow and checkpoint policy are proposed; objective locations and resupply rules remain open.", "Caption")
    d.add_heading("4. Selected pillars and implementation plan", 1)
    pillar_work_table(d, emphasize_pillars=True, include_proof=False)
    para(d, "**Integration and physics support.** Connect UI, combat and coordinated NPC movement within the city. A Blueprint manager controls objectives and checkpoint state. Configure CharacterMovement, collision and engine physics; no custom dynamics solver.")
    sources(d, include_local=False)
    assert 250 <= len(re.findall(r"\S+", " ".join(CONCEPT))) <= 400
    save(d, "CS549_Assignment1_Proposal")

def assignment2():
    d = document("Assignment 2  Product Requirements Technical Specification and MVP")
    # Fit the added concept visual by tightening paragraph gaps, not body type.
    d.styles["Normal"].paragraph_format.space_after = Pt(3)
    for name in ["Heading 1", "Heading 2"]:
        d.styles[name].paragraph_format.space_before = Pt(6)
        d.styles[name].paragraph_format.space_after = Pt(3)
    para(d, "**Yupu Guo (yg745), Group Leader  |  Yuqi Pu (yp549)  |  Jingdi Wu (jw2046)**", "Caption")
    d.add_heading("1. Product requirements (PRD)", 1)
    para(d, "**1.1. Problem and audience.** For PC FPS players and CS549 reviewers, integrate UI, character/environment interactions and coordinated NPC behavior in France Liberation, reducing the varied terrain and interaction complexity of the Normandy concept.")
    para(d, "**1.2. Experience.** Traverse connected streets with intermediate objectives; their sequence and locations remain open. Begin with 1 Allied player, 2 Allied NPCs and 3 German NPCs. Expand finite groups after pacing, navigation and performance checks; six is not a final cap.")
    d.add_heading("1.3. User stories", 2)
    for s in [
        "As a player, I want synchronized run/aim/fire/reload actions so that motion and ammunition agree.",
        "As a player, I want walls and soldiers to block shots so that cover has consistent consequences.",
        "As a player, I want allies to coordinate and enemies to patrol/search on foot so that movement affects combat.",
        "As a player, I want clear objectives and checkpoint retry so that progress and failure are understandable.",
    ]:
        p = para(d, s)
        p.paragraph_format.space_after = Pt(2)
    d.add_heading("1.4. Feature priorities (MoSCoW)", 2)
    table(d, ["MoSCoW", "Feature commitment"], [
        ["Must", "Initial six; configurable objectives and NPC routes; ally follow/regroup; one rifle; four pillars; move/aim/fire/reload/damage; health/ammo/objective UI; win/fail/retry; Windows build."],
        ["Should", "Checkpoints at selected safe objective boundaries; additional finite groups after testing; crouch if supported; impact/footstep audio."],
        ["Could", "Hearing; custom tactical A*; exposure-weighted routes; ragdolls; improved hand IK."],
        ["Won't", "Landing/ocean, multiplayer, driving, broad interiors, destructible buildings, custom detailed soldiers, complex squad commands, infinite waves, runtime LLMs."],
    ], [.8, 6.3])
    d.add_heading("2. Technical specification", 1)
    para(d, "**2.1. Stack.** UE5; Blueprint visual scripting, C++ only if needed. Enhanced Input, UMG, Animation Blueprints, IK Retargeter, NavMesh, AIController/Behavior Trees, AI Perception and Niagara. Structs/Data Assets configure stages/NPCs; no external runtime library required.")
    para(d, "**2.2. Dependencies.** Original asset: UE5.6; working copy: 5.8. Pin a tested version; retain ChaosVehiclesPlugin. Purchase compatible soldier/rifle rigs and clips separately. Survey routes, collision, sightlines and NavMesh; use fixed daylight/static cover. [1]")
    para(d, "**2.3. AI strategy and performance.** ChatGPT/Codex and ImageGen assist offline planning/code/visuals; no runtime AI service. Target: 60 FPS at 1080p on i9-12900F / RTX 3080 / 32 GB Windows PC. Profile mean/p95 frame times, roster and active NPC counts; unmeasured.")
    mockup(d, width=4.6)
    d.add_page_break()
    d.add_heading("2.4. Pillars and implementation", 2)
    pillar_work_table(d, emphasize_pillars=True, include_proof=False)
    para(d, "**2.5. Shared integration.** UI reads authoritative health/ammo/objective state. Player/NPC weapons share hit rules; tracers are cosmetic. Configure purchased rigs, collision and CharacterMovement; reuse engine physics.")
    d.add_heading("2.6. Mission flow and objective control", 2)
    flowchart(d)
    para(d, "Proposed logic, not final geography. Six is an initial roster; checkpoint sites and any resupply/reinforcement rules remain open.", "Caption")
    para(d, "A Blueprint manager advances objectives once from player arrival or assigned-group defeat events. Proposed checkpoints save objective, player health/ammo and relevant NPC state; retry restores that snapshot, or starts fresh if none exists. Saving alone does not heal, refill or revive. Full restart remains available. [7]")
    d.add_heading("3. Narrow vertical slice (MVP)", 1)
    para(d, "**3.1. Core slice and hardest feature.** Deliver a polished connected-street encounter with the initial roster, one rifle, basic UI and intermediate objectives. The hardest feature is integrating UI and physical interactions with the city while NPC movement, decisions and roles remain coordinated as numbers grow.")
    para(d, "**3.2. Midterm demonstration.** Provide a Windows build, gameplay recording and logs. Show UI matching health/ammo, walls blocking movement/shots, correct interrupted reloads, ally regrouping and enemy sight/search. Check objective progression and checkpoint restoration. Compare independent NPC movement with coordinated destinations at bottlenecks; record stalls/frame times before adding NPCs.")
    para(d, "**3.3. MVP exclusions.** Defer additional groups, complex squad commands, advanced cover tactics, physical bullets and citywide simulation. Final mission layout and checkpoint placement follow the editor survey and playtesting.")
    sources(d, include_local=False, label="4. References")
    save(d, "CS549_Assignment2_Proposal")

if __name__ == "__main__":
    assignment1()
    assignment2()
    print("Assignment 1 concept summary words:", len(re.findall(r"\S+", " ".join(CONCEPT))))
