"""Run only after inspecting the actual frames listed here."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,read,write,sha
base=ROOT/'tmp/g1-field-manual-ui-20261011';dest=base/'VISUAL_REVIEW.json';assert not dest.exists()
images=[]
for identity in ['ui_pages_field_v2','ui_pages_small_field_v2']:
    paths=sorted((ROOT/'tmp/g1-combat-ui-20261011/checks'/identity).glob('*.png'));assert len(paths)==10
    for p in paths:images.append(dict(path=p.relative_to(ROOT).as_posix(),size_bytes=p.stat().st_size,sha256=sha(p)))
for p in [ROOT/'tmp/g1-combat-ui-20261011/checks/ui_confirm_field_v2/01_restart_confirmation.png',ROOT/'tmp/g1-combat-ui-20261011/checks/ui_equipment_pause_field_v2/01_live_frag_pause.png',OUT/'checks/throw_ui_field_v2/01_prepare.png',OUT/'checks/interactions_ui_field_v2/supply_empty.png',OUT/'checks/enemy_clear_ui_field_v2/saved_window.png',OUT/'checks/enemy_clear_ui_field_v2/clean_hud.png']:
    assert p.is_file();images.append(dict(path=p.relative_to(ROOT).as_posix(),size_bytes=p.stat().st_size,sha256=sha(p)))
write(dest,dict(status='pass',game_sha256=read(OUT/'candidate_field_manual_v2/runtime.json')['game_sha256'],reviewed_by='Codex actual runtime image inspection on 2026-10-11',scope='Ten 1080p frames individually inspected; ten 720p frames reviewed in overview plus original-size help/settings and remaining original pages. Correct page/category/value content, contained titles/descriptions/keycaps/settings, aligned two-line rows; confirmation and active/save/hazard frames inspected. Not human/device/aspect-ratio acceptance.',images=images))
print(dest)
