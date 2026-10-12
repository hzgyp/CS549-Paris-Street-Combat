from pathlib import Path
import sys,json
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'Tools/Integration/TacticalEquipmentV1'))
from prepare import read,write,sha
review=read(root/'Docs/Development/CURRENT_GRENADE_MODEL_REVIEW.json');doc=review['result']
inv_path=root/'Assets/Registry/assets/inventory.json';inv=read(inv_path)
base=root/'Assets/LocalWorking/Experiments/GrenadeModels/20261011'
for aid,kind,model,description,origin in [
 ('frag-grenade','Frag',base/'frag_finish_v1/MkIIExisting.glb','现有盟军装备分区提取的Mk II手雷，原几何/UV/1024衍生贴图；已集成统一本地试玩，非基础几何占位。','purchased_adapted'),
 ('smoke-grenade','Smoke',base/'smoke/finish_v1/ANM8Smoke.glb','资产索引无独立模型后制作的AN-M8风格灰罐黄标外壳，1943外观资料；已集成统一本地试玩。','team_created')]:
    a=next(a for a in inv['assets'] if a['id']==aid)
    a.update(description=description,origin=origin,validation='最终Game运行/导出验证，人工统一试玩待审',human_review='本次模型候选待人工复验',limitations=['原Hold动作位于屏幕下沿，下半部有继承遮挡；未改手指/角色动作。','静态模型预览不替代实际游戏接触/全动作验收。'],rights_scope='手雷继承伞兵商业源的私下项目共享许可；衍生模型/贴图留私有。烟雾外壳团队原创，史料图未作为贴图或分发。',lifecycle='candidate')
    if aid=='frag-grenade':a['related_ids']=list(dict.fromkeys(a.get('related_ids',[])+['allied-soldier']))
    a['aliases']=list(dict.fromkeys(a.get('aliases',[])+(['Mk II','MKII','WWII grenade'] if aid=='frag-grenade' else ['AN-M8','M8','WWII smoke grenade'])))
    a['documents']=list(dict.fromkeys(a.get('documents',[])+[review['implementation'],doc]))
    inv.setdefault('members',{})[aid]=[dict(name=model.stem,path=model.relative_to(root).as_posix(),kind='GLB',duration=None,frames=None)]+[dict(name=Path(r['path']).name,path=review['playable_directory']+'/'+r['path'],kind='RuntimeGeometry' if r['path'].endswith('.json') else 'Texture2DPNG',duration=None,frames=None) for r in review['assets'] if '/'+kind+'/' in r['path']]
    rules=inv.setdefault('usage_rules',[])
    if not any(x['asset_id']==aid and x.get('filename')=='ParisGrenadeMesh.inl' for x in rules):rules.append(dict(asset_id=aid,filename='ParisGrenadeMesh.inl',needle='Equipment/Grenades',label='统一试玩瞬态网格/PBR；保留原hand_r与玩法/存档，不写native包。'))
write(inv_path,inv)
hist_path=root/'Assets/Registry/mappings/inventory-history.json';hist=read(hist_path)
for aid,tris in [('frag-grenade',2733),('smoke-grenade',7562)]:
    rid=aid+'-model-v1-20261011';assert not any(r['id']==rid for r in hist['revisions'])
    hist['revisions'].append(dict(id=rid,asset_id=aid,title='统一试玩道具模型 v1 (2026-10-11)',kind='inventory_revision',result='local_verified_manual_review_pending',summary='占位模型替换；原手指/枪械/保存保护通过。',scope='资产索引优先，独立GLB与实际UE渲染，13个最终Game实跑；原Hold视图下沿遮挡保留。',document=doc,metrics=dict(triangles=tris,texture_size=1024),media_ids=[]))
write(hist_path,hist)
reg_path=root/'Assets/Registry/registry.json';reg=read(reg_path)
for s in reg['selectors']:
    if s['id']=='ui-review':s['assets']=list(dict.fromkeys(s['assets']+['frag-grenade','smoke-grenade']))
reg['selectors'].append(dict(id='grenade-model-review',channel='candidate',title='手雷/烟雾弹模型统一评审候选',path='Docs/Development/CURRENT_GRENADE_MODEL_REVIEW.json',assets=['frag-grenade','smoke-grenade','allied-soldier','first-person'],optional=True))
write(reg_path,reg)
# Register actual private GLB locations for future inventory lookup; no server run.
p=root/'Assets/LocalWorking/AssetWorkbench/private-records/models.json';models=read(p)
for aid,model,blend in [('frag-grenade',base/'frag_finish_v1/MkIIExisting.glb',base/'frag_finish_v1/MkIIExisting.blend'),('smoke-grenade',base/'smoke/finish_v1/ANM8Smoke.glb',base/'smoke/finish_v1/ANM8SmokePacked.blend')]:
    models['models'].append(dict(id=aid+'-model-v1-20261011',asset_ids=[aid],path=model.relative_to(root).as_posix(),sha256=sha(model),size_bytes=model.stat().st_size,audience='local_owner',label='统一试玩道具模型',label_en='Unified trial prop',revision='model-v1-20261011',scope='静态外观；实际玩法/手持验收见结果，未改人物/手指。',scope_en='Static exterior; see runtime result. Original characters/fingers unchanged.',source_files=[dict(path=blend.relative_to(root).as_posix(),sha256=sha(blend))],clips=[]))
write(p,models)
print('ASSET REGISTRATIONS UPDATED')
