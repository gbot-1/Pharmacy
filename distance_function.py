import requests
import geopandas as gpd
from concurrent.futures import ThreadPoolExecutor

def get_planar_distance(gdf_init,geometry,nb_point):
    gdf = gdf_init.copy(deep=True)
    gdf['distance'] = gdf.geometry.distance(geometry)
    closest_points = gdf.sort_values(by='distance').head(nb_point)

    closest_points.crs = "EPSG:3812"
    closest_points = closest_points.to_crs("EPSG:4326") #convert to WGS 84 - needed for road distance
    # closest_points.to_csv('closest_WGS.csv')
    
    return closest_points

def distance_fly_old_new_implantation(point1, point2):
    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame({'id': ['point1', 'point2'], 'geometry': [point1, point2]}, crs="EPSG:3812")

    # Convert the GeoDataFrame to Belgian Lambert 2008 CRS (EPSG:3812)
    gdf = gdf.to_crs("EPSG:3812")

    # Compute the distance between the points
    distance = gdf.at[0, 'geometry'].distance(gdf.at[1, 'geometry'])

    return distance
    
# """Compute road distance"""
# def get_road_distance_a(coord1, coord2):
#     # Correct OSRM API endpoint format
#     osrm_route_url = f"http://router.project-osrm.org/route/v1/walking/{coord1[0]},{coord1[1]};{coord2[0]},{coord2[1]}?overview=full"
#     # Sending a request to OSRM API
#     response = requests.get(osrm_route_url)

#     # Check if the request was successful
#     if response.status_code == 200:
#         data = response.json()
#         # Check if routes are available
#         if data['routes']:
#             distance = data['routes'][0]['distance']  # distance in meters
#             if distance < 50:
#                 return (distance + 5)
#             else:
#                 return distance
#         else:
#             return "No route found"
#     else:
#         return "Request failed"
    
def get_road_distance(coord1, coord2, API_KEY):
    # OpenRouteService API endpoint for directions
    ors_route_url = "https://api.openrouteservice.org/v2/directions/foot-walking"
    
    # Headers to include your API key
    headers = {
        'Authorization': API_KEY,
        'Content-Type': 'application/json'
    }
    
    # Body for the POST request, including the start and end coordinates
    body = {
        "coordinates": [coord1, coord2]
    }
        
    # Sending a POST request to OpenRouteService API
    response = requests.post(ors_route_url, json=body, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        try:
            # Accessing the distance using the corrected path based on your response structure
            distance = data['routes'][0]['segments'][0]['distance']
            if distance < 50:
                return distance + 5
            else:
                return distance
        except (KeyError, IndexError) as e:
            # Handle missing keys or out-of-index errors
            print(f"Error accessing distance: {e}")
            return "Error accessing route information"
    else:
        return "Request failed"

def road_distance(gdf, coord_init, API_KEY):
    # Convert the initial coordinate to EPSG:4326 if necessary
    temp_gdf = gpd.GeoDataFrame([1], geometry=[coord_init], crs="EPSG:3812")
    temp_gdf = temp_gdf.to_crs("EPSG:4326")
    first_point = temp_gdf.geometry.iloc[0]
    first_coord = (first_point.x, first_point.y)

    
    # Prepare a list of coordinate pairs for parallel processing
    coord_pairs = []
    for index, row in gdf.iterrows():
        current_point = row.geometry
        current_coord = (current_point.x, current_point.y)
        coord_pairs.append((first_coord, current_coord))
    
    # Function to wrap get_road_distance for use with ThreadPoolExecutor
    def get_distance(params):
        return get_road_distance(*params, API_KEY)
    
    # Calculate distances in parallel
    road_distances = []
    with ThreadPoolExecutor(max_workers=40) as executor:
        futures = [executor.submit(get_distance, pair) for pair in coord_pairs]
        for future in futures:
            road_distances.append(future.result())
    
    # Adding the road distances as a new column to the GeoDataFrame
    gdf['road_distance'] = road_distances
    return gdf