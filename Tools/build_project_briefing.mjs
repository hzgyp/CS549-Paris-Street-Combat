import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

// Use the managed runtime. No project or system package installation is needed.
const runtime = process.env.RUNTIME_ROOT ?? '/Users/marcuscicero/.cache/codex-runtimes/codex-primary-runtime/dependencies';
process.env.RUNTIME_NODE_MODULES ??= path.join(runtime, 'node/node_modules');
process.env.RUNTIME_NODE ??= path.join(runtime, 'node/bin/node');
process.env.RUNTIME_BIN_DIR ??= path.join(runtime, 'bin/override');
const requireRuntime = createRequire(path.join(process.env.RUNTIME_NODE_MODULES, '__briefing__.cjs'));
const { Presentation, PresentationFile } = await import(pathToFileURL(requireRuntime.resolve('@oai/artifact-tool')));
const SKILL_DIR = process.env.SKILL_DIR ?? '/Users/marcuscicero/.codex/plugins/cache/openai-primary-runtime/presentations/26.905.11957/skills/presentations';
const { finalizePresentation, resolvePresentationFont } = await import(pathToFileURL(path.join(SKILL_DIR, 'container_tools/artifact_tool_utils.mjs')));
const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tmp = path.join(project, 'tmp/presentation-review');
const output = path.join(project, 'Docs/Presentation');
const visuals = path.join(project, 'Docs/Proposal/Visuals');
await fs.mkdir(tmp, { recursive: true });
await fs.mkdir(output, { recursive: true });
const revision = process.env.BRIEFING_REVISION ?? 'revised';
const finalPath = path.join(output, process.env.BRIEFING_FILENAME ?? `CS549_Paris_Street_Combat_Briefing_2026-09-24_${revision}.pptx`);
const font = resolvePresentationFont({ fontFamily: 'Arial' });
const C = { bg:'#F4F2EC', ink:'#1B2D32', muted:'#536165', olive:'#4B6655', pale:'#E5ECE5', gold:'#AD7D39', goldPale:'#F5EBD4', red:'#A34B43', redPale:'#F4E7E3', line:'#C9CECA', white:'#FFFFFF' };
const p = Presentation.create({ slideSize:{ width:1280, height:720 } });
const all = [];
const noteRecords = [];
const urls = {
  fab:'https://www.fab.com/listings/dae418da-1969-444a-821c-c1f30a3f21b6',
  animation:'https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-notifies-in-unreal-engine',
  collision:'https://dev.epicgames.com/documentation/en-us/unreal-engine/collision-in-unreal-engine---overview',
  navigation:'https://dev.epicgames.com/documentation/en-us/unreal-engine/navigation-system-in-unreal-engine',
  behavior:'https://dev.epicgames.com/documentation/en-us/unreal-engine/behavior-tree-in-unreal-engine---overview',
  perception:'https://dev.epicgames.com/documentation/en-us/unreal-engine/ai-perception-in-unreal-engine',
  events:'https://dev.epicgames.com/documentation/en-us/unreal-engine/event-dispatchers-in-unreal-engine',
};
function text(s, str, x,y,w,h, size=26, opts={}) {
  const sh = s.shapes.add({ geometry:'textbox', name:opts.name ?? str.slice(0,45), position:{left:x,top:y,width:w,height:h}, fill:'none', line:{fill:'none',width:0} });
  sh.text = str;
  sh.text.style = { typeface:font, fontSize:size, color:opts.color ?? C.ink, bold:!!opts.bold, alignment:opts.align ?? 'left', verticalAlignment:opts.valign ?? 'top', autoFit:'none', wrap:'square', insets:{left:0,right:0,top:0,bottom:0}, ...opts.style };
  return sh;
}
function rule(s,x,y,w,color=C.line) {
  return s.shapes.add({geometry:'line',position:{left:x,top:y,width:w,height:0},fill:'none',line:{fill:color,width:1}});
}
function slide(title, index, appendix=false) {
  const s=p.slides.add(); all.push(s); s.background.fill=C.bg;
  text(s, title,64,45,1152,68,44,{bold:true});
  rule(s,64,122,1152);
  text(s, appendix ? 'CS549  /  Q&A reference' : 'CS549  /  Project briefing  /  24 September 2026',64,681,1050,20,15,{color:C.muted});
  text(s,String(index).padStart(2,'0'),1160,678,56,24,18,{color:C.muted,align:'right'});
  return s;
}
function notes(s,title,time,script,sources=[]) {
  const body=`${time ? `Suggested speaking time: ${time} seconds\n\n` : 'Q&A reference slide\n\n'}${script}\n\nSources and provenance:\nCurrent Assignment 1 proposal, sections 2–4, and Assignment 2 proposal, sections 1–3 (23 September 2026).\n${sources.join('\n')}`;
  s.speakerNotes.textFrame.setText(body);
  noteRecords.push({title,time,script,sources});
}
async function picture(s,file,x,y,w,h,alt) {
  const blob=new Uint8Array(await fs.readFile(path.join(visuals,file)));
  return s.images.add({blob,contentType:file.endsWith('.png')?'image/png':'image/jpeg',position:{left:x,top:y,width:w,height:h},fit:'contain',alt});
}
function table(s,values,x,y,width,widths,heights,size=25) {
  const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width,height:heights.reduce((a,b)=>a+b,0),columnWidths:widths,values});
  t.styleOptions={headerRow:false,bandedRows:false};
  t.borders.assign({style:'solid',fill:C.line,width:1});
  for(let r=0;r<values.length;r++) {
    t.rows[r].height=heights[r];
    t.cells.block({row:r,column:0,rowCount:1,columnCount:values[0].length}).assign({margins:{left:15,right:15,top:13,bottom:10},anchor:'center'});
    for(let c=0;c<values[0].length;c++) {
      const cell=t.getCell(r,c); cell.fill=r===0?C.ink:(r%2===0?'#ECEEE8':C.bg);
      cell.text.style={typeface:font,fontSize:r===0?24:size,bold:r===0||c===0,color:r===0?C.white:C.ink,autoFit:'none',verticalAlignment:'middle',insets:{left:15,right:15,top:12,bottom:10}};
    }
  }
  return t;
}
function node(s,title,body,x,y,w,h,kind='normal') {
  const fill=kind==='fail'?C.redPale:kind==='clear'?C.goldPale:C.pale;
  const stroke=kind==='fail'?C.red:kind==='clear'?C.gold:C.olive;
  const n=s.shapes.add({geometry:'roundRect',name:title,position:{left:x,top:y,width:w,height:h},fill,line:{fill:stroke,width:1.8},borderRadius:9});
  n.text=[[{run:title,textStyle:{bold:true,fontSize:'25px'}}],[{run:body,textStyle:{fontSize:'23px'}}]];
  n.text.style={typeface:font,color:C.ink,alignment:'center',verticalAlignment:'middle',autoFit:'none',insets:{left:8,right:8,top:10,bottom:8}};
  return n;
}
function connect(s,a,b,from='right',to='left',arrow=true,kind='straight',color=C.muted) {
  // In DrawingML, the tail is the destination end of this connector.
  return s.shapes.connect(a,b,{kind,fromSide:from,toSide:to,line:{fill:color,width:2.2},...(arrow?{tail:{type:'triangle',width:'med',length:'med'}}:{})});
}
function point(s,x,y) {
  return s.shapes.add({geometry:'rect',name:'Restart routing anchor',position:{left:x,top:y,width:0.1,height:0.1},fill:'none',line:{fill:'none',width:0}});
}

// 1. Project and visual intent.
{
  const s=p.slides.add();all.push(s);s.background.fill=C.bg;
  text(s,'Paris Street Combat',64,34,1152,82,62,{bold:true});
  text(s,'A single-player first-person squad mission in Unreal Engine 5',64,118,1152,44,32);
  text(s,'Goal: make character actions, cover and NPC decisions work together',64,169,1152,40,27,{color:C.olive});
  text(s,'Yupu Guo (yg745), Group Leader     Yuqi Pu (yp549)     Jingdi Wu (jw2046)',64,218,1152,30,22,{color:C.muted});
  await picture(s,'paris-six-character-concept.png',64,263,1152,384,'Generated concept of the initial squad encounter across connected French city streets');
  text(s,'AI-generated concept informed by official France Liberation references. Illustrative layout, not gameplay.',64,653,1152,22,16,{color:C.muted});
  text(s,'CS549  /  24 September 2026',64,688,1050,20,15,{color:C.muted});
  text(s,'01',1160,682,56,24,18,{color:C.muted,align:'right'});
  notes(s,'Paris Street Combat',20,'Paris Street Combat is a single-player first-person squad mission in Unreal Engine 5, set during the August 1944 liberation period. Our goal is to make character actions, cover and NPC decisions work together. This image illustrates the intended experience. It is a concept, not a gameplay screenshot.',[
    `Meshingun Studio, WW2 – France Liberation: ${urls.fab}`,
    'Image: OpenAI ImageGen concept from the current proposals. Both official Meshingun gallery images served as appearance references. It does not establish the actual vendor map layout.'
  ]);
}
// 2. Asset pack only, without mission or roster decisions.
{
  const s=slide('WW2 – France Liberation',2);
  text(s,'Environment asset pack',64,161,470,43,31,{bold:true});
  text(s,'Meshingun Studio',64,211,470,36,27,{color:C.olive});
  text(s,'Existing city environment\nModular buildings and street props\nTextures and materials\nEnvironment assembly tools',64,286,474,215,27,{style:{lineSpacing:1.3}});
  await picture(s,'paris-environment-01.jpg',566,157,650,366,'Official Meshingun Studio France Liberation environment showcase with branding preserved');
  text(s,'Official supplier showcase',566,536,650,28,18,{color:C.muted});
  rule(s,64,583,1152);
  text(s,'An existing visual environment for our street combat project',64,601,1152,44,31,{bold:true});
  text(s,'Soldier and weapon assets will be selected separately.',64,647,1152,29,24,{color:C.muted});
  notes(s,'WW2 – France Liberation',35,'France Liberation is Meshingun Studio’s environment pack. It provides a large existing city with modular architecture, street props, textures, materials and environment-building tools. This gives us the visual setting for street combat. We can spend more of our effort on the interactive experience instead of building the whole city. The image is the supplier’s showcase. It does not demonstrate our gameplay. Soldier and weapon assets will be selected separately.',[
    urls.fab,
    'Official gallery image: https://media.fab.com/image_previews/gallery_images/282f0ee9-eb1d-44e3-b0cc-178ec3dbb90b/60c6bd58-9210-4dcd-9cd1-ea455a261b26.jpg'
  ]);
}
// 3. General mission progression. Checkpoint placement remains a design choice.
{
  const s=slide('Mission progression and checkpoints',3);
  text(s,'Proposed flow. Objective locations and checkpoint boundaries remain open.',64,146,1152,40,26,{color:C.olive});
  const a=node(s,'START / RESUME','Initial or saved\nmission state',64,250,200,130);
  const b=node(s,'CURRENT OBJECTIVE','Reach a location\nor clear a group',308,250,250,130);
  const c=node(s,'UPDATE STATE','Goal completed\nSave if configured',602,250,255,130,'clear');
  const d=node(s,'NEXT / COMPLETE','Advance objective\nor finish mission',901,250,300,130);
  connect(s,a,b);connect(s,b,c);connect(s,c,d);
  const q1=point(s,1051,212),q2=point(s,433,212);
  connect(s,d,q1,'top','bottom',false);connect(s,q1,q2,'left','right',false);connect(s,q2,b,'bottom','top');
  text(s,'More objectives',630,184,240,28,21,{color:C.muted});
  const death=node(s,'PLAYER DEATH','During an active objective',98,491,314,102,'fail');
  const retry=node(s,'RETRY','Restore latest checkpoint, or start if none',539,491,600,102);
  connect(s,death,retry,'right','left',true,'straight',C.red);
  connect(s,retry,b,'top','bottom',true,'elbow');
  text(s,'Checkpoint saving and ammunition / reinforcement rules are separate design decisions.',64,627,1152,39,24,{color:C.muted});
  notes(s,'Mission progression and checkpoints',45,'The flow is now a general mission structure rather than a fixed sequence of locations. The player works through objectives such as reaching a point or clearing an assigned group. Completing an objective updates progress and can save a checkpoint at a selected safe boundary. If the player dies, retry restores the latest saved mission state, or returns to the beginning when no checkpoint exists. A checkpoint records the state we choose to preserve, including ammunition and relevant NPC status. It does not automatically refill ammunition or replace fallen allies. Checkpoint locations, resource supplies and reinforcement rules will be decided during mission design and playtesting.',[
    'Current revised mission flow in both proposals.',
    'Epic SaveGame documentation: https://dev.epicgames.com/documentation/unreal-engine/saving-and-loading-your-game-in-unreal-engine'
  ]);
}
// 4. Keep the comparison compact. Terminology explanations belong in chat.
{
  const s=slide('Four pillars and concrete work',4);
  table(s,[
    ['Pillar','Specific work','Proposed implementation'],
    ['Animation','Coherent movement,\nfiring and reloading','Adapt purchased motion clips.\nControl transitions and action timing.'],
    ['Collision\nDetection','Character contact and\ncorrect weapon hits','Configure movement collision.\nCheck aim and objects blocking shots.'],
    ['Pathfinding &\nNavigation','Reach destinations\nand avoid crowding','UE NavMesh and MoveTo. Separate\ndestinations, avoidance and replanning.'],
    ['NPC AI','Perceive, decide\nand coordinate','Behavior Trees + AI Perception.\nIndividual state and squad assignments.'],
  ],64,160,1152,[244,362,546],[54,103,103,103,103],25);
  text(s,'Physics, animation and the UI must reflect the same gameplay state.',64,644,1152,32,24,{color:C.muted});
  notes(s,'Four pillars and concrete work',65,'The four pillars describe the work we will own. Animation means making purchased movement and weapon actions work on our characters, then keeping the transitions and timing coherent. Collision means checking how characters contact the scene and what a shot actually hits. Friendly-fire rules are a separate gameplay choice. Navigation means getting soldiers through the actual streets without everyone occupying the same destination or blocking a narrow passage. We will begin with Unreal’s NavMesh and MoveTo instead of committing to a separate A* implementation. NPC AI decides what soldiers do: observe, move, engage, search, or regroup. Individual decisions need simple squad coordination so roles and positions remain coherent as the population increases.',[urls.animation,urls.collision,urls.navigation,urls.behavior,urls.perception]);
}
// 5. Selected tools only. No unagreed version-control commitment.
{
  const s=slide('Proposed technical stack',5);
  const rows=[
    ['Development','Unreal Engine 5 + Blueprints','C++ only if a specific need appears'],
    ['Characters','Animation Blueprints, IK Retargeter, CharacterMovement','Compatible soldier, weapon and motion assets'],
    ['NPC systems','NavMesh, AIController, Behavior Trees, AI Perception','A squad coordinator connects individual decisions'],
    ['UI and progress','UMG, gameplay events and SaveGame','Health, ammunition, objectives and proposed checkpoints'],
  ];
  rows.forEach((r,i)=>{
    const y=163+i*110;
    text(s,r[0],64,y,240,42,27,{bold:true,color:C.olive});
    text(s,r[1],330,y,886,39,27,{bold:true});
    text(s,r[2],330,y+43,886,37,24,{color:C.muted});
    if(i<3)rule(s,64,y+94,1152);
  });
  text(s,'First check',64,620,240,38,25,{bold:true,color:C.gold});
  text(s,'Verify engine compatibility and the chosen character / weapon assets.',330,618,886,42,25);
  notes(s,'Proposed technical stack',40,'Our proposed stack stays inside Unreal Engine 5. Blueprints connect the character systems, NPC decisions, UI and mission state. Animation Blueprints control motion, with IK Retargeter available when purchased clips use a different skeleton. NavMesh supports movement, while Behavior Trees and perception support NPC decisions. We will add a small squad coordinator for shared assignments. UMG provides the UI, and SaveGame can store selected checkpoint data. The first technical check is compatibility between the environment, engine version and chosen soldier and weapon assets.',[urls.fab,urls.navigation,urls.behavior,urls.perception,
    'https://dev.epicgames.com/documentation/unreal-engine/widget-blueprints-in-umg-for-unreal-engine',
    'https://dev.epicgames.com/documentation/unreal-engine/saving-and-loading-your-game-in-unreal-engine'
  ]);
}
// 6. User-defined challenges, with room to explain rather than read dense lists.
{
  const s=slide('Hardest expected challenges',6);
  text(s,'01',64,181,68,58,45,{bold:true,color:C.gold});
  text(s,'Integrating gameplay into the environment',163,181,1053,45,33,{bold:true});
  text(s,'Connect the UI to character actions, collisions and combat.\nMake visual feedback agree with physical interactions.',163,245,1030,100,29);
  rule(s,163,371,1053);
  text(s,'02',64,407,68,58,45,{bold:true,color:C.gold});
  text(s,'Coordinating a growing NPC population',163,407,1053,45,33,{bold:true});
  text(s,'Coordinate movement, targets and individual decisions.\nAvoid crowding and conflicting actions as groups grow.',163,471,1030,100,29);
  text(s,'Both challenges require editor work, observation and repeated playtests.',64,625,1152,38,25,{color:C.olive});
  notes(s,'Hardest expected challenges',65,'We expect two main challenges. The first is integrating gameplay into the purchased environment. A health display or ammunition counter is only useful when it agrees with the actual character and weapon state. Likewise, characters need to move naturally around buildings and cover, and shot feedback must agree with collision results. This requires scene configuration, gameplay integration and visual checking. The second challenge is planning NPC movement and behavior as their number increases. Separate routes alone do not make a squad cooperate. We need shared assignments with individual perception and decisions, different destinations, and recovery when characters block one another. We must test whether the result looks coherent and whether the simulation remains responsive. Coding tools can help implement these parts, but judging their behavior in the actual city requires our own editor work and playtesting.',['Expected project challenges follow the team’s current priorities. No runtime validation is claimed.']);
}
// 7. Single closing slide, intentionally without footer or other content.
{
  const s=p.slides.add(); all.push(s); s.background.fill=C.bg;
  text(s,'Q&A',0,260,1280,200,112,{bold:true,align:'center',valign:'middle'});
  s.speakerNotes.textFrame.setText('Q&A');
  noteRecords.push({title:'Q&A',time:null,script:'Questions and discussion.',sources:[]});
}

const candidatePath=path.join(tmp,`candidate-${revision}.pptx`);
await (await PresentationFile.exportPptx(p)).save(candidatePath);
await fs.writeFile(path.join(tmp,`briefing-${revision}.json`),JSON.stringify(p.toProto(),null,2));
await fs.writeFile(path.join(tmp,`notes-${revision}.json`),JSON.stringify(noteRecords,null,2));
console.log(`Draft written: ${candidatePath}`);
const result=await finalizePresentation({workspaceDir:project,candidatePath,finalPath,
  pythonExecutable:path.join(runtime,'python/bin/python3'),
  integrityValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','4'],
  requiredNativeTableOwnerSlides:[4],requiredNativeChartOwnerSlides:[],
  fontPolicy:{basis:'design',families:[font]},verifyArtifactToolImport:true,
  receiptPath:path.join(tmp,`validation-${revision}.json`),
});
console.log(`Finalized: ${finalPath}`);
const renderDir=path.join(tmp,`renders-${revision}`);await fs.mkdir(renderDir,{recursive:true});
for(let i=0;i<all.length;i++) {
  const blob=await p.export({slide:all[i],format:'png',scale:1});
  await fs.writeFile(path.join(renderDir,`slide-${i+1}.png`),new Uint8Array(await blob.arrayBuffer()));
}
const rehearsal=['# Paris Street Combat — presentation notes','',
  '24 September 2026. Slides 1–6 total approximately four and a half minutes. Slide 7 is the closing Q&A slide.',
  '',...noteRecords.map((n,i)=>`## ${i+1}. ${n.title}${n.time?` (${n.time} seconds)`:''}\n\n${n.script}\n`)];
await fs.writeFile(path.join(output,'PRESENTATION_NOTES.md'),rehearsal.join('\n'));
console.log(`Rendered ${all.length} slides and saved presentation notes.`);
