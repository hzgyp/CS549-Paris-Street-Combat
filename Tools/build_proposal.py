"""Build the two-page course report. Requires reportlab; no engine execution."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'Docs/Proposal/CS549_Paris_Street_Combat_Proposal.pdf'
INK, TEAL, GRAY = colors.HexColor('#172B38'), colors.HexColor('#176B74'), colors.HexColor('#52616B')
body = ParagraphStyle('Body', fontName='Helvetica', fontSize=9.1, leading=12.0, textColor=INK, spaceAfter=6)
small = ParagraphStyle('Small', parent=body, fontSize=8.2, leading=10.5, spaceAfter=4)
title = ParagraphStyle('Title', parent=body, fontName='Helvetica-Bold', fontSize=24, leading=28, spaceAfter=8)
heading = ParagraphStyle('Heading', parent=body, fontName='Helvetica-Bold', fontSize=11.5, leading=15, textColor=TEAL, spaceBefore=7, spaceAfter=5)
tag = ParagraphStyle('Tag', parent=small, fontName='Helvetica-Bold', textColor=TEAL)

def p(t, style=body):
    return Paragraph(t, style)

def table(rows, widths):
    data = [[p(c, small) for c in row] for row in rows]
    t = Table(data, colWidths=widths, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'TOP'), ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E7EFF0')),
        ('LINEBELOW',(0,0),(-1,0),0.7,TEAL), ('LINEBELOW',(0,1),(-1,-1),0.35,colors.HexColor('#D5DDDF')),
        ('LEFTPADDING',(0,0),(-1,-1),7), ('RIGHTPADDING',(0,0),(-1,-1),7),
        ('TOPPADDING',(0,0),(-1,-1),6), ('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    return t

def footer(c, d):
    c.setStrokeColor(colors.HexColor('#D5DDDF')); c.line(42,39,570,39)
    c.setFont('Helvetica',8); c.setFillColor(GRAY)
    c.drawString(42,26,'CS549 | Paris Street Combat | Project Specification')
    c.drawRightString(570,26,str(d.page))

story = [p('CS549 / PROJECT SPECIFICATION',tag),p('Paris Street Combat',title),
 p('<b>Yupu Guo</b> (yg745, Team Leader)  |  <b>Yuqi Pu</b> (yp549)  |  <b>Jingdi Wu</b> (jw2046)',small),
 p('<b>Primary pillars: Rendering, Animation, Collision Detection</b>'),
 p('1. Product requirements',heading),
 p('A compact single-player FPS encounter in a fictionalized Paris street during the liberation period in August 1944. Normandy is historical background only. Existing environment and compatible character/weapon assets let us focus on agreement between visible feedback, animated weapon actions, and physical shot obstruction.'),
 p('<b>Audience:</b> PC FPS players and course reviewers studying real-time graphics and interaction. The player enters a bounded street, uses cover, engages a small enemy group, completes one objective, and can restart. Exact date, units and equipment will be selected from historical sources; we do not claim an exact street reconstruction.'),
 p('<b>User stories</b>'),
 p('As a player, I want solid cover to block shots from my muzzle even when my crosshair sees beyond it, so that positioning is meaningful. As a player, I want firing and reloading to agree with ammunition state, so that repeated or interrupted actions remain predictable. As a player, I want surface-specific impact feedback, so that I can understand what I hit. As a reviewer, I want matched technical comparisons, so that the team\'s contribution is observable.'),
 table([
 ['<b>Priority</b>','<b>Semester scope</b>'],
 ['<b>Must</b>','One bounded street; one player weapon; one enemy configuration and a small enemy group; movement, aim, fire, reload, damage, win/fail/reset; coherent collision and animation; bounded impact feedback; three pillar comparisons; Windows package.'],
 ['<b>Should</b>','Compatible crouch, minimal enemy movement, spatial audio, and concise objective/health/ammo UI.'],
 ['<b>Could</b>','One feedback refinement or extra short approach after the complete MVP passes.'],
 ['<b>Won\'t</b>','Playable landing/ocean; detailed custom character production; dynamic weather; driving; complex allies/civilians; broad interiors; unrestricted destruction; multiplayer; open-world city; runtime LLM NPCs.']
 ],[67,461]),
 p('2. Technical specification',heading),
 p('<b>Stack:</b> Unreal Engine 5.8.x (installed baseline 5.8.2), Blueprint-first gameplay, Enhanced Input, materials/Niagara, Animation Blueprints/Montages and retargeting where needed, collision traces/Physical Materials, UMG and basic engine-supported NPC behavior. Git/LFS tracks team work. Compatibility and packaged execution will be checked during development.'),
 p('<b>Assets and boundaries:</b> WW2 - France Liberation supplies the city environment, not our technical contribution. The supplier excludes trailer soldiers and some combat VFX. We will acquire compatible existing character/weapon/action assets; engine systems and external assets will be identified separately from team-authored mechanisms.',small),
 PageBreak(),p('TECHNICAL CONTRIBUTION / MVP',tag),p('One encounter, three mechanisms',title),
 table([
 ['<b>Pillar</b>','<b>Team mechanism</b>','<b>Planned comparison</b>'],
 ['<b>Rendering</b>','Surface-driven impact selection, placement and parameters, with bounded lifetime and active count.','Generic versus surface-aware feedback using identical view/shot conditions; GPU frame time and effect count.'],
 ['<b>Animation</b>','Move/aim/fire/reload arbitration; guarded animation events synchronize ammo state and actions.','Timer-only reference versus event synchronization; repeated input, reload interruptions and hand/weapon alignment.'],
 ['<b>Collision Detection</b>','Camera-intent trace followed by muzzle-path obstruction query; one consistent hit/surface result.','Camera-only versus two-stage checks at walls/corners; false hits/blocking and frame-rate consistency.']
 ],[82,220,226]),
 p('Unreal supplies the underlying renderer, animation runtime, scene queries and navigation. We own the Blueprint rules, integration and controlled experiments. AI/navigation supports the encounter; it is not an additional primary pillar.',small),
 p('<b>AI development strategy:</b> AI assists research, documentation, scripts, Blueprint work, diagnostics and tests. No runtime AI service is required. After an unsuccessful 38-iteration character-production experiment, the team discontinued AI-led from-scratch detailed character modeling. Asset gaps will use existing compatible resources, bounded adaptation, professional assistance or scope reduction.'),
 p('<b>Performance:</b> Target Windows at 1920 x 1080 and a declared quality preset, aiming for 60 FPS on an i9-12900F / RTX 3080 10 GB / 32 GB desktop. This is an unmeasured target. We will record frame-time distribution, hitches and GPU memory under repeatable workloads, and run the package on another machine.'),
 p('3. Narrow vertical slice',heading),
 p('<b>MVP:</b> A 60-90-second street-corner encounter using one weapon and a small enemy group. The player moves, aims, fires, reloads, takes damage, reaches a clear win/fail state and restarts. One fixed lighting preset and limited outdoor space constrain asset and performance costs.'),
 p('<b>Hardest feature:</b> Keeping muzzle obstruction, hit feedback, weapon animation and ammunition consistent during close-cover combat and interrupted actions, using compatible acquired assets.'),
 p('<b>Proof by midterm:</b> Demonstrate a Windows package outside the editor, a complete encounter, three restart cycles, fixed corner/reload cases and matched pillar comparisons. Record the quality preset and frame times; have a teammate reproduce the run. These are planned checks, not completed results.'),
 p('<b>Explicit MVP cuts:</b> Additional streets, multiple weapons, driving, allies/civilians, moving doors, destruction, weather and broad interiors.'),
 p('<b>Delivery:</b> Yupu leads integration and proposed collision/gunplay work; Jingdi continues environment/rendering; Yuqi is proposed for animation integration. Each member explains one mechanism and its evidence. We will align technical depth and the revised concept with the instructor/mentor and retain the required approval email proof separately.'),
 p('References',heading),
 p('<link href="https://www.fab.com/listings/dae418da-1969-444a-821c-c1f30a3f21b6" color="#176B74">Meshingun Studio: WW2 - France Liberation</link> (environment dependency); '
       '<link href="https://www.museeliberation-leclerc-moulin.paris.fr/en/museum/la-liberation-de-paris" color="#176B74">Musee de la Liberation: The Liberation of Paris</link> (historical context).',small)]

OUT.parent.mkdir(parents=True,exist_ok=True)
doc=SimpleDocTemplate(str(OUT),pagesize=(612,792),rightMargin=42,leftMargin=42,topMargin=35,bottomMargin=48,
    title='Paris Street Combat - CS549 Project Specification',author='Yupu Guo, Yuqi Pu, Jingdi Wu')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
