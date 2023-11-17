import os
import shutil
import time
import rasterio
import numpy as np
import matplotlib.pyplot as plt

class Sentinel2Converter:
    def __init__(self):
        pass

    def to_png(self, path_tif: str, bands: list[str], image_dir: str, remove=False):
        """
        Visualize Sentinel-2 RGB images and save them as PNG files.

        Parameters:
        - path_tif (str): Path to the directory containing Sentinel-2 TIFF files.
        - bands (list[str]): List of band names (e.g., ['B4', 'B3', 'B2'] for red, green, and blue).
        - image_dir (str): Directory to save the generated RGB images.
        - remove (bool): If True, remove existing images in image_dir before processing.

        Returns:
        None
        """
        if remove:
            self._remove_existing_images(image_dir)

        tiff_files = self._identify_tiff_files(path_tif, image_dir)

        for file in tiff_files:
            files = [rasterio.open(f'{file[0]}.{band}.tif') for band in bands]
            red, green, blue = self._normalize_bands(files)
            rgb_image = np.stack((red, green, blue), axis=-1)

            self._display_and_save_image(rgb_image, file[1])

    def to_geoTiff(self, path_tif: str, bands: list[str], image_dir: str, remove=False):
        """
        Visualize Sentinel-2 RGB images and save them as PNG files.

        Parameters:
        - path_tif (str): Path to the directory containing Sentinel-2 TIFF files.
        - bands (list[str]): List of band names (e.g., ['B4', 'B3', 'B2'] for red, green, and blue).
        - image_dir (str): Directory to save the generated RGB images.
        - remove (bool): If True, remove existing images in image_dir before processing.

        Returns:
        None
        """
        if remove:
            self._remove_existing_images(image_dir)

        tiff_files = self._identify_tiff_files(path_tif, image_dir)

        for file in tiff_files:
            #loaded = [rasterio.open(f'{file[0]}.{band}.tif') for band in bands]

            files = [f'{file[0]}.{band}.tif' for band in bands]
            with rasterio.open(files[0]) as src0:
                meta = src0.meta
            # Update meta to reflect the number of layers
            meta.update(count = len(files))
            # Read each layer and write it to stack
            with rasterio.open(str(file[1][:-4]+".tif"), 'w', **meta) as dst:
                for id, layer in enumerate(files, start=1):
                    with rasterio.open(layer) as src1:
                        dst.write_band(id, src1.read(1))


    def _remove_existing_images(self, image_dir):
        """
        Removes existing images in the specified directory.

        Parameters:
        - image_dir (str): The directory path containing images to be removed.
        """
        shutil.rmtree(image_dir)
        time.sleep(1)
        os.makedirs(image_dir)

    def _identify_tiff_files(self, path_tif, image_dir):
        """
        Identifies TIFF files in the specified directory and returns a list of file pairs.

        Parameters:
        - path_tif (str): The directory path containing TIFF files.
        - image_dir (str): The directory path where corresponding PNG files will be stored.

        Returns:
        - tiff_files (list): A list of file pairs where each pair consists of the TIFF file path and the corresponding PNG file path.
        """
        tiff_files = []

        for root, dirs, files in os.walk(path_tif):
            for file in files:
                if file.lower().endswith(".tif") or file.lower().endswith(".tiff"):
                    relative_path = os.path.relpath(root, path_tif).replace("\\", "/")
                    file_split = file.split(".")
                    new_entry = [f"{path_tif}{relative_path}/{file_split[0]}", f"{image_dir}{relative_path}/{file_split[0]}.png"]
                    if new_entry not in tiff_files:
                        tiff_files.append(new_entry)
                        os.makedirs(f"{image_dir}{relative_path}", exist_ok=True)

        return tiff_files

    def _normalize_bands(self, files):
        """
        Normalizes bands in a list of files and returns the normalized data.

        Parameters:
        - files (list): A list of file objects representing image bands.

        Returns:
        - normalized_data (list): A list of normalized image bands.
        """
        normalize = lambda band: (band.read(1) * (255 / np.max(band.read(1)))).astype(np.uint8)
        return map(normalize, files)

    def _display_and_save_image(self, rgb_image, file_path):
        """
        Displays and saves an RGB image.

        Parameters:
        - rgb_image: The RGB image to be displayed and saved.
        - file_path (str): The file path to save the image.
        """
        plt.figure(figsize=(10, 10))
        plt.imshow(rgb_image)
        plt.savefig(file_path)
        plt.close('all')

# Example usage:
# visualizer = Sentinel2Visualizer()
# visualizer.visualize_rgb_images(path_tif='your_path', bands=['B4', 'B3', 'B2'], image_dir='your_output_dir', remove=True)
