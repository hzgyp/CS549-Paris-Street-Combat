"""Emit an apply_patch patch for fact-derived Markdown catalogs; never asset bytes."""
import collections
import difflib
import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[2]
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
F=load('Assets/LocalWorking/Validation/2026-10-03-asset-catalog-v1/Catalog/catalog_facts.json')
G=load('Assets/LocalWorking/Validation/2026-10-03-asset-catalog-v1/Guns/views_v1/weapon_library_inventory.json')
V='LocalWorking/Validation/2026-10-03-asset-catalog-v1'
names={'german':'German Soldier WWII','us':'US Paratrooper','rifle_old':'Rifle Animset Pro','d059':'D059 Rifle Pro - MoCap Pack','arms':'ShooterStarter FPS Arm A'}
locations={
 'german':'LocalShared/SFTP/baselines/character-original-intake/character-20261001-v1/CHAR-G-GermanSoldierWWII',
 'us':'LocalShared/SFTP/baselines/character-original-intake/character-20261001-v1/CHAR-A-USSoldier',
 'rifle_old':'LocalShared/SFTP/baselines/character-original-intake/character-20261001-v1/ANI-TP-RifleAnimsetPro',
 'd059':'LocalShared/SFTP/baselines/rifle-pro-mocap-original/rifle-motion-20261002-v1',
 'arms':'LocalWorking/Intake/2026-10-01/01_ShooterStarter_FPS_Arm_A'}
def safe(s):return str(s).replace('|','\\|').replace('\n',' ')
def size(n):return f'{n:,} B ({n/1024**3:.3f} GiB)'
def tab(headers,rows):return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |']+['| '+' | '.join(safe(v) for v in row)+' |' for row in rows])
def image(label,path):return f'![{label}](<{path}>)'
def catalog(zh):
    text=['# '+('闲鱼已下载资产详细清单' if zh else 'Downloaded Xianyu asset catalog'),'',
      '2026-10-03 · yg745 · '+('本机盘点，不是发布清单。' if zh else 'Local inspection; not a release manifest.'),'',
      ('范围：此前两批士兵/动作、ShooterStarter、D059、125包UE4动作合集及新MW2枪械库。巴黎地图另列背景依赖；现有记录指向Meshingun Studio/Fab，不能据此断言其交易渠道也是闲鱼。旧Normandy/Lux3D实验不列为可用生产资产。' if zh else
       'Scope: earlier soldier/action deliveries, ShooterStarter, D059, the 125-pack UE4 collection and the new MW2 gun library. Paris is listed separately as an existing dependency; its recorded origin is Meshingun Studio/Fab, not proof of a Xianyu transaction. Retired Normandy/Lux3D experiments are not production assets.'),'',
      ('本次：实际核对原文件存在/大小，读取125个压缩包内部目录，Blender安全打开新枪库并检查截图。旧UE类别/骨架/动作时长来自注明日期的实际加载记录，并非本次重新逐动作运行。资产名、宣传图、成功导入均不能证明历史正确或运行可用。' if zh else
       'This review checks delivered-file presence/sizes, reads all 125 archive headers, and safely opens/renders the gun library. Earlier UE class/rig/duration facts come from dated real-load records, not a new runtime test of every action. Names, previews and import success do not prove historical or runtime fitness.'),'',
      ('图片仅在本机私有目录中，Markdown直接引用已有图片，没有把商业资产或截图复制到Git。组员需要对应私有证据文件才能显示。新MW2包三人共享/来源授权尚未确认，保留LocalWorking；之前的共享确认不自动覆盖这次。' if zh else
       'Images reference existing private local files, with no commercial bytes/screenshots copied into Git. Teammates need those private files to display images. New MW2 provenance/three-member sharing is unconfirmed; it stays LocalWorking. Previous attestations do not cover it automatically.'),'',
      '## '+('1. 下载批次总览' if zh else '1. Delivery overview'),'']
    rows=[]
    for d in F['deliveries']:
        rows.append([names[d['key']],str(d['original_files']),size(d['original_bytes']),str(d['present']),locations[d['key']]])
    rows += [['UE4 animation collection','250','24,108,906,232 B','125 archives + 125 previews','LocalWorking/Intake/2026-10-01/03_UE4_Animation_Collection/'],['MW2_Guns_Asset_Library.blend','1',size(F['gun_source']['size_bytes']),'1','LocalWorking/Intake/2026-10-03/01_MW2_Guns_Asset_Library/']]
    text += [tab(['Bundle','Files','Original size','Present / coverage','Physical location relative to Assets'],rows),'',
      ('上表大小是原始交付，不要与整合版本相加当作唯一文件总量；整合文件、别名与对象版本有重叠。存在/大小核对不是本轮全旧包SHA校验。' if zh else 'Sizes refer to originals, not deduplicated total storage. Adaptations, aliases and hash objects overlap. Presence/size checks are not a new full-original SHA audit.'),'']
    for num,d in enumerate(F['deliveries'],2):
        key=d['key']; assets=d['assets']
        text += [f'## {num}. {names[key]}','',tab(['UE class','Count'],sorted(d['classes'].items())),'']
        status={
         'german':('有两套完整德军人物、无头/装备相关网格、7条原包动作、56张Texture2D。已修复整合基线在character-ue582-v1；德军平移动作适配有后续记录。MP40只是冲锋枪，不是德军步枪。','Two complete German variants plus no-head/equipment meshes, 7 delivered actions and 56 Texture2D assets. Repaired integration baseline is character-ue582-v1; later translation/locomotion adaptation is recorded separately. MP40 is an SMG, not a rifle.'),
         'us':('有两套完整美军伞兵、无头/装备网格、M1 Garand外观，5条原包动作、83张Texture2D。现有M1为一骨骼刚性外观，不能据此证明独立枪机/漏夹可动。','Two complete US paratrooper variants plus no-head/equipment meshes, M1 Garand appearance, 5 delivered actions and 83 Texture2D assets. Existing M1 is a one-bone rigid appearance model, not evidence of independent bolt/en-bloc motion.'),
         'rifle_old':('277条AnimSequence，含原地/根运动、持枪移动、跑跳蹲趴、开火、换弹、受击/死亡等家族；下方原始名表才是精确目录。当前真正绑定换弹是Rifle_Reload_2，不是D059。','277 AnimSequences: in-place/root-motion, rifle locomotion, run/jump/crouch/prone, fire/reload/hit/death families. Exact raw names are in the native index. The current actual reload binding is Rifle_Reload_2, not D059.'),
         'd059':('761条AnimSequence，含原地/根运动及站立/蹲姿单发、点射、连射、瞄准/放松换弹。70骨mannequin；现代M4预览模型不选择为二战武器。15条动作/33原生依赖+配置共35文件已选SFTP基线；整个原包没有全量进入游戏。选中换弹不等于当前换弹已切换。','761 AnimSequences including in-place/root-motion and standing/crouched single/burst/continuous fire, aim/relaxed reload. 70-bone mannequin; modern M4 preview is not selected as a WWII weapon. Selected SFTP baseline is 15 clips/33 native packages plus configuration, 35 files total, not the whole pack in game. Selection into a baseline is not a current reload switch.'),
         'arms':('候选双臂与左右分离网格，现代袖子/手套；现代步枪和附件。14条动画中7条是demo手臂动作、7条是武器/附件动作。武器Reload驱动枪械零件，不代表配套第一人称双手换弹。旧直接套D059的取景/参考姿态试验失败；保持LocalWorking，不用于替换已认可连续手臂。','Combined and split arm candidates with modern sleeves/gloves, modern rifle and attachments. Of 14 animations, 7 are demo-arm clips and 7 are weapon/attachment clips. Weapon Reload drives gun parts, not matched FP hand reload. The old direct D059 pose/framing trial failed; retain LocalWorking and do not replace accepted continuous arms.')}
        text += [status[key][0 if zh else 1],'',
          ('模型及骨架：' if zh else 'Meshes and rigs:'),'',tab(['Asset','Class','Bones','LOD / materials','Skeleton'],[[x['path'],x['class'],x.get('bone_count','—'),str(x.get('lod_count','—'))+' / '+str(len(x.get('materials',[]))),x.get('skeleton','—')] for x in assets if x['class'] in ('SkeletalMesh','StaticMesh')]),'']
        anims=[x for x in assets if x['class']=='AnimSequence']
        text += [('换弹/射击相关原始动作名（这里只筛名称；后坐视觉和实际绑定另验）：' if zh else 'Reload/fire raw action names (name discovery only; recoil appearance/current binding are separate):'),'',
                 tab(['Clip','Seconds','Root motion'],[[x['path'].split('/')[-1],f"{x.get('sequence_length',0):.4f}",x.get('root_motion','—')] for x in anims if re_search(x['path'])]),'']
        if key in ('german','us'):
            prefix='german' if key=='german' else 'allied'
            text += [image('Historical native final-body capture; 2026-10-01',f'LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001/FinalNativeCaptures/{prefix}_A_three_quarter.png'),'']
        elif key=='d059':text += [image('Historical 15 selected source-clip diagnostic views', 'LocalWorking/Validation/UE582/2026-10-01-weapons-v1/Evidence/Baseline20261002/source_motion_sheet_1.png'),'']
        elif key=='arms':text += [image('Historical candidate reference mesh, NOT an accepted FP setup','LocalWorking/Validation/UE582/2026-10-01-weapons-v1/Evidence/CandidateProbe_v2/reference_00_front_minus_y.png'),'']
    text += ['## '+('7. UE4动作合集：125包内部目录已读，无全量解压' if zh else '7. UE4 collection: all 125 headers read, no bulk extraction'),'']
    text += [('125个压缩包全部内部目录读取成功；成员/原生文件数并不是动画条数，.uasset还可能是模型、材质、骨架、蓝图。完整原始目录见私有catalog_facts.json，原生包名索引见附录。仅按标题/内部名字筛选，不运行包中脚本或工程。四个旧重复筛查包的CRC/大小结果不是SHA相同证明。' if zh else
              'All 125 archive headers were read successfully. Member/native-file counts are NOT animation counts: .uasset may be a mesh, material, skeleton or Blueprint. Private catalog_facts.json contains exact member paths; see the native-name appendix. No bundled script/project is executed. Earlier CRC/size duplicate screening is not SHA equality.'),'',
             tab(['Archive','Members','Native files','Expanded MiB','Source formats','Preview'],[[x['title'],x.get('member_count','—'),len(x.get('native_files',[])),f"{x.get('expanded_bytes',0)/1024**2:.1f}",', '.join(f'{k}:{v}' for k,v in x.get('other_formats',{}).items()) or '—',', '.join(x['preview_files']) or '—'] for x in F['archives']]),'']
    text += ['## '+('8. 新MW2枪械库：不补二战德军步枪' if zh else '8. New MW2 gun library: does not fill the German WWII rifle gap'),'',
      ('文件实际打开：54个集合，其中Collection为泛用集合，另53个有武器标签；1048对象=774网格+274骨架；无Action。1571个image datablock，1570打包，剩余Render Result不是缺失外部贴图。集合、骨架/附件不是53套UE可用枪，也不证明动画存在。' if zh else
       'Opened file: 54 collections, including generic Collection and 53 weapon-labeled collections; 1,048 objects = 774 meshes + 274 armatures; no Actions. 1,571 image datablocks, 1,570 packed; remaining Render Result is not a missing external texture. Collections/rigs/attachments do not certify 53 UE-ready weapons or supplied animation.'),'',
      ('名称及已检查外观均指向现代武器，未见Kar98k/Gewehr/M1/MP40/StG等二战候选。Lachmann等名称即使对应德国设计也不是1944装备。保留本机参考；不把现代枪作为德军武器替代，不直接迁入游戏/SFTP。来源可能涉及游戏导出，但本轮未验证，权利未知。' if zh else
       'Names and reviewed geometry indicate modern weapons, with no Kar98k/Gewehr/M1/MP40/StG candidates found. Even a German-designed modern gun is not 1944 equipment. Retain locally; no modern substitute, game import or SFTP publication. Possible game-export provenance is unverified and rights remain unknown.'),'']
    rows=[]
    for c in G['collections']:
        objs=[x for x in G['objects'] if c['name'] in x['collections']]
        meshes=[x for x in objs if x['type']=='MESH']; rigs=[x for x in objs if x['type']=='ARMATURE']
        rows.append([c['name'],len(meshes),len(rigs),sum(x['triangles'] for x in meshes),sum(not x['uv_layers'] for x in meshes),len({m for x in meshes for m in x['materials'] if m}),'; '.join(str(len(x['bones'])) for x in rigs)])
    text += [tab(['Collection label','Mesh objects','Rig objects','Raw triangles','Meshes without UV','Distinct materials','Bones per rig'],rows),'',
      ('上表统计原网格，不含modifier求值/LOD/UE性能认证。Workbench图只供几何辨识，局部蓝灰诊断色不等于正式PBR贴图效果；贴图打包不等于材质正确。' if zh else 'Counts use raw meshes, not evaluated modifiers/LOD/UE performance. Workbench views identify geometry; blue-gray diagnostic shading is not final PBR appearance. Packed textures do not certify materials.'),'',
      image('Lachmann-762 modern weapon geometry diagnostic',V+'/Guns/views_v1/Lachmann-762_side.png'),'',
      image('SA-B 50 modern bolt-action geometry diagnostic',V+'/Guns/views_v1/SA-B_50_side.png'),'',
      image('m4a1 modern weapon geometry diagnostic',V+'/Guns/views_v1/m4a1_side.png'),'']
    text += ['## '+('9. 当前使用与不应重复买的内容' if zh else '9. Actual use and avoid-repeat purchases'),'',
      ('当前发布版使用现有巴黎地图、美军/德军角色、RifleAnimsetPro动作及连续手臂；本地PlayerActionsV6等尚未发布。换弹Rifle_Reload_2在用，D059两条换弹只是候选；原包连射/点射存在不等于当前已播放或镜头后坐已实现。先适配库存，不重复买通用动作/现代枪。德军二战步枪和M1可动枪机/漏夹专用内容仍未被这批解决。' if zh else
       'Published playtest uses the existing Paris, US/German characters, RifleAnimsetPro actions and continuous arms; local PlayerActionsV6 drafts are not published. Rifle_Reload_2 is bound; D059 reloads are candidates. Burst/continuous clips existing does not mean they play in game or camera recoil is implemented. Reuse inventory before buying generic actions/modern guns. WWII German rifle and M1 moving bolt/en-bloc content remain open.'),'',
      ('巴黎环境参考：原生Content清单15,850文件/28,421,951,358字节，路径LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/WW2City；不属于此次新增枪库。素材交易渠道没有在本轮核实。' if zh else
       'Paris context: 15,850 original Content files / 28,421,951,358 bytes; LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Content/WW2City. Not the new gun library; its transaction channel was not verified here.'),'',
      '## '+('10. 详细索引与证据' if zh else '10. Detailed indexes and evidence'),'',
      '- [Native asset / exact action index](XIAN_YU_NATIVE_ASSET_INDEX_20261003.md)',
      '- [All archive native-name index](XIAN_YU_ARCHIVE_CONTENTS_20261003.md)',
      '- [Private current facts JSON](LocalWorking/Validation/2026-10-03-asset-catalog-v1/Catalog/catalog_facts.json)',
      '- [Private Blender object/rig/material/image inventory](LocalWorking/Validation/2026-10-03-asset-catalog-v1/Guns/views_v1/weapon_library_inventory.json)',
      '- [Reload review](../Docs/Development/RELOAD_COMPARISON_20261003_ZH.md)',
      '- [Original intake result](../Docs/Development/WEAPON_ASSET_VALIDATION_RESULT_20261001.md)',
      '- [Selected rifle-motion baseline result](../Docs/Development/WEAPON_BASELINE_AND_RELOAD_RESULT_20261002.md)','']
    return '\n'.join(text)
def re_search(p):return any(s in p.lower() for s in ('reload','fire','shoot','recoil'))

native=['# Native asset / action index — 2026-10-03','','Generated from earlier actual UE load records, with original presence/size checks this turn. Class counts are not new runtime passes. Asset names, animation seconds and root-motion flags are listed exactly; source rigs differ.','']
for d in F['deliveries']:
    native += ['## '+names[d['key']],'',tab(['Package','Class','Seconds / root motion'],[[x['path'],x['class'],f"{x.get('sequence_length',0):.6f} / {x.get('root_motion','—')}" if x['class']=='AnimSequence' else '—'] for x in d['assets']]),'']
archive=['# Archive content index — 2026-10-03','','All 125 headers read this turn. Not extracted, imported or runtime accepted. These are native package file names, not independently verified animation names. Member paths and exact formats/counts remain in the private facts JSON. No extraction passwords appear here.','']
for x in F['archives']:
    archive += ['## '+x['title'],'',f"Members: {x.get('member_count',0)}; native files: {len(x.get('native_files',[]))}; expanded bytes: {x.get('expanded_bytes',0):,}. Header status: {x['status']}.",'', '```text']
    # Preserve relative native paths but strip non-native wrappers to avoid credential-bearing delivery folder names.
    for n in x.get('native_files',[]):
        parts=n.replace('\\','/').split('/')
        native_start=next((i for i,p in enumerate(parts) if p=='Content'),len(parts)-1)
        archive.append('/'.join(parts[native_start:]))
    archive += ['```','']
docs={'Assets/XIAN_YU_ASSET_CATALOG_20261003_ZH.md':catalog(True),
      'Assets/XIAN_YU_ASSET_CATALOG_20261003.md':catalog(False),
      'Assets/XIAN_YU_NATIVE_ASSET_INDEX_20261003.md':'\n'.join(native),
      'Assets/XIAN_YU_ARCHIVE_CONTENTS_20261003.md':'\n'.join(archive)}
if len(sys.argv)==5 and sys.argv[1]=='--repair':
    path=sys.argv[2]; offset=int(sys.argv[3]); limit=int(sys.argv[4])
    old=(ROOT/path).read_text(encoding='utf-8').splitlines()
    new=docs[path].splitlines()
    assert len(old)==len(new)+1 and old[-1].startswith('<!-- generated catalog segment')
    before=old[offset:offset+limit]; after=new[offset:offset+limit]
    if before!=after:
        print('*** Begin Patch\n*** Update File: '+path)
        delta=list(difflib.unified_diff(before,after,n=2,lineterm=''))[2:]
        for line in delta:
            print('@@' if line.startswith('@@') else line)
        print('*** End Patch')
elif len(sys.argv)==2 and sys.argv[1]=='--counts':
    print(json.dumps({p:len(b.splitlines()) for p,b in docs.items()}))
else:
    path=sys.argv[1]
    offset=int(sys.argv[2]); limit=int(sys.argv[3])
    lines=docs[path].splitlines()
    chunk=lines[offset:offset+limit]
    marker=f'<!-- generated catalog segment {offset+len(chunk)} -->'
    print('*** Begin Patch')
    if offset==0:
        assert not (ROOT/path).exists(), 'Refuse occupied catalog'
        print('*** Add File: '+path)
    else:
        print('*** Update File: '+path)
        print('@@')
        print(f'-<!-- generated catalog segment {offset} -->')
    for line in chunk:print('+'+line)
    print('+'+marker)
    print('*** End Patch')
