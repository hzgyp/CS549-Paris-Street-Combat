import {test,expect} from '@playwright/test';
import {readFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
const root=resolve(process.cwd(),'../../..');
const state=resolve(root,'Assets/LocalWorking/AssetWorkbench');
const session=()=>JSON.parse(readFileSync(resolve(state,'runtime/session.json'),'utf8'));
const shots=resolve(state,'runs/history-library-20261017/screenshots');mkdirSync(shots,{recursive:true});

test.beforeEach(async({context})=>{
 const s=session();expect((await context.request.post('/api/v1/session',{data:{token:s.token},headers:{Origin:`http://127.0.0.1:${s.port}`}})).ok()).toBeTruthy();
});

test('historical text, scoped gallery, original image, bilingual navigation and global search',async({page,context})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 const rows=(await (await context.request.get('/api/v1/research')).json()).data.items;
 expect(rows).toHaveLength(67);expect(rows.every((r:any)=>['paris','equipment'].includes(r.scope))).toBeTruthy();
 await page.goto('/research');await expect(page.getByRole('heading',{name:'历史资料',exact:true})).toBeVisible();
 await expect(page.locator('.list-summary')).toContainText(String(rows.length));
 await page.getByLabel('搜索历史资料').fill('街垒');
 // Search original text, not only card headings.
 await expect(page.locator('.research-card').first()).toBeVisible();
 await page.getByLabel('搜索历史资料').fill('');await page.getByLabel('资料类型').selectOption('image');
 await page.getByRole('button',{name:'巴黎 · 1944',exact:true}).click();
 await expect(page.locator('.research-card')).toHaveCount(2);
 await expect(page.locator('.research-cover img')).toHaveCount(0);
 await page.getByRole('button',{name:'装备研究',exact:true}).click();await expect(page.locator('.research-cover img')).toHaveCount(rows.filter((r:any)=>r.kind==='image'&&r.scope==='equipment').slice(0,24).filter((r:any)=>r.media_id).length);
 for(const img of await page.locator('.research-cover img').all()){await img.scrollIntoViewIfNeeded();await img.evaluate((i:HTMLImageElement)=>i.decode());}
 await page.screenshot({path:resolve(shots,'museum-gallery-zh.png'),fullPage:true});
 const rifle=rows.find((r:any)=>r.kind==='image'&&r.scope==='equipment'&&r.title.startsWith('Kar98k 2019'));
 await page.goto('/research/'+rifle.id);await expect(page.locator('.research-metadata')).toContainText('CC0');
 await page.locator('.research-image img').evaluate((i:HTMLImageElement)=>i.decode());
 await page.getByLabel('放大图片').click();await expect(page.getByRole('dialog',{name:'图片预览'})).toBeVisible();await page.keyboard.press('Escape');
 await expect(page.getByRole('dialog')).toHaveCount(0);
 const original=await context.request.get('/api/v1/media/'+rifle.media_id+'?original=true');expect(original.ok()).toBeTruthy();expect(original.headers()['content-type']).toContain('image/jpeg');
 await page.getByRole('button',{name:'English',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Registration source',exact:true})).toBeVisible();
 await page.screenshot({path:resolve(shots,'museum-photo-en.png'),fullPage:true});
 await page.getByLabel('Global search').fill('MEDKIT_REAL_REFERENCE_AUDIT');await page.getByLabel('Global search').press('Enter');
 await expect(page.getByRole('heading',{name:'Project search',exact:true})).toBeVisible();
 await page.getByRole('button',{name:/WWII medical bag/}).click();
 await expect(page.locator('.research-text')).toContainText('different inventory/donor');
 await expect(page.locator('.research-links a')).toHaveCount(4);
 await page.screenshot({path:resolve(shots,'medkit-research-en.png'),fullPage:true});
 await page.locator('.content section').last().getByRole('button').click();await expect(page.locator('.source-modal pre')).toContainText('No full-resolution original media');await page.keyboard.press('Escape');
 await page.setViewportSize({width:1280,height:900});await page.goto('/research');
 await expect(page.getByRole('heading',{name:'Historical references',exact:true})).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 await page.screenshot({path:resolve(shots,'library-en-1280.png'),fullPage:true});
 expect(errors).toEqual([]);
});

test('every permitted historical preview decodes and restricted records expose no media',async({context})=>{
 const rows=(await (await context.request.get('/api/v1/research?kind=image')).json()).data.items;
 for(const r of rows){
  if(r.image_access==='preview'){
   const image=await context.request.get('/api/v1/media/'+r.media_id);expect(image.ok(),r.title).toBeTruthy();expect(image.headers()['content-type']).toContain('image/jpeg');
   expect((await image.body()).length).toBeGreaterThan(1000);
  }else expect(r.media_id).toBeNull();
 }
});
