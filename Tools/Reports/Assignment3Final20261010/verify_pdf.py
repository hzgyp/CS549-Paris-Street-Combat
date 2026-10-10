"""Validate report structure, copied measurements, links, bounds and font embeds."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import pdfplumber
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[3]
PDF = ROOT / 'output/pdf/Paris_Street_Combat_Assignment3_20261010_EN.pdf'
QA = ROOT / 'tmp/pdfs/assignment3-final-20261010'
REPO = 'https://github.com/hzgyp/CS549-Paris-Street-Combat'
PATHS = [
    'Docs/Development/TEAM_CURRENT_BUILD_20261009.md',
]

reader = PdfReader(PDF)
assert len(reader.pages) == 2, 'Course requires 1-2 pages; layout expects 2'
pages = [page.extract_text() for page in reader.pages]
text = '\n'.join(pages)
flat = ' '.join(text.split())
required = [
    'Plan vs. Reality', 'Technical Verification and Performance', 'AI Utility',
    'Roadmap to Final', 'Deliverables and Access', 'Animation',
    'Collision Detection', 'Pathfinding and Navigation', 'NPC AI / Behavior Trees',
    'All four pillars are complete', '10 working days (team estimate)',
    'Reload sleeve obstruction', 'HUD refinement', 'Richer gameplay',
    'More NPCs and stress tests', 'DOWNLOAD_GAME.cmd', 'PLAY_G1_REVISION.cmd',
    'SFTPAccess_20261010', 'instructor approval of that channel remains to be confirmed',
    'player death/restart', 'a second computer', 'NPC brains gated off',
]
for phrase in required:
    assert phrase in flat, f'Missing required content: {phrase}'
assert flat.index('First, we tried GPT') < flat.index('We then purchased'), 'Wrong AI chronology'
assert 'Retained implementation records:' not in flat
assert not re.search(r'BEGIN .*PRIVATE KEY|cs549sftp|\b(?:\d{1,3}\.){3}\d{1,3}\b', text)
assert '\ufffd' not in text and '\u25a0' not in text

perf = json.loads((ROOT / 'tmp/assignment3-review-20261010/performance/SUMMARY.json').read_text())
for run in perf['runs']:
    for key in ('fps', 'mean_ms', 'p95_ms'):
        assert f'{run[key]:.2f}' in flat, f'Wrong normal metric {key}'
active = perf['dynamic_workload']['active_mission']
for key in ('fps', 'mean_ms', 'p95_ms', 'seconds'):
    assert f'{active[key]:.2f}' in flat, f'Wrong active metric {key}'
assert f"{perf['dynamic_workload']['max_ms'] / 1000:.2f}" in flat

expected_links = {REPO, 'https://youtu.be/SktbFHNYP54'} | {REPO + '/blob/main/' + p for p in PATHS}
links = []
for page in reader.pages:
    width, height = float(page.mediabox.width), float(page.mediabox.height)
    for ref in page.get('/Annots', []):
        annotation = ref.get_object()
        action = annotation.get('/A', {})
        if '/URI' in action:
            links.append(str(action['/URI']))
            x0, y0, x1, y1 = map(float, annotation['/Rect'])
            assert 0 <= x0 <= x1 <= width and 0 <= y0 <= y1 <= height
assert set(links) == expected_links

embedded_fonts = set()
for page in reader.pages:
    for ref in page['/Resources']['/Font'].values():
        font = ref.get_object()
        if '/FontDescriptor' in font:
            descriptor = font['/FontDescriptor'].get_object()
            if '/FontFile2' in descriptor:
                embedded_fonts.add(str(font['/BaseFont']))
assert len(embedded_fonts) >= 2

with pdfplumber.open(PDF) as doc:
    for index, page in enumerate(doc.pages):
        for word in page.extract_words():
            assert 35 <= word['x0'] <= word['x1'] <= page.width - 35
            assert 25 <= word['top'] <= word['bottom'] <= page.height - 18
        assert f'{index + 1} / 2' in pages[index]

remote = subprocess.run(['git', 'ls-remote', 'origin', 'refs/heads/main'], cwd=ROOT,
                        capture_output=True, text=True, check=True).stdout.split()[0]
for path in PATHS:
    subprocess.run(['git', 'cat-file', '-e', remote + ':' + path], cwd=ROOT, check=True)

result = {
    'status': 'automated_checks_pass_visual_review_required',
    'verified_at': datetime.now(timezone.utc).isoformat(),
    'pdf': str(PDF), 'bytes': PDF.stat().st_size,
    'sha256': hashlib.sha256(PDF.read_bytes()).hexdigest(), 'pages': len(reader.pages),
    'word_count': len(flat.split()), 'required_content': required,
    'measurement_source': 'tmp/assignment3-review-20261010/performance/SUMMARY.json',
    'links': links, 'verified_remote_main': remote,
    'linked_repository_files_exist_at_remote_main': PATHS,
    'embedded_fonts': sorted(embedded_fonts),
    'bounds_and_footer_check': 'pass', 'credential_text_check': 'pass',
    'scope': 'PDF production only; no new gameplay test, publication or course submission',
}
QA.mkdir(parents=True, exist_ok=True)
(QA / 'TEXT_EN.txt').write_text(text, encoding='utf-8')
(QA / 'VERIFICATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k:result[k] for k in ('status','pages','bytes','sha256','word_count')}))
