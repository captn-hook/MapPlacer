import bpy
from bpy.types import Panel

class INTERFACE_PT_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Map Placer"
    bl_category = "MP"
    bl_idname = "INTERFACE_PT_Panel"

    def draw(self, context):    

        layout = self.layout
        layout.label(text= "Source Data:")
        row = layout.row()
        layout.prop(context.window_manager, "file_path")
        
        row = layout.row()
        layout.prop(context.window_manager, "coordinate_mode")
        row = layout.row()
        layout.prop(context.window_manager, "scale")
        row = layout.row()
        layout.prop(context.window_manager, "x")
        layout.prop(context.window_manager, "y")
        layout.prop(context.window_manager, "z")
        row = layout.row()
        layout.prop(context.window_manager, "lat")
        layout.prop(context.window_manager, "lon")
        row = layout.row()
        layout.prop(context.window_manager, "marker_mode")
        row = layout.row()
        layout.prop(context.window_manager, "marker", text="Marker Object")
        row = layout.row()
        row.operator("run.main", text="Run Placer", icon='PLAY')