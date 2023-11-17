import os
import shutil
from zipfile import ZipFile
from glob import glob
from time import sleep
from Meta_Information import Data_Management
from Google_Earth_Engine import EarthEngineDownloader

class Satellite_Downloader:
    def __init__(self, information:Data_Management):
        
        self.information = information
        if(self.information.remove):
            self.remove_old_images()

    def get_ids(self):
        '''
        It creates a symbolic name for a downloaded file using the longitude and latitude values
        '''
        
        lat = self.information.points[0, :]
        lon = self.information.points[1, :]
        id = self.information.points[2, :]
        ids = []
        for i in range(len(lat)):
            ids.append('lat_' + str(lat[i]) + '_lon_' + str(lon[i]))

        return id

    def __find(self):
        """
        Returns the paths of files contained in a directory, excluding 'ini' files.

        :return: A list of file paths in the specified directory.
        """
        # Get all file paths in the directory
        names = glob(self.information.downloads_folder_path)

        # Exclude 'ini' files from the list
        names = [name for name in names if not name.endswith('ini')]

        return names

    def data_extractor(self, sentinel_path, id, date):
        """
        Extracts downloaded Sentinel images, organizes them into folders, and removes the zip files.

        Parameters:
        - sentinel_path (str): The base path for Sentinel images.
        - zone_name (str): The name of the geographic zone.
        - date (str): The date of the Sentinel images.

        This function first identifies downloaded zip files, removes non-zip files, and extracts the content
        into folders organized by zone and date. After extraction, it removes all the zip files.

        Raises:
        - Exception: An exception is caught and printed if there is an issue during the extraction process.
        """
        names = self.__find()

        for i in range(len(names)):
            if not ('.zip' in names[i]):
                shutil.rmtree(names[i])

        names = self.__find()

        # It tries to extract all the downloaded image into a folder
        for i in range(len(names)):
            if self.information.windows == True:
                f = names[i].split('.')[0].split('\\')
                fn = f[len(f) - 1]
                pos = os.path.join(sentinel_path + str(id)[:-2], os.path.join(date, fn))
            else:
                f = names[i].split('.')[0].split('/')
                fn = f[len(f) - 1]
                pos = os.path.join(sentinel_path + str(id)[:-2], os.path.join(date, fn))

            os.makedirs(pos, exist_ok=True)
            try:
                with ZipFile(names[i], 'r') as ZipObj:
                    ZipObj.extractall(pos)
                    print('               + Extracting file %d of %d' % (i + 1, len(names)))
            except Exception:
                print('               !!! Extraction exception !!!')
                pass
        # After the extraction it removes all the zip files
        for i in range(len(names)):
            os.remove(names[i])

    def GEE_download(self):
        """
        Downloads Sentinel-2 and Sentinel-1 images using Google Earth Engine.

        This function initiates the download process for Sentinel-2 and Sentinel-1 images from Google Earth Engine.
        It uses the EarthEngineDownloader class to retrieve information about scenes, rectangles, and download data.
        The downloaded data is then organized and extracted from the zipped downloads.

        Raises:
        - Exception: An exception may be raised during the download process, and it will be printed to the console.
        """

        ids = self.get_ids()

        # Assuming EarthEngineDownloader is another class with the required methods
        # You may need to adjust this part based on your actual implementation
        EE_Downloader = EarthEngineDownloader(
            information=self.information,
            ids=ids
        )

        amount_of_points = EE_Downloader.get_scenes_and_rectangles()

        self.n_scenes = self.information.n_of_scene
        self.n_images = self.information.n_images
        if self.information.n_of_scene == 0:
            self.n_scenes = amount_of_points

        for scene in range(0, self.n_scenes):
            # --------------------------------------------- SENTINEL-2 ---------------------------------------------
            if "S2" in self.information.satellites:
                for period in range(len(self.information.start_dates)):
                    length = EE_Downloader.get_s2_data_from_gge(scene, period)
                    print('\n%d Available Sentinel-2 Images for scene %d of %d' % (
                        length, scene + 1, self.n_scenes))
                    if self.information.n_images == 0:
                        self.n_images = length
                    EE_Downloader.download_s2_data(scene, period)
                    # sleep(1)
                    self.data_extractor(self.information.sen2_images_base_path, ids[scene],
                                         self.information.date_names[period])

                print(
                    f'Downloaded: {self.n_images} S2-Images from scene {scene + 1} of {self.information.n_of_scene} between {self.information.start_dates[period]} and {self.information.end_dates[period]}')

            # --------------------------------------------- SENTINEL-1 ---------------------------------------------
            if "S1" in self.information.satellites:
                for period in range(len(self.information.start_dates)):
                    length = EE_Downloader.get_s1_data_from_gge(scene, period)
                    print('\n%d Available Sentinel-2 Images for scene %d of %d' % (
                        length, scene + 1, self.n_scenes))
                    if self.information.n_of_scene == 0:
                        self.__n_images = length
                    EE_Downloader.download_s1_data(scene, period)
                    # sleep(1)
                    self.data_extractor(self.information.sen1_images_base_path, ids[scene],
                                         self.information.date_names[period])

                print(
                    f'Downloaded: {self.n_images} S1-Images from scene {scene + 1} of {self.information.n_of_scene} between {self.information.start_dates[period]} and {self.information.end_dates[period]}')

        print('   #Download completed')

    def remove_old_images(self):
        """
        Removes existing images in the specified directory and recreates the directory.

        This method checks if the image directory exists, removes it, and then recreates the directory.
        If the directory does not exist, it creates a new one.

        Note: This function is primarily used for cleaning up and preparing the image directory.

        Raises:
        - FileNotFoundError: If the specified image directory is not found.
        - Exception: An exception may be raised if there is an issue during the removal or creation process,
        and it will be printed to the console.
        """
        try:
            if os.path.exists(self.information.image_path):
                shutil.rmtree(self.information.image_path)
            os.makedirs(self.information.image_path)
        except FileNotFoundError:
            print(f"Error: The specified image directory '{self.information.image_path}' was not found.")
        except Exception as e:
            print(f"An error occurred during the process: {e}")
