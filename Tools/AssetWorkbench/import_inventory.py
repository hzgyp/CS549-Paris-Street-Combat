"""Reconcile existing local deliveries into workbench metadata. Never extracts or saves assets."""
from pathlib import Path
import hashlib
import json
import re
from PIL import Image
import io

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT/'Assets/LocalWorking/AssetWorkbench'
REG = ROOT/'Assets/Registry'
CATALOG_DOC = 'Assets/XIAN_YU_ASSET_CATALOG_20261003_ZH.md'
FACTS = 'Assets/LocalWorking/Validation/2026-10-03-asset-catalog-v1/Catalog/catalog_facts.json'
GUNS = 'Assets/LocalWorking/Validation/2026-10-03-asset-catalog-v1/Guns/views_v1/weapon_library_inventory.json'

def load(p): return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def slug(s): return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')

assets=[]; histories=[]; members={}; translations={}; patches={}; rules=[]
media=load('Assets/LocalWorking/AssetWorkbench/private-records/media.json')
media['files']=[m for m in media['files'] if not m.get('inventory_import')]
fingerprints=[]

def bilingual(zh,en): translations[zh]=en;return zh
def add(aid,zh,en,category,origin='purchased',description=None,parent=None,bundles=(),life='retained'):
    a=dict(id=aid,name=bilingual(zh,en),name_en=en,category=category,origin=origin,lifecycle=life,owner='Yupu / Paris team',bundles=list(bundles),description=description or bilingual('原始交付；未登记当前游戏使用。','Original delivery; no registered current game use.'),human_review=bilingual('见原始记录','See source records'),limitations=[bilingual('游戏兼容性未由本次预览验证。','Game compatibility was not tested in this preview.')],documents=[CATALOG_DOC],order=8+len(assets),aliases=[en,zh],validation=bilingual('库存登记','Inventory recorded'),rights_scope=bilingual('仅本机内部查看；发布按来源许可。','Internal local viewing; redistribution follows source rights.'),parent_id=parent)
    assets.append(a);return a
def preview(aid,path,label,en,kind='supplier thumbnail'):
    # User policy: supplier/purchase images never return during re-import.
    if kind=='supplier thumbnail':return None
    p=Path(path);p=p if p.is_absolute() else ROOT/p
    if not p.is_file():raise RuntimeError(f'Missing explicit preview: {p}')
    mime='audio/wav' if p.suffix=='.wav' else 'image/jpeg' if p.suffix.lower() in ('.jpg','.jpeg') else 'image/png'
    if mime.startswith('image/'):
        with Image.open(p) as im:im.verify()
    mid=('audio-' if mime.startswith('audio') else 'inv-')+aid+'-'+str(sum(m['asset_id']==aid for m in media['files']))
    media['files'].append(dict(id=mid,asset_id=aid,path=p.relative_to(ROOT).as_posix(),sha256=digest(p),size_bytes=p.stat().st_size,label=bilingual(label,en),kind=kind,audience='local_owner',rights_basis='User requested local internal inventory; existing private delivery/evidence; no redistribution',mime=mime,inventory_import=True))
    return mid
def revision(aid,title,summary,en,metrics=None,document=CATALOG_DOC):
    rid=aid+'-'+slug(title)
    histories.append(dict(id=rid,asset_id=aid,title=title,kind='inventory_revision',result='recorded',summary=bilingual(summary,en),scope=bilingual('来源登记；未新增运行验收。','Source record; no new runtime acceptance.'),document=document,metrics=metrics or {},media_ids=[m['id'] for m in media['files'] if m['asset_id']==aid][:1]))
def member(aid,rows): members[aid]=rows
def usage(aid,filename,needle,label,en):rules.append(dict(asset_id=aid,filename=filename,needle=needle,label=bilingual(label,en)))

def main():
    f=load(FACTS);g=load(GUNS)
    for p in [FACTS,GUNS]:fingerprints.append(dict(path=p,sha256=digest(ROOT/p)))
    add('d059-rifle-pro','D059 步枪动作库','D059 Rifle Pro MoCap','动作',bundles=['rifle-pro-mocap-ue582-selected'],description=bilingual('761 段原始动作；15 段曾选入适配集。','761 original clips; 15 previously selected for adaptation.'))
    add('shooter-starter','Shooter Starter 手臂与武器','Shooter Starter Arms & Weapons','人物',description=bilingual('现代手臂与武器来源；不是当前认可手臂。','Modern arms and weapon source; not the accepted current arms.'))
    add('ue4-animation-collection','UE4 动画合集','UE4 Animation Collection','动作',description=bilingual('125 个原始动画包，按包检索。','125 original animation packages, individually searchable.'))
    add('mw2-library','MW2 武器库','MW2 Weapon Library','武器',description=bilingual('53 个武器集合；SP-R 208 用作改制来源。','53 weapon collections; SP-R 208 used as an adaptation source.'))
    assets[-1].update(usage_hint='source_only',related_ids=['german-rifle'])
    add('muzzle-flash','枪口特效包','Muzzle Flash Pack','特效',description=bilingual('MsvFx 原包；游戏选用 Rifle 01 效果及其依赖。','MsvFx original pack; the game selects the Rifle 01 effect and its dependencies.'))
    for aid,zh,en,cat,origin,desc,desc_en in [
        ('frag-grenade','破片手雷','Fragmentation grenade','道具','team_created','候选版基础几何组合，尚无独立精细模型。','Candidate basic-shape assembly; no separate detailed model.'),
        ('smoke-grenade','烟雾弹','Smoke grenade','道具','team_created','候选版基础几何罐体。','Candidate basic-shape canister.'),
        ('smoke-effect','烟雾效果','Smoke effect','特效','adapted','复用城市烟雾素材，构建临时粒子材质。','City smoke source reused with transient particle material.'),
        ('ammo-box','弹药补给箱','Ammunition supply box','道具','adapted','城市 SM_AmmoBox_01a；候选版有限补给。','City SM_AmmoBox_01a; finite resupply in the candidate.'),
        ('explosion-audio','爆炸音效','Explosion audio','音频','adapted','CC0 qubodup 162363 适配音效。','Adapted CC0 qubodup 162363 sound effect.')]:
        a=add(aid,zh,en,cat,origin,description=bilingual(desc,desc_en),life='candidate');a['documents']=['Docs/Development/MissionLoopV1/TACTICAL_EQUIPMENT_RESULT_20261011_ZH.md']
        revision(aid,'equipment-v16-20261011',desc,desc_en,document=a['documents'][0])
    keys={'german':'german-soldier','us':'allied-soldier','rifle_old':'rifle-animation','d059':'d059-rifle-pro','arms':'shooter-starter'}
    for d in f['deliveries']:
        aid=keys[d['key']]
        member(aid,[dict(name=x['path'].split('/')[-1],path=x['path'],kind=x['class'],duration=x.get('sequence_length'),frames=x.get('frames')) for x in d['assets']])
        revision(aid,'original-intake-20261001', '原始交付库存；加载结论见历史记录。','Original delivery inventory; load results remain historical.',{'files':d['original_files'],'bytes':d['original_bytes'],'classes':d['classes']})
    # Exact cached UE thumbnails embedded in the delivered packages, not newly inferred imagery.
    arms_root=ROOT/'Assets/LocalWorking/Intake/2026-10-01/01_ShooterStarter_FPS_Arm_A'
    for name in ['SKM_FPS_Arm_A','SKM_Rifle_A_Assembled']:
        p=next(arms_root.rglob(name+'.uasset'));raw=p.read_bytes();start=raw.find(b'\x89PNG\r\n\x1a\n')
        if start<0:continue
        end=raw.find(b'IEND',start)+8;png=raw[start:end]
        with Image.open(io.BytesIO(png)) as im:im.verify()
        out=STATE/'previews/shooter-starter'/f'{name}.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(png)
        preview('shooter-starter',out,'原件内嵌 UE 缩略图 · '+name,'Embedded original UE thumbnail · '+name,'embedded UE thumbnail')
    revision('rifle-animation','duplicate-delivery-20261004','重复交付：298 个原生文件及 SourceFiles.zip 与原件相同。','Duplicate delivery: 298 native files and SourceFiles.zip match the original.')
    for aid,title,zh,en,doc in [
        ('allied-soldier','formal-v18-grip-v16-20261006','V18 原生整合沿用人工认可的 V16 握姿。','V18 native integration retains the manually accepted V16 grip.','ALLIED_NPC_FORMAL_V18_RESULT_20261006.md'),
        ('first-person','formal-v21-appearance-v20-20261005','V21 原生整合保留认可的 V20 展示。','V21 native integration retains the accepted V20 presentation.','FIRST_PERSON_FORMAL_V21_RESULT_20261005.md'),
        ('recorded-audio','recorded-foley-v1-20261009','31 条历史音效；后续 V2 修正脚步触地和跳跃。','31 historical cues; V2 later corrects foot contact and jumping.','G1_AUDIO_REALISM_RESULT_20261009.md'),
        ('recorded-audio','foot-contact-audio-v2-20261009','33 条运行音效；实录 M1，德军仍使用合成枪声。','33 runtime cues; recorded M1 fire, with the synthetic German shot retained.','G1_FOOT_CONTACT_AUDIO_V2_RESULT_20261009.md')]:
        revision(aid,title,zh,en,document='Docs/Development/'+doc)
    base=ROOT/'Assets/LocalWorking/Intake/2026-10-01/03_UE4_Animation_Collection'
    archives={p.name:p for p in base.rglob('*.7z')};images={p.name:p for p in base.rglob('*') if p.suffix.lower() in ('.png','.jpg','.jpeg')}
    assert len(f['archives'])==len(archives)==125
    for row in f['archives']:
        title=Path(row['title']).stem;aid='anim-'+slug(title)
        add(aid,title,title,'动作',parent='ue4-animation-collection',description=bilingual('原始动画包；未登记当前游戏使用。','Original animation package; no registered current game use.'))
        names=row['preview_files'] or (['Superhero Flight Animations.png'] if title=='Superhero Flight Animations 426' else [])
        for n in names:preview(aid,images[n],'供应商预览图','Supplier thumbnail')
        p=archives[row['title']];h=digest(p)
        revision(aid,'original-delivery-20261001','已核对本机原始压缩包；成员来自历史目录读取，未解压。','Local original archive hashed; members come from the historical header listing, without extraction.',{'filename':p.name,'sha256':h,'bytes':p.stat().st_size,'members':row['member_count']})
        member(aid,[dict(name=Path(x).name,path=x,kind=Path(x).suffix) for x in row['native_files']])
        if title=='Rifle Animset Pro':
            assets[-1]['related_ids']=['rifle-animation'];assets[-1]['description']=bilingual('合集内同名来源；原生交付与重复交付见步枪动作库。','Same-name collection source; see Rifle Animset Pro for native and duplicate deliveries.')
    member('ue4-animation-collection',[dict(name=x['title'],path=x['title'],kind='archive',asset_id='anim-'+slug(Path(x['title']).stem)) for x in f['archives']])
    preview('ue4-animation-collection',images['Rifle Animset Pro.png'],'合集示例：Rifle Animset Pro 供应图','Collection sample: Rifle Animset Pro supplier image')
    revision('ue4-animation-collection','delivery-20261001','125 个压缩包及 125 张供应图。','125 archives and 125 supplier images.',{'archives':125,'previews':125})
    weapon_colls=[c for c in g['collections'] if c['objects']];assert len(weapon_colls)==53
    render_root=STATE/'previews/mw2'
    rendered=json.loads((render_root/'weapon_library_inventory.json').read_text(encoding='utf-8'))
    assert len(rendered['renders'])==106,'Wait for all exact collection renders before importing'
    obj={o['name']:o for o in g['objects']}
    source=next((ROOT/'Assets/LocalWorking/Intake/2026-10-03/01_MW2_Guns_Asset_Library').rglob('*.blend'))
    source_sha=digest(source)
    for c in weapon_colls:
        name=c['name'];aid='mw2-'+slug(name)
        add(aid,name,name,'武器',parent='mw2-library',description=bilingual('现代武器来源集合；未作为完整武器接入当前游戏。','Modern weapon source collection; not integrated as a complete current-game weapon.'))
        member(aid,[dict(name=n,path=n,kind=obj[n]['type'],triangles=obj[n].get('triangles')) for n in c['objects']])
        for view in [x for x in rendered['renders'] if x['name']==name]:
            corrected=STATE/'previews/pila-framing-v2'/view['file']
            path=corrected if name=='PILA' and corrected.is_file() else render_root/view['file']
            preview(aid,path,'Blender 集合诊断预览 · '+view['view'],'Blender collection diagnostic · '+view['view'],'Blender diagnostic')
        revision(aid,'original-delivery-20261003','来源集合身份；无现成动作。','Source collection identity; no supplied actions.',{'collection':name,'source_sha256':source_sha,'objects':len(c['objects']),'actions':0})
        if name=='SP-R 208':assets[-1]['usage_hint']='source_only';assets[-1]['related_ids']=['german-rifle'];assets[-1]['description']=bilingual('机匣、枪管等用于 FineWoodV15 改制；原枪未整把入游戏。','Receiver and barrel parts used in FineWoodV15; the original weapon is not used as a whole.')
    member('mw2-library',[dict(name=c['name'],path=c['name'],kind='collection',asset_id='mw2-'+slug(c['name'])) for c in weapon_colls])
    first=next(x for x in rendered['renders'] if x['name']=='SP-R 208')
    preview('mw2-library',render_root/first['file'],'库内示例：SP-R 208 集合','Library sample: SP-R 208 collection','Blender diagnostic')
    revision('mw2-library','original-delivery-20261003','原始 Blender 武器库，只读生成预览。','Original Blender library; previews generated read-only.',{'sha256':source_sha,'bytes':source.stat().st_size,'collections':53,'actions':0})
    reload=ROOT/'Assets/LocalWorking/Validation/2026-10-03-asset-catalog-v1/Reload/compare_v4'
    preview('rifle-animation',reload/'current_allied_sheet.png','历史换弹动作对比 · 2026-10-03','Historical reload comparison · 2026-10-03','UE historical preview')
    preview('d059-rifle-pro',reload/'d059_aim_sheet.png','D059 动作适配对比 · 2026-10-03','D059 adaptation comparison · 2026-10-03','UE historical preview')
    muzzle=ROOT/'Assets/LocalWorking/Intake/2026-10-04/01_Muzzle_Flash_VFX'
    mf=[p for p in muzzle.rglob('*') if p.is_file()]
    member('muzzle-flash',[dict(name=p.name,path=p.relative_to(muzzle).as_posix(),kind=p.suffix) for p in mf])
    revision('muzzle-flash','original-delivery-20261004','原始 MsvFx 交付。','Original MsvFx delivery.',{'files':len(mf)})
    revision('muzzle-flash','native-integration-20261008','选择 Rifle 01 特效和 25 项来源依赖。','Rifle 01 effect selected with 25 source dependencies.',document='Docs/Development/MuzzleFlashV1/MUZZLE_FLASH_ASSET_USAGE_ZH.md')
    preview('muzzle-flash','Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MuzzleFlashV1/formal_transactions_v1_20261008/PC_City_Player_pulse_08.png','UE 枪口效果历史截图 · 2026-10-08','Historical UE muzzle effect · 2026-10-08','UE historical preview')
    checks=ROOT/'tmp/g1-tactical-equipment-20261010/checks'
    preview('frag-grenade',checks/'throw_v15_early/01_prepare.png','v15 手雷准备截图','v15 grenade preparation capture','UE historical preview')
    preview('smoke-effect',checks/'smoke_v16_early/smoke_dense.png','v16 实际烟雾截图','v16 actual smoke capture','UE historical preview')
    preview('smoke-grenade',checks/'smoke_v16_early/smoke_dense.png','烟雾弹部署效果；非罐体近照','Smoke deployment effect; not a canister close-up','UE historical preview')
    preview('ammo-box',checks/'interactions_ui_field_v2/supply_empty.png','候选版补给箱交互截图','Candidate supply box interaction capture','UE historical preview')
    explosion=ROOT/'tmp/g1-tactical-equipment-20261010/candidate_full_v16/Runtime/Windows/WW2FranceLiberation/Audio/equipment_explosion.wav'
    assert digest(explosion)=='92fc18b0d0b78b479700e5c0dced4de7df6300fee39a34000b83d43f028b0464'
    preview('explosion-audio',explosion,'实际爆炸 WAV','Actual explosion WAV','audio')
    # Source-qualified references; importer resolves these against current pinned source manifests.
    usage('rifle-animation','ParisNPCGripV15.cpp','/Game/RifleAnimsetPro/','原生握姿策略引用部分步枪动作。','Native grip policy references selected rifle clips.')
    usage('muzzle-flash','ParisMuzzleFlashV1.cpp','Niagara_Riffle_MuzzleFlash_01','枪口插件引用 Rifle 01 特效。','Muzzle plugin references the Rifle 01 effect.')
    usage('frag-grenade','ParisTacticalEquipment.cpp','Kind==TEXT("Frag")','候选装备源码构建手雷几何。','Candidate equipment code constructs grenade geometry.')
    usage('smoke-grenade','ParisTacticalEquipment.cpp','Kind==TEXT("Smoke")','候选装备源码构建烟雾弹罐体。','Candidate equipment code constructs a smoke canister.')
    usage('ammo-box','ParisEquipmentWorld.inl','SM_AmmoBox_01a','补给点引用城市弹药箱。','Supply sites reference the city ammunition box.')
    usage('smoke-effect','ParisEquipmentSmoke.inl','/SmokeFog/','烟雾材质引用城市素材。','Smoke material references city source assets.')
    usage('explosion-audio','ParisEquipmentAudio.inl','equipment_explosion.wav','爆炸事件加载登记 WAV。','Explosion events load the registered WAV.')
    audio=load('Assets/Sync/manifests/paris-g1-recorded-audio.json')
    for row in audio['files']:
        p=ROOT/row['path'];name=p.stem;aid='cue-'+slug(name)
        a=add(aid,name,name,'音频','adapted',parent='recorded-audio',description=bilingual('项目运行音频；逐条播放原始 WAV。','Project runtime audio; play the actual WAV cue.'))
        assert digest(p)==row['sha256']
        preview(aid,p,'运行音频 · '+name,'Runtime audio · '+name,'audio')
        revision(aid,'audio-v2-20261009','已发布音频清单中的确定文件版本。','Exact file version from the published audio manifest.',{'sha256':row['sha256'],'bytes':row['size_bytes']},document='Assets/Sync/manifests/paris-g1-recorded-audio.json')
        a['inherit_usage_from']='recorded-audio'
        if name=='fire':
            a['origin']='team_created';a['description']=bilingual('保留的合成德军枪声；不是实录 K98。','Retained synthetic German shot; not a recorded K98.')
    member('recorded-audio',[dict(name=Path(x['path']).name,path=Path(x['path']).name,kind='WAV',asset_id='cue-'+slug(Path(x['path']).stem)) for x in audio['files']])
    # Full city package file inventory remains in the hashed Catalog; index its members without inventing mesh classes.
    city=load('Assets/Sync/manifests/france-liberation-content.json')
    member('paris-city',[dict(name=Path(x['path']).name,path=x['path'],kind=Path(x['path']).suffix) for x in city['files']])
    rules.append(dict(asset_id='paris-city',filename='DefaultEngine.ini',needle='GameDefaultMap=/Game/ParisCombat/Maps/',label=bilingual('当前游戏默认地图','Current gameplay default map')))
    rifle_sources=[]
    for p in sorted((ROOT/'Assets/Integration').glob('GERMAN_RIFLE_*INVENTORY*.json')):
        d=json.loads(p.read_text(encoding='utf-8-sig'))
        source=dict(path=p.relative_to(ROOT).as_posix(),sha256=digest(p),date=d.get('date'),candidate=d.get('candidate'),models=[x for x in d.get('private_files',[]) if x['path'].endswith(('.glb','.blend'))])
        rifle_sources.append(source)
        title=p.stem.replace('GERMAN_RIFLE_','').replace('_INVENTORY','')
        revision('german-rifle',title,'历史模型库存；后续人工采用以 V14 整合记录为准。','Historical model inventory; later adoption follows the V14 integration record.',{'inventory_sha256':source['sha256'],'models':source['models']},document='Assets/Registry/mappings/rifle-inventory-sources.json')
    save(REG/'mappings/rifle-inventory-sources.json',dict(records=rifle_sources))
    for a in assets:
        if a['id'] not in {h['asset_id'] for h in histories}:revision(a['id'],'inventory-20261011','原始来源及内容登记。','Original source and contents recorded.')
    save(REG/'assets/inventory.json',dict(schema_version=1,assets=assets,patches=patches,usage_rules=rules,members=members,source_fingerprints=fingerprints))
    save(REG/'mappings/inventory-history.json',dict(revisions=histories))
    save(ROOT/'Tools/AssetWorkbench/frontend/src/inventory-translations.json',translations)
    save(STATE/'private-records/media.json',media)
    save(STATE/'runs/inventory-import.json',dict(assets_added=len(assets),archive_packages=125,weapon_collections=53,member_count=sum(map(len,members.values())),media_count=len(media['files']),missing_preview=[a['id'] for a in assets if not any(m['asset_id']==a['id'] for m in media['files'])],sources=fingerprints))
    print(json.dumps({'assets_added':len(assets),'media':len(media['files']),'members':sum(map(len,members.values()))}))

if __name__=='__main__':main()
