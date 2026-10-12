import {test,expect} from '@playwright/test';
import {readFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
const state=resolve(process.cwd(),'../../../Assets/LocalWorking/AssetWorkbench');
const shots=resolve(state,'runs/viewer3d');mkdirSync(shots,{recursive:true});
test.beforeEach(async({context})=>{
 const s=JSON.parse(readFileSync(resolve(state,'runtime/session.json'),'utf8'));
 expect((await context.request.post('/api/v1/session',{data:{token:s.token},headers:{Origin:`http://127.0.0.1:${s.port}`}})).ok()).toBeTruthy();
});
test('current model WebGL previews, orbit, zoom, pan, reset and static model state',async({page})=>{
 test.setTimeout(180000);const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 for(const id of ['pressure-mine','german-rifle']){
  await page.goto('/assets/'+id);const stage=page.getByTestId('model-viewport');
  await expect(stage).toHaveAttribute('data-status','ready',{timeout:90000});
  await expect.poll(async()=>Number(await stage.getAttribute('data-meshes'))).toBeGreaterThan(0);
  const original=await stage.getAttribute('data-camera'),box=(await stage.boundingBox())!;
  await page.mouse.move(box.x+box.width/2,box.y+box.height/2);await page.mouse.down();await page.mouse.move(box.x+box.width*.7,box.y+box.height*.6,{steps:12});await page.mouse.up();
  await expect.poll(()=>stage.getAttribute('data-camera')).not.toBe(original);
  const rotated=await stage.getAttribute('data-camera');await page.mouse.wheel(0,-250);await expect.poll(()=>stage.getAttribute('data-camera')).not.toBe(rotated);
  await page.getByRole('button',{name:'复位视角'}).click();
  await expect.poll(()=>stage.getAttribute('data-camera')).toBe(original);
  await page.mouse.move(box.x+box.width/2,box.y+box.height/2);await page.mouse.down({button:'right'});await page.mouse.move(box.x+box.width*.6,box.y+box.height*.6,{steps:8});await page.mouse.up({button:'right'});
  await expect.poll(()=>stage.getAttribute('data-camera')).not.toBe(original);await page.getByRole('button',{name:'复位视角'}).click();await expect.poll(()=>stage.getAttribute('data-camera')).toBe(original);
  await page.getByRole('button',{name:'线框',exact:true}).click();await expect(page.getByRole('button',{name:'线框',exact:true})).toHaveAttribute('aria-pressed','true');await page.getByRole('button',{name:'线框',exact:true}).click();
  await expect(page.getByText('静态模型 · 无内嵌动画')).toBeVisible();
  await stage.screenshot({path:resolve(shots,id+'.png')});
 }
 await page.setViewportSize({width:1366,height:768});await expect(page.getByTestId('model-viewport')).toBeVisible();expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();await page.screenshot({path:resolve(shots,'viewer-1366.png'),fullPage:true});
 expect(errors).toEqual([]);
});
test('real skeleton clips, seek, play, pause, speed, bilingual controls and asset switching',async({page})=>{
 test.setTimeout(240000);const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 for(const id of ['german-soldier','allied-soldier','first-person']){
  await page.goto('/assets/'+id);const stage=page.getByTestId('model-viewport');await expect(stage).toHaveAttribute('data-status','ready',{timeout:90000});
  await expect(page.getByLabel('动画',{exact:true}).locator('option')).toHaveCount(7);
  await page.getByLabel('动画',{exact:true}).selectOption('Rifle_Reload_2');
  const still=await stage.screenshot({path:resolve(shots,id+'-reload-start.png')});
  await page.getByLabel('动画时间',{exact:true}).click();await expect.poll(async()=>Number(await stage.getAttribute('data-animation-time'))).toBeGreaterThan(.8);
  const moved=await stage.screenshot({path:resolve(shots,id+'-reload-mid.png')});expect(still.equals(moved)).toBeFalsy();
  await page.getByRole('button',{name:'播放',exact:true}).click();await expect.poll(async()=>Number(await stage.getAttribute('data-animation-time'))).toBeGreaterThan(1.05);
  await page.getByRole('button',{name:'暂停',exact:true}).click();const paused=await stage.getAttribute('data-animation-time');await page.waitForTimeout(300);expect(await stage.getAttribute('data-animation-time')).toBe(paused);
  await page.getByLabel('播放速度').selectOption('2');await expect(page.getByLabel('播放速度')).toHaveValue('2');
  await page.getByLabel('动画',{exact:true}).selectOption('Rifle_Death_3');await page.getByLabel('动画时间',{exact:true}).focus();await page.keyboard.press('End');await page.getByRole('button',{name:'复位视角'}).click();await stage.screenshot({path:resolve(shots,id+'-death.png')});
  await page.getByLabel('动画',{exact:true}).selectOption('Rifle_Idle');await page.getByRole('button',{name:'复位视角'}).click();
  await page.screenshot({path:resolve(shots,id+'-page.png'),fullPage:true});
 }
 await page.getByRole('button',{name:'English',exact:true}).click();await expect(page.getByLabel('Animation',{exact:true})).toBeVisible();await expect(page.getByRole('button',{name:'Play',exact:true})).toBeVisible();
 await page.getByLabel('Model version').selectOption('m1-garand-browser-v3');await expect(page.getByTestId('model-viewport')).toHaveAttribute('data-status','ready',{timeout:60000});await expect(page.getByText('Static model · No embedded animation')).toBeVisible();await page.getByTestId('model-viewport').screenshot({path:resolve(shots,'m1-garand.png')});
 await page.getByRole('button',{name:'Images & audio',exact:true}).click();await expect(page.locator('.viewer3d canvas')).toHaveCount(0);
 expect(errors).toEqual([]);
});
