import type {MapPoint} from './npcNodeMap';

export type SightEvidence={schema:'paris.npc.sight.v1';at:number;observer:string;target:string;origin:MapPoint;heading:number;target_position:MapPoint;distance_m:number;range_m:number;angle_degrees:number;half_fov_degrees:number;fov_degrees:number;visible:boolean;failure:null|'Distance'|'Angle'|'Occlusion';gates:Record<'distance'|'angle'|'occlusion','Success'|'Failure'|'Skipped'>;visible_hostiles:string[];map_sha256:string|null;ray:null|{blocked:boolean;point:MapPoint|null;cell:MapPoint|null;cell_size_m?:number;reason:string|null;checked_cells?:number}};
// Formats recorded predicates. Never recomputes a gate from rounded display values.
export function sightReason(s:SightEvidence,english=false){
 const n=(v:number)=>v.toFixed(2);
 if(s.visible)return english?'Player visible: distance, angle and occlusion passed.':'看见玩家：距离、角度和遮挡检查均通过。';
 if(s.failure==='Distance')return english?`Player not seen: ${n(s.distance_m)} m exceeds ${n(s.range_m)} m.`:`没看见玩家：距离 ${n(s.distance_m)} m 超出 ${n(s.range_m)} m。`;
 if(s.failure==='Angle')return english?`Player not seen: off-axis ${n(s.angle_degrees)}° exceeds half-FOV ${n(s.half_fov_degrees)}°.`:`没看见玩家：偏角 ${n(s.angle_degrees)}° 超出半视角 ${n(s.half_fov_degrees)}°。`;
 if(s.ray?.point)return english?'Player not seen: the sight ray hits a blocked cell.':'没看见玩家：视线被黑色栅格阻挡，红点为首个遮挡点。';
 return english?'Player not seen: ray rejected; no confirmed hit point.':'没看见玩家：射线检查拒绝，未记录确定的遮挡点。';
}

/** Draw only the sampled evidence. Actor animation is deliberately not an input. */
export function drawSight(ctx:CanvasRenderingContext2D,s:SightEvidence,project:(p:MapPoint)=>MapPoint,scale:number,english:boolean){
 const a=project(s.origin),b=project(s.target_position),hit=s.ray?.point?project(s.ray.point):null;
 const colour=s.visible?'#087d61':s.failure==='Occlusion'?'#ba243b':'#a36200';
 ctx.save();ctx.lineWidth=3;ctx.strokeStyle=colour;ctx.setLineDash(s.ray?[]:[8,5]);ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...(hit||b));ctx.stroke();
 if(hit){ctx.globalAlpha=.65;ctx.setLineDash([5,5]);ctx.beginPath();ctx.moveTo(...hit);ctx.lineTo(...b);ctx.stroke();ctx.globalAlpha=1;ctx.setLineDash([]);if(s.ray?.cell){const size=s.ray.cell_size_m||.25,p=project([s.ray.cell[0]*size,s.ray.cell[1]*size]);ctx.fillStyle='#ba243b55';ctx.fillRect(...p,size*scale,size*scale);ctx.strokeRect(...p,Math.max(2,size*scale),Math.max(2,size*scale))}ctx.fillStyle='#e63050';ctx.beginPath();ctx.arc(...hit,6,0,Math.PI*2);ctx.fill();ctx.strokeStyle='#fff';ctx.lineWidth=1;ctx.stroke()}
 ctx.strokeStyle=colour;ctx.lineWidth=2;ctx.setLineDash([]);ctx.strokeRect(a[0]-5,a[1]-5,10,10);ctx.beginPath();ctx.moveTo(b[0]-6,b[1]-6);ctx.lineTo(b[0]+6,b[1]+6);ctx.moveTo(b[0]+6,b[1]-6);ctx.lineTo(b[0]-6,b[1]+6);ctx.stroke();
 const transform=ctx.getTransform(),width=ctx.canvas.width/transform.a,height=ctx.canvas.height/transform.d,boxes:number[][]=[];
 const label=(p:MapPoint,text:string,above=false)=>{ctx.font='bold 11px system-ui';const w=ctx.measureText(text).width+8,x=Math.max(3,Math.min(width-w-3,p[0]+8));let y=Math.max(3,Math.min(height-19,p[1]+(above?-27:9)));while(boxes.some(b=>x<b[0]+b[2]&&x+w>b[0]&&Math.abs(y-b[1])<17)&&y+34<height)y+=18;boxes.push([x,y,w]);ctx.fillStyle='#fffffff0';ctx.fillRect(x,y,w,16);ctx.fillStyle=colour;ctx.fillText(text,x+4,y+12)};
 label(a,`${s.observer} · ${english?'sense':'感知'} ${s.at.toFixed(1)} s`);label(b,english?'P sampled position':'P 感知时位置');if(hit)label(hit,english?'First hit':'首个遮挡点',true);ctx.restore();
}
