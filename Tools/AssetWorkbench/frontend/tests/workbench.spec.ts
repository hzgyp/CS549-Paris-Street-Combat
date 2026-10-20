import { test, expect } from '@playwright/test';
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const state=resolve(process.cwd(),'../../../Assets/LocalWorking/AssetWorkbench');
const screenshots=resolve(state,'runs/screenshots');mkdirSync(screenshots,{recursive:true});
test.beforeEach(async({context})=>{
 const session=JSON.parse(readFileSync(resolve(state,'runtime/session.json'),'utf8'));
 const result=await context.request.post('/api/v1/session',{data:{token:session.token},headers:{Origin:`http://127.0.0.1:${session.port}`}});
 expect(result.ok()).toBeTruthy();
});

test('overview, library search, filters, details and sources',async({page})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 const start=Date.now();await page.goto('/');await expect(page.getByRole('heading',{name:'资产总览'})).toBeVisible();
 await expect(page.locator('.asset-card')).toHaveCount(4);
 await page.locator('.asset-card img').first().evaluate((img:HTMLImageElement)=>img.decode());
 const elapsed=Date.now()-start;writeFileSync(resolve(state,'runs/browser-timing.json'),JSON.stringify({first_interactive_ms:elapsed,viewport:'1920x1080',browser:'installed Chrome',scope:'server and index already ready'}));
 await page.screenshot({path:resolve(screenshots,'overview-1920.png'),fullPage:true});
 await page.getByRole('button',{name:'浏览全部资产'}).click();await expect(page.locator('.asset-card')).toHaveCount(24);
 await page.getByRole('textbox',{name:'搜索资产',exact:true}).fill('地雷');await expect(page.locator('.asset-card')).toHaveCount(1);
 await page.locator('.asset-card').click();await expect(page.getByRole('heading',{name:'盘形压力地雷',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'版本与取舍'}).click();await expect(page.getByRole('heading',{name:'UE整合 v1 · 外观失败'})).toBeVisible();
 await page.locator('.timeline').getByRole('button',{name:'查看依据'}).first().click();await expect(page.getByRole('dialog',{name:'来源记录'})).toBeVisible();await expect(page.locator('.source-modal pre')).toContainText('MI030');
 await page.keyboard.press('Escape');await expect(page.getByRole('dialog')).toHaveCount(0);
 await page.goto('/assets');await expect(page.locator('.asset-card')).toHaveCount(24);await page.getByRole('textbox',{name:'全局搜索'}).fill('US Paratrooper');await page.getByRole('textbox',{name:'全局搜索'}).press('Enter');await expect(page.locator('.asset-card')).toHaveCount(1);await expect(page.locator('.asset-card')).toContainText('盟军伞兵');
 await page.getByRole('button',{name:'清空搜索'}).click();await expect(page.locator('.asset-card')).toHaveCount(24);await page.getByRole('button',{name:'人物',exact:true}).click();await expect(page.locator('.asset-card')).toHaveCount(3);
 await page.getByRole('button',{name:'全部资产',exact:true}).click();await page.getByRole('button',{name:'列表视图'}).click();await expect(page.locator('.asset-card.list')).toHaveCount(24);await page.getByRole('button',{name:'卡片视图'}).click();
 await page.getByRole('button',{name:'筛选',exact:true}).click();await page.getByLabel('访问许可',{exact:true}).selectOption('private_local');await expect(page.locator('.asset-card')).toHaveCount(24);await page.getByLabel('负责人',{exact:true}).selectOption('Yupu / Paris team');await page.getByRole('button',{name:'重置筛选'}).click();await expect(page.locator('.asset-card')).toHaveCount(24);
 await page.screenshot({path:resolve(screenshots,'library-1920.png'),fullPage:true});expect(errors).toEqual([]);
});

test('compare, selected builds, file query, templates and refresh',async({page,context})=>{
 await context.grantPermissions(['clipboard-read','clipboard-write']);await page.goto('/compare');await expect(page.getByText('模型身份相同；UE整合不同。')).toBeVisible();await expect(page.locator('.comparison-panel')).toHaveCount(2);
 for(const image of await page.locator('.comparison-image img').all())await image.evaluate((img:HTMLImageElement)=>img.decode());
 await page.screenshot({path:resolve(screenshots,'comparison-1920.png'),fullPage:true});
 await page.goto('/builds');await expect(page.getByRole('heading',{name:/g1-enemy-clear/})).toBeVisible();await page.getByRole('button',{name:'团队已发布包',exact:true}).click();await expect(page.getByRole('heading',{name:'paris-g1-playtest-20261009-audio-v2'})).toBeVisible();
 await page.getByRole('button',{name:'查看该构建文件',exact:true}).click();await expect(page.getByRole('heading',{name:'文件索引',exact:true})).toBeVisible();
 await page.goto('/files?bundle=paris-g1-recorded-audio');await page.getByRole('textbox',{name:'搜索文件路径'}).fill('fire_m1');await expect(page.locator('tbody tr')).toHaveCount(1);await expect(page.locator('tbody')).toContainText('fire_m1.wav');
 await page.goto('/requirements');await expect(page.getByRole('heading',{name:'道具资产需求',exact:true})).toBeVisible();await page.getByRole('button',{name:'人物资产需求',exact:true}).click();await expect(page.locator('.template-content .notice')).toContainText('不重启详细AI人物制作');await page.getByRole('button',{name:'复制模板',exact:true}).click();await expect(page.getByRole('status')).toContainText('模板已复制');expect(await page.evaluate(()=>navigator.clipboard.readText())).toContain('早期门槛');
 await page.screenshot({path:resolve(screenshots,'requirements-1920.png'),fullPage:true});
 await page.getByRole('button',{name:'刷新索引',exact:true}).click();await expect(page.getByRole('status')).toContainText('平台与资料索引已同步',{timeout:20000});await page.goto('/health-check');await expect(page.getByText('已完成',{exact:true}).first()).toBeVisible();
});

test('1366 layout, media loading, keyboard and no horizontal overflow',async({page})=>{
 await page.setViewportSize({width:1366,height:768});await page.goto('/assets');await expect(page.locator('.asset-card')).toHaveCount(24);
 for(const img of await page.locator('.card-media img').all()){await img.scrollIntoViewIfNeeded();await img.evaluate((i:HTMLImageElement)=>i.decode())}await page.evaluate(()=>scrollTo(0,0));
 const checks=await page.locator('.card-media img').evaluateAll(async(images:HTMLImageElement[])=>{await Promise.all(images.map(i=>i.decode().catch(()=>{})));return images.map(i=>({src:new URL(i.src).pathname,loaded:i.complete&&i.naturalWidth>0}))});expect(checks.every(x=>x.loaded)).toBeTruthy();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();await page.screenshot({path:resolve(screenshots,'library-1366.png'),fullPage:true});
 await page.getByRole('textbox',{name:'搜索资产',exact:true}).focus();await page.keyboard.type('rifle');await expect.poll(()=>page.locator('.asset-card').count()).toBeGreaterThan(3);await page.getByRole('button',{name:'清空搜索'}).click();
 await page.goto('/compare');await expect(page.locator('.comparison-panel')).toHaveCount(2);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();await page.screenshot({path:resolve(screenshots,'comparison-1366.png'),fullPage:true});
 await page.goto('/assets/recorded-audio');await expect(page.locator('audio')).toHaveCount(1);await page.locator('audio').evaluate(async(a:HTMLAudioElement)=>{a.load();await new Promise<void>((ok,no)=>{a.onloadedmetadata=()=>ok();a.onerror=()=>no(new Error('audio failed'))})});expect(await page.locator('audio').evaluate((a:HTMLAudioElement)=>a.duration)).toBeGreaterThan(0);
});
