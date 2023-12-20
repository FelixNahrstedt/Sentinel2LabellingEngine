import base64
import hashlib
import os
import subprocess
import ee
from geetools import batch
import urllib.parse
from Meta_Information import Data_Management
from helper_functions import get_coordinates_square
from shapely import Point

class EarthEngineDownloader:
    def __init__(self,information:Data_Management,ids:list):
        """
        Initialize the EarthEngineDownloader class.
        """
        self.information = information
        self.ids = ids
        self.authenticate_earth_engine()
        self.get_scenes_and_rectangles()
    
    def base64param(self,byte_string: bytes) -> bytes:
        """Encodes bytes for use as a URL parameter."""
        return base64.urlsafe_b64encode(byte_string).rstrip(b'=')


    def _nonce_table(self,*nonce_keys: str):
        """Makes random nonces, and adds PKCE challenges for each _verifier nonce."""
        table = {}
        for key in nonce_keys:
            table[key] = self.base64param(os.urandom(32))
            if key.endswith('_verifier'):
                # Generate a challenge that the server will use to ensure that requests
                # only work with our verifiers.  https://tools.ietf.org/html/rfc7636
                pkce_challenge = self.base64param(hashlib.sha256(table[key]).digest())
                table[key.replace('_verifier', '_challenge')] = pkce_challenge
        return {k: v.decode() for k, v in table.items()}

    def authenticate_earth_engine(self):
        """
        Authenticate to the Google Earth Engine account.
        """
        try:
            ee.Initialize()
            print("Earth Engine authentication successful.")
        except Exception as e:
            print(f"Error running the Earth Engine Authentication: {e}")
            try:
                nonces = ['request_id', 'token_verifier', 'client_verifier']
                request_info = self._nonce_table(*nonces)
                AUTH_PAGE_URL = 'https://code.earthengine.google.com/client-auth'
                SCOPES = [
                    'https://www.googleapis.com/auth/earthengine',
                    'https://www.googleapis.com/auth/devstorage.full_control'
                ]
                AUTH_URL_TEMPLATE = AUTH_PAGE_URL + '?scopes={scopes}' + (
                    '&request_id={request_id}&tc={token_challenge}&cc={client_challenge}')
                url = AUTH_URL_TEMPLATE.format(
                    scopes=urllib.parse.quote(' '.join(SCOPES)), **request_info)
                code_verifier = ':'.join(request_info[k] for k in nonces)
                #auth_url, code_verifier = ee.Authenticate(quiet=True, auth_mode="notebook")
                print(f"Go to: {url}")
                auth_code = input("Authentication code:")
                ee.Authenticate(authorization_code=auth_code,code_verifier=code_verifier)
                #ee.Authenticate(auth_mode="notebook")
                ee.Initialize()
                print("Google Cloud SDK initialized successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error running the Bash script: {e}")
                print("Please ensure that you have Google Cloud SDK and Earth Engine set up.")

    # def get_coordinates_square(self, latitude, longitude, image_size_in_m):
    #     """
    #     Given a latitude and a longitude, return a square of size `image_size_in_m` of coordinates.

    #     Parameters:
    #     - latitude: Latitude of the center point.
    #     - longitude: Longitude of the center point.
    #     - image_size_in_m: Size of the square in meters.

    #     Returns:
    #     A list containing coordinates in GeoJSON format and a list of bounding box coordinates.
    #     """
    #     half_size = image_size_in_m / 2
    #     easting, northing, zone_number, zone_letter = utm.from_latlon(latitude, longitude)
    #     slat = utm.to_latlon(easting - half_size, northing - half_size, zone_number, zone_letter)
    #     wlon = utm.to_latlon(easting - half_size, northing + half_size, zone_number, zone_letter)
    #     nlat = utm.to_latlon(easting + half_size, northing + half_size, zone_number, zone_letter)
    #     elon = utm.to_latlon(easting + half_size, northing - half_size, zone_number, zone_letter)

    #     coordinates_geojson = [
    #         [wlon[1], nlat[0]], [elon[1], nlat[0]],
    #         [elon[1], slat[0]], [wlon[1], slat[0]]
    #     ]
    #     # [Northwestern Longitude, Southwestern Latitude, Southeastern Longitude, Northeastern Latitude]
    #     bounding_box = [wlon[1], slat[0], elon[1], nlat[0]]
    #     return coordinates_geojson, bounding_box

    def get_scenes_and_rectangles(self):
        """
        Given latitude and longitude lists, return a list of scenes and rectangles.

        Parameters:
        - longitude_list: List of longitudes.
        - latitude_list: List of latitudes.
        - image_size_m: Size of the square in meters.

        Returns:
        Lists of scenes and rectangles.
        """
        scene = []
        rectangles = []

        for i in range(len(self.information.longitude_list)):
            coordinates_square = get_coordinates_square(Point([self.information.longitude_list[i], self.information.latitude_list[i]]), self.information.patch_size)
            
            scene.append(coordinates_square[0])
            rectangles.append(coordinates_square[1])

        self.scenes = scene
        self.rectangles = rectangles

        return len(scene)

    def get_s2_data_from_gge(self, number_of_scene, number_of_date):
        """
        Get Sentinel-2 data from Google Earth Engine.

        Parameters:
        - aoi: Area of interest (rectangle coordinates).
        - start_date: Start date of the time period.
        - end_date: End date of the time period.
        - selectors: List of bands to select.

        Returns:
        A list of Sentinel-2 images and the number of images available.
        """
        patch = ee.Geometry.Rectangle(self.rectangles[number_of_scene],proj="EPSG:4326")
        dataset = ee.ImageCollection("COPERNICUS/S2")\
            .filterBounds(patch)\
            .filterDate(self.information.start_dates[number_of_date], self.information.end_dates[number_of_date])\
            .sort('system:time_start', True)\
            .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', self.information.cloud_percentage))

        dataset = dataset.select(self.information.s2_bands)
        available_images = dataset.getInfo()
        data = dataset.toList(dataset.size())
        length = len(available_images['features'])
        self.s2data = data

        return length

    def download_s2_data(self, number_of_scene, number_of_date):
        """
        Download Sentinel-2 data from Google Earth Engine.

        Parameters:
        - data: List of Sentinel-2 images.
        - region: Region coordinates in GeoJSON format.
        - zone_name: Name of the zone.
        - date: Date of the data.
        - download_path: Path to download the data.
        - n_images: Number of images to download.
        - selectors: List of bands to select.
        """
        downloaded_image = 0

        for i in range(1, self.information.n_images+1):
            try:
                image = ee.Image(self.s2data.get(i))
                image.select(self.information.s2_bands)
                name = image.id().getInfo()
                acquisition_date = image.date().format('YYYY-MM-dd').getInfo()
                batch.image.toLocal(image, name=name, path=self.information.download_path, region=self.scenes[number_of_scene], toFolder=True)
                #print(f'          * Zone {zone_name}, period: {date}, img: {i} of {n_images}')
                downloaded_image += 1
            except Exception:
                print(f'          ! No Acceptable data for zone {self.ids[number_of_scene]}, period: {self.information.start_dates[number_of_date]}-{self.information.end_dates[number_of_date]}, img: {i} of {self.information.n_images}')
                pass
        print(f'          => Downloaded {downloaded_image} of {self.information.n_images}')

    def filter_cloudy(self, image_collection, max_cloud_fraction=0.5):
        """
        Filter cloudy images from an image collection.

        Parameters:
        - image_collection: Google Earth Engine ImageCollection.
        - max_cloud_fraction: Maximum allowed cloud cover fraction.

        Returns:
        Filtered ImageCollection.
        """
        return image_collection.filter(ee.Filter.eq('CLOUD_COVER', max_cloud_fraction))

    def get_s1_data_from_gge(self, number_of_scene, number_of_date):
        """
        Get Sentinel-1 data from Google Earth Engine.

        Parameters:
        - rectangle: Bounding box coordinates.
        - start_date: Start date of the time period.
        - end_date: End date of the time period.
        - selectors: List of bands to select.

        Returns:
        A list of Sentinel-1 images and the number of images available.
        """
        patch = ee.Geometry.Rectangle(self.rectangles[number_of_scene])
        dataset = ee.ImageCollection("COPERNICUS/S1_GRD").filterBounds(patch).filterDate(self.information.start_dates[number_of_date], self.information.end_dates[number_of_date]).sort('system:time_start', True)
        dataset = dataset.select(self.information.s1_bands)
        data = dataset.toList(dataset.size())
        available_images = dataset.getInfo()
        length = len(available_images['features'])
        
        self.s2data = data

        return length

    def download_s1_data(self, number_of_scene, number_of_date):
            """
            Download Sentinel-1 data from Google Earth Engine.

            Parameters:
            - data: List of Sentinel-1 images.
            - region: Region coordinates in GeoJSON format.
            - zone_name: Name of the zone.
            - date: Date of the data.
            - download_path: Path to download the data.
            - n_images: Number of images to download.
            - selectors: List of bands to select.
            """
            downloaded_image = 0

            for i in range(1, self.information.n_images+1):
                try:
                    image = ee.Image(self.s1data.get(i))
                    image.select(self.information.s1_bands)
                    name = image.id().getInfo()
                    batch.image.toLocal(image, name=name, path=self.information.download_path, scale=10, region=self.scenes[number_of_scene], toFolder=True)
                    #print(f'          * Zone {zone_name}, period: {date}, img: {i} of {n_images}')
                    downloaded_image += 1
                except Exception:
                    print(f'          ! No Acceptable data for zone {self.ids[number_of_scene]}, period: {self.information.start_dates[number_of_date]}-{self.information.end_dates[number_of_date]}, img: {i} of {self.information.n_images}')
                    pass
            print(f'          => Downloaded {downloaded_image} of {self.information.n_images}')
