import pandas as pd
import geopandas as gpd
from shapely import wkt
import time

start = time.time()

# Define the file paths
# input_csv_path = r'D:\Pharmacy_Raph\adresses_wallonie.csv'  # Replace with your input CSV file path
# output_csv_path = r'D:\Pharmacy_Raph\adresses.csv'  # Replace with your desired output CSV file path

# input_csv_path = r'D:\Pharmacy_Raph\QGIS\URBIS_ADM_Adresses\adresses_bruxelles.csv'  # Replace with your input CSV file path
# output_csv_path = r'D:\Pharmacy_Raph\adresses_bruxelles.csv'  # Replace with your desired output CSV file path

input_csv_path = r"D:\Pharmacy_Raph\QGIS\Adresse_flandre_2.csv"  # Replace with your input CSV file path
output_csv_path = r"D:\Pharmacy_Raph\QGIS\Adresse_flandre_2_clean.csv"  # Replace with your desired output CSV file path

# Read the CSV file
df = pd.read_csv(input_csv_path)

# Specify the columns to keep
# columns_to_keep = ['X1', 'Y1','CODEPOSTAL','ZONE_ADRES','RUE_NOM','NUMERO']  #WALLONIE - Replace with the columns you want to keep
# columns_to_keep = ['XL72', 'YL72','ZIPCODE','MUNNAMEFRE','STRNAMEFRE','POLICENUM']  #BRUXELLES - Replace with the columns you want to keep
columns_to_keep = ['geometry','POSTCODE','GEMEENTE','STRAATNM','HUISNR']  #BRUXELLES - Replace with the columns you want to keep

# Keep only the specified columns
df = df[columns_to_keep]

df['geometry'] = df['geometry'].apply(wkt.loads) #FLANDRE
gdf = gpd.GeoDataFrame(df, geometry='geometry') #FLANDRE

# gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.XL72, df.YL72), crs = 'EPSG:31370') #BRUXELLES
# gdf = gdf.to_crs('epsg:3812') #BRUXELLES
gdf['X'] = gdf.geometry.x
gdf['Y'] = gdf.geometry.y
columns_to_keep_2 = ['X', 'Y','POSTCODE','GEMEENTE','STRAATNM','HUISNR']
# Keep only the specified columns
gdf = gdf[columns_to_keep_2]

# Save the modified DataFrame back to a CSV file
gdf.to_csv(output_csv_path, index=False)

print(f"Columns {columns_to_keep} have been kept and the new CSV file is saved as {output_csv_path}.")

end = time.time()
print(end-start)
