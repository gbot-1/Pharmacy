import geopandas as gpd
import pandas as pd
import numpy as np
import re
from shapely.geometry import Point, Polygon, LineString
import matplotlib.pyplot as plt

# Function to find the point at x% distance
def point_at_percentage(p1, p2, percentage):
    return Point(p1.x + percentage * (p2.x - p1.x), p1.y + percentage * (p2.y - p1.y))

# Function to get closest points at a given percentage distance
def gdf_at_percentage(gdf_init, reference_point, x_percentage, nb_vertex):
    closest_points = gdf_init.head(nb_vertex)
    closest_points['point_at_x%'] = closest_points.geometry.apply(
        lambda point: point_at_percentage(reference_point, point, x_percentage)
    )
    return closest_points

# Function to sort points in clockwise order
def angle_from_reference_point(point, reference_point):
    return np.arctan2(point[1] - reference_point.y, point[0] - reference_point.x)

def create_polygon(reference_point, coords):
    sorted_coords = sorted(coords, key=lambda point: angle_from_reference_point(point, reference_point))
    return Polygon(sorted_coords)

def is_point_inside_polygon(polygon, reference_point):
    return polygon.contains(reference_point)

def vertices_coords(gdf_points_init, reference_point, x_percentage, nb_vertex):
    closest_points = gdf_at_percentage(gdf_points_init, reference_point, x_percentage, nb_vertex)
    coords = np.array([[point.x, point.y] for point in closest_points['point_at_x%']])
    return coords

def generate_polygon(gdf_points_init, reference_point, x_percentage, nb_vertex):
    polygon = None
    gdf = gdf_points_init.iloc[1:]
    nb_vertex -= 1
    i = 0
    while polygon is None or not is_point_inside_polygon(polygon, reference_point):
        coords = vertices_coords(gdf, reference_point, x_percentage, nb_vertex + i)
        polygon = create_polygon(reference_point, coords)
        i += 1
        if i > 10:
            break
    return polygon

def alphanum_key(s):
    s = str(s)
    return tuple(int(text) if text.isdigit() else text for text in re.split('([0-9]+)', s))

def find_points_in_polygon(csv_file, polygon, output_file):
    points_df = pd.read_csv(csv_file)
    points_gdf = gpd.GeoDataFrame(points_df, geometry=gpd.points_from_xy(points_df.X, points_df.Y), crs="EPSG:4326")
    
    gdf_polygon = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[polygon])

    # Find points within the polygon
    points_within_polygon = gpd.sjoin(points_gdf, gdf_polygon, how='inner', predicate='within')

    # Apply the custom sort to NUMERO column
    points_within_polygon['NUMERO_SORT_KEY'] = points_within_polygon['NUMERO'].apply(alphanum_key)

    # Sort the data
    sorted_data = points_within_polygon.sort_values(by=['CODEPOSTAL', 'RUE_NOM', 'NUMERO_SORT_KEY'])
    sorted_data = sorted_data.drop(columns=['X', 'Y', 'NUMERO_SORT_KEY', 'geometry', 'index_right'])

    # Save the result to a new CSV file
    sorted_data.to_csv(output_file, index=False)
    gdf_polygon.to_file("polygon.shp", driver='ESRI Shapefile')

    return points_within_polygon

# Plotting function
def plot_polygon(gdf_points_init, reference_point, polygon, x_percentage, nb_vertex):
    closest_points = gdf_at_percentage(gdf_points_init, reference_point, x_percentage, nb_vertex)
    
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf_points_init.plot(ax=ax, color='blue', label='Point Cloud')
    gpd.GeoSeries([reference_point]).plot(ax=ax, color='red', label='Reference Point')
    gpd.GeoSeries([polygon]).plot(ax=ax, color='orange', alpha=0.5, edgecolor='black', label='Polygon')

    for idx, row in closest_points.iterrows():
        closest_point = row.geometry
        line = LineString([reference_point, closest_point])
        gpd.GeoSeries([line]).plot(ax=ax, color='green')
        point_at_x = row['point_at_x%']
        gpd.GeoSeries([point_at_x]).plot(ax=ax, color='purple')

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('2D Georeferenced Point Cloud with Closest Points and Polygon')
    plt.legend()
    plt.grid(True)
    plt.show()
