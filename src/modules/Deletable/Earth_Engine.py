# Google Earth Engine & Python API

import math
import ee
# Authenticate to your Google Earth Engine account
from geetools import batch
import utm


import subprocess
import ee

def authenticate_earth_engine():
    try:
         # Attempt to authenticate via OAuth, which also checks if there's an active session.
        ee.Initialize()
        print("Earth Engine authentication successful.")

    except Exception as e:
        print(f"Error running the Earth Engine Authentication: {e}")

        try:
            # If browser-based authentication fails, attempt to initialize Google Cloud SDK.
            subprocess.run("gcloud init", shell=True)
            ee.Authenticate()
            ee.Initialize()
            print("Google Cloud SDK initialized successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error running the Bash script: {e}")
            print("Please ensure that you have Google Cloud SDK and Earth Engine set up.")

# Call the authentication function to start the process
authenticate_earth_engine()

# def change_in_latitude(kms):
#     '''
#         Given a distance north, it returns the change in latitude
#     '''

#     return (kms/EARTH_RADIUS)*RADIANS_TO_DEGREE

# def change_in_longitude(latitude, kms):
#     '''
#         Given a latitude and a distance west, it returns the change in longitude
#     '''

#     r = EARTH_RADIUS*math.cos(latitude*DEGREES_TO_RADIANS)
#     return (kms/r)*RADIANS_TO_DEGREE

def get_coordinates_square(latitude, longitude, image_size_in_m):
    '''
        Given a latitude and a longitude it returns a square of size=size of coordinates
    '''

    half_size = image_size_in_m/2
    # slat = latitude+change_in_latitude(-half_size)
    # nlat = latitude+change_in_latitude(half_size)
    # wlon = longitude+change_in_longitude(latitude, -half_size)
    # elon = longitude+change_in_longitude(latitude, half_size)
    
    easting, northing, zone_number, zone_letter = utm.from_latlon(latitude, longitude)

    # For a rectangle buffer, for east and west only latitudes are important, for north and south longitudes

    slat = utm.to_latlon(easting-(half_size), northing-(half_size),zone_number,zone_letter)
    wlon = utm.to_latlon(easting-(half_size), northing+(half_size),zone_number,zone_letter)
    nlat = utm.to_latlon(easting+(half_size), northing+(half_size),zone_number,zone_letter)
    elon = utm.to_latlon(easting+(half_size), northing-(half_size),zone_number,zone_letter)

    return ['[[{:.4f},{:.4f}],[{:.4f},{:.4f}],[{:.4f},{:.4f}],[{:.4f},{:.4f}]]'.format(wlon[1],nlat[0],elon[1],nlat[0],wlon[1],slat[0],elon[1],slat[0]), [wlon[1],slat[0],elon[1],nlat[0]]]

def get_region_and_rectangle(longitude_list, latitude_list, image_size_m):
    '''
        Given a latitude and a longitude list it returns a square of coordinates list
    '''
    regions = []
    rectangles = []

    for i in range(len(longitude_list)):
        # buffers the objects
        coordinates_square = get_coordinates_square(longitude_list[i], latitude_list[i], image_size_in_m=image_size_m)
        regions.append(coordinates_square[0])
        rectangles.append(coordinates_square[1])

    return regions, rectangles

def get_s2_data_from_gge(aoi, start_date, end_date, selectors = ["B2", "B3", "B4", "QA60"]):
    patch = ee.Geometry.Rectangle(aoi)
    dataset = ee.ImageCollection("COPERNICUS/S2")\
        .filterBounds(patch)\
        .filterDate(start_date,end_date)\
        .sort('system:time_start', True)\
        .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', 0))
    # The final product will contains 4 bands, the RGB bands and the QA60 band
    #dataset = filter_cloudy(dataset)
    dataset = dataset.select(selectors)
    available_images = dataset.getInfo()
    data = dataset.toList(dataset.size())
    length = len(available_images['features'])
    # Iterate through the collection and get acquisition dates
    return data, length

def download_s2_data(data, region, zone_name, date, download_path, n_imgs=3, selectors = ["B2", "B3", "B4", "QA60"]):
    downloaded_image = 0

    for i in range(1, n_imgs+1):
        try:
            image = ee.Image(data.get(i))
            image.select(selectors)
            name = image.id().getInfo()
            acquisition_date = image.date().format('YYYY-MM-dd').getInfo()
            batch.image.toLocal(image, name=name, path=download_path, scale=10, region=region, toFolder=True)
            #print('\nDownloading Zone %s, date: %s, img: %d of %d' % (zone_name, date, i, n_imgs))
            downloaded_image = downloaded_image + 1
        except Exception:
            print('          ! No Acceptable data for zone %s, period: %s, img: %d of %d' % (zone_name, date, i, n_imgs))
            pass
    print('\n=> Downloaded %d of %d' % (downloaded_image, n_imgs))

def filter_cloudy(image_collection:ee.ImageCollection, max_cloud_fraction=0.5):
    return image_collection.filter(ee.Filter.eq('CLOUD_COVER', max_cloud_fraction));

def get_s1_data_from_gge(rectangle, start_date, end_date, selectors = ["VV"]):
    patch = ee.Geometry.Rectangle(rectangle)
    dataset = ee.ImageCollection("COPERNICUS/S1_GRD").filterBounds(patch).filterDate(start_date,end_date).sort('system:time_start', True)
    # The final product will contains 4 bands, the RGB bands and the QA60 band
    #dataset = filter_cloudy(dataset)
    dataset = dataset.select(selectors)
    #dataset = dataset.filter(ee.Filter.eq('orbitProperties_pass','ASCENDING'))
    data = dataset.toList(dataset.size())
    available_images = dataset.getInfo()
    length = len(available_images['features'])

    return data, length

def download_s1_data(data, region, zone_name, date, download_path, n_imgs=3, selectors = ["VV"]):
    downloaded_image = 0

    for i in range(1, n_imgs+1):
        try:
            image = ee.Image(data.get(i))
            image.select(selectors)
            name = image.id().getInfo()
            batch.image.toLocal(image, name=name, path=download_path, scale=10, region=region, toFolder=True)
            #print('          Downloading Zone %s, period: %s, img: %d of %d' % (zone_name, date, i, n_imgs))
            downloaded_image = downloaded_image + 1
        except Exception:
            print('          ! Missing data for zone %s, period: %s, img: %d of %d' % (zone_name, date, i, n_imgs))
            pass
    print('\n=> Downloaded %d of %d' % (downloaded_image, n_imgs))
