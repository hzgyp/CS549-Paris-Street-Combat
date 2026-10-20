import {test,expect} from '@playwright/test';
import {readFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
const root=resolve(process.cwd(),'../../..');
const state=resolve(root,'Assets/LocalWorking/AssetWorkbench');
const session=()=>JSON.parse(readFileSync(resolve(state,'runtime/session.json'),'utf8'));
const shots=resolve(state,'runs/gameplay-integration-20261013/screenshots');mkdirSync(shots,{recursive:true});

test.beforeEach(async({context})=>{
 const s=session();expect((await context.request.post('/api/v1/session',{data:{token:s.token},headers:{Origin:`http://127.0.0.1:${s.port}`}})).ok()).toBeTruthy();
});

test('bilingual design navigation, scope, figures, sources and asset links',async({page,context})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 const rows=(await(await context.request.get('/api/v1/gameplay')).json()).data.items;
 expect(rows).toHaveLength(14);
 const current=rows.find((g:any)=>g.id==='g1-current');
 const baseline=JSON.parse(readFileSync(resolve(root,'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json'),'utf8').replace(/^\uFEFF/,''));
 expect(current.implementation.game_sha256).toBe(baseline.game_sha256);
 expect(current.implementation.state).toBe('formal');
 expect(rows.find((g:any)=>g.id==='bridge-ab').validation.state).toBe('failed_fixed_routes');
 await page.goto('/gameplay');await expect(page.locator('.gameplay-card')).toHaveCount(14);
 await page.screenshot({path:resolve(shots,'gameplay-zh.png'),fullPage:true});
 await page.getByLabel('实现状态').selectOption('unimplemented');await expect(page.locator('.gameplay-card')).toHaveCount(5);
 await page.getByLabel('实现状态').selectOption('');
 await page.getByLabel('搜索玩法').fill('smoke-cover');await expect(page.locator('.gameplay-card')).toHaveCount(1);
 await page.goto('/gameplay/g1-tutorial');
 await expect(page.getByText('未实现',{exact:true})).toBeVisible();
 await expect(page.locator('.gameplay-section ol li')).toHaveCount(9);
 for(const img of await page.locator('.gameplay-figures img').all())await img.evaluate((i:HTMLImageElement)=>i.decode());
 await page.getByRole('button',{name:'English',exact:true}).click();
 await expect(page.getByText('Not implemented',{exact:true})).toBeVisible();
 const text=await page.locator('main').evaluate(el=>{const copy=el.cloneNode(true) as HTMLElement;copy.querySelector('.language-switch')?.remove();return copy.innerText||copy.textContent||''});expect(text.match(/[\u3400-\u9fff]+/g)||[]).toEqual([]);
 await page.screenshot({path:resolve(shots,'tutorial-en.png'),fullPage:true});
 await page.locator('.gameplay-section .source-row button').first().click();await expect(page.locator('.source-modal pre')).toContainText('巴黎过桥教程');await page.keyboard.press('Escape');
 await page.goto('/gameplay/postbridge-routes');await expect(page.locator('tbody tr')).toHaveCount(9);
 await expect(page.getByText('Survey links only',{exact:true})).toBeVisible();
 await page.goto('/gameplay/smoke-cover');await page.locator('.gameplay-assets button').filter({hasText:'Smoke Grenade'}).click();
 await expect(page.getByTestId('model-viewport')).toHaveAttribute('data-status','ready');
 await expect(page.getByRole('heading',{name:'Linked gameplay design',exact:true})).toBeVisible();
 await page.goto('/gameplay/allied-recruitment');await expect(page.getByText('Not implemented',{exact:true})).toBeVisible();await expect(page.locator('main')).toContainText('finite');
 for(const img of await page.locator('.gameplay-figures img').all())await img.evaluate((i:HTMLImageElement)=>i.decode());
 await page.setViewportSize({width:1280,height:900});await page.goto('/gameplay');await expect(page.locator('.gameplay-card')).toHaveCount(14);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 await page.screenshot({path:resolve(shots,'gameplay-en-1280.png'),fullPage:true});
 expect(errors).toEqual([]);
});

test('public HTTP refresh publishes all three navigation outputs',async({page,context})=>{
 const s=session();test.skip(!s.external_origin,'No public origin configured');
 const share=readFileSync(resolve(state,'runtime/public-share-link.txt'),'utf8').trim();
 await page.goto(share);await expect(page.getByRole('heading',{name:'资产总览',exact:true})).toBeVisible();
 const old=(await(await context.request.get(s.external_origin+'/api/v1/health')).json()).snapshot_id;
 await page.getByRole('button',{name:'刷新索引',exact:true}).click();
 await expect.poll(async()=>(await(await context.request.get(s.external_origin+'/api/v1/health')).json()).snapshot_id,{timeout:50000}).not.toBe(old);
 await expect(page.getByText('平台与资料索引已同步',{exact:true})).toBeVisible();
 const index=JSON.parse(readFileSync(resolve(root,'Assets/Registry/asset-index.json'),'utf8'));
 expect(index.asset_count).toBe(229);expect(index.gameplay_count).toBe(14);
 expect(readFileSync(resolve(root,'Assets/Registry/GAMEPLAY_DIRECTORY.md'),'utf8')).toContain('bridge-ab');
 const health=await(await context.request.get(s.external_origin+'/api/v1/health')).json();
 const job=health.jobs.find((j:any)=>j.snapshot_id===health.snapshot_id);
 expect(job.status).toBe('succeeded');
 expect(job.navigation_index.files).toHaveLength(3);
});
