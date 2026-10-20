import React,{useState} from 'react';
import type {NodeEvidence} from './npcNodeMap';
import {sightReason} from './npcSight';
import {searchExplanation,searchPhase} from './npcSearch';

export function NpcNodeEvidence({evidence,english,onFocus}:{evidence?:NodeEvidence;english:boolean;onFocus:()=>void}){
 const [collapsed,setCollapsed]=useState(false),t=(zh:string,en:string)=>english?en:zh;
 if(!evidence)return null;
 const e=evidence,status:Record<string,string>=english?{Success:'Passed / completed',Failure:'Failed',Running:'Running',Skipped:'Not evaluated'}:{Success:'通过 / 完成',Failure:'失败',Running:'运行中',Skipped:'未执行'};
 const searchNode=!!e.search&&/^(memory|grace|search|travel|return)(\.|$)/.test(e.nodeId);
 return <aside className={'npc-node-evidence'+(collapsed?' is-collapsed':'')} id="npc-node-evidence" data-node-id={e.nodeId} data-status={e.status} data-actor={e.actorId} data-tick-at={e.at} aria-label={t('节点与地图判定依据','Node and map evidence')}>
  <header><strong title={`${e.actorId} · ${e.title}`}>{e.actorId} · {e.title}</strong><button id="npc-node-collapse" aria-expanded={!collapsed} onClick={()=>setCollapsed(!collapsed)}>{collapsed?t('展开','Show'):t('收起','Hide')}</button></header>
  {!collapsed&&<><div className="npc-node-meta"><span className={'bt-'+e.status.toLowerCase()}>{status[e.status]}</span><span>{t('判定','Tick')} {e.at.toFixed(1)} s</span><button id="npc-node-focus-map" disabled={!e.marks.length&&!e.vision} onClick={onFocus}>{e.vision?t('定位视线 / 目标','Focus sight / targets'):t('定位目标','Focus targets')}</button></div>
  {searchNode&&<div id="npc-search-node" data-phase={e.search!.phase} data-at={e.search!.at}><strong>{searchPhase(e.search!,english)} · {e.search!.remaining===undefined?t('计时未运行','Timer inactive'):t('剩余 ','Remaining ')+e.search!.remaining.toFixed(1)+' s'}</strong><p>{e.status==='Skipped'?t('当前节点未执行；搜索记录仅供上下文对照。','This node was not evaluated; search evidence is context only.'):searchExplanation(e.search!,english)}</p></div>}
  {e.vision&&<div id="npc-sight-evidence" data-failure={e.vision.failure||'None'} data-sense-at={e.vision.at}>
   <p id="npc-sight-reason">{sightReason(e.vision,english)}</p><div className="npc-sight-gates">{(['distance','angle','occlusion'] as const).map((key,i)=><span key={key} className={'bt-'+e.vision!.gates[key].toLowerCase()} data-gate={key} data-status={e.vision!.gates[key]} title={key==='distance'?`${e.vision!.distance_m.toFixed(3)} / ${e.vision!.range_m} m`:key==='angle'?`${e.vision!.angle_degrees.toFixed(3)} / ${e.vision!.half_fov_degrees}°`:t('通过前两项后才检查遮挡','Occlusion runs only after distance and angle pass')}>{t(['距离','角度','遮挡'][i],['Distance','Angle','Occlusion'][i])} {e.vision!.gates[key]==='Success'?'✓':e.vision!.gates[key]==='Failure'?'×':'—'}</span>)}<small>{t('感知','Sense')} {e.vision.at.toFixed(1)} s{e.status==='Skipped'?t(' · 节点未执行',' · node skipped'):''}</small></div>
  </div>}
  <p id="npc-node-reason">{e.reason}</p><details id="npc-node-facts"><summary>{t('判定依据与图例','Evidence and legend')} ({e.facts.length})</summary><p>{t('◇ 橙色：原始请求　● 青色：接纳目标　× 红色：拒绝候选　紫色：观察 / 搜索。视线：绿实线可见、橙虚线未进入遮挡检查、红点为首个遮挡，红点后虚线为参考。范围示意不表示全区可通行。','◇ Orange: desired/requested · ● Teal: admitted goal · × Red: rejected candidate · Purple: observation/search. Sight: green clear, amber dashed untested occlusion, red first hit with a dashed reference beyond. Envelopes do not imply reachability.')}</p><ul>{e.facts.map((fact,i)=><li key={i}>{fact}</li>)}</ul><p>{t('依据此节点的决策时刻；播放中的人物使用平滑插值，条件成功不等于身体已到达。','Evidence belongs to this node’s decision tick; moving actors are interpolated. A passed condition does not mean physical arrival.')}</p></details></>}
 </aside>;
}
