import {test,expect} from '@playwright/test';
import {readFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
const root=resolve(process.cwd(),'../../..');
const state=resolve(root,'Assets/LocalWorking/AssetWorkbench');
const shots=resolve(state,'runs',process.env.AW_GRENADE_CAPTURE_DIR||'grenade-models-qa-v2');mkdirSync(shots,{recursive:true});
test.beforeEach(async({context})=>{
 const session=JSON.parse(readFileSync(resolve(state,'runtime/session.json'),'utf8'));
 expect((await context.request.post('/api/v1/session',{data:{token:session.token},headers:{Origin:`http://127.0.0.1:${session.port}`}})).ok()).toBeTruthy();
});
test('grenade 3D source models render, orbit, zoom and reset',async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 for(const id of ['frag-grenade','smoke-grenade']){
  await page.goto('/assets/'+id);const stage=page.getByTestId('model-viewport');
  await expect(stage).toHaveAttribute('data-status','ready');
  await expect(stage).toHaveAttribute('data-model',id+'-model-v1-20261011');
  await expect.poll(async()=>Number(await stage.getAttribute('data-meshes'))).toBeGreaterThan(0);
  await expect(page.getByText('静态模型 · 无内嵌动画',{exact:true})).toBeVisible();
  await stage.screenshot({path:resolve(shots,id+'-front.png')});
  const front=await stage.screenshot(),camera=await stage.getAttribute('data-camera'),box=(await stage.boundingBox())!;
  await page.mouse.move(box.x+box.width*.5,box.y+box.height*.5);await page.mouse.down();await page.mouse.move(box.x+box.width*.7,box.y+box.height*.5,{steps:12});await page.mouse.up();
  await expect.poll(()=>stage.getAttribute('data-camera')).not.toBe(camera);
  const turned=await stage.screenshot({path:resolve(shots,id+'-side.png')});expect(front.equals(turned)).toBeFalsy();
  const rotated=await stage.getAttribute('data-camera');await page.mouse.wheel(0,-160);await expect.poll(()=>stage.getAttribute('data-camera')).not.toBe(rotated);
  await page.getByRole('button',{name:'复位视角',exact:true}).click();
  await page.getByRole('button',{name:'English',exact:true}).click();await expect(page.getByText('Static model · No embedded animation',{exact:true})).toBeVisible();
  await page.getByRole('button',{name:'中文',exact:true}).click();
  await page.setViewportSize({width:1366,height:768});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  await page.screenshot({path:resolve(shots,id+'-detail-1366.png'),fullPage:true});
  await page.setViewportSize({width:1920,height:1080});
 }
 expect(errors).toEqual([]);
});
test('grenade versions, current formal use and refreshed reference index',async({page,context})=>{
 for(const id of ['frag-grenade','smoke-grenade']){
  const a=(await(await context.request.get('/api/v1/assets/'+id)).json()).data;
  expect(a.usage_status).toBe('formal');expect(a.models).toHaveLength(1);
  expect(a.preview_id).toBe(id+'-model-v1-browser-front');
  expect(a.usage.some((u:any)=>u.build_id==='equipment-input-review')).toBeTruthy();
  expect(a.usage.some((u:any)=>u.build_id==='formal')).toBeTruthy();
  const revisions=(await(await context.request.get('/api/v1/assets/'+id+'/revisions')).json()).data;
  const model=revisions.find((r:any)=>r.id===id+'-model-v1-20261011');
  const input=revisions.find((r:any)=>r.id===id+'-wheel-integration-v4-20261011');
  expect(input.parent_ids).toContain(model.id);expect(input.model_identity).toBe(model.model_identity);
  expect(model.model_identity).toBe(a.models[0].sha256);
  await page.goto('/assets/'+id);await expect(page.getByTestId('model-viewport')).toHaveAttribute('data-status','ready');
  await page.getByRole('button',{name:'版本与取舍',exact:true}).click();await expect(page.locator('.timeline')).toContainText('滚轮装备整合 v4');
  await page.getByRole('button',{name:'游戏使用',exact:true}).click();await expect(page.locator('.usage-row[data-build-id="formal"]').first()).toBeVisible();
  await page.getByRole('button',{name:'图片与音频',exact:true}).click();
  await expect(page.locator('.media-caption')).toContainText('模型 v1');
  await page.locator('.detail-media img').scrollIntoViewIfNeeded();await page.locator('.detail-media img').evaluate((i:HTMLImageElement)=>i.decode());
  for(const img of await page.locator('.media-thumbs img').all()){await img.scrollIntoViewIfNeeded();await img.evaluate((i:HTMLImageElement)=>i.decode())}
  await page.evaluate(()=>scrollTo(0,0));
  await page.screenshot({path:resolve(shots,id+'-usage.png'),fullPage:true});
  await page.getByRole('button',{name:'English',exact:true}).click();
  const untranslated=await page.locator('main').evaluate(el=>{const c=el.cloneNode(true) as HTMLElement;c.querySelector('.language-switch')?.remove();return c.innerText||c.textContent||''});
  expect(untranslated.match(/[\u3400-\u9fff]+/g)||[]).toEqual([]);
  await page.getByRole('button',{name:'中文',exact:true}).click();
 }
 const index=JSON.parse(readFileSync(resolve(root,'Assets/Registry/asset-index.json'),'utf8'));
 for(const id of ['frag-grenade','smoke-grenade'])expect(index.assets.find((a:any)=>a.id===id).revisions.some((r:any)=>r.id===id+'-wheel-integration-v4-20261011')).toBeTruthy();
});
