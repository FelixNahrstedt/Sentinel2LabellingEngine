import math
import pyproj
import utm
from shapely.geometry import Point, Polygon
from math import radians, sin, cos, sqrt, asin, degrees
from pyproj import Transformer
from shapely.ops import transform
from functools import partial
import geopy as gp
import geopy.distance as geoDist
from pyproj import CRS, Transformer
from shapely.geometry import Point
from shapely.ops import transform
# Distances are measured in kilometers
# Longitudes and latitudes are measured in degrees
# Earth is assumed to be perfectly spherical
EARTH_RADIUS  = 6371.0
DEGREES_TO_RADIANS = math.pi/180.0
RADIANS_TO_DEGREE = 180.0/math.pi

def change_in_latitude(kms):
    '''
        Given a distance north, it returns the change in latitude
    '''

    return (kms/EARTH_RADIUS)*RADIANS_TO_DEGREE

def change_in_longitude(latitude, kms):
    '''
        Given a latitude and a distance west, it returns the change in longitude
    '''

    r = EARTH_RADIUS*math.cos(latitude*DEGREES_TO_RADIANS)
    return (kms/r)*RADIANS_TO_DEGREE

def get_coordinates_square(point:Point,distance):
    '''
        Given a latitude and a longitude it returns a square of size=size of coordinates
    '''

    half_size = distance/1000/2

    slat = point.x+change_in_latitude(-half_size)
    nlat = point.x+change_in_latitude(half_size)
    wlon = point.y+change_in_longitude(point.x, -half_size)
    elon = point.y+change_in_longitude(point.x, half_size)
    coordinates_geojson = [
            [wlon,slat], [wlon,nlat], [elon,nlat], [elon,slat]
        ] #[wlon,slat] [wlon,nlat], [elon,nlat], [elon,slat]

        # [Northeastern Longitude, Southeastern Latitude, Southwestern Longitude, Northwestern Latitude]
        # [poly[0][1], poly[2][0],poly[1][1], poly[1][0]]
    bounding_box = [wlon,slat,elon,nlat]
    return coordinates_geojson, bounding_box


# def point_to_buffer_3(point:Point,distance):
#         """
#         Given a latitude and a longitude, return a square of size `image_size_in_m` of coordinates.

#         Parameters:
#         - latitude: Latitude of the center point.
#         - longitude: Longitude of the center point.
#         - image_size_in_m: Size of the square in meters.

#         Returns:
#         A list containing coordinates in GeoJSON format and a list of bounding box coordinates.
#         """
#         half_size = distance / 2
#         easting, northing, zone_number, zone_letter = utm.from_latlon(point.x, point.y)
#         slat = utm.to_latlon(easting - half_size, northing - half_size, zone_number, zone_letter)
#         wlon = utm.to_latlon(easting - half_size, northing + half_size, zone_number, zone_letter)
#         nlat = utm.to_latlon(easting + half_size, northing + half_size, zone_number, zone_letter)
#         elon = utm.to_latlon(easting + half_size, northing - half_size, zone_number, zone_letter)

#         coordinates_geojson = [
#             [wlon[1], nlat[0]], [elon[1], nlat[0]],
#             [elon[1], slat[0]], [wlon[1], slat[0]]
#         ]

#         # [Northeastern Longitude, Southeastern Latitude, Southwestern Longitude, Northwestern Latitude]
#         # [poly[0][1], poly[2][0],poly[1][1], poly[1][0]]
#         bounding_box = [wlon[1], slat[0], elon[1], nlat[0]]

#         # coordinates_geojson_buffers = [
#         #     [nlat[0], wlon[1]], [nlat[0], elon[1]],
#         #     [slat[0], elon[1]], [slat[0], wlon[1]]
#         # ]
#         print(bounding_box)
#         print("\nNew:")
#         print(point_to_buffer(point,distance)[1])

#         return coordinates_geojson, bounding_box

# def point_to_buffer(point:Point, buffer):
#     half_size = (buffer/2) #for a radius in kilometers
#     # wgs84 = Proj(init='epsg:4326')
#     # crs3857 = Proj(init='epsg:3857')
#     # transformer_front = Transformer.from_crs('epsg:3857', 'epsg:4326',always_xy=True)
#     # lon,lat  = transformer_front.transform(point.y, point.x)
#     lat = point.x
#     lon = point.y
#     slat = lat+change_in_latitude(-half_size)
#     nlat = lat+change_in_latitude(half_size)
#     wlon = lon+change_in_longitude(lat, -half_size)
#     elon = lon+change_in_longitude(lat, half_size)  

#     #transformer_back = Transformer.from_crs('epsg:4326','epsg:3857',always_xy=True)
#     # lat_a,lon_a  = transformer_back.transform(wlon,nlat) # wlon,nlat nlat,wlon
#     # lat_b,lon_b  = transformer_back.transform(elon,nlat) # elon,nlat nlat,elon
#     # lat_c,lon_c  = transformer_back.transform(elon,slat) # elon,slat slat,elon
#     # lat_d,lon_d  = transformer_back.transform(wlon,slat ) # wlon,slat slat,wlon

#     coordinates_geojson = [
#             [wlon, nlat], [elon, nlat],
#             [elon, slat], [wlon, slat]
#         ]

#     # [Northeastern Longitude, Southeastern Latitude, Southwestern Longitude, Northwestern Latitude]
#     # [poly[0][1], poly[2][0],poly[1][1], poly[1][0]]
#     bounding_box = [wlon, slat, elon, nlat]
#     print(bounding_box)
#     #print(point_to_buffer_2(point,buffer)[1])

#     return coordinates_geojson, bounding_box

# def change_in_latitude(distance_north):
#     '''
#         Given a distance north, it returns the change in latitude
#     '''
#     RADIANS_TO_DEGREE = 180.0/math.pi
#     EARTH_RADIUS = 6371000.0

#     return (distance_north/EARTH_RADIUS)*RADIANS_TO_DEGREE

# def change_in_longitude(latitude, distance_west):
#     """
#     Calculate the change in longitude in degrees given a distance west (positive/negative) in meters and a latitude.
#     Uses the Haversine formula.
#     """
#     # Earth radius in meters
#     EARTH_RADIUS = 6371000.0
#     DEGREES_TO_RADIANS = math.pi/180.0
#     RADIANS_TO_DEGREE = 180.0/math.pi
#     r = EARTH_RADIUS*math.cos(latitude*DEGREES_TO_RADIANS)
#     return (distance_west/r)*RADIANS_TO_DEGREE

# def point_to_buffer_2(point_origin:Point, buffer):
#     top_right, bottom_right, Bottom_left,
#     print("correct buffer:")
#     N,W,S,E = buffer_in_meters(point_origin,buffer)
#     N,E,
#     S,E,N,W = geodesic_point_buffer(point_origin.y,point_origin.x,buffer/2)[:4]
#     print(S,E,N,W)
#     half_size = (buffer/2) #for a radius in kilometers

#     lon = point_origin.x
#     lat = point_origin.y
    
#     d = geoDist.distance(meters = half_size)
#     point = gp.Point(lat,lon)

#     north = d.destination(point, bearing=0)

#     east = d.destination(point, bearing=90)
#     south = d.destination(point, bearing=180)
#     west = d.destination(point, bearing=270)

    
#     coordinates_geojson = [
#             [north.latitude, east.longitude], [south.latitude, east.longitude],
#             [south.latitude, west.longitude], [north.latitude, west.longitude]
#         ]
#     coordinates_geojson_new = [
#             [N[1], E[0]], [S[1], E[0]],
#             [S[1], W[0]], [N[1], W[0]]
#         ]
#     print(coordinates_geojson)
#     print("\n",lon,lat)
#     print((north.latitude,north.longitude),(east.latitude,east.longitude))
#     print((south.latitude,south.longitude),(west.latitude,west.longitude))
       
#     print(geoDist.geodesic((east.latitude, east.longitude),(west.latitude, west.longitude)).km,
#          geoDist.geodesic((north.latitude, north.longitude),(south.latitude, south.longitude)).km)
#     bounding_box = [north.latitude,west.longitude, south.latitude,east.longitude]
#     bounding_box_new = [N[1],W[0],S[1],E[0]]
#     print(bounding_box_new)
    
#     print(bounding_box)
#     a,b = get_coordinates_square(point_origin,buffer)
#     print(bounding_box)
#     return a,b

# def buffer_in_meters(point: Point, buffer):
#     #print(point.y,point.x)
#     """
#     Returns the geometry of a circle or square around a point with a given radius/length in meters.
#     """ 
#     half_size = buffer/2
#     # pyproj 2 style for defining projections
#     local_azimuthal_projection = f"+proj=aeqd +R=6371000 +units=m +lat_0={point.y} +lon_0={point.x}"
#     transformer_wgs84_to_aeqd = Transformer.from_crs("EPSG:4326", local_azimuthal_projection,always_xy=True)
#     transformer_aeqd_to_wgs84 = Transformer.from_crs(local_azimuthal_projection, "EPSG:4326",always_xy=True)

#     # Transform point to local azimuthal projection
#     point_transformed = transformer_wgs84_to_aeqd.transform(point.y, point.x)

#     # Buffer the transformed point (square)
#     slat = (point_transformed[0] - half_size, point_transformed[1] - half_size)
#     wlon = (point_transformed[0]  - half_size, point_transformed[1] + half_size)
#     nlat = (point_transformed[0]  + half_size, point_transformed[1] + half_size)
#     elon = (point_transformed[0]  + half_size, point_transformed[1]  - half_size)

#     newP_S = transformer_aeqd_to_wgs84.transform(slat[0],slat[1])
#     newP_E = transformer_aeqd_to_wgs84.transform(wlon[0],wlon[1])
#     newP_N = transformer_aeqd_to_wgs84.transform(nlat[0],nlat[1])
#     newP_W = transformer_aeqd_to_wgs84.transform(elon[0],elon[1])
#     #print(newP_S,newP_W,newP_N,newP_E)
#     list_p = [(newP_S[1],newP_S[0]),(newP_W[1],newP_W[0]),(newP_N[1],newP_N[0]),(newP_E[1],newP_E[0])]
#     #buffer = Point(point_transformed).buffer(buffer, cap_style="square")
    
#     # Get the exterior ring
#     #exterior_ring = buffer.exterior

#     # Get the coordinates of the exterior ring
#     #points = list(exterior_ring.coords)

#     # north, w, S,E
#     # list_p = []
#     # for p in points: 
#     #     newP = transformer_aeqd_to_wgs84.transform(p[0], p[1])
#     #     list_p.append((newP[1],newP[0]))
#     return list_p

# def geodesic_point_buffer(lat, lon, m):
#     # Azimuthal equidistant projection
#     aeqd_proj = CRS.from_proj4(
#         f"+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0")
#     tfmr = Transformer.from_proj(aeqd_proj, aeqd_proj.geodetic_crs)
#     buf = Point(0, 0).buffer(m,cap_style="square")  # distance in metres
#     return transform(tfmr.transform, buf).exterior.coords[:]