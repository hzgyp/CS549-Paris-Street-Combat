// Owned local browser only; no human tabs or asset refresh.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require('C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../../..'),base=path.join(root,'tmp/npc-ai-parameters-20261018/work_v1');
const origin=process.env.NPC_PARAMETERS_ORIGIN||`http://127.0.0.1:${JSON.parse(fs.readFileSync(path.join(base,'QA_SERVER.json'),'utf8')).port}`;
const stage=process.env.NPC_PARAMETERS_STAGE||'candidate-v1',out=path.join(base,stage);fs.mkdirSync(out,{recursive:true});
const checks=[],frames=[],errors=[],pass=s=>{checks.push(s);fs.writeFileSync(path.join(out,'progress.json'),JSON.stringify(checks));};let browser,context,page,endpoint;
async function read(){return (await(await context.request.get(endpoint)).json()).frame}
async function result(action,operation){const pending=page.waitForResponse(r=>r.url().includes('/npc-simulation/sessions')&&r.request().method()==='POST'&&(!operation||r.request().postDataJSON()?.operation===operation));pending.catch(()=>{});await action();const r=await pending;assert.equal(r.status(),200);const data=await r.json();endpoint=origin+'/api/v1/npc-simulation/sessions/'+data.session_id;frames.push(data.frame);await page.waitForFunction(rev=>Number(document.querySelector('.npc-sim')?.dataset.revision)===rev,data.frame.revision);return data.frame}
async function apply(patch){for(const [key,v]of Object.entries(patch))await page.locator('#npc-param-'+key).fill(String(v));return result(()=>page.locator('#npc-parameters-apply').click(),'configure')}
async function step(n){let f;for(let i=0;i<n;i++)f=await result(()=>page.locator('#npc-step').click());return f}
async function coord(p){const c=page.locator('canvas');await c.scrollIntoViewIfNeeded();const b=await c.boundingBox(),z=Number(await c.getAttribute('data-zoom')),centre=(await c.getAttribute('data-centre')).split(',').map(Number),s=Math.min(b.width/180,b.height/240)*z;return [b.x+b.width/2+(p[0]-centre[0])*s,b.y+b.height/2+(p[1]-centre[1])*s]}
async function main(){
 browser=await chromium.launch({channel:'msedge',headless:true});context=await browser.newContext({viewport:{width:1480,height:1100},storageState:fs.existsSync(path.join(base,'qa-owner.private.json'))?path.join(base,'qa-owner.private.json'):undefined});page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));page.setDefaultTimeout(10000);
 const auth=await context.request.get(origin+'/api/v1/session');assert.equal(auth.status(),200);await context.storageState({path:path.join(base,'qa-owner.private.json')});
 await page.goto(origin+'/npc-simulation');await page.locator('canvas[data-ready="true"]').waitFor();
 endpoint=origin+'/api/v1/npc-simulation/sessions/'+await page.evaluate(()=>sessionStorage.getItem('paris.npc.live-session'));
 assert.equal(await page.locator('.npc-parameter-fields input').count(),5);assert.equal(await page.locator('iframe').count(),0);pass('Five bounded controls are inside the native executing behavior-tree page');
 let f=await read(),before=f;
 await page.locator('#npc-param-follow_distance').fill('999');assert.ok(await page.locator('#npc-parameters-apply').isDisabled());assert.deepEqual(await read(),before);
 await page.locator('#npc-param-follow_distance').fill('');assert.ok(await page.locator('#npc-parameters-apply').isDisabled());pass('Out-of-range and empty drafts cannot mutate the simulation');
 f=await apply({follow_distance:6});assert.deepEqual(f.actors,before.actors);assert.equal(f.at,before.at);assert.equal(f.parameters.follow_distance,6);
 const desired=f.behavior_trees.A1.nodes['follow.compute'].detail.desired_slot,p=f.actors.P;
 assert.ok(Math.abs(desired[0]-(p.position[0]-6*Math.cos(p.heading)+1.2*Math.sin(p.heading)))<1e-6);pass('Applying follow distance changes the actual formation target without advancing or teleporting');
 await page.locator('[data-node-id="follow.compute"]').click();assert.ok((await page.locator('.npc-node-parameters').innerText()).includes('6'));
 assert.ok(await page.locator('label.is-bound[for="npc-param-follow_distance"]').count());pass('Selected executing node identifies its bound editable threshold');
 const appliedIndex=await page.locator('#npc-history').getAttribute('max');
 f=await step(24);assert.equal(f.moves.A1.result,'Arrived');assert.ok(f.moves.A1.arrival_error<=.45);pass('Allied movement reaches its newly configured real path goal');
 await page.locator('#npc-history').fill('0');assert.equal(await page.locator('#npc-param-follow_distance').inputValue(),'3');assert.ok(await page.locator('#npc-param-follow_distance').isDisabled());assert.ok(await page.locator('#npc-parameters-apply').isDisabled());
 await page.locator('#npc-history').fill(appliedIndex);assert.equal(await page.locator('#npc-param-follow_distance').inputValue(),'6');
 await page.getByRole('button',{name:'回到当前',exact:true}).click();pass('Timeline displays historical settings read-only, including the same-time apply frame');
 await page.locator('#npc-save').click();let layout=await page.evaluate(()=>JSON.parse(localStorage.getItem('paris.npc.saved-map-layout')));assert.equal(layout.parameters.follow_distance,6);
 await apply({follow_distance:4});f=await result(()=>page.locator('#npc-restore').click());assert.equal(f.parameters.follow_distance,6);assert.equal(f.at,0);pass('Save and restore round-trip the applied parameters with the layout');
 f=await result(()=>page.locator('#npc-reset').click());assert.equal(f.parameters.follow_distance,6);pass('Reset keeps the current tuning for repeated comparisons');
 await page.evaluate(()=>{const key='paris.npc.saved-map-layout',v=JSON.parse(localStorage.getItem(key));delete v.parameters;localStorage.setItem(key,JSON.stringify(v))});f=await result(()=>page.locator('#npc-restore').click());assert.equal(f.parameters.follow_distance,3);pass('Existing saved layouts without parameters load the original defaults');
 f=await result(()=>page.locator('#npc-preset').selectOption('search'));await page.locator('#npc-tree-agent').selectOption('G1');f=await step(2);assert.ok(f.minds.G1.engage_permitted);
 const oldAllies=['A1','A2'].map(id=>f.minds[id].live_visible);f=await apply({german_sight_range:2});assert.ok(!f.minds.G1.live_visible);assert.deepEqual(['A1','A2'].map(id=>f.minds[id].live_visible),oldAllies);
 assert.equal(Number(await page.locator('canvas').getAttribute('data-vision-range')),2);pass('Changing German range changes actual sight and map shading while Allied sight stays intact');
 f=await apply({german_sight_range:14,german_sight_fov_degrees:30});assert.ok(Math.abs(Number(await page.locator('canvas').getAttribute('data-vision-fov'))-30)<1e-6);
 await page.locator('[data-node-id="sight.check"]').click();assert.ok((await page.locator('#npc-tree-node-detail').innerText()).includes('30'));pass('German view angle drives the server condition and displayed cone');
 f=await apply({german_sight_fov_degrees:120});
 // Explicit hidden placement after real sight; preserve actual personal last observation.
 const from=f.actors.P.position;
 f=await result(async()=>{await page.mouse.move(...await coord(from));await page.mouse.down();await page.mouse.move(...await coord([92.125,95.125]),{steps:10});await page.mouse.up()});
 f=await step(3);assert.ok(f.minds.G1.search_deadline>=0);const m=f.minds.G1,started=m.search_started,originPoint=m.search_origin,observation=m.memory;
 f=await apply({search_duration:20});assert.equal(f.minds.G1.search_deadline,started+20);assert.deepEqual(f.minds.G1.search_origin,originPoint);assert.deepEqual(f.minds.G1.memory,observation);pass('Extending an active search keeps the original start, frozen origin and personal memory');
 f=await step(2);f=await apply({search_duration:1});assert.ok(['Return','Guard'].includes(f.minds.G1.state));assert.equal(f.minds.G1.search_deadline,-1);pass('Shortening below elapsed search time ends the current search immediately');
 await page.locator('#npc-tree-expand').click();assert.equal(await page.locator('[role="dialog"]').count(),1);
 f=await apply({loss_grace:1.2});assert.equal(f.parameters.loss_grace,1.2);assert.equal(await page.locator('#root').evaluate(e=>e.inert),true);
 await page.locator('#npc-tree-full').check();await page.locator('#npc-tree-fit').click();
 const fit=await page.locator('.npc-bt-viewport').evaluate(el=>{const s=el.querySelector('svg').getBoundingClientRect(),b=el.getBoundingClientRect();return s.right-b.left<=el.clientWidth+2&&s.bottom-b.top<=el.clientHeight+2});assert.ok(fit);
 await page.locator('.npc-bt').screenshot({path:path.join(out,'parameters-tree-preview.jpg'),type:'jpeg',quality:65});
 await page.keyboard.press('Escape');assert.equal(await page.locator('[role="dialog"]').count(),0);await page.waitForFunction(()=>document.activeElement===document.getElementById('npc-tree-expand'));pass('Fullscreen editing, complete-tree fit and Escape focus restoration remain functional');
 await page.getByRole('button',{name:'English',exact:true}).click();await page.setViewportSize({width:390,height:844});await page.locator('#npc-tree-expand').click();await page.getByRole('button',{name:'Hide details',exact:true}).click();await page.locator('#npc-tree-fit').click();
 const narrow=await page.locator('.npc-bt').boundingBox();assert.ok(narrow.x+narrow.width<=390);assert.ok(await page.locator('.npc-bt').evaluate(e=>e.scrollWidth<=e.clientWidth));await page.locator('.npc-parameters').evaluate(e=>e.scrollTop=e.scrollHeight);assert.ok((await page.locator('.npc-parameters').innerText()).includes('Maximum search time'));
 await page.locator('.npc-bt').screenshot({path:path.join(out,'parameters-narrow-preview.jpg'),type:'jpeg',quality:65});await page.keyboard.press('Escape');pass('English 390px fullscreen keeps localized parameter controls contained and scrollable');
 await page.setViewportSize({width:1480,height:1100});await page.reload();await page.locator('canvas[data-ready="true"]').waitFor();assert.equal(await page.locator('#npc-param-loss_grace').inputValue(),'1.2');assert.equal(await page.locator('#npc-play').innerText(),'Run');pass('Reload restores the paused owned world and applied settings without token input');
 await page.locator('#npc-parameters-defaults').click();f=await result(()=>page.locator('#npc-parameters-apply').click(),'configure');assert.equal(f.parameters.loss_grace,.6);assert.equal(f.parameters.search_duration,6);pass('Fill defaults applies through the same real-world mutation');
 await page.locator('#npc-play').click();f=await apply({search_duration:10});assert.equal(f.parameters.search_duration,10);assert.equal(await page.locator('#npc-play').innerText(),'Pause');await page.waitForTimeout(650);await page.locator('#npc-play').click();pass('Tuning during playback preserves run state and serializes with physics steps');
 assert.deepEqual(errors,[]);pass('No uncaught browser errors');
}
main().then(()=>{fs.writeFileSync(path.join(out,'PARAMETERS_BROWSER_RESULT.json'),JSON.stringify({status:'pass',checks,trace_frames:frames.length,errors},null,2));fs.writeFileSync(path.join(out,'PARAMETERS_BROWSER_TRACE.json'),JSON.stringify(frames));console.log(JSON.stringify({status:'pass',checks:checks.length,trace_frames:frames.length,stage}))}).catch(async e=>{if(page)await page.screenshot({path:path.join(out,'failure-preview.jpg'),type:'jpeg',quality:65}).catch(()=>{});fs.writeFileSync(path.join(out,'PARAMETERS_BROWSER_FAILED.json'),JSON.stringify({checks,error:e.stack,errors},null,2));console.error(e.stack);process.exitCode=1}).finally(async()=>{if(browser)await browser.close()});
