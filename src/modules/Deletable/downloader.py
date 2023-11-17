from zipfile import ZipFile
from time import sleep
from glob import glob
import shutil
import Earth_Engine as gee
import os
from zipfile import ZipFile


def find(directory):
    '''
        It returns the paths of files contained in a directory
    '''

    names = []

    for folder in glob(directory):
        names.append(folder)

    # It removes unnecessary file from the names list
    for i in range(len(names)):
        if names[i].endswith('ini'):
            names.pop(i)
            break

    return names

def get_ids(points):
    '''
        It creates a symbolic name for a downloaded file using the longitude and latitude values
    '''

    lat = points[0,:]
    lon = points[1,:]
    ids = []
    for i in range(len(lat)):
        ids.append('lat_'+str(lat[i])+'_lon_'+str(lon[i]))

    return ids


def data_extractor(path, zone_name, date, downloads_folder_path, windows):
    names = find(downloads_folder_path)

    for i in range(len(names)):
        if not ('.zip' in names[i]):
            shutil.rmtree(names[i])

    names = find(downloads_folder_path)

    # It tries to extract all the downloaded image into a folder
    for i in range(len(names)):
        if windows == True:
            f = names[i].split('.')[0].split('\\')
            fn = f[len(f)-1]
            #pos = path+zone_name+'\\'+date+'\\'+fn
            pos = os.path.join(path+zone_name, os.path.join(date, fn))
        else:
            f = names[i].split('.')[0].split('/')
            fn = f[len(f)-1]
            #pos = path+zone_name+'/'+date+'/'+fn
            pos = os.path.join(path+zone_name, os.path.join(date, fn))

        os.makedirs(pos, exist_ok=True)
        try:
            with ZipFile(names[i], 'r') as ZipObj:
                ZipObj.extractall(pos)
                print('               + Extracting file %d of %d' % (i+1, len(names)))
        except Exception:
            print('               !!! Extraction exception !!!')
            pass
    # After the extraction it removes all the zip files
    for i in range(len(names)):
        os.remove(names[i])

def download(satellites,points, patch_size, start_date, end_date, date_names, s2_selectors, s1_selectors, n_of_scenes, n_imgs, downloads_folder_path, download_path, sen2_images_base_path, sen1_images_base_path, windows):
    
    # make a get_ids
    regions, rectangles = gee.get_region_and_rectangle(points[0,:], points[1,:],image_size_m=patch_size)

    ids = get_ids(points)
    if n_of_scenes == 0:
        n_of_scenes = len(regions)

    for scene in range(0, n_of_scenes):
        #--------------------------------------------- SENTINEL-2 ---------------------------------------------
        if("S2" in satellites):
            print('   # Sentinel-2 data downloading')
            print('     > Sentinel-2 region %d of %d download started' % (scene+1, n_of_scenes))
            
            for period in range(len(start_date)):
                s2data, length = gee.get_s2_data_from_gge(rectangles[scene], start_date[period], end_date[period])
                if n_imgs == 0:
                    n_imgs = length
                gee.download_s2_data(s2data, regions[scene], ids[scene], date_names[period], download_path, n_imgs=n_imgs, selectors=s2_selectors)
                #sleep(1)
                data_extractor(sen2_images_base_path, ids[scene], date_names[period], downloads_folder_path, windows = windows)

            print('     > Sentinel-2 region %d of %d download completed' % (scene+1, n_of_scenes))

        #--------------------------------------------- SENTINEL-1 ---------------------------------------------
        if("S1" in satellites):
            print('   # Sentinel-1 data downloading')
            print('     > Sentinel-1 region %d of %d download started' % (scene+1, n_of_scenes))
            for period in range(len(start_date)):
                s1data, length = gee.get_s1_data_from_gge(rectangles[scene], start_date[period], end_date[period])
                if n_imgs == 0:
                    n_imgs = length
                gee.download_s1_data(s1data, regions[scene], ids[scene], date_names[period], download_path, n_imgs=n_imgs, selectors=s1_selectors)
                #sleep(1)
                data_extractor(sen1_images_base_path, ids[scene], date_names[period], downloads_folder_path, windows = windows)
                #sleep(3)

            print('     > Sentinel-1 region %d of %d download completed' % (scene+1, n_of_scenes))


    print('   #Download completed')