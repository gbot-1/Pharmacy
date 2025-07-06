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
        'coordinates': [start_coords, end_coords],
        "preference": 'shortest'
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


    # Add markers with text for the start and end points
    folium.Marker(location=geometry[0],
                  icon=folium.Icon(prefix='fa', icon="plus", color='green', icon_color="white"),
                  tooltip=folium.Tooltip("Ancienne implantation", permanent=True, direction="bottom")
                  ).add_to(map)

    folium.Marker(location=geometry[-1],
                  icon=folium.Icon(color="green", prefix='fa', icon='plus', icon_color='white'),
                  tooltip=folium.Tooltip("Nouvelle implantation", permanent=True, direction="bottom")
                  ).add_to(map)
    
    # Custom CSS to increase tooltip font size
    style = "<style>.leaflet-tooltip { font-size: 14px; }</style>"

    # Adding custom CSS to the map
    map.get_root().html.add_child(folium.Element(style))
    
    url = ("D:/Pharmacy_Raph/Codes/North.png")
    FloatImage(url, bottom=85, left=90, width='50px').add_to(map)
    
    # Save the map to an HTML file
    map.save(map_path)

def display_route_all_pharma(gdf, API_KEY, map_path, bool_old, offset_map, shp_path=None):
    pharmacy_label = "Ancienne pharmacie" if bool_old else "Nouvelle pharmacie"
    # Assuming the first row is the start point
    start_point = gdf.iloc[0]
    start_coords = [start_point.geometry.x, start_point.geometry.y]

    # Prepare tasks for each route
    tasks = [((start_coords, [row.geometry.x, row.geometry.y]), index) for index, row in gdf.iloc[1:].iterrows()]
    
    all_coords = []

    # Create an empty map without a specified center
    map = folium.Map(zoom_control=False, control_scale=True)

    if shp_path:
        polygon_gdf = gpd.read_file(shp_path)
        folium.GeoJson(
            polygon_gdf,
            style_function=lambda x: {
                'fillColor': 'none',
                'color': 'blue',
                'weight': 2,
                'dashArray': '5, 5'
            }
        ).add_to(map)

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
        icon=folium.Icon(prefix='fa', icon="plus", color='green', icon_color="white"),
        tooltip=folium.Tooltip(f"{pharmacy_label}", permanent=True, direction="bottom")
    ).add_to(map)

    lats, lons = zip(*all_coords)
    map.fit_bounds([[min(lats), min(lons)], [max(lats)+offset_map, max(lons)]])

    url = ("D:/Pharmacy_Raph/Codes/North.png")
    FloatImage(url, bottom=85, left=90, width='50px').add_to(map)

    # Save the map to an HTML file
    map.save(map_path)