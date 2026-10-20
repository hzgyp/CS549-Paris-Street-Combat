import React,{memo,useEffect,useMemo,useRef,useState} from 'react';
import {createPortal} from 'react-dom';
import {useTreeWindow} from './useTreeWindow';
import {useLocale} from './i18n';
import {NpcParameters,type Parameters,type ParameterField} from './NpcParameters';
import {NpcNodeEvidence} from './NpcNodeEvidence';
import type {NodeEvidence} from './npcNodeMap';
import './npc-behavior-tree.css';

export type TreeNode={id:string;kind:string;op?:string;label:[string,string];description:[string,string];children:string[];parameters?:string[]};
export type TreeDefinition={id:string;root:string;nodes:TreeNode[];decision_interval:number;max_node_visits:number};
export type TreeTrace={definition:string;at:number;status:string;visited:string[];nodes:Record<string,{status:string;detail:Record<string,any>}>;blackboard:Record<string,any>};
const statusLabels:Record<string,[string,string]>={Success:['成功','Success'],Failure:['失败','Failure'],Running:['运行中','Running'],Skipped:['未执行','Skipped']};
const kinds:Record<string,[string,string]>={Selector:['选择器 · 按优先级','Selector · priority'],Sequence:['序列 · 依次执行','Sequence · in order'],Condition:['条件','Condition'],Action:['动作','Action'],ForceSuccess:['修饰器 · 保留意图','Decorator · keep intent']};
const fields:Record<string,[string,string]>={maneuver:['本成员协同分工','Member maneuver'],holder_ready:['掩护者实际就绪','Holder physically ready'],holder:['掩护成员','Covering member'],mover:['推进成员','Advancing member'],phase:['交替推进阶段','Bound phase'],cover:['障碍物掩体验证','Obstacle cover proof'],last_swap:['实际到达换位记录','Physical arrival swap'],contact:['冻结目击通报','Frozen sight report'],leg:['有限侧翼路径','Bounded flank leg'],squad_report:['小队遇袭通报','Squad hit report'],combat:['射击判定','Fire gates'],health:['生命值','Health'],ammo:['剩余弹药','Ammunition'],report:['冻结的小队通报','Frozen squad report'],permitted:['允许开火','Fire permitted'],target:['观察目标','Observed target'],mode:['行进分工','Movement role'],leash:['玩家活动边界','Player leash'],chase_used:['本轮追击路程','Chase travel'],chase_limit:['追击上限','Chase limit'],player_sight:['玩家视觉采样','Player sight sample'],state:['决策状态','Decision state'],live_visible:['实时看见敌方','Hostile currently visible'],observation:['个人最后观察','Private last observation'],squad_observation:['小队敌情','Squad observation'],player_position:['友军玩家位置','Friendly player position'],home:['守卫锚点','Guard anchor'],search_origin:['固定搜索原点','Frozen search origin'],search_deadline:['搜索期限','Search deadline'],search_index:['搜索点序号','Search index'],move_goal:['实际路径目标','Actual path goal'],move_result:['实际移动结果','Actual movement result'],requests:['路径请求次数','Path requests'],request_limit:['请求上限','Request limit'],retries:['已用重试','Retries used'],reservation:['独立位置占用','Separated reservation'],goal:['本次目标','Goal'],requested_goal:['本次请求目标','Requested goal'],result:['移动结果','Movement result'],limit:['上限','Limit'],assignment:['共同分工位置','Joint assignment'],role:['分工角色','Role'],reason:['决策原因','Decision reason'],elapsed:['状态已持续','Time in state'],dwell:['警戒停留','Alert dwell'],sense:['观察来源','Observation sense'],since_last_sight:['距最后看见','Since last sight'],grace:['视线丢失宽限','Sight-loss grace'],consumed_at:['已消费观察时间','Consumed observation time'],raster:['地图场景','Raster scene'],slot:['占用位置','Reserved slot'],desired_slot:['原始队形位置','Desired formation slot'],requested_offset:['固定搜索偏移','Frozen search offset'],projected:['可用搜索候选','Admitted search candidate'],candidate_limit:['候选上限','Candidate limit'],deadline:['固定期限','Fixed deadline'],arrival_error:['距实际目标','Actual arrival error'],requires_new_order:['等待新指令','New order required'],child_status:['移动子节点结果','Movement child result'],arrival_claim:['代表实际到达','Claims physical arrival']};
const names:Record<string,[string,string]>={Scout:['前出探路','Scout'],Cover:['侧翼掩护','Cover wing'],Dead:['阵亡','Casualty'],Guard:['守卫','Guard'],Alert:['警戒','Alert'],Engage:['交战意图','Engage'],Investigate:['调查观察点','Investigate'],Search:['有限搜索','Search'],Return:['返回锚点','Return'],Follow:['跟随','Follow'],Regroup:['归队','Regroup'],Support:['支援','Support'],Overwatch:['掩护','Overwatch'],Waiting:['等待','Waiting'],Moving:['移动中','Moving'],Arrived:['实际到达','Arrived'],Idle:['驻停','Idle'],Unreachable:['不可达','Unreachable'],BudgetExceeded:['路径预算耗尽','Path budget exceeded'],WaitingBudgetExhausted:['等待 · 规划耗尽','Waiting · planning exhausted'],Stalled:['移动停滞','Stalled']};

export const NpcBehaviorTree=memo(function NpcBehaviorTree({definition,trace,actorId,frameAt,onSelect,onInspect,nodeEvidence,onFocusMap,parameterSchema,parameters,parametersLocked,review,onApply}:{definition?:TreeDefinition;trace?:TreeTrace;actorId:string;frameAt:number;onSelect:(id:string)=>void;onInspect:(id:string)=>void;nodeEvidence?:NodeEvidence;onFocusMap:()=>void;parameterSchema:ParameterField[];parameters:Parameters;parametersLocked:boolean;review:boolean;onApply:(v:Parameters)=>Promise<void>}){
 const {locale}=useLocale(),l=locale==='en'?1:0,t=(zh:string,en:string)=>l?en:zh;
 const [picked,setPicked]=useState('root'),[full,setFull]=useState(false),[following,setFollowing]=useState(true);
 const diagram=useMemo(()=>{
  if(!definition)return null;
  const byId=Object.fromEntries(definition.nodes.map(n=>[n.id,n])),positions:Record<string,{x:number;y:number;collapsed:number}>={},edges:{parent:string;child:string}[]=[];let row=0,maxDepth=0;
  function descendants(id:string):number{return byId[id].children.reduce((sum,c)=>sum+1+descendants(c),0)}
  function place(id:string,depth:number):number{
   const n=byId[id],collapsed=!full&&trace?.nodes[id]?.status==='Skipped'&&n.children.length>0;
   const ys=collapsed?[]:n.children.map(child=>{edges.push({parent:id,child});return place(child,depth+1)});
   const y=ys.length?(ys[0]+ys[ys.length-1])/2:36+row++*90;
   positions[id]={x:24+depth*254,y,collapsed:collapsed?descendants(id):0};maxDepth=Math.max(maxDepth,depth);return y;
  }
  place(definition.root,0);return {byId,positions,edges,width:48+maxDepth*254+226,height:Math.max(160,row*90+10)};
 },[definition,trace,full]);
 const window=useTreeWindow(diagram?.width||1,diagram?.height||1),{viewport}=window;
 const wasExpanded=useRef(false),keepInspectionOnReturn=useRef(false);
 useEffect(()=>{if(wasExpanded.current&&!window.expanded){const keep=keepInspectionOnReturn.current;keepInspectionOnReturn.current=false;setFollowing(!keep);window.changeZoom(1);if(keep)requestAnimationFrame(()=>{const p=diagram?.positions[picked],el=viewport.current;if(p&&el)el.scrollTo({left:p.x+113-el.clientWidth/2,top:p.y-el.clientHeight/2,behavior:'instant'})})}wasExpanded.current=window.expanded},[window.expanded]);
 const activeId=trace&&diagram?([...trace.visited].reverse().find(id=>diagram.byId[id]?.kind==='Action'&&trace.nodes[id].status==='Running')||trace.visited.find(id=>diagram.byId[id]?.kind==='Action')||definition!.root):'root';
 useEffect(()=>{setFollowing(true)},[actorId,definition?.id]);
 useEffect(()=>{onInspect(picked)},[picked,actorId,onInspect]);
 useEffect(()=>{
  if(!following||!diagram)return;
  setPicked(activeId);
  const el=viewport.current,p=diagram.positions[activeId];if(!el||!p)return;
  const locate=()=>{const x=p.x*window.zoom,y=(p.y-34)*window.zoom,w=226*window.zoom,h=70*window.zoom;
   if(x<el.scrollLeft+12||x+w>el.scrollLeft+el.clientWidth-20||y<el.scrollTop+12||y+h>el.scrollTop+el.clientHeight-20)
    el.scrollTo({left:x+w/2-el.clientWidth/2,top:y+h/2-el.clientHeight/2,behavior:'instant'});
  };
  locate();const observer=new ResizeObserver(locate);observer.observe(el);return()=>observer.disconnect();
 },[following,activeId,diagram,window.zoom,window.expanded,viewport]);
 if(!definition||!trace||!diagram)return <section className="npc-bt panel"><h2>{t('行为树','Behavior tree')}</h2><p>{t('正在加载决策树…','Loading decision tree…')}</p></section>;
 const node=diagram.byId[picked]||diagram.byId[definition.root],record=trace.nodes[node.id],board=trace.blackboard;
 const status=(s:string)=>statusLabels[s]?.[l]||s;
 function value(v:any):string{
  if(v?.schema==='paris.npc.sight.v1')return `${v.observer} → P · ${v.at.toFixed(1)} s · ${v.visible?t('看见玩家','Player visible'):v.failure}`;
  if(v==null||v===-1)return '—';
  if(typeof v==='boolean')return v?t('是','Yes'):t('否','No');
  if(typeof v==='number')return Number.isInteger(v)?String(v):v.toFixed(2);
  if(typeof v==='string')return names[v]?.[l]||v;
  if(Array.isArray(v))return v.map(value).join(', ')+' m';
  if(v.actor_id)return `${v.actor_id} @ ${value(v.position)} · ${v.at.toFixed(1)} s · ${v.sense==='report'?t('报告','report'):v.sense==='hearing'?t('听觉','hearing'):t('视觉','sight')}`;
  if(v.id&&v.position)return `${v.id} · ${value(v.position)}`;
  return JSON.stringify(v);
 }
 function focusActive(){setFollowing(true);setPicked(activeId);const el=viewport.current,p=diagram!.positions[activeId];if(el&&p)el.scrollTo({left:(p.x+113)*window.zoom-el.clientWidth/2,top:p.y*window.zoom-el.clientHeight/2,behavior:'instant'})}
 function inspect(id:string){setFollowing(false);setPicked(id)}
 const active=diagram.byId[activeId],ancestors=[activeId];let parent=definition.nodes.find(n=>n.children.includes(activeId));while(parent){ancestors.unshift(parent.id);parent=definition.nodes.find(n=>n.children.includes(parent!.id))}
 const parametersForm=<NpcParameters schema={parameterSchema} values={parameters} locked={parametersLocked} review={review} onApply={onApply} bindings={node.parameters}/>;
 const labelLines=(label:string)=>{if(l){const words=label.split(' ');let a='';while(words.length&&a.length+words[0].length<27)a+=(a?' ':'')+words.shift();return [a,words.join(' ')]}return [label.slice(0,15),label.slice(15)]};
 const content=<section ref={window.section} className={'npc-bt panel'+(window.expanded?' npc-bt-expanded':'')} data-actor={actorId} data-tick-at={trace.at} data-tree-state={board.state} role={window.expanded?'dialog':undefined} aria-modal={window.expanded?true:undefined} aria-label={window.expanded?t('行为树查看器','Behavior tree viewer'):undefined}>
  <div className="npc-bt-heading"><div><h2>{t('行为树 · 实时执行','Behavior tree · live execution')}</h2></div><label>{t('观察成员','Observe member')}<select id="npc-tree-agent" value={actorId} onChange={e=>{setPicked('root');onSelect(e.target.value)}}>{['A1','A2','G1','G2','G3'].map(id=><option key={id}>{id}</option>)}</select></label></div>
  <div className="npc-bt-toolbar"><strong>{actorId} · {value(board.state)}</strong><span>{review?t('回访','Review'):t('决策','Tick')} {trace.at.toFixed(1)} s <small>({t('画面','frame')} {frameAt.toFixed(1)} s)</small></span><label><input id="npc-tree-follow" type="checkbox" checked={following} onChange={e=>setFollowing(e.target.checked)}/>{t('跟随执行','Follow execution')}</label><button id="npc-tree-focus" onClick={focusActive}>{t('定位执行节点','Focus executed node')}</button></div>
  {window.expanded&&parametersForm}
  <div className="npc-bt-current" data-active-node={activeId} data-following={following}><span className={'bt-'+trace.nodes[activeId].status.toLowerCase()}>{status(trace.nodes[activeId].status)}</span><strong id="npc-tree-active-label">{active.label[l]}</strong><ol aria-label={t('当前执行分支','Current execution branch')}>{ancestors.map(id=><li key={id}><button onClick={()=>inspect(id)} title={diagram.byId[id].description[l]}>{diagram.byId[id].label[l]}</button></li>)}</ol></div>
  <div className="npc-bt-view-tools" aria-label={t('视图控制','View controls')}>{window.expanded&&<button id="npc-parameters-observe" onClick={()=>window.setExpanded(false)}>{t('回到联动视图','Return to linked view')}</button>}<button id="npc-tree-expand" onClick={()=>window.setExpanded(!window.expanded)}>{window.expanded?t('退出全屏','Exit fullscreen'):t('全屏查看','Fullscreen')}</button><button id="npc-tree-fit" onClick={()=>{setFollowing(false);window.fit()}}>{t('适应窗口','Fit to window')}</button><div className="npc-bt-zoom"><button aria-label={t('缩小行为树','Zoom out tree')} onClick={()=>window.changeZoom(window.zoom/1.2)}>−</button><output aria-label={t('行为树缩放比例','Tree zoom')}>{Math.round(window.zoom*100)}%</output><button aria-label={t('放大行为树','Zoom in tree')} onClick={()=>window.changeZoom(window.zoom*1.2)}>＋</button><button onClick={()=>window.changeZoom(1)}>100%</button></div><label><input id="npc-tree-full" type="checkbox" checked={full} onChange={e=>setFull(e.target.checked)}/>{t('完整树','Full tree')}</label><button id="npc-tree-inspect" aria-pressed={window.inspecting} onClick={()=>window.setInspecting(!window.inspecting)}>{window.inspecting?t('收起详情','Hide details'):t('节点详情','Node details')}</button><small>{t('拖动平移 · Ctrl + 滚轮缩放','Drag to pan · Ctrl + scroll to zoom')}{window.expanded?' · Esc':''}</small></div>
  <div className="npc-bt-legend">{Object.keys(statusLabels).map(s=><span key={s} className={'bt-'+s.toLowerCase()}><i/>{status(s)}</span>)}<small>{trace.visited.length} / {definition.max_node_visits} {t('节点已评估','nodes evaluated')}</small></div>
  <div className={'npc-bt-body'+(!window.inspecting?' npc-bt-no-inspector':'')}><div className={'npc-bt-viewport'+(window.dragging?' is-dragging':'')} ref={viewport} tabIndex={0} aria-label={t('可滚动行为树节点图','Scrollable behavior tree diagram')} {...window.gestures} onPointerDown={e=>{setFollowing(false);window.gestures.onPointerDown(e)}} onWheel={()=>setFollowing(false)} onKeyDown={e=>{if(['ArrowDown','ArrowUp','ArrowLeft','ArrowRight','Home','End','PageDown','PageUp'].includes(e.key))setFollowing(false)}}>
   <svg width={diagram.width*window.zoom} height={diagram.height*window.zoom} viewBox={`0 0 ${diagram.width} ${diagram.height}`} role="group" aria-label={t('带执行状态的行为树','Behavior tree with execution status')}>
    {diagram.edges.map(({parent,child})=>{const a=diagram.positions[parent],b=diagram.positions[child],s=trace.nodes[child].status;return <path key={child} className={'npc-bt-edge bt-'+s.toLowerCase()} d={`M ${a.x+226} ${a.y} C ${a.x+240} ${a.y}, ${b.x-14} ${b.y}, ${b.x} ${b.y}`}/>})}
    {Object.entries(diagram.positions).map(([id,p])=>{const n=diagram.byId[id],s=trace.nodes[id].status,lines=labelLines(n.label[l]);return <g key={id} data-node-id={id} data-status={s} data-current={id===activeId} className={'npc-bt-node bt-'+s.toLowerCase()+(node.id===id?' bt-picked':'')+(id===activeId?' bt-current':'')} transform={`translate(${p.x},${p.y-34})`} role="button" tabIndex={0} aria-label={`${n.label[l]} · ${status(s)}`} onClick={()=>inspect(id)} onKeyDown={e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();inspect(id)}}}><title>{n.description[l]}</title><rect width="226" height="70" rx="7"/><text className="bt-kind" x="10" y="14">{kinds[n.kind]?.[l]}</text><text className="bt-label" x="10" y="33">{lines[0]}</text>{lines[1]&&<text className="bt-label" x="10" y="48">{lines[1]}</text>}<text className="bt-status" x="10" y="62">{status(s)}{p.collapsed?` · ${p.collapsed} ${t('子节点折叠','children folded')}`:''}</text></g>})}
   </svg>
  </div><aside className="npc-bt-inspect" hidden={!window.inspecting}><h3 id="npc-tree-node-title">{node.label[l]}</h3><span className={'npc-bt-result bt-'+record.status.toLowerCase()}>{status(record.status)} · {kinds[node.kind]?.[l]}</span><p>{node.description[l]}</p>{!!node.parameters?.length&&<p className="npc-node-parameters">{t('关联参数','Bound parameters')}: {node.parameters.map(key=>{const f=parameterSchema.find(f=>f.key===key);return `${f?.label[l]||key} = ${parameters[key]} ${f?.unit||''}`}).join(' · ')}</p>}<dl id="npc-tree-node-detail">{Object.entries(record.detail).map(([key,v])=><React.Fragment key={key}><dt>{parameterSchema.find(f=>f.key===key)?.label[l]||fields[key]?.[l]||(key==='search_started'?t('搜索开始时刻','Search started'):key)}</dt><dd>{value(v)}</dd></React.Fragment>)}</dl>{record.status==='Skipped'&&<p>{t('本次没有执行到此节点；更高优先级分支已选中，或前置条件未通过。','This node was not executed: an earlier branch was selected or a preceding condition stopped the sequence.')}</p>}
   <details open><summary>{t('本次决策黑板','Decision blackboard')}</summary><dl id="npc-tree-blackboard">{Object.entries(board).filter(([key,v])=>key!=='request_limit'&&(v!=null&&v!==-1||['live_visible','observation','search_deadline'].includes(key))).map(([key,v])=><React.Fragment key={key}><dt>{parameterSchema.find(f=>f.key===key)?.label[l]||fields[key]?.[l]||(key==='search_started'?t('搜索开始时刻','Search started'):key)}</dt><dd>{key==='requests'?`${v} / ${board.request_limit}`:value(v)}</dd></React.Fragment>)}</dl></details>
  </aside></div>
  <NpcNodeEvidence evidence={nodeEvidence} english={!!l} onFocus={()=>{if(window.expanded){keepInspectionOnReturn.current=true;setFollowing(false);window.setExpanded(false)}onFocusMap()}}/>
  {!nodeEvidence&&<p className="npc-bt-footnote">{t('蓝色为持续执行；绿色表示该节点完成判定。只有“移动”动作显示成功才表示实际到达。“保留意图”不会把路径失败变成到达。时间轴回访显示当时的树与黑板。','Blue means ongoing execution; green means that node completed its evaluation. Only a successful Move action claims actual arrival. Keep intent never turns a failed path into arrival. Timeline review shows the recorded tree and blackboard.')}</p>}
 </section>;
 return window.expanded?createPortal(content,document.body):<>{parametersForm}{content}</>;
});
