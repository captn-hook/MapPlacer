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
    
    win.file_path = bpy.props.StringProperty(name="Data Path", description="CSV file to rerieve locations from", default="/sampledata.csv")
    win.coordinate_mode = bpy.props.EnumProperty(
        name="Coordinate Mode",
        description="Choose which coordinate system to use",
        items=[
            ('XYZ', "XYZ", "Use X, Y, Z coordinates"),
            ('XY', "XY", "Use X, Y coordinates"),
            ('Spherical', "Spherical", "Use Latitude and Longitude coordinates"),
        ], 
        default='Spherical'
    )
    win.scale = bpy.props.FloatProperty(name="Scale", description="Scale factor for output", default=10.0, min=0.01, max=100.0)
    win.x = bpy.props.StringProperty(name="X coordinate column", description="Column in CSV for X coordinate", default="x")
    win.y = bpy.props.StringProperty(name="Y coordinate column", description="Column in CSV for Y coordinate", default="y")
    win.z = bpy.props.StringProperty(name="Z coordinate column", description="Column in CSV for Z coordinate", default="z")
    win.lat = bpy.props.StringProperty(name="Latitude column", description="Column in CSV for Latitude coordinate", default="Lat")
    win.lon = bpy.props.StringProperty(name="Longitude column", description="Column in CSV for Longitude coordinate", default="Lng")
    
    win.marker_mode = bpy.props.EnumProperty(
        name="Marker Mode",
        description="Choose which mode to use",
        items=[
            ('Object', "Object", "Place objects at coordinates"),
            ('Connections', "Connections", "Create connections between coordinates"),
            ('Both', "Both", "Place objects and create connections"),
        ],
        default='Both'
    )
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
    del win.coordinate_mode
    del win.scale
    del win.x
    del win.y
    del win.z
    del win.lat
    del win.lon
    del win.marker_mode
    del win.marker