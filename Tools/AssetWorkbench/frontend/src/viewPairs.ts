type Data=Record<string,any>;
export type ViewPair={id:string;label:Data;left?:string;right?:string;registered:boolean;cameraMatch:boolean};

export function buildViewPairs(left:Data,right:Data):ViewPair[]{
 const groups=new Map<string,ViewPair>(),unknown:ViewPair[]=[];
 for(const [side,row] of [['left',left],['right',right]] as const){
  const counts:Data={};for(const id of row.media_ids||[]){const key=row.image_views?.[id]?.key;if(key)counts[key]=(counts[key]||0)+1}
  for(const id of row.media_ids||[]){
   const view=row.image_views?.[id];
   if(!view||counts[view.key]>1){unknown.push({id:`unknown:${side}:${id}`,label:{zh:'未登记视角',en:'Unregistered view'},[side]:id,registered:false,cameraMatch:false});continue}
   const pair:ViewPair=groups.get(view.key)||{id:'view:'+view.key,label:view.label,registered:true,cameraMatch:false};pair[side]=id;groups.set(view.key,pair);
  }
 }
 const order=['hero','front','back','side','top','rear_oblique','detail'];
 const rank=(p:ViewPair)=>p.id.startsWith('view:medkit:')?order.indexOf(p.id.split(':').at(-1)!):20;
 const known=[...groups.values()];
 for(const p of known){const l=left.image_views?.[p.left||''],r=right.image_views?.[p.right||''];p.cameraMatch=Boolean(l?.camera_group&&l.camera_group===r?.camera_group)}
 return known.sort((a,b)=>Number(Boolean(b.left&&b.right))-Number(Boolean(a.left&&a.right))||rank(a)-rank(b)||a.id.localeCompare(b.id)).concat(unknown);
}
