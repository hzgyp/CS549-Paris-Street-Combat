import React,{useState} from 'react';
import {searchPhase,searchStepStatus,searchExplanation,type SearchEvidence} from './npcSearch';

export function NpcSearchPanel({evidence,english,onFocus}:{evidence?:SearchEvidence;english:boolean;onFocus:()=>void}){
 const [collapsed,setCollapsed]=useState(false),t=(zh:string,en:string)=>english?en:zh,e=evidence;
 if(!e)return null;
 const xy=(p:number[])=>p.map(v=>v.toFixed(2)).join(', ');
 return <aside id="npc-search" className={'npc-search'+(collapsed?' is-collapsed':'')} data-phase={e.phase} data-actor={e.actorId} data-at={e.at} data-tree-at={e.treeAt} onPointerDown={event=>event.stopPropagation()}>
  <header><strong>{e.actorId} · {searchPhase(e,english)}</strong><span id="npc-search-remaining">{e.remaining===undefined?t('计时未运行','Timer inactive'):t('剩余 ','Remaining ')+e.remaining.toFixed(1)+' s'}</span><button id="npc-search-collapse" onClick={()=>setCollapsed(!collapsed)} aria-expanded={!collapsed}>{collapsed?'+':'−'}</button></header>
  {!collapsed&&<><p id="npc-search-observation">{e.observation?(e.observation.sense==='sight'?t('最后目击 ','Last seen '):e.observation.sense==='report'?t('小队通报 ','Squad report '):t('听觉事件 ','Heard event '))+e.observation.actor_id+' @ '+e.observation.at.toFixed(1)+' s · '+xy(e.observation.position)+' m':t('没有私人观察','No private observation')}</p>
   <div id="npc-search-order">{e.origin&&<span>{t('原点 0','Origin 0')}</span>}{e.steps.map(s=><span key={s.order} data-order={s.order} data-status={s.status} className={s.order===e.currentOrder?'is-current':''} title={searchStepStatus(s,english)}>{' → S'+s.order}{s.status==='arrived'?' ✓':s.status==='skipped'?' ×':s.order===e.currentOrder?' ●':''}</span>)}{!e.steps.length&&<span>{t('偏移点尚未执行','No offset evaluated yet')}</span>}</div>
   <details id="npc-search-details"><summary>{t('为什么去这里 / 点位明细','Why here / point details')}</summary><p>{searchExplanation(e,english)}</p><p>{t('状态','State')}: {e.state} · {t('树判定','Tree tick')} {e.treeAt.toFixed(1)} s · {t('当前帧','Frame')} {e.at.toFixed(1)} s</p>
    {e.origin&&<p>{t('冻结原点','Frozen origin')}: {xy(e.origin)} m · {t('开始','Started')} {e.started?.toFixed(1)} s{e.deadline!==undefined?' · '+t('截止','Deadline')+' '+e.deadline.toFixed(1)+' s':''}</p>}
    <ol>{e.steps.map(s=><li key={s.order}><strong>S{s.order} · {searchStepStatus(s,english)}</strong><br/>{t('请求','Requested')} ({xy(s.requested)}) → {s.admitted?t('接纳','Admitted')+' ('+xy(s.admitted)+') m':t('无接纳位置','No admitted point')}<br/>{t('首次执行','First evaluated')} {s.firstAt.toFixed(1)} s · {t('候选上限','Candidate limit')} {s.limit} · {s.movement}</li>)}</ol>
    <p>{t('编号只含本帧之前实际执行的偏移点，后续点尚未生成。紫色虚线仅表示先后顺序，实际路径另绘；索引推进不等于身体到达。','Numbers include only offsets evaluated up to this frame; future points are not generated. Purple dashes show order, not travel paths. Advancing an index does not prove arrival.')}</p>
    {e.partial&&<p>{t('早期历史已不在保留窗口，当前顺序可能不完整。','Earlier history is outside the retained window; this sequence may be incomplete.')}</p>}
    <p>{t('树分支','Tree branch')}: {e.branch.join(' → ')}</p><button id="npc-search-focus" disabled={!e.origin&&!e.observation} onClick={onFocus}>{t('定位搜索记录','Focus search evidence')}</button>
   </details></>}
 </aside>;
}
