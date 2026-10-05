"""Apply the qualified shared-wrap profile with Unreal's Python commandlet.

Only six sampler-source properties in M_RoadMaster change. Textures, graph
connections, static switches, instances, geometry and physics are preserved.
The checks fail closed if the source content or effective texture settings drift.
"""
MASTER = '/Game/Carla/Static/GenericMaterials/000_Masters/M_RoadMaster'
INSTANCES = ('MI_Road_Asphalt_A', 'MI_Road_Asphalt_B',
             'MI_Road_Asphalt_B_LaneMarkingWhite',
             'MI_Road_Asphalt_B_LaneMarkingYellow', 'MI_Road_Rural_A')
NODES = ('MaterialExpressionTextureSample_12',
         'MaterialExpressionTextureSampleParameter2D_0',
         'MaterialExpressionTextureSampleParameter2D_1',
         'MaterialExpressionTextureSampleParameter2D_4',
         'MaterialExpressionTextureSampleParameter2D_5',
         'MaterialExpressionTextureSampleParameter2D_6')


def require_compatible(settings):
    expected = dict(address_x='TA_WRAP', address_y='TA_WRAP', filter='TF_DEFAULT',
                    lod_group='TEXTUREGROUP_WORLD', virtual_texture_streaming=False)
    if settings != expected:
        raise ValueError('Texture addressing/filter/group differs from shared-wrap profile')


def apply():
    import json
    import unreal
    master = unreal.load_asset(MASTER)
    assert master is not None
    instances = [unreal.load_asset('/Game/Carla/Static/GenericMaterials/Roads/' + n)
                 for n in INSTANCES]
    assert all(instances)
    nodes = {n.get_name(): n for n in unreal.ObjectIterator(unreal.MaterialExpressionTextureSample)
             if n.get_outer() == master}
    assert len(nodes) == 37, 'Road master graph changed; requalify the profile'
    before_count = unreal.MaterialEditingLibrary.get_num_material_expressions(master)

    def check(texture):
        assert texture is not None
        settings = {p: texture.get_editor_property(p).name for p in
                    ('address_x', 'address_y', 'filter', 'lod_group')}
        settings['virtual_texture_streaming'] = texture.get_editor_property('virtual_texture_streaming')
        require_compatible(settings)

    pending = []
    for name in NODES:
        node = nodes[name]
        current = node.get_editor_property('sampler_source')
        assert current in (unreal.SamplerSourceMode.SSM_FROM_TEXTURE_ASSET,
                           unreal.SamplerSourceMode.SSM_WRAP_WORLD_GROUP_SETTINGS)
        check(node.get_editor_property('texture'))
        if isinstance(node, unreal.MaterialExpressionTextureSampleParameter2D):
            parameter = node.get_editor_property('parameter_name')
            for instance in instances:
                check(unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(instance, parameter))
        if current == unreal.SamplerSourceMode.SSM_FROM_TEXTURE_ASSET:
            pending.append(node)
    assert len(pending) in (0, len(NODES)), 'Partial profile must be reconciled, not replayed'
    for node in pending:
        node.set_editor_property('sampler_source', unreal.SamplerSourceMode.SSM_WRAP_WORLD_GROUP_SETTINGS)
    if pending:
        unreal.MaterialEditingLibrary.recompile_material(master)
        assert unreal.MaterialEditingLibrary.get_num_material_expressions(master) == before_count
        assert unreal.EditorAssetLibrary.save_loaded_asset(master, only_if_is_dirty=False)
    unreal.log_warning('ROAD_SHARED_SAMPLERS=' + json.dumps(dict(
        asset=MASTER, changedNodes=[n.get_name() for n in pending],
        profileNodes=list(NODES), graphExpressions=before_count,
        outcome='APPLIED' if pending else 'ALREADY_APPLIED'), sort_keys=True))


if __name__ == '__main__':
    apply()
