"""TO DO"""
"""
Only one call of the API instead of 2. => stored geometry 
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
FOLDER_NAME_TEX = 'Tex_files'
NB_POINT = 10
YEAR = str(datetime.datetime.now().year)
API_KEY = '5b3ce3597851110001cf6248cca3afa1547a460ab12d2624d73dbe4e'

map_offset = 0


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

# report_type = project_type()

# Get input data
coord_init, id_number = get_coord_by_pharma_id(gdf)
new_coordinates = coordinate_new_implantation()
New_adresse = adress_new_implantation()
ref_plan = date_and_ref()

#small manipulation to have the new coordinates into the appropriate format
temp_gdf = gpd.GeoDataFrame([1], geometry=[new_coordinates], crs="EPSG:3812").geometry.iloc[0]
x_y_new_implentation = (temp_gdf.x, temp_gdf.y)

# Calculate closest points
closest_points_old = road_distance(get_planar_distance(gdf, coord_init, NB_POINT), coord_init, API_KEY)
closest_points_old = closest_points_old.sort_values(by='road_distance')
original_order = closest_points_old.index
closest_points_old = closest_points_old.reset_index(drop=True)

# Create folders
folder_name = ref_plan[1] + "_" + str(closest_points_old.iloc[1]['Nom'])
folder_name = folder_name.replace(" ", "_").replace("/", "_")  # Replace spaces and slashes
folder_path = os.path.join(MAIN_FOLDER, YEAR, folder_name)
create_folder(folder_path)
    
closest_points_old.to_csv(os.path.join(folder_path, 'distance_closest_points_old.csv'))

"""Create CSV for new implentation"""
gdf_temp = create_gdf_new_implentation(gdf, closest_points_old, New_adresse, new_coordinates)
closest_points_new = road_distance(get_planar_distance(gdf_temp, new_coordinates, NB_POINT), new_coordinates, API_KEY)
if set(original_order) == set(closest_points_new.index):
    closest_points_new = closest_points_new.reindex(original_order).reset_index(drop=True)
else:
    closest_points_new = closest_points_new.reset_index(drop=True)
closest_points_new.to_csv(os.path.join(folder_path, 'distance_closest_points_new.csv'))

############################################################################################
# """Polygon drawing"""
# x_percentage = 0.3
# nb_vertex = 7

# reference_point = closest_points_new.geometry.iloc[0]
# print(reference_point)

# gdf_test = closest_points_new.iloc[2:]
# coords = np.array([[point.y, point.x] for point in gdf_test['midpoint']])
# zone_protection = create_polygon(reference_point, coords)

# # zone_protection = generate_polygon(closest_points_new, reference_point, x_percentage, nb_vertex)

# plot_polygon(closest_points_new, reference_point, zone_protection, x_percentage, nb_vertex)

# find_points_in_polygon(ADRESS_CSV, zone_protection, 'adresses_in_polygon.csv')

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
    display_route(route_geometry, html_path)
else:
    print("Failed to retrieve route")

save_svg_to_png(html_path, new_implentation_png)

display_route_all_pharma(closest_points_old, API_KEY, html_path_all_old, 1, map_offset)

save_svg_to_png(html_path_all_old, all_itinerary_old_png)

display_route_all_pharma(closest_points_new, API_KEY, html_path_all_new, 0, map_offset)

save_svg_to_png(html_path_all_new, all_itinerary_new_png)

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
    'Distance_fly' : str(round(distance_fly_old_new_implantation(coord_init, new_coordinates),2)),
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
