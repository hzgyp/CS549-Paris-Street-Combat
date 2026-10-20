// Owned fresh contexts: no bootstrap token, cookie injection or manual login.
const fs=require('fs');
const path=require('path');
const assert=require('assert/strict');
const {chromium}=require('C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../../..');
const evidence=path.join(root,'tmp/asset-workbench-local-access-20261017/work_v1');
const origin='http://127.0.0.1:8766';

(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const context=await browser.newContext({viewport:{width:1480,height:1000}});
 const page=await context.newPage();const checks=[],errors=[],apiFailures=[];
 const pass=name=>checks.push(name);
 page.on('pageerror',e=>errors.push(e.message));
 page.on('response',r=>{if(r.url().includes('/api/')&&r.status()>=400)apiFailures.push({url:r.url(),status:r.status()});});
 try {
  assert.equal((await context.cookies()).length,0);
  await page.goto(origin+'/npc-simulation');
  await page.locator('canvas[data-ready="true"]').waitFor({timeout:20000});
  assert.equal(page.url(),origin+'/npc-simulation');
  assert.equal(await page.locator('.npc-members button').count(),6);
  pass('Fresh plain NPC deep link opens without token or pre-existing cookies');
  const cookie=(await context.cookies()).find(c=>c.name==='aw_session');
  assert.ok(cookie?.httpOnly);assert.equal(cookie.sameSite,'Strict');
  const status=await context.request.get(origin+'/api/v1/session');assert.equal(status.status(),200);
  const csrf=(await status.json()).csrf;
  pass('Page automatically establishes a HttpOnly same-site session');
  const next=page.waitForResponse(r=>r.url().includes('/api/v1/npc-simulation/sessions/')&&r.request().method()==='POST');
  await page.locator('#npc-step').click();const stepped=await next;assert.equal(stepped.status(),200);
  const world=await stepped.json();assert.ok(world.frame.at>0);
  const endpoint=stepped.url();
  await page.waitForFunction(at=>document.querySelector('.npc-clock')?.textContent.startsWith(at.toFixed(1)),world.frame.at);
  pass('NPC actually advances using the automatically established session');
  await page.reload();await page.locator('canvas[data-ready="true"]').waitFor();
  assert.ok((await page.locator('.npc-clock').innerText()).startsWith(world.frame.at.toFixed(1)));
  assert.equal((await context.cookies()).find(c=>c.name==='aw_session').value,cookie.value);
  assert.equal((await(await context.request.get(origin+'/api/v1/session')).json()).csrf,csrf);
  assert.equal((await context.request.get(endpoint)).status(),200);
  pass('Reload preserves the session and paused NPC world');
  await page.getByRole('button',{name:'资产库',exact:true}).click();
  await page.locator('.asset-card').first().waitFor({timeout:15000});
  const health=await(await context.request.get(origin+'/api/v1/health')).json();
  assert.equal(health.mode,'local_read_only');assert.ok(health.snapshot_id);
  pass('Existing asset library and current index remain accessible');
  await page.getByRole('button',{name:'NPC交互',exact:true}).click();
  await page.locator('canvas[data-ready="true"]').waitFor();
  pass('Native sidebar returns to the scene without a credential link');
  const other=await browser.newContext();const otherPage=await other.newPage();
  await otherPage.goto(origin+'/npc-simulation');await otherPage.locator('canvas[data-ready="true"]').waitFor();
  assert.notEqual((await other.cookies()).find(c=>c.name==='aw_session').value,cookie.value);
  assert.equal((await other.request.get(endpoint)).status(),404);
  await other.close();pass('A second token-free browser cannot read the first browser NPC world');
  assert.deepEqual(errors,[]);assert.deepEqual(apiFailures,[]);
  pass('No page errors or failing API requests during normal entry/reload/navigation');
  const receipt={status:'passed',checks,errors,apiFailures,snapshot_id:health.snapshot_id,world_at:world.frame.at,entry:origin+'/npc-simulation'};
  fs.writeFileSync(path.join(evidence,'browser-installed.json'),JSON.stringify(receipt,null,2));
  console.log(JSON.stringify({status:receipt.status,checks:checks.length,snapshot_id:health.snapshot_id}));
 }catch(e){
  fs.writeFileSync(path.join(evidence,'browser-failed.json'),JSON.stringify({status:'failed',checks,errors,apiFailures,error:String(e.stack)},null,2));
  throw e;
 }finally{await context.close();await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
