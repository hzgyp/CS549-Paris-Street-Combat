"""A simple non-emissive eye PBR alternative; vendor eye material stays untouched."""
import unreal


def build_eye_material(faction):
    base = '/Game/ParisCombat/Characters/Adaptation/Materials'
    path = base + '/M_EyePBR_' + faction + '_v1'
    material = unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else None
    if material:
        material.modify()
        material.set_editor_property('used_with_skeletal_mesh', True)
        unreal.MaterialEditingLibrary.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material, False)
        return material
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(path.split('/')[-1], base,
        unreal.Material, unreal.MaterialFactoryNew())
    material.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
    material.set_editor_property('used_with_skeletal_mesh', True)
    lib = unreal.MaterialEditingLibrary

    def node(cls, **properties):
        expression = lib.create_material_expression(material, cls, 0, 0)
        for key, value in properties.items():
            expression.set_editor_property(key, value)
        return expression

    def wire(source, dest, pin, output=''):
        if not lib.connect_material_expressions(source, output, dest, pin):
            raise RuntimeError('Could not wire ' + pin)

    root = '/Game/' + ('GermanSoldier' if faction == 'German' else 'USParatrooper') + '/Textures/Eyes/'
    coord = node(unreal.MaterialExpressionTextureCoordinate)
    center = node(unreal.MaterialExpressionConstant2Vector, r=.5, g=.5)
    offset = node(unreal.MaterialExpressionSubtract)
    wire(coord, offset, 'A'); wire(center, offset, 'B')
    scale = node(unreal.MaterialExpressionMultiply, const_b=1 / (.159 * 2))
    wire(offset, scale, 'A')
    add = node(unreal.MaterialExpressionAdd)
    wire(scale, add, 'A'); wire(center, add, 'B')
    iris = node(unreal.MaterialExpressionTextureSample, texture=unreal.load_asset(root + 'T_EyeBaseColor'),
        sampler_source=unreal.SamplerSourceMode.SSM_CLAMP_WORLD_GROUP_SETTINGS)
    sclera = node(unreal.MaterialExpressionTextureSample, texture=unreal.load_asset(root + 'T_EyeScleraBaseColor'))
    wire(add, iris, 'UVs'); wire(coord, sclera, 'UVs')
    mask = node(unreal.MaterialExpressionSphereMask, attenuation_radius=.159, hardness_percent=90.0)
    wire(coord, mask, 'A'); wire(center, mask, 'B')
    blend = node(unreal.MaterialExpressionLinearInterpolate)
    wire(sclera, blend, 'A', 'RGB'); wire(iris, blend, 'B', 'RGB'); wire(mask, blend, 'Alpha')
    lib.connect_material_property(blend, '', unreal.MaterialProperty.MP_BASE_COLOR)
    rough = node(unreal.MaterialExpressionConstant, r=.15)
    spec = node(unreal.MaterialExpressionConstant, r=.3)
    lib.connect_material_property(rough, '', unreal.MaterialProperty.MP_ROUGHNESS)
    lib.connect_material_property(spec, '', unreal.MaterialProperty.MP_SPECULAR)
    lib.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    return material
