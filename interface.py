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
        layout.prop(context.window_manager, "file_path", text="Data Path")
        
        row = layout.row()
        layout.prop(context.window_manager, "label_from", text="From Label")
        layout.prop(context.window_manager, "lat_from", text="Lat From")
        layout.prop(context.window_manager, "lng_from", text="Lng From")
        
        row = layout.row()
        layout.prop(context.window_manager, "label_to", text="To Label")
        layout.prop(context.window_manager, "lat_to", text="Lat To")
        layout.prop(context.window_manager, "lng_to", text="Lng To")
        
        row = layout.row()
        layout.prop(context.window_manager, "label_to2", text="To Label 2")
        layout.prop(context.window_manager, "lat_to2", text="Lat To 2")
        layout.prop(context.window_manager, "lng_to2", text="Lng To 2")
        
        row = layout.row()
        layout.prop(context.window_manager, "scale")
        
        row = layout.row()
        layout.prop(context.window_manager, "marker", text="Marker Object")
        
        row = layout.row()
        row.operator("run.main", text="Run Placer", icon='PLAY')