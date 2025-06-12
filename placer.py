import bpy
from bpy.types import Operator
import pyproj, math
import os

from . dataIngest import ingest_data

# Spherical settings for WGS-84
R = 6378137
f_inv = 298.257224
f = 1.0 / f_inv
e2 = 1 - (1 - f) * (1 - f)

connection_cache = {}
marker_cache = {}
color_cache = []

class run_placer(Operator):
    bl_idname = "run.main"
    bl_label = "Run the main function"
    bl_description = "Place markers/connections based on CSV data"
    
    @classmethod
    def poll(cls, context):
        # make sure that:
        # 1. The file path is set
        # 3. if the marker mode is set to 'Object' or 'Both', the marker object is set
        win = context.window_manager
        if not win.file_path1:
            return False
        return True
    
    def execute(self, context):
        
        win = context.window_manager
        file_path1 = win.file_path1
        file_path2 = win.file_path2
        scale = win.scale
        lat_from = win.lat_from
        lng_from = win.lng_from
        lat_to = win.lat_to
        lng_to = win.lng_to
        label = win.label
        marker_object = win.marker
        
        abspath = fixfile(file_path1)
        try:
            if file_path2:
                abspath2 = fixfile(file_path2)
                data = ingest_data(abspath, abspath2, lat_from=lat_from, lng_from=lng_from, lat_to=lat_to, lng_to=lng_to, label=label)
            else:
                data = ingest_data(abspath, lat_from=lat_from, lng_from=lng_from, lat_to=lat_to, lng_to=lng_to)

            global connection_cache, marker_cache, color_cache
            
            connection_cache = {}
            marker_cache = {}         
            color_cache = preload_colors(4)  # Preload colors for connections   
            
            place_markers(data, context, scale, marker_object)
            # Clear the cache
            connection_cache = {}
            color_cache = []
            marker_cache = {}

            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error processing {e}")
            return {'CANCELLED'}
        
def place_markers(data, context, scale, marker_object, level=0):
    objs_to = []
    for location in data:
        if location.connections:
            place_markers(location.connections, context, scale, marker_object, level + 1)
            
        lat = location.lat
        lon = location.lng
        obj_from = place_marker(context, lat, lon, scale, marker_object)
        objs_to.append(obj_from)
            
        if len(objs_to) > 0:
            # Create connections 
            for obj_to in objs_to:
                create_connection(context, obj_from, obj_to, scale, level=level)

def place_marker(context, lat, lon, scale, marker_object):
    name = f"Marker_{lat}_{lon}"
    # Check if the marker already exists in the cache
    if name in marker_cache:
        return marker_cache[name]
                
    x, y, z = gps2ecef_custom(lat, lon, 0)
    # Divide by earth radius to get normalized coordinates
    x /= R
    y /= R
    z /= R
    x *= scale
    y *= scale
    z *= scale

    new_marker = marker_object.copy()
    new_marker.data = marker_object.data.copy()
    # change the name to the coordinates
    new_marker.name = name
    new_marker.location = (x, y, z)
    context.collection.objects.link(new_marker)
    
    marker_cache[name] = new_marker
    
    return new_marker    

def create_connection(context, obj_from, obj_to, scale, level=0):
    if obj_from == obj_to:
        return None
    # Check if the connection already exists
    name1 = obj_from.name + "_" + obj_to.name
    name2 = obj_to.name + "_" + obj_from.name
    if name1 in connection_cache:
        return connection_cache[name1]
    elif name2 in connection_cache:
        return connection_cache[name2]
    
    # Create a new curve with 3 handles
    curve_data = bpy.data.curves.new(name=name1, type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 4
    curve_data.render_resolution_u = 12
    
    # Set width and color of the curve based on level
    if level >= len(color_cache):
        create_material(level)
        
    widths = [0.5, 0.2, 0.05, 0.01]
    if level < len(widths):
        curve_data.bevel_depth = widths[level]
        material = color_cache[level]
    else:
        curve_data.bevel_depth = widths[-1]
        material = color_cache[-1]
    
    # Calculate the midpoint height based on the distance between the two objects
    distance = math.sqrt(
        (obj_from.location.x - obj_to.location.x) ** 2 +
        (obj_from.location.y - obj_to.location.y) ** 2 +
        (obj_from.location.z - obj_to.location.z) ** 2
    )
    
    midpoint = (
        (obj_from.location.x + obj_to.location.x) / 2,
        (obj_from.location.y + obj_to.location.y) / 2,
        (obj_from.location.z + obj_to.location.z) / 2
    )
    
    midpoint = normalize_tuple(midpoint, scale + (distance / 5))
    
    # Create a new spline
    spline = curve_data.splines.new(type='BEZIER')
    spline.bezier_points.add(2)  # Three points total (start, midpoint, end)
    
    spline.bezier_points[0].co = obj_from.location
    handle_left1 = normalize_tuple(obj_from.location, scale - (distance / 4))
    handle_right1 = normalize_tuple(obj_from.location, scale + (distance / 4))
    spline.bezier_points[0].handle_left = handle_left1
    spline.bezier_points[0].handle_right = handle_right1
    
    spline.bezier_points[1].co = midpoint
    
    spline.bezier_points[2].co = obj_to.location
    handle_left2 = normalize_tuple(obj_to.location, scale + (distance / 4))
    handle_right2 = normalize_tuple(obj_to.location, scale - (distance / 4))
    spline.bezier_points[2].handle_left = handle_left2
    spline.bezier_points[2].handle_right = handle_right2
    
    spline.bezier_points[1].handle_left = handle_right1
    spline.bezier_points[1].handle_right = handle_left2
    
    # set the midpoint to automatic
    spline.bezier_points[1].handle_left_type = 'AUTO'
    spline.bezier_points[1].handle_right_type = 'AUTO'  
    
    
    # Create a new object with the curve data
    curve_object = bpy.data.objects.new(name=f"Connection_{obj_from.name}_{obj_to.name}", object_data=curve_data)
    # Set the material for the curve
    curve_object.data.materials.append(material)
    # Link the curve object to the current collection
    context.collection.objects.link(curve_object)
    
    connection_cache[name1] = curve_object    
    return curve_object  

def preload_colors(num_colors):
    # Preload colors for connections
    for i in range(num_colors):
        create_material(i)
    return color_cache

def create_material(level):
    colors = ['#FF0000', '#0000FF', '#00FF00', '#FFFF00']
    if level >= len(colors):
        return None
    color_hex = colors[level]
    color_rgb = tuple(int(color_hex[i:i+2], 16) / 255.0 for i in (1, 3, 5))
    # Create a new material
    material = bpy.data.materials.new(name=f"ConnectionColor_{level}")
    material.use_nodes = True
    # Get the material's node tree
    nodes = material.node_tree.nodes
    # Clear existing nodes
    nodes.clear()
    # Create a new rgb node
    rgb_node = nodes.new(type='ShaderNodeRGB')
    rgb_node.outputs[0].default_value = (*color_rgb, 1 - level * 0.2)  # Set alpha based on level
    # Set the alpha mode of the material
    # material.blend_method = 'BLEND'
    # Connect the rgb node to the output
    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (200, 0)
    material.node_tree.links.new(rgb_node.outputs[0], output_node.inputs['Surface'])
    # Add the material to the color cache
    color_cache.append(material)

def normalize_tuple(tuple, scale = 1.0):
    length = math.sqrt(tuple[0]**2 + tuple[1]**2 + tuple[2]**2)
    tuple = (
        tuple[0] / length * scale,
        tuple[1] / length * scale,
        tuple[2] / length * scale
    )
    return tuple
    
def fixfile(file):
    if file[0] == "/":
        return bpy.path.abspath(r"//" + file[1:])
    else:
        return bpy.path.abspath(file)
    
# Sample (Lat, Lng, Alt)
ex_LLA = [
    (0,  45,  1000),
    (45, 90,  2000),
    (48.8567,  2.3508,  80),
    (61.4140105652, 23.7281341313, 149.821),
    (51.760597, -1.261247, 114.284188),
]

def gps2ecef_pyproj(lat, lon, alt):
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    
    x, y, z = pyproj.transform(lla, ecef, lon, lat, alt, radians=False)
    return x, y, z

def gps2ecef_custom(latitude, longitude, altitude):
    # (lat, lon) in WSG-84 degrees
    # altitude in meters
    cosLat = math.cos(latitude * math.pi / 180)
    sinLat = math.sin(latitude * math.pi / 180)

    cosLong = math.cos(longitude * math.pi / 180)
    sinLong = math.sin(longitude * math.pi / 180)

    c = 1 / math.sqrt(cosLat * cosLat + (1 - f) * (1 - f) * sinLat * sinLat)
    s = (1 - f) * (1 - f) * c

    x = (R*c + altitude) * cosLat * cosLong
    y = (R*c + altitude) * cosLat * sinLong
    z = (R*s + altitude) * sinLat

    return x, y, z

def ecef_to_enu(x, y, z, latRef, longRef, altRef):
    cosLatRef = math.cos(latRef * math.pi / 180)
    sinLatRef = math.sin(latRef * math.pi / 180)

    cosLongRef = math.cos(longRef * math.pi / 180)
    sinLongRef = math.sin(longRef * math.pi / 180)

    cRef = 1 / math.sqrt(cosLatRef * cosLatRef + (1 - f) * (1 - f) * sinLatRef * sinLatRef)

    x0 = (R*cRef + altRef) * cosLatRef * cosLongRef
    y0 = (R*cRef + altRef) * cosLatRef * sinLongRef
    z0 = (R*cRef*(1-e2) + altRef) * sinLatRef

    xEast = (-(x-x0) * sinLongRef) + ((y-y0)*cosLongRef)

    yNorth = (-cosLongRef*sinLatRef*(x-x0)) - (sinLatRef*sinLongRef*(y-y0)) + (cosLatRef*(z-z0))

    zUp = (cosLatRef*cosLongRef*(x-x0)) + (cosLatRef*sinLongRef*(y-y0)) + (sinLatRef*(z-z0))

    return xEast, yNorth, zUp

# Geodetic Coordinates (Latitude, Longitude, Altitude)
def geodetic_to_enu(lat, lon, h, lat_ref, lon_ref, h_ref):
    x, y, z = gps2ecef_custom(lat, lon, h)
    return ecef_to_enu(x, y, z, lat_ref, lon_ref, h_ref)

def geodetic_to_enu(qu_LLA, rf_LLA):
    ECEF    = gps2ecef_custom(qu_LLA)
    ENU     = ecef_to_enu(ECEF, rf_LLA)
    return ENU 

def run_test():
    for pt in ex_LLA:
        xPy,yPy,zPy = gps2ecef_pyproj(pt[0], pt[1], pt[2])   
        xF,yF,zF        = gps2ecef_custom(pt[0], pt[1], pt[2])
        xE, yN, zU  = ecef_to_enu(xF,yF,zF, pt[0], pt[1], pt[2])
    
        print('\n>>> LLA: {}'.format(pt))
        print(">> pyproj (XYZ)\t = ", xPy, yPy, zPy)
        print(">> ECEF (XYZ)\t = ", xF, yF, zF)
        print('>> ENU (XYZ) \t = ', xE, yN, zU)
        print('-'*100)

if __name__ == "__main__":
    run_test()