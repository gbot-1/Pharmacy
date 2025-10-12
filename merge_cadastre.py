import geopandas as gpd
import pandas as pd

# Write first file directly
print("Writing Brussels cadastre...")
first = gpd.read_file(r'D:/Pharmacy_Raph/QGIS/Cadastre/Bpn_CaPa_BRU.shp', columns=[])
target_crs = first.crs
first.to_file(r'D:/Pharmacy_Raph/QGIS/Cadastre/Belgian_Cadastre.shp')
del first  # Free memory

# Append other files one by one
file_list = [
    r'D:/Pharmacy_Raph/QGIS/Cadastre/Bpn_CaPa_VLA.shp',
    r'D:/Pharmacy_Raph/QGIS/Cadastre/Bpn_CaPa_WAL.shp'
]

for filename in file_list:
    print(f"Appending {filename.split('/')[-1]}...")
    gdf = gpd.read_file(filename, columns=[])
    gdf = gdf.to_crs(target_crs)
    
    # Read existing file, append, and overwrite
    existing = gpd.read_file(r'D:/Pharmacy_Raph/QGIS/Cadastre/Belgian_Cadastre.shp')
    combined = gpd.GeoDataFrame(
        pd.concat([existing, gdf], ignore_index=True),
        crs=target_crs
    )
    combined.to_file(r'D:/Pharmacy_Raph/QGIS/Cadastre/Belgian_Cadastre.shp')
    
    del gdf, existing, combined  # Free memory

print("Done!")

