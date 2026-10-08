// Read-only data routing checks in Node. This does not execute browser UI.
const fs=require('fs'),vm=require('vm'),zlib=require('zlib'),crypto=require('crypto');
const path=require('path'),file=process.argv[2],text=fs.readFileSync(file,'utf8');
const data=text.match(/<script type="application\/json" id="fineDataset">([\s\S]*?)<\/script>/)[1];
const blocks=[...text.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
blocks.forEach(code=>new vm.Script(code));
const context={document:{getElementById:()=>({textContent:data,remove(){}})},URL,URLSearchParams,Uint8Array,Blob,Response,DecompressionStream,atob,Map,Math,Number,String,Boolean,JSON,Error};
vm.createContext(context);vm.runInContext(blocks[0],context);
(async()=>{let checks=0;const config=await vm.runInContext("fineJSON('/api/config')",context);if(config.spec.cell_cm!==25||config.spec.columns!==4032)throw Error('Wrong frame');checks+=2;
 const payload=JSON.parse(data),requests=[];
 for(const scope of ['saved','full']){
  const keys=Object.keys(payload.tiles).filter(k=>k.startsWith(scope+':'));
  for(const key of [keys[0],keys[Math.floor(keys.length/2)],keys.at(-1)]){
   const tile=JSON.parse(zlib.gunzipSync(Buffer.from(payload.tiles[key],'base64')));
   const candidates=tile.nodes.length?[tile.nodes[0],tile.nodes.at(-1)]:[];
   for(const n of candidates){const params=new URLSearchParams({current:scope==='saved'?'1':'0',mode:'walk',layer:String(n[3]),group:'-1',c:String(n[1]),r:String(n[2])});const result=await vm.runInContext(`fineJSON(${JSON.stringify('/api/point?'+params)})`,context);const node=result.city_nodes.find(x=>x.id===n[0]);if(!node||node.source_sample_scope!==scope||node.feet_cm[2]!==n[5]||node.saved_group!==(scope==='saved'?n[6]:-1))throw Error('Point scope/Z route');if(result.xy_cm[0]!==-50400+(n[1]+.5)*25||result.xy_cm[1]!==50400-(n[2]+.5)*25)throw Error('Coordinate mapping');checks+=5;requests.push({scope,c:n[1],r:n[2],id:n[0]})}
  }
  for(const c of [2604,2607])for(const r of [2560,2563]){const result=await vm.runInContext(`fineJSON('/api/point?current=${scope==='saved'?1:0}&c=${c}&r=${r}&mode=walk&group=-1&layer=0')`,context);if(result.city_nodes.some(n=>n.eligible))throw Error('Quarantine readmitted');checks++;}
 }
 if(text.includes('await fetch(')||text.includes("im.src='/map.png"))throw Error('External resource route remains');checks+=2;
 if(!text.includes('(view.scale*4).toFixed(1)'))throw Error('Wrong physical scale label');checks++;
 const result={status:'pass_fine_offline_data_contract',checks,requests,browser_ui_or_tablet_qa:false,sha256:crypto.createHash('sha256').update(text).digest('hex')};
 const out=path.join(path.dirname(file),'audit_tool.json');if(fs.existsSync(out))throw Error('Preserve prior audit');fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
})().catch(e=>{console.error(e);process.exitCode=1});
