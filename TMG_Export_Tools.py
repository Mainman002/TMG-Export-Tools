import bpy, sys, os, platform
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, FloatProperty
from bpy.types import Operator


def _change_export_presets(self, context):
    scene = context.scene
    tmg_exp_vars = scene.tmg_exp_vars

    if tmg_exp_vars.exp_pref_presets == 'UE4':
        tmg_exp_vars.exp_export_format = 'fbx'
        scene.tmg_exp_vars.exp_uvs_name = 'UVChannel_'
        scene.tmg_exp_vars.exp_uvs_start_int = 1

    if tmg_exp_vars.exp_pref_presets == 'Unity':
        tmg_exp_vars.exp_export_format = 'fbx'
        scene.tmg_exp_vars.exp_uvs_name = 'UV'
        scene.tmg_exp_vars.exp_uvs_start_int = 1

    if tmg_exp_vars.exp_pref_presets == 'Godot':
        tmg_exp_vars.exp_export_format = 'gltf_embedded'
        scene.tmg_exp_vars.exp_uvs_name = 'UV_'
        scene.tmg_exp_vars.exp_uvs_start_int = 1
        
    return
    

class TMG_Export_Properties(bpy.types.PropertyGroup):
    
    ## Menu Categories
    exp_category : bpy.props.BoolProperty(default=False)
    exp_object_category : bpy.props.BoolProperty(default=False)
    exp_uv_category : bpy.props.BoolProperty(default=False)
    exp_leaf_bones : bpy.props.BoolProperty(default=False, description='Add bone to armature ends')

    use_collection_name : bpy.props.BoolProperty( name="Use Collection Name", default=True, description='Exports into nested folder by collection name' )
    
    exp_pref_presets : bpy.props.EnumProperty(name='App Presets', default='UE4', description='Presets for different apps',
    items=[
    ('UE4', 'UE4', ''),
    ('Unity', 'Unity', ''),
    ('Godot', 'Godot', '')], update=_change_export_presets)
    
    exp_export_format : bpy.props.EnumProperty(name='Export Type', default='fbx', description='Export model filetype',
    items=[
    ('fbx', 'fbx', ''),
    ('obj', 'obj', ''),
    ('glb', 'glb', ''),
    ('gltf_separate', 'gltf+', '')])
    
    ## Default FBX Export Options
    exp_directory : bpy.props.StringProperty(name='Directory', description='Sets the folder directory path for models to export into')
    exp_folder_by_type : bpy.props.BoolProperty(default=False, description='Exports into nested folder by model type')
    exp_use_selection : bpy.props.BoolProperty(default=True, description='If you want to export only selected or everything in your blend file (Might not work correctly)')
    exp_apply_unit_scale : bpy.props.BoolProperty(default=True, description='Takes into account current Blend Unit scale, else use export units scale')
    exp_use_tspace : bpy.props.BoolProperty(default=True, description='Apply global space transforms to object rotations, else only axis space is written to model file')
    exp_embed_textures : bpy.props.BoolProperty(default=False, description='Inclued textures used in the materials')
    exp_use_mesh_modifiers : bpy.props.BoolProperty(default=True, description='Apply modifiers to mesh objects !WARNING! prevents exporting shape keys')
    
    ## Object Transform Options
    exp_apply_mesh : bpy.props.BoolProperty(default=False, description='Converts object to Mesh applying everything !WARNING! will apply all modifiers')
    exp_reset_location : bpy.props.BoolProperty(default=True, description='Sets Location values to 0 (Scene Origin)')
    exp_reset_rotation : bpy.props.BoolProperty(default=False, description='Sets Rotation values to 0')
    exp_reset_scale : bpy.props.BoolProperty(default=False, description='Sets Scale values to 0')
    
    ## UV Layer Options
    exp_uvs_name : bpy.props.StringProperty(name='UV Names', default='UVChannel_', description='UV layer name')
    exp_pack_single_lightmap_uv : bpy.props.BoolProperty(default=False, description='Pack UV layer 2 to single UV area !WARNING! will unwrap the 2nd UV layer')
    exp_rename_uvs : bpy.props.BoolProperty(default=False, description='Sets UV layer names to UVChannel_1 and UVChannel_2')
    exp_uvs_start_int : bpy.props.IntProperty(name='UV Start Index', default=1, min=0, soft_max=1, step=1, description='Integer value placed at the end of UV layer names')
    exp_add_lightmap_uv : bpy.props.BoolProperty(default=False, description='Adds a 2nd UV layer for use as Lightmaps')
    exp_unwrap_lightmap_uv : bpy.props.BoolProperty(default=False, description='Unwraps UV layer 2 !WARNING! will unwrap the 2nd UV layer')
    
    exp_unwrap_method : bpy.props.EnumProperty(name='Unwrap Method', default='0', description='Method used when unwrapping lightmaps',
    items=[
    ('0', 'Smart UV Project', 'Uses Smart UV Project (Recomended if Lightmap method failes)'),
    ('1', 'Lightmap Pack', 'Uses Lightmap Pack (Good for basic meshes, more complex meshes may fail)')])
    
    exp_UVpack_margin : bpy.props.FloatProperty(name='UVpack Margin', default=0.005, soft_min=0.001, soft_max=0.1, step=0.001, precision=3, description='Space around UV islands when packing UVs')
    
#    exp_lightmap_res : bpy.props.EnumProperty(name='Lightmap Resolution', default='128', description='Lightmap texture resolution to pack UVs in',
#    items=[
#    ('64', '64', ''),
#    ('128', '128', ''),
#    ('196', '196', ''),
#    ('256', '256', ''),
#    ('512', '512', ''),
#    ('1024', '1024', '')])


def _mode_switch(_mode):
    if bpy.context.active_object:
        bpy.ops.object.mode_set(mode=_mode)
    return{"Finished"}


def _objs_loop(objs=None):
    return objs
    return{'FINISHED'}


def _parent_loop(_parents=None):
    return _parents
    return{'FINISHED'}


def _ob_group_switch(ob):
    _mode_switch('OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
    ob.select_set(state=True)
    bpy.context.view_layer.objects.active = ob
    return ob
    return{'FINISHED'}


def _cursor_to_obj(ob=None):
    if ob:
        bpy.context.scene.cursor.location = ob.location
    return{'FINISHED'}


def _apply_mesh(_ob=None):
    scene = bpy.context.scene
    tmg_exp_vars = scene.tmg_exp_vars
    
    if _ob:
        bpy.ops.object.convert(target='MESH')
    return{'FINISHED'}


def _center_obj(ob=None):
    if ob:
        ob.location = (0, 0, 0)
    return{'FINISHED'}


def _unwrap(_ob):
    scene = bpy.context.scene
    tmg_exp_vars = scene.tmg_exp_vars
    
    if _ob.type == 'MESH':
        print('\nUnwrapping: ', _ob)
        
        if len(_ob.data.uv_layers) < 1:
            _name = str(scene.tmg_exp_vars.exp_uvs_name + str(tmg_exp_vars.exp_uvs_start_int))
            _ob.data.uv_layers.new(name=_name)
        
        for _int in range(0,len(_ob.data.uv_layers)):
            if tmg_exp_vars.exp_rename_uvs:
                _name = str(scene.tmg_exp_vars.exp_uvs_name + str(tmg_exp_vars.exp_uvs_start_int))
                _ob.data.uv_layers[0].name = str(_name)
            
            if tmg_exp_vars.exp_add_lightmap_uv and len(_ob.data.uv_layers) < 2:
                _name = str(scene.tmg_exp_vars.exp_uvs_name + '%s') % str(_int+tmg_exp_vars.exp_uvs_start_int+1)
                _ob.data.uv_layers.new(name=_name)
            
            if tmg_exp_vars.exp_rename_uvs and len(_ob.data.uv_layers) > 1:
                _name = str(scene.tmg_exp_vars.exp_uvs_name + '%s') % str(_int+tmg_exp_vars.exp_uvs_start_int)
                _ob.data.uv_layers[_int].name = str(_name)
                
            if len(_ob.data.uv_layers)-1 >= 1:
                _ob.data.uv_layers[1].active = True
        
        if tmg_exp_vars.exp_unwrap_lightmap_uv and len(_ob.data.uv_layers) > 1:
            _mode_switch('EDIT')
            bpy.context.scene.tool_settings.use_uv_select_sync = True
            bpy.ops.mesh.reveal()
            bpy.ops.mesh.select_all(action='SELECT')
            
            if tmg_exp_vars.exp_unwrap_method == '0':
                bpy.ops.uv.smart_project()
                
            if tmg_exp_vars.exp_unwrap_method == '1':
                bpy.ops.uv.lightmap_pack(
                PREF_CONTEXT='SEL_FACES', 
                PREF_PACK_IN_ONE=True, 
                PREF_NEW_UVLAYER=False, 
                PREF_APPLY_IMAGE=False, 
                PREF_IMG_PX_SIZE=256, 
                PREF_BOX_DIV=24, 
                PREF_MARGIN_DIV=1.0)
            
            if tmg_exp_vars.exp_unwrap_lightmap_uv:
                bpy.ops.uv.pack_islands(margin=tmg_exp_vars.exp_UVpack_margin)
    return{'FINISHED'}


def _export(_col_name, _name, _path):
    scene = bpy.context.scene
    tmg_exp_vars = scene.tmg_exp_vars
    _new_path = None

    if platform.system() != "Windows":
        _slash = "/"
    else:
        _slash = str( "\\" )

    print( platform.system() )

    if tmg_exp_vars.exp_folder_by_type: 
        if not os.path.exists( str( _path + tmg_exp_vars.exp_export_format + _slash ) ): os.mkdir( str( _path + tmg_exp_vars.exp_export_format + _slash ) )
        if tmg_exp_vars.use_collection_name and not os.path.exists( str( _path + tmg_exp_vars.exp_export_format + _slash + _col_name + _slash ) ): os.mkdir( str( _path + tmg_exp_vars.exp_export_format + _slash + _col_name + _slash ) )
    else: 
        if tmg_exp_vars.use_collection_name and not os.path.exists( str( _path + _col_name + _slash ) ): os.mkdir( str( _path + _col_name + _slash ) )
        
    if not tmg_exp_vars.exp_export_format == 'glb' or not tmg_exp_vars.exp_export_format == 'gltf_embedded' or not tmg_exp_vars.exp_export_format == 'gltf_separate':
        if tmg_exp_vars.exp_folder_by_type and not tmg_exp_vars.use_collection_name: _new_path = str( _path + tmg_exp_vars.exp_export_format + _slash + _name + '.' + tmg_exp_vars.exp_export_format )
        elif tmg_exp_vars.exp_folder_by_type and tmg_exp_vars.use_collection_name and _col_name: _new_path = str( _path + tmg_exp_vars.exp_export_format + _slash + _col_name + _slash + _name + '.' + tmg_exp_vars.exp_export_format )
        elif not tmg_exp_vars.exp_folder_by_type and tmg_exp_vars.use_collection_name and _col_name: _new_path = str( _path + _col_name + _slash + _name + '.' + tmg_exp_vars.exp_export_format )
        else: _new_path = str( _path + _slash + _name + '.' + tmg_exp_vars.exp_export_format )

    if tmg_exp_vars.exp_export_format == 'fbx':
        bpy.ops.export_scene.fbx(
            filepath=_new_path, 
            check_existing=True, 
            filter_glob='*.fbx', 
            use_selection=scene.tmg_exp_vars.exp_use_selection, 
            use_visible=False, 
            use_active_collection=False, 
            global_scale=1.0, 
            apply_unit_scale=scene.tmg_exp_vars.exp_apply_unit_scale, 
            apply_scale_options='FBX_SCALE_NONE', 
            use_space_transform=True, 
            bake_space_transform=False, 
            object_types={'ARMATURE', 
            'CAMERA', 
            'EMPTY', 
            'LIGHT', 
            'MESH', 
            'OTHER'}, 
            use_mesh_modifiers=scene.tmg_exp_vars.exp_use_mesh_modifiers, 
            use_mesh_modifiers_render=True, 
            mesh_smooth_type='EDGE', 
            colors_type='SRGB', 
            prioritize_active_color=False, 
            use_subsurf=False, 
            use_mesh_edges=False, 
            use_tspace=scene.tmg_exp_vars.exp_use_tspace, 
            use_triangles=False, 
            use_custom_props=False, 
            add_leaf_bones=scene.tmg_exp_vars.exp_leaf_bones, 
            primary_bone_axis='Y', 
            secondary_bone_axis='X', 
            use_armature_deform_only=False, 
            armature_nodetype='NULL', 
            bake_anim=True, 
            bake_anim_use_all_bones=True, 
            bake_anim_use_nla_strips=True, 
            bake_anim_use_all_actions=True, 
            bake_anim_force_startend_keying=True, 
            bake_anim_step=1.0, 
            bake_anim_simplify_factor=1.0, 
            path_mode='AUTO', 
            embed_textures=scene.tmg_exp_vars.exp_embed_textures, 
            batch_mode='OFF', 
            use_batch_own_dir=True, 
            use_metadata=True, 
            axis_forward='-Z', 
            axis_up='Y')

    elif tmg_exp_vars.exp_export_format == 'obj':
        bpy.ops.wm.obj_export(
            filepath=_new_path, 
            # check_existing=True, 
            filter_blender=False, 
            filter_backup=False, 
            filter_image=False, 
            filter_movie=False, 
            filter_python=False, 
            filter_font=False, 
            filter_sound=False, 
            filter_text=False, 
            filter_archive=False, 
            filter_btx=False, 
            filter_collada=False, 
            filter_alembic=False, 
            filter_usd=False, 
            filter_obj=False, 
            filter_volume=False, 
            filter_folder=True, 
            filter_blenlib=False, 
            filemode=8, 
            display_type='DEFAULT', 
            sort_method='DEFAULT', 
            export_animation=False, 
            start_frame=-2147483648, 
            end_frame=2147483647, 
            forward_axis='NEGATIVE_Z', 
            up_axis='Y', 
            global_scale=1.0, 
            apply_modifiers=scene.tmg_exp_vars.exp_use_mesh_modifiers, 
            export_eval_mode='DAG_EVAL_VIEWPORT', 
            export_selected_objects=scene.tmg_exp_vars.exp_use_selection, 
            export_uv=True, 
            export_normals=True, 
            export_colors=False, 
            export_materials=True, 
            export_pbr_extensions=False, 
            path_mode='AUTO', 
            export_triangulated_mesh=False, 
            export_curves_as_nurbs=False, 
            export_object_groups=False, 
            export_material_groups=False, 
            export_vertex_groups=False, 
            export_smooth_groups=False, 
            smooth_group_bitflags=False, 
            filter_glob='*.obj;*.mtl'
            )
        
    elif tmg_exp_vars.exp_export_format == 'glb' or tmg_exp_vars.exp_export_format == 'gltf_embedded' or tmg_exp_vars.exp_export_format == 'gltf_separate':
        if tmg_exp_vars.exp_folder_by_type and not tmg_exp_vars.use_collection_name: _new_path = str( _path + tmg_exp_vars.exp_export_format + _slash + _name )
        elif tmg_exp_vars.exp_folder_by_type and tmg_exp_vars.use_collection_name and _col_name: _new_path = str( _path + tmg_exp_vars.exp_export_format + _slash + _col_name + _slash + _name )
        elif not tmg_exp_vars.exp_folder_by_type and tmg_exp_vars.use_collection_name and _col_name: _new_path = str( _path + _col_name + _slash + _name )
        else: _new_path = str( _path + _slash + _name )
        
        bpy.ops.export_scene.gltf(
            filepath=_new_path, 
            # check_existing=True, 
            export_import_convert_lighting_mode='SPEC', 
            gltf_export_id='', 
            export_format=tmg_exp_vars.exp_export_format.upper(), 
            # ui_tab='GENERAL', 
            # export_copyright='', 
            export_image_format='AUTO', 
            export_image_add_webp=False, 
            export_image_webp_fallback=False, 
            export_texture_dir=_path, 
            export_jpeg_quality=75, 
            export_image_quality=75, 
            export_keep_originals=False, 
            export_texcoords=True, 
            export_normals=True, 
            export_draco_mesh_compression_enable=False, 
            export_draco_mesh_compression_level=6, 
            export_draco_position_quantization=14, 
            export_draco_normal_quantization=10, 
            export_draco_texcoord_quantization=12, 
            export_draco_color_quantization=10, 
            export_draco_generic_quantization=12, 
            export_tangents=False, 
            export_materials='EXPORT', 
            export_colors=True, 
            export_attributes=False, 
            use_mesh_edges=False, 
            use_mesh_vertices=False, 
            export_cameras=False, 
            use_selection=scene.tmg_exp_vars.exp_use_selection, 
            use_visible=False, 
            use_renderable=False, 
            use_active_collection_with_nested=True, 
            use_active_collection=False, 
            use_active_scene=False, 
            export_extras=False, 
            export_yup=True, 
            export_apply=scene.tmg_exp_vars.exp_use_mesh_modifiers, 
            export_animations=True, 
            export_frame_range=False, 
            export_frame_step=1, 
            export_force_sampling=True, 
            export_animation_mode='ACTIONS', 
            export_nla_strips_merged_animation_name='Animation', 
            export_def_bones=False, 
            export_hierarchy_flatten_bones=False, 
            export_optimize_animation_size=True, 
            export_optimize_animation_keep_anim_armature=True, 
            export_optimize_animation_keep_anim_object=False, 
            export_negative_frame='SLIDE', 
            export_anim_slide_to_zero=False, 
            export_bake_animation=False, 
            export_anim_single_armature=True, 
            export_reset_pose_bones=True, 
            export_current_frame=False, 
            export_rest_position_armature=True, 
            export_anim_scene_split_object=True, 
            export_skins=True, 
            export_influence_nb=4, 
            export_all_influences=False, 
            export_morph=True, 
            export_morph_normal=True, 
            export_morph_tangent=False, 
            export_morph_animation=True, 
            export_morph_reset_sk_data=True, 
            export_lights=False, 
            export_try_sparse_sk=True, 
            export_try_omit_sparse_sk=False, 
            export_gpu_instances=False, 
            export_nla_strips=True, 
            export_original_specular=False, 
            # will_save_settings=False, 
            filter_glob='*.glb;*.gltf'
            )
        
    return{'FINISHED'}


def _obj_reset(ob=None):
    if ob:
        ob.location = bpy.context.scene.cursor.location
    return{'FINISHED'}


def main(_directory):
    print('\nSTART: ')
    
    scene = bpy.context.scene
    tmg_exp_vars = scene.tmg_exp_vars
    
    _check = os.path.exists(_directory)
    
    if not _check:
        os.mkdir(path=_directory)
    
    _path = _directory
    print(str('Directory: ' + _path + '\n'))
    
    _mode_switch('OBJECT')
    
    _obs = _objs_loop(bpy.context.selected_objects)
    _previous_obs = _obs
    _parents = []
    temp_list = []
    
    if _obs:
        for obj in _obs:
            if obj.type == 'MESH':
                _ob_group_switch(obj)
                if tmg_exp_vars.exp_apply_mesh:
                    _apply_mesh(obj)
            
            if not obj.parent:
                _parents.append(obj)
                
        for obj in _parents:
            if tmg_exp_vars.exp_reset_location:
                print('\nCursor To: ', obj.name)
                _cursor_to_obj(obj)
                
                print('\nTo Center: ', obj.name)
                _center_obj(obj)
            
            if tmg_exp_vars.exp_pack_single_lightmap_uv:
                obj = _ob_group_switch(obj)
                if obj.type != 'MESH':
                    print('\nSKIPPING UNWRAP: ', obj.name)
                    obj.select_set(state=False)
                    bpy.context.view_layer.objects.active = None
                    if len(bpy.context.selected_objects) > 0:
                        bpy.context.view_layer.objects.active = bpy.context.selected_objects[-1]
                        bpy.context.active_object.select_set(state=True)
                    
                for ob in bpy.context.selected_objects:
                    _unwrap(ob)
            else:
                _ob_group_switch(obj)
                for ob in bpy.context.selected_objects:
                    if ob.type != 'MESH':
                        print('\nSKIPPING UNWRAP: ', ob.name)
                        ob.select_set(state=False)

                if len(bpy.context.selected_objects) > 0:
                    bpy.context.view_layer.objects.active = bpy.context.selected_objects[-1]
                    bpy.context.active_object.select_set(state=True)
                    temp_list = []
                    temp_list = bpy.context.selected_objects
                            
            for ob in temp_list:
                bpy.ops.object.select_all(action='DESELECT')
                ob.select_set(state=True)
                bpy.context.view_layer.objects.active = ob
                _unwrap(ob)
                _mode_switch('OBJECT')
                
            _mode_switch('OBJECT')
            _ob_group_switch(obj)
            print('\nOBJS: ', bpy.context.selected_objects)

            col_name = None
            
            for collection in obj.users_collection:
                col_name = collection.name

            _export(col_name, obj.name, _path)
            
            if tmg_exp_vars.exp_reset_location:
                print('\nLocation Reset: ', obj.name)
                _obj_reset(obj)
            
    else:
        print('\nNo Objects')
    
    bpy.ops.object.select_all(action='DESELECT')
    for ob in _previous_obs:
        ob.select_set(state=True)
    bpy.context.view_layer.objects.active = _previous_obs[-1]
    
    print(str('Directory: ' + _path + '\nFINISHED'))

    if tmg_exp_vars.exp_apply_mesh:
        bpy.ops.ed.undo_push()
        bpy.ops.ed.undo()
    
    return{'FINISHED'}


class OBJECT_OT_TMG_Reset_Properties(bpy.types.Operator):
    bl_idname = 'wm.object_tmg_reset_properties'
    bl_label = 'Reset Properties'
    bl_description = 'Resets export properties to default values'
    bl_options  = {'REGISTER', 'UNDO'}
        
    def execute(self, context):
        scene = context.scene
        tmg_exp_vars = scene.tmg_exp_vars
        
        scene.tmg_exp_vars.exp_use_selection = True
        scene.tmg_exp_vars.exp_apply_unit_scale = True
        scene.tmg_exp_vars.exp_use_tspace = True
        scene.tmg_exp_vars.exp_use_mesh_modifiers = True
        scene.tmg_exp_vars.exp_embed_textures = False
        
        scene.tmg_exp_vars.exp_apply_mesh = False
        scene.tmg_exp_vars.exp_reset_location = True
        scene.tmg_exp_vars.exp_reset_rotation = False
        scene.tmg_exp_vars.exp_reset_scale = False
        
        if tmg_exp_vars.exp_pref_presets == 'UE4':
            scene.tmg_exp_vars.exp_uvs_name = 'UVChannel_'
            scene.tmg_exp_vars.exp_uvs_start_int = 1
        
        if tmg_exp_vars.exp_pref_presets == 'Unity':
            scene.tmg_exp_vars.exp_uvs_name = 'UV'
            scene.tmg_exp_vars.exp_uvs_start_int = 1
        
        if tmg_exp_vars.exp_pref_presets == 'Godot':
            scene.tmg_exp_vars.exp_uvs_name = 'UV_'
            scene.tmg_exp_vars.exp_uvs_start_int = 1
            
        scene.tmg_exp_vars.exp_rename_uvs = False
        scene.tmg_exp_vars.exp_add_lightmap_uv = False
        scene.tmg_exp_vars.exp_unwrap_lightmap_uv = False
#        scene.tmg_exp_vars.exp_lightmap_res = '128'
        
        scene.tmg_exp_vars.exp_pack_single_lightmap_uv = False
        scene.tmg_exp_vars.exp_unwrap_method = '0'
        scene.tmg_exp_vars.exp_UVpack_margin = 0.005
        
        return {'FINISHED'}
    

class OBJECT_PT_TMG_Export(bpy.types.Operator):
    """Export Mesh objects to folder directory path as individual model files"""
    bl_idname = "object.tmg_export"
    bl_label = "Export Models To Files"
    bl_options  = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        tmg_exp_vars = scene.tmg_exp_vars
        
        if scene.tmg_exp_vars.exp_directory and bpy.context.selected_objects:
            return main(scene.tmg_exp_vars.exp_directory)
        return{'FINISHED'}


class OBJECT_PT_TMG_Select_Directory(Operator, ImportHelper):
    """Select folder directory path for exported models"""
    bl_idname = "object.tmg_select_directory"
    bl_label = "Select Directory"
    bl_options  = {'REGISTER', 'UNDO'}
    
    directory : bpy.props.StringProperty(subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    # ImportHelper mixin class uses this
    filename_ext = ".fbx;.obj;.glb;.gltf"

    filter_glob: StringProperty(
        default="*.fbx;*.obj;*.glb;*.gltf",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        scene = context.scene
        tmg_exp_vars = scene.tmg_exp_vars
        scene.tmg_exp_vars.exp_directory = self.directory
        return{'FINISHED'}


class OBJECT_PT_TMG_Export_Panel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_tmg_export_panel'
    bl_category = 'TMG'
    bl_label = 'Export Tools'
    bl_context = "objectmode"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        scene = context.scene
        tmg_exp_vars = scene.tmg_exp_vars
        
        if scene.tmg_exp_vars.exp_directory == None:
            scene.tmg_exp_vars.exp_directory = '//'
            
        _check = os.path.exists(scene.tmg_exp_vars.exp_directory)
        selected_type = None
        
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
            
        row.operator('wm.object_tmg_reset_properties', text='', icon='FILE_REFRESH')
        row.operator('object.tmg_select_directory', text='', icon='FILE_FOLDER')
        
        if _check and bpy.context.selected_objects:
            row.operator('object.tmg_export', text='', icon='FOLDER_REDIRECT')
        else:
            row.label(text='', icon='FOLDER_REDIRECT')
            
        row.prop(tmg_exp_vars, 'exp_pref_presets', text='')
        row.prop(tmg_exp_vars, 'exp_export_format', text='')
        
        row = col.row(align=True)
            
        row.prop(tmg_exp_vars, 'exp_directory', text='')
            
        col = layout.column(align=True)
        row = col.row(align=True)
        
        if scene.tmg_exp_vars.exp_category:
            row.prop(tmg_exp_vars, 'exp_category', text='', icon='DOWNARROW_HLT')
        else:
            row.prop(tmg_exp_vars, 'exp_category', text='', icon='RIGHTARROW')
            
        row.label(text='Export Settings')
        
        if scene.tmg_exp_vars.exp_category:
            box = col.box()
            box_col = box.column(align=True)
            
            box_col.prop(tmg_exp_vars, 'exp_apply_unit_scale', text='Apply Unit')
            box_col.prop(tmg_exp_vars, 'exp_use_tspace', text='Use Space Transform')
            box_col.prop(tmg_exp_vars, 'exp_use_mesh_modifiers', text='Apply Modifiers')
            box_col.prop(tmg_exp_vars, 'exp_embed_textures', text='Embed Textures')
            box_col.prop(tmg_exp_vars, 'exp_leaf_bones', text='Leaf Bones')
            
            box = col.box()
            box_col = box.column(align=True)
            
            box_col.prop(tmg_exp_vars, 'exp_folder_by_type', text='Folder by Type')
            box_col.prop(tmg_exp_vars, 'use_collection_name', text='Folder by Collection')
            box_col.prop(tmg_exp_vars, 'exp_reset_location', text='Location to World Origin')
            box_col.prop(tmg_exp_vars, 'exp_apply_mesh', text='Visual Geometry to Mesh')
        
        col = layout.column(align=True)
        row = col.row(align=True)
        
        if scene.tmg_exp_vars.exp_uv_category:
            row.prop(tmg_exp_vars, 'exp_uv_category', text='', icon='DOWNARROW_HLT')
        else:
            row.prop(tmg_exp_vars, 'exp_uv_category', text='', icon='RIGHTARROW')
            
        row.label(text='UV Export Settings')
        
        if scene.tmg_exp_vars.exp_uv_category:
            box = col.box()
            box_col = box.column(align=True)
            
            box_col.prop(tmg_exp_vars, 'exp_rename_uvs', text='Rename UV Layers')
            
            if scene.tmg_exp_vars.exp_rename_uvs:
                row = box_col.row(align=True)
                col = row.split(factor=0.8, align=True)
                col.prop(tmg_exp_vars, 'exp_uvs_name', text='')
                col.prop(tmg_exp_vars, 'exp_uvs_start_int', text='')
                
            box_col.prop(tmg_exp_vars, 'exp_add_lightmap_uv', text='Add Lightmap UV Layer')
            box_col.prop(tmg_exp_vars, 'exp_unwrap_lightmap_uv', text='Unwrap Lightmap UV Layer')
            
            if scene.tmg_exp_vars.exp_unwrap_lightmap_uv:
                box_col.prop(tmg_exp_vars, 'exp_pack_single_lightmap_uv', text='Pack to Single UV')
                box_col.prop(tmg_exp_vars, 'exp_unwrap_method', text='')
                box_col.prop(tmg_exp_vars, 'exp_UVpack_margin', text='UV Margin')
#                row = box_col.row(align=True)
#                col = row.split(factor=0.5, align=True)
#                col.label(text='Lightmap Resolution:')
#                col.prop(tmg_exp_vars, 'exp_lightmap_res', text='')
        



