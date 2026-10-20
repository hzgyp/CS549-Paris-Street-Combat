const assert=require('assert/strict');
const {nodeMapEvidence}=require('../frontend/src/npcNodeMap.ts');
const n=(id,op,children=[])=>({id,op,kind:children.length?'Sequence':op==='goal'||op==='assigned'||op==='visible'?'Condition':'Action',children,label:[id,id],description:['说明','Description']});
const definition={id:'test',root:'root',nodes:[n('root',null,['role','follow','search','sight']),n('role',null,['role.check','role.reserve']),n('role.check','assigned'),n('role.reserve','reserve_role'),n('follow',null,['follow.compute','follow.goal','follow.move']),n('follow.compute','formation'),n('follow.goal','goal'),n('follow.move','move'),n('search',null,['search.project']),n('search.project','project_search'),n('sight','visible')]};
const fresh=()=>({at:8,actors:{A1:{position:[1,2]},P:{position:[90,90]}},moves:{A1:{goal:[7,8],path:[[3,4],[7,8]]}},minds:{A1:{search_points:[[10,11],[12,10]]}},scores:{A1:[]},behavior_trees:{A1:{at:8,nodes:Object.fromEntries(definition.nodes.map(n=>[n.id,{status:'Skipped',detail:{}}])),blackboard:{state:'Search',reservation:{id:'F1',position:[7,8]},search_origin:[10,10],search_started:4,search_deadline:14}}}});
const set=(f,id,status,detail)=>f.behavior_trees.A1.nodes[id]={status,detail};
const evidence=(f,id)=>nodeMapEvidence(f,definition,'A1',id);
let checks=0;
{
 const f=fresh();set(f,'root','Success',{selected_child:'follow'});set(f,'role','Failure',{stopped_child:'role.check'});set(f,'role.check','Failure',{assignment:null});const e=evidence(f,'role.reserve');assert.equal(e.status,'Skipped');assert.match(e.reason,/role.check/);assert.deepEqual(e.marks,[]);checks++;
}
{
 const f=fresh();set(f,'follow.compute','Success',{desired_slot:[6,8],goal:[7,8],follow_distance:5});const e=evidence(f,'follow.compute');assert.deepEqual(e.marks.map(m=>m.point),[[6,8],[7,8]]);assert.equal(e.marks[0].kind,'desired');assert.equal(e.marks[1].kind,'goal');assert.match(e.facts.join(),/5.00/);checks++;
 set(f,'follow.goal','Failure',{goal:null});const absent=evidence(f,'follow.goal');assert.equal(absent.marks.length,0);assert.match(absent.reason,/没有获得目标/);checks++;
}
{
 const f=fresh();set(f,'follow.move','Running',{goal:[7,8],requested_goal:[9,8],result:'Moving',requests:4,retries:1,arrival_error:6});let e=evidence(f,'follow.move');assert.deepEqual(e.marks.map(m=>m.point),[[9,8],[7,8]]);assert.equal(e.path.length,2);assert.match(e.reason,/只有移动动作 Success/);checks++;
 f.moves.A1.goal=[100,100];assert.equal(evidence(f,'follow.move').path.length,0);checks++;
}
{
 const f=fresh();set(f,'role','Success',{});set(f,'role.check','Success',{assignment:'C2',role:'Support',reason:'joint choice'});set(f,'role.reserve','Success',{goal:[4,5],slot:'C2'});f.scores.A1=[{id:'C1',position:[3,5],valid:true,score:100,gates:[]},{id:'C2',position:[4,5],valid:true,score:10,gates:[]},{id:'C3',position:[5,5],valid:false,score:999,gates:['BudgetExceeded']}];const e=evidence(f,'role');assert.equal(e.marks.find(m=>m.id==='cover-C2').kind,'goal');assert.equal(e.marks.find(m=>m.id==='cover-C1').kind,'candidate');assert.equal(e.marks.find(m=>m.id==='cover-C3').kind,'rejected');assert.match(e.facts.join(),/BudgetExceeded/);checks++;
 set(f,'role.check','Failure',{assignment:null,role:null,reason:'no current contact'});f.scores.A1=[];assert.equal(evidence(f,'role.check').marks.length,0);assert.match(evidence(f,'role.check').facts.join(),/no current contact/);checks++;
}
{
 const f=fresh();set(f,'search.project','Success',{requested_offset:[12,10],projected:[11.5,10],candidate_limit:25});const e=evidence(f,'search.project');assert.equal(e.area.radius,2);assert.deepEqual(e.area.centre,[10,10]);assert.ok(!e.marks.some(m=>m.point[0]===90));assert.match(e.facts.join(),/14.00/);checks++;
 const old=structuredClone(f);old.at=5;old.behavior_trees.A1.at=5;old.behavior_trees.A1.blackboard.search_deadline=9;f.behavior_trees.A1.blackboard.search_origin=[99,99];assert.equal(evidence(old,'search.project').at,5);assert.deepEqual(evidence(old,'search.project').area.centre,[10,10]);assert.match(evidence(old,'search.project').facts.join(),/9.00/);checks++;
 set(old,'search.project','Success',{requested_offset:[12,10],projected:null,candidate_limit:25});assert.ok(!evidence(old,'search.project').marks.some(m=>m.id==='projected-search'));checks++;
}
{
 const f=fresh();set(f,'sight','Failure',{live_visible:false,observation:null,german_sight_range:2,german_sight_fov_degrees:30});const e=evidence(f,'sight');assert.equal(e.marks.length,0);assert.match(e.reason,/否/);assert.match(e.facts.join(),/未细分/);checks++;
 assert.equal(nodeMapEvidence(undefined,definition,'A1','sight'),undefined);assert.equal(nodeMapEvidence(f,undefined,'A1','sight'),undefined);checks++;
}
{
 const f=fresh(),s={schema:'paris.npc.sight.v1',at:7.8,observer:'G1',target:'P',origin:[1,2],heading:0,target_position:[9,2],distance_m:8,range_m:14,angle_degrees:0,half_fov_degrees:60,fov_degrees:120,visible:false,failure:'Occlusion',gates:{distance:'Success',angle:'Success',occlusion:'Failure'},visible_hostiles:['A2'],map_sha256:'map',ray:{blocked:true,point:[4,2],cell:[16,8],cell_size_m:.25}};
 f.behavior_trees.A1.blackboard.player_sight=s;set(f,'sight','Success',{live_visible:true,observation:{actor_id:'A2',position:[3,2]}});const e=evidence(f,'sight');assert.equal(e.vision,s);assert.match(e.reason,/A2/);assert.ok(e.facts.some(x=>x.includes('首个遮挡点')));checks++;
 set(f,'search.project','Skipped',{});const skipped=evidence(f,'search.project');assert.equal(skipped.vision,s);assert.deepEqual(skipped.marks,[]);assert.match(skipped.reason,/未执行/);checks++;
 const old=structuredClone(f);f.behavior_trees.A1.blackboard.player_sight={...s,at:8,visible:true,failure:null};assert.equal(evidence(old,'sight').vision.at,7.8);assert.equal(evidence(old,'sight').vision.failure,'Occlusion');checks++;
}
console.log(JSON.stringify({status:'passed',checks}));
