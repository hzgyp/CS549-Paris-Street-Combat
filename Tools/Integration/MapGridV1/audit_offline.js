// Static/data-contract test only. This does not launch or simulate a browser UI.
const fs=require('fs'),zlib=require('zlib'),vm=require('vm'),path=require('path'),crypto=require('crypto'),assert=require('assert');
const dir=process.argv[2],html=fs.readFileSync(path.join(dir,'PARIS_GRID_TOOL_20261007.html'),'utf8');
const expected=JSON.parse(fs.readFileSync(path.join(dir,'offline_expected.json'),'utf8'));
assert(!/\bfetch\s*\(|<script[^>]+src=|<link[^>]+href=/.test(html));
const data=JSON.parse(zlib.gunzipSync(Buffer.from(html.match(/id="offlineDataset">([^<]+)</)[1],'base64')));
const adapter=fs.readFileSync(path.join(__dirname,'offline_api.js'),'utf8');new vm.Script(adapter);
new vm.Script(html.slice(html.lastIndexOf('<script>')+8,html.lastIndexOf('</script>')));
const begin=adapter.indexOf('function offlineParams');
const fakeDocument={createElement(type){assert.equal(type,'canvas');return {width:0,height:0,getContext(){return {fillStyle:'black',fillRect(){}}},toDataURL(){return 'data:image/png;static-test-only'}}}};
const context={URL,URLSearchParams,Map,Array,Number,Boolean,Math,document:fakeDocument,offlineData:data,offlineNodeIndex:new Map(),offlineMaskCache:new Map()};
for(const n of data.nodes){const key=(n[4]*data.config.spec.rows+n[2])*data.config.spec.columns+n[1];let list=context.offlineNodeIndex.get(key);if(!list)context.offlineNodeIndex.set(key,list=[]);list.push(n)}
vm.createContext(context);vm.runInContext(adapter.slice(begin),context);
for(const test of expected.checks){assert.equal(context.offlineJSON('/api/mask?'+test.query).white_cells,test.white_cells,test.query)}
for(const current of [0,1])for(const [c,r] of expected.quarantined_xy){
 const point=context.offlineJSON(`/api/point?c=${c}&r=${r}&current=${current}&group=-1&mode=walk&layer=0`);
 assert(point.city_nodes.length>0&&point.city_nodes.every(n=>!n.eligible));
 assert(point.city_nodes.some(n=>n.filter_reasons.some(t=>t.includes('隔离'))));
 for(const s of point.surfaces){assert.deepEqual(s.nav_cm.slice(0,2),point.xy_cm);assert.deepEqual(s.feet_cm.slice(0,2),point.xy_cm)}
}
let tested=0;
for(const current of [0,1]){
 const node=data.nodes.find(n=>n[4]===current&&n[3]===0&&n[17]&&n[7]===expected.scope_default_groups[current]);
 const point=context.offlineJSON(`/api/point?c=${node[1]}&r=${node[2]}&current=${current}&group=${node[7]}&mode=walk&layer=0`);
 const n=point.city_nodes.find(n=>n.id===node[0]);assert(n.eligible);assert.equal(n.feet_cm[2],node[6]);assert.equal(n.source_sample_scope,current?'saved':'full');
 assert(n.polys.every(p=>typeof p==='string'));assert.deepEqual(n.sample_ids,node[12]);assert(!('assembly_sites' in n));tested++;
}
const result={status:'pass_offline_script_syntax_and_data_contract',mask_queries:expected.checks.length,white_coordinate_scope_checks:tested,
 raw_surface_records:data.raw.length,normalized_nodes:data.nodes.length,external_requests_in_source:0,browser_ui_verified:false,
 html_sha256:crypto.createHash('sha256').update(html).digest('hex')};
const target=path.join(dir,'audit_offline_v1.json');assert(!fs.existsSync(target));fs.writeFileSync(target,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
