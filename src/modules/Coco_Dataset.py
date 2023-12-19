import datetime
import math
import os
import json
import glob
import time
from timeit import Timer
import fiftyone as fo
import numpy as np
import rasterio
from shapely.geometry import Point
from helper_functions import get_coordinates_square
import geopandas as gpd
from decimal import Decimal, getcontext
from shapely import Polygon
import geopandas as gpd
import utm
import geopy.distance as gp
from pyproj import Proj, transform
from pyproj import Transformer
from PIL import Image 
from math import radians, cos, sin, asin, sqrt


class DatasetCreator:
    def __init__(self):
        pass

    def create_dataset(self, path_images, path_json,path_filtered_json, obj_name, Coco_path,label_radius):
        folders = self.get_subfolders(path_images)
        json_data = self.load_json(path_json)
        filtered_json = self.filter_json_entries(json_data, folders, path_images,label_radius)
        self.save_json(path_filtered_json, filtered_json)
        dataset = self.create_coco(Coco_path, filtered_json, obj_name)
        session = fo.launch_app(dataset, port=4000, desktop=True)
        session.wait()

    def get_subfolders(self, folder_path):
        items = os.listdir(folder_path)
        subfolders = [item for item in items if os.path.isdir(os.path.join(folder_path, item))]
        return subfolders

    def load_json(self, json_path):
        with open(json_path, 'r') as file:
            json_data = json.load(file)
        return json_data

    def save_json(self, json_path, data):
        with open(json_path, 'w') as json_file:
            json.dump(data, json_file, indent=2)

    def haversine(self, lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance in kilometers between two points 
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
        return c * r

    def calculate_relative_coordinates(self, rectangle_inner, label, label_radius,extra_data):
        # Define the transformation parameters
        crs, transform, image_width, image_height,bounds = extra_data
        Sentinel_Resolution = 10
        [elat, nlon, wlat, slon] = rectangle_inner
        [left, bottom, right, top]= bounds
        Top_Left_Outer = (left,top) #TopRight
        #Bottom_Left_Outer = (sw_longitude,se_latitude)#Borrom right
        Bottom_Right_Outer = (right,bottom)#bottom left
        #Top_Right_Outer = (ne_longitude,ne_latitude)
        transformer = Transformer.from_crs("EPSG:4326",str(crs),always_xy=True)
        nlon, wlat = transformer.transform(nlon, wlat)
        Top_Left_Inner = (nlon, wlat) 
        #Top_Right_Inner = (nlon,elat)
        slon, elat = transformer.transform(slon, elat)
        Bottom_Right_Inner = (slon, elat) 
        #Bottom_Left_Inner = (slon,wlat)

        # dist1 = self.haversine(Top_Left_Inner[1],Bottom_Right_Inner[0],Bottom_Right_Inner[1],Bottom_Right_Inner[0])*1000
        # dist2 = self.haversine(Top_Left_Inner[1],Top_Left_Inner[0],Bottom_Right_Inner[1],Top_Left_Inner[0])*1000

        #print(outer_width,outer_height)
        width_outer = abs(left - right)
        height_outer = abs(top - bottom)
        radius = label_radius/width_outer
      
        offset_east_west = (Top_Left_Inner[0] - Top_Left_Outer[0])
        offset_north_south = (Top_Left_Outer[1] - Top_Left_Inner[1])

        relative_top_left_x = offset_east_west / width_outer
        relative_top_left_y = offset_north_south / height_outer

        bbox = {"bbox": [relative_top_left_x, relative_top_left_y, radius, radius], "label": label}
        return bbox

    def get_relative_filenames(self, folder_path):
        # Get a list of all items in the folder
        items = os.listdir(folder_path)

        # Filter out non-file items (subfolders, etc.)
        files = [item for item in items if os.path.isfile(os.path.join(folder_path, item))]

        # Get relative filenames
        relative_filenames = [os.path.join(folder_path, file) for file in files]

        return relative_filenames
    
    def filter_json_entries(self, json_structure, id_list, path_images,label_radius):
        filtered_entries = []
        for entry in json_structure:
            if str(entry["index"]) in id_list:
                files = self.get_relative_filenames(os.path.join(path_images, str(entry["index"])))
                entry["image_paths"] = files
                new_bufferpoints = []
                for bufferpoint in entry["bufferpoints"]:
                    try:
                        # img = Image.open(files[0])
                        newStr = str(files[0]).replace("PNG", "GeoTif")
                        newStr = str(newStr).replace("png", "tif")

                        extra_data = None
                        with rasterio.open(newStr) as src:
                            # Replace these with the actual latitude and longitude of your point
                            # Get the affine transformation matrix
                            extra_data = [src.crs, src.transform, src.width, src.height,src.bounds]
    
                    except Exception as e:
                        print("Image filtered out because of low color variability",e)
                        continue

                    lat_long = [[item["lat"], item["lon"]] for item in json_structure if "index" in item and
                                item["index"] == bufferpoint[0]][0]
                    polygon = get_coordinates_square(Point(lat_long[0], lat_long[1]), entry["element_size"])[1]
                    new_bufferpoints.append(
                        self.calculate_relative_coordinates(polygon, entry["label"], label_radius,extra_data))
                entry["bufferpoints"] = new_bufferpoints
                filtered_entries.append(entry)
        return filtered_entries

    def create_coco(self, save_dataset_path, filtered_json, obj_name):
        datasets = fo.list_datasets()
        for dataset in datasets:
            set = fo.load_dataset(dataset)
            set.delete()
        hash_name = hash(datetime.datetime.now())
        dataset = fo.Dataset(name=str(str(hash_name) + "__" + obj_name), persistent=False, overwrite=True)
        detections = []
        for images_for_location in filtered_json:
            for different_dates_path in images_for_location["image_paths"]:
                sample = fo.Sample(filepath=different_dates_path)
                for obj in images_for_location["bufferpoints"]:
                    label = obj["label"]
                    bounding_box = obj["bbox"]
                    detections.append(
                        fo.Detection(label=label,
                                     bounding_box=bounding_box,
                                     image_index=images_for_location["index"],
                                     latitude=images_for_location["lat"],
                                     longitude=images_for_location["lon"],
                                     OSM_Date=images_for_location["source:date"]))
                sample[obj_name] = fo.Detections(detections=detections)
                dataset.add_sample(sample)
                detections = []

        label_field = obj_name
        dataset.export(
            export_dir=save_dataset_path,
            dataset_type=fo.types.COCODetectionDataset,
            label_field=label_field,
        )
        return dataset
    

