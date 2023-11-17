# Example usage:
# Create an instance of the class with default presets
from Meta_Information import Data_Management
from Sat_Converter import Sentinel2Converter
from OSM_Query import OSM_Downloader
from Sat_Downloader import Satellite_Downloader

query = '''[out:json];
    area["ISO3166-1"="NL"];
    (node["power"="generator"]["generator:source"="wind"]["manufacturer"="Vestas"](area);
    );
    out center;'''

# Osm = OSM_Downloader()
# amount, csv, json = Osm.query_OSM(query,1000,100,"Niederlandee")
# Data_Settings = Data_Management(points_path=csv,
#                                 start_dates=['2019-01-01'], 
#                                 end_dates=['2019-12-01'],
#                                 patch_size=1000,
#                                 remove=True,
#                                 convert_s2=True,
#                                 n_of_scene=5,
#                                 n_images=2,
#                                 cloud_percentage=2)
# Downloader = Satellite_Downloader(Data_Settings)
# Downloader.GEE_download()

# if(Data_Settings.convert_s2):
converter = Sentinel2Converter()
#     converter.to_png("../data/Images/",["B2","B3","B4"], "../data/PNG/", remove=True)
converter.to_geoTiff("../data/Images/",["B2","B3","B4"], "../data/GeoTif/", remove=True)
