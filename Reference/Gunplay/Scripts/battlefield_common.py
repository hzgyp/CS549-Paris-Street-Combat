"""Editor-only helpers for the first playable combat layer."""
from pathlib import Path
import unreal,sys
sys.path.insert(0,str(Path(__file__).parent))
from g1_graph import *
import build_first_asset_kit as kit
R=Path(__file__).resolve().parents[2]
_defaults={}
_authoring_refs=[]
def retain_spawners():
    # The experimental graph API creates transient node spawners. Keep their
    # Python wrappers alive across the compiler's GC while this build runs.
    typ=getattr(unreal,'BlueprintNodeSpawner',None)
    if typ:_authoring_refs.extend(unreal.ObjectIterator(typ))
    else:
        for obj in unreal.ObjectIterator():
            if obj:
                c=unreal.Object.get_class(obj)
                if c and str(unreal.Object.get_name(c)).endswith('NodeSpawner'):_authoring_refs.append(obj)
def compile_save(bp):
    retain_spawners();assert L.compile_blueprint(bp);kit.save(bp)
def member(g,bp,name,kind,default=''):
    if name in [str(n) for n in L.list_member_variable_names(bp)]:return
    tp=L.get_basic_type_by_name(kind) if isinstance(kind,str) else kind
    assert L.add_member_variable(bp,name,tp),name
    if default:_defaults.setdefault(bp.get_path_name(),{})[name]=(kind,default)
D='/Game/Normandy/Battlefield01';MC='/Game/Normandy/Blueprints/Core/BP_MissionController.BP_MissionController_C'
def path(n):return D+'/'+n
def cls(n):return path(n)+'.'+n+'_C'
def v(g,x,y,z):return pure(g,'math.MakeVector',X=x,Y=y,Z=z)
def add(g,a,b):return pure(g,'math.Add_DoubleDouble',A=a,B=b)
def mul(g,a,b):return pure(g,'math.Multiply_DoubleDouble',A=a,B=b)
def sub(g,a,b):return pure(g,'math.Subtract_DoubleDouble',A=a,B=b)
def now(g):return pure(g,'game.GetTimeSeconds')
def loc(g):return pure(g,'/Script/Engine.Actor.K2_GetActorLocation')
def plus(g,a,b):return pure(g,'math.Add_VectorVector',A=a,B=b)
def diff(g,a,b):return pure(g,'math.Subtract_VectorVector',A=a,B=b)
def lt(g,a,b):return pure(g,'math.Less_DoubleDouble',A=a,B=b)
def ge(g,a,b):return pure(g,'math.GreaterEqual_DoubleDouble',A=a,B=b)
def valid(g,a):return pure(g,'system.IsValid',Object=a)
def own(g,bp,n,**kw):return call(g,cls_path(bp)+'.'+n,**kw)
def create(n,parent=None):
    assert not A.does_asset_exist(path(n)),n+' already exists; do not regenerate live graphs'
    bp=L.create_blueprint_asset_with_parent(path(n),parent or unreal.Actor.static_class());assert bp
    # AddMemberVariable consults SkeletonGeneratedClass; fresh Actor assets do
    # not reliably have it until their first compile in UE 5.8.
    assert L.compile_blueprint(bp)
    return bp
def graph(bp):return unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
def assembly(bp):
    hs=kit.SUB.k2_gather_subobject_data_for_blueprint(bp);root=next(h for h in hs if kit.DATA.is_root_actor(kit.SUB.k2_find_subobject_data_from_handle(h)))
    h,reason=kit.SUB.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,new_class=unreal.SceneComponent,blueprint_context=bp));assert kit.DATA.is_handle_valid(h),reason;kit.SUB.rename_subobject(h,'BattleRoot');return h
def part(bp,root,n,mesh,mat,p=(0,0,0),s=(1,1,1),r=(0,0,0),collision=False):
    return kit.part(bp,root,n,A.load_asset(mesh),A.load_asset(mat),p,r,s,True,collision)
def finish(bp):
    for n in L.list_graph_names(bp):tidy(unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,n))
    retain_spawners();assert L.compile_blueprint(bp)
    d=unreal.get_default_object(bp.generated_class())
    for n,(kind,val) in _defaults.get(bp.get_path_name(),{}).items():
        if kind=='real':val=float(val)
        elif kind=='int':val=int(val)
        elif kind=='bool':val=val.lower()=='true'
        elif isinstance(val,str) and val.startswith('(X='):
            import re
            val=unreal.Vector(*[float(x) for x in re.findall(r'[XYZ]=([\d.\-]+)',val)])
        d.set_editor_property(n,val)
    kit.save(bp);unreal.log('BATTLEFIELD_BUILT '+bp.get_name());return bp
def sound(g,n,position,volume=1):return call(g,'game.PlaySoundAtLocation',Sound=path(n),Location=position,VolumeMultiplier=volume,PitchMultiplier=1,AttenuationSettings=path('ATT_Battlefield'))
def spawn(g,n,position,rotation='(Pitch=0,Yaw=0,Roll=0)',scale='(X=1,Y=1,Z=1)'):
    t=pure(g,'math.MakeTransform',Location=position,Rotation=rotation,Scale=scale)
    begin=call(g,'game.BeginDeferredActorSpawnFromClass',ActorClass=cls(n),SpawnTransform=t,CollisionHandlingOverride='AlwaysSpawn')
    end=call(g,'game.FinishSpawningActor',Actor=op(begin),SpawnTransform=t)
    link(op(begin,'then'),ip(end,'execute'));return begin,end
def event(bp,name):return L.add_event_override(bp,name,unreal.IntPoint(0,0))
