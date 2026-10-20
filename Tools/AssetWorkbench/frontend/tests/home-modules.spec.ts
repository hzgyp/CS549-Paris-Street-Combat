import {test,expect} from '@playwright/test';
import {readFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
const state=resolve(process.cwd(),'../../../Assets/LocalWorking/AssetWorkbench');
const shots=resolve(state,'runs/home-modules-20261017/screenshots');mkdirSync(shots,{recursive:true});
test.beforeEach(async({context})=>{
 const s=JSON.parse(readFileSync(resolve(state,'runtime/session.json'),'utf8'));
 expect((await context.request.post('/api/v1/session',{data:{token:s.token},headers:{Origin:`http://127.0.0.1:${s.port}`}})).ok()).toBeTruthy();
});
test('five illustrated modules, current formal identity and collapsed build archive',async({page,context})=>{
 const overview=(await(await context.request.get('/api/v1/overview')).json()).data;
 await page.goto('/');await expect(page.locator('[data-home-module]')).toHaveCount(5);
 await expect(page.locator('.home-release')).toHaveAttribute('data-build-id','formal');
 await expect(page.locator('.home-release')).toContainText(overview.homepage.release.version);
 await expect(page.locator('[data-home-card]')).toHaveCount(10);
 for(const [id,count] of [['actions',2],['characters',2],['scenes',1],['props',5]] as const){
  const module=page.locator(`[data-home-module="${id}"]`);await expect(module.locator('[data-home-card]')).toHaveCount(count);
  for(const img of await module.locator('img').all()){await img.scrollIntoViewIfNeeded();await img.evaluate((i:HTMLImageElement)=>i.decode());expect(await img.evaluate((i:HTMLImageElement)=>i.naturalWidth)).toBeGreaterThan(100);}
 }
 await page.locator('.home-release img').evaluate((i:HTMLImageElement)=>i.decode());
 await expect(page.locator('.home-no-picture')).toHaveCount(0);
 expect(await page.locator('.home-archive details').evaluate((d:HTMLDetailsElement)=>d.open)).toBeFalsy();
 await expect(page.locator('.home-release [data-home-card]')).toHaveCount(0);
 await page.locator('.home-archive summary').click();await expect(page.locator('.home-archive details a')).toHaveCount(overview.builds.length-1);
 await page.locator('.home-archive summary').click();await page.evaluate(()=>window.scrollTo(0,0));
 await page.screenshot({path:resolve(shots,'desktop-1920.jpg'),type:'jpeg',quality:70});
 await page.locator('#home-props').scrollIntoViewIfNeeded();await page.screenshot({path:resolve(shots,'props-1920.jpg'),type:'jpeg',quality:70});
});
test('scoped action, asset, gameplay and current release routes remain usable',async({page})=>{
 await page.goto('/');await page.locator('[data-home-card="grenade-holding"]').click();
 await expect(page).toHaveURL(/\/compare\?.*right=first-person-thumb-polish-accepted-20261017/);
 await expect(page.locator('[data-version-id="first-person-thumb-polish-accepted-20261017"]')).toBeVisible();
 await page.goto('/');await page.locator('[data-home-card="ctrl-transition"]').click();
 await expect(page).toHaveURL(/\/assets\/first-person\?tab=versions/);await expect(page.getByRole('heading',{name:'版本与整合记录',exact:true})).toBeVisible();
 await page.goto('/');const prop=page.locator('[data-home-module="props"] [data-home-card]').first();const href=await prop.getAttribute('href');await prop.click();await expect(page).toHaveURL(new RegExp(href!));
 await page.goto('/');await page.locator('.home-release-links a').first().click();await expect(page).toHaveURL(/\/builds\/formal$/);
 await page.goto('/');await page.locator('.home-release-links a').nth(1).click();await expect(page).toHaveURL(/\/gameplay\/g1-tutorial$/);
});
test('English, narrow layouts and unavailable release previews are explicit',async({page})=>{
 await page.goto('/');await page.getByRole('button',{name:'English',exact:true}).click();
 await expect(page.locator('.home-heading h1')).toHaveText('Asset releases');
 await expect(page.locator('#home-actions h2')).toHaveText('Actions');
 await expect(page.locator('#home-props h2')).toHaveText('Equipment and props');
 for(const width of [1366,640,390]){
  await page.setViewportSize({width,height:900});await page.evaluate(()=>window.scrollTo(0,0));
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBeTruthy();
  await page.screenshot({path:resolve(shots,`english-${width}.jpg`),type:'jpeg',quality:70});
 }
 await page.route('**/api/v1/overview*',async route=>{const response=await route.fetch();const body=await response.json();body.data.homepage.release.cover_id=null;body.data.homepage.release.cover_state='not_registered';await route.fulfill({response,json:body});});
 await page.reload();await expect(page.locator('.home-release-picture')).toContainText('Preview not registered');
 await expect(page.locator('.home-release-picture>span')).toHaveCount(0);
});
