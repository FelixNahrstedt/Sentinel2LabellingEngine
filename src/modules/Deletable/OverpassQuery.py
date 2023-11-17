import geopandas as gpd
import requests
import json
from rtree import index as myindex
import matplotlib.pyplot as plt
import math
import utm
import csv
from shapely.geometry import Point
from shapely.geometry import Polygon

def query_OSM(query, buffer_distance, filename):
    """
    Perform an Overpass API query, process the results, and save JSON data and a visualization.

    Args:
        query (str): Overpass query string.
        buffer_distance (int): The distance in meters for creating rectangular buffers.
        filename (str): The filename for saving JSON and the plot.

    Returns:
        None
    """

    # Define the Overpass API endpoint
    overpass_url = "http://overpass-api.de/api/interpreter"
    csv_file_path = f"../data/Latest_Coordinates_{filename}.csv"

    # Perform the Overpass API query
    response = requests.get(overpass_url, params={'data': query})
    nodes = response.json()
    nodeList = nodes["elements"]
    csv_data = []

    for index, element in enumerate(nodeList):
        lat = element.get("lat", "")
        lon = element.get("lon", "")
        csv_data.append([index, lat, lon])

    with open(csv_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["index", "latitude", "longitude"])  # Write the header row
        csv_writer.writerows(csv_data)  # Write the data rows

    # Call the search_coordinates function to process the nodes
    search_coordinates(nodeList, buffer_distance, filename)

    # Save the OSM data as JSON
    with open(f"../data/OSM-{filename}.json", 'w') as json_file:
        json.dump(nodes, json_file, indent=4)
    
    return len(nodeList)

def search_coordinates(points, distance, filename):
    """
    Search for points within rectangular buffers, save results to JSON, and create a visualization.

    Args:
        points (list): List of dictionaries with 'lon' and 'lat' coordinates.
        distance (int): The distance in meters for creating rectangular buffers.
        filename (str): The filename for saving JSON and the plot.

    Returns:
        None
    """

    # Extract latitude and longitude from the list of points
    longitude_list = [point["lon"] for point in points]

    latitude_list = [point["lat"] for point in points]

    id_list = [point["id"] for point in points]

    # Create a GeoDataFrame from the list of latitude/longitude pairs
    gdf = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy(longitude_list, latitude_list),
        crs="EPSG:4326"
    )

    #regions, rectangles = get_region_and_rectangle(longitude_list,latitude_list,distance/1000)
    # Create a list of rectangular buffers around every point
    buffer_list = []
    for index, point in gdf.iterrows():
        print(f"distance is {distance} meters")
        buffer_distance = meters_to_degrees(point.geometry.x, distance)
        easting, northing, zone_number, zone_letter = utm.from_latlon(point.geometry.x, point.geometry.y)
        lon_lat_list = [utm.to_latlon(easting-(distance/2), northing-(distance/2),zone_number,zone_letter),
                        utm.to_latlon(easting-(distance/2), northing+(distance/2),zone_number,zone_letter),
                        utm.to_latlon(easting+(distance/2), northing+(distance/2),zone_number,zone_letter),
                        utm.to_latlon(easting+(distance/2), northing-(distance/2),zone_number,zone_letter),
                        ]
        polygon = Polygon(lon_lat_list)
        #print(buffer_distance_lat,buffer_distance_lon)
        #print(buffer_distance, compare_buffer)
        buffer = point.geometry.buffer(buffer_distance, cap_style=3)  # Buffer of given distance (in degrees)
        print(buffer,polygon)
        buffer_list.append(polygon)

    # Create a spatial index for the GeoDataFrame
    spatial_index = myindex.Index()
    for idx, geometry in gdf['geometry'].items():
        spatial_index.insert(idx, geometry.bounds)

    # Create a list of lists containing points within each buffer
    filled_rectangles = []
    print("here")
    for index, buffer in enumerate(buffer_list):
        points_within_buffer = {"lat": point.geometry.x, "lon": point.geometry.y,"index":index, "bufferpoints": []}
        for idx in spatial_index.intersection(buffer.bounds):
            point = gdf.loc[idx]
            if buffer.contains(point['geometry']):
                points_within_buffer["bufferpoints"].append((point['geometry'].x, point['geometry'].y))
        filled_rectangles.append(points_within_buffer)

    # Save the results as JSON
    json_string = json.dumps(filled_rectangles, indent=4)
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

    # Save the plot
    plt.savefig(f'static/images/Bounding_boxes_{filename}.png', bbox_inches='tight')  # Change the file extension as needed
    plt.show()

def meters_to_degrees(lat, meters):
    """
    Convert a distance in meters to the equivalent distance in degrees.

    Args:
        lat (float): Latitude in degrees.
        lon (float): Longitude in degrees.
        meters (float): Distance in meters.

    Returns:
        float: Equivalent distance in degrees.
    """
    # Earth's radius in meters (mean radius, assuming a sphere)
    earth_radius = 63710088  # Approximately 63710088 km

    # Latitude in radians
    lat_rad = math.radians(lat)

    # Calculate the circumference at the given latitude
    circumference = 2 * math.pi * earth_radius * math.cos(lat_rad)

    # Calculate the conversion factor from meters to degrees
    degrees_per_meter = 360.0 / circumference

    # Convert meters to degrees
    degrees = meters * degrees_per_meter

    return degrees


query = '''[out:json];
    area["ISO3166-1"="NL"];
    (node["power"="generator"]["generator:source"="wind"]["manufacturer"="Vestas"](area);
    );
    out center;'''
#query_OSM(query,10000,"Test")
