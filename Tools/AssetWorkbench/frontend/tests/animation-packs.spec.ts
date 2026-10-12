import {test,expect} from '@playwright/test';
import {readFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
const state=resolve(process.cwd(),'../../../Assets/LocalWorking/AssetWorkbench');
const shots=resolve(state,'runs/animation-packs-v2');mkdirSync(shots,{recursive:true});
const packs=()=>Object.values(JSON.parse(readFileSync(resolve(state,'private-records/animation-packs.json'),'utf8')).packs) as any[];
test.beforeEach(async({context})=>{
 const s=JSON.parse(readFileSync(resolve(state,'runtime/session.json'),'utf8'));
 expect((await context.request.post('/api/v1/session',{data:{token:s.token},headers:{Origin:`http://127.0.0.1:${s.port}`}})).ok()).toBeTruthy();
});
test('every package opens its own real animation in WebGL',async({page})=>{
 test.setTimeout(480000);const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 for(const pack of packs()){
  await page.goto('/assets/'+pack.id);const stage=page.getByTestId('model-viewport');
  await expect(stage).toHaveAttribute('data-status','ready',{timeout:60000});
  await expect(stage).toHaveAttribute('data-model','animation-'+pack.default_clip);
  await expect.poll(async()=>Number(await stage.getAttribute('data-meshes'))).toBeGreaterThan(0);
  await expect(page.getByLabel('选择包内动作')).toHaveValue(pack.default_clip);
  await expect(page.getByLabel('选择包内动作').locator('option')).toHaveCount(pack.clips.length);
  await page.getByLabel('动画时间',{exact:true}).click();
  await stage.screenshot({path:resolve(shots,pack.id+'.png')});
 }
 expect(errors).toEqual([]);
});
test('uncached native action preparation, selection, play controls and camera',async({page,context})=>{
 test.setTimeout(240000);const pack=packs().find(x=>x.id==='anim-rifle-animset-pro');
 const target=pack.clips.find((x:any)=>x.name==='Rifle_WalkFwdLoop')||pack.clips.find((x:any)=>/WalkFwdLoop/.test(x.name));expect(target).toBeTruthy();
 await page.goto('/assets/'+pack.id);const stage=page.getByTestId('model-viewport');await expect(stage).toHaveAttribute('data-status','ready');
 await page.getByLabel('搜索动作').fill('WalkFwdLoop');await page.getByLabel('选择包内动作').selectOption(target.id);
 await expect(stage).toHaveAttribute('data-status','ready',{timeout:180000});await expect(stage).toHaveAttribute('data-model','animation-'+target.id);
 const before=await stage.screenshot();await page.getByRole('button',{name:'播放',exact:true}).click();await expect.poll(async()=>Number(await stage.getAttribute('data-animation-time'))).toBeGreaterThan(.15);
 await page.getByRole('button',{name:'暂停',exact:true}).click();const paused=await stage.getAttribute('data-animation-time');await page.waitForTimeout(200);expect(await stage.getAttribute('data-animation-time')).toBe(paused);
 const after=await stage.screenshot({path:resolve(shots,'rifle-walk.png')});expect(before.equals(after)).toBeFalsy();
 const camera=await stage.getAttribute('data-camera'),box=(await stage.boundingBox())!;
 await page.mouse.move(box.x+box.width*.5,box.y+box.height*.5);await page.mouse.down();await page.mouse.move(box.x+box.width*.65,box.y+box.height*.6,{steps:10});await page.mouse.up();await expect.poll(()=>stage.getAttribute('data-camera')).not.toBe(camera);
 const rotated=await stage.getAttribute('data-camera');await page.mouse.wheel(0,-200);await expect.poll(()=>stage.getAttribute('data-camera')).not.toBe(rotated);
 await page.getByLabel('播放速度').selectOption('2');await page.getByRole('button',{name:'English',exact:true}).click();await expect(page.getByLabel('Select package animation')).toHaveValue(target.id);
 await page.getByLabel('Search animations').fill('');await page.getByLabel('Select package animation').selectOption(pack.default_clip);await expect(stage).toHaveAttribute('data-model','animation-'+pack.default_clip);
 await page.getByLabel('Select package animation').selectOption(target.id);await expect(stage).toHaveAttribute('data-model','animation-'+target.id,{timeout:10000});
 const status=await(await context.request.get(`/api/v1/animation-packs/${pack.id}/clips/${target.id}`)).json();expect(status.status).toBe('ready');
 await page.screenshot({path:resolve(shots,'pack-en.png'),fullPage:true});
});
test('dependency mannequin and knife actions render across the timeline',async({page})=>{
 const cases=JSON.parse(readFileSync(resolve(state,'runs/animation-packs/lazy-checks.json'),'utf8'));
 const folder=resolve(shots,'additional-actions');mkdirSync(folder,{recursive:true});
 for(const item of cases){
  await page.goto('/assets/'+item.asset_id);const stage=page.getByTestId('model-viewport');
  await expect(stage).toHaveAttribute('data-status','ready');
  await page.getByLabel('选择包内动作').selectOption(item.clip.id);
  await expect(stage).toHaveAttribute('data-model','animation-'+item.clip.id);
  const slider=page.getByLabel('动画时间',{exact:true}),box=(await slider.boundingBox())!;
  const frames:Buffer[]=[];
  for(const fraction of [.1,.5,.9]){
   await slider.click({position:{x:box.width*fraction,y:box.height/2}});
   frames.push(await stage.screenshot({path:resolve(folder,item.asset_id+'-'+fraction+'.png')}));
  }
  expect(frames[0].equals(frames[2])).toBeFalsy();
 }
});
