#import downloader
import pandas as pd
import numpy as np
import shutil
#import Earth_Engine as gee
import os



class Data_Management:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Data_Management, cls).__new__(cls)
            cls._instance.__initialized = False

        return cls._instance

    def __init__(
            self,
            points_path: str = "",
            file_path_filtered_json:str = "",
            start_dates: list[str] = [""],
            end_dates: list[str] = [""],
            patch_size: int = 0,
            windows: bool = True,
            get_OSM_nodes:bool = True,
            download_img:bool = True,
            convert_s2: bool = False,
            create_dataset:bool = False,
            base_path: str = '../data/',
            n_of_scene: int = 20,
            n_images: int = 1,
            cloud_percentage:float = 0.2,
            satellites: list[str] = ["S2"],
            date_names: list[str] = [''],
            s2_bands: list[str] = ["B2", "B3", "B4"],
            s1_bands: list[str] = ["VV"],
            remove: bool = False
        ):
        """
        Initializes DataProcessingConfiguration with default parameters and paths.

        Parameters:
        - points_path (str): Path to the OSM nodes data including latitude and longitude.
        - start_dates (list[str]): The start date for image downloads (if multiple, make a list).
        - end_dates (list[str]): The end date for image downloads (if multiple, make a list).
        - patch_size (int): The size of the image patch in meters.
        - windows (bool): Set to True if running on Windows, False otherwise for path correction.
        - convert_s2 (bool): Set to True to enable Sentinel-2 data conversion to PNG.
        - base_path (str): The base path for data storage.
        - n_of_scene (int): The number of OSM Node data (scenes) to download.
        - n_images (int): The number of images to download for the same scene (for different overpass times). (if 1 only the first one that was found will be downloaded)
        - cloud_percentage (float): The amount of cloud coverage that is allowed maximum between 0 and 1
        - satellites (list[str]): A list of satellite names to download images from - only so far ["S1", "S2"].
        - date_names (list[str]): Names for the date periods.
        - s2_bands (list[str]): Bands or selectors for Sentinel-2 images. e.g., ["B2", "B3", "B4"]
        - s1_bands (list[str]): Bands or selectors for Sentinel-1 images. e.g., ["VV"]
        - remove (bool): Set to True to enable removal of previous TIFF files within the base_path/Images folder.

        Attributes:
        - download_path (str): The path for downloaded images.
        - downloads_folder_path (str): The path for downloaded images folder.
        - sen2_images_base_path (str): The base path for Sentinel-2 images.
        - sen1_images_base_path (str): The base path for Sentinel-1 images.
        """

        if not self.__initialized:
            self.points_path =points_path
            self.windows = windows
            self.convert_s2 = convert_s2
            self.remove = remove
            self.satellites = satellites
            self.file_path_filtered_json = file_path_filtered_json
            self.start_dates = start_dates
            self.end_dates = end_dates
            self.download_img = download_img
            self.get_OSM_nodes = get_OSM_nodes
            self.date_names = date_names
            self.create_dataset = create_dataset
            self.n_images = n_images
            self.s2_bands = s2_bands
            self.s1_bands = s1_bands
            self.n_of_scene = n_of_scene
            self.patch_size = patch_size  
            self.cloud_percentage = cloud_percentage
            if(cloud_percentage>1 or cloud_percentage<0):
               self.cloud_percentage = 0.2
               print(f"Cloud Percentage has been set to {str(self.cloud_percentage)} as it was not between 0 and 1")
            # Define paths for data storage
            self.download_path = os.path.join(base_path, "Downloads")
            self.downloads_folder_path = os.path.join(base_path, 'Downloads', '*') if windows else os.path.join(base_path, 'Downloads', '*')
            self.image_path = os.path.join(base_path, 'Images')
            os.makedirs(self.image_path, exist_ok=True)
            os.makedirs(self.download_path, exist_ok=True)
            self.sen2_images_base_path = os.path.join(base_path, 'Images/')
            self.sen1_images_base_path = os.path.join(base_path, 'Images/')
            self.__initialized = True

    def __get_points(self, points_path):
        """
        Load latitude and longitude data from a CSV file.

        Parameters:
        - points_path (str): Path to the CSV file containing latitude and longitude data.

        Returns:
        - points (numpy.ndarray): A NumPy array containing latitude and longitude points.
        """
        data_frame = pd.read_csv(points_path, index_col=0)
        data = data_frame.reset_index().to_numpy()

        num_points = len(data)
        points = np.ones((3, num_points))

        for i in range(num_points):
            points[0, i] = data[i][1]
            points[1, i] = data[i][2]
            points[2, i] = data[i][0]
        
        return points
    
    def set_filepath_filtered_json(self,filepath):
        self.file_path_filtered_json = filepath
        self.points = self.__get_points(self.points_path)
        self.latitude_list = self.points[1, :]
        self.longitude_list = self.points[0, :]




