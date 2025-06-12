lat_from = 'PI_Lat'
lng_from = 'PI_Lng'
lat_to = 'CoPI_Lat'
lng_to = 'CoPI_Lng'

class Location:
    def __init__(self, lat, lng, connections=None):
        self.lat = lat
        self.lng = lng
        self.connections = connections if connections is not None else []
        
    def __repr__(self):
        string = f"Location: ({self.lat}, {self.lng})"
        if self.connections:
            string += f", connections:\n"
        for conn in self.connections:
            string += f"    {conn}\n"
        
        return string

def ingest_data(file_path):

    with open(file_path, 'r') as file:
        lines = file.readlines()
        header = lines[0].strip('\n').split(',')
        data = [line.strip('\n').split(',') for line in lines[1:]]
        data = [dict(zip(header, row)) for row in data]
        
    return_data = []
    for row in data:
        row_data = {}
        row_data = Location(
            lat=float(row.get(lat_from, None)),
            lng=float(row.get(lng_from, None)),
            connections=[
                Location(
                    lat=float(row.get(lat_to, None)),
                    lng=float(row.get(lng_to, None))
                )
            ]
        )
        return_data.append(row_data)
    return return_data

if __name__  == "__main__":
    #file_path = "PIs-coPIs data.csv"  
    file_path = "PIs-coPIs data.csv"
    data = ingest_data(file_path)
    
    print("Ingested Data:")
    for item in data:
        print(item)
        