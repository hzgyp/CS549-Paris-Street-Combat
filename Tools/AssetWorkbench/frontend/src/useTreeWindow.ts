import {useEffect,useLayoutEffect,useRef,useState} from 'react';

export function useTreeWindow(width:number,height:number){
 const [expanded,setExpanded]=useState(false),[zoom,setZoom]=useState(1),[inspecting,setInspecting]=useState(false),[dragging,setDragging]=useState(false);
 const viewport=useRef<HTMLDivElement>(null),section=useRef<HTMLElement>(null);
 const opener=useRef<HTMLElement|null>(null);
 const anchor=useRef<{x:number;y:number;clientX:number;clientY:number}|null>(null);
 const drag=useRef<{id:number;x:number;y:number;left:number;top:number;moved:boolean}|null>(null),suppressClick=useRef(false);
 function changeZoom(next:number,clientX?:number,clientY?:number){
  const el=viewport.current;if(!el)return;
  const px=clientX??el.clientWidth/2,py=clientY??el.clientHeight/2;
  anchor.current={x:(el.scrollLeft+px)/zoom,y:(el.scrollTop+py)/zoom,clientX:px,clientY:py};
  setZoom(Math.min(2,Math.max(.05,next)));
 }
 function fit(){const el=viewport.current;if(el){anchor.current=null;setZoom(Math.min(1,Math.max(.05,Math.min((el.clientWidth-24)/width,(el.clientHeight-24)/height))));el.scrollTo(0,0)}}
 useLayoutEffect(()=>{const el=viewport.current,a=anchor.current;if(el&&a){el.scrollTo(a.x*zoom-a.clientX,a.y*zoom-a.clientY);anchor.current=null}},[zoom]);
 useEffect(()=>{
  const el=viewport.current;if(!el)return;
  function wheel(e:WheelEvent){if(e.ctrlKey||e.metaKey){e.preventDefault();const r=el!.getBoundingClientRect();changeZoom(zoom*Math.exp(-e.deltaY*.002),e.clientX-r.left,e.clientY-r.top)}}
  el.addEventListener('wheel',wheel,{passive:false});return()=>el.removeEventListener('wheel',wheel);
 },[zoom,expanded,width,height]);
 useEffect(()=>{
  if(!expanded)return;
  const previous=opener.current,overflow=document.body.style.overflow,root=document.getElementById('root'),wasInert=root?.inert;
  document.body.style.overflow='hidden';if(root)root.inert=true;
  const frame=requestAnimationFrame(()=>{fit();section.current?.querySelector<HTMLButtonElement>('#npc-tree-expand')?.focus()});
  function keys(e:KeyboardEvent){
   if(e.key==='Escape'){e.preventDefault();setExpanded(false)}
   if(e.key==='Tab'){
    const items=Array.from(section.current?.querySelectorAll<HTMLElement>('button:not(:disabled),select,input,[tabindex="0"]')||[]).filter(el=>el.getClientRects().length>0);
    const first=items[0],last=items[items.length-1];
    if(e.shiftKey&&(document.activeElement===first||!section.current?.contains(document.activeElement))){e.preventDefault();last?.focus()}
    else if(!e.shiftKey&&(document.activeElement===last||!section.current?.contains(document.activeElement))){e.preventDefault();first?.focus()}
   }
  }
  document.addEventListener('keydown',keys);
  return()=>{cancelAnimationFrame(frame);document.body.style.overflow=overflow;if(root)root.inert=!!wasInert;document.removeEventListener('keydown',keys);requestAnimationFrame(()=>{if(previous?.isConnected)previous.focus();else document.getElementById('npc-tree-expand')?.focus()})};
 },[expanded]);
 function pointerDown(e:React.PointerEvent<HTMLDivElement>){
  if(e.button!==0||(e.target as Element).closest('[data-node-id]'))return;
  const el=e.currentTarget;drag.current={id:e.pointerId,x:e.clientX,y:e.clientY,left:el.scrollLeft,top:el.scrollTop,moved:false};suppressClick.current=false;el.setPointerCapture(e.pointerId);
 }
 function pointerMove(e:React.PointerEvent<HTMLDivElement>){const d=drag.current;if(!d||d.id!==e.pointerId)return;const dx=e.clientX-d.x,dy=e.clientY-d.y;if(Math.hypot(dx,dy)>4){d.moved=true;setDragging(true)}if(d.moved){e.currentTarget.scrollTo(d.left-dx,d.top-dy);e.preventDefault()}}
 function pointerEnd(e:React.PointerEvent<HTMLDivElement>){const d=drag.current;if(d?.id!==e.pointerId)return;suppressClick.current=d.moved;drag.current=null;setDragging(false);if(e.currentTarget.hasPointerCapture(e.pointerId))e.currentTarget.releasePointerCapture(e.pointerId)}
 function expand(next:boolean){if(next)opener.current=document.activeElement as HTMLElement|null;setExpanded(next)}
 return {expanded,setExpanded:expand,zoom,changeZoom,fit,inspecting,setInspecting,viewport,section,dragging,
  gestures:{onPointerDown:pointerDown,onPointerMove:pointerMove,onPointerUp:pointerEnd,onPointerCancel:pointerEnd,onLostPointerCapture:()=>{drag.current=null;setDragging(false)},onClickCapture:(e:React.MouseEvent)=>{if(suppressClick.current){e.preventDefault();e.stopPropagation();suppressClick.current=false}}}};
}
