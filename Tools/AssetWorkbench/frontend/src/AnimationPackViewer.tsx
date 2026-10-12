import {useEffect,useState} from 'react';
import {ModelViewer} from './ModelViewer';
import {useLocale} from './i18n';
type Data=Record<string,any>;
export function AnimationPackViewer({pack,snapshot,csrf}:{pack:string;snapshot:string;csrf:string}){
 const {locale}=useLocale(),t=(zh:string,en:string)=>locale==='zh'?zh:en;
 const [directory,setDirectory]=useState<Data|null>(null),[selected,setSelected]=useState(''),[q,setQ]=useState(''),[result,setResult]=useState<Data|null>(null),[error,setError]=useState(''),[attempt,setAttempt]=useState(0);
 useEffect(()=>{const abort=new AbortController();setDirectory(null);setSelected('');setQ('');setError('');
  fetch('/api/v1/animation-packs/'+pack,{signal:abort.signal}).then(async r=>{const d=await r.json();if(!r.ok)throw Error(d.code);return d}).then(d=>{setDirectory(d);setSelected(d.default_clip)}).catch(e=>{if(e.name!=='AbortError')setError(e.message)});return()=>abort.abort();
 },[pack]);
 useEffect(()=>{
  if(!selected)return;let dead=false,retryOnce=attempt>0,timer:ReturnType<typeof setTimeout>;const abort=new AbortController();setResult(null);setError('');
  const url='/api/v1/animation-packs/'+pack+'/clips/'+selected;
  async function poll(){
   try{
    let response=await fetch(url,{signal:abort.signal});let data=await response.json();if(!response.ok)throw Error(data.code);
    if(data.status==='uncached'||(data.status==='failed'&&retryOnce)){
     response=await fetch(url+'/prepare'+(retryOnce?'?retry=true':''),{method:'POST',headers:{'x-csrf-token':csrf},signal:abort.signal});data=await response.json();
     if(response.status!==409)retryOnce=false;
     if(response.status===409&&data.code==='ANIMATION_BUSY')data={status:'preparing',phase:'waiting'};
     else if(!response.ok)throw Error(data.code);
    }
    if(dead)return;setResult(data);
    if(data.status==='preparing')timer=setTimeout(poll,1500);
   }catch(e){if(!dead&&(e as Error).name!=='AbortError')setError((e as Error).message)}
  }
  poll();return()=>{dead=true;abort.abort();clearTimeout(timer)};
 },[pack,selected,attempt,csrf]);
 const filtered=directory?.clips.filter((c:Data)=>(c.name+' '+c.path).toLowerCase().includes(q.toLowerCase()))||[];
 const current=directory?.clips.find((c:Data)=>c.id===selected);
 const errorCode=error||result?.code;
 const errorText:Data={NO_COMPATIBLE_PACKAGE_MESH:t('包内缺少匹配骨架的预览模型。','No package mesh matches this skeleton.'),SOURCE_LOAD_FAILED:t('原生动作或依赖无法加载。','The native animation or a dependency could not be loaded.'),SOURCE_CHANGED:t('来源文件已变化，需重新登记。','Source files changed. Re-register before preparing.'),GLB_VALIDATION_FAILED:t('浏览器动画转换验证未通过。','Browser animation validation failed.')};
 return <section className="animation-pack" aria-label={t('动画包预览','Animation pack preview')}>
  <div className="animation-pack-picker"><label>{t('包内动作','Package animations')} · {directory?.clips.length||0}<input aria-label={t('搜索动作','Search animations')} placeholder={t('按名称或路径搜索','Search name or path')} value={q} onChange={e=>setQ(e.target.value)}/></label>
   <select aria-label={t('选择包内动作','Select package animation')} value={selected} onChange={e=>{setSelected(e.target.value);setAttempt(0)}} disabled={!directory}>
    {current&&!filtered.some((c:Data)=>c.id===selected)&&<option value={selected}>{current.name} ({t('当前','Current')})</option>}
    {filtered.map((c:Data)=><option key={c.id} value={c.id}>{c.path.split('/').slice(-3).join('/').split('.')[0]}</option>)}
   </select><small>{filtered.length} {t('个匹配动作','matching animations')}</small>
  </div>
  {result?.status==='ready'&&result.clip_id===selected?<ModelViewer key={selected} models={[result.model]} snapshot={snapshot}/>:<div className="animation-pack-status" role="status">
   {error||result?.status==='failed'?<><strong>{t('动作准备失败','Animation preparation failed')}</strong><span>{errorText[errorCode]||errorCode}</span><button className="secondary" onClick={()=>setAttempt(x=>x+1)}>{t('重试','Retry')}</button></>:<><strong>{result?.phase==='waiting'?t('等待其他动作准备完成…','Waiting for another animation…'):result?.phase==='convert'?t('正在转换并检查动画…','Converting and checking animation…'):t('正在准备动作…','Preparing animation…')}</strong><span>{t('首次选择需在本机转换，完成后缓存。','First use requires local conversion. The result is cached.')}</span></>}
  </div>}
  {current&&<div className="animation-pack-source"><code>{current.path}</code></div>}
 </section>;
}
