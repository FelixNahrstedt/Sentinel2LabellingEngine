# config.py

# Specify the Overpass API Query
query = '''[out:json];
area["ISO3166-1"="NL"];
(node["power"="generator"]["generator:source"="wind"]["manufacturer"="Vestas"](area);
);
out center;'''

# ---------- Workflow specifications --------
# if you are starting a new project - set all to true
# If OSM Nodes need to be downloaded and coordinates need to be searched
get_OSM_nodes = True
# if the satellite images are to be downloaded with Google Earth Engine
download_img = True
# if the satellite tif bands should be converted to GeoTif and PNG images
convert_s2=True
# if a coco dataset should be created from the png images
create_dataset = True

# ------------- General Specification -----------
# Specify the size of the Image to be downloaded in meters
Image_Size = 1000  # meters
# Specify the size of the Objects that are supposed to be labelled in meters
Object_Size = 100   # meters
# Filename for Image Consistency
filename = "Netherlands"
# Name of the Object to be labelled
element_name = "Wind_Turbines"
# if the image folder should be removed if there is one 
remove=True
# how many images in total do you want to download (set to 0 if all available should be downloaded)
n_of_scene=1
# from how many different dates the images are supposed to be downloaded
n_images=1

# --------------- Additional changes you could make ----------------
# how big the maximum cloud fraction should be present within an image
cloud_percentage=0.2
# how big the allowed color variablility is within the image (can be set to exclude image borders and sensor mistakes)
variability_threshhold=20
# start dates for the image request
start_dates = ['2023-01-01']
# end dates for the image request
end_dates = ['2023-12-01']
# filepath for saving coordinates from OSM
csv_file_path = f"../data/Coordinates{filename}-{element_name}.csv"
# filepath for saving the buffered coordinates after coordinate search
filePath = f"../data/BufferedObjects-{filename}.json"
# if you use way centers - still in testing 
get_way_centers = False
# if you want to create an image of the bounding boxes needed for the search
make_bounding_box_image = False
# where you want to save it
bounding_box_image_path = "static/images/"



