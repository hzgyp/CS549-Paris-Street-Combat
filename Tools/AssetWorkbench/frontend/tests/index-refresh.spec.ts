import {test,expect} from '@playwright/test';
import {readFileSync,mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';
const root=resolve(process.cwd(),'../../..');
test('refresh synchronizes navigation files and reports success in both languages',async({page,context})=>{
 const s=JSON.parse(readFileSync(resolve(root,'Assets/LocalWorking/AssetWorkbench/runtime/session.json'),'utf8'));
 expect((await context.request.post('/api/v1/session',{data:{token:s.token},headers:{Origin:`http://127.0.0.1:${s.port}`}})).ok()).toBeTruthy();
 await page.goto('/');
 for(const locale of ['zh','en']){
  await page.getByRole('button',{name:locale==='zh'?'中文':'English',exact:true}).click();
  const started=page.waitForResponse(r=>r.url().endsWith('/api/v1/index/jobs')&&r.request().method()==='POST');
  await page.getByRole('button',{name:locale==='zh'?'刷新索引':'Refresh index',exact:true}).click();
  const job=await(await started).json();
  await expect(page.getByRole('status')).toContainText(locale==='zh'?'平台与资料索引已同步':'Platform and asset reference index synchronized',{timeout:30000});
  const finished=await(await context.request.get('/api/v1/index/jobs/'+job.id)).json();
  expect(finished.status).toBe('succeeded');expect(finished.navigation_index.status).toBe('synced');
  expect(finished.navigation_index.asset_count).toBe(finished.coverage.asset_count);
  for(const file of finished.navigation_index.files){
   expect(createHash('sha256').update(readFileSync(resolve(root,file.path))).digest('hex')).toBe(file.sha256);
  }
  const index=JSON.parse(readFileSync(resolve(root,'Assets/Registry/asset-index.json'),'utf8'));
  expect(index.assets.length).toBe(finished.coverage.asset_count);
  expect(readFileSync(resolve(root,'Assets/Registry/ASSET_DIRECTORY.md'),'utf8')).toContain('平台刷新时自动生成');
  const shots=resolve(root,'Assets/LocalWorking/AssetWorkbench/runs/index-refresh-v2');mkdirSync(shots,{recursive:true});
  await page.screenshot({path:resolve(shots,'synced-'+locale+'.png'),fullPage:true});
 }
});
