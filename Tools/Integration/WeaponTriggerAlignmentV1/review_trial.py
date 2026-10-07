"""Compose fixed before/after diagnostic evidence and verify protected native bytes."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE=STORE/'Evidence/WeaponTriggerAlignmentV1'
OUT=BASE/'review_v1';assert not OUT.exists();OUT.mkdir()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
fit=json.loads((BASE/'trigger_fit_v1/result.json').read_text());assert not fit['errors'] and fit['inputs_unchanged']
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
big=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',33)
def tile(im,path,x,y,w,h,label):
    src=Image.open(path).convert('RGB');src.thumbnail((w,h-35));im.paste(src,(x+(w-src.width)//2,y+35+(h-35-src.height)//2))
    ImageDraw.Draw(im).text((x+12,y+3),label,font=font,fill='white')
sheet=Image.new('RGB',(1600,6*365),(38,38,38))
for i,v in enumerate(fit['views']):
    tile(sheet,BASE/'trigger_fit_v1'/v['file'],(i%4)*400,(i//4)*365,400,365,f"{v['phase_s']}s {v['condition']} {v['view']}")
sheet.save(OUT/'all_24_views.png')
comparison=Image.new('RGB',(1600,1090),(38,38,38));draw=ImageDraw.Draw(comparison)
draw.text((20,8),'枪位平移对比（手指、模型、源动作不变；尚未用于游戏）',font=big,fill='white')
for i,c in enumerate(('before','after')):
    tile(comparison,BASE/'trigger_fit_v1'/f'0.0_{c}_left.png',i*800,65,800,650,'调整前' if c=='before' else '仅调整枪位后')
    tile(comparison,BASE/'trigger_fit_v1'/f'0.0_{c}_whole.png',i*800,715,800,320,'整枪与支撑手（蓝色）')
draw.text((20,1045),'结果：食指靠近护圈，但仍未完全贴合；左支撑手悬空，候选不选入正式版本。',font=font,fill=(255,190,110))
comparison.save(OUT/'before_after.png')
rows=json.loads((STORE/'Evidence/ReloadIndexContactV6/map_recovery_v1/result.json').read_text())['files']
assert len(rows)==528
changes=[]
for row in rows:
    p=ROOT/row['path']
    if p.stat().st_size!=row['size_bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:changes.append(row['path'])
assert not changes,changes
report={'status':'trial_collected_native528_unchanged_visual_review_pending','guard_snapshot':'Evidence/ReloadIndexContactV6/map_recovery_v1/result.json',
 'guard_count':528,'guard_changes':changes,'all_images_opened':False,'native_selected':False,'finger_modified':False,
 'source_unchanged':fit['inputs_unchanged'],'translation_cm':fit['candidate']['gun_local_delta_cm'],
 'diagnostic_limit':'Area-weighted surface-region centroids, nominal clearance; not proof of exact solid contact. Fixed clip, not runtime blend.',
 'source_binding_review':{
 'allied':{'source':'Tools/Integration/ue_rifle_action_attachment_author.py','package':'/Game/ParisCombat/Blueprints/WeaponAttachmentV3/BP_PC_RifleAttachmentV3',
  'rule':'Right hollow excluding index, two-hollow heading, anchor(-LeftShiftCm,-8,0); no actual trigger landmark'},
 'german':{'source':'Tools/Integration/ue_german_rifle_author.py','package':'/Game/ParisCombat/Weapons/GermanRifleUEV1/BP_PC_GermanRifleAttachmentV2',
  'rule':'Independent German GripXYZ and two-hollow heading; no actual trigger landmark'},
 'npc_native_fit':'Not authored/tested: do not copy failed player translation; controllers/BT/BB unchanged.'}}
(OUT/'result.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'guard_count':len(rows),'guard_changes':changes,'images':len(fit['views'])}))
