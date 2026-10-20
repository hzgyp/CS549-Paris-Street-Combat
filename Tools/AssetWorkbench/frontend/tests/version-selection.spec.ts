import {test,expect} from '@playwright/test';
import {readFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {defaultPair,orderedVersions} from '../src/versionSelection';
const root=resolve(process.cwd(),'../../..'),state=resolve(root,'Assets/LocalWorking/AssetWorkbench');
const shots=resolve(state,'runs/view-pairing-20261017/selection-screenshots');mkdirSync(shots,{recursive:true});
test.beforeEach(async({context})=>{
 const s=JSON.parse(readFileSync(resolve(state,'runtime/session.json'),'utf8'));
 expect((await context.request.post('/api/v1/session',{data:{token:s.token},headers:{Origin:`http://127.0.0.1:${s.port}`}})).ok()).toBeTruthy();
});
test('defaults use explicit scoped lineage, never insertion order or another human pass',()=>{
 const rows=[{id:'current',adoption:{primary:true,previous_id:'prior'}},{id:'prior'},{id:'unrelated-appended-pass',review:{basis:'human'},result:'pass'}];
 expect(defaultPair(rows)).toEqual({left:'prior',right:'current'});expect(orderedVersions(rows)[0].id).toBe('current');
 expect(defaultPair([{id:'current',adoption:{primary:true,previous_id:null}}])).toEqual({left:'',right:'current'});
});
test('medical pin, filters, stable manual pair, bilingual reset and asset switching',async({page,context})=>{
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 const current='medical-pouch-human-accepted-20261017',previous='medical-pouch-stain-v1-20261017';
 await page.goto('/compare?asset=medical-pouch');const selects=page.locator('.compare-controls select');
 await expect(selects.nth(1)).toHaveValue(previous);await expect(selects.nth(2)).toHaveValue(current);
 const rows=page.locator('.version-index tbody tr');await expect(rows.first()).toHaveAttribute('data-version-row',current);
 const revisions=(await(await context.request.get('/api/v1/assets/medical-pouch/revisions')).json()).data;
 const filters=page.getByLabel('评审筛选');
 for(const [name,stateName] of [['人工通过','human_approved'],['未通过','not_passed'],['待复核','pending']]){
  await filters.getByRole('button',{name:new RegExp('^'+name)}).click();
  const expected=revisions.filter((r:any)=>r.adoption||r.review_state===stateName||(!r.review_state&&stateName==='pending')).length;
  await expect(rows).toHaveCount(expected);await expect(rows.first()).toHaveAttribute('data-version-row',current);
  await expect(selects.nth(1)).toHaveValue(previous);await expect(selects.nth(2)).toHaveValue(current);
 }
 await filters.getByRole('button',{name:/^未通过/}).click();const failed=rows.filter({hasText:'medical-pouch-finish-v2-20261017'});
 await expect(failed).toContainText('失败原件保留');await failed.getByRole('button',{name:'左侧',exact:true}).click();
 await expect(page.locator('[data-version-id="medical-pouch-finish-v2-20261017"]')).toContainText('136');
 await expect(selects.nth(1)).toHaveValue('medical-pouch-finish-v2-20261017');await page.reload();
 await expect(selects.nth(1)).toHaveValue('medical-pouch-finish-v2-20261017');await expect(selects.nth(2)).toHaveValue(current);
 const snapshot=await page.locator('footer').innerText();
 await page.getByRole('button',{name:'刷新索引',exact:true}).click();
 await expect(page.locator('footer')).not.toHaveText(snapshot,{timeout:45000});
 await expect(selects.nth(1)).toHaveValue('medical-pouch-finish-v2-20261017');await expect(selects.nth(2)).toHaveValue(current);
 await expect(rows.first()).toHaveAttribute('data-version-row',current);
 await page.getByRole('button',{name:'上一版对比当前采用版',exact:true}).click();await expect(selects.nth(1)).toHaveValue(previous);
 await page.getByRole('button',{name:'English',exact:true}).click();await expect(rows.first()).toContainText('Current adopted');
 await page.getByLabel('Review filters').getByRole('button',{name:/^Pending review/}).click();await expect(rows.first()).toHaveAttribute('data-version-row',current);
 await page.screenshot({path:resolve(shots,'medical-default-filter-en.png'),fullPage:true});
 await selects.nth(0).selectOption('frag-grenade');await expect(selects.nth(1)).toHaveValue('frag-grenade-thumb-web-corrective-20261016');await expect(selects.nth(2)).toHaveValue('frag-grenade-thumb-polish-accepted-20261017');
 await expect(rows.first()).toHaveAttribute('data-version-row','frag-grenade-thumb-polish-accepted-20261017');
 await page.screenshot({path:resolve(shots,'frag-default-en.png'),fullPage:true});
 await selects.nth(0).selectOption('first-person');await expect(selects.nth(2)).toHaveValue('first-person-thumb-polish-accepted-20261017');
 await expect(page.locator('.version-index tbody tr.adopted-version')).toHaveCount(2);
 await page.setViewportSize({width:1366,height:768});expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 await selects.nth(0).selectOption('pressure-mine');await expect(page.getByText('No adopted revision registered.',{exact:false})).toBeVisible();
 await expect(page.locator('.version-index tbody tr.adopted-version')).toHaveCount(0);expect(errors).toEqual([]);
});
test('asset version history uses the same pin and filters',async({page})=>{
 await page.goto('/assets/medical-pouch');await page.getByRole('button',{name:'版本与取舍',exact:true}).click();
 const rows=page.locator('.timeline article');await expect(rows.first()).toHaveAttribute('data-version-row','medical-pouch-human-accepted-20261017');
 await page.getByLabel('评审筛选').getByRole('button',{name:/^未通过/}).click();await expect(rows).toHaveCount(2);await expect(rows.nth(1)).toContainText('136');
 await page.locator('.timeline').screenshot({path:resolve(shots,'medical-timeline-zh.png')});
});
