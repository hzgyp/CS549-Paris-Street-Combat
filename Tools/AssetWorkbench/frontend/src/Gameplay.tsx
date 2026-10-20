import {useEffect,useState} from 'react';
import {ReferenceLinks} from './ReferenceLinks';
import {ArrowLeft,ArrowRight,FileText,Search,Layers3,MapPin} from 'lucide-react';
import {useLocale} from './i18n';

type Data=Record<string,any>;
type Props={id?:string;snapshot:string;navigate:(url:string)=>void;source:(id:string)=>void};
const kinds:Data={mechanic:{zh:'玩法规则',en:'Mechanics'},mission:{zh:'任务设计',en:'Missions'},route:{zh:'地图与路线',en:'Maps and routes'},presentation:{zh:'表现与交互',en:'Presentation'}};
const states:Data={confirmed:{zh:'规则已确认',en:'Confirmed rules'},review:{zh:'方案待评审',en:'Proposal for review'},reference:{zh:'验证参考',en:'Validation reference'},formal:{zh:'正式采用',en:'Adopted'},unimplemented:{zh:'未实现',en:'Not implemented'},diagnostic:{zh:'独立诊断',en:'Diagnostic only'},scoped_verified:{zh:'限定范围已验证',en:'Verified within scope'},survey_only:{zh:'仅测绘连接',en:'Survey links only'},pending:{zh:'待验证',en:'Pending validation'},failed_fixed_routes:{zh:'固定路线未通过',en:'Fixed routes failed'}};
export function Gameplay({id,snapshot,navigate,source}:Props){
 const {locale}=useLocale();const t=(v:any):string=>typeof v==='string'?v:v?.[locale]||'';
 const word=(zh:string,en:string)=>locale==='zh'?zh:en;
 const [q,setQ]=useState(''),[kind,setKind]=useState(''),[implementation,setImplementation]=useState('');
 const [data,setData]=useState<Data|null>(null),[error,setError]=useState('');
 const query=new URLSearchParams({q,kind,implementation,snapshot_id:snapshot}).toString();
 useEffect(()=>{const controller=new AbortController();setData(null);setError('');
  fetch('/api/v1/gameplay'+(id?'/'+encodeURIComponent(id)+'?snapshot_id='+snapshot:'?'+query),{signal:controller.signal})
   .then(async r=>{const json=await r.json();if(!r.ok)throw new Error(json.message);return json.data})
   .then(setData).catch(e=>{if(e.name!=='AbortError')setError(e.message)});return()=>controller.abort();
 },[id,snapshot,query]);
 const tags=(g:Data)=><div className="gameplay-tags"><span className="badge">{t(states[g.design_state])}</span><span className={'badge '+(g.implementation.state==='formal'?'formal':'')}>{t(states[g.implementation.state])}</span><span className={'badge '+(g.validation.state==='failed_fixed_routes'?'fail':'')}>{t(states[g.validation.state])}</span></div>;
 const heading=(title:string,description:string)=><div className="page-title"><div><h1>{title}</h1><p>{description}</p></div></div>;
 if(error)return <div className="empty error"><p>{error}</p></div>;
 if(!id)return <>{heading(word('玩法设计','Gameplay design'),word('规则、任务、地图点位与实现版本。','Rules, missions, map sites and implementation versions.'))}
  <div className="library-tools"><label className="search-box"><Search size={18}/><input aria-label={word('搜索玩法','Search gameplay')} value={q} onChange={e=>setQ(e.target.value)} placeholder={word('搜索规则、任务或关联资产…','Search rules, missions or linked assets…')}/></label>
   <select aria-label={word('实现状态','Implementation status')} value={implementation} onChange={e=>setImplementation(e.target.value)}><option value="">{word('全部实现状态','All implementation states')}</option>{['formal','unimplemented','diagnostic'].map(s=><option key={s} value={s}>{t(states[s])}</option>)}</select></div>
  <div className="categories"><button className={!kind?'active':''} onClick={()=>setKind('')}>{word('全部','All')}</button>{Object.entries(kinds).map(([k,v])=><button key={k} className={kind===k?'active':''} onClick={()=>setKind(k)}>{t(v)}</button>)}</div>
  <div className="list-summary"><span>{data?data.total+' '+word('条记录','records'):word('读取中…','Loading…')}</span><span>{word('设计、实现与验证范围分别记录','Design, implementation and validation are tracked separately')}</span></div>
  {!data?<div className="loading">{word('读取中…','Loading…')}</div>:!data.items.length?<div className="empty">{word('无匹配记录','No matching records')}</div>:<div className="gameplay-grid">{data.items.map((g:Data)=><button className="gameplay-card" key={g.id} onClick={()=>navigate('/gameplay/'+g.id)}><small>{t(kinds[g.kind])} · {g.id}</small><h2>{t(g.title)}<ArrowRight size={18}/></h2><p>{t(g.summary)}</p>{tags(g)}<div className="gameplay-card-footer">{g.asset_ids.length} {word('关联资产','linked assets')} · {g.implementation.revision||g.revision}</div></button>)}</div>}</>;
 if(!data)return <div className="loading">{word('读取中…','Loading…')}</div>;
 const g=data;
 const textList=(title:string,rows:any[],ordered=false)=>rows?.length?<section className="panel gameplay-section"><h2>{title}</h2>{ordered?<ol>{rows.map((r,i)=><li key={i}>{t(r)}</li>)}</ol>:<ul>{rows.map((r,i)=><li key={i}>{t(r)}</li>)}</ul>}</section>:null;
 return <><button className="text-button back" onClick={()=>navigate('/gameplay')}><ArrowLeft size={16}/>{word('返回玩法设计','Back to gameplay')}</button>{heading(t(g.title),t(g.summary))}{tags(g)}
  {g.source_changed&&<div className="notice gameplay-notice">{word('来源文档已更新，摘要需复核；请以最新原文为准。','Source documents changed; review the summary and follow the latest originals.')}</div>}
  <div className="two-columns gameplay-status"><section className="panel"><h2>{word('实现版本','Implementation')}</h2><p>{t(g.implementation.note)}</p>{g.implementation.build_id&&<button className="text-button" onClick={()=>navigate('/builds/'+g.implementation.build_id)}><Layers3 size={16}/>{word('查看当前构建','View current build')}</button>}{g.implementation.revision&&<code>{g.implementation.revision}<br/>Game {g.implementation.game_sha256?.slice(0,12)}</code>}</section>
   <section className="panel"><h2>{word('验证范围','Validation scope')}</h2><p>{t(g.validation.note)}</p><small>{word('登记修订','Registration revision')} {g.revision}</small></section></div>
  {textList(word('玩法规则','Gameplay rules'),g.rules)}{textList(word('任务步骤','Mission steps'),g.steps,true)}
  {g.media_ids?.length>0&&<section className="panel gameplay-section"><h2>{word('设计图与实图','Design figures and actual captures')}</h2><p className="muted">{word('来源图保留原文；设计图不代表新运行验收。','Source figures retain their original language; design figures are not new runtime validation.')}</p><div className="gameplay-figures">{g.media_ids.map((mid:string)=><img key={mid} src={'/api/v1/media/'+mid+'?snapshot_id='+snapshot} alt={t(g.title)} loading="lazy"/>)}</div></section>}
  {g.locations?.length>0&&<section className="panel gameplay-section"><h2><MapPin size={17}/>{word('候选地点','Candidate sites')}</h2><p className="muted">{word('独立扩展测绘L0，脚底坐标（米）；不是已采用角色出生点。','Expanded survey L0, foot coordinates in metres; these are not approved actor spawn sites.')}</p><div className="member-table"><table><thead><tr><th>ID</th><th>XYZ (m)</th><th>{word('支撑','Support')}</th><th>{word('范围与状态','Scope and status')}</th></tr></thead><tbody>{g.locations.map((p:Data)=><tr key={p.id}><td>{p.id}</td><td>{p.foot_xyz_m.join(', ')}</td><td><code>{p.support}</code></td><td>{t(p.note)}</td></tr>)}</tbody></table></div></section>}
  {textList(word('待解决事项','Open items'),g.open_items)}
  <ReferenceLinks references={g.historical_references} snapshot={snapshot} navigate={navigate}/>
  <section className="panel gameplay-section"><h2>{word('关联资产','Linked assets')}</h2><div className="gameplay-assets">{g.assets.map((a:Data)=><button className="secondary" key={a.id} onClick={()=>navigate('/assets/'+a.id)}>{locale==='en'?a.name_en:a.name}<ArrowRight size={15}/></button>)}</div></section>
  <section className="panel gameplay-section"><h2>{word('来源文档','Source documents')}</h2>{g.documents.map((d:Data)=><div className="source-row" key={d.path}><FileText size={17}/><button className="text-button" onClick={()=>source(d.source_id)}>{t(d.title)}</button><code>{d.sha256.slice(0,12)}</code></div>)}</section>
  {g.related_ids?.length>0&&<section className="panel gameplay-section"><h2>{word('相关玩法','Related gameplay')}</h2><div className="button-row">{g.related_ids.map((related:string)=><button className="secondary" key={related} onClick={()=>navigate('/gameplay/'+related)}>{related}<ArrowRight size={15}/></button>)}</div></section>}</>;
}
