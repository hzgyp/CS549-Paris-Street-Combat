"""Correct the existing city asset; preserve identity, members and immutable sources."""
import hashlib,json,re,argparse
from pathlib import Path
from asset_index import atomic_write
from app.catalog import identity

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--attempt',default='v1',choices=['v1','v2']);parser.add_argument('--metadata-only',action='store_true');parser.add_argument('--existing-scenes',action='store_true');args=parser.parse_args()
RUN=ROOT/f'Assets/LocalWorking/AssetWorkbench/runs/city-map-capture-{args.attempt}'
OUT=ROOT/'Assets/LocalWorking/AssetWorkbench/runs/city-map-registration-v1'
OUT.mkdir(parents=True,exist_ok=True)
def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,data):atomic_write(ROOT/path,(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
capture={};review={'images':[]}
if not args.metadata_only and not args.existing_scenes:
    capture=json.loads((RUN/'capture-v1/result.json').read_text(encoding='utf-8'))
    process=json.loads((RUN/'process.json').read_text(encoding='utf-8'))
    review=json.loads((RUN/'visual-review.json').read_text(encoding='utf-8'))
    assert capture['status']=='captured_pending_visual_review' and process['protected_inputs_unchanged'] and process['exit_code']==0
    assert review['status']=='approved_for_private_preview' and review['images'],'Actual image inspection required'
protected=json.loads((RUN/'protected-before.json').read_text())
assert all(digest(ROOT/p)==h for p,h in protected.items()),'Protected map/source changed'
paths={'pilots':'Assets/Registry/assets/pilots.json','inventory':'Assets/Registry/assets/inventory.json',
       'history':'Assets/Registry/mappings/history.json','media':'Assets/LocalWorking/AssetWorkbench/private-records/media.json'}
data={k:load(p) for k,p in paths.items()}
before={k:digest(ROOT/p) for k,p in paths.items()}
asset=next(a for a in data['pilots']['assets'] if a['id']=='paris-city')
manifest=load('Assets/Sync/manifests/france-liberation-content.json')
catalog=load('Assets/Sync/CATALOG.json')
active=next(m for m in catalog['active_manifests'] if m['asset_id']=='france-liberation-content')
assert active['sha256']==digest(ROOT/active['path'])
city=next(x for x in manifest['files'] if x['path'].endswith('/Maps/LV_Paris_WW2.umap'))
assert digest(ROOT/city['path'])==city['sha256'],'Current vendor main map differs from selected manifest'
roles={'LV_Paris_WW2':'城市主关卡','LV_Lighting_Day':'白昼灯光','LV_Lighting_Midnight':'午夜灯光','LV_Lighting_WarFog':'战争雾灯光',
       'LV_NewsetDressing':'新增场景陈设','LV_Powerline':'电线网络','LV_Proxy':'代理场景','LV_SetDressing':'场景陈设',
       'LV_SplineRoads':'样条道路','LV_StructureAsset':'建筑与结构','LV_VFX':'场景特效','LV_Overview':'资源概览关卡'}
levels=[{'name':Path(f['path']).name,'path':f['path'],'role':roles.get(Path(f['path']).stem,'资源概览关卡'),'size_bytes':f['size_bytes'],'sha256':f['sha256']}
        for f in manifest['files'] if f['path'].endswith('.umap') and '/WW2City/Maps/' in f['path']]
levels.sort(key=lambda f:(f['name']!='LV_Paris_WW2.umap',f['name']))
asset.update(name='巴黎二战地图 · France Liberation',name_en='France Liberation · Paris WWII map',category='地图',
             description='完整巴黎城市环境包；15,850文件、69个关卡/场景层，当前游戏使用其G1派生地图。',
             human_review='当前游戏地图来源',validation='原件清单与当前游戏默认地图已登记',
             limitations=['地图原件只读；预览不代表全图碰撞、导航或性能验收。'],
             aliases=list(dict.fromkeys(asset.get('aliases',[])+['地图','巴黎地图','巴黎二战地图','法国解放','France Liberation','WW2City','LV_Paris_WW2','LV_ParisG1_Midterm_V1','Meshingun Studio'])))
asset['documents']=list(dict.fromkeys(asset.get('documents',[])+['Docs/Development/AssetWorkbenchV1/CITY_MAP_ASSET_USAGE_20261011_ZH.md','Assets/Sync/RIGHTS.md']))
asset['map_details']={'supplier':'Meshingun Studio','delivery_version':'d20260630 (UE5.6+)','content_version':manifest['asset_version'],
                      'file_count':len(manifest['files']),'size_bytes':sum(f['size_bytes'] for f in manifest['files']),
                      'level_count':sum(f['path'].endswith('.umap') for f in manifest['files']),
                      'vendor_map':'/Game/WW2City/Maps/LV_Paris_WW2','game_map':'/Game/ParisCombat/Maps/LV_ParisG1_Midterm_V1','levels':levels}
assert asset['map_details']['level_count']==69 and len(data['inventory']['members']['paris-city'])==15850
labels={'city-overview':'城市总览','city-overhead':'城市俯视','city-bridge':'河岸与桥梁','city-streets':'城市街区'}
previews=[]
for name in review['images']:
    row=next(c for c in capture['captures'] if c['file']==name+'.png')
    image=RUN/'capture-v1'/row['file'];assert digest(image)==row['sha256']
    previews.append({'id':'paris-map-'+name,'asset_id':'paris-city','path':image.relative_to(ROOT).as_posix(),'sha256':row['sha256'],
                     'size_bytes':image.stat().st_size,'mime':'image/png','label':labels[name],'kind':'真实UE场景截图','audience':'local_owner',
                     'rights_basis':'Existing owner-attested private project team sharing; user requested real asset previews; no public redistribution',
                     'actual_capture':True,'source_map':capture['map'],'source_map_sha256':city['sha256']})
data['media']['files']=previews+[m for m in data['media']['files'] if m['id'] not in {x['id'] for x in previews}]
rule={'asset_id':'paris-city','filename':'DefaultEngine.ini','needle':'GameDefaultMap=/Game/ParisCombat/Maps/','label':'当前游戏默认地图'}
if rule not in data['inventory']['usage_rules']:data['inventory']['usage_rules'].append(rule)
bundle_revision=identity('paris-city',manifest['asset_version'],active['sha256'])
native_active=next(m for m in catalog['active_manifests'] if m['asset_id']=='paris-gameplay-native-playtest')
native=load(native_active['path']);assert digest(ROOT/native_active['path'])==native_active['sha256']
native_maps=[f for f in native['files'] if '/ParisCombat/Maps/' in f['path'] and f['path'].endswith('.umap')]
if args.existing_scenes:
    scene_review=load('Assets/LocalWorking/AssetWorkbench/runs/city-map-existing-scenes/visual-review.json')
    assert scene_review['status']=='approved_for_private_preview'
    selector=load('Docs/Development/CURRENT_UI_REVIEW.json')
    game_map=next(f for f in native_maps if f['path'].endswith('/LV_ParisG1_Midterm_V1.umap'))
    assert digest(ROOT/game_map['path'])==game_map['sha256']
    for image in scene_review['images']:
        check=next(c for c in selector['checks'] if c['mode']==image['check_mode'])
        assert check['result']==image['result'] and digest(ROOT/check['result'])==check['sha256']
        assert image['game_sha256']==selector['game_sha256'] and digest(ROOT/image['path'])==image['sha256']
        previews.append({'id':image['id'],'asset_id':'paris-city','path':image['path'],'sha256':image['sha256'],
                         'size_bytes':(ROOT/image['path']).stat().st_size,'mime':'image/png','label':image['label'],'kind':'真实游戏场景截图 · 局部',
                         'audience':'local_owner','rights_basis':'Existing owner-attested private project team sharing; user requested actual map previews',
                         'actual_capture':True,'source_map':asset['map_details']['game_map'],'source_map_sha256':game_map['sha256'],
                         'game_sha256':selector['game_sha256'],'check_result':check['result'],'check_result_sha256':check['sha256'],
                         'scope':'已有实跑截图；仅展示G1局部，不是全图总览或本次新运行验收。'})
    data['media']['files']=previews+[m for m in data['media']['files'] if m['id'] not in {p['id'] for p in previews}]
doc='Docs/Development/AssetWorkbenchV1/CITY_MAP_ASSET_USAGE_20261011_ZH.md'
revisions=[{'id':'paris-city-delivery-d20260630','asset_id':'paris-city','title':'France Liberation 原始交付 d20260630','kind':'delivery_revision',
            'parent_ids':[],'document':doc,'summary':'原始供应城市及外部Actor、建筑预制关卡、材质与贴图；保留交付版本来源。',
            'scope':'版本名来自原始交付路径；不宣称本次对原始全包重验','result':'recorded','media_ids':[],
            'metrics':{'delivery_version':'d20260630','source_manifest_sha256':active['sha256']}},
           {'id':'paris-city-g1-native-20261008','asset_id':'paris-city','title':'G1 原生派生地图','kind':'integration_revision',
            'parent_ids':[bundle_revision],'document':doc,'summary':'游戏使用G1派生关卡；供应城市原件与游戏关卡分别登记。',
            'scope':'地图与美术范围，不新增游戏运行验收','result':'recorded','media_ids':[p['id'] for p in previews],
            'metrics':{'native_version':native['asset_version'],'native_manifest_sha256':native_active['sha256'],'native_maps':native_maps}}]
data['history']['revisions']=[r for r in data['history']['revisions'] if r['id'] not in {x['id'] for x in revisions}]+revisions
for key,path in paths.items():
    assert digest(ROOT/path)==before[key],'Registration changed during update'
    backup=OUT/(key+'-before.json')
    if not backup.exists():backup.write_bytes((ROOT/path).read_bytes())
    save(path,data[key])
save((OUT/('metadata-registration.json' if args.metadata_only else 'registration.json')).relative_to(ROOT).as_posix(),{'status':'registered_metadata_pending_previews' if args.metadata_only else 'registered_pending_platform_refresh','asset_id':'paris-city',
     'map_details':asset['map_details'],'media_ids':[p['id'] for p in previews],'native_maps':native_maps,'protected_inputs_unchanged':True})
assert all(digest(ROOT/p)==h for p,h in protected.items()),'Protected map input changed'
print('Registered city metadata; actual previews remain pending.' if args.metadata_only else 'Registered existing city asset, original/derived map versions, actual previews and level directory.')
