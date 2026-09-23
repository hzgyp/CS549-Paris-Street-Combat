"""Import the first reusable mesh/material kit and build its Blueprint assemblies."""
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[2]
ASSETS=unreal.EditorAssetLibrary
TOOLS=unreal.AssetToolsHelpers.get_asset_tools()
MESHES='/Game/Normandy/Meshes/FirstKit'
MATS='/Game/Normandy/Materials/FirstKit'
BP_DIR='/Game/Normandy/Blueprints/Environment'
LIB=unreal.BlueprintEditorLibrary
MAT=unreal.MaterialEditingLibrary
SUB=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
DATA=unreal.SubobjectDataBlueprintFunctionLibrary

def save(asset):
    assert ASSETS.save_loaded_asset(asset,only_if_is_dirty=False),asset.get_name()

def import_mesh(name):
    path=MESHES+'/'+name
    if ASSETS.does_asset_exist(path):return ASSETS.load_asset(path)
    task=unreal.AssetImportTask()
    task.filename=str(ROOT/'Assets/Source/Normandy/FirstKit'/(name+'.obj'))
    task.destination_path=MESHES
    task.destination_name=name
    task.automated=True;task.save=True;task.replace_existing=True
    task.factory=unreal.FbxFactory()
    options=unreal.FbxImportUI()
    options.import_mesh=True;options.import_as_skeletal=False
    options.import_materials=False;options.import_textures=False
    options.mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH
    options.automated_import_should_detect_type=False
    data=options.static_mesh_import_data
    data.combine_meshes=True;data.auto_generate_collision=False
    data.convert_scene=False;data.convert_scene_unit=False
    data.generate_lightmap_u_vs=True
    task.options=options
    TOOLS.import_asset_tasks([task])
    mesh=ASSETS.load_asset(path)
    assert mesh,name
    editor=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem) or unreal.new_object(unreal.StaticMeshEditorSubsystem)
    editor.remove_collisions(mesh)
    assert editor.add_simple_collisions(mesh,unreal.ScriptingCollisionShapeType.BOX)>=0
    save(mesh)
    unreal.log('KIT MESH '+name+' bounds='+str(mesh.get_bounding_box()))
    return mesh

def import_texture(suffix,name,normal=False,linear=False):
    path='/Game/ThirdParty/PolyHaven/CoastSand01/'+name
    if ASSETS.does_asset_exist(path):return ASSETS.load_asset(path)
    task=unreal.AssetImportTask()
    task.filename=str(ROOT/'Assets/Source/ThirdParty/PolyHaven/coast_sand_01'/('coast_sand_01_'+suffix+'_1k.jpg'))
    task.destination_path='/Game/ThirdParty/PolyHaven/CoastSand01'
    task.destination_name=name;task.automated=True;task.save=True
    TOOLS.import_asset_tasks([task])
    texture=ASSETS.load_asset(path);assert texture,name
    if normal:texture.set_editor_property('compression_settings',unreal.TextureCompressionSettings.TC_NORMALMAP)
    if normal or linear:texture.set_editor_property('srgb',False)
    save(texture)
    return texture

def node(material,cls,x=0,y=0,**kw):
    result=MAT.create_material_expression(material,cls,x,y);assert result
    for key,value in kw.items():result.set_editor_property(key,value)
    return result

def wire(a,b,name,out=''):
    if name=='Input' and MAT.get_material_expression_input_names(b)==['None']:name='None'
    assert MAT.connect_material_expressions(a,out,b,name),(a.get_name(),b.get_name(),name)

def scalar(m,name,value,x=0,y=0):
    return node(m,unreal.MaterialExpressionScalarParameter,x,y,parameter_name=name,default_value=value)

def color(m,name,value,x=0,y=0):
    return node(m,unreal.MaterialExpressionVectorParameter,x,y,parameter_name=name,default_value=unreal.LinearColor(*value,1))

def operation(m,cls,a,b,x=0,y=0):
    n=node(m,cls,x,y);wire(a,n,'A');wire(b,n,'B');return n

def output(m,n,prop,out=''):
    assert MAT.connect_material_property(n,out,prop)

def finish_material(m):
    MAT.recompile_material(m);save(m);return m

def material(name):
    return TOOLS.create_asset(name,MATS,unreal.Material,unreal.MaterialFactoryNew())

def surface_master():
    name='M_KitSurface'
    if ASSETS.does_asset_exist(MATS+'/'+name):return ASSETS.load_asset(MATS+'/'+name)
    m=material(name)
    base=color(m,'BaseColor',(0.12,0.14,0.14),-500,0)
    rough=scalar(m,'Roughness',0.7,-500,200)
    metal=scalar(m,'Metallic',0,-500,400)
    output(m,base,unreal.MaterialProperty.MP_BASE_COLOR)
    output(m,rough,unreal.MaterialProperty.MP_ROUGHNESS)
    output(m,metal,unreal.MaterialProperty.MP_METALLIC)
    return finish_material(m)

def sand_master(textures):
    name='M_CoastSand_Master'
    m=ASSETS.load_asset(MATS+'/'+name) if ASSETS.does_asset_exist(MATS+'/'+name) else material(name)
    MAT.delete_all_material_expressions(m)
    position=node(m,unreal.MaterialExpressionWorldPosition,-1600,0)
    uv=node(m,unreal.MaterialExpressionComponentMask,-1400,0,r=True,g=True)
    wire(position,uv,'Input')
    tiling=scalar(m,'TileSizeCm',1500,-1400,220)
    scaled=operation(m,unreal.MaterialExpressionDivide,uv,tiling,-1150,0)
    samples=[]
    for i,texture in enumerate(textures):
        n=node(m,unreal.MaterialExpressionTextureSample,-900,i*260,texture=texture)
        if i==1:n.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
        elif i==2:n.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
        wire(scaled,n,'UVs');samples.append(n)
    wet=scalar(m,'Wetness',0,-1100,900)
    sat=node(m,unreal.MaterialExpressionSaturate,-850,900);wire(wet,sat,'Input')
    tint_dry=color(m,'DryTint',(0.85,0.80,0.70),-600,-220)
    tint_wet=color(m,'WetTint',(0.38,0.40,0.40),-600,-50)
    tint=node(m,unreal.MaterialExpressionLinearInterpolate,-300,-100)
    wire(tint_dry,tint,'A','RGB');wire(tint_wet,tint,'B','RGB');wire(sat,tint,'Alpha')
    base=node(m,unreal.MaterialExpressionMultiply,0,0)
    wire(samples[0],base,'A','RGB');wire(tint,base,'B')
    rough=node(m,unreal.MaterialExpressionLinearInterpolate,-100,450)
    dry_r=scalar(m,'DryRoughness',0.88,-500,500)
    wet_r=scalar(m,'WetRoughness',0.33,-500,700)
    wire(dry_r,rough,'A');wire(wet_r,rough,'B');wire(sat,rough,'Alpha')
    # Keep texture variation in both states rather than replacing roughness with a constant.
    variation=node(m,unreal.MaterialExpressionMultiply,150,450)
    wire(samples[2],variation,'A','R');wire(rough,variation,'B')
    normal_scale=scalar(m,'NormalStrength',0.45,-550,1050)
    flat=node(m,unreal.MaterialExpressionConstant3Vector,-550,1200,constant=unreal.LinearColor(0,0,1,1))
    normal=node(m,unreal.MaterialExpressionLinearInterpolate,-100,950)
    wire(flat,normal,'A');wire(samples[1],normal,'B','RGB');wire(normal_scale,normal,'Alpha')
    output(m,base,unreal.MaterialProperty.MP_BASE_COLOR)
    output(m,variation,unreal.MaterialProperty.MP_ROUGHNESS)
    output(m,normal,unreal.MaterialProperty.MP_NORMAL)
    return finish_material(m)

def instance(name,parent,scalars=None,vectors=None):
    path=MATS+'/'+name
    m=ASSETS.load_asset(path) if ASSETS.does_asset_exist(path) else TOOLS.create_asset(name,MATS,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    MAT.set_material_instance_parent(m,parent)
    for key,value in (scalars or {}).items():
        MAT.set_material_instance_scalar_parameter_value(m,key,value)
        assert abs(MAT.get_material_instance_scalar_parameter_value(m,key)-value)<0.001,(name,key)
    for key,value in (vectors or {}).items():MAT.set_material_instance_vector_parameter_value(m,key,unreal.LinearColor(*value,1))
    MAT.update_material_instance(m);save(m);return m

def new_assembly(name):
    path=BP_DIR+'/'+name
    if ASSETS.does_asset_exist(path):return ASSETS.load_asset(path),None
    bp=LIB.create_blueprint_asset_with_parent(path,unreal.Actor.static_class());assert bp
    handles=SUB.k2_gather_subobject_data_for_blueprint(bp)
    root=next(h for h in handles if DATA.is_root_actor(SUB.k2_find_subobject_data_from_handle(h)))
    h,reason=SUB.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,new_class=unreal.SceneComponent,blueprint_context=bp))
    assert DATA.is_handle_valid(h),reason
    assert SUB.rename_subobject(h,'AssemblyRoot')
    return bp,h

def part(bp,root,name,mesh,mat,loc=(0,0,0),rotation=(0,0,0),scale=(1,1,1),movable=False,collision=True):
    h,reason=SUB.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,new_class=unreal.StaticMeshComponent,blueprint_context=bp))
    assert DATA.is_handle_valid(h),reason
    assert SUB.rename_subobject(h,name)
    obj=DATA.get_object_for_blueprint(SUB.k2_find_subobject_data_from_handle(h),bp)
    assert obj,name
    obj.set_static_mesh(mesh);obj.set_material(0,mat)
    obj.set_editor_property('relative_location',unreal.Vector(*loc))
    obj.set_editor_property('relative_rotation',unreal.Rotator(pitch=rotation[0],yaw=rotation[1],roll=rotation[2]))
    obj.set_editor_property('relative_scale3d',unreal.Vector(*scale))
    obj.set_mobility(unreal.ComponentMobility.MOVABLE)
    obj.set_collision_profile_name('BlockAll' if collision else 'NoCollision')
    return obj

def ramp_function(bp):
    g=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,'SetRampAngle')
    degrees=g.add_graph_input_parameter('Degrees',LIB.get_basic_type_by_name('float'))
    ramp=g.add_get_member_variable_node('Ramp')
    clamp=g.add_call_function_node('/Script/Engine.KismetMathLibrary.FClamp')
    rot=g.add_call_function_node('/Script/Engine.KismetMathLibrary.MakeRotator')
    call=g.add_call_function_node('/Script/Engine.SceneComponent.K2_SetRelativeRotation')
    def ip(n,p):return LIB.find_input_pin(n,p)
    def op(n,p):return LIB.find_output_pin(n,p)
    def link(a,b):assert a.try_create_connection(b)
    link(degrees,ip(clamp,'Value'))
    assert ip(clamp,'Min').set_pin_value('-20.0');assert ip(clamp,'Max').set_pin_value('90.0')
    link(op(clamp,'ReturnValue'),ip(rot,'Pitch'))
    link(op(rot,'ReturnValue'),ip(call,'NewRotation'))
    link(op(ramp,'Ramp'),ip(call,'self'))
    link(g.find_graph_entry_pin(),ip(call,'execute'))

def build():
    meshes={n:import_mesh(n) for n in ['SM_SteelIBeam_240','SM_TimberBeam_240','SM_KitBox_100','SM_CraftDeck_Blockout','SM_CraftSide_Blockout','SM_CraftStern_Blockout','SM_CraftRamp_Hinged']}
    textures=[import_texture('diff','T_CoastSand01_Color'),import_texture('nor_dx','T_CoastSand01_Normal',normal=True),import_texture('rough','T_CoastSand01_Roughness',linear=True)]
    surface=surface_master();sand=sand_master(textures)
    mats={
      'steel':instance('MI_ObstacleSteel',surface,{'Roughness':0.62,'Metallic':0.85},{'BaseColor':(0.085,0.07,0.055)}),
      'wood':instance('MI_CraftPaintedWood',surface,{'Roughness':0.78,'Metallic':0},{'BaseColor':(0.19,0.23,0.22)}),
      'timber':instance('MI_ObstacleTimber',surface,{'Roughness':0.9,'Metallic':0},{'BaseColor':(0.19,0.125,0.07)}),
      'ramp':instance('MI_RampPaintedSteel',surface,{'Roughness':0.66,'Metallic':0},{'BaseColor':(0.13,0.16,0.16)}),
      'dry':instance('MI_CoastSand_Dry',sand,{'Wetness':0.0}),
      'wet':instance('MI_CoastSand_Wet',sand,{'Wetness':0.8}),
    }
    bp,root=new_assembly('BP_SteelHedgehog')
    if root:
        for name,rotation in [('BeamA',(45,0,0)),('BeamB',(-45,0,0)),('BeamC',(0,90,0))]:
            part(bp,root,name,meshes['SM_SteelIBeam_240'],mats['steel'],(0,0,92),rotation)
        part(bp,root,'JointPlate',meshes['SM_KitBox_100'],mats['steel'],(0,0,92),scale=(0.30,0.28,0.32))
        assert LIB.compile_blueprint(bp);save(bp)
    bp,root=new_assembly('BP_TimberObstacle')
    if root:
        part(bp,root,'InclinedBeam',meshes['SM_TimberBeam_240'],mats['timber'],(0,0,92),(45,0,0))
        part(bp,root,'Support',meshes['SM_TimberBeam_240'],mats['timber'],(52,0,85),(-60,0,0),(0.7,1,1))
        part(bp,root,'FootBrace',meshes['SM_TimberBeam_240'],mats['timber'],(20,0,12),(0,90,0),(0.65,1,1))
        assert LIB.compile_blueprint(bp);save(bp)
    bp,root=new_assembly('BP_LandingCraft_Blockout')
    if root:
        part(bp,root,'Deck',meshes['SM_CraftDeck_Blockout'],mats['wood'],movable=True)
        part(bp,root,'PortSide',meshes['SM_CraftSide_Blockout'],mats['wood'],(0,-155,0),movable=True)
        part(bp,root,'StarboardSide',meshes['SM_CraftSide_Blockout'],mats['wood'],(0,155,0),movable=True)
        part(bp,root,'Stern',meshes['SM_CraftStern_Blockout'],mats['wood'],(-550,0,0),movable=True)
        for y,name in [(-133,'BowPort'),(133,'BowStarboard')]:
            part(bp,root,name,meshes['SM_KitBox_100'],mats['wood'],(550,y,70),scale=(0.12,0.44,1.4),movable=True)
        for x in range(-450,501,100):
            for y in [-148,148]:
                part(bp,root,'Frame_'+str(x).replace('-','N')+'_'+str(y).replace('-','N'),meshes['SM_KitBox_100'],mats['wood'],(x,y,70),scale=(0.07,0.07,1.35),movable=True)
        part(bp,root,'Ramp',meshes['SM_CraftRamp_Hinged'],mats['ramp'],(550,0,0),(-12,0,0),movable=True)
        ramp_function(bp)
        assert LIB.compile_blueprint(bp);save(bp)
    for name in ['BP_SteelHedgehog','BP_TimberObstacle','BP_LandingCraft_Blockout']:
        blueprint=ASSETS.load_asset(BP_DIR+'/'+name)
        for handle in SUB.k2_gather_subobject_data_for_blueprint(blueprint):
            data=SUB.k2_find_subobject_data_from_handle(handle)
            obj=DATA.get_object_for_blueprint(data,blueprint)
            if isinstance(obj,unreal.SceneComponent):
                obj.set_editor_property('mobility',unreal.ComponentMobility.MOVABLE)
        assert LIB.compile_blueprint(blueprint);save(blueprint)
    unreal.log('KIT COMPLETE meshes=7 textures=3 assemblies=3')

if __name__=='__main__':build()
