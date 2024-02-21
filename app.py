import geopandas as gpd
from shapely.geometry import Point, Polygon, LineString
import pandas as pd
import fiona
fiona.drvsupport.supported_drivers['libkml'] = 'rw'
import numpy as np
import geopy
from geopy import distance
import datetime
# from datetime import datetime
import time
from math import radians, degrees, cos, sin, asin, sqrt, atan2
from statistics import mean 
from shapely import wkt
import math
from flask import Flask, request, jsonify, session,current_app
from flask_cors import CORS
import io
from io import BytesIO
from io import StringIO
import json
from geopy.distance import distance
import zipfile
import shutil
import os
import xml.etree.ElementTree as ET
import requests
app = Flask(__name__)
CORS(app, origins='*')
AIStime=None
gdf=None
@app.route('/images', methods=['POST'])
def images():
    # output_dir=r"C:\Users\Training\Desktop\dead_ship\DEAD_SHIP"
    output_dir = current_app.root_path+'/my-app'
    os.makedirs(output_dir, exist_ok=True)
    file=request.data
    # print(file)
    with zipfile.ZipFile(BytesIO(file), 'r') as kmz:
        kmz.extractall(output_dir)
    
    # Find KML files
    kml_files = [filename for filename in kmz.namelist() if filename.endswith('.kml')]
    
    for kml_file in kml_files:
        kml_path = os.path.join(output_dir, kml_file)
        tree = ET.parse(kml_path)
        root = tree.getroot()
        
        # Extract image URLs from KML
        image_urls = []
        for elem in root.iter():
            if elem.tag.endswith('Icon') or elem.tag.endswith('GroundOverlay'):
                for child in elem:
                    if child.tag.endswith('href'):
                        image_urls.append(child.text)
        
        # Download and save images
        for url in image_urls:
            image_filename = os.path.basename(url)
            image_path = os.path.join(output_dir, image_filename)
            with open(image_path, 'wb') as f:
                response = requests.get(url)
                f.write(response.content)
                print(f"Downloaded: {image_filename}")

    return "images extraction Failed"


@app.route('/process_xml', methods=['POST'])
def process_xml():
    global AIStime,gdf
    xml_data = request.data
    req_data=xml_data
    req_data=BytesIO(req_data)
    fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
    with fiona.open(req_data) as collection:
        gdf = gpd.GeoDataFrame.from_features(collection)
    # remove empty Time Stamp data
    gdf = gdf.drop(gdf[gdf.Time_Stamp.isnull()].index)
    # Convert to datetime format
    gdf.Time_Stamp = pd.to_datetime(gdf.Time_Stamp.str.split(',').str[0].str.strip('{') +","+ gdf.Time_Stamp.str.split(',').str[1].str[:15], format='%d-%m-%Y,%H:%M:%S.%f')
    # Convert to Unix time
    gdf.Time_Stamp = (gdf.Time_Stamp - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
    # Get mean Value
    r_time = round(gdf.Time_Stamp.mean())
    # Convert Back to date time format
    average_timestamp = pd.to_datetime(r_time, unit='s')
    #change UTM to IST, Differernce is 5:30 hours
    time_change = datetime.timedelta(hours=5,minutes=30)
    AIStime = average_timestamp + time_change
    AIStime_type=str(AIStime)
    return jsonify({'timestamp_type': AIStime_type})
@app.route('/process_csv', methods=['POST'])
def process_csv():
    global AIStime,gdf
    if request.method == 'POST':
        print(request.data)
        # data=io.BytesIO(request.data)
        # data=pd.read_csv(data)
        # print(data)
        # data = json.loads(request.data)
        # print(data)
        # csv_data=json.loads(data["csvData"])
        # print(csv_data)
        # print(csv_data)
        # csv_io = io.BytesIO(csv_data)
        # csv_df = pd.read_csv(csv_io)
        # xml_data=request.files.get('xmldata')
        # print(xml_data)
        # print(csv_df)
        # output_folder=r"C:\Users\Training\Desktop\output"
        # pair_line_out = output_folder + "\\" +"pair_line.shp"
        # single_line_out = output_folder + "\\" +"single_line.shp"
        # int_point_pair_out = output_folder + "\\" +"int_point_pair.shp"
        # int_point_single_out = output_folder + "\\" + "int_point_single.shp"
        # buffer_poly_out = output_folder + "\\" +  "buffer_poly.shp"
        # csv_io = io.BytesIO(csv_data)
        # csv_df = pd.read_csv(csv_io)
        # # print(csv_df)
        # pairs = csv_df[csv_df.duplicated(subset='ID_IMO',keep=False)]
        # print(pairs)
        # non_pairs = csv_df[~csv_df.duplicated(subset='ID_IMO',keep=False)]
        # pairs.TIMESTAMP_SOURCE = pd.to_datetime(pairs.TIMESTAMP_SOURCE, format= "%d-%m-%Y %H:%M")
        # grp = pairs.groupby('ID_IMO')
        # imo = []
        # geometry=[]
        # geometry_line=[]
        # for i in grp.ID_IMO:
        #     a,b = grp.get_group(i[0]).index[:2]
        #     t1 = pairs._get_value(a,'TIMESTAMP_SOURCE')
        #     t2 = pairs._get_value(b,'TIMESTAMP_SOURCE')
        #     if t1 < t2:
        #         lat_start,long_start = pairs._get_value(a,'KINEMATIC_POS_LLA_LAT'), pairs._get_value(a,'KINEMATIC_POS_LLA_LON')
        #         lat_end,long_end = pairs._get_value(b,'KINEMATIC_POS_LLA_LAT'), pairs._get_value(b,'KINEMATIC_POS_LLA_LON')
        #         ratio = (AIStime -t1)/(t2-t1)
                
        #     elif t1 == t2:
        #         ratio = 0
        #     else:
        #         lat_start,long_start = pairs._get_value(b,'KINEMATIC_POS_LLA_LAT'), pairs._get_value(b,'KINEMATIC_POS_LLA_LON')
        #         lat_end,long_end = pairs._get_value(a,'KINEMATIC_POS_LLA_LAT'), pairs._get_value(a,'KINEMATIC_POS_LLA_LON')
        #         ratio = (AIStime -t2)/(t1-t2)
                

        #     d, b = haversine(long_start,lat_start,long_end,lat_end)
        #     d = d*ratio

        #     new = new_pt(lat_start,long_start, d,b)
        #     imo.append(i[0])
        #     geometry.append(Point(new.longitude, new.latitude))
        #     geometry_line.append(LineString([(long_start, lat_start),(long_end, lat_end)]))
            
            

        # int_points_pair = gpd.GeoDataFrame(columns= ['IMO','geometry'],crs='EPSG:4326')
        # int_points_pair.geometry = geometry
        # int_points_pair.IMO = imo

        # pair_line = gpd.GeoDataFrame(columns= ['IMO','geometry'],crs='EPSG:4326')
        # pair_line.geometry = geometry_line
        # pair_line.IMO = imo
        # #Exporting to shapefile
        # int_points_pair.to_file(int_point_pair_out, driver='ESRI Shapefile')
        # pair_line.to_file(pair_line_out, driver='ESRI Shapefile')
        # non_pairs = non_pairs.dropna(subset= ['ID_IMO','KINEMATIC_POS_LLA_LAT','KINEMATIC_POS_LLA_LON','KINEMATIC_SPEED','KINEMATIC_HEADING_TRUE'])
        # non_pairs.TIMESTAMP_SOURCE = pd.to_datetime(non_pairs.TIMESTAMP_SOURCE, format= "%d-%m-%Y %H:%M")
        # geometry = []
        # line_geometry = []
        # imo = []
        # for i in non_pairs.ID_IMO:
        #     index = non_pairs[non_pairs['ID_IMO']==i].index[0]
        #     t = non_pairs._get_value(index, 'TIMESTAMP_SOURCE')
            
            
        #     if t < AIStime:
        #         delta_time = AIStime - t
        #         delta_time = delta_time.total_seconds()/3600
        #         lat_start = non_pairs._get_value(index,'KINEMATIC_POS_LLA_LAT')
        #         long_start = non_pairs._get_value(index,'KINEMATIC_POS_LLA_LON')
        #         heading = non_pairs._get_value(index,'KINEMATIC_HEADING_TRUE')
                
        #     else:
        #         delta_time = t - AIStime
        #         delta_time = delta_time.total_seconds()/3600
        #         lat_start = non_pairs._get_value(index,'KINEMATIC_POS_LLA_LON')
        #         long_start = non_pairs._get_value(index,'KINEMATIC_POS_LLA_LAT')
        #         heading = abs(non_pairs._get_value(index,'KINEMATIC_HEADING_TRUE') - 180)
                

        #     heading = non_pairs._get_value(index,'KINEMATIC_HEADING_TRUE')
        #     speed_km = non_pairs._get_value(index,'KINEMATIC_SPEED') * 1.852
        #     distance = delta_time*speed_km

        #     int_pt = new_pt(lat_start,long_start,distance,heading) 
        #     geometry.append(Point(int_pt.longitude, int_pt.latitude))
        #     line_geometry.append(LineString([(long_start, lat_start),(int_pt.longitude, int_pt.latitude)]))
        #     imo.append(i)
            
        # int_points_single = gpd.GeoDataFrame(columns= ['IMO','geometry'],crs='EPSG:4326')
        # int_points_single.geometry = geometry
        # int_points_single.IMO = imo

        # single_line = gpd.GeoDataFrame(columns= ['IMO','geometry'],crs='EPSG:4326')
        # single_line.geometry = line_geometry
        # single_line.IMO = imo
        # #Exporting to shapefile
        # int_points_single.to_file(int_point_single_out, driver='ESRI Shapefile')
        # single_line.to_file(single_line_out, driver='ESRI Shapefile')
        # deg = meters_to_degrees(5000, 13.5)
        # buffer_geom = int_points_pair.buffer(deg)

        # buffer_geom.to_file(buffer_poly_out, driver="ESRI Shapefile")
        # buffer_geom = int_points_single.buffer(deg)

        # with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        #         for filename in [pair_line_out, single_line_out, int_point_pair_out, int_point_single_out, buffer_poly_out]:
        #             zipf.write(filename, os.path.basename(filename))

        # # Send the zip file to the client
        # return send_file(zip_file_path, as_attachment=True)
        return "Success"
    return jsonify({'error': 'Method not allowed'}), 405
# to get distance and angle between two points.
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.

    # Bearing
    x = sin(dlon)*cos(lat2)
    y = (cos(lat1)*sin(lat2) - (sin(lat1)*cos(lat2)*cos(dlat)))

    bearing = atan2(x,y)
    bearing = degrees(bearing)
    distance = c*r

    return distance , bearing
# To get Interpolated POint
def new_pt(start_lat,start_long, distance_km,bearing_deg):
    new_pt = geopy.distance.distance(kilometers=distance_km).destination((start_lat,start_long), bearing=bearing_deg)
    return new_pt
def meters_to_degrees(meters, latitude):
    # Radius of the Earth at the given latitude
    earth_radius_at_latitude = 6378137.0 / math.sqrt(1 - 0.00669438 * math.sin(math.radians(latitude))**2)

    # Conversion factor from meters to degrees
    meters_to_degrees_conversion = 1 / (earth_radius_at_latitude * math.pi / 180)

    # Convert distance to degrees
    degrees = meters * meters_to_degrees_conversion
    return degrees
if __name__ == '__main__':
    app.run(debug=True)