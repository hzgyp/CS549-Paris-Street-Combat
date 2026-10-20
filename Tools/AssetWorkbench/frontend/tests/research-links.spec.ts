import {test,expect} from '@playwright/test';
import {readFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
const root=resolve(process.cwd(),'../../..');
const state=resolve(root,'Assets/LocalWorking/AssetWorkbench');
const shots=resolve(state,'runs/history-associations-20261017/screenshots');mkdirSync(shots,{recursive:true});
test.beforeEach(async({context})=>{
 const s=JSON.parse(readFileSync(resolve(state,'runtime/session.json'),'utf8'));
 expect((await context.request.post('/api/v1/session',{data:{token:s.token},headers:{Origin:`http://127.0.0.1:${s.port}`}})).ok()).toBeTruthy();
});

test('asset excerpts, source images, zoom, bilingual labels and reverse gameplay links',async({page,context})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('/assets/german-rifle');
 const references=page.locator('.reference-section');await expect(references).toContainText('参考文字、图片与来源');
 await expect(references.locator('.reference-thumb img')).toHaveCount(4);
 for(const img of await references.locator('img').all())await img.evaluate((i:HTMLImageElement)=>i.decode());
 await expect(references.locator('pre').first()).not.toBeEmpty();
 expect(await references.locator('a[href^="https://"]').count()).toBeGreaterThan(0);
 await references.scrollIntoViewIfNeeded();await page.screenshot({path:resolve(shots,'rifle-inline-zh.png')});
 await references.locator('.reference-thumb').first().click();await expect(page.getByRole('dialog',{name:'参考图预览'})).toBeVisible();
 const original=page.getByRole('link',{name:'查看原图'});expect(await original.getAttribute('href')).toContain('original=true');
 await page.keyboard.press('Escape');await expect(page.getByRole('dialog')).toHaveCount(0);
 await page.getByRole('button',{name:'English',exact:true}).click();await expect(references).toContainText('Reference text, images and sources');
 await references.getByRole('button',{name:'Full text and provenance'}).first().click();
 await expect(page.getByRole('heading',{name:'Linked gameplay design',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Rifle firing and reload',exact:true}).click();await expect(page).toHaveURL(/\/gameplay\/rifle-resources/);
 await expect(page.locator('.reference-section .reference-thumb img')).toHaveCount(4);
 await page.locator('.reference-section').scrollIntoViewIfNeeded();await page.screenshot({path:resolve(shots,'rifle-gameplay-en.png')});
 await page.goto('/gameplay/medical-kits');await expect(page.getByText('Not implemented',{exact:true})).toBeVisible();
 await expect(page.locator('.reference-section')).toContainText('candidate model is not adopted');
 await page.locator('.reference-section').scrollIntoViewIfNeeded();await page.screenshot({path:resolve(shots,'medical-design-en.png')});
 expect(errors).toEqual([]);
});

test('Paris context keeps rights-limited pictures linked, unrelated research stays unassigned',async({page,context})=>{
 const map=(await(await context.request.get('/api/v1/assets/paris-city')).json()).data;
 expect(map.historical_references.length).toBeGreaterThan(5);
 expect(map.historical_references.every((r:any)=>r.scope==='paris')).toBeTruthy();
 const weather=(await(await context.request.get('/api/v1/research?kind=weather')).json()).data.items;
 expect(weather).toHaveLength(0);
 await page.goto('/assets/paris-city');const refs=page.locator('.reference-section');await expect(refs.locator('.reference-link-only')).toHaveCount(2);
 await expect(refs.locator('img')).toHaveCount(0);await expect(refs).toContainText('关卡路线与购买地图不是史实地形复原');
 await refs.scrollIntoViewIfNeeded();await page.screenshot({path:resolve(shots,'paris-context-zh.png')});
 await page.getByRole('button',{name:'English',exact:true}).click();await page.setViewportSize({width:1280,height:900});
 await page.goto('/assets/allied-soldier');await expect(page.locator('.reference-thumb').first()).toBeVisible();
 for(const img of await page.locator('.reference-thumb img').all())await img.evaluate((i:HTMLImageElement)=>i.decode());
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 await page.locator('.reference-section').scrollIntoViewIfNeeded();await page.screenshot({path:resolve(shots,'uniform-reference-en-1280.png')});
});
