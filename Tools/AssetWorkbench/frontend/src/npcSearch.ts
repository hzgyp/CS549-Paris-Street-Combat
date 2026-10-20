import type {TreeTrace} from './NpcBehaviorTree';

type Point=[number,number];
export type SearchFrame={at:number;revision:number;minds:Record<string,any>;moves:Record<string,any>;behavior_trees:Record<string,TreeTrace>};
export type SearchStep={order:number;requested:Point;admitted?:Point;firstAt:number;lastAt:number;limit:number;status:'moving'|'arrived'|'skipped'|'advanced'|'blocked';movement:string};
export type SearchEvidence={actorId:string;at:number;treeAt:number;state:string;phase:'idle'|'visible'|'grace'|'investigate'|'search'|'ended'|'blocked';active:boolean;origin?:Point;observation?:{actor_id:string;position:Point;at:number;sense:string};started?:number;deadline?:number;remaining?:number;steps:SearchStep[];currentOrder?:number;index?:number;branch:string[];reason:string;partial:boolean;nodeId?:string};
const point=(p:any):p is Point=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite);
const same=(a:any,b:any)=>point(a)&&point(b)&&Math.hypot(a[0]-b[0],a[1]-b[1])<1e-6;
const copy=(p:Point):Point=>[p[0],p[1]];
const observed=(o:any)=>o&&point(o.position)&&Number.isFinite(o.at)?{actor_id:String(o.actor_id),position:copy(o.position),at:o.at,sense:String(o.sense)}:undefined;

/** Read-only projection of a history PREFIX. No future coordinates, AI or path queries. */
export function searchEvidence(frame:SearchFrame|undefined,history:SearchFrame[],actorId:string):SearchEvidence|undefined{
 const trace=frame?.behavior_trees[actorId];if(!frame||trace?.definition!=='german')return;
 const b=trace.blackboard,generation=frame.minds[actorId]?.generation;
 const rows=history.filter(f=>f.at<=frame.at&&f.revision<=frame.revision&&f.minds[actorId]?.generation===generation&&f.behavior_trees[actorId]?.definition==='german');
 if(rows.at(-1)!==frame)rows.push(frame);
 const seeds=rows.filter(f=>{const v=f.behavior_trees[actorId].blackboard;return point(v.search_origin)&&v.search_started>=0&&v.search_deadline>=0});
 const seed=seeds.at(-1)?.behavior_trees[actorId].blackboard;
 const currentEpisode=point(b.search_origin)&&b.search_started>=0;
 const origin=currentEpisode?b.search_origin:seed?.search_origin,started=currentEpisode?b.search_started:seed?.search_started;
 const active=point(b.search_origin)&&b.search_deadline>=0&&!b.live_visible;
 const grace=trace.nodes['grace.check']?.status==='Success';
 const phase:SearchEvidence['phase']=b.live_visible?'visible':grace?'grace':active?(b.state==='Investigate'?'investigate':b.state==='Search'?'search':'blocked'):seed?'ended':'idle';
 const result:SearchEvidence={actorId,at:frame.at,treeAt:trace.at,state:b.state,phase,active,
  observation:observed(b.observation),steps:[],branch:trace.visited.filter(id=>/^(squad|grace|memory|search|travel|return|sight|engage|budget)(\.|$)/.test(id)),
  reason:frame.minds[actorId]?.reason||'',partial:false,index:b.search_index};
 if(active){result.deadline=b.search_deadline;result.remaining=Math.max(0,b.search_deadline-frame.at)}
 // A new grace/visible observation must not inherit an older episode's route.
 if(!point(origin)||started<0||phase==='grace'||phase==='idle'||(phase==='visible'&&!seed))return result;
 result.origin=copy(origin);result.started=started;
 const episode=rows.filter(f=>{const v=f.behavior_trees[actorId].blackboard;return v.search_started===started&&same(v.search_origin,origin)});
 const first=episode[0];result.partial=!!first&&first.behavior_trees[actorId].at>started+1e-6;
 result.observation=observed(episode.find(f=>same(f.behavior_trees[actorId].blackboard.observation?.position,origin))?.behavior_trees[actorId].blackboard.observation)||result.observation;
 for(const f of episode){
  const tr=f.behavior_trees[actorId],p=tr.nodes['search.project'];if(p?.status!=='Success'||!point(p.detail.requested_offset))continue;
  const d=p.detail;let step=result.steps.find(s=>same(s.requested,d.requested_offset));
  if(!step){const prior=result.steps.at(-1);if(prior?.status==='moving'||prior?.status==='blocked')prior.status='advanced';
   step={order:result.steps.length+1,requested:copy(d.requested_offset),firstAt:tr.at,lastAt:tr.at,limit:d.candidate_limit,status:'moving',movement:''};result.steps.push(step)}
  step.lastAt=tr.at;step.limit=d.candidate_limit;
  if(!point(d.projected)){step.admitted=undefined;step.status='skipped';step.movement='no complete bounded candidate';continue}
  step.admitted=copy(d.projected);
  const move=f.moves[actorId],action=tr.nodes['search.move'];step.movement=move?.result||'';
  const arrived=action?.status==='Success'&&same(action.detail.goal,d.projected)||move?.result==='Arrived'&&same(move.goal,d.projected);
  if(arrived)step.status='arrived';
  else if(step.status!=='arrived')step.status=action?.status==='Failure'||['Unreachable','Stalled','BudgetExceeded','WaitingBudgetExhausted'].includes(move?.result)?'blocked':'moving';
 }
 const current=trace.nodes['search.project'];
 if(active&&current?.status==='Success')result.currentOrder=result.steps.find(s=>same(s.requested,current.detail.requested_offset))?.order;
 return result;
}

export function searchPhase(e:SearchEvidence,english=false){
 const labels={idle:['尚无搜索记录','No search recorded'],visible:['获得敌方视线','Hostile sight acquired'],grace:['视线丢失 · 宽限确认','Sight lost · grace'],investigate:['调查最后观察点','Investigate frozen observation'],search:['按记录顺序搜索','Search recorded offsets'],ended:['搜索已结束','Search ended'],blocked:['搜索移动受限','Search movement limited']};
 return labels[e.phase][english?1:0];
}
export function searchStepStatus(s:SearchStep,english=false){
 return {moving:['当前移动','Moving'],arrived:['已记录到达','Recorded arrival'],skipped:['跳过：无完整候选','Skipped: no complete candidate'],advanced:['已推进；未记录到达','Advanced; no recorded arrival'],blocked:['移动受限','Movement limited']}[s.status][english?1:0];
}
export function searchExplanation(e:SearchEvidence,english=false){
 const t=(zh:string,en:string)=>english?en:zh;
 if(e.phase==='visible')return t('实时视线分支优先；停止沿旧搜索轨迹追踪。此时看见的目标可能是其他盟军。','Live sight takes priority over the old search route; the visible hostile may be another ally.');
 if(e.phase==='grace')return t('先等待丢失视线宽限结束，保留私人观察；此刻搜索分支尚未执行。','Wait for sight-loss grace while retaining private observation; the search branch has not run yet.');
 if(e.phase==='investigate')return t('前往冻结观察点或通报分配的接近位置；每人使用不同接近方向。到达后搜索周边偏移点；没有完整接近路径时也可尝试有限周边点，转入搜索本身不等于到达。','Approach the frozen observation or assigned report sector, using separated approaches. Arrival permits offset search; a missing complete approach also permits bounded nearby candidates. Entering Search alone does not prove arrival.');
 if(e.phase==='search')return t('围绕冻结原点依次请求偏移点，再检查有限净空与完整路径候选。空心点是请求，实心点是接纳位置；无完整候选则跳过。','Request offsets around the frozen origin, then check bounded clearance and complete-path candidates. Hollow points are requests, solid points admitted goals; no complete candidate means skip.');
 if(e.phase==='blocked')return t('搜索期限仍在推进，但当前树/移动记录限制继续移动；不会自动重置规划预算。','The search deadline continues, but tree/movement evidence limits travel; the planning budget is not automatically reset.');
 if(e.phase==='ended')return t('此轮已停止，保留的编号是历史记录，不是当前移动指令。到期或有限点用尽后返回锚点；具体状态以本次树记录为准。','This episode stopped. Retained numbers are history, not current orders. Deadline or finite-point exhaustion returns to the anchor; use the current tree state for the result.');
 return t('尚无本成员的搜索轨迹；先让其获得观察，再丢失视线。','No search trail for this actor; acquire an observation, then lose sight.');
}

/** Dashed order connections are a schematic, never a route or reachability claim. */
export function drawSearch(ctx:CanvasRenderingContext2D,e:SearchEvidence,project:(p:Point)=>Point,english=false){
 ctx.save();const colour=e.active?'#873fad':'#756a80';ctx.strokeStyle=colour;ctx.fillStyle=colour;ctx.font='bold 11px system-ui';
 if(e.origin&&e.steps.length){ctx.lineWidth=1.5;ctx.setLineDash([2,6]);ctx.beginPath();[e.origin,...e.steps.map(s=>s.requested)].forEach((p,i)=>{const q=project(p);i?ctx.lineTo(...q):ctx.moveTo(...q)});ctx.stroke();ctx.setLineDash([])}
 if(e.observation){const p=project(e.observation.position);ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(p[0]-9,p[1]);ctx.lineTo(p[0]+9,p[1]);ctx.moveTo(p[0],p[1]-9);ctx.lineTo(p[0],p[1]+9);ctx.stroke();
  const label=(e.observation.sense==='sight'?(english?'Last seen ':'最后目击 '):e.observation.sense==='report'?(english?'Squad report ':'小队通报 '):(english?'Heard event ':'听觉事件 '))+e.observation.actor_id+' @ '+e.observation.at.toFixed(1)+' s';
  ctx.fillStyle='rgba(255,255,250,.95)';ctx.fillRect(p[0]+12,p[1]+9,ctx.measureText(label).width+8,17);ctx.fillStyle=colour;ctx.fillText(label,p[0]+16,p[1]+21)}
 if(e.origin){const p=project(e.origin);ctx.beginPath();ctx.arc(...p,14,0,Math.PI*2);ctx.stroke()}
 for(const step of e.steps){const p=project(step.requested),selected=e.active&&e.currentOrder===step.order;
  ctx.strokeStyle=step.status==='skipped'?'#b12d41':colour;ctx.lineWidth=selected?3:1.5;ctx.beginPath();ctx.moveTo(p[0],p[1]-9);ctx.lineTo(p[0]+9,p[1]);ctx.lineTo(p[0],p[1]+9);ctx.lineTo(p[0]-9,p[1]);ctx.closePath();ctx.stroke();
  if(step.admitted){const q=project(step.admitted);ctx.strokeStyle='#007d7a';ctx.fillStyle='#007d7a';if(!same(step.requested,step.admitted)){ctx.setLineDash([3,3]);ctx.beginPath();ctx.moveTo(...p);ctx.lineTo(...q);ctx.stroke();ctx.setLineDash([])}ctx.beginPath();ctx.arc(...q,selected?6:3,0,Math.PI*2);ctx.fill()}
  if(selected){ctx.strokeStyle='#007d7a';ctx.beginPath();ctx.arc(...p,18,0,Math.PI*2);ctx.stroke()}
  const label='S'+step.order+(step.status==='arrived'?' ✓':step.status==='skipped'?' ×':'');ctx.fillStyle='rgba(255,255,250,.96)';ctx.fillRect(p[0]-13,p[1]-30,ctx.measureText(label).width+8,16);ctx.fillStyle=colour;ctx.fillText(label,p[0]-9,p[1]-18);
 }
 ctx.restore();
}
