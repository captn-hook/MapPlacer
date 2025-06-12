
class Location:
    def __init__(self, lat, lng, connections=None):
        self.lat = lat
        self.lng = lng
        self.connections = connections if connections is not None else []
        
    def __repr__(self, level=0):
        indent = "    " * level
        string = f"{indent}Location: ({self.lat}, {self.lng})"
        if self.connections:
            string += f", connections:\n"
        for conn in self.connections:
            string += f"{indent}    " + conn.__repr__(level + 1) + "\n"
        if self.connections:
            string = string.rstrip('\n')
        
        return string

def ingest_data(file_path1, file_path2=None, 
                lat_from='Lat', lng_from='Lng', 
                lat_to='DB_Lat', lng_to='DB_Lng', label=None):

    with open(file_path1, 'r') as file:
        lines = file.readlines()
        header = lines[0].strip('\n').split(',')
        data1 = [line.strip('\n').split(',') for line in lines[1:]]
        data1 = [dict(zip(header, row)) for row in data1]
        
    if file_path2 is not None:
        with open(file_path2, 'r') as file:
            lines = file.readlines()
            header = lines[0].strip('\n').split(',')
            data2 = [line.strip('\n').split(',') for line in lines[1:]]
            data2 = [dict(zip(header, row)) for row in data2] if file_path2 else []        
            
        sub_locations = {}
        for row in data2:
            lat = float(row.get(lat_to, None))
            lng = float(row.get(lng_to, None))
            label_value = row.get(label, None)
            
            if sub_locations.get(label_value) is None:
                sub_locations[label_value] = [Location(lat=lat, lng=lng)]
            else:
                sub_locations[label_value].append(Location(lat=lat, lng=lng))
                
    return_data = []
    
    for row in data1:
        lat_from_value = row.get(lat_from, None)
        lng_from_value = row.get(lng_from, None)
        lat_to_value = row.get(lat_to, None)
        lng_to_value = row.get(lng_to, None)
        
        if label is not None:
            label_value = row.get(label, None)
        
        connections = []
        
        if file_path2 is not None and label_value and sub_locations.get(label_value):
            connections = sub_locations[label_value]        
        
        row_data = Location(
            lat=float(lat_from_value),
            lng=float(lng_from_value),
            connections=[
                Location(
                    lat=float(lat_to_value),
                    lng=float(lng_to_value),
                    connections=connections
                )
            ]
        )
        
        return_data.append(row_data)
        
    return return_data

if __name__  == "__main__":
    test_case = 2
    
    if test_case == 1:
        lat_from = 'PI_Lat'
        lng_from = 'PI_Lng'
        lat_to = 'CoPI_Lat'
        lng_to = 'CoPI_Lng'

        file_path = "PIs-coPIs data.csv"
        data = ingest_data(file_path, lat_from=lat_from, lng_from=lng_from, lat_to=lat_to, lng_to=lng_to)
        
    elif test_case == 2:
        lat_from = 'Lat'
        lng_from = 'Lng'
        lat_to = 'DB_Lat'
        lng_to = 'DB_Lng'
        label = 'DB_Name'

        file_path1 = "PIs-DBs direct data.csv"
        file_path2 = "DBs-SRCs data.csv"
        data = ingest_data(file_path1, file_path2, 
                           lat_from=lat_from, lng_from=lng_from, 
                           lat_to=lat_to, lng_to=lng_to, label=label)
    
    print("Ingested Data:")
    for item in data:
        print(item)
        