type Revision = Record<string, any>;

export function orderedVersions(rows:Revision[]):Revision[]{
 return rows.slice().reverse().sort((a,b)=>Number(Boolean(b.adoption))-Number(Boolean(a.adoption)) || Number(Boolean(b.adoption?.primary))-Number(Boolean(a.adoption?.primary)));
}

export function defaultPair(rows:Revision[]){
 const current=rows.find(r=>r.adoption?.primary)||rows.find(r=>r.adoption);
 if(current)return {left:current.adoption.previous_id||'',right:current.id};
 // Unknown adoption stays unknown; these are only the latest registered records.
 const list=rows.filter(r=>r.kind!=='bundle_revision').slice().reverse();
 const latest=list[0]||rows[rows.length-1];
 const prior=rows.find(r=>r.id===latest?.parent_ids?.[0])||list[1];
 return {left:prior?.id||'',right:latest?.id||''};
}

export function visibleVersions(rows:Revision[],filter:string){
 return orderedVersions(rows).filter(r=>r.adoption||filter==='all'||(r.review_state||'pending')===filter);
}
