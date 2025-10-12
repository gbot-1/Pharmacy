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

def display_route(geometry, map_path, padding):
    # Create an empty map without a specified center
    map = folium.Map(zoom_control=False,control_scale=True, zoom_snap=0.1)
    
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
    
    # FIT THE MAP TO THE ROUTE BOUNDS - This was missing!
    lats, lons = zip(*geometry)
    # map.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])

    # padding = 0.00002  # Very small padding - adjust as needed (0.001 is about 100m)
    map.fit_bounds([[min(lats) - padding, min(lons) - padding], 
                    [max(lats) + padding, max(lons) + padding]])
    
    # Custom CSS to increase tooltip font size
    style = "<style>.leaflet-tooltip { font-size: 14px; }</style>"

    # Adding custom CSS to the map
    map.get_root().html.add_child(folium.Element(style))
    
    url = ("D:/Pharmacy_Raph/Codes/North.png")
    FloatImage(url, bottom=85, left=90, width='50px').add_to(map)
    
    # Save the map to an HTML file
    map.save(map_path)

def display_route_all_pharma(gdf, API_KEY, map_path, bool_old, offset_map, shp_path=None):
    pharmacy_label = "Ancienne" if bool_old else "Nouvelle"
    # Assuming the first row is the start point
    start_point = gdf.iloc[0]
    start_coords = [start_point.geometry.x, start_point.geometry.y]

    # Prepare tasks for each route
    tasks = [((start_coords, [row.geometry.x, row.geometry.y]), index) for index, row in gdf.iloc[1:].iterrows()]
    
    all_coords = []

    # Create an empty map without a specified center
    map = folium.Map(zoom_control=False, control_scale=True, zoom_snap=0.2)

    if shp_path:
        polygon_gdf = gpd.read_file(shp_path)
        folium.GeoJson(
            polygon_gdf,
            style_function=lambda x: {
                'fillColor': 'rgba(255, 165, 0)',  # light orange with 30% opacity
                'color': 'orange',                      # border color
                'weight': 2,
                'fillOpacity': 0.3                      # also controls fill transparency
            }
        ).add_to(map)

    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_route = {executor.submit(get_route, task[0], task[1], API_KEY): (task, index) for task, index in tasks}
        for future in future_to_route:
            task, index = future_to_route[future]
            geometry = future.result()
            if geometry:
                folium.PolyLine(geometry, weight=1, color='blue').add_to(map)
                folium.Marker(
                    location=geometry[-1],
                    icon=folium.DivIcon(
                        html=f"""
                            <div style="
                                background-color: rgba(0, 0, 255, 0.0);   /* semi-transparent blue */
                                color: black;
                                border-radius: 50%;
                                width: 150px;
                                height: 150px;
                                text-align: center;
                                font-size: 18px;
                                line-height: 150px;
                                font-weight: bold;
                            ">
                                {index}
                            </div>
                        """,
                        icon_size=(150, 150)
                    )
                ).add_to(map)
                all_coords.extend(geometry)

    folium.Marker(
        location=geometry[0],
        icon=folium.Icon(prefix='fa', icon="plus", color='green', icon_color="white"),
        tooltip=folium.Tooltip(f"{pharmacy_label}", permanent=True, direction="bottom")
    ).add_to(map)

   # TIGHTER ZOOM - Reduce padding around the bounds
    lats, lons = zip(*all_coords)
    # Option 1: Use smaller padding values instead of offset_map
    delta_lat = round(max(lats) - min(lats), 3)
    print(delta_lat)
    padding = delta_lat*1e-2  # Very small padding - adjust as needed (0.001 is about 100m)
    print(padding)
    map.fit_bounds([[min(lats) - padding, min(lons)], 
                    [max(lats) + padding, max(lons)]])
    
    # Option 2: If you want to keep using offset_map, make it much smaller
    # map.fit_bounds([[min(lats), min(lons)], [max(lats) + offset_map, max(lons)]])

    url = ("D:/Pharmacy_Raph/Codes/North.png")
    FloatImage(url, bottom=85, left=90, width='50px').add_to(map)

    # Save the map to an HTML file
    map.save(map_path)