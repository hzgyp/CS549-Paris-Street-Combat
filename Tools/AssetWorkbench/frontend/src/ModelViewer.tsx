import {useEffect,useRef,useState} from 'react';
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import {useLocale} from './i18n';

type RecordData=Record<string,any>;
type View={renderer:THREE.WebGLRenderer;scene:THREE.Scene;camera:THREE.PerspectiveCamera;controls:OrbitControls;model?:THREE.Group;mixer?:THREE.AnimationMixer;clips:THREE.AnimationClip[];action?:THREE.AnimationAction;playing:boolean;speed:number;reset:()=>void};
export function ModelViewer({models,snapshot}:{models:RecordData[];snapshot:string}){
 const {locale}=useLocale();const t=(zh:string,en:string)=>locale==='zh'?zh:en;
 const host=useRef<HTMLDivElement>(null),view=useRef<View|null>(null);
 const [selected,setSelected]=useState(models[0]?.id||''),[status,setStatus]=useState('loading'),[error,setError]=useState(''),[clips,setClips]=useState<THREE.AnimationClip[]>([]),[clip,setClip]=useState(''),[playing,setPlaying]=useState(false),[time,setTime]=useState(0),[speed,setSpeed]=useState(1),[wire,setWire]=useState(false);
 const m=models.find(x=>x.id===selected)||models[0];
 useEffect(()=>{
  if(!host.current||!m)return;const el=host.current;let dead=false,frame=0,last=performance.now(),lastUi=0,visible=true;
  const abort=new AbortController();setStatus('loading');setError('');setClips([]);setClip('');setTime(0);setPlaying(false);setWire(false);setSpeed(1);
  let renderer:THREE.WebGLRenderer;
  try{renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,preserveDrawingBuffer:true});}
  catch{setStatus('error');setError(t('当前浏览器无法启用 WebGL。','WebGL is unavailable in this browser.'));return;}
  const packPreview=Boolean(m.file_url);
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=packPreview?.75:1;
  el.appendChild(renderer.domElement);renderer.domElement.setAttribute('aria-label','3D viewport');renderer.domElement.tabIndex=0;
  const scene=new THREE.Scene();scene.background=new THREE.Color('#dce0d9');
  const envScene=new RoomEnvironment();const pmrem=new THREE.PMREMGenerator(renderer);const environment=pmrem.fromScene(envScene,.04);scene.environment=environment.texture;pmrem.dispose();envScene.dispose();
  scene.environmentIntensity=packPreview?.35:1;
  scene.add(new THREE.HemisphereLight(0xffffff,0x687367,packPreview?.55:2));const light=new THREE.DirectionalLight(0xffffff,packPreview?1.5:2.3);light.position.set(3,5,4);scene.add(light);
  const camera=new THREE.PerspectiveCamera(35,1,.001,10000);camera.position.set(2,1,3);
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.09;controls.screenSpacePanning=true;
  const v:View={renderer,scene,camera,controls,clips:[],playing:false,speed:1,reset:()=>{}};view.current=v;
  let followCenter:THREE.Vector3|undefined,fitRadius=0;
  const modelBounds=()=>{v.model!.updateMatrixWorld(true);v.model!.traverse(o=>{if(o instanceof THREE.SkinnedMesh)o.skeleton.update()});return new THREE.Box3().setFromObject(v.model!,true)};
  const resize=()=>{const width=el.clientWidth,height=el.clientHeight;renderer.setSize(width,height,false);camera.aspect=width/Math.max(height,1);camera.updateProjectionMatrix();};
  const ro=new ResizeObserver(resize);ro.observe(el);resize();
  const io=new IntersectionObserver(([e])=>{visible=e.isIntersecting});io.observe(el);
  const contextLost=(e:Event)=>{e.preventDefault();v.playing=false;setPlaying(false);setStatus('error');setError(t('3D 上下文已中断，请重新加载页面。','3D context lost. Reload the page.'));};renderer.domElement.addEventListener('webglcontextlost',contextLost);
  const animate=(now:number)=>{
   if(dead)return;frame=requestAnimationFrame(animate);const dt=Math.min((now-last)/1000,.05);last=now;
   if(!visible||document.hidden)return;
   if(v.playing&&v.mixer)v.mixer.update(dt*v.speed);
   // Translate camera and orbit target together so native root motion stays visible,
   // while preserving the user's rotation, zoom and pan offset.
   if(packPreview&&v.model&&followCenter){const center=modelBounds().getCenter(new THREE.Vector3()),delta=center.clone().sub(followCenter);camera.position.add(delta);controls.target.add(delta);followCenter.copy(center)}
   controls.update();renderer.render(scene,camera);
   el.dataset.meshes=String(renderer.info.memory.geometries);
   if(v.action&&now-lastUi>100){setTime(v.action.time);lastUi=now}
   el.dataset.camera=camera.position.toArray().map(x=>x.toFixed(4)).join(',');
   el.dataset.animationTime=v.action?.time.toFixed(4)||'0';
  };frame=requestAnimationFrame(animate);
  const disposeModel=(model:THREE.Object3D)=>{
   const geometries=new Set<THREE.BufferGeometry>(),materials=new Set<THREE.Material>(),textures=new Set<THREE.Texture>();
   model.traverse(o=>{if(o instanceof THREE.Mesh){geometries.add(o.geometry);(Array.isArray(o.material)?o.material:[o.material]).forEach(mat=>{materials.add(mat);Object.values(mat).forEach(value=>{if(value instanceof THREE.Texture)textures.add(value)})})}if(o instanceof THREE.SkinnedMesh)o.skeleton.dispose()});
   textures.forEach(texture=>{const data=texture.source?.data;if(typeof ImageBitmap!=='undefined'&&data instanceof ImageBitmap)data.close();texture.dispose()});materials.forEach(mat=>mat.dispose());geometries.forEach(g=>g.dispose());
  };
  (async()=>{
   try{
    const response=await fetch(m.file_url||('/api/v1/models/'+m.id+'/file?snapshot_id='+snapshot),{signal:abort.signal});
    if(!response.ok){const e=await response.json();throw new Error(e.code||'MODEL_UNAVAILABLE')}
    const buffer=await response.arrayBuffer();if(dead)return;
    const manager=new THREE.LoadingManager();manager.setURLModifier(url=>{if(!url.startsWith('blob:'))throw new Error('EXTERNAL_RESOURCE_REJECTED');return url});
    const gltf=await new GLTFLoader(manager).parseAsync(buffer,'');
    if(dead){disposeModel(gltf.scene);return}
    v.model=gltf.scene;scene.add(v.model);v.clips=gltf.animations;if(m.file_url&&v.clips.length===1)v.clips[0].name=m.label;v.mixer=new THREE.AnimationMixer(v.model);
    // Fit the actual skinned bounds. This also handles centimeter-authored static GLBs.
    v.reset=()=>{const box=modelBounds(),center=box.getCenter(new THREE.Vector3()),extent=box.getSize(new THREE.Vector3());
     const radius=Math.max(extent.length()*.5,fitRadius,.01),halfFov=Math.atan(Math.tan(THREE.MathUtils.degToRad(camera.fov*.5))*Math.min(camera.aspect,1)),distance=radius/Math.sin(halfFov)*1.12;
     controls.enableDamping=false;controls.update();camera.near=Math.max(radius/1000,.00001);camera.far=radius*200;controls.minDistance=radius*.08;controls.maxDistance=radius*30;controls.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(1,.45,1.6).normalize().multiplyScalar(distance));camera.updateProjectionMatrix();controls.update();controls.enableDamping=true};
    setClips(v.clips);setStatus('ready');el.dataset.meshes=String(renderer.info.memory.geometries);el.dataset.model=m.id;
    if(v.clips.length){const c=v.clips[0];v.action=v.mixer.clipAction(c);v.action.play();v.action.paused=true;v.mixer.update(0);setClip(c.name)}
    if(packPreview&&v.action){for(let i=0;i<=8;i++){v.action.time=v.clips[0].duration*i/8;v.mixer.update(0);fitRadius=Math.max(fitRadius,modelBounds().getSize(new THREE.Vector3()).length()*.5)}v.action.time=0;v.mixer.update(0)}
    v.reset();
    if(packPreview)followCenter=modelBounds().getCenter(new THREE.Vector3());
   }catch(e){if(!dead&&(e as Error).name!=='AbortError'){setStatus('error');setError((e as Error).message)}}
  })();
  return()=>{dead=true;abort.abort();cancelAnimationFrame(frame);ro.disconnect();io.disconnect();controls.dispose();if(v.mixer){v.mixer.stopAllAction();if(v.model)v.mixer.uncacheRoot(v.model)}if(v.model)disposeModel(v.model);environment.dispose();renderer.domElement.removeEventListener('webglcontextlost',contextLost);renderer.dispose();renderer.forceContextLoss();renderer.domElement.remove();if(view.current===v)view.current=null;};
 },[m?.id,snapshot]);
 const duration=clips.find(c=>c.name===clip)?.duration||0;
 function choose(name:string){const v=view.current;if(!v?.mixer)return;v.mixer.stopAllAction();const c=v.clips.find(c=>c.name===name);if(!c)return;v.action=v.mixer.clipAction(c);v.action.reset().play();v.action.paused=!v.playing;v.mixer.update(0);setClip(name);setTime(0)}
 function toggle(){const v=view.current;if(!v?.action)return;v.playing=!v.playing;v.action.paused=!v.playing;setPlaying(v.playing)}
 function seek(value:number){const v=view.current;if(!v?.mixer||!v.action)return;v.action.time=value;v.mixer.update(0);setTime(value)}
 function wireframe(){const value=!wire;setWire(value);view.current?.model?.traverse(o=>{if(o instanceof THREE.Mesh)(Array.isArray(o.material)?o.material:[o.material]).forEach(mat=>{if('wireframe' in mat)(mat as THREE.MeshStandardMaterial).wireframe=value})})}
 return <section className="viewer3d" aria-label={t('3D 模型预览','3D model preview')}>
  <div className="viewer3d-bar"><strong>{t('3D 预览','3D preview')}</strong>{models.length>1&&<select aria-label={t('模型版本','Model version')} value={m.id} onChange={e=>setSelected(e.target.value)}>{models.map(x=><option key={x.id} value={x.id}>{locale==='zh'?x.label:x.label_en}</option>)}</select>}<button className="secondary" onClick={()=>view.current?.reset()} disabled={status!=='ready'}>{t('复位视角','Reset view')}</button><button className={'secondary '+(wire?'selected':'')} aria-pressed={wire} onClick={wireframe} disabled={status!=='ready'}>{t('线框','Wireframe')}</button></div>
  <div className="viewer3d-stage" ref={host} data-status={status} data-testid="model-viewport">{status!=='ready'&&<div className="viewer3d-overlay" role="status">{status==='loading'?t('正在加载模型…','Loading model…'):t('模型加载失败：','Model loading failed: ')+error}</div>}</div>
  <div className="viewer3d-controls">{clips.length>0?<><select aria-label={t('动画','Animation')} value={clip} onChange={e=>choose(e.target.value)}>{clips.map(c=><option key={c.name} value={c.name}>{c.name}</option>)}</select><button className="primary" onClick={toggle}>{playing?t('暂停','Pause'):t('播放','Play')}</button><input aria-label={t('动画时间','Animation time')} type="range" min={0} max={duration} step={.001} value={Math.min(time,duration)} onChange={e=>seek(Number(e.target.value))}/><output>{time.toFixed(2)} / {duration.toFixed(2)} s</output><select aria-label={t('播放速度','Playback speed')} value={speed} onChange={e=>{const value=Number(e.target.value);setSpeed(value);if(view.current)view.current.speed=value}}>{[.25,.5,1,1.5,2].map(x=><option key={x} value={x}>{x}×</option>)}</select></>:status==='ready'?<span>{t('静态模型 · 无内嵌动画','Static model · No embedded animation')}</span>:null}</div>
  <div className="viewer3d-note"><span>{t('左键旋转 · 滚轮缩放 · 右键平移','Left drag: orbit · Wheel: zoom · Right drag: pan')}</span><span>{locale==='zh'?m.scope:m.scope_en}</span><code>{m.revision} · SHA {m.sha256.slice(0,12)}</code></div>
 </section>;
}
