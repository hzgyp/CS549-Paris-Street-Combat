"""Apply the approved visual design to an immutable child of UI v5."""
from pathlib import Path
import sys, argparse, re
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import prepare,OUT,read,write,rows,sha
ap=argparse.ArgumentParser();ap.add_argument('revision');a=ap.parse_args()
base=ROOT/'tmp/g1-field-manual-ui-20261011';base.mkdir(exist_ok=True)
parent=read(ROOT/'Docs/Development/CURRENT_UI_REVIEW.json')
assert parent['game_sha256']=='95132229e0281acea0535e00ab2b54f22df749bba1ed4d976b00496da9325db9'
source=ROOT/parent['source_snapshot'];expected=read(ROOT/parent['source_manifest'])['files']
assert rows(source)==expected
if not (base/'freeze.json').exists():
    user=Path.home()/'AppData/Local/ParisStreetCombat'/parent['user_dir']
    write(base/'freeze.json',dict(parent=parent,parent_files=expected,parent_normal_files=rows(ROOT/parent['playable_directory']),user_root=str(user),user_files=rows(user)))
prepare(a.revision,'candidate_ui_v5')
project=OUT/a.revision/'Project'
assert all(sha(project/r['path'])==r['sha256'] for r in expected)
private=project/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
template=ROOT/'Tools/Integration/FieldManualUIV1'
for name in ['ParisFieldManualPaint.inl','ParisFieldManualMenu.inl']:
    (private/name).write_bytes((template/name).read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
cpp=private/'ParisCombatUI.cpp';text=cpp.read_text('utf-8-sig')
text=text.replace('#include "Engine/Canvas.h"','#include "Engine/Canvas.h"\n#include "Engine/Font.h"\n#include "CanvasItem.h"\n#include "Fonts/CompositeFont.h"\n#include "Fonts/SlateFontInfo.h"\n#include "UObject/StrongObjectPtr.h"\n#include "Misc/Paths.h"')
begin=text.index('struct FPaint {');end=text.index('const TCHAR* Tabs[]',begin)
text=text[:begin]+'#include "ParisFieldManualPaint.inl"\n'+text[end:]
begin=text.index('bool DrawMenu(');end=text.index('void DrawExtras(',begin)
text=text[:begin]+'#include "ParisFieldManualMenu.inl"\n'+text[end:]
assert text.count('218,316+I*73,320,52')==2
text=text.replace('218,316+I*73,320,52','SideX,SideY+I*SideStep,SideW,SideH')
text=text.replace('640+I*255,222,245,52','NavX[I],NavY,NavW[I],NavH')
text=text.replace('640+I*205,304,195,52','GroupX+I*GroupStep,GroupY,GroupW,GroupH')
text=text.replace('P.Box(X,967,220,82,FLinearColor(.009,.015,.012,.75));','P.Line(X+8,1049,X+207,1049,Brass);')
cpp.write_bytes(text.replace('\n','\r\n').encode())
public=private.parent/'Public/ParisBridgeMission.h';raw=public.read_bytes()
old=b'    virtual void DrawHUD() override;';assert raw.count(old)==1
public.write_bytes(raw.replace(old,old+b'\r\n    UCanvas* GetCombatCanvas() const { return Canvas.Get(); }'))
probe=private/'ParisCombatUIProbe.cpp';text=probe.read_text('utf-8-sig')
for old,new in [('Click(PC,950,248)','Click(PC,1185,171)'),('Click(PC,1280,248)','Click(PC,1385,171)'),('Click(PC,1530,248)','Click(PC,1565,171)'),('Click(PC,640+(Step-2)*205+70,330)','Click(PC,660+(Step-2)*205+70,388)'),('Click(PC,350,488)','Click(PC,350,494)'),('Click(PC,350,634)','Click(PC,350,662)'),('Click(PC,350,414)','Click(PC,350,410)'),('Click(PC,350,343)','Click(PC,350,326)')]:
    assert old in text,old;text=text.replace(old,new)
probe.write_bytes(text.replace('\n','\r\n').encode())
write(OUT/a.revision/'field-authoring.json',dict(parent=parent['source_snapshot'],status='independent_visual_candidate',changed='rendering/fonts/hit-coordinates/probe-coordinates/nonreflected_Canvas_accessor',native='no changes'))
print(project)
