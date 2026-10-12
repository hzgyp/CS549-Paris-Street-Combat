import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
const root=resolve(process.cwd(),'../../..');
test('LAN authority authenticates and renders the shared 3D catalog',async({page,context})=>{
 const s=JSON.parse(readFileSync(resolve(root,'Assets/LocalWorking/AssetWorkbench/runtime/session.json'),'utf8'));
 expect(s.host).toBe('0.0.0.0');expect(s.share_ips.length).toBeGreaterThan(0);
 const origin=`http://${s.share_ips[0]}:${s.port}`;
 expect((await context.request.get(origin+'/api/v1/assets')).status()).toBe(401);
 const login=await context.request.post(origin+'/api/v1/session',{data:{token:s.token},headers:{Origin:origin}});expect(login.ok()).toBeTruthy();
 await page.goto(origin+'/assets/smoke-grenade');
 await expect(page.getByTestId('model-viewport')).toHaveAttribute('data-status','ready',{timeout:30000});
 await expect(page.getByRole('heading',{name:'烟雾弹',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'English',exact:true}).click();await expect(page.getByText('Static model · No embedded animation',{exact:true})).toBeVisible();
 expect((await context.request.get(origin+'/api/v1/assets',{headers:{Origin:'http://unrelated.invalid'}})).status()).toBe(403);
 const health=await(await context.request.get(origin+'/api/v1/health')).json();expect(health.mode).toBe('shared_read_only');
});

test('configured public forward exchanges the sharing credential and renders 3D',async({page,context})=>{
 const s=JSON.parse(readFileSync(resolve(root,'Assets/LocalWorking/AssetWorkbench/runtime/session.json'),'utf8'));
 test.skip(!s.external_origin,'No external sharing address configured');
 const origin=s.external_origin;
 expect((await context.request.get(origin+'/api/v1/assets')).status()).toBe(401);
 const share=readFileSync(resolve(root,'Assets/LocalWorking/AssetWorkbench/runtime/public-share-link.txt'),'utf8').trim();
 await page.goto(share);
 await expect(page.getByRole('heading',{name:'资产总览',exact:true})).toBeVisible();
 expect(new URL(page.url()).hash).toBe('');
 await page.goto(origin+'/assets/frag-grenade');
 await expect(page.getByTestId('model-viewport')).toHaveAttribute('data-status','ready',{timeout:30000});
 await expect(page.getByRole('heading',{name:'破片手雷',exact:true})).toBeVisible();
 expect((await context.request.get(origin+'/api/v1/assets')).ok()).toBeTruthy();
 expect((await context.request.get(origin+'/api/v1/assets',{headers:{Origin:'http://unrelated.invalid'}})).status()).toBe(403);
});
