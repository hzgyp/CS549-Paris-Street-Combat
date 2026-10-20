import {useEffect,useState} from 'react';
import {ArrowLeft,ArrowRight,ExternalLink,FileText,ImageOff,Search,X} from 'lucide-react';
import {useLocale} from './i18n';

type Data=Record<string,any>;
export function Research({id,snapshot,navigate,source}:{id?:string;snapshot:string;navigate:(p:string)=>void;source:(id:string)=>void}){
 const {locale}=useLocale();const w=(zh:string,en:string)=>locale==='zh'?zh:en;
 const scopes:Data={paris:w('巴黎 · 1944','Paris · 1944'),equipment:w('装备研究','Equipment research')};
 const kinds:Data={source:w('来源记录','Sources'),image:w('图片','Images'),note:w('研究文字','Research notes')};
 const [q,setQ]=useState(new URLSearchParams(location.search).get('q')||''),[scope,setScope]=useState(''),[kind,setKind]=useState(''),[page,setPage]=useState(0);
 const [data,setData]=useState<Data|null>(null),[error,setError]=useState(''),[zoom,setZoom]=useState(false),[imageFailed,setImageFailed]=useState(false);
 const query=new URLSearchParams({q,scope,kind,snapshot_id:snapshot}).toString();
 useEffect(()=>{const c=new AbortController();setData(null);setError('');setZoom(false);setImageFailed(false);setPage(0);
  fetch('/api/v1/research'+(id?'/'+encodeURIComponent(id)+'?snapshot_id='+snapshot:'?'+query),{signal:c.signal}).then(async r=>{const d=await r.json();if(!r.ok)throw new Error(d.message);return d.data}).then(setData).catch(e=>{if(e.name!=='AbortError')setError(e.message)});return()=>c.abort();
 },[id,query,snapshot]);
 useEffect(()=>{const listener=(e:KeyboardEvent)=>{if(e.key==='Escape')setZoom(false)};window.addEventListener('keydown',listener);return()=>window.removeEventListener('keydown',listener)},[]);
 const image=(r:Data)=>'/api/v1/media/'+r.media_id+'?snapshot_id='+snapshot;
 const heading=(title:string,description:string)=><div className="page-title"><div><h1>{title}</h1><p>{description}</p></div></div>;
 if(error)return <div className="empty error">{error}</div>;
 if(!id)return <>{heading(w('历史资料','Historical references'),w('文字、图片、来源与适用范围。','Text, images, sources and scope.'))}
  <div className="library-tools"><label className="search-box"><Search size={18}/><input aria-label={w('搜索历史资料','Search historical references')} placeholder={w('搜索正文、图片说明、机构或地点…','Search text, captions, institutions or places…')} value={q} onChange={e=>setQ(e.target.value)}/></label><select aria-label={w('资料类型','Reference type')} value={kind} onChange={e=>setKind(e.target.value)}><option value="">{w('全部类型','All types')}</option>{Object.entries(kinds).map(([k,v])=><option key={k} value={k}>{v}</option>)}</select></div>
  <div className="categories"><button className={!scope?'active':''} onClick={()=>setScope('')}>{w('全部','All')}</button>{Object.entries(scopes).map(([k,v])=><button key={k} className={scope===k?'active':''} onClick={()=>setScope(k)}>{v}</button>)}</div>
  <div className="list-summary"><span>{data?data.total+' '+w('条记录','records'):w('读取中…','Loading…')}</span><span>{w('原文保留原语言；图片按登记权利展示','Original language retained; images follow recorded rights')}</span></div>
  {!data?<div className="loading">{w('读取中…','Loading…')}</div>:!data.items.length?<div className="empty">{w('无匹配资料','No matching references')}</div>:<div className="research-grid">{data.items.slice(page*24,(page+1)*24).map((r:Data)=><button className="research-card" key={r.id} onClick={()=>navigate('/research/'+r.id)}>{r.kind==='image'&&<div className="research-cover">{r.media_id?<img src={image(r)} alt={r.title} loading="lazy"/>:<div className="media-placeholder"><ImageOff size={28}/><span>{w('来源链接','Source link')}</span></div>}</div>}<div className="research-card-body"><small>{scopes[r.scope]} · {kinds[r.kind]}</small><h2>{r.title}<ArrowRight size={16}/></h2><p>{r.institution||r.location}</p><small>{r.date}</small></div></button>)}</div>}
  {data&&data.total>24&&<div className="button-row research-pager"><button className="secondary" disabled={!page} onClick={()=>setPage(page-1)}>{w('上一页','Previous')}</button><span>{page+1} / {Math.ceil(data.total/24)}</span><button className="secondary" disabled={(page+1)*24>=data.total} onClick={()=>setPage(page+1)}>{w('下一页','Next')}</button></div>}</>;
 if(!data)return <div className="loading">{w('读取中…','Loading…')}</div>;
 const r=data;
 const access=r.image_access==='rights_link_only'?w('仅来源链接；未登记展示许可','Source link only; display rights not established'):r.image_access==='missing'?w('本机原件缺失','Local original unavailable'):'';
 return <><button className="text-button back" onClick={()=>navigate('/research')}><ArrowLeft size={16}/>{w('返回历史资料','Back to references')}</button>{heading(r.title,scopes[r.scope]+' · '+kinds[r.kind])}
  <section className="panel research-metadata"><dl>{[[w('机构 / 来源','Institution / source'),r.institution],[w('日期','Date'),r.date],[w('地点 / 范围','Location / scope'),r.location],[w('权利记录','Recorded rights'),r.rights]].map(([k,v])=><div key={k}><dt>{k}</dt><dd>{v||w('未记录','Not recorded')}</dd></div>)}</dl>{r.limitation&&<p className="research-limitation">{r.limitation}</p>}{access&&<p>{access}</p>}{r.links.length>0&&<div className="research-links">{r.links.map((l:Data)=><a href={l.url} key={l.url} target="_blank" rel="noopener noreferrer"><ExternalLink size={15}/><span>{l.title==='来源 / Source'?w('打开来源','Open source'):l.title}</span></a>)}</div>}</section>
  {r.media_id&&<section className="panel research-image"><button onClick={()=>setZoom(true)} aria-label={w('放大图片','Enlarge image')}>{imageFailed?<span>{w('图片不可用，请刷新索引核对原件','Image unavailable; refresh to check the original')}</span>:<img src={image(r)} alt={r.title} onError={()=>setImageFailed(true)}/>}</button><div className="source-row"><span>{r.dimensions?.join(' × ')} · SHA256 <code>{r.image_sha256}</code></span><a href={image(r)+'&original=true'} target="_blank" rel="noopener noreferrer">{w('查看原图','View original')}</a></div></section>}
  {r.body&&<section className="panel research-text"><h2>{w('资料原文','Original text')}</h2><pre>{r.body}</pre></section>}
  {r.local_files.length>0&&<section className="panel"><h2>{w('本地存档','Local archives')}</h2>{r.local_files.map((f:Data)=><p className="research-path" key={f.path}><code>{f.path}</code> · {f.available?w('已保存','Present'):w('缺失','Missing')}</p>)}</section>}
  {r.assets?.length>0&&<section className="panel gameplay-section"><h2>{w('关联资产','Linked assets')}</h2>{r.assets.map((a:Data)=><div className="reference-reverse" key={a.id}><button className="secondary" onClick={()=>navigate('/assets/'+a.id)}>{locale==='en'?a.name_en:a.name}<ArrowRight size={15}/></button><p>{r.asset_links?.find((l:Data)=>l.id===a.id)?.note[locale]}</p></div>)}</section>}
  {r.gameplay?.length>0&&<section className="panel gameplay-section"><h2>{w('关联玩法设计','Linked gameplay design')}</h2>{r.gameplay.map((g:Data)=><div className="reference-reverse" key={g.id}><button className="secondary" onClick={()=>navigate('/gameplay/'+g.id)}>{g.title[locale]}<ArrowRight size={15}/></button><p>{r.gameplay_links?.find((l:Data)=>l.id===g.id)?.note[locale]}</p></div>)}</section>}
  <section className="panel"><h2>{w('登记依据','Registration source')}</h2><button className="text-button" onClick={()=>source(r.source_id)}><FileText size={16}/>{r.register}</button><p className="research-path"><code>{r.source_sha256}</code></p></section>
  {zoom&&<div className="modal-backdrop research-zoom" role="dialog" aria-modal="true" aria-label={w('图片预览','Image preview')} onClick={()=>setZoom(false)}><button className="icon-button" aria-label={w('关闭图片','Close image')} onClick={()=>setZoom(false)}><X/></button><img src={image(r)} alt={r.title}/></div>}</>;
}
