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
        layout.prop(context.window_manager, "file_path1", text="Data Path")
        layout.prop(context.window_manager, "file_path2", text="Optional Data")    
        layout.prop(context.window_manager, "label", text="Label Column")    
        row = layout.row()
        layout.prop(context.window_manager, "lat_from", text="Lat From")
        layout.prop(context.window_manager, "lng_from", text="Lng From")
        row = layout.row()
        layout.prop(context.window_manager, "lat_to", text="Lat To")
        layout.prop(context.window_manager, "lng_to", text="Lng To")
        row = layout.row()
        layout.prop(context.window_manager, "scale")
        row = layout.row()
        layout.prop(context.window_manager, "marker", text="Marker Object")
        row = layout.row()
        row.operator("run.main", text="Run Placer", icon='PLAY')