import {test,expect} from '@playwright/test';
import {readFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
const root=resolve(process.cwd(),'../../..');
const state=resolve(root,'Assets/LocalWorking/AssetWorkbench');
const shots=resolve(state,'runs/equipment-history-retirement-20261017/screenshots');mkdirSync(shots,{recursive:true});
test.beforeEach(async({context})=>{
 const s=JSON.parse(readFileSync(resolve(state,'runtime/session.json'),'utf8'));
 expect((await context.request.post('/api/v1/session',{data:{token:s.token},headers:{Origin:`http://127.0.0.1:${s.port}`}})).ok()).toBeTruthy();
});

test('grenade, smoke and ammunition references show text, original figures and sources',async({page,context})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 for(const [asset,game,title] of [['frag-grenade','frag-throw','Mk II'],['smoke-grenade','smoke-cover','AN-M8'],['ammo-box','finite-supply','SM_AmmoBox_01a']]){
  const detail=(await(await context.request.get('/api/v1/assets/'+asset)).json()).data;
  expect(detail.historical_references).toHaveLength(3);
  const refs=detail.historical_references;const img=refs.find((r:any)=>r.kind==='image');
  expect(refs.every((r:any)=>r.links.length&&r.association.note.zh&&r.association.note.en)).toBeTruthy();
  await page.goto('/assets/'+asset);
  const section=page.locator('.reference-section');await expect(section.locator('.reference-thumb img')).toHaveCount(1);
  await expect(section).toContainText(title);await expect(section.locator('pre')).not.toBeEmpty();
  const image=section.locator('.reference-thumb img');await image.evaluate((i:HTMLImageElement)=>i.decode());
  expect(await image.evaluate((i:HTMLImageElement)=>i.naturalWidth)).toBeGreaterThan(200);
  await section.scrollIntoViewIfNeeded();await page.screenshot({path:resolve(shots,asset+'-zh.png')});
  await section.locator('.reference-thumb').click();const dialog=page.getByRole('dialog',{name:'参考图预览'});await expect(dialog).toBeVisible();
  await dialog.locator('img').evaluate((i:HTMLImageElement)=>i.decode());
  const original=await context.request.get((await dialog.getByRole('link',{name:'查看原图'}).getAttribute('href'))!);
  expect(original.ok()).toBeTruthy();expect(original.headers()['content-type']).toContain('image/png');
  await page.keyboard.press('Escape');
  await page.getByRole('button',{name:'English',exact:true}).click();await expect(section).toContainText('Reference text, images and sources');
  expect(await section.locator('a[href^="https://"]').count()).toBeGreaterThan(0);
  await section.scrollIntoViewIfNeeded();await page.screenshot({path:resolve(shots,asset+'-en.png')});
  await page.goto('/research/'+img.id);await expect(page.getByRole('heading',{name:'Linked gameplay design',exact:true})).toBeVisible();
  await page.goto('/gameplay/'+game);await expect(page.locator('.reference-section .reference-thumb img')).toHaveCount(1);
  await page.getByRole('button',{name:'中文',exact:true}).click();
 }
 expect(errors).toEqual([]);
});

test('current library excludes retired Normandy records and retains shared rifle files',async({page,context})=>{
 const rows=(await(await context.request.get('/api/v1/research')).json()).data.items;
 expect(rows).toHaveLength(67);expect(rows.every((r:any)=>['paris','equipment'].includes(r.scope))).toBeTruthy();
 expect(rows.some((r:any)=>r.kind==='motion'||r.kind==='weather')).toBeFalsy();
 await page.goto('/research');await expect(page.getByRole('button',{name:/诺曼底/})).toHaveCount(0);
 for(const bundle of ['gunplay-reference-assets','historical-reference-assets']){
  const files=(await(await context.request.get('/api/v1/files?bundle='+bundle+'&limit=200')).json()).data;
  const retired=JSON.parse(readFileSync(resolve(root,'Assets/Registry/library-scope.json'),'utf8')).retired_files.filter((r:any)=>r.bundle===bundle);
  const paths=new Set(files.items.map((r:any)=>r.path));expect(retired.every((r:any)=>!paths.has(r.path))).toBeTruthy();
  if(bundle==='gunplay-reference-assets'){expect(paths.size).toBe(5);expect([...paths].every((p:any)=>p.includes('/SourceAssets/'))).toBeTruthy();}
 }
 await page.goto('/builds');await expect(page.getByText('原清单',{exact:false}).first()).toBeVisible();
});
