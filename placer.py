import bpy
from bpy.types import Operator
import pyproj, math
import os

# Spherical settings for WGS-84
R = 6378137
f_inv = 298.257224
f = 1.0 / f_inv
e2 = 1 - (1 - f) * (1 - f)

class run_placer(Operator):
    bl_idname = "run.main"
    bl_label = "Run the main function"
    bl_description = "Place markers/connections based on CSV data"
    
    @classmethod
    def poll(cls, context):
        # make sure that:
        # 1. The file path is set
        # 3. if the marker mode is set to 'Object' or 'Both', the marker object is set
        wm = context.window_manager
        if not wm.file_path:
            return False
        if wm.marker_mode in {'Object', 'Both'} and not wm.marker:
            return False
        return True
    
    def execute(self, context):
        
        wm = context.window_manager
        file_path = wm.file_path
        coordinate_mode = wm.coordinate_mode
        scale = wm.scale
        x_col = wm.x
        y_col = wm.y
        z_col = wm.z
        lat_col = wm.lat
        lon_col = wm.lon
        marker_mode = wm.marker_mode
        marker_object = wm.marker
        
        abspath = fixfile(file_path)
        print(f"Using file: {abspath}")
        try:
            with open(abspath, 'r') as file:
                lines = file.readlines()
                header = lines[0].strip('\n').split(',')
                data = [line.strip('\n').split(',') for line in lines[1:]]
                data = [dict(zip(header, row)) for row in data]
                
                for row in data:
                    if coordinate_mode == 'XYZ':
                        x = float(row[x_col]) * scale
                        y = float(row[y_col]) * scale
                        z = float(row[z_col]) * scale
                        name = f"{x}_{y}_{z}"
                    elif coordinate_mode == 'XY':
                        x = float(row[x_col]) * scale
                        y = float(row[y_col]) * scale
                        z = 0.0
                        name = f"{x}_{y}"
                    elif coordinate_mode == 'Spherical':
                        lat = float(row[lat_col])
                        lon = float(row[lon_col])
                        x, y, z = gps2ecef_custom(lat, lon, 0)
                        # Divide by earth radius to get normalized coordinates
                        x /= R
                        y /= R
                        z /= R
                        x *= scale
                        y *= scale
                        z *= scale
                        name = f"{lat}_{lon}"
                    else:
                        self.report({'ERROR'}, "Invalid coordinate mode selected")
                        return {'CANCELLED'}

                    if marker_mode in {'Object', 'Both'}:
                        if marker_object:
                            new_marker = marker_object.copy()
                            new_marker.data = marker_object.data.copy()
                            # change the name to the coordinates
                            new_marker.name = f"Marker_{name}"
                            new_marker.location = (x, y, z)
                            context.collection.objects.link(new_marker)
                    if marker_mode in {'Connections', 'Both'}:
                        # Create a curve to connect points
                        print(f"Creating connection from ({x}, {y}, {z})")
                        # if 'prev_x' in locals() and 'prev_y' in locals() and 'prev_z' in locals():
                        #     curve_data = bpy.data.curves.new(name="ConnectionCurve", type='CURVE')
                        #     curve_data.dimensions = '3D'
                        #     polyline = curve_data.splines.new('POLY')
                        #     polyline.points.add(1)
                        #     polyline.points[0].co = (prev_x, prev_y, prev_z, 1.0)
                        #     polyline.points[1].co = (x, y, z, 1.0)
                        #     curve_object = bpy.data.objects.new("Connection", curve_data)
                        #     context.collection.objects.link(curve_object)
                        
                    

            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to read file: {e}")
            return {'CANCELLED'}

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