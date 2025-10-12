"""TO DO"""
"""
POLYGONE
Si carte trop petite, pas mettre itinéraire mais truc différent sur page de garde 
meilleur zoom cartes + polygone visible 100% 
test is_in_polygon
path adresse_in_polygon
Only one call of the API instead of 2. => stored geometry 

Rapport transfert simple
if < 100 m: 
    rapport classique
else:
    if is_in_25%:
        rapport classique
    else:
        polygone 50% w/ liste habitations

Transfert + Fusion
Rapport classique

Fusion
if ( >= 1 pharma in dist<1000):
    tableau distance par rapport nouvelle
    plan nouvelle adresse
    plan 2 adresses
else:
    tableau distance par rapport nouvelle
    plan nouvelle adresse
    plan 2 adresses
    polygone 50% + adresse_in_polygone.csv



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

FILEPATH = 'D:/Pharmacy_Raph/Lst_Pharmacies_pub_Extended.xlsx'
ADRESS_CSV = 'D:/Pharmacy_Raph/adresses.csv'
TEMPLATE_PATH = 'D:/Pharmacy_Raph/Codes/template_rapport.tex'
MAIN_FOLDER = "D:/Pharmacy_Raph"
MAP_NEW_PHARMACY = 'map_new_implentation.png'
HTML_NEW_PHARMACY = 'itinerary_new_pharmacy.html'
MAP_ALL_PHARMACY_OLD = 'map_all_pharmacy_old.png'
MAP_ALL_PHARMACY_NEW = 'map_all_pharmacy_new.png'
HTML_ALL_PHARMACY_OLD = 'all_itineraries_old.html'
HTML_ALL_PHARMACY_NEW = 'all_itineraries_new.html'
POLYGON_50_PERCENT = 'polygon_50_percent'
POLYGON_25_PERCENT = 'polygon_25_percent'
EXCEL_HOUSES = 'adresses_in_polygon.csv'
CADASTRAL_MAP = 'D:/Pharmacy_Raph/QGIS/Cadastre/Bpn_CaPa_WAL.shp'
FOLDER_NAME_TEX = 'Tex_files'
NB_POINT = 10
YEAR = str(datetime.datetime.now().year)
API_KEY = '5b3ce3597851110001cf6248cca3afa1547a460ab12d2624d73dbe4e'

map_offset = 0.001

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

report_type = project_type()

# Get input data
coord_init, id_number = get_coord_by_pharma_id(gdf)
new_coordinates = coordinate_new_implantation()
New_adresse = adress_new_implantation()
ref_plan = date_and_ref()

closest_points_old = selection_pharmacies(gdf, coord_init, NB_POINT, new_coordinates)
closest_points_old = closest_points_old.to_crs("EPSG:4326") #convert to WGS 84 - needed for road distance

#small manipulation to have the new coordinates into the appropriate format
temp_gdf = gpd.GeoDataFrame([1], geometry=[new_coordinates], crs="EPSG:3812").geometry.iloc[0]
x_y_new_implentation = (temp_gdf.x, temp_gdf.y)

# Calculate closest points
closest_points_old = road_distance(closest_points_old, coord_init, API_KEY)
closest_points_old = closest_points_old.sort_values(by='road_distance')
closest_points_old = closest_points_old.reset_index(drop=True)

# Create folders
folder_name = ref_plan[1] + "_" + str(closest_points_old.iloc[0]['Nom'])
folder_name = folder_name.replace(" ", "_").replace("/", "_")  # Replace spaces and slashes
folder_path = os.path.join(MAIN_FOLDER, YEAR, folder_name)
create_folder(folder_path)
    
closest_points_old.to_csv(os.path.join(folder_path, 'distance_closest_points_old.csv'))

"""Create CSV for new implentation"""
gdf_temp = create_gdf_new_implentation(closest_points_old, New_adresse, new_coordinates)
closest_points_new = get_planar_distance(gdf_temp, new_coordinates, NB_POINT)
closest_points_new = closest_points_new.to_crs("EPSG:4326")
closest_points_new = road_distance(closest_points_new, new_coordinates, API_KEY)
# Sorting the second dataframe using this mapping
order_mapping = {auth_num: idx for idx, auth_num in enumerate(closest_points_old["Numéro d'autorisation"])}
closest_points_new = closest_points_new.copy()
closest_points_new['sort_key'] = closest_points_new["Numéro d'autorisation"].map(order_mapping)
closest_points_new = closest_points_new.sort_values('sort_key').drop('sort_key', axis=1)

closest_points_new.to_csv(os.path.join(folder_path, 'distance_closest_points_new.csv'))

distance_old_new = distance_fly_old_new_implantation(coord_init, new_coordinates)
if distance_old_new <= 100:
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
protection_zone_quarter_distance = create_polygon_from_intersections(closest_points_old, polygon_quarter_distance_shp)
is_in_polygon = protection_zone_quarter_distance.contains(new_coordinates)

##########################################################################################
html_path = os.path.join(MAIN_FOLDER, YEAR, folder_name, HTML_NEW_PHARMACY)
new_implentation_png = os.path.join(MAIN_FOLDER, YEAR, folder_name, MAP_NEW_PHARMACY)
html_path_all_old = os.path.join(MAIN_FOLDER, YEAR, folder_name, HTML_ALL_PHARMACY_OLD)
html_path_all_new = os.path.join(MAIN_FOLDER, YEAR, folder_name, HTML_ALL_PHARMACY_NEW)
all_itinerary_old_png = os.path.join(MAIN_FOLDER, YEAR, folder_name, MAP_ALL_PHARMACY_OLD)
all_itinerary_new_png = os.path.join(MAIN_FOLDER, YEAR, folder_name, MAP_ALL_PHARMACY_NEW)
start_coords = point_to_list(coord_init)
end_coords = point_to_list(new_coordinates)

# Get the route geometry
route_geometry = get_route(start_coords, end_coords, API_KEY)

# Display the route
if route_geometry:
    padding = distance_old_new*1e-6 
    display_route(route_geometry, html_path, padding)
else:
    print("Failed to retrieve route")

# Create converter once at the beginning
converter = HTMLToPNGConverter()

# Your original code with optimized calls:
converter.convert_single(html_path, new_implentation_png)

if report_type == 1:
    if near_transfert or is_in_polygon:
        polygon_midistance = None
        polygon_quarter = None
    else:
        polygon_midistance = polygon_midistance_shp + '.shp'
        polygon_quarter =  polygon_quarter_distance_shp + '.shp'
elif report_type == 2:
    polygon_midistance = None
    polygon_quarter = None 
elif report_type == 3:
    if closest_points_new.iloc[1]['distance'] < 1000:
        polygon_midistance = None
        polygon_quarter = None
    else:
        polygon_midistance = polygon_midistance_shp + '.shp'
        polygon_quarter =  polygon_quarter_distance_shp + '.shp'

display_route_all_pharma(closest_points_old, API_KEY, html_path_all_old, 1, map_offset, polygon_midistance)
converter.convert_single(html_path_all_old, all_itinerary_old_png)

display_route_all_pharma(closest_points_new, API_KEY, html_path_all_new, 0, map_offset, polygon_quarter)
converter.convert_single(html_path_all_new, all_itinerary_new_png)

#########################################################################################
"""Creates the .tex files"""
cache = {}
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
    'Distance_road': str(get_road_distance_and_geometry(point_to_list(coord_init), point_to_list(new_coordinates), API_KEY, cache)[0]),
    'Distance_fly' : str(round(distance_old_new,2)),
    'Map_new_implentation' : new_implentation_png.replace('\\', '/'),
    'Map_all_itinerary_old' : all_itinerary_old_png.replace('\\','/'),
    'Map_all_itinerary_new' : all_itinerary_new_png.replace('\\','/')
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
