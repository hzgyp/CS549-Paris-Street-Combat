"""Record a completed manual frame inspection; run only after inspecting these images."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,read,write,sha
base=ROOT/'tmp/g1-combat-ui-20261011'; dest=base/'VISUAL_REVIEW.json'
assert not dest.exists()
runtime=read(OUT/'candidate_ui_v5/runtime.json')
images=[]
for identity in ['ui_pages_v5','ui_pages_small_v5']:
    files=sorted((base/'checks'/identity).glob('*.png'));assert len(files)==10
    for p in files:images.append(dict(path=p.relative_to(ROOT).as_posix(),size_bytes=p.stat().st_size,sha256=sha(p)))
for p in [base/'checks/ui_confirm_v5/01_restart_confirmation.png',base/'checks/ui_equipment_pause_v5/01_live_frag_pause.png',OUT/'checks/throw_ui_v5/01_prepare.png',OUT/'checks/interactions_ui_v5/supply_empty.png',OUT/'checks/enemy_clear_ui_v5/saved_window.png',OUT/'checks/enemy_clear_ui_v5/clean_hud.png']:
    assert p.is_file();images.append(dict(path=p.relative_to(ROOT).as_posix(),size_bytes=p.stat().st_size,sha256=sha(p)))
write(dest,dict(status='pass',reviewed_by='Codex actual image inspection on 2026-10-11',game_sha256=runtime['game_sha256'],scope='Actual final Game frames; 1080p/720p core pages and help groups, confirmation, paused live equipment, active throw/supply guidance, real save success and clean post-save HUD. Title/category/data match; no clipping or hint overlap; saved E tutorial absent after success. Not human play/whole aspect-ratio/device acceptance.',images=images))
print(dest)
