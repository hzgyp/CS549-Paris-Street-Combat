"""Label real rendered views and verify private data/current guard epoch."""
import ast,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,read,write,row,sha,guards
BASE=STORE/'Evidence/GermanNPCAlliedGripV13';SRC=BASE/'presentation_v2';OUT=BASE/'review_sheets_v1'
assert not OUT.exists();OUT.mkdir(parents=True)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
def sheet(name,stages,views):
    width=900;height=638;header=60;footer=70
    canvas=Image.new('RGB',(len(views)*width,len(stages)*(height+header)+footer),(31,35,41));draw=ImageDraw.Draw(canvas)
    for j,stage in enumerate(stages):
        for k,view in enumerate(views):
            x=k*width;y=j*(height+header)
            image=Image.open(SRC/(stage+'_'+view+'.png')).convert('RGB');image.thumbnail((width,height))
            canvas.paste(image,(x+(width-image.width)//2,y+header))
            label=('仅参数复用 / 未采用' if stage=='transfer' else '整体对位对照 / 未采用')+' · '+view
            draw.text((x+16,y+12),label,font=font,fill=(231,235,240))
    draw.text((18,canvas.height-55),'仅静态接触诊断：保留原骨长、模型和权重；衣袖边界为展示隔离，不是游戏裁切；尚未通过完整握合/UE验收。',font=small,fill=(215,222,229))
    dest=OUT/name;canvas.save(dest,quality=93);return row(dest)
images=[sheet('three_views_comparison.jpg',('transfer','seating'),('right','reverse','top')),
        sheet('trigger_support_comparison.jpg',('transfer','seating'),('trigger','support','under')),
        sheet('full_context_comparison.jpg',('transfer','seating'),('context',))]
results=[]
for relative in ('probe_v1','probe_v2','transfer_fit_v2','seating_v3','gray_v3','textured_v3','presentation_v2'):
    p=BASE/relative/'result.json';r=read(p);assert not r['errors']
    assert r['guards_after']==618 and r['inputs_unchanged']
    results.append(row(p))
    for e in r.get('images',[]):assert sha(ROOT/e['path'])==e['sha256']
    # Development-time source edits are recorded separately from immutable
    # asset/data protection; don't relabel earlier script revisions exact.
    mismatches=[e['path'] for e in r.get('inputs',[]) if sha(ROOT/e['path'])!=e['sha256']]
    assert not [p for p in mismatches if not p.startswith('Tools/')],mismatches
    if mismatches:r['historical_tool_revision_changes_observed_read_only']=mismatches
    # Never rewrite the earlier receipt with the derived observation.
    results[-1]['historical_tool_revision_changes']=mismatches
tools=list(Path(__file__).parent.glob('*.py'))
for p in tools:ast.parse(p.read_text(encoding='utf-8'))
write(OUT/'result.json',{'status':'parameter_reuse_verified_complete_grip_not_accepted',
  'guard_count':guards(),'results':results,'sheets':images,'tools':[row(p) for p in tools],
  'source_modified':False,'native_tested':False,'formal_selected':False,
  'one_seating_comparison_stopped':True,'known_portable_jacket_material_parity_limit':True})
print('618 guards exact; pose/data and images checked; tools parsed; whole contact remains unaccepted')
