bl_info = {
    "name" : 'Data Scale' ,
    "description" : "Quickly inspect the total size of datablocks",
    "author" : "hisanimations",
    "version" : (1, 0, 0),
    "blender" : (3, 0, 0),
    "location" : "View3d > Spawner",
    "support" : "COMMUNITY",
    "category" : "Assets",
    "doc_url": "https://github.com/hisprofile/OptiPloy"
}

import bpy
import os
from bpy.types import (Operator, AddonPreferences, Menu)
from bpy.utils import register_classes_factory
from bpy.props import (BoolProperty, StringProperty, EnumProperty)

TEMP_FILE = os.path.join(
    os.path.dirname(__file__),
    'temp.blend'
)

def inherits_from(a, b):
    if isinstance(b, tuple):
        try:
            for i in b:
                if issubclass(a, i): return True
            return False
        except TypeError:
            return False
    try:
        return issubclass(a, b)
    except TypeError:
        return False

def return_ids(context):
    if context.area.type in {'OUTLINER', 'VIEW_3D'}:
        return context.selected_ids
    elif context.area.type == 'PROPERTIES':
        space = context.space_data
        space_context = space.context
        match space_context:
            case 'OBJECT':
                return context.object
            case 'DATA':
                return context.object.data
            case 'MATERIAL':
                return context.material
            case 'SCENE':
                return context.scene
            case 'TEXTURE':
                return context.texture
            case 'WORLD':
                return context.world
            case 'COLLECTION':
                return context.collection
    elif context.area.type == 'TOPBAR':
            return context.selected_objects
    return None

def return_ids_set(context: bpy.types.Context, poll=False) -> set:
    gatherings = set()
    ids = return_ids(context)
    if '__iter__' in dir(ids):
        gatherings.update(set(ids))
    else:
        gatherings.add(ids)
    gatherings.discard(None)
    if not gatherings:
        return None
    return gatherings

def format_size(size_in_bytes):
    """
    Convert size in bytes to a human-readable format.
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0

class datascale_prefs(AddonPreferences):
    bl_idname = __package__
    compress: BoolProperty(default=False, name='Compress', description='Did you know you can save .blend files in a compressed state?')

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'compress', text='Compress Results')
        layout.label(text='Did you know you can save .blend projects in a compressed state?')
        layout.label(text='To make every .blend file save as compressed by default in the future, save your start-up file as compressed!')
        layout.separator()
        layout.label(text='Resulting sizes include .blend file headers and not raw data, which is usually negligible.')


class datascale_OT_weigh(Operator):
    bl_idname = 'datascale.weigh'
    bl_label = 'Weigh IDs'
    bl_description = 'Export the datablocks to calculate their total size on the hard drive.'

    @classmethod
    def poll(cls, context):
        return bool(return_ids(context))

    def execute(self, context):
        props = context.preferences.addons[__package__].preferences
        print(props)
        gatherings = return_ids_set(context)
        if not gatherings:
            return {'CANCELLED'}

        bpy.data.libraries.write(TEMP_FILE, gatherings, compress=props.compress)
        file_size = os.path.getsize(TEMP_FILE)
        file_size = format_size(file_size)
        os.remove(TEMP_FILE)
        report_msg = ' '.join([
            'The',
            str(len(gatherings)),
            'datablocks' if len(gatherings) > 1 else 'datablock', # nice to pick between plural and singular
            'weigh' if len(gatherings) > 1 else 'weighs',
            file_size
        ])
        self.report({'INFO'}, report_msg)
        return {'FINISHED'}

class datascale_OT_export(Operator):
    bl_idname = 'datascale.export'
    bl_label = 'Export Selected IDs as Library'
    bl_description = 'Export selected IDs to a new .blend file'

    directory: StringProperty(subtype='DIR_PATH')
    filepath: StringProperty(subtype='FILE_PATH')
    filename: StringProperty(subtype='FILE_NAME', default='.blend')
    check_existing: BoolProperty(
        name="Check Existing",
        description="Check and warn on overwriting existing files",
        default=True,
        options={'HIDDEN'},
    )
    filename_ext = '.blend'
    filter_blender: BoolProperty(default=True, options={'HIDDEN'})
    filter_folder: BoolProperty(default=True, options={'HIDDEN'})
    filter_blenlib: BoolProperty(default=True, options={'HIDDEN'})
    filter_glob:StringProperty(default='.blend', options={'HIDDEN'})

    path_remap: EnumProperty(
        items=(
            ('NONE', 'None', 'No path manipulation.'),
            ('RELATIVE', 'Relative', 'Remap paths that are already relative to the new location.'),
            ('RELATIVE_ALL', 'Relative All', 'Remap all paths to be relative to the new location (default)'),
            ('ABSOLUTE', 'Absolute', 'Make all paths absolute on writing.')
        ),
        name='Library Path Remap',
        description='The Remap operation for used .blend libraries in the export',
        default='RELATIVE_ALL'
    )
    fake_user: BoolProperty(default=True, name='Fake Users for IDs', description='Give Fake Users to IDs to ensure their persistence')
    compress: BoolProperty(default=False, name='Compress', description='Compress the export')
    create_default_scene:BoolProperty(default=True, name='Create Default Scene', description='Creates a default scene so the exported IDs show on first run. Otherwise, they will be hidden until you manually link them to a scene.')

    @classmethod
    def poll(cls, context):
        return bool(return_ids(context))

    def draw(self, context):
        layout = self.layout
        layout.label(text='Library Path Remap Operation')
        col = layout.column()
        col.prop(self, 'path_remap', expand=True)
        layout.separator()
        layout.prop(self, 'fake_user')
        layout.prop(self, 'compress')
        layout.prop(self, 'create_default_scene')

    def invoke(self, context, event):
        props = context.preferences.addons[__package__].preferences
        self.compress = props.compress
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def check(self, context):
        import os
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(os.path.splitext(filepath)[0], self.filename_ext)
        if self.filepath != filepath: # is it better to just always return True?
            self.filepath = filepath
            return True
        return False
    
    def execute(self, context):
        print(dir(context))
        print(context.area.type)
        default_scene = None
        #return {'FINISHED'}
        ids = return_ids_set(context)
        if not ids:
             return {'CANCELLED'}
        if self.create_default_scene:
            # if there already is a scene selected, we need to check if there are selected collections or objects that aren't linked to this scene.
            # gather selected scenes, collections, and objects
            existing_scenes = set(filter(lambda a: isinstance(a, bpy.types.Scene), ids))
            selected_objs = set(filter(lambda a: isinstance(a, bpy.types.Object), ids))
            selected_cols = set(filter(lambda a: isinstance(a, bpy.types.Collection), ids))

            # create sets to remove from the selected data
            selected_cols_objs = set()
            [selected_cols_objs.update(set(col.objects)) for col in selected_cols]
            scenes_collections = set()
            [scenes_collections.update(set(scn.collection.children_recursive)) for scn in existing_scenes]
            scenes_objects = set()
            [scenes_objects.update(set(scn.objects)) for scn in existing_scenes]

            # isolate all collections who are not a part of any selected scene.
            # isolate all objects who are not a part of any selected scene.
            # isolate all objects who are not a part of any selected collections.
            selected_cols.difference_update(set(scenes_collections))
            selected_objs.difference_update(scenes_objects)
            selected_objs.difference_update(selected_cols_objs)
            # get only the collections that do not have parents
            [selected_cols.discard(child) for col in list(selected_cols) for child in col.children_recursive]

            if selected_cols or selected_objs:
                default_scene = bpy.data.scenes.new('DATASCALE_scene')
                ids.add(default_scene)
            if selected_cols:
                [default_scene.collection.children.link(col) for col in selected_cols]
            if selected_objs:
                [default_scene.collection.objects.link(obj) for obj in selected_objs]

        bpy.data.libraries.write(self.filepath, ids, path_remap=self.path_remap, fake_user=self.fake_user, compress=self.compress)
        
        if default_scene:
             bpy.data.scenes.remove(default_scene)
        
        filesize = format_size(os.path.getsize(self.filepath))
        self.report({'INFO'}, f'Export successful with a size of {filesize}')
        return {'FINISHED'}

class DATASCALE_MT_Menu(Menu):
    bl_label = 'Data Scale Operators'
    bl_idname = 'DATASCALE_MT_Menu'

    def draw(self, context):
        props = context.preferences.addons[__package__].preferences
        layout = self.layout
        layout.prop(props, 'compress')
        layout.operator('datascale.weigh')
        layout.operator('datascale.export')

def menu_func(self, context):
    if not getattr(context, 'property', None): return # i cannot get it to show at the same level as "Mark as asset." 
    # according to this issue, https://projects.blender.org/blender/blender/issues/126006
    # the "Mark as asset" operator shows when bpy.context.id can be accessed. this does not seem to exist in Python :(
    self.layout.separator()
    self.layout.menu('DATASCALE_MT_Menu')

def export_menu(self, context):
    self.layout.operator('datascale.export')

def object_menu(self, context):
    self.layout.separator()
    self.layout.operator('datascale.weigh')

classes = [value for value in vars().values()
           if (inherits_from(value, (Operator, AddonPreferences, Menu)))
           and (not value in {Operator, AddonPreferences, Menu})]

classes = [
    datascale_prefs,
    datascale_OT_weigh,
    datascale_OT_export,
    DATASCALE_MT_Menu
]

reg_classes, unreg_classes = register_classes_factory(classes)

def register():
    reg_classes()
    bpy.types.OUTLINER_MT_context_menu.append(menu_func)
    bpy.types.OUTLINER_MT_object.append(menu_func)
    bpy.types.OUTLINER_MT_collection.append(menu_func)
    bpy.types.UI_MT_button_context_menu.append(menu_func)
    bpy.types.TOPBAR_MT_file_export.append(export_menu)
    bpy.types.VIEW3D_MT_object.append(object_menu)

def unregister():
    unreg_classes()
    bpy.types.OUTLINER_MT_context_menu.remove(menu_func)
    bpy.types.OUTLINER_MT_object.remove(menu_func)
    bpy.types.OUTLINER_MT_collection.remove(menu_func)
    bpy.types.UI_MT_button_context_menu.remove(menu_func)
    bpy.types.TOPBAR_MT_file_export.remove(export_menu)
    bpy.types.VIEW3D_MT_object.remove(object_menu)