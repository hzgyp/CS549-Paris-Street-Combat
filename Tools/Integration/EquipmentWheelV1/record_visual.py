from pathlib import Path
import sys
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'Tools/Integration/TacticalEquipmentV1'))
from prepare import read,write,sha,OUT
rev=sys.argv[1];epoch=sys.argv[2];game=read(OUT/rev/'runtime.json')['game_sha256']
paths=[OUT/'checks'/('wheel_'+epoch)/'01_selected_frag.png',OUT/'checks'/('wheel_'+epoch)/'02_hold.png',OUT/'checks'/('wheel_'+epoch)/'03_final_hud.png',root/'tmp/g1-combat-ui-20261011/checks'/('ui_pages_'+epoch)/'05_help_2.png']
write(root/'tmp/g1-equipment-wheel-20261011/VISUAL_REVIEW.json',dict(status='reviewed_actual_hud_and_help_with_inherited_hand_limit',game_sha256=game,images=[dict(path=p.relative_to(root).as_posix(),size_bytes=p.stat().st_size,sha256=sha(p)) for p in paths],review=['Three slots and actual selected underline align; counts match real inventory.','Rifle selected after empty smoke has no stale NO GRENADES message.','Equipment controls page has WHEEL / LEFT MOUSE / ESC-WHEEL, correct rows and no G/Q instructions.','Held exterior remains at original low hand/frame position; no new model/contact/motion acceptance.'],scope='Actual final Game images in explicit isolated input/UI fixtures; not manual whole-game acceptance'))
print('ACTUAL VISUAL REVIEW RECORDED')
