const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require('C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../../..'),out=path.join(root,'tmp/npc-ai-smooth-display-20261017/work_v1');
const stage=process.env.NPC_PERF_STAGE||'candidate-v1',origin=process.env.NPC_PERF_ORIGIN||'http://127.0.0.1:8766';
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true}),context=await browser.newContext({viewport:{width:1480,height:1100}}),page=await context.newPage();
 const checks=[],errors=[],frames=[];let endpoint='';page.on('pageerror',e=>errors.push(e.message));
 page.on('response',async r=>{if(r.url().includes('/npc-simulation/sessions/')&&r.request().method()==='POST'&&r.status()===200){endpoint=r.url();frames.push(await r.json());}});
 const pass=s=>checks.push(s),ready=()=>page.locator('canvas[data-ready="true"]').waitFor();
 try{
  await page.goto(origin+'/npc-simulation');await ready();
  await page.locator('.npc-toolbar select').last().selectOption('4');
  await page.locator('#npc-play').click();await page.waitForTimeout(900);
  const rendered=Number(await page.locator('canvas').getAttribute('data-render-at'));
  assert.ok(rendered>=2&&rendered<=4.5);pass('4x playback consumes recorded poses at the chosen speed');
  const canvas=page.locator('canvas');await canvas.scrollIntoViewIfNeeded();
  const box=await canvas.boundingBox(),zoom=Number(await canvas.getAttribute('data-zoom')),centre=(await canvas.getAttribute('data-centre')).split(',').map(Number),s=Math.min(box.width/180,box.height/240)*zoom;
  const point=JSON.parse(await canvas.getAttribute('data-render-actors')).A1.position;
  await page.mouse.click(box.x+box.width/2+(point[0]-centre[0])*s,box.y+box.height/2+(point[1]-centre[1])*s);
  assert.equal(await page.locator('#npc-agent').inputValue(),'A1');assert.equal(await page.locator('#npc-play').innerText(),'运行');pass('Picking the actually rendered member pauses and selects it');
  await page.waitForTimeout(300);const paused=await(await context.request.get(endpoint)).json(),paints=await canvas.getAttribute('data-render-at');
  await page.waitForTimeout(600);assert.equal((await(await context.request.get(endpoint)).json()).frame.at,paused.frame.at);assert.equal(await canvas.getAttribute('data-render-at'),paints);pass('Pause drains requests and stops further simulation/render progression');
  const response=page.waitForResponse(r=>r.url()===endpoint&&r.request().method()==='POST');await page.locator('#npc-step').click();const stepped=await(await response).json();
  await page.waitForFunction(at=>Number(document.querySelector('canvas').dataset.renderAt)===at,stepped.frame.at);
  assert.deepEqual(JSON.parse(await canvas.getAttribute('data-render-actors')),stepped.frame.actors);pass('Manual half-second step renders the authoritative endpoint immediately');
  await page.locator('#npc-history').fill('1');await page.waitForTimeout(60);assert.ok(await page.locator('#npc-play').isDisabled());
  const historical=await canvas.getAttribute('data-render-at');await page.waitForTimeout(200);assert.equal(await canvas.getAttribute('data-render-at'),historical);
  await page.getByRole('button',{name:'回到当前',exact:true}).click();pass('Timeline review cancels animation and returns to the live endpoint');
  await page.locator('#npc-reset').click();await page.waitForFunction(()=>document.querySelector('.npc-clock').textContent.startsWith('0.0'));
  assert.equal(Number(await canvas.getAttribute('data-render-at')),0);pass('Reset clears old presentation and starts at zero');
  // Exercise the installed finite-end UI without waiting two wall-clock minutes.
  const id=await page.evaluate(()=>sessionStorage.getItem('paris.npc.live-session'));
  endpoint=origin+'/api/v1/npc-simulation/sessions/'+id;
  let world=await(await context.request.get(endpoint)).json();const csrf=(await(await context.request.get(origin+'/api/v1/session')).json()).csrf;
  for(let i=0;i<239;i++){
   const r=await context.request.post(endpoint,{data:{revision:world.frame.revision,request_id:'finite_ui_'+i,operation:'step',seconds:.5},headers:{Origin:origin,'X-CSRF-Token':csrf}});assert.equal(r.status(),200);world=await r.json();
  }
  assert.equal(world.frame.at,119.5);await page.reload();await ready();await page.locator('.npc-toolbar select').last().selectOption('4');await page.locator('#npc-play').click();
  await page.waitForFunction(()=>document.querySelector('#npc-play').disabled&&document.querySelector('#npc-play').textContent==='运行',{},{timeout:5000});
  assert.equal(Number(await canvas.getAttribute('data-render-at')),120);pass('Final recorded segment drains and finite playback stops at 120 seconds');
  assert.deepEqual(errors,[]);pass('No uncaught errors in speed/pick/pause/step/review/reset/finite-end controls');
  fs.writeFileSync(path.join(out,stage+'-controls.json'),JSON.stringify({status:'passed',checks,errors},null,2));
  console.log(JSON.stringify({status:'passed',checks:checks.length}));
 }catch(e){fs.writeFileSync(path.join(out,stage+'-controls-failed.json'),JSON.stringify({status:'failed',checks,errors,error:String(e.stack)},null,2));throw e;}
 finally{await context.close();await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
