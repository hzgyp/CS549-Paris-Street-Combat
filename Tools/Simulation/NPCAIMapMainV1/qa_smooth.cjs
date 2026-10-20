// New owned contexts; record real canvas paints, not just the browser RAF clock.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require('C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../../..'),out=path.join(root,'tmp/npc-ai-smooth-display-20261017/work_v1');
const stage=process.env.NPC_PERF_STAGE||'baseline',origin=process.env.NPC_PERF_ORIGIN||'http://127.0.0.1:8766';
const percentile=(a,p)=>a.slice().sort((x,y)=>x-y)[Math.min(a.length-1,Math.floor(a.length*p))]||0;
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const context=await browser.newContext({viewport:{width:1480,height:1100}});const page=await context.newPage();
 const errors=[],requests=[];page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(()=>{
  window.npcPaintTrace=[];
  const arc=CanvasRenderingContext2D.prototype.arc,text=CanvasRenderingContext2D.prototype.fillText,image=CanvasRenderingContext2D.prototype.drawImage;
  CanvasRenderingContext2D.prototype.drawImage=function(...args){if(this.npcPaintStart==null)this.npcPaintStart=performance.now();return image.apply(this,args)};
  CanvasRenderingContext2D.prototype.arc=function(x,y,r,...rest){if(r===8&&!this.npcPlayerPoint)this.npcPlayerPoint=[x,y];return arc.call(this,x,y,r,...rest)};
  CanvasRenderingContext2D.prototype.fillText=function(label,...rest){const result=text.call(this,label,...rest);if(label==='5 m'){window.npcPaintTrace.push({wall:performance.now(),draw_ms:performance.now()-this.npcPaintStart,point:this.npcPlayerPoint,at:this.canvas.dataset.renderAt||null,poses:this.canvas.dataset.renderActors||null});this.npcPlayerPoint=null;this.npcPaintStart=null;}return result};
 });
 page.on('requestfinished',r=>{if(r.url().includes('/npc-simulation/sessions/')&&r.method()==='POST'){const t=r.timing();requests.push(t.responseEnd-t.startTime+t.startTime)}});
 try{
  await page.goto(origin+'/npc-simulation');await page.locator('canvas[data-ready="true"]').waitFor({timeout:20000});
  const c=page.locator('canvas');await c.scrollIntoViewIfNeeded();
  const box=await c.boundingBox(),zoom=Number(await c.getAttribute('data-zoom')),centre=(await c.getAttribute('data-centre')).split(',').map(Number),scale=Math.min(box.width/180,box.height/240)*zoom;
  const response=page.waitForResponse(r=>r.url().includes('/npc-simulation/sessions/')&&r.request().method()==='POST');
  await page.mouse.click(box.x+box.width/2+(92.125-centre[0])*scale,box.y+box.height/2+(95.125-centre[1])*scale);assert.equal((await response).status(),200);
  await page.evaluate(()=>{window.npcPaintTrace=[]});await page.locator('#npc-play').click();
  await page.waitForTimeout(2600);await page.locator('#npc-play').click();
  const samples=await page.evaluate(()=>window.npcPaintTrace),gaps=samples.slice(1).map((s,i)=>s.wall-samples[i].wall);
  const moving=samples.slice(1).filter((s,i)=>s.point&&samples[i].point&&Math.hypot(s.point[0]-samples[i].point[0],s.point[1]-samples[i].point[1])>.01).length;
  const result={stage,status:'measured',paint_count:samples.length,moving_paints:moving,paint_gap_median_ms:percentile(gaps,.5),paint_gap_p95_ms:percentile(gaps,.95),paint_gap_max_ms:Math.max(...gaps),draw_p95_ms:percentile(samples.map(s=>s.draw_ms),.95),request_p95_ms:percentile(requests,.95),requests:requests.length,errors,samples};
  assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,stage+'-performance.json'),JSON.stringify(result,null,2));
  if(!stage.startsWith('baseline')){assert.ok(moving>=80,'too few genuinely moving paints');assert.ok(result.paint_gap_p95_ms<40,'paint gaps exceed 40ms');}
  console.log(JSON.stringify({...result,samples:undefined}));
 }finally{await context.close();await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
