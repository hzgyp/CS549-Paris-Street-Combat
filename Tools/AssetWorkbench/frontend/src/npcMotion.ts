export type MotionActor={position:[number,number];heading:number;team:string;alive:boolean;health?:number;ammo?:number;squad?:string};
export type MotionSample={at:number;actors:Record<string,MotionActor>};

// Presentation follows only adjacent, recorded physics ticks; no extrapolation.
export class MotionPlayback {
 samples:MotionSample[]=[];
 at=0;
 lastWall:number|null=null;
 clear(){this.samples=[];this.lastWall=null;this.at=0;}
 push(incoming:MotionSample[]){
  if(!incoming.length)return;
  if(!this.samples.length)this.at=incoming[0].at;
  for(const sample of incoming){
   const last=this.samples.at(-1);
   if(last&&sample.at<last.at)continue;
   if(last&&sample.at===last.at)this.samples[this.samples.length-1]=sample;
   else this.samples.push(sample);
  }
  if(this.samples.length>16){this.samples=this.samples.slice(-16);this.at=Math.max(this.at,this.samples[0].at);}
 }
 sample(wall:number,speed:number):MotionSample|null {
  if(!this.samples.length){this.lastWall=null;return null;}
  const elapsed=this.lastWall===null?0:Math.max(0,wall-this.lastWall)/1000;
  this.lastWall=wall;
  this.at=Math.min(this.samples.at(-1)!.at,this.at+elapsed*speed);
  while(this.samples.length>1&&this.samples[1].at<=this.at+1e-9)this.samples.shift();
  const a=this.samples[0],b=this.samples[1];
  if(!b)return {at:this.at,actors:a.actors};
  const alpha=Math.max(0,Math.min(1,(this.at-a.at)/(b.at-a.at)));
  const actors:Record<string,MotionActor>={};
  for(const [id,from] of Object.entries(a.actors)){
   const to=b.actors[id]||from,delta=Math.atan2(Math.sin(to.heading-from.heading),Math.cos(to.heading-from.heading));
   actors[id]={...from,position:[from.position[0]+(to.position[0]-from.position[0])*alpha,from.position[1]+(to.position[1]-from.position[1])*alpha],heading:from.heading+delta*alpha};
  }
  return {at:this.at,actors};
 }
}
