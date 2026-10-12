import {test,expect} from '@playwright/test';
import {readFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
const state=resolve(process.cwd(),'../../../Assets/LocalWorking/AssetWorkbench');
const shots=resolve(state,'runs/inventory/screenshots');mkdirSync(shots,{recursive:true});
test.beforeEach(async({context})=>{
 const session=JSON.parse(readFileSync(resolve(state,'runtime/session.json'),'utf8'));
 expect((await context.request.post('/api/v1/session',{data:{token:session.token},headers:{Origin:`http://127.0.0.1:${session.port}`}})).ok()).toBeTruthy();
});
test('complete package paging, members, source usage and weapon views',async({page,context})=>{
 await page.goto('/assets?parent=ue4-animation-collection');await expect(page.locator('.list-summary')).toContainText('125 件资产');await expect(page.locator('.asset-card')).toHaveCount(24);
 const ids=new Set<string>();
 for(let i=0;i<6;i++){
  for(const id of await page.locator('.asset-card .en-name').allTextContents()){expect(ids.has(id)).toBeFalsy();ids.add(id)}
  if(i<5){await page.getByRole('button',{name:'下一页',exact:true}).click();await expect(page.locator('.pagination')).toContainText(`页 ${i+2}`)}
 }
 expect(ids.size).toBe(125);await expect(page.getByRole('button',{name:'下一页',exact:true})).toBeDisabled();
 await page.getByRole('button',{name:'English',exact:true}).click();await expect(page.locator('.pagination')).toContainText('Page 6');
 await page.getByRole('textbox',{name:'Search assets',exact:true}).fill('Superhero');await expect(page.locator('.asset-card')).toHaveCount(1);await expect(page.locator('.pagination')).toContainText('Page 1');
 await page.locator('.asset-card').click();await page.getByRole('button',{name:'Images & audio',exact:true}).click();await page.locator('.detail-media img').evaluate((i:HTMLImageElement)=>i.decode());
 await page.getByRole('button',{name:'Contents',exact:true}).click();await expect(page.locator('tbody tr')).toHaveCount(50);await page.getByRole('textbox',{name:'Search package contents'}).fill('idle');await expect.poll(()=>page.locator('tbody tr').count()).toBeGreaterThan(0);
 await page.goto('/assets/mw2-sp-r-208');await expect(page.locator('.media-thumbs button')).toHaveCount(2);await page.locator('.media-thumbs button').last().click();await page.locator('.detail-media img').evaluate((i:HTMLImageElement)=>i.decode());await page.screenshot({path:resolve(shots,'weapon-en.png'),fullPage:true});
 await page.goto('/assets/muzzle-flash');await page.getByRole('button',{name:'Game usage',exact:true}).click();await expect(page.locator('.usage-row[data-build-id="formal"]')).toBeVisible();await page.locator('main .source-row').getByRole('button',{name:'View source',exact:true}).first().click();await expect(page.locator('.source-modal pre')).toContainText('Niagara_Riffle_MuzzleFlash_01');await page.keyboard.press('Escape');
 await page.goto('/assets/frag-grenade');await page.getByRole('button',{name:'Game usage',exact:true}).click();await expect(page.locator('.usage-row[data-build-id="formal"]')).toHaveCount(0);const frag=(await(await context.request.get('/api/v1/assets/frag-grenade')).json()).data;await expect(page.locator('.usage-row')).toHaveCount(frag.usage.length);await expect(page.locator('.usage-row[data-build-id="equipment-input-review"]').first()).toBeVisible();
 await page.goto('/assets?parent=mw2-library');await expect(page.locator('.list-summary')).toContainText('53 assets');for(const img of await page.locator('.card-media img').all()){await img.scrollIntoViewIfNeeded();await img.evaluate((i:HTMLImageElement)=>i.decode())}await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:resolve(shots,'weapons-en.png'),fullPage:true});
 const main=await page.locator('main').evaluate(el=>{const copy=el.cloneNode(true) as HTMLElement;copy.querySelector('.language-switch')?.remove();return copy.textContent});expect(main).not.toMatch(/[\u3400-\u9fff]/);
 await page.getByRole('button',{name:'中文',exact:true}).click();await page.setViewportSize({width:1366,height:768});await page.screenshot({path:resolve(shots,'weapons-zh-1366.png'),fullPage:true});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 const overview=await (await context.request.get('/api/v1/overview')).json();expect(overview.data.stats.asset_count).toBeGreaterThan(200);
});
