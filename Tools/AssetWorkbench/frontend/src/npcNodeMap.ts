import type {TreeDefinition,TreeTrace} from './NpcBehaviorTree';
import {sightReason,type SightEvidence} from './npcSight.ts';
import {searchExplanation,type SearchEvidence} from './npcSearch.ts';
import {fireReason} from './npcCombat.ts';
import {maneuverReason} from './npcManeuver.ts';

export type MapPoint=[number,number];
export type NodeMark={id:string;point:MapPoint;label:string;kind:'desired'|'goal'|'observation'|'origin'|'candidate'|'rejected';radius?:number};
export type NodeEvidence={actorId:string;nodeId:string;at:number;status:string;title:string;reason:string;facts:string[];marks:NodeMark[];path:MapPoint[];vision?:SightEvidence;search?:SearchEvidence;area?:{centre:MapPoint;radius:number;label:string}};
type EvidenceFrame={at:number;actors:Record<string,{position:MapPoint}>;minds:Record<string,any>;moves:Record<string,any>;scores:Record<string,any[]>;behavior_trees:Record<string,TreeTrace>};
const point=(v:any):v is MapPoint=>Array.isArray(v)&&v.length===2&&v.every(Number.isFinite);
const num=(v:any)=>typeof v==='number'&&Number.isFinite(v)?v.toFixed(2):'—';
const xy=(p:MapPoint)=>`(${num(p[0])}, ${num(p[1])}) m`;
const same=(a:any,b:any)=>point(a)&&point(b)&&Math.hypot(a[0]-b[0],a[1]-b[1])<1e-6;

/** Projects recorded evidence only. Never evaluates AI conditions or admits a path. */
export function nodeMapEvidence(frame:EvidenceFrame|undefined,definition:TreeDefinition|undefined,actorId:string,nodeId:string,english=false,search?:SearchEvidence):NodeEvidence|undefined{
 if(!frame||!definition)return;
 const trace=frame.behavior_trees[actorId],byId=Object.fromEntries(definition.nodes.map(n=>[n.id,n]));
 const node=byId[nodeId]||byId[definition.root],record=trace?.nodes[node.id];if(!record)return;
 const t=(zh:string,en:string)=>english?en:zh,label=(id:string)=>byId[id]?.label[english?1:0]||id;
 const result:NodeEvidence={actorId,nodeId:node.id,at:trace.at,status:record.status,title:label(node.id),reason:'',facts:[],marks:[],path:[]};
 const board=trace.blackboard,fact=(zh:string,en:string)=>result.facts.push(t(zh,en));
 if(search){result.search={...search,nodeId:node.id};fact(searchExplanation(search),searchExplanation(search,true));fact(`记录搜索点 ${search.steps.map(s=>'S'+s.order).join(' → ')||'尚无'}；剩余 ${search.remaining===undefined?'未计时':num(search.remaining)+' s'}；本帧 ${num(search.at)} s。`,`Recorded search points ${search.steps.map(s=>'S'+s.order).join(' → ')||'none'}; remaining ${search.remaining===undefined?'inactive':num(search.remaining)+' s'}; frame ${num(search.at)} s.`)}
 const sight=board.player_sight as SightEvidence|undefined;
 if(sight?.schema==='paris.npc.sight.v1'){
  result.vision=sight;
  fact(`感知 ${sight.at.toFixed(1)} s → 树判定 ${trace.at.toFixed(1)} s；射线端点是感知时的位置，不随平滑人物移动。`,`Sense ${sight.at.toFixed(1)} s → tree tick ${trace.at.toFixed(1)} s; ray endpoints are sampled positions, not animated poses.`);
  fact(`距离 ${num(sight.distance_m)} / ${num(sight.range_m)} m；偏角 ${num(sight.angle_degrees)} / 半视角 ${num(sight.half_fov_degrees)}°（完整视角 ${num(sight.fov_degrees)}°）。`,`Distance ${num(sight.distance_m)} / ${num(sight.range_m)} m; off-axis ${num(sight.angle_degrees)} / half-FOV ${num(sight.half_fov_degrees)}° (full FOV ${num(sight.fov_degrees)}°).`);
  fact('树的实时视觉条件检查任意盟军；玩家判定单独显示。未执行的后续检查不当作失败。','The tree checks any Allied hostile; player visibility is shown separately. Skipped downstream gates are not failures.');
  fact('显示数值保留两位小数；角度判定使用未舍入的点积与阈值。扇形为采样轮廓示意，射线和遮挡点来自精确栅格遍历。','Numbers are rounded to two decimals; the angle gate uses unrounded dot/cos values. The fan is illustrative; the ray and first hit use exact grid traversal.');
  fact(`本次看见：${sight.visible_hostiles.join(', ')||'无'}。地图黑色包含未知区域；射线保守检查穿角两侧栅格。`,`Visible hostiles: ${sight.visible_hostiles.join(', ')||'none'}. Black includes unknown cells; conservative rays check both sides at corners.`);
  if(sight.ray?.point)fact(`首个遮挡点 ${xy(sight.ray.point)}${sight.ray.cell?' · 栅格 '+sight.ray.cell.join(', '):''}。红点后虚线仅表示到玩家的参考连线。`,`First hit ${xy(sight.ray.point)}${sight.ray.cell?' · cell '+sight.ray.cell.join(', '):''}. The dashed segment beyond it is a reference to the player.`);
 }
 const mark=(id:string,p:any,zh:string,en:string,kind:NodeMark['kind'])=>{if(point(p)&&!result.marks.some(m=>m.id===id))result.marks.push({id,point:[...p],label:t(zh,en),kind})};
 const ancestors=[];let current=node;
 while(current.id!==definition.root){const parent=definition.nodes.find(n=>n.children.includes(current.id));if(!parent)break;ancestors.unshift(parent);current=parent}
 if(record.status==='Skipped'){
  const blocker=[...ancestors].reverse().find(n=>{const d=trace.nodes[n.id]?.detail;return d?.stopped_child||d?.selected_child});
  const detail=blocker&&trace.nodes[blocker.id].detail;
  const child=detail?.stopped_child||detail?.selected_child;
  result.reason=child?t(`未执行：${label(blocker!.id)}${detail?.stopped_child?'停在':'已选中'}「${label(child)}」。`,`Not evaluated: ${label(blocker!.id)} ${detail?.stopped_child?'stopped at':'selected'} “${label(child)}”.`):t('未执行：本次没有访问该分支。','Not evaluated: this branch was not visited in this tick.');
  fact('没有该节点本次的条件结果或目标；不套用其他分支的目标。','No predicate result or target for this node in this tick; targets from other branches are not substituted.');
  return result;
 }
 const d=record.detail,op=node.op;
 const descendants=(id:string):string[]=>[id,...byId[id].children.flatMap(descendants)];
 const records=descendants(node.id).filter(id=>trace.nodes[id]?.status!=='Skipped').map(id=>({node:byId[id],...trace.nodes[id]}));
 const stop=d.stopped_child||d.selected_child;
 result.reason=stop?t(`${d.stopped_child?'序列停在':'选择分支'}「${label(stop)}」：${trace.nodes[stop]?.status}。`,`${d.stopped_child?'Sequence stopped at':'Selected branch'} “${label(stop)}”: ${trace.nodes[stop]?.status}.`):node.description[english?1:0];
 if(node.kind==='ForceSuccess')result.reason=t(`子节点 ${d.child_status}；这里只保留意图，不代表人物已到达。`,`Child ${d.child_status}; this preserves intent and does not claim physical arrival.`);
 const predicates:Record<string,()=>void>={
  dead:()=>{result.reason=t(`存活=${d.alive}；生命值 ${d.health}。阵亡分支停止移动和射击。`,`Alive=${d.alive}; health ${d.health}. The casualty branch stops movement and fire.`)},
  fire_ready:()=>{result.reason=fireReason(d.reason,english);fact(`目标 ${d.target||'无'} · 弹药 ${d.ammo} · 冷却剩余 ${num(d.cooldown_remaining)} s · 武器上限 ${d.range_limit} m${d.blocking_actor?' · 挡住射界 '+d.blocking_actor:''}。`,`Target ${d.target||'none'} · ammo ${d.ammo} · cooldown ${num(d.cooldown_remaining)} s · weapon limit ${d.range_limit} m${d.blocking_actor?' · blocked by '+d.blocking_actor:''}.`);mark('fire-origin',d.origin,'射手采样位置','Sampled shooter','origin');mark('fire-target',d.target_position,'射击检查目标','Fire-check target','observation')},
  squad_report:()=>{const r=d.report;result.reason=r?t(`${r.victim}${r.kind==='casualty'?'阵亡':'遇袭'}通报；${d.live_visible?'自己已有视线，优先目视':'没有自己的实时视线，只能调查通报'}。`,`${r.victim} ${r.kind} report; ${d.live_visible?'own sight takes priority':'no own sight: investigate the report only'}.`):t('没有可用的小队遇袭通报。','No usable squad incident report.');if(r){mark('reported-origin',r.position,'冻结通报位置','Frozen reported location','origin');fact(`通报 ${num(r.at)} s · 来源 ${r.source} · ${r.basis==='victim_last_sight'?'受击者最后目击':'粗略枪声 / 受击方位'} · 不确定半径 ${num(r.uncertainty)} m。`,`Report ${num(r.at)} s · source ${r.source} · ${r.basis} · uncertainty ${num(r.uncertainty)} m.`)}},
  budget:()=>{result.reason=t(`规划耗尽条件${record.status==='Success'?'通过':'未通过'}；已用 ${d.requests} / ${d.limit} 次，移动结果 ${d.result}。`,`Planning-exhausted predicate ${record.status==='Success'?'passed':'failed'}; ${d.requests} / ${d.limit} requests, movement ${d.result}.`)},
  assigned:()=>{result.reason=d.assignment?t(`已获共同分工：${d.role} → ${d.assignment}。`,`Joint assignment exists: ${d.role} → ${d.assignment}.`):t('未获得共同分工位置；转入后续归队/跟随判断。','No joint assignment; subsequent regroup/follow branches may run.');fact(`分工器原因：${d.reason}`,`Assignment reason: ${d.reason}`)},
  contact:()=>{result.reason=d.observation?t('有本次可用的小队敌情，归队条件通过。','Usable squad observation exists; regroup predicate passed.'):t('没有本次可用的小队敌情，归队条件失败。','No usable squad observation in this tick; regroup predicate failed.')},
  goal:()=>{result.reason=point(d.goal)?t(`目标存在：${xy(d.goal)}；此条件不检查实际到达。`,`Goal exists: ${xy(d.goal)}; this predicate does not test arrival.`):t('本分支没有获得目标；不能提交该分支的移动。','This branch produced no goal; its movement cannot be submitted.')},
  visible:()=>{result.reason=t(`实时视觉输入 = ${d.live_visible?'是':'否'}，私人观察 = ${d.observation?'有':'无'}；两者同时成立才通过。`,`Live sight = ${!!d.live_visible}, private observation = ${d.observation?'present':'absent'}; both are required.`);if(sight){result.reason=t(`树条件${record.status==='Success'?'通过':'失败'}：看见 ${sight.visible_hostiles.join(', ')||'无目标'}，保留观察 ${d.observation?.actor_id||'无'}。`,`Tree ${record.status}: visible ${sight.visible_hostiles.join(', ')||'none'}, retained observation ${d.observation?.actor_id||'none'}.`);fact(sightReason(sight),sightReason(sight,true))}else fact(`视野 ${d.german_sight_range} m / ${d.german_sight_fov_degrees}°；日志未细分距离、朝向或遮挡的拒绝原因。`,`Vision ${d.german_sight_range} m / ${d.german_sight_fov_degrees}°; this trace does not split rejection into distance, facing or occlusion.`)},
  alert:()=>{result.reason=t(`判定时状态 ${d.state}；已持续 ${num(d.elapsed)} s，警戒停留 ${num(d.dwell)} s。`,`State at evaluation: ${d.state}; elapsed ${num(d.elapsed)} s, alert dwell ${num(d.dwell)} s.`);fact('Guard/Return 直接通过；Alert 需尚未超过停留时间。','Guard/Return pass directly; Alert requires elapsed time below dwell.')},
  hearing:()=>{result.reason=t(`观察来源 ${d.sense||'无'}，状态 ${d.state}；需要仍在短暂警戒中的听觉观察。`,`Observation sense ${d.sense||'none'}, state ${d.state}; requires a hearing observation during the short Alert phase.`)},
  grace:()=>{result.reason=t(`距最后目视 ${num(d.since_last_sight)} s，宽限 ${num(d.grace)} s；还需保留视觉观察。`,`Since last sight ${num(d.since_last_sight)} s, grace ${num(d.grace)} s; a sight observation must also remain.`);fact(`保留观察来源：${board.observation?.sense||'无'}`,`Retained observation sense: ${board.observation?.sense||'none'}`)},
  memory:()=>{result.reason=t(`观察时刻 ${num(d.observation?.at)} s，已消费至 ${num(d.consumed_at)} s；只有更新的私人观察才通过。`,`Observation at ${num(d.observation?.at)} s, consumed through ${num(d.consumed_at)} s; only a newer private observation passes.`)},
  search:()=>{result.reason=t(`判定时状态 ${d.state}，栅格场景 ${d.raster?'是':'否'}；还需策略提供搜索目标。`,`State at evaluation ${d.state}, raster scene ${!!d.raster}; the policy must also supply a search goal.`)},
  guard:()=>{result.reason=t(`状态 ${d.state} ${d.state==='Guard'?'等于':'不等于'} Guard。`,`State ${d.state} ${d.state==='Guard'?'equals':'does not equal'} Guard.`)}
 };
 if(op&&predicates[op])predicates[op]();
 if(node.id==='bound'||node.id.startsWith('bound.')||node.id==='coordination'||node.id.startsWith('coordination.')){
  const m=d.maneuver||d.cover&&d||board.maneuver;
  result.reason=maneuverReason(m,english);
  if(m){
   fact(`分工 ${m.role} · ${m.reason}`,`Role ${m.role} · ${m.reason}`);
   mark('maneuver-goal',m.goal,'本成员实际分工目标','Admitted maneuver goal','goal');
   if(m.cover){const c=m.cover;mark('cover-hide',c.hide,'经遮挡验证的藏身点','Occluded hide point','goal');mark('cover-peek',c.peek,'可连通的探出射击点','Connected clear peek','candidate');mark('cover-blocker',c.blocker?.point,'藏身射线的实际遮挡点','Actual hide-ray obstruction','rejected');mark('cover-threat',c.threat,'验证掩体的冻结敌情 / 朝向','Frozen threat / authored direction','observation');fact(`藏身遮挡 ${c.hide_blocked?'✓':'×'} · 探出射界 ${c.peek_clear?'✓':'×'} · 连接净空 ${c.connector_clear?'✓':'×'} · 路径 ${c.path_status} · 取样 ${num(c.query_at)} s。`,`Hide blocked ${!!c.hide_blocked} · peek clear ${!!c.peek_clear} · connector clear ${!!c.connector_clear} · path ${c.path_status} · query ${num(c.query_at)} s.`)}
   if(m.contact){mark('shared-contact',m.contact.position,'目击者冻结通报','Frozen observer report','origin');fact(`目击者 ${m.contact.source} · 取样 ${num(m.contact.at)} s；通报不授予实时开火权限。`,`Observer ${m.contact.source} · sample ${num(m.contact.at)} s; a report never grants fire permission.`)}
   if(m.last_swap)fact(`上次换位：${m.last_swap.arrived_actor} @ ${num(m.last_swap.at)} s · 当时距藏身点 ${num(m.last_swap.error)} m。`,`Last swap: ${m.last_swap.arrived_actor} at ${num(m.last_swap.at)} s · physical hide error ${num(m.last_swap.error)} m.`);
  }
 }
 for(const r of records.filter(r=>['tactical_contact','scouting','covering','tactical_plan'].includes(r.node.op||''))){const a=r.detail;fact(`角色 ${a.role} · 接敌 ${a.contact?'是':'否'} · 玩家范围 ${a.leash} m · 已追击 ${num(a.chase_used)} / ${a.chase_limit} m。`,`Role ${a.role} · contact ${!!a.contact} · player leash ${a.leash} m · chase ${num(a.chase_used)} / ${a.chase_limit} m.`);mark('tactical-desired',a.desired_slot,'原始战术位','Desired tactical slot','desired');mark('tactical-goal',a.goal,'接纳战术位','Admitted tactical slot','goal');if(r.node.id===node.id)result.reason=t(`${a.reason}；${a.goal?'有完整且分离的位置':'无完整候选，明确等待'}。`,`${a.reason}; ${a.goal?'complete separated destination admitted':'no complete candidate; wait'}.`)}
 const formation=records.find(r=>r.node.op==='formation');
 if(formation){const f=formation.detail;mark('desired',f.desired_slot,'原始跟随位','Desired follow slot','desired');mark('formation-goal',f.goal,'可用跟随位','Admitted follow slot','goal');fact(`跟随距离 ${num(f.follow_distance)} m；${f.goal?'已获得可用队形目标':'没有完整的独立队形路径'}。`,`Follow distance ${num(f.follow_distance)} m; ${f.goal?'an admitted formation goal exists':'no complete separated formation path was obtained'}.`);if(op==='formation')result.reason=t('空心菱形是原始队形位，实心目标是路径接纳的位置；计算成功不等于已经到达。','Hollow diamond: desired slot; solid target: admitted goal. Successful computation does not mean arrival.')}
 const roleScope=node.id==='role'||node.id.startsWith('role.');
 if(roleScope){
  const assignment=records.find(r=>r.node.op==='assigned')?.detail.assignment||records.find(r=>r.node.op==='reserve_role')?.detail.slot||(record.status!=='Failure'?board.reservation?.id:null);
  for(const row of frame.scores[actorId]||[]){const chosen=row.id===assignment;mark('cover-'+row.id,row.position,`${row.id}${chosen?' 已分配':row.valid?' 候选':' 拒绝'}`,`${row.id}${chosen?' assigned':row.valid?' candidate':' rejected'}`,chosen?'goal':row.valid?'candidate':'rejected');fact(`${row.id} ${xy(row.position)} · ${row.valid?'可用':'拒绝'} · 得分 ${num(row.score)}${row.gates?.length?' · '+row.gates.join(', '):''}`,`${row.id} ${xy(row.position)} · ${row.valid?'admitted':'rejected'} · score ${num(row.score)}${row.gates?.length?' · '+row.gates.join(', '):''}`)}
  if(!frame.scores[actorId]?.length)fact('本次分工器没有生成支援候选点。','The assignment policy generated no support candidates in this tick.');
  fact('每名盟军独立选择完整路径与射界合适的位置；排除队友已预约的位置，一人阵亡不会禁止另一人支援。','Each ally independently selects a complete path and suitable fire lane, excluding teammate reservations. A casualty does not disable the surviving ally.');
 }
 for(const r of records){const a=r.detail;
  if(r.node.op==='reserve_role'||r.node.op==='reserve_formation'||r.node.op==='goal')mark('goal-'+r.node.id,a.goal,r.node.op==='reserve_role'?`支援 ${a.slot}`:'本分支目标',r.node.op==='reserve_role'?`Support ${a.slot}`:'Branch goal','goal');
  if(r.node.op==='enemy_policy'){mark('policy-goal',a.goal,'策略目标','Policy goal','goal');fact(`策略：${a.state} · ${a.reason}`,`Policy: ${a.state} · ${a.reason}`)}
  if(r.node.op==='enemy_policy'&&a.report){mark('squad-report',a.report.position,'小队冻结通报','Frozen squad report','origin');fact(`分区 ${a.sector+1} · ${a.report.victim} ${a.report.kind} · 通报不会授予实时开火权限。`,`Sector ${a.sector+1} · ${a.report.victim} ${a.report.kind} · reports do not grant live fire permission.`)}
  if(r.node.op==='fire'){mark('shot-origin',a.origin,'射击起点','Shot origin','origin');mark('shot-target',a.target_position,'记录的着弹点','Recorded impact','observation');fact(a.fired?`已射击 ${a.target} · 伤害 ${a.damage_applied} · 剩余生命 ${a.health_after}。`:`未射击：${fireReason(a.reason)}。`,a.fired?`Fired at ${a.target} · damage ${a.damage_applied} · health after ${a.health_after}.`:`Withheld: ${fireReason(a.reason,true)}.`)}
  if(r.node.op==='project_search'){mark('requested-search',a.requested_offset,'原始搜索偏移','Requested search offset','desired');mark('projected-search',a.projected,'接纳搜索点','Admitted search point','goal');fact(`最多 ${a.candidate_limit} 个局部候选；${a.projected?'接纳投影':'无完整候选，跳过该偏移'}。`,`At most ${a.candidate_limit} local candidates; ${a.projected?'projection admitted':'no complete candidate; skip this offset'}.`)}
  if(r.node.op==='move'){
   mark('requested-move',a.requested_goal,'本次移动请求','Requested move goal','desired');mark('actual-move',a.goal,'实际路径目标','Actual path goal','goal');
   fact(`移动 ${a.result} · 请求 ${a.requests} · 重试 ${a.retries} · 判定时距目标 ${num(a.arrival_error)} m。`,`Move ${a.result} · requests ${a.requests} · retries ${a.retries} · goal error at evaluation ${num(a.arrival_error)} m.`);
   if(same(a.goal,frame.moves[actorId]?.goal))result.path=frame.moves[actorId]?.path?.filter(point)||[];
   if(op==='move')result.reason=t(`${a.result}：只有移动动作 Success 才表示本次实际到达；空心请求位可能与保留的路径目标不同。`,`${a.result}: only Move Success claims arrival in this tick; the hollow request may differ from the retained path goal.`);
  }
 }
 const observation=d.observation||(op==='contact'?board.squad_observation:['visible','grace','memory','enemy_policy'].includes(op||'')?board.observation:null);
 if(observation){mark('observation',observation.position,'记录的观察点','Recorded observation','observation');fact(`观察 ${observation.actor_id} @ ${num(observation.at)} s · ${observation.sense}。`,`Observation ${observation.actor_id} @ ${num(observation.at)} s · ${observation.sense}.`)}
 const searchScope=(node.id==='search'||node.id.startsWith('search.')||records.some(r=>r.node.op==='enemy_policy'&&r.detail.state==='Search'));
 if(searchScope&&point(board.search_origin)){
  mark('search-origin',board.search_origin,'固定搜索原点','Frozen search origin','origin');
  const recordedOffset=trace.nodes['search.project'];
  const points=(search?.active&&search.steps.length?search.steps.map(s=>s.requested):frame.minds[actorId]?.search_points||(recordedOffset?.status==='Success'?[recordedOffset.detail.requested_offset]:[])).filter(point) as MapPoint[];
  if(board.state==='Search'){points.forEach((p,i)=>mark('search-'+i,p,`记录偏移 ${i+1}`,`Recorded offset ${i+1}`,'candidate'));const radius=Math.max(0,...points.map(p=>Math.hypot(p[0]-board.search_origin[0],p[1]-board.search_origin[1])));if(radius)result.area={centre:board.search_origin,radius,label:t('本次记录偏移的范围示意 · 不代表全区可通行','Envelope of the recorded offset · not a reachability claim')};fact('仅标出本次日志中的搜索偏移；没有假定未来搜索点。','Only offsets present in this tick are shown; future search points are not assumed.');}
  fact(`搜索开始 ${num(board.search_started)} s · 截止 ${num(board.search_deadline)} s · 当前判定 ${num(trace.at)} s。`,`Search start ${num(board.search_started)} s · deadline ${num(board.search_deadline)} s · tick ${num(trace.at)} s.`);
 }
 if(op==='guard_hold')mark('home',board.home,'守卫锚点','Guard anchor','goal');
 if(!result.marks.length)fact('此节点本次没有可标记的空间目标。','This node has no recorded spatial target in this tick.');
 return result;
}
