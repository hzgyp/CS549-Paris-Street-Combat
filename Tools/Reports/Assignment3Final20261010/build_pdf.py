"""Typeset the user-approved Assignment 3 outline; do not launch the game.

New report generator. The rejected Assignment3Review20261010 generator and
PDFs are historical failure evidence and are not used here.
"""
from pathlib import Path
import json
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak,
    KeepTogether,
)

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'output/pdf/Paris_Street_Combat_Assignment3_20261010_EN.pdf'
QA = ROOT / 'tmp/pdfs/assignment3-final-20261010'
REPO = 'https://github.com/hzgyp/CS549-Paris-Street-Combat'
VIDEO = 'https://youtu.be/SktbFHNYP54'
BLUE = colors.HexColor('#24465F')
INK = colors.HexColor('#202A32')
GRAY = colors.HexColor('#52606B')
RULE = colors.HexColor('#CDD5DC')

pdfmetrics.registerFont(TTFont('ReportArial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ReportArialBold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('ReportArial', normal='ReportArial', bold='ReportArialBold')

styles = {
    'title': ParagraphStyle('Title', fontName='ReportArialBold', fontSize=20,
                            leading=23, textColor=BLUE, spaceAfter=7),
    'meta': ParagraphStyle('Meta', fontName='ReportArial', fontSize=9,
                           leading=12, textColor=GRAY, spaceAfter=9),
    'h': ParagraphStyle('Heading', fontName='ReportArialBold', fontSize=11.5,
                        leading=15, textColor=BLUE, spaceBefore=9, spaceAfter=6),
    'body': ParagraphStyle('Body', fontName='ReportArial', fontSize=9.6,
                           leading=12.9, textColor=INK, spaceAfter=7),
    'cell': ParagraphStyle('Cell', fontName='ReportArial', fontSize=9.2,
                           leading=12, textColor=INK),
    'small': ParagraphStyle('Small', fontName='ReportArial', fontSize=8.1,
                            leading=10.5, textColor=GRAY, spaceAfter=5),
}

def p(text, style='body'):
    return Paragraph(text, styles[style])

def link(url, label):
    return f'<a href="{url}" color="#24465F"><u>{label}</u></a>'

def heading(text):
    return p(text, 'h')

def table(rows, widths, header=True):
    data = [[p(t, 'cell') for t in row] for row in rows]
    t = Table(data, colWidths=widths, hAlign='LEFT')
    commands = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -1), .35, RULE),
    ]
    if header:
        commands += [('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EDF2F5'))]
    t.setStyle(TableStyle(commands))
    return t

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(.5)
    canvas.line(43, 37, 569, 37)
    canvas.setFont('ReportArial', 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(43, 24, 'CS549 | Paris Street Combat | Assignment 3')
    canvas.drawRightString(569, 24, f'{doc.page} / 2')
    canvas.restoreState()

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    story = []
    story += [p('Paris Street Combat', 'title'),
              p('Assignment 3: MVP Implementation &amp; Demo | 10 October 2026<br/>'
                'Yupu Guo (yg745), Group Leader | Yuqi Pu (yp549) | Jingdi Wu (jw2046)', 'meta')]
    story += [heading('1. Plan vs. Reality'),
              p('Following the completed and approved Assignment 2, we built the core technical '
                'slice: animation, collision, navigation and independent NPC decisions working '
                'together in the Paris environment. The playable mission starts across the river: '
                'cross the bridge with two allies, defeat three German guards and capture G1. '
                'A highlighted safe zone then offers a consent-based checkpoint save. Loading '
                'restores progress and resources; player death supports mission restart.')]
    story += [table([
        ['<b>Graphics pillar</b>', '<b>Implemented and verified in the MVP</b>'],
        ['<b>Animation</b>', 'Player walk/run/slow movement, crouch, crawl, jump, aim, fire and reload; '
         'NPC movement/combat and death. Weapon events conserve ammunition, and saved corpses '
         'restore directly to the terminal death pose.'],
        ['<b>Collision Detection</b>', 'Character/environment collision blocks movement. Camera-to-aim '
         'and muzzle-to-aim traces resolve cover, soldier obstruction and damage. Health and '
         'ammunition displays read the same authoritative gameplay state.'],
        ['<b>Pathfinding and Navigation</b>', 'UE NavMesh/MoveTo drives real character travel. Map '
         'surveys and formal-character tests established the mission route and bridge crossing; '
         'allies follow/regroup at distinct goals, with bounded replanning and blocked-path recovery.'],
        ['<b>NPC AI / Behavior Trees</b>', 'Shared behavior definitions use separate controllers and '
         'Blackboards. Faction/perception drives engagement, remembered targets, timed search '
         'and return to duty; squad goals, reservations and death cleanup coordinate allies.'],
    ], [129, 397])]
    story += [Spacer(1, 6),
              p('<b>Result and scope changes.</b> All four pillars are complete and accepted for '
                'the current MVP, supported by retained tests and manual review. The midterm '
                'ends at G1; city-center occupation and later '
                'stages are deferred. Checkpoints moved from Should to implemented. We use UE '
                'navigation rather than the optional custom tactical A*. The initial roster '
                'remains one player, two allies and three guards.')]
    story += [heading('2. Technical Verification and Performance'),
              p('Implementation uses UE 5.8.2, existing Animation Blueprints, native C++ gameplay '
                'and presentation modules, character collision/traces, NavMesh/MoveTo and '
                'Behavior Trees. Retained stage-specific evidence includes the October 2 '
                'combat/HUD regression (15 cases, 62 assertions), October 3 player-action '
                'regression (16 scenarios, 66 assertions), October 7 NPC acceptance B00-B05, '
                'and subsequent G1/save/load/restart and manual checks. Validation spans dated '
                'builds with the scopes recorded in each test receipt. A teammate also confirmed '
                'the shared game runs and is playable '
                'on a second computer.', 'small')]
    story += [p('<b>Target:</b> 60 FPS at 1920 x 1080 on i9-12900F / RTX 3080 / 32 GB Windows PC. '
                'Measured at High, ray tracing/VSync off, uncapped, with the existing roster. '
                'Ready baselines use offscreen rendering.', 'small')]
    story += [table([
        ['<b>10 October measurement</b>', '<b>Mean FPS</b>', '<b>Mean / p95 frame time</b>'],
        ['Normal audio V2, stationary Ready<br/>3 runs; 30 s warmup, then 91-93 s each',
         '101.04 / 101.16 / 102.14', '9.90 / 11.04 ms<br/>9.89 / 11.14 ms<br/>9.79 / 10.78 ms'],
        ['Separate V6 input-helper run<br/>Crossing to Won, approximately 60.26 s',
         '94.08', '10.63 / 12.20 ms'],
    ], [266, 109, 151])]
    story += [Spacer(1, 5),
              p('Ready measurements test rendering with NPC brains gated off. The helper run '
                'includes telemetry overhead and approximate phase alignment. Means exceed '
                'the target in these measured windows, not every frame or arbitrary NPC load. '
                'Its whole capture retains an 8.47 s loading hitch. The approved video shows '
                'live UE timing/RAM/VRAM counters during the existing-roster workload, including '
                'roughly 8 s load/restart stalls and a brief texture-budget warning; diagnostics, '
                'input assistance and OBS add overhead. This reports local limits without '
                'claiming an isolated hardware cause or large-population capacity.', 'small')]

    story += [PageBreak(), heading('3. AI Utility'),
              p('<b>First, we tried GPT-assisted detailed modeling.</b> The team had no professional '
                '3D modeling experience. Repeated AI-designed/executed character trials, including '
                'a 38-iteration experiment, did not produce assets meeting this project\'s '
                'production needs. We stopped that route and moved to existing assets.'),
              p('<b>We then purchased existing licensed assets.</b> This provided substantially '
                'better base models, but they were not ready to integrate unchanged. Hands, '
                'weapons, character poses and animations needed fitting. The initial set lacked '
                'a suitable German rifle and corresponding effects/audio. We addressed these '
                'gaps incrementally through compatible assets, bounded adaptation, attachments, '
                'event timing and in-game verification. Model processing and adaptation took '
                'approximately <b>10 working days (team estimate)</b>, longer than expected. '
                'The current build integrates armed NPCs, muzzle effects and gameplay sound.'),
              p('<b>Value and cost.</b> ChatGPT/Codex helped turn requirements into code, diagnose '
                'engine/import issues, build validation tools and document failures. ImageGen '
                'helped with concept and HUD references; the playable HUD implements the '
                'approved design. Detailed runtime models primarily come from purchased assets. '
                'AI was useful for implementation and '
                'diagnostics, while modeling retries and asset integration consumed more time '
                'than planned. AI narration is a '
                'demo-production aid. The proposal did not commit to runtime LLM/API calls: '
                'NPC decision-making runs locally through UE Behavior Trees.')]
    story += [heading('4. Roadmap to Final'), table([
        ['<b>Remaining work</b>', '<b>Next implementation and verification</b>'],
        ['<b>Reload sleeve obstruction</b>', 'Correct the sleeve that still occludes the first-person '
         'camera during reload. Preserve accepted models, finger poses and weapon/ammunition '
         'transactions; verify the complete action in motion.'],
        ['<b>HUD refinement</b>', 'Improve layout, visual details, feedback and readability across '
         'resolutions while retaining the working health, ammunition, minimap and checkpoint UI.'],
        ['<b>Richer gameplay</b>', 'Extend the G1 loop with reviewed mission stages, encounter pacing, '
         'route choices and squad cooperation. Decide specific additions through design review.'],
        ['<b>More NPCs and stress tests</b>', 'Extend multiple-squad roles, target assignment, '
         'perception/attack, congestion recovery and mission lifecycle. Test increasing '
         'populations for behavior correctness, frame times, memory and stalls. Current '
         'small-roster acceptance does not establish this future capacity.'],
    ], [129, 397])]
    story += [heading('5. Deliverables and Access'),
              p('<b>Playable Windows build:</b> selected audio V2, '
                '<b>Paris-G1-Audio-V2-20261009.zip</b> (8.48 GB), with executable, cooked assets '
                'and runtime prerequisites. Use the separately supplied private course attachment '
                '<b>SFTPAccess_20261010</b>: run <b>DOWNLOAD_GAME.cmd</b>, wait for download and '
                'SHA-256 verification, extract the entire game archive, then run '
                '<b>PLAY_G1_REVISION.cmd</b>. Windows OpenSSH is required for download; allow at '
                'least 18 GB free disk space. Credentials stay outside this report and public Git.', 'small'),
              p('Private SFTP is the selected alternative to the specified Drive/itch.io channel; '
                'instructor approval of that channel remains to be confirmed. The hosting PC '
                'must remain online. Course attachment upload and independent reviewer download '
                'are separate from the teammate playability check.', 'small'),
              p('<b>Real-time demo (2:38):</b> ' + link(VIDEO, VIDEO) + '<br/>'
                'English embedded captions, AI voiceover and live performance display; includes '
                'checkpoint restore and enemy-caused player death/restart. Normal-speed input '
                'assistance, separate takes and cuts are disclosed. The 30 FPS video export '
                'rate is separate from game FPS.', 'small'),
              p('<b>Public source:</b> ' + link(REPO, REPO) + '<br/>'
                'README links the build/restoration workflow; the ' +
                link(REPO + '/blob/main/Docs/Development/TEAM_CURRENT_BUILD_20261009.md',
                     'current-build guide') + ' identifies the selected 42-file source and '
                'licensed dependencies. Public source does not include commercial asset bytes; '
                'restore authorized assets before rebuilding.', 'small')]
    doc = SimpleDocTemplate(str(OUT), pagesize=letter, leftMargin=43, rightMargin=43,
                            topMargin=37, bottomMargin=47,
                            title='Paris Street Combat - Assignment 3 MVP Progress Report',
                            author='Yupu Guo; Yuqi Pu; Jingdi Wu',
                            subject='Four-pillar MVP, implementation evidence, AI utility and roadmap')
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(json.dumps({'pdf': str(OUT), 'bytes': OUT.stat().st_size}))

if __name__ == '__main__':
    main()
