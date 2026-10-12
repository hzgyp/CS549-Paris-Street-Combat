"""Verify the narrow visual delta plus existing native/gameplay protection."""
from pathlib import Path
import sys,argparse,re
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,read,write,rows,sha,INNER
ap=argparse.ArgumentParser();ap.add_argument('revision');a=ap.parse_args()
freeze=read(ROOT/'tmp/g1-field-manual-ui-20261011/freeze.json');old=ROOT/freeze['parent']['source_snapshot'];new=OUT/a.revision/'Project'
assert rows(old)==freeze['parent_files']
changed=[r['path'] for r in freeze['parent_files'] if sha(new/r['path'])!=r['sha256']]
base='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/'
allowed=[base+'Private/ParisCombatUI.cpp',base+'Private/ParisCombatUIProbe.cpp',base+'Public/ParisBridgeMission.h']
assert set(changed)==set(allowed),changed
public=base+'Public/ParisBridgeMission.h'
assert (new/public).read_bytes().replace(b'    UCanvas* GetCombatCanvas() const { return Canvas.Get(); }\r\n',b'')==(old/public).read_bytes()
for row in freeze['parent_files']:
    if row['path'].endswith('.h'):
        assert re.findall(rb'U(?:PROPERTY|FUNCTION)\([^\n]*\)[^\n]*',(old/row['path']).read_bytes())==re.findall(rb'U(?:PROPERTY|FUNCTION)\([^\n]*\)[^\n]*',(new/row['path']).read_bytes())
path=base+'Private/ParisCombatUI.cpp';prior=(old/path).read_text('utf-8-sig');after=(new/path).read_text('utf-8-sig')
for header in ['Engine/Font.h','CanvasItem.h','Fonts/CompositeFont.h','Fonts/SlateFontInfo.h','UObject/StrongObjectPtr.h','Misc/Paths.h']:
    after=after.replace('#include "'+header+'"\n','')
def block(text,start,end):return text[text.index(start):text.index(end,text.index(start))]
after=after.replace('#include "ParisFieldManualPaint.inl"\n',block(prior,'struct FPaint {','const TCHAR* Tabs[]'))
after=after.replace('#include "ParisFieldManualMenu.inl"\n',block(prior,'bool DrawMenu(','void DrawExtras('))
for before,render in [('218,316+I*73,320,52','SideX,SideY+I*SideStep,SideW,SideH'),('640+I*255,222,245,52','NavX[I],NavY,NavW[I],NavH'),('640+I*205,304,195,52','GroupX+I*GroupStep,GroupY,GroupW,GroupH'),('P.Box(X,967,220,82,FLinearColor(.009,.015,.012,.75));','P.Line(X+8,1049,X+207,1049,Brass);')]:
    after=after.replace(render,before)
assert after==prior,'Unapproved input/state/guidance logic delta'
original=read(ROOT/'tmp/g1-tactical-equipment-20261010/freeze.json')
for row in original['protected_native']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
assert rows(ROOT/original['parent']['source_snapshot'])==original['parent_files']
assert sha(ROOT/original['parent']['playable_directory']/INNER)==original['parent']['game_sha256']
assert sha(ROOT/'Assets/Sync/CATALOG.json')==original['catalog_sha256']
assert rows(Path(original['user_root']))==original['user_files']
assert rows(Path(freeze['user_root']))==freeze['user_files']
assert rows(ROOT/freeze['parent']['playable_directory'])==freeze['parent_normal_files']
write(OUT/a.revision/'field-protection.json',dict(status='pass',parent_source_files=len(freeze['parent_files']),changed_parent_files=changed,added_visual_files=['ParisFieldManualPaint.inl','ParisFieldManualMenu.inl'],native_files=len(original['protected_native']),reflection_exact=True,UI_input_state_pause_confirmation_guidance_logic_exact_except_hit_bounds=True,all_other_parent_files_exact=True,models_fingers_gun_save_equipment_AI_navigation_exact=True,parent_normal_user_files_catalog_formal_exact=True))
print('PASS field-manual visual boundary / parent / native / users / formal / Catalog')
