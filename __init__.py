import bpy
#from bpy.app.handlers import persistent

bl_info = {
    "name" : "MapPlacer",
    "author" : "Tristan Hook",
    "description" : "Places on maps",
    "blender" : (4, 2, 0),
    "version" : (1, 0, 0),
    "location" : "VIEW3D",
    "warning" : "",
    "category" : "Generic"
}

from . interface import INTERFACE_PT_Panel
from . placer import run_placer

def register():
    
    bpy.utils.register_class(INTERFACE_PT_Panel)
    bpy.utils.register_class(run_placer)
        
    win = bpy.types.WindowManager
    
    win.file_path = bpy.props.StringProperty(name="Data Path", description="CSV file to rerieve locations from", default="/PIs-DBs.csv")

    win.scale = bpy.props.FloatProperty(name="Scale", description="Scale factor for output", default=10.0, min=0.01, max=100.0)
    
    win.label_from = bpy.props.StringProperty(name="From Label column", description="Column in CSV for first file labels", default="Location")
    win.lat_from = bpy.props.StringProperty(name="Latitude from column", description="Column in CSV for Latitude coordinate", default="Lat")
    win.lng_from = bpy.props.StringProperty(name="Longitude fromcolumn", description="Column in CSV for Longitude coordinate", default="Lng")
   
    win.label_to = bpy.props.StringProperty(name="To Label column", description="Column in CSV for second file labels", default="DB_Location, DB_Name")
    win.lat_to = bpy.props.StringProperty(name="Latitude to column", description="Column in CSV for Latitude coordinate of destination", default="DB_Lat")
    win.lng_to = bpy.props.StringProperty(name="Longitude to column", description="Column in CSV for Longitude coordinate of destination", default="DB_Lng")
    
    win.label_to2 = bpy.props.StringProperty(name="To Label 2 column", description="Column in CSV for second file labels 2", default="DB_Location2, DB_Name2")
    win.lat_to2 = bpy.props.StringProperty(name="Latitude to 2 column", description="Column in CSV for Latitude coordinate of destination 2", default="DB_Lat2")
    win.lng_to2 = bpy.props.StringProperty(name="Longitude to 2 column", description="Column in CSV for Longitude coordinate of destination 2", default="DB_Lng2")
    
    win.marker = bpy.props.PointerProperty(
        name="Marker Object",
        description="Object to use as marker",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'MESH'  # Ensure it's a mesh object
    )
    
def unregister():
    bpy.utils.unregister_class(INTERFACE_PT_Panel)
    bpy.utils.unregister_class(run_placer)
        
    win = bpy.types.WindowManager
    
    del win.file_path
    del win.scale
    
    del win.label_from
    del win.lat_from
    del win.lng_from
    
    del win.label_to
    del win.lat_to
    del win.lng_to
    
    del win.label_to2
    del win.lat_to2
    del win.lng_to2
    
    del win.marker