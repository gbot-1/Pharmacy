"""Polygon drawing
Le 25% (par rapport à l'ancienne) est une alternative si tu dépasses les 100m par la rue. 
Tu regardes si tu es dans le polygone pour savoir si tu ne déplaces pas trop loin de l'ancienne 
puisque la  nouvelle doit etre dans le polygone => INTERSECTION PERPENDICULAIRES


50% (par rapport à la nouvelle) pour vérifier si le déménagement ne se fait pas dans une zone où 
tu deservirait trop ou trop peu de personnes en fonction des habitants => PAR LA RUE
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import re
from shapely.geometry import Point, Polygon, LineString
import matplotlib.pyplot as plt

# Function to sort points in clockwise order
def angle_from_reference_point(point, reference_point):
    return np.arctan2(point[1] - reference_point.y, point[0] - reference_point.x)

def alphanum_key(s):
    s = str(s)
    return tuple(int(text) if text.isdigit() else text for text in re.split('([0-9]+)', s))

def find_points_in_polygon(csv_file, polygon, output_file):
    points_df = pd.read_csv(csv_file)
    # Assuming the CSV has 'latitude' and 'longitude' columns
    points_gdf = gpd.GeoDataFrame(points_df, geometry=gpd.points_from_xy(points_df.X, points_df.Y), crs="3812")

    gdf_polygon = gpd.GeoDataFrame(index=[0], crs='epsg:3812', geometry=[polygon])

    # Find points within the polygon
    points_within_polygon = gpd.sjoin(points_gdf, gdf_polygon, how='inner', predicate='within')
    # Apply the custom sort to NUMERO column
    points_within_polygon['NUMERO_SORT_KEY'] = points_within_polygon['NUMERO'].apply(alphanum_key)

    # Sort the data
    sorted_data = points_within_polygon.sort_values(by=['CODEPOSTAL', 'RUE_NOM', 'NUMERO_SORT_KEY'])
    
    columns_to_keep = ['X','Y','CODEPOSTAL','ZONE_ADRES','RUE_NOM','NUMERO']  # Replace with the columns you want to keep

    # Keep only the specified columns
    sorted_data = sorted_data[columns_to_keep]
    sorted_data["NBR_HABITANTS"] = ""

    # Save the result to a new CSV file
    sorted_data.to_csv(output_file, encoding='utf-8-sig', index=False)

    return points_within_polygon

def polygon_mid_distance(gdf, polygon_midistance_shp, cadastral_map):
    gdf_truncated = gdf.iloc[1:]
    all_points = [point for point_list in gdf_truncated['midpoint'] for point in point_list]
    coords = np.array([[point.y, point.x] for point in all_points])
    reference_point = gdf.geometry.iloc[0]
    sorted_coords = sorted(coords, key=lambda point: angle_from_reference_point(point, reference_point))
    
    protection_zone = Polygon(sorted_coords)

    gdf_polygon = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[protection_zone])
    gdf_polygon = gdf_polygon.to_crs('EPSG:3812')
    gdf_polygon.to_file(polygon_midistance_shp+'.shp', driver='ESRI Shapefile')

    protection_zone_fitted = fit_polygon_to_cadastral_plan(polygon_midistance_shp, cadastral_map)

    return protection_zone_fitted

def fit_polygon_to_cadastral_plan(polygon_path, cadastral_map):

    polygon_gdf = gpd.read_file(polygon_path+'.shp')
    polygon = polygon_gdf.geometry[0]  # Get the Shapely polygon

    parcels = gpd.read_file(cadastral_map, 
                        bbox=polygon.bounds,  # Only load relevant area
                        ignore_geometry=False,
                        include_fields=[])  # Skip attribute data for speed
    
    intersecting_parcels = parcels[parcels.intersects(polygon)]

    # Get the union of all selected parcels as your fitted polygon
    fitted_polygon = intersecting_parcels.union_all()

    # Convert to GeoDataFrame for saving
    fitted_gdf = gpd.GeoDataFrame([{'id': 1}], geometry=[fitted_polygon], crs=parcels.crs)
    fitted_gdf = fitted_gdf.to_crs('EPSG:4326')
    # Save to shapefile
    fitted_gdf.to_file(polygon_path+'_fitted.shp')
    
    return fitted_polygon

def find_quarter_point(reference_point, other_point):
    """
    Find the point at 25% distance from reference_point to another point.
    """
    reference_point_coords = np.array([reference_point.x, reference_point.y])
    other_coords = np.array([other_point.x, other_point.y])
    
    # Calculate 25% of the way from reference_point to other point
    quarter_point = reference_point_coords + 0.25 * (other_coords - reference_point_coords)
    return Point(quarter_point[0], quarter_point[1])

def get_perpendicular_line(reference_point, other_point, quarter_point, length=10000):
    """
    Create a perpendicular line at the quarter point.
    """
    # Direction vector from reference_point to other point
    dx = other_point.x - reference_point.x
    dy = other_point.y - reference_point.y
    
    # Perpendicular direction (rotate 90 degrees)
    perp_dx = -dy
    perp_dy = dx
    
    # Normalize the perpendicular direction
    perp_length = np.sqrt(perp_dx**2 + perp_dy**2)
    if perp_length == 0:
        return None
    
    perp_dx /= perp_length
    perp_dy /= perp_length
    
    # Create perpendicular line extending in both directions
    start_point = Point(
        quarter_point.x - length * perp_dx,
        quarter_point.y - length * perp_dy
    )
    end_point = Point(
        quarter_point.x + length * perp_dx,
        quarter_point.y + length * perp_dy
    )
    
    return LineString([start_point, end_point])

def find_perpendicular_intersections_ordered(gdf):
    """
    Find perpendicular intersections and return them ordered to create a convex polygon.
    """
    # Ensure we have at least 3 points
    if len(gdf) < 3:
        raise ValueError("Il faut mminimum 3 points pour créer un polygone")
    
    # Get reference point (first point)
    reference_point = gdf.geometry.iloc[0]
    other_points = gdf.geometry.iloc[1:]
    
    # Sort other points by angle from reference point to ensure convex polygon
    def angle_from_reference_point(point):
        return np.arctan2(point.y - reference_point.y, point.x - reference_point.x)
    
    # Create list of (point, angle) pairs and sort by angle
    point_angle_pairs = [(point, angle_from_reference_point(point)) for point in other_points]
    point_angle_pairs.sort(key=lambda x: x[1])
    sorted_points = [pair[0] for pair in point_angle_pairs]
    
    # Create perpendicular lines for each sorted point
    perpendicular_lines = []
    
    for other_point in sorted_points:
        quarter_point = find_quarter_point(reference_point, other_point)
        perp_line = get_perpendicular_line(reference_point, other_point, quarter_point)
        if perp_line is not None:
            perpendicular_lines.append(perp_line)
    
    # Find intersections between adjacent perpendicular lines to create convex polygon
    intersections = [] 
    n_lines = len(perpendicular_lines)
    
    for i in range(n_lines):
        # Get intersection with next line (wrap around for last line)
        j = (i + 1) % n_lines
        intersection = perpendicular_lines[i].intersection(perpendicular_lines[j])
        
        if not intersection.is_empty:
            if intersection.geom_type == 'Point':
                intersections.append(intersection)
            elif intersection.geom_type == 'MultiPoint':
                intersections.append(list(intersection.geoms)[0])
    
    return intersections, perpendicular_lines

def create_polygon_from_intersections(gdf, polygon_quarter_distance_shp):
    intersections, perpendicular_lines = find_perpendicular_intersections_ordered(gdf)
    """
    Create a polygon from intersection points by ordering them properly.
    """
    if len(intersections) < 3:
        raise ValueError("Il faut minimum 3 points pour créer un polygone")
    
    # Convert to coordinates
    coords = [(point.x, point.y) for point in intersections]
    
    # Find centroid for ordering points
    centroid_x = sum(x for x, y in coords) / len(coords)
    centroid_y = sum(y for x, y in coords) / len(coords)
    
    # Sort points by angle from centroid
    def angle_from_centroid(coord):
        x, y = coord
        return np.arctan2(y - centroid_y, x - centroid_x)
    
    sorted_coords = sorted(coords, key=angle_from_centroid)

    polygon = Polygon(sorted_coords)

    gdf_polygon = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[polygon])
    gdf_polygon = gdf_polygon.to_crs('EPSG:3812')
    gdf_polygon.to_file(polygon_quarter_distance_shp+'.shp', driver='ESRI Shapefile')

    return polygon

def visualisation_parcels(parcels, intersecting_parcels):
    fig, ax = plt.subplots(figsize=(12, 12))
    parcels.plot(ax=ax, color='lightgray', edgecolor='black', linewidth=0.3, alpha=0.5)
    intersecting_parcels.plot(ax=ax, color='red', edgecolor='black', linewidth=0.5, alpha=0.6)
    plt.title('Parcels intersecting the polygon')
    plt.show()