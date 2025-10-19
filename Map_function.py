import requests
import folium
from folium.features import DivIcon
from folium.plugins import FloatImage
from concurrent.futures import ThreadPoolExecutor
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import LineString

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

# def display_route(geometry, map_path, padding):
#     # Create an empty map without a specified center
#     map = folium.Map(zoom_control=False,control_scale=True, zoom_snap=0.1)
    
#     folium.PolyLine(geometry, color='blue').add_to(map)


#     # Add markers with text for the start and end points
#     folium.Marker(location=geometry[0],
#                   icon=folium.Icon(prefix='fa', icon="plus", color='green', icon_color="white"),
#                   tooltip=folium.Tooltip("Ancienne implantation", permanent=True, direction="bottom")
#                   ).add_to(map)

#     folium.Marker(location=geometry[-1],
#                   icon=folium.Icon(color="green", prefix='fa', icon='plus', icon_color='white'),
#                   tooltip=folium.Tooltip("Nouvelle implantation", permanent=True, direction="bottom")
#                   ).add_to(map)
    
#     # FIT THE MAP TO THE ROUTE BOUNDS - This was missing!
#     lats, lons = zip(*geometry)
#     # map.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])

#     # padding = 0.00002  # Very small padding - adjust as needed (0.001 is about 100m)
#     map.fit_bounds([[min(lats) - padding, min(lons) - padding], 
#                     [max(lats) + padding, max(lons) + padding]])
    
#     # Custom CSS to increase tooltip font size
#     style = "<style>.leaflet-tooltip { font-size: 14px; }</style>"

#     # Adding custom CSS to the map
#     map.get_root().html.add_child(folium.Element(style))
    
#     url = ("D:/Pharmacy_Raph/Codes/North.png")
#     FloatImage(url, bottom=85, left=90, width='50px').add_to(map)
    
#     # Save the map to an HTML file
#     map.save(map_path)

# def display_route_all_pharma(gdf, API_KEY, map_path, bool_old, offset_map, shp_path=None):
#     pharmacy_label = "Ancienne" if bool_old else "Nouvelle"
#     # Assuming the first row is the start point
#     start_point = gdf.iloc[0]
#     start_coords = [start_point.geometry.x, start_point.geometry.y]

#     # Prepare tasks for each route
#     tasks = [((start_coords, [row.geometry.x, row.geometry.y]), index) for index, row in gdf.iloc[1:].iterrows()]
    
#     all_coords = []

#     # Create an empty map without a specified center
#     map = folium.Map(zoom_control=False, control_scale=True, zoom_snap=0.2)

#     if shp_path:
#         polygon_gdf = gpd.read_file(shp_path)
#         folium.GeoJson(
#             polygon_gdf,
#             style_function=lambda x: {
#                 'fillColor': 'rgba(255, 165, 0)',  # light orange with 30% opacity
#                 'color': 'orange',                      # border color
#                 'weight': 2,
#                 'fillOpacity': 0.3                      # also controls fill transparency
#             }
#         ).add_to(map)

#     with ThreadPoolExecutor(max_workers=20) as executor:
#         future_to_route = {executor.submit(get_route, task[0], task[1], API_KEY): (task, index) for task, index in tasks}
#         for future in future_to_route:
#             task, index = future_to_route[future]
#             geometry = future.result()
#             if geometry:
#                 folium.PolyLine(geometry, weight=1, color='blue').add_to(map)
#                 folium.Marker(
#                     location=geometry[-1],
#                     icon=folium.DivIcon(
#                         html=f"""
#                             <div style="
#                                 background-color: rgba(0, 0, 255, 0.0);   /* semi-transparent blue */
#                                 color: black;
#                                 border-radius: 50%;
#                                 width: 150px;
#                                 height: 150px;
#                                 text-align: center;
#                                 font-size: 18px;
#                                 line-height: 150px;
#                                 font-weight: bold;
#                             ">
#                                 {index}
#                             </div>
#                         """,
#                         icon_size=(150, 150)
#                     )
#                 ).add_to(map)
#                 all_coords.extend(geometry)

#     folium.Marker(
#         location=geometry[0],
#         icon=folium.Icon(prefix='fa', icon="plus", color='green', icon_color="white"),
#         tooltip=folium.Tooltip(f"{pharmacy_label}", permanent=True, direction="bottom")
#     ).add_to(map)

#    # TIGHTER ZOOM - Reduce padding around the bounds
#     lats, lons = zip(*all_coords)
#     # Option 1: Use smaller padding values instead of offset_map
#     delta_lat = round(max(lats) - min(lats), 3)
#     print(delta_lat)
#     padding = delta_lat*1e-2  # Very small padding - adjust as needed (0.001 is about 100m)
#     print(padding)
#     map.fit_bounds([[min(lats) - padding, min(lons)], 
#                     [max(lats) + padding, max(lons)]])
    
#     # Option 2: If you want to keep using offset_map, make it much smaller
#     # map.fit_bounds([[min(lats), min(lons)], [max(lats) + offset_map, max(lons)]])

#     url = ("D:/Pharmacy_Raph/Codes/North.png")
#     FloatImage(url, bottom=85, left=90, width='50px').add_to(map)

#     # Save the map to an HTML file
#     map.save(map_path)

def itinerary_cadastral_background(route_geometry, cadastral_map, map_path): 
    coords_lat_long = [(lon, lat) for lat, lon in route_geometry]
    route = LineString(coords_lat_long)

    gdf = gpd.GeoDataFrame([{'id': 1}], geometry=[route], crs='EPSG:4326')

    gdf_transformed = gdf.to_crs('EPSG:3812')

    transformed_route = gdf_transformed.geometry[0]
    # Extract coordinates
    x_coords = [coord[0] for coord in transformed_route.coords]
    y_coords = [coord[1] for coord in transformed_route.coords]

    minx, miny, maxx, maxy = transformed_route.bounds

    # Calculate 10% expansion
    width = maxx - minx
    height = maxy - miny
    buffer_x = width * 0.4  # 10% buffer
    buffer_y = height * 0.4

    expanded_bounds = (
        minx - buffer_x,
        miny - buffer_y,
        maxx + buffer_x,
        maxy + buffer_y
    )
    parcels = gpd.read_file(cadastral_map, 
                    bbox=expanded_bounds,  # Only load relevant area
                    ignore_geometry=False,
                    include_fields=[])  # Skip attribute data for speed
    
    fig, ax = plt.subplots(figsize=(12, 12))
    parcels.plot(ax=ax, color='white', edgecolor='black', linewidth=0.3, alpha=0.5)
    gdf_transformed.plot(ax=ax, color='blue', linewidth=2.5, alpha=0.6)
    ax.plot(x_coords[0], y_coords[0], 'go', markersize=12, zorder=2)
    ax.text(x_coords[0], y_coords[0], '   Ancienne', fontsize=12, color='black', 
            ha='left', va='bottom', weight='bold')
    ax.plot(x_coords[-1], y_coords[-1], 'ro', markersize=12, zorder=2)
    ax.text(x_coords[-1], y_coords[-1], '   Nouvelle', fontsize=12, color='black', 
            ha='left', va='bottom', weight='bold')
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim([minx-width*0.2,maxx+width*0.2])
    ax.set_ylim([miny-height*0.2,maxy+height*0.2])
    ax.set_xlabel('Est (EPSG:3812)', fontsize=12)
    ax.set_ylabel('Nord (EPSG:3812)', fontsize=12)
    plt.tight_layout()
    plt.savefig(map_path, dpi=600, bbox_inches='tight')

def polygon_50_map(cadastral_map, fitted_polygon, polygon_50, adresse_polygon, polygon_50_percent_pdf, 
                       coords_new_pharma, route_geometry, gdf_pharmacy, bool_polygon):
    gdf_fitted = gpd.read_file(fitted_polygon, crs='EPSG:4326')
    gdf_fitted = gdf_fitted.to_crs('EPSG:3812')
    gdf_50_percent = gpd.read_file(polygon_50)
    df = pd.read_csv(adresse_polygon)
    adresse_in_polygon = gpd.GeoDataFrame(df,geometry=gpd.points_from_xy(df.X, df.Y), crs='EPSG:31370')
    adresse_in_polygon = adresse_in_polygon.to_crs('EPSG:3812')
    gdf_pharmacy = gdf_pharmacy.to_crs('EPSG:3812')
    gdf_pharmacy = gdf_pharmacy.iloc[1:]

    minx, miny, maxx, maxy = gdf_pharmacy.total_bounds
    # Calculate 10% expansion
    width = maxx - minx
    height = maxy - miny
    buffer_x = width * 0.1  # 10% buffer
    buffer_y = height * 0.1

    expanded_bounds = (
        minx - buffer_x,
        miny - buffer_y,
        maxx + buffer_x,
        maxy + buffer_y
    )

    parcels = gpd.read_file(cadastral_map, 
                bbox=expanded_bounds,  # Only load relevant area
                ignore_geometry=False,
                include_fields=[])  # Skip attribute data for speed
    
    fig, ax = plt.subplots(figsize=(12, 12))
    parcels.plot(ax=ax, color='white', edgecolor='black', linewidth=0.3, alpha=0.4)
    gdf_pharmacy.plot(ax=ax, color= 'magenta', marker='D', markersize=75, edgecolor='black', zorder=8)
    # Add index labels to each geometry
    for idx, row in gdf_pharmacy.iterrows():
        # Get the centroid of the geometry for label placement
        centroid = row.geometry.centroid 
        # Add text at the centroid
        ax.text(centroid.x, centroid.y, '  '+str(idx), fontsize=15, color='black', ha='left', va='bottom', weight='bold', zorder=9)  # High zorder to appear on top
        
        
    if bool_polygon:
        gdf_fitted.plot(ax=ax, color='green', linewidth=2.5, alpha=0.25)
        gdf_50_percent.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1.5, alpha=1)
        adresse_in_polygon.plot(ax=ax, color='blue', markersize=1)

    # Define colors for different iterations
    iteration_colors = ['darkorange', 'moccasin', 'moccasin'] 
    
    for i in range(1, len(route_geometry)):  # Start from 1 to skip empty routes
        route_variations = route_geometry[i]
        
        # Plot each iteration for this route
        for iteration_idx, coords in enumerate(route_variations):
            if len(coords) > 0:  # Check if coordinates exist
                # Create LineString from coordinates (swap lat/lon to lon/lat)
                line = LineString([(lon, lat) for lat, lon in coords])
                gdf_line = gpd.GeoDataFrame([{'geometry': line}], crs='EPSG:4326')
                gdf_line = gdf_line.to_crs('EPSG:3812')
                
                # Get color for this iteration
                color = iteration_colors[iteration_idx] if iteration_idx < len(iteration_colors) else 'gray'

                zorder = 7 - iteration_idx
                
                # # Add label only once per iteration type
                # label = iteration_labels[iteration_idx] if iteration_idx < len(iteration_labels) else f'Iteration {iteration_idx + 1}'
                # if iteration_idx not in labels_added:
                #     gdf_line.plot(ax=ax, color=color, linewidth=2, alpha=0.7, label=label)
                #     labels_added.add(iteration_idx)
                # else:
                gdf_line.plot(ax=ax, color=color, linewidth=3, alpha=0.9, zorder=zorder)
    

    ax.plot(coords_new_pharma.x, coords_new_pharma.y, 'ro', markersize=10, zorder=10)
    ax.text(coords_new_pharma.x, coords_new_pharma.y, '  X: %.2f\n  Y: %.2f' %(coords_new_pharma.x, coords_new_pharma.y),
            fontsize=10, color='black', ha='left', va='bottom', weight='bold', zorder=9)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('Est (EPSG:3812)', fontsize=12)
    ax.set_ylabel('Nord (EPSG:3812)', fontsize=12)
    ax.set_xlim([minx-width*0.05,maxx+width*0.05])
    ax.set_ylim([miny-height*0.05,maxy+height*0.05])
    plt.tight_layout()
    plt.savefig('polygon_50.png', dpi=300, bbox_inches='tight')

    plt.savefig(polygon_50_percent_pdf, bbox_inches='tight')


def polygon_25_map(cadastral_map, polygon_25, map_path, gdf_pharmacy, old_coordinates, new_coordinates, route_geometry, bool_polygon):
    gdf_25_percent = gpd.read_file(polygon_25)
    # df = pd.read_csv(list_pharmacy)
    # gdf_pharmacy = gpd.GeoDataFrame(df,geometry=gpd.points_from_xy(df.X, df.Y), crs='EPSG:3812')
    gdf_pharmacy = gdf_pharmacy.to_crs('EPSG:3812')
    gdf_pharmacy = gdf_pharmacy.iloc[1:]

    minx, miny, maxx, maxy = gdf_pharmacy.total_bounds
    # Calculate 10% expansion
    width = maxx - minx
    height = maxy - miny
    buffer_x = width * 0.1  # 10% buffer
    buffer_y = height * 0.1

    expanded_bounds = (
        minx - buffer_x,
        miny - buffer_y,
        maxx + buffer_x,
        maxy + buffer_y
    )

    parcels = gpd.read_file(cadastral_map, 
                bbox=expanded_bounds,  # Only load relevant area
                ignore_geometry=False,
                include_fields=[])  # Skip attribute data for speed
    
    fig, ax = plt.subplots(figsize=(12, 12))
    parcels.plot(ax=ax, color='white', edgecolor='black', linewidth=0.3, alpha=0.4)
    if bool_polygon:
        gdf_25_percent.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1.5, alpha=1)
    gdf_pharmacy.plot(ax=ax, color= 'magenta', marker='D', markersize=75, edgecolor='black', zorder=8)

    for idx, row in gdf_pharmacy.iterrows():
        # Get the centroid of the geometry for label placement
        centroid = row.geometry.centroid 
        # Add text at the centroid
        ax.text(centroid.x, centroid.y, '  '+str(idx), fontsize=15, color='black', ha='left', va='bottom', weight='bold', zorder=9)  # High zorder to appear on top
      
    # Define colors for different iterations
    iteration_colors = ['darkorange', 'moccasin', 'moccasin'] 

    for i in range(1, len(route_geometry)):  # Start from 1 to skip empty routes
        route_variations = route_geometry[i]
        
        # Plot each iteration for this route
        for iteration_idx, coords in enumerate(route_variations):
            if len(coords) > 0:  # Check if coordinates exist
                # Create LineString from coordinates (swap lat/lon to lon/lat)
                line = LineString([(lon, lat) for lat, lon in coords])
                gdf_line = gpd.GeoDataFrame([{'geometry': line}], crs='EPSG:4326')
                gdf_line = gdf_line.to_crs('EPSG:3812')
                
                # Get color for this iteration
                color = iteration_colors[iteration_idx] if iteration_idx < len(iteration_colors) else 'gray'

                zorder = 8 - iteration_idx
                
                # # Add label only once per iteration type
                # label = iteration_labels[iteration_idx] if iteration_idx < len(iteration_labels) else f'Iteration {iteration_idx + 1}'
                # if iteration_idx not in labels_added:
                #     gdf_line.plot(ax=ax, color=color, linewidth=2, alpha=0.7, label=label)
                #     labels_added.add(iteration_idx)
                # else:
                gdf_line.plot(ax=ax, color=color, linewidth=2.5, alpha=0.8, zorder=zorder)
  

    ax.plot(old_coordinates.x, old_coordinates.y, 'ro', markersize=10, zorder=10)
    ax.text(old_coordinates.x, old_coordinates.y, '  X: %.2f\n  Y: %.2f' %(old_coordinates.x, old_coordinates.y),
            fontsize=10, color='black', ha='left', va='bottom', weight='bold', zorder=9)
    ax.plot(new_coordinates.x, new_coordinates.y, 'go', markersize=10, zorder=10)
    ax.text(new_coordinates.x, new_coordinates.y, '  X: %.2f\n  Y: %.2f' %(new_coordinates.x, new_coordinates.y),
            fontsize=10, color='black', ha='left', va='bottom', weight='bold', zorder=9)
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('Est (EPSG:3812)', fontsize=12)
    ax.set_ylabel('Nord (EPSG:3812)', fontsize=12)
    ax.set_xlim([minx-width*0.05,maxx+width*0.05])
    ax.set_ylim([miny-height*0.05,maxy+height*0.05])
    plt.tight_layout()
    plt.savefig('polygon_25.png', dpi=300, bbox_inches='tight')
    plt.savefig(map_path, bbox_inches='tight')
    