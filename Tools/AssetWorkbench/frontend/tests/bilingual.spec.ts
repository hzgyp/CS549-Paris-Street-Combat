import {test,expect} from '@playwright/test';
import {readFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
const state=resolve(process.cwd(),'../../../Assets/LocalWorking/AssetWorkbench');
const shots=resolve(state,'runs/bilingual/screenshots');mkdirSync(shots,{recursive:true});
test.beforeEach(async({context})=>{
 const session=JSON.parse(readFileSync(resolve(state,'runtime/session.json'),'utf8'));
 expect((await context.request.post('/api/v1/session',{data:{token:session.token},headers:{Origin:`http://127.0.0.1:${session.port}`}})).ok()).toBeTruthy();
});

test('language changes preserve filters, revisions, templates and source identity',async({page,context})=>{
 await context.grantPermissions(['clipboard-read','clipboard-write']);
 await page.goto('/assets');await expect(page.locator('.asset-card')).toHaveCount(24);
 await page.getByRole('textbox',{name:'搜索资产',exact:true}).fill('地雷');await expect(page.locator('.asset-card')).toHaveCount(1);
 const url=page.url();await page.getByRole('button',{name:'English',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Asset library',exact:true})).toBeVisible();expect(page.url()).toBe(url);
 await expect(page.getByRole('textbox',{name:'Search assets',exact:true})).toHaveValue('地雷');await expect(page.locator('.asset-card')).toHaveCount(1);
 await page.locator('.asset-card').click();await expect(page.getByRole('heading',{name:'Pressure mine',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Revisions & decisions',exact:true}).click();
 await page.locator('.timeline').getByRole('button',{name:'View source',exact:true}).first().click();
 await expect(page.getByRole('heading',{name:'Source record · Original text',exact:true})).toBeVisible();
 const original=await page.locator('.source-modal pre').textContent(),sourcePath=await page.locator('.source-path').textContent();
 await page.keyboard.press('Escape');await page.getByRole('button',{name:'中文',exact:true}).click();
 await expect(page.getByRole('button',{name:'版本与取舍',exact:true})).toHaveClass('active');
 await page.locator('.timeline').getByRole('button',{name:'查看依据'}).first().click();
 expect(await page.locator('.source-modal pre').textContent()).toBe(original);expect(await page.locator('.source-path').textContent()).toBe(sourcePath);await page.keyboard.press('Escape');
 await page.goto('/compare');await expect(page.locator('.comparison-panel')).toHaveCount(2);const selects=page.locator('.compare-controls select');await selects.nth(1).selectOption('mine-ue-v2');await selects.nth(2).selectOption('mine-ue-v1');
 await page.getByRole('button',{name:'English',exact:true}).click();await expect(selects.nth(1)).toHaveValue('mine-ue-v2');await expect(selects.nth(2)).toHaveValue('mine-ue-v1');
 await page.reload();await expect(page.locator('html')).toHaveAttribute('lang','en');await expect(selects.nth(1)).toHaveValue('mine-ue-v2');
 await page.goto('/requirements');await page.getByRole('button',{name:'Character requirements',exact:true}).click();await page.getByRole('button',{name:'Copy template',exact:true}).click();
 const english=await page.evaluate(()=>navigator.clipboard.readText());expect(english).toContain('# Character requirements');expect(english).toContain('stop conditions');expect(english).not.toMatch(/[\u3400-\u9fff]/);
 const downloadPromise=page.waitForEvent('download');await page.getByRole('button',{name:'Download',exact:true}).click();const download=await downloadPromise;expect(readFileSync((await download.path())!,'utf8').replaceAll('\r\n','\n')).toBe(english.replaceAll('\r\n','\n'));
 await page.getByRole('button',{name:'中文',exact:true}).click();await expect(page.getByRole('heading',{name:'人物资产需求',exact:true})).toBeVisible();await page.getByRole('button',{name:'复制模板',exact:true}).click();expect(await page.evaluate(()=>navigator.clipboard.readText())).toContain('不重启详细AI人物制作');
});

for(const width of [1920,1366])test(`English and Chinese pages at ${width}`,async({page})=>{
 await page.setViewportSize({width,height:width===1920?1080:768});await page.goto('/');
 await expect(page.getByRole('heading',{name:'资产总览',exact:true})).toBeVisible();
 await expect(page.locator('.overview-intro')).toHaveCount(0);
 await page.screenshot({path:resolve(shots,`overview-zh-${width}.png`),fullPage:true});
 await page.getByRole('button',{name:'English',exact:true}).click();
 for(const [route,ready] of [['/','Asset overview'],['/assets','Asset library'],['/assets/pressure-mine','Pressure mine'],['/compare','Version comparison'],['/builds','Builds & usage'],['/requirements','Asset requirements'],['/health-check','Catalog health']]){
  await page.goto(route);await expect(page.getByRole('heading',{name:ready,exact:true})).toBeVisible();
  await expect(page.locator('.loading')).toHaveCount(0);
  if(route==='/assets')await page.getByRole('button',{name:'Filters',exact:true}).click();
  const remaining=await page.locator('main').evaluate(el=>{const copy=el.cloneNode(true) as HTMLElement;copy.querySelector('.language-switch')?.remove();return copy.innerText||copy.textContent||''});
  expect(remaining.match(/[\u3400-\u9fff]+/g)||[],route).toEqual([]);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),route).toBeTruthy();
  for(const img of await page.locator('img').all()){await img.scrollIntoViewIfNeeded();await img.evaluate((image:HTMLImageElement)=>image.decode().catch(()=>{}))}await page.evaluate(()=>scrollTo(0,0));
  await page.screenshot({path:resolve(shots,`${route.replaceAll('/','-')||'overview'}-en-${width}.png`),fullPage:true});
 }
});
