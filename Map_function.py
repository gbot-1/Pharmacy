import requests
import folium
from folium.features import DivIcon
from folium.plugins import FloatImage
from concurrent.futures import ThreadPoolExecutor
import geopandas as gpd

def get_route(start_coords, end_coords, API_KEY):
    # OpenRouteService Directions API endpoint
    endpoint = 'https://api.openrouteservice.org/v2/directions/foot-walking/geojson'

    # Request headers
    headers = {
        'Authorization': API_KEY,
        'Content-Type': 'application/json'
    }

    # Request body
    body = {
        'coordinates': [start_coords, end_coords]
    }

    # Make the request
    response = requests.post(endpoint, json=body, headers=headers)
    
    # Check the response
    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return None

    data = response.json()

    # Extract the geometry
    geometry = data['features'][0]['geometry']['coordinates']

    # Flip coordinates (OpenRouteService uses lon/lat instead of lat/lon)
    geometry = [(lat, lon) for lon, lat in geometry]

    return geometry

def display_route(geometry, map_path):
    # Create an empty map without a specified center
    map = folium.Map(zoom_control=False,control_scale=True)
    
    folium.PolyLine(geometry, color='blue').add_to(map)


    # Calculate the bounds of the route
    lats, lons = zip(*geometry)
    map.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])
    
    # Add markers with text for the start and end points
    folium.Marker(location=geometry[0],
                  icon=folium.Icon(prefix='fa', icon="horse", color='cadetblue', icon_color="pink"),
                  tooltip=folium.Tooltip("Ancienne implémentation", permanent=True, direction="bottom")
                  ).add_to(map)

    folium.Marker(location=geometry[-1],
                  icon=folium.Icon(color="blue", prefix='fa', icon='dog', icon_color='red'),
                  tooltip=folium.Tooltip("Nouvelle implémentation", permanent=True, direction="bottom")
                  ).add_to(map)
    
    url = ("D:/Pharmacy_Raph/Codes/North.png")
    FloatImage(url, bottom=85, left=90, width='50px').add_to(map)
    
    # Save the map to an HTML file
    map.save(map_path)

def display_route_all_pharma(gdf, API_KEY, map_path, bool_old, offset_map):
    pharmacy_label = "Ancienne pharmacie" if bool_old else "Nouvelle pharmacie"
    # Assuming the first row is the start point
    start_point = gdf.iloc[0]
    start_coords = [start_point.geometry.x, start_point.geometry.y]

    # Prepare tasks for each route
    tasks = [((start_coords, [row.geometry.x, row.geometry.y]), index) for index, row in gdf.iloc[1:].iterrows()]
    
    all_coords = []

    # Create an empty map without a specified center
    map = folium.Map(zoom_control=False, control_scale=True)

    # Loop through gdf starting from the second row to plot each route
    # for index, row in gdf.iloc[1:10].iterrows():
    #     end_coords = [row.geometry.x, row.geometry.y]
    #     geometry = get_route(start_coords, end_coords, API_KEY)

    #     if geometry:
    #         folium.PolyLine(geometry, color='blue').add_to(map)
    #         # Add marker for the end point of this route
    #         folium.Marker(
    #             location=geometry[-1],
    #             icon=folium.Icon(color="blue", prefix='fa', icon='dog', icon_color='red'),
    #             tooltip=folium.Tooltip(f"{index}", permanent=True, direction="bottom")
    #         ).add_to(map)
        
    #     all_coords.extend(geometry)
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_route = {executor.submit(get_route, task[0], task[1], API_KEY): (task, index) for task, index in tasks}
        for future in future_to_route:
            task, index = future_to_route[future]
            geometry = future.result()
            if geometry:
                folium.PolyLine(geometry, color='blue').add_to(map)
                folium.Marker(
                    location=geometry[-1],
                    icon=folium.Icon(color="blue", prefix='fa', icon=f"{index}", icon_color='red'),
                ).add_to(map)
                all_coords.extend(geometry)

    folium.Marker(
        location=geometry[0],
        icon=folium.Icon(prefix='fa', icon="horse", color='cadetblue', icon_color="pink"),
        tooltip=folium.Tooltip("Ancienne \n implantation", permanent=True, direction="bottom")
    ).add_to(map)

    lats, lons = zip(*all_coords)
    map.fit_bounds([[min(lats), min(lons)], [max(lats)+offset_map, max(lons)]])

    url = ("D:/Pharmacy_Raph/Codes/North.png")
    FloatImage(url, bottom=85, left=90, width='50px').add_to(map)

    # Save the map to an HTML file
    map.save(map_path)