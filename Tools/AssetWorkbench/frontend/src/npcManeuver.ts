/** Display recorded roles only, never derive AI readiness or a future role. */
export function maneuverAt(frame:any,id:string,at=frame.at):any|undefined{
 const trace=frame.behavior_trees?.[id],record=trace?.blackboard?.maneuver;
 return record&&Number.isFinite(record.at)&&record.at<=at&&trace.at<=at?record:undefined;
}
const roles:Record<string,[string,string]>={PrepareCover:['进入掩体 / 探出','Take cover / peek'],CoverWatch:['原地掩护','Cover watch'],Advance:['推进下一掩体','Advance to cover'],WaitCover:['等待队友掩护','Wait for cover'],OpenFormation:['无合格掩体 · 队形','No cover · formation'],Solo:['单人支援','Solo support'],ContactWatch:['目击者 · 压制观察','Observer · contact watch'],FlankLeft:['左翼包抄','Flank left'],FlankRight:['右翼包抄','Flank right'],SearchSector:['分区搜索','Sector search']};
export function maneuverRole(record:any,english=false){const role=roles[record?.role];return role?role[english?1:0]:''}
export function maneuverReason(m:any,english=false){
 const t=(zh:string,en:string)=>english?en:zh;
 if(!m)return t('本帧没有协同分工记录。','No recorded maneuver in this frame.');
 if(m.role==='Solo')return t('同伴已阵亡，使用独立支援；不再要求双人换位。','Partner unavailable; use independent support without a two-person bound.');
 if(m.role==='OpenFormation')return t('没有完整、分离且能向前推进的掩体组合，回退到明确的队形移动。','No complete separated forward cover pair; explicitly fall back to formation.');
 if(m.role==='SearchSector')return t(`第${m.sector}搜索扇区：冻结观察点，实际到达后推进点序，截止${m.deadline?.toFixed(1)}秒。`,`Search sector ${m.sector}: frozen evidence, actual arrival advances points; deadline ${m.deadline?.toFixed(1)} s.`);
 if(m.leg&&m.at>=m.leg.expires)return t('本轮包抄的有限时间已用完，原地观察，等待实际新敌情或新指令。','This finite flank leg expired; hold for materially new contact or a new order.');
 if(m.contact)return t(`由${m.contact.source}在${m.contact.at.toFixed(1)}秒目击并通报；${m.role==='ContactWatch'?'本成员保持目视观察':'按冻结通报走侧翼，自己看见后才能开火'}。`,`${m.contact.source} sight report at ${m.contact.at.toFixed(1)} s; ${m.role==='ContactWatch'?'this member holds visual contact':'approach the frozen flank; own sight is required to fire'}.`);
 const gates:Record<string,[string,string]>={entered_hide:['尚未进入藏身点','hide not reached'],at_peek:['尚未到探出点','peek not reached'],ammunition:['掩护者无弹药','holder has no ammunition'],holder_budget:['掩护者移动预算已用完','holder movement budget exhausted'],actual_watch_sight:['实际位置没有有效射界','actual watch sight failed'],mover_budget:['推进者移动预算已用完','mover movement budget exhausted']};
 const failed=Object.entries(m.ready_gates||{}).filter(([,ok])=>!ok).map(([key])=>gates[key]?.[english?1:0]||key).join(' / ');
 return t(`第${m.phase}阶段：${m.holder}掩护、${m.mover}推进；${m.holder_ready?'掩护已实际到位':`推进等待：${failed||'掩护尚未就绪'}`}。${m.threat_basis==='authored_forward_watch'?'方向来自玩家朝向，并非发现敌人。':'掩体针对记录的敌情位置。'}`,`Phase ${m.phase}: ${m.holder} covers, ${m.mover} advances; ${m.holder_ready?'holder is physically ready':`advance waits: ${failed||'holder not ready'}`}. ${m.threat_basis==='authored_forward_watch'?'Direction is authored player facing, not a detected enemy.':'Cover is relative to recorded contact.'}`);
}
