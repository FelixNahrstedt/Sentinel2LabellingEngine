import geopandas as gpd
import requests
import json
from rtree import index as myindex
import matplotlib.pyplot as plt
import math
import utm
import csv
from shapely.geometry import Point, Polygon
import time
from helper_functions import get_coordinates_square

class OSM_Downloader:
    def __init__(self):
        pass

    def query_OSM(self, query, Image_size, element_size, filename, label,csv_file_path,make_bounding_box_image = True, bounding_box_image_path= "static/images/",get_way_centers=False):
        """
        Perform an Overpass API query, process the results, and save JSON data and a visualization.

        Args:
            query (str): Overpass query string.
            Image_size (int): The distance in meters for creating rectangular buffers.
            element_size (int): The size (square) of the object for labelling
            filename (str): The filename for saving JSON and the plot.

        Returns:
            int: Number of nodes in the OSM query result.
        """
        overpass_url = "http://overpass-api.de/api/interpreter"
        

        # Perform the Overpass API query
        response = requests.get(overpass_url, params={'data': query})
        try:
            nodes = response.json()
            nodeList = nodes["elements"]
        except Exception as e: 
            print("\n", "Incorrect OSM Query, please check the format!", "\n")
            print(e)
        if(len(nodeList)<=0):
            print(f"No Items: Length of nodes is {len(nodeList)}")
            return
        print(f"Length of nodes is {len(nodeList)}")

        csv_data = []
        updated_json = []

        for index, element in enumerate(nodeList):
            json_struct = {"lat":0,"lon":0,"id":0, "source:date":""}
            if(get_way_centers):
                center = element.get("center", "")
                json_struct["lat"] = center.get("lat", "")
                json_struct["lon"] = center.get("lon", "")
                json_struct["id"] = element.get("id", "")
                json_struct["source:date"] = element['tags'].get("source:date", "")
            else:
                json_struct["lat"] = element.get("lat", "")
                json_struct["lon"] = element.get("lon", "")
                json_struct["id"] = element.get("id", "")
                json_struct["source:date"] = element['tags'].get("source:date", "")

            csv_data.append([json_struct["id"], json_struct["lat"] , json_struct["lon"]])
            updated_json.append(json_struct)
        
        with open(csv_file_path, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["index", "latitude", "longitude"])  # Write the header row
            csv_writer.writerows(csv_data)  # Write the data rows
        start_time_cs = time.time()
        filePath= self.search_coordinates(updated_json, Image_size,element_size, filename, label,make_bounding_box_image,bounding_box_image_path)
        end_time_cs = time.time()
        total_execution_time = end_time_cs - start_time_cs
        json_file_path = f"../data/OSM-{filename}.json"
        with open(json_file_path, 'w') as json_file:
            json.dump(nodes, json_file, indent=4)

        return len(nodeList),csv_file_path,json_file_path,filePath,total_execution_time
    
    def check_bounds(self,buffer:Polygon, point:Point):
        in_buffer = buffer.contains_properly(point)
        return in_buffer

    def search_coordinates(self, points, image_size,element_size, filename, label, make_bounding_box_image, bounding_box_image_path):
        """
        Search for points within rectangular buffers, save results to JSON, and create a visualization.

        Args:
            points (list): List of dictionaries with 'lon' and 'lat' coordinates.
            image_size (int): The image size in meters (buffer around the point - radius for square buffer).
            element_size (int): The element_size in meters for creating rectangular buffers.
            filename (str): The filename for saving JSON and the plot.

        Returns:
            None
        """
        longitude_list = [point["lon"] for point in points]
        latitude_list = [point["lat"] for point in points]
        source_dates = [point["source:date"] for point in points]
        id_list = [point["id"] for point in points]

        gdf = gpd.GeoDataFrame(
            geometry=gpd.points_from_xy(longitude_list, latitude_list),
            crs="EPSG:4326" 
        )
        #gdf.to_crs("EPSG:4326")

        buffer_list = []
        for index, point in gdf.iterrows():
            poly = get_coordinates_square(point.geometry,image_size)[0]
            polygon = Polygon([[a[1],a[0]]for a in poly])
            buffer_list.append(polygon)

        spatial_index = myindex.Index()
        for idx, geometry in gdf['geometry'].items():
            spatial_index.insert(idx, geometry.bounds)

        filled_rectangles = []
        for index, buffer in enumerate(buffer_list):
            points_within_buffer = {
                "lat": gdf.loc[index].geometry.x, 
                "lon": gdf.loc[index].geometry.y, 
                "image_paths": [],
                "source:date":source_dates[index],
                "Image-Box": get_coordinates_square(gdf.loc[index].geometry,image_size)[0],
                "index":points[index]["id"], 
                "label":label, 
                "element_size":element_size,
                "bufferpoints": []}
            # get the buffer and check if point is in buffer
            for index, point in gdf.iterrows():
                if self.check_bounds(buffer,point["geometry"]):
                    points_within_buffer["bufferpoints"].append([id_list[index]])
            filled_rectangles.append(points_within_buffer)

        json_string = json.dumps(filled_rectangles, indent=4)
        filePath = f"../data/BufferedObjects-{filename}.json"
        with open(filePath, "w") as json_file:
            json_file.write(json_string)
        print("finished coordinate search")
        if(make_bounding_box_image):
            buffers_gdf = gpd.GeoDataFrame({'geometry': buffer_list}, crs=gdf.crs)
            fig, ax = plt.subplots(figsize=(8, 8))
            gdf.plot(ax=ax, color='blue', markersize=10, label='Points')
            buffers_gdf.boundary.plot(ax=ax, color='red', linewidth=1, linestyle='--', label='Buffers')
            plt.xlabel('Longitude')
            plt.ylabel('Latitude')
            plt.title('Points and Rectangular Buffers')
            plt.legend()
            plt.savefig(f'{bounding_box_image_path}Bounding_boxes_{filename}.png', bbox_inches='tight')
            plt.show()
        return filePath

    # def meters_to_degrees(self, lat, meters):
    #     """
    #     Convert a distance in meters to the equivalent distance in degrees.

    #     Args:
    #         lat (float): Latitude in degrees.
    #         meters (float): Distance in meters.

    #     Returns:
    #         float: Equivalent distance in degrees.
    #     """
    #     earth_radius = 63710088
    #     lat_rad = math.radians(lat)
    #     circumference = 2 * math.pi * earth_radius * math.cos(lat_rad)
    #     degrees_per_meter = 360.0 / circumference
    #     degrees = meters * degrees_per_meter

    #     return degrees
