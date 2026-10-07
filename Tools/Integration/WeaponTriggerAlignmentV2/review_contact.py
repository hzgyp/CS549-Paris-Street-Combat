"""Private diagnostic contact sheets and unchanged native guards, not game adoption."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE=STORE/'Evidence/WeaponTriggerAlignmentV2'
OUT=BASE/'review_v1';assert not OUT.exists();OUT.mkdir()
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22);big=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',32)
def tile(sheet,path,x,y,w,h,label):
    src=Image.open(path).convert('RGB');src.thumbnail((w,h-35));sheet.paste(src,(x+(w-src.width)//2,y+35+(h-35-src.height)//2))
    ImageDraw.Draw(sheet).text((x+8,y+5),label,font=font,fill='white')
reports={}
for identity in ('pivot_fit_v2','index_pose_v1'):
    data=json.loads((BASE/identity/'result.json').read_text());assert not data['errors'] and data['inputs_unchanged'];reports[identity]=data
    sheet=Image.new('RGB',(1600,((len(data['views'])+3)//4)*345),(38,38,38))
    for i,v in enumerate(data['views']):tile(sheet,BASE/identity/v['file'],(i%4)*400,(i//4)*345,400,345,f"{v['phase_s']} {v['condition']} {v['view']}")
    sheet.save(OUT/(identity+'_all_views.png'))
# Use exact V2 rerendered original and same camera after, avoiding mixed presets.
sheet=Image.new('RGB',(1800,1180),(38,38,38));draw=ImageDraw.Draw(sheet)
draw.text((20,8),'右食指对扳机／左手支撑：本轮校准（离线对比，尚未写入游戏）',font=big,fill='white')
tile(sheet,BASE/'pivot_fit_v2/0.0_original_left.png',0,60,900,650,'原枪位＋原姿态')
tile(sheet,BASE/'index_pose_v1/0.0_existing_index_pose_v3_left.png',900,60,900,650,'扳机支点校准＋复用现有三节食指姿态')
tile(sheet,BASE/'pivot_fit_v2/0.0_original_whole.png',0,710,900,300,'原双手关系')
tile(sheet,BASE/'index_pose_v1/0.0_existing_index_pose_v3_whole.png',900,710,900,300,'左掌已贴回枪身；左臂未改动')
draw.text((20,1030),'八相位：食指穿木托／护圈均为0；扳机薄片仍有表面交叉，未宣称完全无穿模。',font=font,fill=(255,190,110))
draw.text((20,1080),'模型、权重、源动作、镜头未改；仅局部三节右食指旋转复用。未选入正式游戏／NPC。',font=font,fill='white')
sheet.save(OUT/'before_after.png')
rows=json.loads((STORE/'Evidence/ReloadIndexContactV6/map_recovery_v1/result.json').read_text())['files'];assert len(rows)==528
changes=[x['path'] for x in rows if (ROOT/x['path']).stat().st_size!=x['size_bytes'] or hashlib.sha256((ROOT/x['path']).read_bytes()).hexdigest()!=x['sha256']];assert not changes,changes
r={'status':'diagnostic_evidence_composed_current528_unchanged_pending_visual_inspection','guard_count':528,'guard_changes':changes,
 'guard_snapshot':'Evidence/ReloadIndexContactV6/map_recovery_v1/result.json','formal_selection':False,'native_authored':False,
 'pivot_views':len(reports['pivot_fit_v2']['views']),'index_pose_views':len(reports['index_pose_v1']['views']),
 'remaining':'Blade22 crossing triangles; native dynamic/idle/locomotion/transition/nearwall tests not performed',
 'pose_source':'Existing D059 target2.2s local rotations ONLY index_01/02/03_r; no source mutation/left IK'}
(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
