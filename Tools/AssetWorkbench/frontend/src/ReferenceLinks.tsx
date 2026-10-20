import {useEffect,useState} from 'react';
import {ArrowRight,ExternalLink,X} from 'lucide-react';
import {useLocale} from './i18n';

type Data=Record<string,any>;
export function ReferenceLinks({references=[],snapshot,navigate}:{references:Data[];snapshot:string;navigate:(p:string)=>void}){
 const {locale}=useLocale();const w=(zh:string,en:string)=>locale==='zh'?zh:en;
 const [expanded,setExpanded]=useState(false),[zoom,setZoom]=useState<Data|null>(null);
 useEffect(()=>{setExpanded(false);setZoom(null)},[references]);
 useEffect(()=>{const close=(e:KeyboardEvent)=>{if(e.key==='Escape')setZoom(null)};window.addEventListener('keydown',close);return()=>window.removeEventListener('keydown',close)},[]);
 const image=(r:Data)=>'/api/v1/media/'+encodeURIComponent(r.media_id)+'?snapshot_id='+snapshot;
 const scopes:Data={paris:w('巴黎 · 1944','Paris · 1944'),equipment:w('装备研究','Equipment research')};
 const types:Data={context:w('场景背景','Context'),visual:w('外观参考','Appearance'),identity_check:w('身份核对','Identity check'),adaptation:w('玩法改编','Gameplay adaptation'),comparison:w('对照资料','Comparison')};
 const images=references.filter(r=>r.kind==='image'),texts=references.filter(r=>r.kind!=='image');
 const purpose=(r:Data)=>r.association&&<p className="reference-purpose"><strong>{types[r.association.relation]}</strong> · {r.association.note[locale]}</p>;
 const sources=(r:Data)=><div className="reference-sources">{r.links?.map((l:Data)=><a href={l.url} key={l.url} target="_blank" rel="noopener noreferrer"><ExternalLink size={14}/>{w('来源','Source')}{r.links.length>1?' · '+(r.links.indexOf(l)+1):''}</a>)}<button className="text-button" onClick={()=>navigate('/research/'+r.id)}>{w('资料全文与来源记录','Full text and provenance')}<ArrowRight size={14}/></button></div>;
 return <section className="panel reference-section"><div className="section-head"><h2>{w('参考文字、图片与来源','Reference text, images and sources')}</h2><span>{references.length} {w('条','records')}</span></div>
  {!references.length?<p className="muted">{w('尚未登记对应历史资料。','No corresponding historical references registered.')}</p>:<>
  {images.length>0&&<div className="reference-images">{(expanded?images:images.slice(0,4)).map(r=><article key={r.id} className="reference-image-card">{r.media_id?<button className="reference-thumb" aria-label={w('放大参考图：','Enlarge reference: ')+r.title} onClick={()=>setZoom(r)}><img loading="lazy" src={image(r)} alt={r.title}/></button>:<div className="reference-link-only">{w('图片仅提供来源链接','Image available through source link only')}</div>}<div><small>{scopes[r.scope]} · {r.date}</small><h3>{r.title}</h3>{purpose(r)}{r.excerpt&&<p className="reference-caption">{r.excerpt}</p>}<small>{r.institution} · {r.rights}</small>{r.limitation&&<details><summary>{w('适用限制','Limitations')}</summary><p>{r.limitation}</p></details>}{sources(r)}</div></article>)}</div>}
  <div className="reference-texts">{(expanded?texts:texts.slice(0,4)).map(r=><article key={r.id}><small>{scopes[r.scope]} · {r.institution} {r.date}</small><h3>{r.title}</h3>{purpose(r)}{r.excerpt&&<pre>{r.excerpt}{r.has_more?'…':''}</pre>}{r.limitation&&<details><summary>{w('适用限制','Limitations')}</summary><p>{r.limitation}</p></details>}{sources(r)}</article>)}</div>
  {(images.length>4||texts.length>4)&&<button className="secondary" onClick={()=>setExpanded(!expanded)}>{expanded?w('收起资料','Show fewer'):w('展开全部 '+references.length+' 条资料','Show all '+references.length+' references')}</button>}</>}
  {zoom&&<div className="modal-backdrop research-zoom" role="dialog" aria-modal="true" aria-label={w('参考图预览','Reference image preview')} onClick={()=>setZoom(null)}><button className="icon-button" aria-label={w('关闭图片','Close image')} onClick={()=>setZoom(null)}><X/></button><img src={image(zoom)} alt={zoom.title}/><a className="reference-original" href={image(zoom)+'&original=true'} target="_blank" rel="noopener noreferrer" onClick={e=>e.stopPropagation()}>{w('查看原图','View original')}</a></div>}
 </section>;
}
