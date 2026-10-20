"""Index existing gameplay designs and sync reviewed asset metadata. No game/asset writes."""
import json,hashlib,re
from pathlib import Path
from asset_index import atomic_write

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Assets/LocalWorking/AssetWorkbench/runs/gameplay-integration-20261013'
OUT.mkdir(parents=True,exist_ok=True)
def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))
def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(path,value):atomic_write(ROOT/path,(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def pair(zh,en):return {'zh':zh,'en':en}
def doc(path,zh,en):return {'path':path,'title':pair(zh,en),'registered_sha256':digest(ROOT/path)}
def docs(stem,title):
    rows=[doc(stem+'_ZH.md',title[0],title[1]+' · Chinese source')]
    if (ROOT/(stem+'.md')).is_file():rows.append(doc(stem+'.md',title[0]+' · English',title[1]))
    return rows
EQUIP=docs('Docs/Development/MissionLoopV1/TACTICAL_EQUIPMENT_GAMEPLAY_DESIGN_20261010',('装备玩法设计','Equipment gameplay design'))
TUTORIAL=docs('Docs/Development/MissionLoopV1/PARIS_TUTORIAL_POSTBRIDGE_DESIGN_20261012',('教程与桥后设计','Tutorial and post-bridge design'))
RECRUIT=docs('Docs/Development/MissionLoopV1/G1_TUTORIAL_SITE_AND_RECRUITMENT_DESIGN_20261013',('教学选点与盟军招募方案','Tutorial sites and Allied recruitment proposal'))
ADOPTION=docs('Docs/Development/G1_SLEEVE_BASELINE_ADOPTION_RESULT_20261013',('当前78正式采用','Current 78 baseline adoption'))
CHECKPOINT=docs('Docs/Development/G1_ENEMY_CLEAR_CHECKPOINT_RESULT_20261010',('清场存档规则','Enemy-clear checkpoint rule'))
entries=[]
def add(aid,kind,title,summary,assets,rules=(),steps=(),open_items=(),sources=(),implemented=False,validation=None,related=(),media=()):
    r={'id':aid,'kind':kind,'title':pair(*title),'summary':pair(*summary),'design_state':'confirmed' if implemented else 'review',
       'revision':'2026-10-13','asset_ids':list(assets),'related_ids':list(related),'documents':list(sources),
       'rules':[pair(*x) for x in rules],'steps':[pair(*x) for x in steps],'open_items':[pair(*x) for x in open_items],'media_ids':list(media),
       'implementation':{'state':'formal' if implemented else 'unimplemented','note':pair('当前正式版已采用；原验证范围保留。' if implemented else '方案尚未接入正式游戏。','Adopted in the current baseline; original validation scope retained.' if implemented else 'This proposal is not implemented in the formal game.')},
       'validation':validation or {'state':'scoped_verified' if implemented else 'pending','note':pair('读取既有结果；本次未重跑游戏。' if implemented else '需要有界实现与实际验证。','Existing results only; the game was not rerun here.' if implemented else 'Bounded implementation and actual validation are required.')}}
    if implemented:r['implementation']['build_id']='formal'
    entries.append(r);return r

add('g1-current','mission',('G1 桥头战斗','G1 bridgehead combat'),('当前可玩阶段：过桥、清除三名登记守军、主动保存。','Current playable stage: cross the bridge, clear three registered guards and save explicitly.'),
    ['paris-city','allied-soldier','german-soldier','first-person'],
    rules=[('所属登记敌军全灭即完成任务；小队到齐、特定路线和教程动作不加锁。','Eliminating the registered enemy group completes the objective; squad arrival, a specific route and tutorial actions do not add gates.'),('保留原两名盟军及三名守军布局；新阶段未实现。','The original two-Allied/three-guard layout is retained; additional stages are not implemented.')],
    sources=ADOPTION+CHECKPOINT,implemented=True,related=['checkpoint','g1-tutorial','m2-junction'])
add('rifle-resources','mechanic',('步枪射击与装弹','Rifle firing and reload'),('原枪械事务与有限弹药守恒。','Original weapon transactions and finite ammunition conservation.'),['first-person','german-rifle','rifle-animation','recorded-audio'],
    rules=[('实际射击消耗装填弹药；空枪不能产生有效射击。','Actual firing consumes loaded rounds; an empty weapon cannot fire effectively.'),('装弹从备用弹药转入枪内，原动作提交一次；不复制或补满库存。','Reload transfers reserve rounds into the weapon and commits once through the original action; no duplication or refill.')],sources=ADOPTION+EQUIP,implemented=True)
add('frag-throw','mechanic',('手榴弹投掷','Fragmentation grenade'),('滚轮选择，按住左键准备，松开投掷。','Select with the wheel, hold the left button to prepare and release to throw.'),['frag-grenade','rifle-animation','explosion-audio'],
    rules=[('滚轮跳过空库存；全部投掷物用尽时仍保留步枪。','The wheel skips exhausted types; the rifle remains available when all throwables are exhausted.'),('准备阶段可取消且不消耗；释放后仅提交一次，有限引信与遮挡伤害沿用。','Preparation can be cancelled without spending inventory; release commits once with the existing finite fuse and occluded damage.')],sources=ADOPTION+EQUIP,implemented=True,related=['smoke-cover','m2-junction'])
add('smoke-cover','mechanic',('烟幕掩护','Smoke cover'),('烟幕影响发现和实时追踪，子弹仍可穿过。','Smoke affects detection and live tracking; bullets can still pass through.'),['smoke-grenade','smoke-effect','rifle-animation'],
    rules=[('同一烟幕过滤两阵营实时视线；离开后可重新发现，不能提供无敌。','The same smoke filters both factions\' live sight; detection can resume after leaving, without invulnerability.'),('烟幕有有限生命期；存读档不重置时间或返还库存。','Smoke has a finite lifetime; restore does not reset its timer or return inventory.')],sources=ADOPTION+EQUIP,implemented=True,related=['frag-throw','m2-junction'])
add('enemy-mine','mechanic',('预设敌方地雷','Preplaced enemy mines'),('观察、绕行或近距离拆除；首版没有玩家布雷。','Observe, bypass or disarm nearby; the first version has no player mine deployment.'),['pressure-mine','explosion-audio','paris-city'],
    rules=[('落地胶囊脚底接触只触发一次，双方均会受影响。','Grounded capsule-foot contact triggers once and affects either faction.'),('可见并瞄准，水平2米内按住E两秒；遮挡、松键或移开取消。','Observe and aim within two horizontal metres, then hold E for two seconds; occlusion, release or moving away cancels.'),('已触发/已拆除状态恢复，不重复伤害；未拆雷不能阻止清场保存。','Spent/disarmed states restore without repeated damage; an armed mine does not block enemy-clear saving.')],sources=ADOPTION+EQUIP,implemented=True,related=['checkpoint','finite-supply'])
add('finite-supply','mechanic',('有限弹药补给','Finite ammunition supply'),('实物箱向备用弹药转移有限库存。','Physical supply boxes transfer finite stock into reserve ammunition.'),['ammo-box','paris-city'],
    rules=[('领取受箱内库存和玩家容量约束，不直接填充枪内弹药。','Grants are bounded by box stock and player capacity; they do not directly load the weapon.'),('同次库存扣减与领取提交；连续按E或读档不重复领取。','Stock reduction and the grant commit together; repeated E or restore cannot duplicate grants.')],sources=ADOPTION+EQUIP,implemented=True,related=['g1-tutorial','m2-junction'])
add('checkpoint','mechanic',('清场与主动存档','Enemy clearance and explicit saving'),('敌军全灭后，进入圈内按E并明确确认。','After enemy clearance, enter the circle, press E and explicitly confirm.'),['paris-city','first-person'],
    rules=[('只有所属登记敌组全灭决定任务门槛；保留圈内交互与实际写盘校验。','Only elimination of the registered enemy group gates the objective; circle interaction and actual write validation remain.'),('保存动态装备、设施库存及状态；校验schema、资源、checksum、写盘和回读。','Save dynamic equipment, facility stock and state; validate schema, resources, checksum, write and readback.'),('取消或写盘失败不能显示已保存；读档不补给或重播已死NPC。','Cancellation or write failure cannot display a save success; restore does not refill resources or replay dead NPCs.')],sources=ADOPTION+CHECKPOINT+EQUIP,implemented=True,related=['enemy-mine','finite-supply'])
add('sleeve-workspace','presentation',('第一人称袖子与装备显示','First-person sleeve and equipment display'),('78版调整显示工作范围，沿用原模型、骨长与手指。','Version 78 adjusts the display workspace while retaining the original mesh, bone lengths and fingers.'),['first-person','frag-grenade','smoke-grenade'],
    rules=[('原模型、权重和UV不替换；失败拟合衍生不进入普通包。','Original meshes, weights and UVs are retained; the failed fitted derivative is excluded from the normal build.')],
    open_items=[('近肩衣料应变及细致接触、全部运动仍有范围限制。','Proximal garment strain, fine contact and complete locomotion remain outside the passed scope.')],
    sources=ADOPTION+docs('Docs/Development/SLEEVE_OCCLUSION_RESULT_20261012',('袖子显示验证','Sleeve display validation')),implemented=True,media=['fp-sleeve-reload-v12','fp-sleeve-smoke-v12'])
tutorial=add('g1-tutorial','mission',('G1 过桥教程','G1 bridge tutorial'),('前岸练习、对话招募、过桥应用、桥头清场、观察拆雷、主动保存。','Near-bank practice, recruitment dialogue, bridge crossing, bridgehead combat, mine disarm and explicit saving.'),
    ['paris-city','first-person','allied-soldier','german-soldier','ammo-box','pressure-mine','frag-grenade','smoke-grenade'],
    rules=[('教程完成标记不成为清场或保存的新门槛。','Tutorial completion flags never add enemy-clear or save gates.'),('Ready当前不允许移动；需独立教学状态和安全练习点。','Ready currently disallows movement; a separate teaching phase and safe practice sites are required.')],
    steps=[('移动、看向和跑步：WASD、鼠标、Shift。','Move, look and run: WASD, mouse and Shift.'),('起跳落地：Space；先验起落净空。','Jump/land: Space; first validate takeoff and landing clearance.'),('Ctrl蹲、Z匍匐并真实移动、再起身。','Crouch with Ctrl, prone with Z, actually crawl and stand up.'),('安全射线处真实射击与R装弹。','Actually fire along a safe line and reload with R.'),('瞄准前岸有限弹药箱按E领取备用弹。','Aim at the near-bank finite supply box and press E for reserve rounds.'),('沿C桥跟随并利用掩体清除原三名守军。','Cross bridge C with squad support and cover, clearing the original three guards.'),('清场后观察雷1并练习拆除；雷2说明绕行。','After clearance, observe mine 1 and practise disarming; mine 2 illustrates bypassing.'),('CP1圈内按E、明确确认并检查保存成功。','At CP1, press E inside the circle, explicitly confirm and check save success.')],
    open_items=[('前岸练习净空、连续匍匐足迹、安全射线与盟军通行待验。','Near-bank clearance, continuous crawling footprints, safe firing lines and Allied passage require validation.')],sources=TUTORIAL+RECRUIT,related=['g1-current','checkpoint','m2-junction','allied-recruitment'],media=['design-g1-tutorial','design-tutorial-local'])
tutorial['steps'].insert(5,pair('先完成匍匐练习，再对话确认招募第一名盟军；第二名可选，不作为过关门槛。','After validated crawling, confirm the first Allied recruit through dialogue; the second is optional and never gates progress.'))
tutorial['rules'].append(pair('13October招募方案替代早期自动跟随教学安排；原12October设计图保留早期布局。','The 13 October recruitment proposal supersedes the early automatic-follow tutorial plan; the 12 October figure retains its earlier layout.'))
tutorial['open_items'].append(pair('当前匍匐点不能采用；E5仅为首查区域，连续5至8米短廊需原玩家实测。','The current crawl site cannot be adopted; E5 is only the first inspection region, and the proposed 5–8 m corridor needs original-player validation.'))
add('allied-recruitment','mechanic',('盟军对话招募与有限补招','Allied dialogue recruitment and finite replacements'),('明确确认招募，最多两名存活队员；阵亡释放名额，有限人员池补充。','Confirm recruitment explicitly, with at most two living squadmates; casualties release slots for a finite replacement pool.'),
    ['allied-soldier','paris-city','first-person'],
    rules=[('新游戏拟从0/2开始；近距离可见且无墙遮挡，按E对话，再选择加入并确认。开启对话不能同帧确认。','Proposed new games begin at 0/2; aim at a visible nearby recruit without wall occlusion, press E for dialogue, then choose Join and confirm in a later input.'),
           ('最多两名存活且已招募盟军；落后或寻路卡住仍占名额，不能自动补出第三人。','At most two living recruited Allies; lagging or blocked members still occupy slots and cannot create a third member.'),
           ('保留阵亡NPC与尸体；只从有限登记池招募其他存活NPC。建议原G1两人及M2/M3各一名备用，共四人，数量和地点待评审。','Preserve dead NPCs and corpses; recruit other living NPCs only from a finite registered pool. The draft suggests the original G1 pair plus one reserve at M2 and M3, four total, with counts/sites awaiting review.'),
           ('取消、重复交谈和招募不补血、不重置库存、不赠玩家弹药；交火期间不开放对话。','Cancel, repeat interaction and recruitment never heal, reset stock or grant player ammo; dialogue is unavailable during combat.'),
           ('E模态输入不穿透弹药箱、拆雷或存档；未招募或人员池耗尽不锁住任务和存档。','Modal E input cannot leak to supplies, mine disarm or saving; no recruits or an exhausted pool never gates missions or saves.')],
    open_items=[('距离建议2米，实际对话站位和可见性待验。','The proposed distance is 2 m; actual dialogue sites and visibility require validation.'),
                ('原存档校验固定六演员；新NPC稳定ID、死亡记录、名额和有限池需独立版本兼容、资源与checksum设计。','Original saves validate six fixed actors; new stable IDs, deaths, slots and finite pools require separate version compatibility, resource and checksum design.'),
                ('先由用户选匍匐区域，再写UI、AI和名册存档实施清单；当前正式游戏不改。','First obtain the user-selected crawl region, then prepare UI, AI and roster-save implementation plans; the formal game remains unchanged.')],
    sources=RECRUIT,related=['g1-tutorial','m2-junction','m3-crossstreet','checkpoint'],media=['design-tutorial-local'])
add('m2-junction','mission',('M2 进城路口突破','M2 city-junction assault'),('选择掩体推进或烟幕转移，转角用射击或手雷，可选绕雷补给。','Choose cover or smoke for approach, firing or a grenade at corners, and optional mined supply detours.'),
    ['paris-city','german-soldier','allied-soldier','frag-grenade','smoke-grenade','pressure-mine','ammo-box'],
    rules=[('初稿三名守军；位置、人数与两条接近路线均未冻结。','The draft suggests three guards; positions, count and both approaches are not frozen.'),('必须保留不使用指定消耗品的完成方法；只清除本组守军解锁CP2。','Keep a completion method without a required consumable; only clearing this group unlocks CP2.')],
    open_items=[('G1至T2两条走廊均有测绘连接缺口，需实际通行与双向交火验证。','Both G1-to-T2 corridors have survey connectivity gaps; actual movement and reciprocal combat require validation.'),('G1完成后需保持后续AI运行，目前正式版仍以G1作为整局阶段。','Later AI must continue after G1 completion; the formal game still treats G1 as the complete mission.')],sources=TUTORIAL,related=['g1-tutorial','postbridge-routes','m3-crossstreet'],media=['design-postbridge'])
add('m3-crossstreet','mission',('M3 横街据点','M3 cross-street strongpoint'),('两端入口、分散守军与有限补给取舍。','Two approaches, distributed guards and finite supply decisions.'),['paris-city','german-soldier','allied-soldier','smoke-grenade','frag-grenade','ammo-box'],
    rules=[('初稿四名守军分为两组阵位，室外街区先于建筑内部。','The draft suggests four guards in two supporting positions; outdoor streets precede interiors.'),('最后登记敌组全灭才结束整局；CP3沿用清场主动保存原则。','Only the final registered enemy group ends the complete mission; CP3 retains enemy-clear explicit saving.')],
    open_items=[('先做G1教程＋M2统一试玩；M3人数、点位、小队与交火待验。','First build the G1 tutorial plus M2 trial; M3 count, sites, squad passage and combat remain unverified.')],sources=TUTORIAL,related=['m2-junction','postbridge-routes'],media=['design-postbridge'])
routes=add('postbridge-routes','route',('G1 至T2/T3路线与地点','G1-to-T2/T3 routes and sites'),('25厘米保存/扩展测绘分别记录；测绘连接不是新实体实走。','Saved and expanded 25 cm surveys are recorded separately; graph links are not new physical traversal.'),['paris-city'],
    rules=[('两套范围不合并；黑色含阻挡、未准入和未知，L0不是建筑一层。','Never merge the scopes; black includes blocked, unadmitted and unknown cells, and L0 is not a building floor.'),('CP1至外侧街道、内侧转角均有连接缺口；T2至T3仅测绘图连接。','Both CP1 approaches have connectivity gaps; T2-to-T3 currently has survey graph links only.')],
    sources=TUTORIAL,validation={'state':'survey_only','note':pair('T2至T3：保存157.02米、扩展158.46米，均非新的UE实走距离。','T2-to-T3: 157.02 m saved and 158.46 m expanded graph lengths; neither is a new UE traversal distance.')},related=['m2-junction','m3-crossstreet','bridge-ab'],media=['design-postbridge'])
text=(ROOT/TUTORIAL[0]['path']).read_text(encoding='utf-8')
routes['locations']=[]
point_notes={'CP1':'Existing G1 save position; retain it.','EAST_EXIT':'Eastern exit candidate; linked to CP1 in the survey, next segment unresolved.',
             'RIVER_APPROACH':'Inner approach candidate; linked to CP1, corner connection unresolved.','OUTER_APPROACH':'A 1.768 m nearby diagnostic sample in a local group; not a frozen route.',
             'INNER_TURN':'A 0.707 m nearby sample; northern survey links exist, southern connection unresolved.','INNER_STREET':'Inner junction candidate; linked to the north cross-street in the survey, combat untested.',
             'T2':'Existing junction candidate; CP2 and guard sites require separate validation.','NORTH_CROSS':'North cross-street candidate; surveyed links to T2/T3, flank firing lines untested.',
             'T3':'Cross-street candidate; CP3 and guard sites require separate validation.'}
for line in text.splitlines():
    match=re.match(r'\| (CP1|EAST_EXIT|RIVER_APPROACH|OUTER_APPROACH|INNER_TURN|INNER_STREET|T2|NORTH_CROSS|T3) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|',line)
    if match:
        name,xyz,support,note=match.groups()
        routes['locations'].append({'id':name,'foot_xyz_m':[float(n.strip().replace('−','-')) for n in xyz.split('，')],'support':support.strip(),
                                    'note':pair(note.strip(),point_notes[name])})
assert len(routes['locations'])==9
bridge=add('bridge-ab','route',('A/B 桥路线验证','Bridge A/B route validation'),('固定普通步行四个方向未达另一岸；人工自由入口仍待复核。','Four fixed walking legs did not reach the opposite bank; the free manual trial still awaits review.'),['paris-city','first-person'],
    rules=[('A正向5.08米、反向2.54米；B正向13.21米、反向10.03米，均未达35厘米终点门槛。','A outward 5.08 m/reverse 2.54 m; B outward 13.21 m/reverse 10.03 m; none met the 35 cm endpoint gate.'),('B正向有49个桥面支撑样本，但不是全程走通；四次原生路径查询未通过。','B outward had 49 deck-support samples but did not traverse the whole route; all four native path queries failed.'),('固定腿失败不证明所有入口或绕行不可通；人工入口启动不证明人工跨岸成功。','Fixed-leg failures do not prove all approaches are blocked; launching the manual trial does not prove a manual crossing.')],
    open_items=[('入口、落脚、阻挡Hit和完整绕行足迹待查；不改碰撞或扫描偏移刷通过。','Entrances, landing supports, blocking hits and complete detour footprints need investigation; do not relax collisions or scan offsets to manufacture a pass.')],
    sources=docs('Docs/Development/MissionLoopV1/AB_BRIDGE_PHYSICAL_RESULT_20261013',('A/B固定路线负面','A/B fixed-route negatives'))+docs('Docs/Development/MissionLoopV1/AB_BRIDGE_MANUAL_RESULT_20261013',('人工自由入口待复核','Manual trial awaiting review')),
    validation={'state':'failed_fixed_routes','note':pair('固定路线诊断从旧正式76派生；人工自由入口从78派生。启动与通过分开。','Fixed-route diagnostics derive from formal 76; the free manual trial derives from 78. Launch and successful traversal are separate.')},related=['postbridge-routes'])
bridge['design_state']='reference';bridge['implementation']['state']='diagnostic';bridge['implementation']['note']=pair('仅有独立诊断入口，未采用为任务路线。','Only isolated diagnostic trials exist; these are not adopted mission routes.')
paths=['Assets/Registry/registry.json','Assets/Registry/assets/pilots.json','Assets/Registry/assets/inventory.json','Assets/Registry/mappings/history.json','Assets/Registry/mappings/inventory-history.json','Assets/LocalWorking/AssetWorkbench/private-records/media.json']
original={p:digest(ROOT/p) for p in paths};data={p:load(p) for p in paths}
baseline=load('Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json');assert baseline['source_snapshot']=='Unreal/Variants/G1SleeveWorkspace20261012/Project'
protected={p:digest(ROOT/p) for p in ['Assets/Sync/CATALOG.json','Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json','Docs/Development/CURRENT_SLEEVE_REVIEW.json',baseline['source_manifest']]}
reg=data[paths[0]];reg['gameplay']='Assets/Registry/gameplay/designs.json'
for s in reg['selectors']:
    if s['id']=='ui-review':s.update(channel='historical',title='已采用玩法父版76')
if not any(s['id']=='sleeve-review' for s in reg['selectors']):reg['selectors'].append({'id':'sleeve-review','channel':'formal','title':'当前袖子修复正式78','path':'Docs/Development/CURRENT_SLEEVE_REVIEW.json','assets':['first-person','frag-grenade','smoke-grenade'],'optional':True})
media=data[paths[5]]
for mid,aid,path,label,kind in [
    ('fp-sleeve-reload-v12','first-person','Docs/Images/FirstPersonSleeve/SLEEVE_RELOAD_20261012.png','袖子正式78 · 原模型换弹实图','真实Game截图'),
    ('fp-sleeve-smoke-v12','first-person','Docs/Images/FirstPersonSleeve/SLEEVE_SMOKE_20261012.png','袖子正式78 · 烟雾弹显示实图','真实Game截图'),
    ('design-g1-tutorial','paris-city','Docs/Images/MissionLoopV1/PARIS_G1_TUTORIAL_DESIGN_20261012.png','G1教程设计图（中文原图）','设计图 · 非运行验收'),
    ('design-tutorial-local','paris-city','Docs/Images/MissionLoopV1/G1_TUTORIAL_LOCAL_25CM_20261013.png','G1教学局部25厘米选点图（中文原图）','设计图 · 非运行验收'),
    ('design-postbridge','paris-city','Docs/Images/MissionLoopV1/PARIS_POSTBRIDGE_ROUTE_DESIGN_20261012.png','桥后区域设计图（中文原图）','设计图 · 非运行验收')]:
    f=ROOT/path;row={'id':mid,'asset_id':aid,'path':path,'sha256':digest(f),'size_bytes':f.stat().st_size,'mime':'image/png','label':label,'kind':kind,'audience':'local_owner','rights_basis':'User requested internal project workbench; reviewed project document figure; no coursework upload performed'}
    media['files']=[m for m in media['files'] if m['id']!=mid]+[row]
fp=next(a for a in data[paths[1]]['assets'] if a['id']=='first-person')
fp['documents']=list(dict.fromkeys(fp.get('documents',[])+[d['path'] for d in ADOPTION]))
fp['validation']='原模型沿用；袖子显示工作范围v12已人工采用，完整形变/接触限制保留。'
for a in data[paths[1]]['assets']:
    if a['id'] in reg['selectors'][0]['assets']:
        a['lifecycle']='retained';a['human_review']='当前正式版采用；原验证范围保留。'
fp_history=next(h for h in data[paths[3]]['revisions'] if h['id']=='fp-sleeve-workspace-v12')
fp_history.update(scope='13 October人工采用；既有9项Game/17张图/1545帧范围保留，不新增全动作验收。',media_ids=['fp-sleeve-reload-v12','fp-sleeve-smoke-v12'])
inv=data[paths[2]];history=data[paths[4]]
for aid in ['frag-grenade','smoke-grenade']:
    a=next(a for a in inv['assets'] if a['id']==aid);a['lifecycle']='retained';a['validation']='模型v1沿用；投掷玩法已正式采用，当前78版保留。'
    a['description']='Mk II 手雷；原几何与PBR沿用，当前正式78版使用模型v1。' if aid=='frag-grenade' else 'AN-M8 风格烟雾弹；自建外壳与PBR，当前正式78版使用模型v1。'
    a['human_review']='当前正式版采用；原验证范围保留。'
    a['documents']=list(dict.fromkeys(a.get('documents',[])+[d['path'] for d in ADOPTION]))
    for member in inv['members'][aid]:
        if member['kind'] in ('RuntimeGeometry','Texture2DPNG'):
            suffix=member['path'].split('/Windows/',1)[1];target=ROOT/baseline['playable_directory']/'Windows'/suffix
            assert target.is_file(),'Current runtime asset unavailable'
            protected[target.relative_to(ROOT).as_posix()]=digest(target)
            member['path']=target.relative_to(ROOT).as_posix()
    model=next(h for h in history['revisions'] if h['id']==aid+'-model-v1-20261011')
    rid=aid+'-formal-inherited-78-20261013'
    history['revisions']=[h for h in history['revisions'] if h['id']!=rid]+[{'id':rid,'asset_id':aid,'title':'正式78沿用模型v1与投掷玩法','kind':'integration_revision','parent_ids':[aid+'-wheel-integration-v4-20261011'],'document':ADOPTION[0]['path'],'model_identity':model['model_identity'],'summary':'原模型字节不改；76玩法已人工采用，78仅更新第一人称显示工作范围。','scope':'读取人工采用与既有结果；不是本次游戏重跑或新的完整接触验收。','result':'accepted_with_limits','media_ids':model.get('media_ids',[]),'metrics':{'game_sha256':baseline['game_sha256'],'source_manifest_sha256':baseline['source_manifest_sha256']}}]
from app.gameplay import validate
validate({'schema_version':1,'entries':entries},{a['id'] for a in data[paths[1]]['assets']+inv['assets']})
for p in paths:
    assert digest(ROOT/p)==original[p],'Concurrent registration edit; stop before writing'
for p in paths:
    backup=OUT/(Path(p).stem+'-'+str(paths.index(p))+'-before.json')
    if not backup.exists():backup.write_bytes((ROOT/p).read_bytes())
    save(p,data[p])
save(reg['gameplay'],{'schema_version':1,'entries':entries})
assert all(digest(ROOT/p)==h for p,h in protected.items()),'Protected original changed'
save((OUT/'registration.json').relative_to(ROOT).as_posix(),{'status':'registered_pending_refresh','gameplay_count':len(entries),'asset_ids_updated':['first-person','frag-grenade','smoke-grenade','paris-city'],'protected_inputs':protected,'protected_inputs_unchanged':True})
print('Registered',len(entries),'gameplay entries and current78 asset metadata; original bytes preserved.')
