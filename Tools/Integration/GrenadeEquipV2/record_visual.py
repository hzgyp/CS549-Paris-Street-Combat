from pathlib import Path
import sys
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'Tools/Integration/TacticalEquipmentV1'))
from prepare import read,write,sha,OUT
rev=sys.argv[1];epoch=sys.argv[2];game=read(OUT/rev/'runtime.json')['game_sha256'];folder=OUT/'checks'/('wheel_'+epoch)
paths=[folder/x for x in ['01_frag_ready.png','02_frag_hold.png','03_smoke_ready.png','04_smoke_hold.png','05_all_empty_rifle.png']]
write(root/'tmp/g1-grenade-equip-20261011/VISUAL_REVIEW.json',dict(status='reviewed_actual_grenade_ready_hold_and_empty_rifle',game_sha256=game,images=[dict(path=p.relative_to(root).as_posix(),size_bytes=p.stat().st_size,sha256=sha(p)) for p in paths],review=['Frag grid body/lever visible with actual hand; no rifle-ready gesture.','Smoke exterior and yellow band visible with actual hand in ready/hold.','All depleted stays on rifle with both zero counts; no empty-hand transition.','No hand rendering hidden in normal entry; old diagnostic pairs retained privately.'],scope='Actual final Game, isolated existing-roster input fixture; not full contact/continuous motion or human approval'))
print('ACTUAL VISUAL REVIEW RECORDED')
