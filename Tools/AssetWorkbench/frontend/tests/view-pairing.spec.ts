import {test,expect} from '@playwright/test';
import {readFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
import {buildViewPairs} from '../src/viewPairs';
const root=resolve(process.cwd(),'../../..'),state=resolve(root,'Assets/LocalWorking/AssetWorkbench');
const shots=resolve(state,'runs/view-pairing-20261017/screenshots');mkdirSync(shots,{recursive:true});
test.beforeEach(async({context})=>{
 const s=JSON.parse(readFileSync(resolve(state,'runtime/session.json'),'utf8'));
 expect((await context.request.post('/api/v1/session',{data:{token:s.token},headers:{Origin:`http://127.0.0.1:${s.port}`}})).ok()).toBeTruthy();
});
test('only stable subject and view keys pair; unknowns and ambiguous keys never pair',()=>{
 const v=(key:string,group='camera-a')=>({key,label:{zh:'正面',en:'Front'},camera_group:group});
 const pairs=buildViewPairs({media_ids:['a','unknown'],image_views:{a:v('asset:front')}},{media_ids:['b','unknown'],image_views:{b:v('asset:front')}});
 expect(pairs[0]).toMatchObject({left:'a',right:'b',cameraMatch:true});expect(pairs.slice(1)).toHaveLength(2);expect(pairs.slice(1).every(p=>!(p.left&&p.right))).toBeTruthy();
 const duplicate=buildViewPairs({media_ids:['a','b'],image_views:{a:v('asset:front'),b:v('asset:front')}},{media_ids:['c'],image_views:{c:v('asset:front')}});
 expect(duplicate.every(p=>!(p.left&&p.right))).toBeTruthy();
 expect(buildViewPairs({media_ids:['a'],image_views:{a:v('asset:front')}},{media_ids:['b'],image_views:{b:v('other-asset:front')}}).every(p=>!(p.left&&p.right))).toBeTruthy();
 expect(buildViewPairs({media_ids:['a'],image_views:{a:v('asset:front')}},{media_ids:['b'],image_views:{b:v('asset:front','different')}})[0].cameraMatch).toBeFalsy();
});
test('medical view switches from either side, missing views and unknown pictures remain explicit',async({page,context})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/compare?asset=medical-pouch');const view=page.getByLabel('对照视角',{exact:true}),left=page.locator('[data-paired-side="0"]'),right=page.locator('[data-paired-side="1"]');
 await expect(view).toHaveValue('view:medkit:hero');await expect(page.getByTestId('paired-controls')).toContainText('2 组配对');
 const img=async(side:any)=>{const node=side.locator('.version-main-image img');await node.evaluate((i:HTMLImageElement)=>i.decode());return node.getAttribute('src')};
 const first=await img(left);await right.getByRole('button',{name:'截图 2',exact:true}).click();await expect(view).toHaveValue('view:medkit:detail');expect(await img(left)).not.toBe(first);await expect(left.locator('.paired-view-label')).toContainText('前部细节');await expect(right.locator('.paired-view-label')).toContainText('前部细节');
 const original=await context.request.get((await right.getByRole('link',{name:'查看原图',exact:true}).getAttribute('href'))!);expect(original.ok()).toBeTruthy();
 const d=(await(await context.request.get('/api/v1/assets/medical-pouch/revisions')).json()).data,accepted=d.find((r:any)=>r.id==='medical-pouch-human-accepted-20261017');
 const selected=(await img(right))!.split('/media/')[1].split('?')[0];expect(createHash('sha256').update(await original.body()).digest('hex')).toBe(accepted.screenshots.find((s:any)=>s.id===selected).sha256);
 await view.selectOption('view:medkit:front');await expect(left.getByTestId('missing-view-0')).toContainText('无对应视角');await expect(left.locator('.version-main-image img')).toHaveCount(0);await img(right);
 await page.getByTestId('paired-controls').scrollIntoViewIfNeeded();await page.screenshot({path:resolve(shots,'medical-missing-front.jpg'),type:'jpeg',quality:72});
 const unknown=await view.locator('option').evaluateAll(nodes=>nodes.map((n:any)=>n.value).find(v=>v.startsWith('unknown:left:')));expect(unknown).toBeTruthy();await view.selectOption(unknown!);await expect(page.getByTestId('paired-controls')).toContainText('视角未登记');await img(left);await expect(right.getByTestId('missing-view-1')).toBeVisible();
 await view.selectOption('view:medkit:hero');await page.screenshot({path:resolve(shots,'medical-paired-hero-zh.jpg'),type:'jpeg',quality:72});
 await page.getByRole('button',{name:'English',exact:true}).click();await expect(page.getByLabel('Comparison view',{exact:true})).toHaveValue('view:medkit:hero');await expect(page.getByTestId('paired-controls')).toContainText('same camera parameters');
 await page.setViewportSize({width:1366,height:768});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 await page.setViewportSize({width:640,height:900});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();expect(errors).toEqual([]);
});
test('dual enlargement shares zoom, pan, reset and view selection; Escape restores focus',async({page})=>{
 await page.goto('/compare?asset=medical-pouch');const left=page.locator('[data-paired-side="0"]');const opener=left.getByRole('button',{name:'放大截图',exact:true});await opener.click();
 const dialog=page.getByRole('dialog',{name:'对照截图'});await expect(dialog).toBeVisible();const images=dialog.locator('.paired-pan-area img');await expect(images).toHaveCount(2);for(const i of await images.all())await i.evaluate((n:HTMLImageElement)=>n.decode());
 await dialog.getByRole('button',{name:'放大',exact:true}).click();await expect(dialog.locator('output')).toHaveText('150%');
 const transforms=()=>images.evaluateAll(nodes=>nodes.map(n=>(n as HTMLElement).style.transform));expect(await transforms()).toEqual(['translate(0px, 0px) scale(1.5)','translate(0px, 0px) scale(1.5)']);
 const area=dialog.getByTestId('paired-pan-1'),box=(await area.boundingBox())!;await page.mouse.move(box.x+box.width*.5,box.y+box.height*.5);await page.mouse.down();await page.mouse.move(box.x+box.width*.5+65,box.y+box.height*.5+24,{steps:5});await page.mouse.up();const moved=await transforms();expect(moved[0]).toBe(moved[1]);expect(moved[0]).toContain('65px, 24px');
 await dialog.getByRole('button',{name:'重置视图',exact:true}).click();await expect(dialog.locator('output')).toHaveText('100%');expect(await transforms()).toEqual(['translate(0px, 0px) scale(1)','translate(0px, 0px) scale(1)']);
 await dialog.getByLabel('放大视角',{exact:true}).selectOption('view:medkit:detail');await expect(page.getByLabel('对照视角',{exact:true})).toHaveValue('view:medkit:detail');await expect(images.first()).toHaveAttribute('alt','前部细节');
 await dialog.getByRole('button',{name:'放大',exact:true}).click();await page.screenshot({path:resolve(shots,'medical-dual-detail-zoom.jpg'),type:'jpeg',quality:74});
 await dialog.getByRole('button',{name:'关闭对照',exact:true}).focus();await page.keyboard.press('ArrowRight');await expect(page.getByLabel('对照视角',{exact:true})).toHaveValue('view:medkit:front');await expect(dialog.getByTestId('missing-view-0')).toBeVisible();await expect(dialog.locator('output')).toHaveText('100%');
 await page.keyboard.press('Escape');await expect(dialog).toHaveCount(0);
 // The selected front is absent on the left, so the original opener is unmounted.
 await page.getByLabel('对照视角',{exact:true}).selectOption('view:medkit:hero');await opener.click();await page.keyboard.press('Escape');await expect(opener).toBeFocused();
});
test('camera differences are labelled; native grip views never match runtime frames',async({page,context})=>{
 // Locate the authored original by registered view metadata, independent of list order.
 const med=(await(await context.request.get('/api/v1/assets/medical-pouch/revisions')).json()).data;
 const authored=med.find((r:any)=>Object.values(r.image_views||{}).some((v:any)=>v.camera_group==='medkit-authored-v0'));expect(authored).toBeTruthy();
 await page.goto('/compare?asset=medical-pouch&left='+authored.id+'&right=medical-pouch-human-accepted-20261017');
 await expect(page.locator('[data-version-id="'+authored.id+'"]')).toBeVisible();await page.getByLabel('对照视角',{exact:true}).selectOption('view:medkit:hero');await expect(page.getByTestId('paired-controls')).toContainText('相机参数不同或未核实');
 await page.goto('/compare?asset=frag-grenade');await expect(page.getByTestId('paired-controls')).toContainText('0 组配对');const selector=page.getByLabel('对照视角',{exact:true});
 const values=await selector.locator('option').evaluateAll(nodes=>nodes.map((n:any)=>n.value));const runtime=values.find(v=>v.startsWith('view:grip:runtime-fp:'));expect(runtime).toBeTruthy();await selector.selectOption(runtime!);await expect(page.locator('[data-paired-side="0"]').getByTestId('missing-view-0')).toBeVisible();await page.locator('[data-paired-side="1"] .version-main-image img').evaluate((i:HTMLImageElement)=>i.decode());
 await page.getByTestId('paired-controls').scrollIntoViewIfNeeded();await page.screenshot({path:resolve(shots,'grip-offline-vs-runtime-unpaired.jpg'),type:'jpeg',quality:72});
 const rows=(await(await context.request.get('/api/v1/assets/frag-grenade/revisions')).json()).data;const offline=rows.find((r:any)=>r.id.includes('web-polish')&&Object.keys(r.image_views||{}).length);expect(offline).toBeTruthy();await page.locator('.compare-controls select').nth(2).selectOption(offline.id);
 await expect(page.locator('[data-version-id="'+offline.id+'"]')).toBeVisible();
 const paired=(await page.getByLabel('对照视角',{exact:true}).locator('option').evaluateAll(nodes=>nodes.map((n:any)=>({value:n.value,text:n.textContent})))).find(v=>v.text.includes('相机参数一致'));expect(paired).toBeTruthy();await page.getByLabel('对照视角',{exact:true}).selectOption(paired!.value);await expect(page.locator('.paired-gallery .version-main-image img')).toHaveCount(2);
});
