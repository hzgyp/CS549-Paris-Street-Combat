import React,{useState} from 'react';
type Point=[number,number];
import {fireReason} from './npcCombat';
import {maneuverAt} from './npcManeuver';
export function NpcTacticsControls({frame,locked,english,onFire}:{frame:any;locked:boolean;english:boolean;onFire:(id:string)=>void}){
 const [target,setTarget]=useState('G1'),t=(zh:string,en:string)=>english?en:zh,check=frame.combat?.checks.P;
 return <div className="npc-tactics-controls"><label>{t('玩家射击目标','Player target')}<select id="npc-fire-target" value={target} disabled={locked} onChange={e=>setTarget(e.target.value)}>{['G1','G2','G3'].map(id=><option key={id} value={id} disabled={!frame.actors[id].alive}>{id} · {frame.actors[id].health} HP</option>)}</select></label><button id="npc-fire" disabled={locked||!frame.actors.P.alive||!frame.actors[target].alive} onClick={()=>onFire(target)}>{t('玩家射击','Player fire')}</button><small id="npc-combat-status">{t('每发','Per shot')} {frame.parameters.combat_damage} HP · {t('冷却','cooldown')} 1.5 s · P {frame.actors.P.ammo}/30 {t('发','rounds')}{check?' · '+fireReason(check.reason,english):''}</small></div>;
}
/** Draw only frozen server evidence at/before the displayed pose time. */
export function drawTactics(ctx:CanvasRenderingContext2D,frame:any,actorId:string,at:number,project:(p:Point)=>Point,english=false){
 const maneuver=maneuverAt(frame,actorId,at),cover=maneuver?.cover;
 if(cover){
  const hide=project(cover.hide),peek=project(cover.peek),block=project(cover.blocker.point);
  ctx.lineWidth=2;ctx.strokeStyle='#6c3b9b';ctx.setLineDash([4,3]);ctx.beginPath();ctx.moveTo(...hide);ctx.lineTo(...peek);ctx.stroke();ctx.setLineDash([]);
  ctx.strokeStyle='#ac3350';ctx.beginPath();ctx.moveTo(...hide);ctx.lineTo(...block);ctx.stroke();
  for(const [p,label,colour] of [[hide,english?'HIDE':'藏身','#6c3b9b'],[peek,english?'PEEK':'探出','#087f9e'],[block,english?'BLOCK':'遮挡','#b42642']] as [Point,string,string][]){ctx.fillStyle=colour;ctx.fillRect(p[0]-4,p[1]-4,8,8);ctx.font='bold 11px system-ui';const width=ctx.measureText(label).width;ctx.fillStyle='#fff';ctx.fillRect(p[0]+5,p[1]-14,width+6,15);ctx.fillStyle=colour;ctx.fillText(label,p[0]+8,p[1]-3)}
 }
 if(maneuver?.goal&&maneuver.contact){const a=project(frame.actors[actorId].position),b=project(maneuver.goal);ctx.strokeStyle='#b35025';ctx.setLineDash([3,5]);ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.stroke();ctx.setLineDash([]);ctx.strokeRect(b[0]-6,b[1]-6,12,12)}
 const notice=frame.behavior_trees[actorId]?.blackboard.squad_report;
 if(notice&&notice.at<=at&&at-notice.at<8){
  const p=project(notice.position);ctx.strokeStyle='#a12978';ctx.lineWidth=2;ctx.setLineDash([4,4]);ctx.beginPath();ctx.arc(...p,18,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);
  const label=notice.victim+(notice.kind==='casualty'?(english?' casualty report':' 阵亡通报'):(english?' hit report':' 遇袭通报'));
  ctx.font='bold 11px system-ui';ctx.fillStyle='#fff5fc';ctx.fillRect(p[0]+20,p[1]-8,ctx.measureText(label).width+8,18);ctx.fillStyle='#8a1d67';ctx.fillText(label,p[0]+24,p[1]+5);
 }
 for(const shot of frame.combat?.shots||[]){
  if(shot.at>at||at-shot.at>.65)continue;
  const a=project(shot.origin),b=project(shot.target_position);ctx.strokeStyle=shot.shooter.startsWith('G')?'#dc6737':'#219ac2';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.stroke();ctx.fillStyle=ctx.strokeStyle;ctx.beginPath();ctx.arc(...b,5,0,2*Math.PI);ctx.fill();ctx.font='bold 12px system-ui';ctx.fillText('-'+shot.damage_applied+' HP',b[0]+8,b[1]+26);
 }
}
