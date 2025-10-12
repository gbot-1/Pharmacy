import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

# Read your polygon
polygon_gdf = gpd.read_file(r'D:\Pharmacy_Raph\2025\25-000_Leriche_Benedicte\polygon_50_percent.shp')
my_polygon = polygon_gdf.geometry[0]  # Get the Shapely polygon

print(my_polygon)

print(f"Polygon bounds: {my_polygon.bounds}")
print(f"Polygon CRS: {polygon_gdf.crs}")

# Load ONLY the parcels that intersect your polygon's bounding box
# This is MUCH faster than loading the entire 900MB file
parcels = gpd.read_file(r'D:\Pharmacy_Raph\QGIS\Cadastre\Bpn_CaPa_WAL.shp', 
                        bbox=my_polygon.bounds,  # Only load relevant area
                        ignore_geometry=False,
                        include_fields=[])  # Skip attribute data for speed

print(f"Loaded {len(parcels)} parcels (instead of all)")

# Ensure same CRS
if parcels.crs != polygon_gdf.crs:
    parcels = parcels.to_crs(polygon_gdf.crs)

# # Clip/fit your polygon to the parcel boundaries
# fitted_gdf = gpd.overlay(parcels,polygon_gdf, how='intersection')

# # Or if you want just the Shapely geometry:
# # fitted_polygon = my_polygon.intersection(parcels.union_all)

# # Visualize
# fig, ax = plt.subplots(1, 2, figsize=(15, 7))

# # Before
# ax[0].set_title('Original Polygon')
# parcels.plot(ax=ax[0], color='lightgray', edgecolor='black', linewidth=0.5)
# polygon_gdf.plot(ax=ax[0], color='blue', alpha=0.5)

# # After
# ax[1].set_title('Fitted to Parcels')
# parcels.plot(ax=ax[1], color='lightgray', edgecolor='black', linewidth=0.5)
# fitted_gdf.plot(ax=ax[1], color='red', alpha=0.5)

# plt.tight_layout()
# plt.show()

# Select parcels that intersect (even slightly) with your polygon
intersecting_parcels = parcels[parcels.intersects(my_polygon)]

# Visualize
fig, ax = plt.subplots(figsize=(12, 12))
parcels.plot(ax=ax, color='lightgray', edgecolor='black', linewidth=0.3, alpha=0.5)
intersecting_parcels.plot(ax=ax, color='red', edgecolor='black', linewidth=0.5, alpha=0.6)
plt.title('Parcels intersecting the polygon')
plt.show()

# Get the union of all selected parcels as your fitted polygon
fitted_polygon = intersecting_parcels.union_all()

# Convert to GeoDataFrame for saving
fitted_gdf = gpd.GeoDataFrame([{'id': 1}], geometry=[fitted_polygon], crs=parcels.crs)

# Save to shapefile
fitted_gdf.to_file('fitted_polygon.shp')

print(f"Selected {len(intersecting_parcels)} parcels")
print(f"Saved to fitted_polygon.shp")