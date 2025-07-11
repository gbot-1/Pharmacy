import requests
import geopandas as gpd
import numpy as np
import polyline
from shapely.geometry import Point
from concurrent.futures import ThreadPoolExecutor

def get_planar_distance(gdf_init,geometry,nb_point):
    gdf = gdf_init.copy(deep=True)
    gdf['distance'] = gdf.geometry.distance(geometry)
    closest_points = gdf.sort_values(by='distance').head(nb_point)
    closest_points = closest_points.reset_index(drop=True)

    closest_points.crs = "EPSG:3812"
    # closest_points = closest_points.to_crs("EPSG:4326") #convert to WGS 84 - needed for road distance
    # # closest_points.to_csv('closest_WGS.csv')
    
    return closest_points

def distance_fly_old_new_implantation(point1, point2):
    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame({'id': ['point1', 'point2'], 'geometry': [point1, point2]}, crs="EPSG:3812")

    # Convert the GeoDataFrame to Belgian Lambert 2008 CRS (EPSG:3812)
    gdf = gdf.to_crs("EPSG:3812")

    # Compute the distance between the points
    distance = gdf.at[0, 'geometry'].distance(gdf.at[1, 'geometry'])

    return distance
    
def get_road_distance_and_geometry(coord1, coord2, API_KEY, cache):
    # Check if the distance and geometry are already in the cache
    if (coord1, coord2) in cache:
        return cache[(coord1, coord2)]
    elif (coord2, coord1) in cache:
        return cache[(coord2, coord1)]
    
    # OpenRouteService API endpoint for directions
    ors_route_url = "https://api.openrouteservice.org/v2/directions/foot-walking"
    
    # Headers to include your API key
    headers = {
        'Authorization': API_KEY,
        'Content-Type': 'application/json'
    }
    
    # Body for the POST request, including the start and end coordinates
    body = {
        "coordinates": [coord1, coord2],
        "preference": 'shortest'
    }
        
    # Sending a POST request to OpenRouteService API
    response = requests.post(ors_route_url, json=body, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        try:
            # Accessing the distance and route geometry
            distance = data['routes'][0]['segments'][0]['distance']
            route_geometry = data['routes'][0]['geometry']
            decoded_geometry = polyline.decode(route_geometry)
            if distance < 50:
                distance += 5
            # Store the result in the cache
            cache[(coord1, coord2)] = (distance, decoded_geometry)
            return distance, decoded_geometry
        except (KeyError, IndexError) as e:
            # Handle missing keys or out-of-index errors
            print(f"Error accessing distance or geometry: {e}")
            return "Error accessing route information", []
    else:
        return "Request failed", []

def get_midpoint_by_geometry(route_geometry):
    if not route_geometry:
        return None
    
    # Calculate the total distance of the route
    total_distance = 0
    distances = []
    for i in range(len(route_geometry) - 1):
        segment_distance = np.linalg.norm(np.array(route_geometry[i]) - np.array(route_geometry[i + 1]))
        distances.append(segment_distance)
        total_distance += segment_distance
    
    # Find the midpoint distance
    midpoint_distance = total_distance / 2
    
    # Traverse the route to find the coordinates at the midpoint distance
    traversed_distance = 0
    for i in range(len(route_geometry) - 1):
        segment_distance = distances[i]
        if traversed_distance + segment_distance >= midpoint_distance:
            # Calculate the exact midpoint coordinates within this segment
            remaining_distance = midpoint_distance - traversed_distance
            ratio = remaining_distance / segment_distance
            midpoint = [
                route_geometry[i][0] + ratio * (route_geometry[i + 1][0] - route_geometry[i][0]),
                route_geometry[i][1] + ratio * (route_geometry[i + 1][1] - route_geometry[i][1])
            ]
            return Point(midpoint)
        traversed_distance += segment_distance
    
    return None

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
    
    # Initialize the cache
    cache = {}

    # Function to wrap get_road_distance_and_geometry for use with ThreadPoolExecutor
    def get_distance_and_geometry(params):
        return get_road_distance_and_geometry(*params, API_KEY, cache)
    
    # Calculate distances and midpoints in parallel
    road_distances = []
    midpoints = []
    with ThreadPoolExecutor(max_workers=40) as executor:
        futures = [executor.submit(get_distance_and_geometry, pair) for pair in coord_pairs]
        for future in futures:
            distance, geometry = future.result()
            road_distances.append(distance)
            midpoints.append(get_midpoint_by_geometry(geometry))
    
    # Adding the road distances and midpoints as new columns to the GeoDataFrame
    gdf['road_distance'] = road_distances
    gdf['midpoint'] = midpoints
    return gdf