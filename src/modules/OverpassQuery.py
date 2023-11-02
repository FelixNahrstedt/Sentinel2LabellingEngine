import geopandas as gpd
import requests
import json
from rtree import index as myindex
import matplotlib.pyplot as plt

def query_OSM(query:str,buffer_distance, filename):
    overpass_url = "http://overpass-api.de/api/interpreter"

    response = requests.get(overpass_url, 
                        params={'data': query})
    nodes = response.json()
    nodeList = nodes["elements"]
    searchCoordinates(nodeList, buffer_distance, filename)

    # Open the file in write mode and save the JSON data
    with open(f"../data/OSM-{filename}.json", 'w') as json_file:
        json.dump(nodes, json_file, indent=4)



def searchCoordinates(list:list, distance:int, filename:str):
    longitude_list = []
    latitude_list = []

    for el in list:
        longitude_list.append(el["lon"])
        latitude_list.append(el["lat"])

    # Create a GeoDataFrame from your list of latitude/longitude pairs
    gdf = gpd.GeoDataFrame(geometry=gpd.points_from_xy(longitude_list, latitude_list), crs="EPSG:4326")
    # Create a list of buffers for all points
    # Create a list of rectangular buffers (100 meters) around every point
    buffer_list = []
    for index, point in gdf.iterrows():
        buffer = point.geometry.buffer(distance / 111000, cap_style=3)  # Buffer of 100 meters (in degrees)
        buffer_list.append(buffer)
    
    # Create a spatial index for the GeoDataFrame
    spatial_index = myindex.Index()
    for idx, geometry in gdf['geometry'].items():
        spatial_index.insert(idx, geometry.bounds)
    
    # Create a list of lists containing points within each buffer
    FilledRectangles = []

    for buffer in buffer_list:
        points_within_buffer = {"lat":point.geometry.x, "lon": point.geometry.y,"bufferpoints":[]}
        for idx in spatial_index.intersection(buffer.bounds):
            point = gdf.loc[idx]
            if buffer.contains(point['geometry']):
                points_within_buffer["bufferpoints"].append((point['geometry'].x, point['geometry'].y))
        FilledRectangles.append(points_within_buffer)
    print(FilledRectangles)
    json_string = json.dumps(FilledRectangles, indent=4)
    with open(f"../data/BufferedObjects-{filename}.json", "w") as json_file:
        json_file.write(json_string)

    # Visualize the buffer_list
    # Create a GeoDataFrame for the buffer_list
    buffers_gdf = gpd.GeoDataFrame({'geometry': buffer_list}, crs=gdf.crs)

    # Plot the GeoDataFrame points and buffers
    fig, ax = plt.subplots(figsize=(8, 8))

    # Plot the GeoDataFrame points
    gdf.plot(ax=ax, color='blue', markersize=10, label='Points')

    # Plot the buffers
    buffers_gdf.boundary.plot(ax=ax, color='red', linewidth=1, linestyle='--', label='Buffers')

    # Set labels and title
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Points and Rectangular Buffers')

    # Add a legend
    plt.legend()
    plt.savefig(f'Bounding_boxes{filename}.png', bbox_inches='tight')  # Change the file extension as needed

    


query = '''[out:json];
    area["ISO3166-1"="NL"];
    (node["power"="generator"]["generator:source"="wind"]["manufacturer"="Vestas"](area);
    );
    out center;'''
query_OSM(query,1000,"Test")
