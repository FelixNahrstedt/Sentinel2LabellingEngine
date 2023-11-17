import geopandas as gpd
import requests
import json
from rtree import index as myindex
import matplotlib.pyplot as plt
import math
import utm
import csv
from shapely.geometry import Point, Polygon

class OSM_Downloader:
    def __init__(self):
        pass

    def query_OSM(self, query, Image_size, element_size, filename):
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
        csv_file_path = f"../data/Latest_Coordinates_{filename}.csv"

        # Perform the Overpass API query
        response = requests.get(overpass_url, params={'data': query})
        nodes = response.json()
        nodeList = nodes["elements"]
        if(len(nodeList)<=0):
            print(f"No Items: Length of nodes is {len(nodeList)}")
            return
        print(f"Length of nodes is {len(nodeList)}")

        csv_data = []

        for index, element in enumerate(nodeList):
            lat = element.get("lat", "")
            lon = element.get("lon", "")
            id = element.get("id", "")
            csv_data.append([id, lat, lon])

        with open(csv_file_path, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["index", "latitude", "longitude"])  # Write the header row
            csv_writer.writerows(csv_data)  # Write the data rows

        self.search_coordinates(nodeList, Image_size,element_size, filename)
        json_file_path = f"../data/OSM-{filename}.json"
        with open(json_file_path, 'w') as json_file:
            json.dump(nodes, json_file, indent=4)

        return len(nodeList),csv_file_path,json_file_path

    def search_coordinates(self, points, image_size,element_size, filename):
        """
        Search for points within rectangular buffers, save results to JSON, and create a visualization.

        Args:
            points (list): List of dictionaries with 'lon' and 'lat' coordinates.
            distance (int): The distance in meters for creating rectangular buffers.
            filename (str): The filename for saving JSON and the plot.

        Returns:
            None
        """
        longitude_list = [point["lon"] for point in points]
        latitude_list = [point["lat"] for point in points]
        source_dates = [point['tags'].get("source:date", None) for point in points]
        id_list = [point["id"] for point in points]

        gdf = gpd.GeoDataFrame(
            geometry=gpd.points_from_xy(longitude_list, latitude_list),
            crs="EPSG:4326"
        )

        buffer_list = []
        for index, point in gdf.iterrows():
            buffer_distance = self.meters_to_degrees(point.geometry.x, image_size)
            lon_lat_list = self.point_to_buffer(point,image_size)
            polygon = Polygon([lon_lat_list["Northwest"],lon_lat_list["Southwest"],lon_lat_list["Southeast"],lon_lat_list["Northeast"]])
            buffer = point.geometry.buffer(buffer_distance, cap_style=3)
            buffer_list.append(polygon)

        spatial_index = myindex.Index()
        for idx, geometry in gdf['geometry'].items():
            spatial_index.insert(idx, geometry.bounds)

        filled_rectangles = []
        for index, buffer in enumerate(buffer_list):
            points_within_buffer = {
                "lat": gdf.loc[index].geometry.x, 
                "lon": gdf.loc[index].geometry.y, 
                "source:date":source_dates[index],
                "Image-Box": self.point_to_buffer(gdf.loc[index],image_size),
                "index":points[index]["id"], 
                "bufferpoints": []}
            for idx in spatial_index.intersection(buffer.bounds):
                point = gdf.loc[idx]
                if buffer.contains(point['geometry']):
                    points_within_buffer["bufferpoints"].append(self.point_to_buffer(point,element_size))
            filled_rectangles.append(points_within_buffer)

        json_string = json.dumps(filled_rectangles, indent=4)
        with open(f"../data/BufferedObjects-{filename}.json", "w") as json_file:
            json_file.write(json_string)

        buffers_gdf = gpd.GeoDataFrame({'geometry': buffer_list}, crs=gdf.crs)

        fig, ax = plt.subplots(figsize=(8, 8))
        gdf.plot(ax=ax, color='blue', markersize=10, label='Points')
        buffers_gdf.boundary.plot(ax=ax, color='red', linewidth=1, linestyle='--', label='Buffers')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.title('Points and Rectangular Buffers')
        plt.legend()
        plt.savefig(f'static/images/Bounding_boxes_{filename}.png', bbox_inches='tight')
        plt.show()

    def point_to_buffer(self,point,distance):
        """
        Given a point and a distance in meters, it returns
        Latitudes/Longitudes of the Northwest,Southwest,Southeast and Northeast buffer

        """
        easting, northing, zone_number, zone_letter = utm.from_latlon(point.geometry.x, point.geometry.y)
        lon_lat_list = {"Northwest":utm.to_latlon(easting-(distance/2), northing+(distance/2),zone_number,zone_letter),
                        "Southwest":utm.to_latlon(easting-(distance/2), northing-(distance/2),zone_number,zone_letter),
                        "Southeast":utm.to_latlon(easting+(distance/2), northing-(distance/2),zone_number,zone_letter),
                        "Northeast":utm.to_latlon(easting+(distance/2), northing+(distance/2),zone_number,zone_letter),
        }
        return lon_lat_list

    def meters_to_degrees(self, lat, meters):
        """
        Convert a distance in meters to the equivalent distance in degrees.

        Args:
            lat (float): Latitude in degrees.
            meters (float): Distance in meters.

        Returns:
            float: Equivalent distance in degrees.
        """
        earth_radius = 63710088
        lat_rad = math.radians(lat)
        circumference = 2 * math.pi * earth_radius * math.cos(lat_rad)
        degrees_per_meter = 360.0 / circumference
        degrees = meters * degrees_per_meter

        return degrees
