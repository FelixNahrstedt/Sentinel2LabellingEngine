# Example usage:
# Create an instance of the class with default presets
from Meta_Information import Data_Management
from Sat_Converter import Sentinel2Converter
from OSM_Query import OSM_Downloader
from Sat_Downloader import Satellite_Downloader
from Coco_Dataset import DatasetCreator
import time

# replace name for name of your config file
from config.config_turbines_Netherlands import query, Image_Size, Object_Size, filename, element_name, csv_file_path, filePath, get_way_centers, start_dates, end_dates, remove, n_of_scene, n_images, cloud_percentage, variability_threshhold, get_OSM_nodes, download_img, convert_s2, create_dataset,make_bounding_box_image,bounding_box_image_path

Data_Settings = Data_Management(points_path=csv_file_path,
                                file_path_filtered_json=filePath,
                                start_dates=start_dates, 
                                end_dates=end_dates,
                                patch_size=Image_Size,
                                remove=remove,
                                get_OSM_nodes = get_OSM_nodes,
                                download_img = download_img,
                                convert_s2=convert_s2,
                                create_dataset = create_dataset,
                                n_of_scene=n_of_scene,
                                n_images=n_images,
                                cloud_percentage=cloud_percentage)

if(Data_Settings.get_OSM_nodes):
    Osm = OSM_Downloader()
    amount, csv, json,filePath = Osm.query_OSM(query,Image_Size,Object_Size,filename,element_name, csv_file_path,make_bounding_box_image, bounding_box_image_path,get_way_centers=get_way_centers)
    Data_Settings.set_filepath_filtered_json(filePath)

if(Data_Settings.download_img):
    Downloader = Satellite_Downloader(Data_Settings)
    Downloader.GEE_download()

if(Data_Settings.convert_s2):
    converter = Sentinel2Converter()
    converter.to_geoTiff("../data/Images/",["B2","B3","B4"], f"../data/GeoTif_{filename}_{element_name}/", remove=True)
    converter.to_png("../data/Images/",["B2","B3","B4"], f"../data/PNG_{filename}_{element_name}/", remove=True,variability_threshhold=variability_threshhold)

if(Data_Settings.create_dataset):
    creator = DatasetCreator()
    creator.create_dataset(f"../data/PNG_{filename}_{element_name}", Data_Settings.file_path_filtered_json,f"../data/{filename}-{element_name}-{Image_Size}.json", element_name, "../data/COCO", Object_Size)

