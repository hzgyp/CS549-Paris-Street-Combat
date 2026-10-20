import React,{useEffect,useState} from 'react';
import {ArrowRight,Box,Clapperboard,FileText,ImageOff,Map,Users,Package,Gamepad2} from 'lucide-react';
import {useLocale} from './i18n';
import './homeOverview.css';
type Data=Record<string,any>;
type LinkProps=React.AnchorHTMLAttributes<HTMLAnchorElement>&{navigate:(url:string)=>void;href:string};
function Link({navigate,href,children,...props}:LinkProps){return <a {...props} href={href} onClick={e=>{if(e.button===0&&!e.ctrlKey&&!e.metaKey&&!e.shiftKey&&!e.altKey){e.preventDefault();navigate(href)}}}>{children}</a>}
function Picture({id,snapshot,alt,fit='contain',priority=false}:{id?:string;snapshot:string;alt:string;fit?:string;priority?:boolean}){
 const [failed,setFailed]=useState(false),{locale}=useLocale();
 useEffect(()=>setFailed(false),[id,snapshot]);
 return !id||failed?<div className="home-no-picture"><ImageOff size={26}/><span>{locale==='en'?'Preview not registered':'预览未登记'}</span></div>:<img key={id} src={'/api/v1/media/'+encodeURIComponent(id)+'?snapshot_id='+encodeURIComponent(snapshot)} alt={alt} style={{objectFit:fit==='cover'?'cover':'contain'}} loading={priority?'eager':'lazy'} onError={()=>setFailed(true)}/>;
}
const icons:Data={actions:Clapperboard,characters:Users,scenes:Map,props:Package};
export function HomeOverview({data,snapshot,navigate}:{data:Data;snapshot:string;navigate:(url:string)=>void}){
 const {locale,tx}=useLocale(),en=locale==='en',home=data.homepage;
 if(!home)return <div className="empty">{en?'Refresh the index to load homepage modules.':'刷新索引以加载首页模块。'}</div>;
 const release=home.release,archive=data.builds.filter((b:Data)=>b.id!==release.build_id);
 const status:Data={adopted:en?'Current adopted':'当前采用',current_use:en?'In current release':'当前使用',registered:en?'Registered':'已登记'};
 return <div className="home-overview">
  <header className="home-heading"><div><span className="home-kicker">PARIS · ASSET WORKBENCH</span><h1>{en?'Asset releases':'资产发布'}</h1><p>{en?'Current releases and assets, grouped by module.':'按模块查看当前版本与资产。'}</p></div><Link className="primary" navigate={navigate} href="/assets">{en?'Browse library':'浏览资产库'}<ArrowRight size={16}/></Link></header>
  <div className="home-stats">{[[data.stats.asset_count,en?'Assets':'资产'],[data.stats.gameplay_count,en?'Gameplay designs':'玩法设计'],[data.stats.bundle_count,en?'File bundles':'交付组'],[data.stats.file_count.toLocaleString(),en?'Indexed files':'索引文件']].map(([value,label])=><div key={label}><strong>{value}</strong><span>{label}</span></div>)}</div>
  <nav className="home-module-nav" aria-label={en?'Homepage modules':'首页模块'}><a href="#home-gameplay"><Gamepad2 size={16}/>{en?'Gameplay release':'玩法发布'}<span>1</span></a>{home.modules.map((m:Data)=>{const Icon=icons[m.id]||Box;return <a key={m.id} href={'#home-'+m.id}><Icon size={16}/>{m.title[locale]}<span>{m.cards.length}</span></a>})}</nav>
  <section className="home-module home-gameplay" id="home-gameplay" aria-labelledby="home-gameplay-title" data-home-module="gameplay">
   <div className="home-section-heading"><div><span className="home-section-number">01</span><h2 id="home-gameplay-title">{en?'Gameplay release':'玩法发布'}</h2></div><Link navigate={navigate} href="/gameplay">{en?'All gameplay designs':'全部玩法设计'}<ArrowRight size={15}/></Link></div>
   <article className="home-release" data-build-id={release.build_id}><Link navigate={navigate} href={release.href} className="home-release-picture" aria-label={en?'View current release':'查看当前正式版'}><Picture key={release.cover_id||'missing'} id={release.cover_id} snapshot={snapshot} alt={en?'Actual capture from the current tutorial release':'当前教学正式版游戏截图'} fit="contain" priority/>{release.cover_id&&<span>{en?'Actual release capture':'正式版游戏截图'}</span>}</Link>
    <div className="home-release-body"><span className="home-release-status"><span/>{en?'Formal release':'正式发布'}</span><h3>{release.title[locale]}</h3><p>{release.summary[locale]}</p><dl><div><dt>{en?'Version':'版本'}</dt><dd>{release.version}</dd></div><div><dt>{en?'Contents':'内容'}</dt><dd>{en?'Gameplay · teaching · UI · audio':'玩法 · 教学 · 界面 · 声音'}</dd></div></dl><div className="home-release-links"><Link className="primary" navigate={navigate} href={release.href}>{en?'View release':'查看发布版本'}<ArrowRight size={16}/></Link><Link navigate={navigate} href={release.gameplay_href}>{en?'Gameplay design':'玩法设计'}<FileText size={15}/></Link></div></div>
   </article>
  </section>
  {home.modules.map((module:Data,index:number)=><section key={module.id} className={'home-module home-'+module.id} id={'home-'+module.id} aria-labelledby={'home-title-'+module.id} data-home-module={module.id}>
   <div className="home-section-heading"><div><span className="home-section-number">{String(index+2).padStart(2,'0')}</span><h2 id={'home-title-'+module.id}>{module.title[locale]}</h2><span className="home-module-count">{module.cards.length}</span></div><Link navigate={navigate} href={module.href}>{en?'Browse category':'查看分类'}<ArrowRight size={15}/></Link></div><p className="home-section-description">{module.description[locale]}</p>
   <div className="home-card-grid">{module.cards.map((card:Data)=><Link key={card.id} navigate={navigate} href={card.href} className="home-asset-card" data-home-card={card.id} data-asset-id={card.asset_id}>
    <div className="home-card-picture"><Picture key={card.cover_id} id={card.cover_id} snapshot={snapshot} alt={card.title[locale]} fit={card.image_fit}/><span className="home-picture-label">{card.image_label[locale]}</span>{card.has_model&&module.id!=='actions'&&<span className="home-model-badge">3D</span>}</div>
    <div className="home-card-body"><div className="home-card-meta"><span className={'home-card-status '+card.status}>{status[card.status]}</span><ArrowRight size={17}/></div><h3>{card.title[locale]}</h3><p>{card.description[locale]}</p></div>
   </Link>)}</div>
  </section>)}
  <section className="home-archive" aria-label={en?'Build archive':'构建记录'}><div><h2>{en?'Build and review records':'构建与评审记录'}</h2><p>{en?'Trials, source builds and retained versions.':'试玩、来源构建与保留版本。'}</p></div><Link navigate={navigate} href="/builds">{en?'View all records':'查看全部记录'}<span>{data.builds.length}</span><ArrowRight size={16}/></Link><details><summary>{en?'Retained builds':'保留构建'}<span>{archive.length}</span></summary><div>{archive.map((b:Data)=><Link key={b.id} navigate={navigate} href={'/builds/'+b.id}><span>{tx(b.title)}</span><code>{b.revision}</code><ArrowRight size={14}/></Link>)}</div></details></section>
  <div className="home-snapshot">{en?'Snapshot':'快照'} <code>{snapshot.slice(0,12)}</code></div>
 </div>;
}
