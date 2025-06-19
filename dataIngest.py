class Connection:
    def __init__(self, label, lat_from, lng_from, lat_to, lng_to):
        self.label = label
        self.lat_from = lat_from
        self.lng_from = lng_from
        self.lat_to = lat_to
        self.lng_to = lng_to
    
def get_single_label(row, label_column):
    # if label_column is a list, use all of them concatenated
    if isinstance(label_column, list):
        return '-'.join([row.get(col, '/ No Label / ') for col in label_column if col in row]) or '/ No Label / '        
        
    else:
        # get the label from the data
        return row.get(label_column, '/ No Label / ')
    

def get_label(row, from_label, to_label, row_index):
    return get_single_label(row, from_label) + ' -> ' + get_single_label(row, to_label)
    
    
def ingest_data(file_path1,
                label_from='Location', lat_from='Lat', lng_from='Lng',
                label_to=['DB_Location', 'DB_Name'], lat_to='DB_Lat', lng_to='DB_Lng',
                label_to2='', lat_to2='', lng_to2=''):
    
    print(f"Ingesting data with args: {file_path1}, {label_from}, {lat_from}, {lng_from}, {label_to}, {lat_to}, {lng_to}, {label_to2}, {lat_to2}, {lng_to2}")

    with open(file_path1, 'r') as file:
        lines = file.readlines()
        header = lines[0].strip('\n').split(',')
        data1 = [line.strip('\n').split(',') for line in lines[1:]]
        data1 = [dict(zip(header, row)) for row in data1]
     
    return_data1 = set()
    return_data2 = set()
    
    for row in data1:
        lat_from_value = row.get(lat_from, '')
        lng_from_value = row.get(lng_from, '')
        lat_to_value = row.get(lat_to, '')
        lng_to_value = row.get(lng_to, '')
        
        # if any is '', throw an error
        if lat_from_value == '' or lng_from_value == '' or lat_to_value == '' or lng_to_value == '':
            raise ValueError(f"Missing data in row number {data1.index(row) + 1}: {row}.")
        
        # if we have a third connection, get it
        if label_to2 != '' and lat_to2 != '' and lng_to2 != '':
        
            lat_to_value2 = row.get(lat_to2, '')
            lng_to_value2 = row.get(lng_to2, '')
            
            # if the connection is not to itself, create it
            if label_to != label_to2 and (lat_to_value != lat_to_value2 or lng_to_value != lng_to_value2) and get_single_label(row, label_to2) != '-':
                # create a connection from to to to2        lol
                
                label2 = get_label(row, label_to, label_to2, data1.index(row))
            
                if lat_to_value2 == '' or lng_to_value2 == '':
                    raise ValueError(f"Missing data in row number {data1.index(row) + 1}: {row} / {get_single_label(row, label_to2)}.")
                
                # check if label 2 already exists in the set
                if label2 not in return_data2:
                    if type(lat_to_value2) is str:
                        lat_from_value = float(lat_to_value.strip())
                    if type(lng_to_value) is str:
                        lng_from_value = float(lng_to_value.strip())
                    if type(lat_to_value2) is str:
                        lat_to_value2 = float(lat_to_value2.strip())
                    if type(lng_to_value2) is str:
                        lng_to_value2 = float(lng_to_value2.strip())
                    return_data2.add(Connection(label2, lat_from_value, lng_from_value, lat_to_value2, lng_to_value2))
                else:
                    print(f"Duplicate sub-connection found: {label2}. Skipping.")
            
        if label_from  != label_to and (lat_from_value != lat_to_value or lng_from_value != lng_to_value):
            label = get_label(row, label_from, label_to, data1.index(row))
            if label not in return_data1:
                if type(lat_from_value) is str:
                    lat_from_value = float(lat_from_value.strip())
                if type(lng_from_value) is str:
                    lng_from_value = float(lng_from_value.strip())
                if type(lat_to_value) is str:
                    lat_to_value = float(lat_to_value.strip())
                if type(lng_to_value) is str:
                    lng_to_value = float(lng_to_value.strip())
                return_data1.add(Connection(label, lat_from_value, lng_from_value, lat_to_value, lng_to_value))
            else:
                print(f"Duplicate connection found: {label}. Skipping.")

    print(f"Processed {len(return_data1)} connections from {file_path1}")
    print(f"{len(return_data2)} additional sub-connections found." if return_data2 else "No additional sub-connections found.")
        
    return return_data1, return_data2

if __name__  == "__main__":
    test_case = 2
    
    if test_case == 1:
        label_from = 'PI_Location'
        lat_from = 'PI_Lat'
        lng_from = 'PI_Lng'
        
        label_to = 'CoPI_Location'
        lat_to = 'CoPI_Lat'
        lng_to = 'CoPI_Lng'

        file_path = "PIs-coPIs.csv"
        data1, data2 = ingest_data(file_path, label_from=label_from, lat_from=lat_from, lng_from=lng_from, label_to=label_to, lat_to=lat_to, lng_to=lng_to)
        
    elif test_case == 2:
        
        label_from = 'Location'
        lat_from = 'Lat'
        lng_from = 'Lng'
        
        labels_to = ['DB_Location', 'DB_Name']
        lat_to = 'DB_Lat'
        lng_to = 'DB_Lng'
        
        labels_to2 = ['DB_Location2', 'DB_Name2']
        lat_to2 = 'DB_Lat2'
        lng_to2 = 'DB_Lng2'     

        file_path = "PIs-DBs.csv"
        data1, data2 = ingest_data(file_path,
                            label_from=label_from, lat_from=lat_from, lng_from=lng_from,
                            label_to=labels_to, lat_to=lat_to, lng_to=lng_to,
                            
                            label_to2=labels_to2, lat_to2=lat_to2, lng_to2=lng_to2)
    print("Ingested Data:", len(data1))
    # for item in data1:
    #     print(item.label, item.lat_from, item.lng_from, item.lat_to, item.lng_to)
        
    print("Sub-Connections:", len(data2))
    # for item in data2:
    #     print(item.label, item.lat_from, item.lng_from, item.lat_to, item.lng_to)