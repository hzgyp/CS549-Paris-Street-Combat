"""Create the private two-page Assignment 3 progress report from dated facts."""
import argparse
import json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MVPCloseoutV1'
NAVY = HexColor('#152B40'); TEAL = HexColor('#117A77'); INK = HexColor('#243747')
MUTED = HexColor('#506372'); PALE = HexColor('#EAF2F4'); ORANGE = HexColor('#A84E17')
BODY = ParagraphStyle('body', fontName='Helvetica', fontSize=10, leading=14, textColor=INK)
SMALL = ParagraphStyle('small', parent=BODY, fontSize=8.8, leading=12)
HEAD = ParagraphStyle('head', parent=BODY, fontName='Helvetica-Bold', textColor=NAVY)

def paragraph(c, text, x, top, width, style=BODY):
    p = Paragraph(text, style); _, h = p.wrap(width, 800); p.drawOn(c, x, top-h); return top-h

def heading(c, text, top):
    c.setFillColor(TEAL); c.setFont('Helvetica-Bold', 12); c.drawString(44, top, text); return top-18

def base(c, page):
    c.setFillColor(NAVY); c.rect(0, 740, 612, 52, fill=1, stroke=0)
    c.setFillColor(white); c.setFont('Helvetica-Bold', 17); c.drawString(44, 765, 'PARIS STREET COMBAT')
    c.setFont('Helvetica', 9); c.drawString(44, 749, 'CS549  |  Assignment 3 progress  |  8 October 2026')
    c.setStrokeColor(PALE); c.line(44, 42, 568, 42)
    c.setFillColor(MUTED); c.setFont('Helvetica', 8)
    c.drawString(44, 28, 'G1 bridgehead MVP  |  Deadline: 13 October 2026  |  Local progress report')
    c.drawRightString(568, 28, f'{page} / 2')

def table(c, rows, top, widths):
    cells = [[Paragraph(v, SMALL if i else HEAD) for v in row] for i, row in enumerate(rows)]
    t = Table(cells, colWidths=widths, hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LINEBELOW',(0,0),(-1,-1),.4,PALE)]))
    _, h = t.wrap(524, 700); t.drawOn(c, 44, top-h); return top-h

def main():
    p = argparse.ArgumentParser(); p.add_argument('--identity', default='progress_v1'); a = p.parse_args()
    delivery=json.loads((STORE/'delivery_v1/delivery_receipt.json').read_text())
    assert delivery['status']=='private_review_bundle_prepared_not_selected' and delivery['media_status']=='pending'
    folder = STORE / a.identity / 'output/pdf'; folder.mkdir(parents=True, exist_ok=True)
    path = folder / 'Paris_Street_Combat_Assignment3_Progress.pdf'
    c = canvas.Canvas(str(path), pagesize=(612,792)); c.setTitle('Paris Street Combat - Assignment 3 Progress')
    c.setAuthor('Paris Street Combat team')
    base(c,1); y = heading(c,'Plan vs. reality',716)
    y = paragraph(c, 'The midterm slice is a squad crossing bridge C and capturing the G1 guards, with '
        'safe checkpoints and restart. The city-centre campaign is deferred. The prototype uses the '
        'existing licensed Paris environment, soldier rigs, accepted grips and original weapon actions.',44,y,524)-14
    y = table(c,[['Commitment','Evidence and present limit'],
        ['Complete mission and saves','Private candidate: three original squad/capture/Won-save/fresh-load '
         'cycles, two full restarts and three correct-checksum old-configuration rejections pass. Human '
         'play and final release selection remain open.'],
        ['Animation','Accepted native first-person, Allied and German presentations retained. Original locomotion '
         'and original rifle transactions retained. Full human motion/contact review remains open.'],
        ['Collision and navigation','One physically witnessed bridge polygon is excluded natively; agent-feet '
         'preflight and far-bank settling are corrected. Original capsules, speed, 55 cm / 25 s arrival '
         'bounds and physical geometry remain. No full-map guarantee.'],
        ['NPC AI / Behavior Trees','One G1 planning node uses native agent coordinates; other BT classes and '
         'per-NPC state stay original. Two Allies regroup in 11.61-12.30 seconds. Natural two-sided combat '
         'in the combined packaged fixture remains unproved.'],
        ['Playable Windows delivery','UE 5.8.2 Windows Development cook and native six-person Ready startup pass '
         'at actual 1920 x 1080. Human full playthrough and teammate-machine checks remain open.']
        ],y,[130,394])-20
    y = heading(c,'Measured performance: target not met',y)
    y = paragraph(c,'i9-12900F / RTX 3080 10 GB / 32 GB; High quality, 100% screen percentage, '
        '1920 x 1080, hardware ray tracing OFF, VSync off, uncapped, 1536 MiB texture pool. Three complete '
        'V13 native CSVs after 20 s warmup include all route/combat hitches; recording is separate.',44,y,524,SMALL)-12
    y = table(c,[['Run','Frames / seconds','Mean ms','p95 ms','Max ms','FPS'],
        ['1','1602 / 30.808','19.23','27.48','75.05','52.00'],
        ['2','1551 / 30.078','19.39','26.08','63.43','51.57'],
        ['3','1554 / 30.347','19.53','26.69','75.13','51.21']],y,[44,150,80,80,80,90])-10
    y = paragraph(c,'The 60 FPS target is unmet; render-thread critical time is about 19 ms. A separate '
        'initial six-person entry measures 53.40 FPS (1631 frames / 30.546 s). The predeclared 6 / 12 / 18 '
        'schedule stops at six; 12 / 18 are unmeasured. Original guard deaths remain, so this is not '
        'sustained six-active capacity. Offscreen Development instrumentation overhead is disclosed.',44,y,524,SMALL)
    assert y>52, ('Page 1 overflow',y)
    c.showPage(); base(c,2); y = heading(c,'AI utility',716)
    y = paragraph(c,'Codex assists with source and dependency audits, Unreal integration code, bounded '
        'diagnostics, test instrumentation, failure analysis and documentation. No runtime LLM or API '
        'is required. Finished licensed assets supply the detailed soldiers and environment.',44,y,524)-10
    y = paragraph(c,'The team stopped an AI-led detailed character-production experiment after 38 iterations '
        'without an acceptable production character. That experience informed the asset-first approach. '
        'Recent testing also exposed a false inference: a complete navigation query or SquadFailed=false '
        'does not establish physical squad arrival. Raw failures and narrower successful results remain '
        'separate; scripted tests do not replace human visual acceptance.',44,y,524)-20
    y = heading(c,'Roadmap to the deadline',y)
    y = table(c,[['Planned window','Exit condition'],
        ['8-10 October','Review the tested functional candidate without further hand/model polish. '
         'Run human action/collision regressions and investigate the measured render-thread limit '
         'through a separately bounded optimization plan.'],
        ['10-11 October','Run the predeclared finite 6 / 12 / 18-combatant stress schedule only after '
         'site and functional admission. Record actual limits and matched independent/coordinated '
         'navigation evidence after the initial performance stop is resolved. Teammates perform '
         'second-machine restoration and play verification.'],
        ['11-12 October','Freeze matching build/source/asset identities. Record a 2-3 minute real-time '
         'annotated demo including the stress limit; update this report and verify reviewer access.'],
        ['13 October','User reviews and submits the tested build/run instructions, video, source and '
         'progress PDF. Dates are planned work windows, not completed tests.']],y,[126,398])-20
    y = heading(c,'Delivery and course status',y)
    y = paragraph(c,'<b>Source:</b> <link href="https://github.com/hzgyp/CS549-Paris-Street-Combat" '
        'color="#117A77">github.com/hzgyp/CS549-Paris-Street-Combat</link>. Published baseline '
        '<font name="Courier">b8a3a6a</font>; the review bundle carries the uncommitted candidate SourcePatch. '
        'Commercial asset bytes are excluded and require the separate licensed private restore.',44,y,524)-10
    y = paragraph(c,'<b>Playable build:</b> a private local Win64 review ZIP includes controls, source patch '
        'and verified cooked-file hashes; it is not a selected release. '
        '<b>Video:</b> pending. Four recording routes failed cadence, readback, GPU-startup or visual-content '
        'admission; no invalid capture is delivered as a demo. Reviewer download and video links are '
        'not verified. Three-member sharing is confirmed; wider finished-product access is unresolved.',44,y,524)-10
    y = paragraph(c,'<b>Course information:</b> the user confirms Assignment 2 and the 13 October 2026 '
        'Assignment 3 deadline. Mentor confirmation was not separately supplied. '
        'This report records progress and open gates; it does not claim submission readiness.',44,y,524)-14
    y = paragraph(c,'Evidence: candidate_agent_v1 / instrument_v13; agent_plain_v1; stress_6_v1; '
        'plain_recovery_v1; private delivery receipt. MI004-MI011 retain route, squad, preflight, '
        'performance and recording failures. No incomplete CSV or invalid movie is acceptance evidence.',44,y,524,SMALL)
    assert y>52, ('Page 2 overflow',y)
    c.save(); print(path)

if __name__=='__main__': main()
