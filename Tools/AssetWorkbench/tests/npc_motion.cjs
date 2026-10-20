const assert=require('assert/strict');
const {MotionPlayback}=require('../frontend/src/npcMotion.ts');
let checks=0;
const pose=(at,x,y=0,heading=0)=>({at,actors:{P:{position:[x,y],heading,team:'allied',alive:true}}});
{
 const p=new MotionPlayback();p.push([pose(0,0),pose(.1,1),pose(.2,1,1)]);p.sample(0,1);
 assert.deepEqual(p.sample(50,1).actors.P.position,[.5,0]);
 const corner=p.sample(150,1).actors.P.position;assert.equal(corner[0],1);assert.ok(Math.abs(corner[1]-.5)<1e-12);checks++;
 assert.equal(p.sample(10000,1).at,.2);assert.deepEqual(p.sample(11000,1).actors.P.position,[1,1]);checks++;
 p.push([pose(.2,1,1),pose(.3,2,1)]);assert.equal(p.samples.length,2);
 assert.ok(p.sample(11050,1).actors.P.position[0]<1.51);checks++;
 p.clear();assert.equal(p.sample(12000,1),null);assert.equal(p.samples.length,0);checks++;
}
{
 const p=new MotionPlayback();p.push([pose(0,0,0,179*Math.PI/180),pose(.1,1,0,-179*Math.PI/180)]);p.sample(0,1);
 assert.ok(Math.abs(p.sample(50,1).actors.P.heading-Math.PI)<1e-10);checks++;
}
{
 const p=new MotionPlayback();p.push(Array.from({length:100},(_,i)=>pose(i/10,i)));assert.equal(p.samples.length,16);
 p.sample(0,4);const next=p.sample(10,4);assert.ok(Math.abs(next.at-8.44)<1e-9);checks++;
}
console.log(JSON.stringify({status:'passed',checks}));
