import {test,expect} from '@playwright/test';
import {readFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
const root=resolve(process.cwd(),'../../..');
const state=resolve(root,'Assets/LocalWorking/AssetWorkbench');
test('city map is searchable and shows levels, versions and game use in both languages',async({page,context})=>{
 const s=JSON.parse(readFileSync(resolve(state,'runtime/session.json'),'utf8'));
 const origin=`http://127.0.0.1:${s.port}`;
 expect((await context.request.post('/api/v1/session',{data:{token:s.token},headers:{Origin:origin}})).ok()).toBeTruthy();
 const a=(await(await context.request.get('/api/v1/assets/paris-city')).json()).data;
 expect(a.category).toBe('地图');expect(a.member_count).toBe(15850);expect(a.map_details.level_count).toBe(69);
 for(const q of ['地图','France Liberation','LV_Paris_WW2']){
  const hits=(await(await context.request.get('/api/v1/assets',{params:{q}})).json()).data.items;
  expect(hits.some((x:any)=>x.id==='paris-city')).toBeTruthy();
 }
 await page.goto('/assets?category='+encodeURIComponent('地图'));
 await expect(page.getByRole('heading',{name:'巴黎二战地图 · France Liberation',exact:true})).toBeVisible();
 await page.getByRole('heading',{name:'巴黎二战地图 · France Liberation',exact:true}).click();
 const summary=page.getByTestId('map-summary');await expect(summary).toContainText('15,850');await expect(summary).toContainText('LV_Paris_WW2.umap');
 await expect(summary).toContainText('/Game/ParisCombat/Maps/LV_ParisG1_Midterm_V1');
 await page.getByRole('button',{name:'查找关卡与场景资源',exact:true}).click();await expect(page.getByRole('textbox',{name:'搜索包内资源',exact:true})).toHaveValue('.umap');await expect(page.getByText('69 成员',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'概览与来源',exact:true}).click();
 const shots=resolve(state,'runs/city-map-ui');mkdirSync(shots,{recursive:true});
 await page.screenshot({path:resolve(shots,'city-map-zh.png'),fullPage:true});
 await page.getByRole('button',{name:'版本与取舍',exact:true}).click();await expect(page.locator('.timeline')).toContainText('d20260630');await expect(page.locator('.timeline')).toContainText('G1 原生派生地图');
 await page.getByRole('button',{name:'游戏使用',exact:true}).click();await expect(page.locator('.usage-row[data-build-id="formal"]').first()).toBeVisible();
 const usages=a.usage.filter((u:any)=>u.basis==='pinned_source_reference'&&u.label==='当前游戏默认地图');expect(usages.length).toBeGreaterThan(0);
 await page.getByRole('button',{name:'包含内容',exact:true}).click();await page.getByRole('textbox',{name:'搜索包内资源',exact:true}).fill('.umap');
 await expect(page.getByText('69 成员',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'概览与来源',exact:true}).click();await page.getByRole('button',{name:'English',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Paris WWII map · France Liberation',exact:true})).toBeVisible();await expect(summary).toContainText('Main levels and scene layers');
 await expect(summary).toContainText('City persistent level');await page.setViewportSize({width:1366,height:768});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 await page.screenshot({path:resolve(shots,'city-map-en.png'),fullPage:true});
 const index=JSON.parse(readFileSync(resolve(root,'Assets/Registry/asset-index.json'),'utf8'));expect(index.assets.find((x:any)=>x.id==='paris-city').category).toBe('地图');
});
test('city map cover uses the inspected real scene and all registered scene images load',async({page,context})=>{
 const s=JSON.parse(readFileSync(resolve(state,'runtime/session.json'),'utf8'));
 const origin=`http://127.0.0.1:${s.port}`;
 expect((await context.request.post('/api/v1/session',{data:{token:s.token},headers:{Origin:origin}})).ok()).toBeTruthy();
 const a=(await(await context.request.get('/api/v1/assets/paris-city')).json()).data;
 expect(a.preview_id).toBe('paris-map-game-bridge');expect(a.media.find((m:any)=>m.id===a.preview_id).actual_capture).toBeTruthy();
 await page.goto('/assets/paris-city');const cover=page.locator('.detail-media img');
 await cover.evaluate((i:HTMLImageElement)=>i.decode());expect(await cover.evaluate((i:HTMLImageElement)=>i.naturalWidth)).toBe(1920);
 for(const image of a.media.filter((m:any)=>m.actual_capture))expect((await context.request.get('/api/v1/media/'+image.id)).ok()).toBeTruthy();
});
