"""Build the superseded 22 September English and Chinese proposal snapshots.

Do not use this script for the current Assignment 1 or Assignment 2 reports. Their
source is Tools/build_assignment_proposals.py; this builder remains only so the
dated provenance PDFs can be reproduced without silently rewriting history.

Requires reportlab and pypdf. Windows Arial / Microsoft YaHei fonts are embedded.
No Unreal execution or asset modification occurs in this document build.
"""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'Docs/Proposal'
FAB = 'https://www.fab.com/listings/dae418da-1969-444a-821c-c1f30a3f21b6'
HISTORY = 'https://www.museeliberation-leclerc-moulin.paris.fr/en/museum/la-liberation-de-paris'
INK, TEAL, GRAY = [colors.HexColor(c) for c in ('#172B38', '#176B74', '#52616B')]
PALE, LINE = colors.HexColor('#E7EFF0'), colors.HexColor('#D5DDDF')
WIDTH = 516

for name, filename in [('EN','arial.ttf'), ('EN-Bold','arialbd.ttf'), ('CN','msyh.ttc'), ('CN-Bold','msyhbd.ttc')]:
    pdfmetrics.registerFont(TTFont(name, str(Path('C:/Windows/Fonts') / filename), subfontIndex=0))
for family in ('EN','CN'):
    pdfmetrics.registerFontFamily(family, normal=family, bold=family+'-Bold', italic=family, boldItalic=family+'-Bold')

COPY = {
 'EN': {
  'title':'Paris Street Combat', 'tag':'CS549 / PROJECT PROPOSAL',
  'team_label':'PROJECT TEAM',
  'roles':['Team leader / Integration','Animation integration (proposed)','Environment / Rendering'],
  'pillars':'Primary pillars: <b>Rendering</b>  /  <b>Animation</b>  /  <b>Collision Detection</b>',
  'caption':'Environment references: Meshingun Studio, <i>WW2 - France Liberation</i> [1]. Supplier showcase images, not completed team gameplay. Lighting, vehicles and aerial elements shown do not expand our MVP scope.',
  'prd':'1. Product requirements',
  'concept':'A compact single-player FPS in a fictionalized Paris street during the August 1944 liberation period [2]. Normandy is background only. For PC FPS players and course reviewers, the goal is coherent interaction between visible feedback, weapon animation and physical shot obstruction, using existing assets.',
  'stories':'<b>User stories.</b> As a player, I want cover to block my muzzle even when my crosshair sees past it; fire/reload animations to agree with ammunition; and impacts to identify the surface hit. As a reviewer, I want matched comparisons that expose the team-authored mechanisms.',
  'scope_head':['Priority','Semester scope'],
  'scope':[
   ['Must','One outdoor street, one player weapon, one enemy configuration with a small group; move/aim/fire/reload/damage; one objective, win/fail/reset; coherent collision/animation/impact feedback; three pillar comparisons; Windows package.'],
   ['Should','Compatible crouch, minimal enemy movement, spatial audio, objective/health/ammo UI.'],
   ['Could','One feedback refinement or a second short approach, only after the complete MVP passes.'],
   ["Won\'t",'Landing/ocean; custom detailed characters; dynamic weather; driving; complex allies/civilians; broad interiors or destruction; multiplayer; open world; runtime LLM NPCs.']
  ],
  'history':'<b>Historical boundary.</b> Select exact date, units and equipment from sources before final asset approval. This is a fictional encounter, not a reconstruction of an exact street or incident.',
  'page2_tag':'TECHNICAL SPECIFICATION / MVP',
  'page2_title':'One encounter, three mechanisms',
  'stack':'<b>Stack.</b> Unreal Engine 5.8.x (installed baseline 5.8.2); Blueprint-first; Enhanced Input; materials/Niagara; Animation Blueprints/Montages and retargeting as needed; traces/Physical Materials; UMG; basic NPC behavior; Git/LFS. Compatibility and packaged execution remain development checks.',
  'mechanism_head':['Pillar','Team-authored mechanism','Planned comparison / evidence'],
  'mechanisms':[
   ['<b>Rendering</b>','Surface-driven impact selection, placement and parameters; bounded lifetime and active count.','Generic vs. surface-aware feedback under identical view/shot conditions; GPU frame time and effect count.'],
   ['<b>Animation</b>','Move/aim/fire/reload arbitration; guarded animation events synchronize ammo and action state.','Timer-only vs. event synchronization; repeated inputs, interrupted reloads and hand/weapon alignment.'],
   ['<b>Collision Detection</b>','Camera-intent trace followed by a muzzle-obstruction query; one consistent hit/surface result.','Camera-only vs. two-stage queries at walls/corners; false hits/blocking and frame-rate consistency.']
  ],
  'boundary':'<b>Engine and asset boundary.</b> Unreal supplies rendering, skeletal animation, scene queries and navigation. The team owns Blueprint rules, integration and experiments. The existing city pack supplies the environment; trailer soldiers and some combat VFX are excluded [1]. Acquire compatible character/weapon/action assets. NPC AI supports play, not a fourth pillar.',
  'ai':'<b>AI strategy.</b> AI assists research, documentation, scripts, Blueprint work, diagnostics and tests; no runtime AI service. After an unsuccessful 38-iteration experiment, we discontinued AI-led, from-scratch detailed character modeling. Fill gaps with existing assets, bounded adaptation, professional help or scope cuts.',
  'performance':'<b>Performance target.</b> Windows, 1920 x 1080, declared quality preset, aiming for 60 FPS on i9-12900F / RTX 3080 10 GB / 32 GB. Not yet measured. Record frame-time distribution, hitches and GPU memory under repeatable workloads; run the package on another machine.',
  'mvp_heading':'3. Narrow vertical slice and delivery',
  'mvp':'<b>MVP.</b> A 60-90-second street-corner encounter: move, aim, fire, reload, take damage, finish one objective or fail, then restart. One weapon, a small enemy group, fixed lighting and limited outdoor space.',
  'challenge':'<b>Hardest feature.</b> Keep muzzle obstruction, impact feedback, animated actions and ammunition consistent during close-cover combat and interrupted actions, using compatible acquired assets.',
  'proof':'<b>Proof by midterm.</b> Show a Windows package outside the editor, a complete encounter, three restarts, fixed corner/reload cases and matched pillar comparisons. Record settings/frame times and have a teammate reproduce the run. These are planned checks.',
  'delivery':'<b>Ownership and scope.</b> Yupu leads integration and proposed collision/gunplay work; Jingdi owns environment/rendering; Yuqi is proposed for animation integration (confirm at kickoff). Defer extra streets, weapons, moving doors and all excluded systems. Each member explains one mechanism and its evidence. Align technical depth with the instructor/mentor; retain actual approval email proof separately.',
  'refs':'References and visual credits',
  'ref1':'Meshingun Studio: WW2 - France Liberation (Fab; environment and images).',
  'ref2':'Musee de la Liberation de Paris: The Liberation of Paris (historical context).',
  'footer':'CS549 | Paris Street Combat | Project proposal',
 },
 'CN': {
  'title':'巴黎巷战', 'tag':'CS549 / 项目提案 · 中文版',
  'team_label':'项目成员',
  'roles':['组长 / 系统集成','动画集成（拟定）','场景 / 渲染'],
  'pillars':'核心支柱：<b>渲染 Rendering</b> / <b>动画 Animation</b> / <b>碰撞检测 Collision Detection</b>',
  'caption':'场景参考：Meshingun Studio 的 WW2 - France Liberation [1]。图片为供应商场景展示，并非本组已完成的玩法。图中灯光、车辆及空中元素不代表扩大 MVP 范围。',
  'prd':'1. 产品需求',
  'concept':'制作一个紧凑的单人第一人称射击（FPS）体验，背景为 1944 年 8 月巴黎解放时期的一段虚构街区战斗 [2]。诺曼底仅作为历史背景。面向 PC 射击游戏玩家及课程评审，使用现有资产，重点实现视觉反馈、武器动画与实际射击遮挡之间的一致交互。',
  'stories':'<b>用户故事。</b>作为玩家，我希望准星能看见墙后目标时，枪口仍会被面前掩体阻挡；开火、换弹动画与弹药状态一致；命中特效能体现表面材质。作为评审，我希望通过条件一致的对照演示，看清团队自行实现的技术机制。',
  'scope_head':['优先级','本学期范围'],
  'scope':[
   ['必须','一段室外街区、一种玩家武器、一种敌人配置及少量敌人；移动、瞄准、开火、换弹、受伤；一个目标、胜负与重置；一致的碰撞、动画和命中反馈；三个支柱的对照实验；Windows 打包。'],
   ['应当','有兼容动画时加入蹲伏；最小敌人移动、空间音效，以及目标、生命和弹药界面。'],
   ['可以','完整 MVP 通过后，再增加一项反馈优化或第二条短距离接近路线。'],
   ['不做','抢滩或海洋；从零精细角色建模；动态天气；驾驶；复杂友军或平民；大范围室内或破坏；多人、开放世界、运行时大语言模型 NPC。']
  ],
  'history':'<b>历史边界。</b>最终资产确认前，以史料确定具体日期、部队和装备。本项目是虚构遭遇战，不宣称精确复原某条街道或某一事件。',
  'page2_tag':'技术规格 / 最小可行版本',
  'page2_title':'一次遭遇战，三个技术机制',
  'stack':'<b>技术栈。</b>Unreal Engine 5.8.x（已安装基线为 5.8.2）；Blueprint 优先；Enhanced Input；材质 / Niagara；Animation Blueprint、Montage 及必要的动画重定向；射线查询 / Physical Material；UMG；基础 NPC 行为；Git/LFS。兼容性与打包运行将在开发阶段检查。',
  'mechanism_head':['技术支柱','团队自行实现的机制','计划对照与证据'],
  'mechanisms':[
   ['<b>渲染<br/>Rendering</b>','根据表面材质选择命中反馈，控制位置与参数；限制特效寿命和同时存在的数量。','相同视角和射击条件下，对比通用反馈与材质感知反馈；记录 GPU 帧时间和特效数量。'],
   ['<b>动画<br/>Animation</b>','协调移动、瞄准、开火与换弹；使用带状态校验的动画事件，同步弹药和动作状态。','对比纯计时与事件同步；检查重复输入、中断换弹，以及手部与武器对齐。'],
   ['<b>碰撞检测<br/>Collision<br/>Detection</b>','先用摄像机射线确定瞄准意图，再查询枪口路径遮挡；输出统一的命中与表面结果。','对比仅摄像机检测与两阶段检测；覆盖墙角、近掩体，记录误命中、误阻挡和不同帧率的一致性。']
  ],
  'boundary':'<b>引擎与资产边界。</b>Unreal 提供渲染、骨骼动画、场景查询和导航；团队负责 Blueprint 规则、集成及实验。现有城市包提供环境，不包含预告片士兵和部分战斗特效 [1]；角色、武器及动作需寻找兼容资产。NPC AI 支撑玩法，不作为第四项支柱。',
  'ai':'<b>AI 使用策略。</b>AI 协助调研、文档、脚本、Blueprint、诊断和测试；不依赖运行时 AI 服务。经过 38 轮未成功的角色实验，团队已停止 AI 从零制作精细角色的路线。缺失资产通过现有资源、有限改造、专业协助或缩减范围处理。',
  'performance':'<b>性能目标。</b>Windows、1920 x 1080、明确画质档位；在 i9-12900F / RTX 3080 10 GB / 32 GB 台式机上争取 60 FPS，目前尚未实测。以可复现负载记录帧时间分布、卡顿和显存占用，并在另一台电脑运行打包版本。',
  'mvp_heading':'3. 最小可行版本与交付',
  'mvp':'<b>MVP。</b>一段 60-90 秒街角遭遇战：移动、瞄准、开火、换弹、受伤，完成一个目标或失败，再重置。仅一种武器、少量敌人、固定灯光和有限室外区域。',
  'challenge':'<b>最难的问题。</b>使用兼容的现成资产，在贴近掩体战斗和动作被打断时，仍保持枪口遮挡、命中反馈、动作动画和弹药状态一致。',
  'proof':'<b>期中证明。</b>在编辑器外展示 Windows 包、完整遭遇战、连续三次重置、固定墙角与换弹案例，以及三个支柱的对照。记录设置和帧时间，由另一名组员复现。这些均为计划验收项。',
  'delivery':'<b>分工与范围。</b>Yupu 负责组长和集成，拟负责碰撞与枪战；Jingdi 负责场景和渲染；Yuqi 拟负责动画集成，启动时确认。额外街区、武器、可动门及已排除系统均后置。每人解释一项机制及证据。与教师或导师确认技术深度，另行保留真实批准邮件证明。',
  'refs':'参考资料与图片来源',
  'ref1':'Meshingun Studio：WW2 - France Liberation（Fab；环境与图片）。',
  'ref2':'巴黎解放博物馆：The Liberation of Paris（历史背景）。',
  'footer':'CS549 | 巴黎巷战 | 项目提案 · 中文版',
 }
}

def build(lang):
    c = COPY[lang]
    cn = lang == 'CN'
    body = ParagraphStyle('body', fontName=lang, fontSize=9.8 if not cn else 10,
        leading=13.0 if not cn else 14.5, textColor=INK, spaceAfter=6, wordWrap='CJK' if cn else None)
    small = ParagraphStyle('small',parent=body,fontSize=8.7 if not cn else 9,leading=11.4 if not cn else 13,spaceAfter=3)
    heading = ParagraphStyle('heading',parent=body,fontName=lang+'-Bold',fontSize=11.5,leading=15,textColor=TEAL,spaceBefore=6,spaceAfter=6)
    title = ParagraphStyle('title',parent=body,fontName=lang+'-Bold',fontSize=24 if not cn else 25,leading=30,spaceAfter=8)
    tag = ParagraphStyle('tag',parent=small,fontName=lang+'-Bold',textColor=TEAL,spaceAfter=5)
    name = ParagraphStyle('name',parent=body,fontName='EN-Bold',fontSize=12,leading=16,spaceAfter=2)
    def p(text,style=body): return Paragraph(text,style)
    def table(rows,widths):
        t=Table([[p(x,small) for x in row] for row in rows],colWidths=widths,hAlign='LEFT')
        t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),PALE),
            ('LINEBELOW',(0,0),(-1,0),.7,TEAL),('LINEBELOW',(0,1),(-1,-1),.35,LINE),
            ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
            ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
        return t
    people=[('Yupu Guo','yg745'),('Yuqi Pu','yp549'),('Jingdi Wu','jw2046')]
    team=Table([[[p(n,name),p(net,small),p(role,small)] for (n,net),role in zip(people,c['roles'])]],colWidths=[172]*3,hAlign='LEFT')
    team.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('BOX',(0,0),(-1,-1),.5,LINE),('INNERGRID',(0,0),(-1,-1),.5,LINE),
        ('LEFTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    images=Table([[Image(str(DEST/'Visuals/paris-environment-01.jpg'),width=253,height=142.3125),'',
                   Image(str(DEST/'Visuals/paris-environment-02.jpg'),width=253,height=142.3125)]],colWidths=[253,10,253],hAlign='LEFT')
    images.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)]))
    story=[p(c['tag'],tag),p(c['title'],title),p(c['team_label'],tag),team,Spacer(1,8),p(c['pillars']),
        Spacer(1,2),images,Spacer(1,4),p(c['caption'],small),p(c['prd'],heading),p(c['concept']),p(c['stories']),
        table([['<b>'+x+'</b>' for x in c['scope_head']]]+c['scope'],[61,455]),Spacer(1,6),p(c['history'],small),
        PageBreak(),p(c['page2_tag'],tag),p(c['page2_title'],title),p('2. '+('Technical specification' if not cn else '技术规格'),heading),p(c['stack']),
        table([['<b>'+x+'</b>' for x in c['mechanism_head']]]+c['mechanisms'],[87,210,219]),Spacer(1,8),
        p(c['boundary']),p(c['ai']),p(c['performance']),p(c['mvp_heading'],heading),p(c['mvp']),p(c['challenge']),p(c['proof']),p(c['delivery']),
        p(c['refs'],heading),p(f'[1] <link href="{FAB}" color="#176B74">{c["ref1"]}</link><br/>[2] <link href="{HISTORY}" color="#176B74">{c["ref2"]}</link>',small)]
    def footer(canvas,doc):
        canvas.setStrokeColor(LINE);canvas.line(42,39,570,39)
        canvas.setFont(lang,8);canvas.setFillColor(GRAY);canvas.drawString(42,26,c['footer']);canvas.drawRightString(570,26,f'{doc.page} / 2')
    suffix='_CN' if cn else ''
    output=DEST/f'CS549_Paris_Street_Combat_Proposal{suffix}.pdf'
    doc=SimpleDocTemplate(str(output),pagesize=(612,792),rightMargin=42,leftMargin=42,topMargin=32,bottomMargin=48,
        title=c['title']+' - CS549',author='Yupu Guo, Yuqi Pu, Jingdi Wu')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    reader=PdfReader(output)
    assert len(reader.pages)==2, f'{lang}: expected 2 pages, got {len(reader.pages)}'
    text='\n'.join(page.extract_text() for page in reader.pages)
    for person,_ in people: assert person in text, person
    assert len(reader.pages[0].images)==2
    print(f'{output}: 2 pages, 3 names, 2 images')

if __name__=='__main__':
    for language in ('EN','CN'): build(language)
