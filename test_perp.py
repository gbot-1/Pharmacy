import geopandas as gpd
import numpy as np
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import nearest_points
import matplotlib.pyplot as plt
from typing import List, Tuple

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
        raise ValueError("Need at least 3 points in the GeoDataFrame")
    
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

def create_polygon_from_intersections(intersections):
    """
    Create a polygon from intersection points by ordering them properly.
    """
    if len(intersections) < 3:
        raise ValueError("Need at least 3 intersection points to create a polygon")
    
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
    
    return Polygon(sorted_coords)

def visualize_construction(gdf, intersections, perpendicular_lines, polygon=None):
    """
    Visualize the construction with highlighted intersections.
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    
    # Plot original points
    gdf.plot(ax=ax, color='red', markersize=100, alpha=0.7, label='Original Points')
    
    # Highlight reference point
    reference_point = gdf.geometry.iloc[0]
    ax.plot(reference_point.x, reference_point.y, 'ro', markersize=15, label='Reference Point (reference_point)')
    
    # Plot intersections with yellow circles
    for intersection in intersections:
        circle = plt.Circle((intersection.x, intersection.y), radius=0.5, 
                          color='yellow', alpha=0.8, linewidth=2, fill=False)
        ax.add_patch(circle)
    ax.plot([], [], 'o', color='yellow', markersize=10, alpha=0.8, 
            markerfacecolor='none', markeredgewidth=2, label='Intersections')
    
    for line in perpendicular_lines:
        x_coords, y_coords = line.xy
        ax.plot(x_coords, y_coords, 'b-', alpha=0.5, linewidth=1)
    ax.plot([], [], 'b-', alpha=0.5, linewidth=1, label='Perpendicular Lines')
    
    # Plot polygon if provided
    if polygon is not None:
        x_coords, y_coords = polygon.exterior.xy
        ax.plot(x_coords, y_coords, 'k-', linewidth=2, alpha=0.8, label='Resulting Polygon')
        ax.fill(x_coords, y_coords, alpha=0.2, color='lightblue')
    
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.set_title('Polygon Construction with Ordered Intersections')
    plt.tight_layout()
    plt.show()

# Example usage
def load_pharmacy_data(csv_file):
    """
    Load pharmacy data from CSV and create GeoDataFrame.
    """
    import pandas as pd
    
    # Read CSV
    df = pd.read_csv(csv_file)
    
    # Create points from X, Y coordinates
    points = [Point(row['X'], row['Y']) for _, row in df.iterrows()]
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=points)
    
    return gdf
def example_usage():
    """
    Example showing how to use the functions with pharmacy data.
    """
    gdf = load_pharmacy_data(r'D:\Pharmacy_Raph\2025\25-998_Pharmacie_Lejeune_Vdm\distance_closest_points_old.csv')
    try:
        # Find ordered intersections to create convex polygon
        intersections, perpendicular_lines = find_perpendicular_intersections_ordered(gdf)
        
        print(f"Created {len(intersections)} intersection points for {len(intersections)}-sided convex polygon")
        
        if len(intersections) >= 0:
            # Create polygon from ordered intersections
            coords = [(point.x, point.y) for point in intersections]
            polygon = Polygon(coords)
            
            # Verify if polygon is convex
            convex_hull = polygon.convex_hull
            is_convex = polygon.equals(convex_hull) or polygon.area / convex_hull.area > 0.99
            
            print(f"Created polygon with area: {polygon.area:.2f}")
            print(f"Is convex: {is_convex}")
            
            # Visualize
            visualize_construction(gdf, intersections, perpendicular_lines, polygon)
            
            gdf_polygon = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[polygon])
            gdf_polygon.to_file("polygon_25_perc.shp", driver='ESRI Shapefile')

            return polygon
        else:
            print("Not enough intersections to create a polygon")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

# Run example
if __name__ == "__main__":
    result_polygon = example_usage()