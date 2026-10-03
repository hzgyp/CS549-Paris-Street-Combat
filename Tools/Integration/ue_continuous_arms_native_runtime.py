"""One-time native actor spawn and read-only observations, never display updates."""
import ast,hashlib,json
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
PACKAGE='/Game/ParisCombat/Blueprints/ContinuousArmsNativeV1/BP_PC_ContinuousArmsNativeV1'
def native_record():
    p=STORE/('Content/'+PACKAGE.removeprefix('/Game/')+'.uasset')
    record={'package':PACKAGE,'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    expected=json.loads((STORE/'Evidence/ContinuousArmsNativeV1/author_v3/result.json').read_text())['saved_trial']
    assert record==expected,'Native display bytes differ from the author checkpoint'
    return record
class NativeTrial:
    def __init__(self,world,player,existing=None):
        self.player=player
        if existing is None:
            cls=unreal.load_class(None,PACKAGE+'.'+PACKAGE.rsplit('/',1)[1]+'_C');assert cls
            api=unreal.get_default_object(unreal.GameplayStatics.static_class())
            self.view=api.call_method('BeginDeferredActorSpawnFromClass',args=(world,cls,unreal.Transform(),unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,player,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
            self.view.set_editor_property('Combatant',player)
            self.view=api.call_method('FinishSpawningActor',args=(self.view,unreal.Transform(),unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
        else:self.view=existing
        self.weapon=None
        path=Path(__file__).with_name('ue_continuous_arms_dynamic.py')
        names={'xyz','fingers','pose_delta','grasp'}
        tree=ast.parse(path.read_text())
        self.n={'unreal':unreal,'source':player.get_component_by_class(unreal.SkeletalMeshComponent),'vm':self.view.skeletal_mesh_component}
        exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(path),'exec'),self.n)
    def initialized(self):
        ready=bool(self.view.get_editor_property('Initialized'))
        if ready:self.weapon=self.view.get_editor_property('DisplayGun')
        return ready
    def update(self):
        # Compatibility with the regression observer API. UE Blueprint tick does all work.
        pass
    def snapshot(self):
        assert self.initialized()
        c=self.player.get_component_by_class(unreal.CameraComponent)
        return {'finger_local_delta':self.n['pose_delta'](),'camera_relative_cm':self.n['xyz'](c.get_editor_property('relative_location')),
                'fov':c.get_editor_property('field_of_view'),'original_anim_class':self.n['source'].get_anim_instance().get_class().get_name(),
                'display_bound':self.player.get_editor_property('WeaponAppearance')==self.weapon,'arms_visible':self.n['vm'].is_visible(),
                'display_updates':'UE Blueprint PostUpdateWork; Python observer update is no-op'}
