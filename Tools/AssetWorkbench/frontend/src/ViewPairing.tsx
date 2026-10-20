import React,{createContext,useContext,useEffect,useMemo,useRef,useState} from 'react';
import {useLocale} from './i18n';
import {buildViewPairs,type ViewPair} from './viewPairs';
type Data=Record<string,any>;
type PairState={rows:[Data,Data];pairs:ViewPair[];pair?:ViewPair;index:number;snapshot:string;choose:(id:string)=>void;open:()=>void};
const PairContext=createContext<PairState>(null!);
function status(pair:ViewPair|undefined,en:boolean){
 if(!pair)return en?'No registered screenshots':'无登记截图';
 if(!pair.registered)return en?'View unregistered · unpaired':'视角未登记 · 未配对';
 if(!pair.left)return en?'Left view missing':'左侧缺少对应视角';
 if(!pair.right)return en?'Right view missing':'右侧缺少对应视角';
 return pair.cameraMatch?(en?'Paired · same camera parameters':'已配对 · 相机参数一致'):(en?'View paired · camera parameters differ or are unverified':'视角已配对 · 相机参数不同或未核实');
}

export function PairedViews({left,right,snapshot,children}:{left:Data;right:Data;snapshot:string;children:React.ReactNode}){
 const {locale}=useLocale(),en=locale==='en';
 const pairs=useMemo(()=>buildViewPairs(left,right),[left,right]);const [selected,setSelected]=useState(''),[zoomed,setZoomed]=useState(false),[scale,setScale]=useState(1),[pan,setPan]=useState({x:0,y:0});
 const pair=pairs.find(p=>p.id===selected)||pairs[0],index=pair?pairs.indexOf(pair):-1;
 const drag=useRef<{x:number;y:number;pan:{x:number;y:number}}|null>(null),dialog=useRef<HTMLDivElement>(null);
 const reset=()=>{setScale(1);setPan({x:0,y:0});drag.current=null};
 useEffect(reset,[pair?.id]);
 useEffect(()=>{
  if(!zoomed)return;const before=document.activeElement as HTMLElement;dialog.current?.querySelector<HTMLButtonElement>('button')?.focus();
  const overflow=document.body.style.overflow;document.body.style.overflow='hidden';
  return()=>{document.body.style.overflow=overflow;before?.focus()};
 },[zoomed]);
 useEffect(()=>{
  if(!zoomed)return;
  const key=(e:KeyboardEvent)=>{
   if(e.key==='Escape'){e.preventDefault();setZoomed(false)}
   if(e.target instanceof HTMLSelectElement)return;
   if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();const next=Math.max(0,Math.min(pairs.length-1,index+(e.key==='ArrowLeft'?-1:1)));if(pairs[next])setSelected(pairs[next].id)}
   if(e.key==='Tab'){const nodes=Array.from(dialog.current?.querySelectorAll<HTMLElement>('button:not(:disabled),select,a[href]')||[]);const first=nodes[0],last=nodes.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus()}}
  };window.addEventListener('keydown',key);
  return()=>window.removeEventListener('keydown',key);
 },[zoomed,index,pairs]);
 const value:PairState={rows:[left,right],pairs,pair,index,snapshot,choose:setSelected,open:()=>{reset();setZoomed(true)}};
 const move=(e:React.PointerEvent<HTMLDivElement>)=>{if(!drag.current)return;setPan({x:drag.current.pan.x+e.clientX-drag.current.x,y:drag.current.pan.y+e.clientY-drag.current.y})};
 return <PairContext.Provider value={value}>{children}{zoomed&&<div className="paired-lightbox" role="dialog" aria-modal="true" aria-label={en?'Paired screenshots':'对照截图'} ref={dialog}>
  <header><button onClick={()=>setZoomed(false)} aria-label={en?'Close comparison':'关闭对照'}>{en?'Close':'关闭'} ×</button><strong>{en?'Linked zoom and pan':'同步缩放与平移'}</strong><div className="paired-zoom-tools"><button aria-label={en?'Zoom out':'缩小'} disabled={scale<=1} onClick={()=>{setScale(Math.max(1,scale-.5));setPan({x:0,y:0})}}>−</button><output>{Math.round(scale*100)}%</output><button aria-label={en?'Zoom in':'放大'} disabled={scale>=6} onClick={()=>setScale(Math.min(6,scale+.5))}>+</button><button onClick={reset}>{en?'Reset view':'重置视图'}</button></div></header>
  <PairControls enlarged/>
  <div className="paired-enlarged-grid">{([0,1] as const).map(side=>{const id=side===0?pair?.left:pair?.right,row=value.rows[side];return <section key={side}><h3>{side===0?(en?'Left':'左侧'):(en?'Right':'右侧')} · {en?(row.title_en||row.title):row.title}</h3><div className="paired-pan-area" data-testid={'paired-pan-'+side} onPointerDown={e=>{if(!id||e.button!==0)return;e.currentTarget.setPointerCapture(e.pointerId);drag.current={x:e.clientX,y:e.clientY,pan}}} onPointerMove={move} onPointerUp={e=>{drag.current=null;if(e.currentTarget.hasPointerCapture(e.pointerId))e.currentTarget.releasePointerCapture(e.pointerId)}} onPointerCancel={()=>{drag.current=null}}>
   {id?<PairPicture id={id} snapshot={snapshot} alt={pair?.label[locale]||''} transform={`translate(${pan.x}px, ${pan.y}px) scale(${scale})`}/>:<Missing side={side}/>}
  </div>{id&&<a href={mediaURL(id,snapshot,true)} target="_blank" rel="noreferrer">{en?'Original image':'查看原图'}</a>}</section>})}</div>
  <p className="paired-help">{en?'Drag either image to move both. Arrow keys switch views; Escape closes.':'拖动任一图片同步平移。方向键切换视角，Esc 关闭。'}</p>
 </div>}</PairContext.Provider>;
}
function mediaURL(id:string,snapshot:string,original=false){return '/api/v1/media/'+encodeURIComponent(id)+'?snapshot_id='+encodeURIComponent(snapshot)+(original?'&original=true':'')}
function PairPicture({id,snapshot,alt,transform}:{id:string;snapshot:string;alt:string;transform?:string}){
 const {locale}=useLocale();const [failed,setFailed]=useState(false);useEffect(()=>setFailed(false),[id,snapshot]);
 return failed?<p role="alert">{locale==='en'?'Image unavailable; original link retained.':'图片无法读取；保留原图链接。'}</p>:<img src={mediaURL(id,snapshot)} alt={alt} draggable={false} style={transform?{transform}:undefined} onError={()=>setFailed(true)}/>;
}
function Missing({side}:{side:0|1}){const {locale}=useLocale(),{pair}=useContext(PairContext);return <div className="paired-missing" data-testid={'missing-view-'+side}><strong>{locale==='en'?'No corresponding view':'无对应视角'}</strong><span>{pair?.registered?(locale==='en'?'This version has no screenshot for this view.':'此版本缺少该视角截图。'):(locale==='en'?'View is unregistered; no match is assumed.':'视角未登记，不作配对。')}</span></div>}

export function PairControls({enlarged=false}:{enlarged?:boolean}){
 const {locale}=useLocale(),en=locale==='en',{pairs,pair,index,choose,open}=useContext(PairContext);
 const matches=pairs.filter(p=>p.left&&p.right).length;
 return <div className="paired-controls" data-testid={enlarged?'paired-controls-enlarged':'paired-controls'}><div><label>{en?'View':'视角'} <select aria-label={en?(enlarged?'Enlarged view':'Comparison view'):(enlarged?'放大视角':'对照视角')} value={pair?.id||''} onChange={e=>choose(e.target.value)} disabled={!pairs.length}>{pairs.map(p=><option key={p.id} value={p.id}>{p.label[locale]} · {status(p,en)}{!p.registered?' · '+(p.left||p.right):''}</option>)}</select></label><button disabled={index<=0} onClick={()=>choose(pairs[index-1].id)}>{en?'Previous view':'上一视角'}</button><button disabled={index<0||index>=pairs.length-1} onClick={()=>choose(pairs[index+1].id)}>{en?'Next view':'下一视角'}</button>{!enlarged&&<button disabled={!pairs.length} onClick={open}>{en?'Enlarge both':'同步放大'}</button>}</div><p className={pair?.left&&pair?.right?'paired-status matched':'paired-status'}>{status(pair,en)} <span>· {en?`${matches} paired / ${pairs.length-matches} unpaired`:`${matches} 组配对 / ${pairs.length-matches} 项未配对`}</span></p></div>;
}

export function PairGallery({side}:{side:0|1}){
 const {locale}=useLocale(),en=locale==='en',{rows,pair,pairs,index,snapshot,choose,open}=useContext(PairContext);const [expanded,setExpanded]=useState(false);
 const id=side===0?pair?.left:pair?.right,row=rows[side],shot=row.screenshots?.find((s:Data)=>s.id===id),view=id?row.image_views?.[id]:null;
 return <div className="version-gallery paired-gallery" data-paired-side={side}>
  <strong className="paired-view-label">{pair?.label[locale]|| (en?'No view':'无视角')} <small>{en?'Linked':'同步'}</small></strong>
  {id?<button className="version-main-image" onClick={open} aria-label={en?'Enlarge screenshot':'放大截图'}><PairPicture id={id} snapshot={snapshot} alt={pair?.label[locale]||''}/></button>:<Missing side={side}/>}
  <div className="version-image-toolbar"><span>{index+1} / {pairs.length}</span><button className="text-button" disabled={!pairs.length} onClick={open}>{en?'Enlarge both':'同步放大'}</button>{id&&<a target="_blank" rel="noreferrer" href={mediaURL(id,snapshot,true)}>{en?'Original image':'查看原图'}</a>}</div>
  <div className="version-thumbnails">{pairs.slice(0,expanded?pairs.length:12).map((p,i)=>{const media=side===0?p.left:p.right;return <button key={p.id} className={p.id===pair?.id?'selected':''} onClick={()=>choose(p.id)} aria-label={(en?'Screenshot ':'截图 ')+(i+1)} title={p.label[locale]+' · '+status(p,en)}>{media?<img src={mediaURL(media,snapshot)} loading="lazy" alt={p.label[locale]}/>:<span className="paired-thumb-missing">{en?'Missing':'缺图'}</span>}<span>{p.label[locale]}</span></button>})}</div>
  {pairs.length>12&&<button className="text-button" onClick={()=>setExpanded(!expanded)}>{expanded?(en?'Collapse views':'收起视角'):(en?`Show all ${pairs.length} views`:`展开全部 ${pairs.length} 个视角`)}</button>}
  {shot&&<details className="version-image-source"><summary>{en?'Image source and identity':'图片来源与身份'}</summary><code>{shot.path}</code><small>SHA256 {shot.sha256}</small>{view&&<><p>{en?'View evidence':'视角依据'} · {view.basis}</p><code>{view.source}</code></>}</details>}
 </div>;
}
