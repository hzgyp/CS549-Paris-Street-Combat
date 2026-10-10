"""Document the old snapped turn only; never modify or run the observer."""
import subprocess
from PIL import Image,ImageDraw
from intake import ROOT,OUT,row,save_json
from inspect_refs import FF

raw=ROOT/'tmp/g1-demo-draft02-20261009/raw/2026-10-09 19-50-56.mkv'
folder=OUT/'old_footage_review';folder.mkdir(exist_ok=True)
times=[46.40,46.47,46.53,46.60,46.67,46.73]
sheet=Image.new('RGB',(1440,3*430),(18,18,18));d=ImageDraw.Draw(sheet)
for i,t in enumerate(times):
    p=folder/(f'turn_{t:.2f}.png')
    if not p.exists():subprocess.run([str(FF),'-nostdin','-v','error','-ss',str(t),'-i',str(raw),'-frames:v','1',str(p)],check=True)
    sheet.paste(Image.open(p).resize((720,405)),((i%2)*720,(i//2)*430))
    d.text(((i%2)*720+8,(i//2)*430+410),f'Existing raw {t:.2f}s',fill='white')
sheet.save(folder/'turn_sheet.png')
save_json(folder/'turn.json',dict(raw=row(raw,ROOT),frames=[row(folder/(f'turn_{t:.2f}.png'),folder) for t in times],
    step_prone_move_source_time=46.459,
    source='Unreal/Variants/G1PresentationAV20261009/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMissionV1.cpp',
    code_lines=[70,205,210],scope='Existing raw inspection only; user-facing turn correction deferred, observer unchanged'))
print('Old turn witness extracted; no new capture')
