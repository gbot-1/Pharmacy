"""TO DO"""
"""
Include list of housing

CLEAN EVERYTHING
"""
##########################################################################################
import time
start_time_overall = time.time()

import geopandas as gpd
import os
import datetime
from Read_excel import* 
from input_function import*
from distance_function import*
from Create_tex_pdf import*
from Map_function import*
from save_fig import*
from polygon_drawing import*

ADRESS_CSV = 'D:/Pharmacy_Raph/adresses.csv'
CADASTRAL_MAP = 'D:/Pharmacy_Raph/QGIS/Cadastre/Bpn_CaPa_WAL.shp'
FILEPATH = 'D:/Pharmacy_Raph/Lst_Pharmacies_pub_Extended.xlsx'
MAIN_FOLDER = "D:/Pharmacy_Raph"
TEMPLATE_PATH = 'D:/Pharmacy_Raph/Codes/template_rapport_'

API_KEY = '5b3ce3597851110001cf6248cca3afa1547a460ab12d2624d73dbe4e'
EXCEL_HOUSES = 'adresses_in_polygon.csv'
FOLDER_NAME_TEX = 'Tex_files'
HABITANTS_TEX = 'table_habitants_per_street.tex'
HTML_ALL_PHARMACY_NEW = 'all_itineraries_new.html'
HTML_ALL_PHARMACY_OLD = 'all_itineraries_old.html'
HTML_NEW_PHARMACY = 'itinerary_new_pharmacy.html'
MAP_ALL_PHARMACY_NEW = 'map_all_pharmacy_new.png'
MAP_ALL_PHARMACY_OLD = 'map_all_pharmacy_old.png'
MAP_NEW_PHARMACY = 'map_new_implentation.pdf'
NB_POINT = 10
POLYGON_25_PERCENT = 'polygon_25_percent'
POLYGON_25_PERCENT_EPS = 'protection_zone_25_percent.pdf'
POLYGON_50_PERCENT = 'polygon_50_percent'
POLYGON_50_PERCENT_EPS = 'protection_zone_50_percent.pdf'
POLYGON_CONSTRUCTION = 'polygon_25_percent_construction.pdf'
POLYGON_CONSTRUCTION_ZOOM = 'polygon_25_percent_construction_zoom.pdf'
YEAR = str(datetime.datetime.now().year)

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def point_to_list(point_coord):
    temp_gdf = gpd.GeoDataFrame([1], geometry=[point_coord], crs="EPSG:3812")
    temp_gdf = temp_gdf.to_crs("EPSG:4326")
    gdf_coord = temp_gdf.geometry.iloc[0]
    list_coord = (gdf_coord.x, gdf_coord.y)
    return list_coord

##########################################################################################
# Load data
df = load_db_from_excel(FILEPATH)
gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.X, df.Y))

report_type, is_temp = project_type()
TEMPLATE_PATH = TEMPLATE_PATH + str(report_type) + '.tex'

# Get input data
coord_init, id_number = get_coord_by_pharma_id(gdf)
if report_type == 3:
    print("\nPharmacie réceptrice")
    new_coordinates, id_number = get_coord_by_pharma_id(gdf)
    New_adresse, name_pharma = get_info_by_pharma_id(id_number, gdf)
else:
    new_coordinates = coordinate_new_implantation()
    New_adresse = adress_new_implantation()
    name_pharma = ""
ref_plan = date_and_ref()

closest_points_old = selection_pharmacies(gdf, coord_init, NB_POINT, new_coordinates)
closest_points_old = closest_points_old.to_crs("EPSG:4326") #convert to WGS 84 - needed for road distance

#small manipulation to have the new coordinates into the appropriate format
temp_gdf = gpd.GeoDataFrame([1], geometry=[new_coordinates], crs="EPSG:3812").geometry.iloc[0]
x_y_new_implentation = (temp_gdf.x, temp_gdf.y)

# Calculate closest points
closest_points_old, routes_geometry_old = road_distance(closest_points_old, coord_init, API_KEY)
closest_points_old = closest_points_old.sort_values(by='road_distance')
closest_points_old = closest_points_old.reset_index(drop=True)

# Create folders
folder_name = ref_plan[1] + "_" + str(closest_points_old.iloc[0]['Nom'])
folder_name = folder_name.replace(" ", "_").replace("/", "_")  # Replace spaces and slashes
folder_path = os.path.join(MAIN_FOLDER, YEAR, folder_name)
create_folder(folder_path)
    
closest_points_old.to_csv(os.path.join(folder_path, 'distance_closest_points_old.csv'))
gdf_routes_geometry_old = save_routes_to_shapefile(routes_geometry_old, folder_path + '/routes_old')

"""Create CSV for new implentation"""
gdf_temp = create_gdf_new_implentation(closest_points_old, New_adresse, new_coordinates, name_pharma)
closest_points_new = get_planar_distance(gdf_temp, new_coordinates, NB_POINT)
closest_points_new = closest_points_new.to_crs("EPSG:4326")
closest_points_new, routes_geometry_new = road_distance(closest_points_new, new_coordinates, API_KEY)
# Sorting the second dataframe using this mapping
order_mapping = {auth_num: idx for idx, auth_num in enumerate(closest_points_old["Numéro d'autorisation"])}
closest_points_new = closest_points_new.copy()
closest_points_new['sort_key'] = closest_points_new["Numéro d'autorisation"].map(order_mapping)
closest_points_new = closest_points_new.sort_values('sort_key').drop('sort_key', axis=1)

closest_points_new.to_csv(os.path.join(folder_path, 'distance_closest_points_new.csv'))
gdf_routes_geometry_new = save_routes_to_shapefile(routes_geometry_new, folder_path + '/routes_new')

cache = {}
distance_old_new = distance_fly_old_new_implantation(coord_init, new_coordinates)
distance_old_new_road = get_road_distance_and_geometry(point_to_list(coord_init), point_to_list(new_coordinates), API_KEY, cache)[0]
if distance_old_new_road <= 100:
    near_transfert = True
else:
    near_transfert = False

############################################################################################
polygon_midistance_shp = os.path.join(MAIN_FOLDER, YEAR, folder_name, POLYGON_50_PERCENT)
polygon_quarter_distance_shp = os.path.join(MAIN_FOLDER, YEAR, folder_name, POLYGON_25_PERCENT)

protection_zone_midistance = polygon_mid_distance(closest_points_new, polygon_midistance_shp, CADASTRAL_MAP)
adresse_polygon = os.path.join(MAIN_FOLDER, YEAR, folder_name, EXCEL_HOUSES)

find_points_in_polygon(ADRESS_CSV, protection_zone_midistance, adresse_polygon)

# intersections, perpendicular_lines = find_perpendicular_intersections_ordered(gdf)
protection_zone_quarter_distance, polygon_construction_elements = create_polygon_from_intersections(closest_points_old, polygon_quarter_distance_shp)
is_in_polygon = protection_zone_quarter_distance.contains(new_coordinates)

##########################################################################################
html_path = os.path.join(MAIN_FOLDER, YEAR, folder_name, HTML_NEW_PHARMACY)
create_folder(os.path.join(MAIN_FOLDER, YEAR, folder_name, FOLDER_NAME_TEX))
new_implentation_pdf = os.path.join(MAIN_FOLDER, YEAR, folder_name, FOLDER_NAME_TEX, MAP_NEW_PHARMACY)
all_itinerary_old_pdf = os.path.join(MAIN_FOLDER, YEAR, folder_name, FOLDER_NAME_TEX, POLYGON_50_PERCENT_EPS)
polygon_construction_pdf = os.path.join(MAIN_FOLDER, YEAR, folder_name, FOLDER_NAME_TEX, POLYGON_CONSTRUCTION)
polygon_construction_pdf_zoom = os.path.join(MAIN_FOLDER, YEAR, folder_name, FOLDER_NAME_TEX, POLYGON_CONSTRUCTION_ZOOM)
all_itinerary_new_pdf = os.path.join(MAIN_FOLDER, YEAR, folder_name, FOLDER_NAME_TEX, POLYGON_25_PERCENT_EPS)
start_coords = point_to_list(coord_init)
end_coords = point_to_list(new_coordinates)

# Get the route geometry
route_geometry = get_route(start_coords, end_coords, API_KEY)

if report_type == 1:
    if near_transfert:
        bool_polygon_midistance = False
        bool_polygon_quarter = False
        bool_near_transfert = True
    elif is_in_polygon:
        bool_polygon_midistance = False
        bool_polygon_quarter = True
        bool_near_transfert = True
    else:
        bool_polygon_midistance = True
        bool_polygon_quarter =  False
        bool_near_transfert = False
elif report_type == 2:
    bool_polygon_midistance = False
    bool_polygon_quarter = False
elif report_type == 3:
    if closest_points_old.iloc[1]['distance'] < 1000:
        bool_polygon_midistance = False
        bool_polygon_quarter = False
    else:
        bool_polygon_midistance = True
        bool_polygon_quarter =  False

itinerary_cadastral_background(route_geometry, CADASTRAL_MAP, new_implentation_pdf)
polygon_50_map(CADASTRAL_MAP, polygon_midistance_shp+'_fitted.shp', polygon_midistance_shp+'.shp', adresse_polygon, 
               all_itinerary_old_pdf, new_coordinates, gdf_routes_geometry_new, closest_points_new, bool_polygon_midistance)
polygon_25_map(CADASTRAL_MAP, polygon_quarter_distance_shp+'.shp', polygon_construction_pdf, closest_points_old, 
               coord_init, new_coordinates, polygon_construction_elements)
polygon_25_map_zoom(CADASTRAL_MAP, polygon_quarter_distance_shp+'.shp', polygon_construction_pdf_zoom, closest_points_old, 
               coord_init, new_coordinates, polygon_construction_elements)
itinerary_old_pharma(CADASTRAL_MAP, all_itinerary_new_pdf, closest_points_old, coord_init, gdf_routes_geometry_old)

#########################################################################################
"""Creates the .tex files"""
if closest_points_old.iloc[1,9] > 1000:
    bool_nearest_1000 = False
else:
    bool_nearest_1000 = True

bool_csv_filled = list_of_people(folder_path, FOLDER_NAME_TEX, HABITANTS_TEX)

tex_dictionary = {
    'Name_pharma': closest_points_old.iloc[0,1],
    'Id_pharma': str(closest_points_old.iloc[0,0]),
    'Old_adress' : closest_points_old.iloc[0,2],
    'Old_postcode' : str(closest_points_old.iloc[0,3]),
    'Old_town' : closest_points_old.iloc[0,4],
    'New_adress': New_adresse[0],
    'New_postcode': New_adresse[1],
    'New_town' : New_adresse[2],
    'Old_X' : str(closest_points_old.iloc[0,5]),
    'Old_Y' : str(closest_points_old.iloc[0,6]),
    'New_X' : str(x_y_new_implentation[0]),
    'New_Y' : str(x_y_new_implentation[1]),
    'Date_plan' : ref_plan[0],
    'Ref_dossier' : ref_plan[1],
    'Distance_road': str(distance_old_new_road),
    'Distance_fly' : str(round(distance_old_new,2)),
    'Map_new_implentation' : new_implentation_pdf.replace('\\', '/'),
    'Map_all_itinerary_old' : all_itinerary_old_pdf.replace('\\','/'),
    'Map_all_itinerary_new' : all_itinerary_new_pdf.replace('\\','/'),
    'Map_polygon_25':polygon_construction_pdf.replace('\\','/'),
    'Map_polygon_25_zoom':polygon_construction_pdf_zoom.replace('\\','/'),
    'Name_pharma_fusion' : closest_points_new.iloc[0,1],
    'Id_pharma_fusion' : str(closest_points_new.iloc[0,0]), 
    'Name_pharma_near' : closest_points_new.iloc[1,1],
    'Id_pharma_near' : str(closest_points_old.iloc[1,0]),
    'Distance_road_near' : closest_points_old.iloc[1,9], 

    'Bool_nearest_1000' : bool_nearest_1000, 
    'Bool_near_transfert' : bool_near_transfert,
    'Bool_temp' : is_temp, 
    'Bool_is_in_polygon': is_in_polygon,
    'Bool_list_people': bool_csv_filled,
    'Bool_25_percent': bool_polygon_quarter,
    'Bool_50_percent': bool_polygon_midistance
}

# Ensure the folder name is valid and does not exist
folder_path_tex = os.path.join(folder_path, FOLDER_NAME_TEX)
create_folder(folder_path_tex)

output_path = folder_path_tex + '/' + folder_name + '.tex'       # Path for the generated LaTeX file
generate_main_latex(TEMPLATE_PATH, output_path, tex_dictionary)

# Creation of the tables
latex_file_path = folder_path_tex + '/table_old_implentation.tex'# Replace with your desired output file path
csv_path_old = folder_path + '/distance_closest_points_old.csv'
csv_to_latex_table(csv_path_old, latex_file_path, True, id_number)

latex_file_path = folder_path_tex + '/table_new_implentation.tex'# Replace with your desired output file path
csv_path_new = folder_path + '/distance_closest_points_new.csv'
csv_to_latex_table(csv_path_new, latex_file_path, False, id_number)

compile_tex_to_pdf(os.path.join(MAIN_FOLDER, YEAR, folder_name, "Tex_files"), folder_name +'.tex')

##########################################################################################
end_time_overall = time.time()
elapsed_time_overall =  end_time_overall - start_time_overall
print(f"Temps overall {round(elapsed_time_overall, 2)}s")
