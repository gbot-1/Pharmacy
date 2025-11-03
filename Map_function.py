import requests
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
    parcels.plot(ax=ax, color='white', edgecolor='silver', linewidth=0.3, alpha=0.5)
    gdf_transformed.plot(ax=ax, color='blue', linewidth=2.5, alpha=0.6)
    ax.plot(x_coords[0], y_coords[0], 'ro', markersize=12, zorder=2)
    ax.text(x_coords[0], y_coords[0], '   Ancienne', fontsize=12, color='black', 
            ha='left', va='bottom', weight='bold')
    ax.plot(x_coords[-1], y_coords[-1], 'go', markersize=12, zorder=2)
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
                        coords_new_pharma, gdf_routes, gdf_pharmacy, bool_polygon, report_type):
    gdf_fitted = gpd.read_file(fitted_polygon, crs='EPSG:4326')
    gdf_fitted = gdf_fitted.to_crs('EPSG:3812')
    gdf_50_percent = gpd.read_file(polygon_50)
    df = pd.read_csv(adresse_polygon)
    adresse_in_polygon = gpd.GeoDataFrame(df,geometry=gpd.points_from_xy(df.X, df.Y), crs='EPSG:3812')
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
    parcels.plot(ax=ax, color='white', edgecolor='silver', linewidth=0.3, alpha=0.4)
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

    # Plot main routes
    main_routes = gdf_routes[gdf_routes['type'] == 'main']
    main_routes.plot(ax=ax, color='darkorange', linewidth=2.5, alpha=0.8, zorder=8)
    
    # Plot alternative routes
    alt_routes = gdf_routes[gdf_routes['type'] == 'alternative']
    alt_routes.plot(ax=ax, color='moccasin', linewidth=2.5, alpha=0.8, zorder=7)

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


def polygon_25_map(cadastral_map, polygon_25, map_path, gdf_pharmacy, old_coordinates, new_coordinates, 
                   gdf_routes, bool_polygon, report_type):
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
    parcels.plot(ax=ax, color='white', edgecolor='silver', linewidth=0.3, alpha=0.4)
    if bool_polygon:
        gdf_25_percent.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1.5, alpha=1)
    gdf_pharmacy.plot(ax=ax, color= 'magenta', marker='D', markersize=75, edgecolor='black', zorder=8)

    for idx, row in gdf_pharmacy.iterrows():
        # Get the centroid of the geometry for label placement
        centroid = row.geometry.centroid 
        # Add text at the centroid
        ax.text(centroid.x, centroid.y, '  '+str(idx), fontsize=15, color='black', ha='left', va='bottom', weight='bold', zorder=9)  # High zorder to appear on top
    
    # Plot main routes
    main_routes = gdf_routes[gdf_routes['type'] == 'main']
    main_routes.plot(ax=ax, color='darkorange', linewidth=2.5, alpha=0.8, zorder=8)
    
    # Plot alternative routes
    alt_routes = gdf_routes[gdf_routes['type'] == 'alternative']
    alt_routes.plot(ax=ax, color='moccasin', linewidth=2.5, alpha=0.8, zorder=7)
    
    ax.plot(old_coordinates.x, old_coordinates.y, 'ro', markersize=10, zorder=10)
    ax.text(old_coordinates.x, old_coordinates.y, '  X: %.2f\n  Y: %.2f' %(old_coordinates.x, old_coordinates.y),
            fontsize=10, color='black', ha='left', va='bottom', weight='bold', zorder=9)
    if report_type != 3 or bool_polygon is True:
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

def save_routes_to_shapefile(route_geometry, output_path, crs='EPSG:3812'):

    routes_data = []
    
    # Skip index 0 (empty routes), process indices 1-5
    for route_idx in range(1, len(route_geometry)):
        route_variations = route_geometry[route_idx]
        
        # Process each iteration for this route
        for iteration_idx, coords in enumerate(route_variations):
            if len(coords) > 0:  # Check if coordinates exist
                # Create LineString from coordinates (swap lat/lon to lon/lat)
                line = LineString([(lon, lat) for lat, lon in coords])
                
                # Determine route type
                route_type = 'main' if iteration_idx == 0 else 'alternative'
                
                # Store route data
                routes_data.append({
                    'geometry': line,
                    'route_id': route_idx,  # Which of the 5 routes (1-5)
                    'iteration': iteration_idx + 1,  # Iteration number (1, 2, 3)
                    'type': route_type  # 'main' or 'alternative'
                })
    
    # Create GeoDataFrame
    gdf_routes = gpd.GeoDataFrame(routes_data, crs='EPSG:4326')  # Input is lat/lon
    
    # Convert to target CRS
    gdf_routes = gdf_routes.to_crs(crs)
    
    # Save to shapefile
    gdf_routes.to_file(output_path + '.shp')

    return gdf_routes
