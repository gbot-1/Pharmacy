# import geopandas as gpd
# import pandas as pd
# from pathlib import Path

# # ===== CONFIGURATION - EDIT THESE VALUES =====
# SHAPEFILE_PATH = r"C:\Users\Win\Downloads\Adres_20251115_Shapefile\Shapefile\Adres_2.shp"  # Path to your input shapefile
# OUTPUT_CSV_PATH = "output.csv"  # Path to your output CSV file
# INCLUDE_GEOMETRY = True  # Set to False if you don't want geometry in CSV
# INPUT_EPSG = 31370  # Lambert72
# OUTPUT_EPSG = 3812  # Lambert2008
# # =============================================

# def shapefile_to_csv(shapefile_path, output_csv_path=None, include_geometry=True, 
#                      input_epsg=31370, output_epsg=3812):
#     """
#     Convert a shapefile to CSV format with coordinate transformation.
    
#     Parameters:
#     -----------
#     shapefile_path : str
#         Path to the input shapefile (.shp)
#     output_csv_path : str, optional
#         Path to the output CSV file. If None, uses the same name as input with .csv extension
#     include_geometry : bool, optional
#         If True, includes WKT geometry representation in the CSV (default: True)
#     input_epsg : int
#         EPSG code of input shapefile (default: 31370 - Lambert72)
#     output_epsg : int
#         EPSG code for output coordinates (default: 3812 - Lambert2008)
    
#     Returns:
#     --------
#     str : Path to the created CSV file
#     """
#     try:
#         # Read the shapefile
#         print(f"Reading shapefile: {shapefile_path}")
#         gdf = gpd.read_file(shapefile_path)
        
#         # Set CRS if not already set
#         if gdf.crs is None:
#             print(f"Setting CRS to EPSG:{input_epsg} (Lambert72)")
#             gdf = gdf.set_crs(f"EPSG:{input_epsg}")
#         else:
#             print(f"Input CRS: {gdf.crs}")
        
#         # Transform to Lambert2008
#         print(f"Transforming to EPSG:{output_epsg} (Lambert2008)")
#         gdf = gdf.to_crs(f"EPSG:{output_epsg}")
        
#         # Determine output path
#         if output_csv_path is None:
#             output_csv_path = Path(shapefile_path).with_suffix('.csv')
        
#         # Convert to DataFrame
#         if include_geometry:
#             # Convert geometry to WKT (Well-Known Text) format
#             df = pd.DataFrame(gdf)
#             df['geometry'] = gdf.geometry.to_wkt()
#         else:
#             # Drop geometry column
#             df = pd.DataFrame(gdf.drop(columns='geometry'))
        
#         # Save to CSV
#         print(f"Saving to CSV: {output_csv_path}")
#         df.to_csv(output_csv_path, index=False)
        
#         print(f"Successfully converted {len(df)} features")
#         print(f"Output CRS: EPSG:{output_epsg}")
#         print(f"Columns: {list(df.columns)}")
        
#         return output_csv_path
        
#     except Exception as e:
#         print(f"Error converting shapefile: {str(e)}")
#         raise

# if __name__ == "__main__":
#     # Run the conversion with the configured values
#     print("=" * 50)
#     print("Shapefile to CSV Converter")
#     print("=" * 50)
    
#     shapefile_to_csv(
#         shapefile_path=SHAPEFILE_PATH,
#         output_csv_path=OUTPUT_CSV_PATH,
#         include_geometry=INCLUDE_GEOMETRY,
#         input_epsg=INPUT_EPSG,
#         output_epsg=OUTPUT_EPSG
#     )
    
#     print("=" * 50)
#     print("Conversion complete!")
#     print("=" * 50)

import pandas as pd
from pathlib import Path

# ===== CONFIGURATION - EDIT THESE VALUES =====
CSV_FILES = [
    r"D:\Pharmacy_Raph\QGIS\Adresse_flandre_0_clean.csv",
    r"D:\Pharmacy_Raph\QGIS\Adresse_flandre_1_clean.csv",
    r"D:\Pharmacy_Raph\QGIS\Adresse_flandre_2_clean.csv"
]
OUTPUT_CSV = "merged_output.csv"

# Columns to use for identifying duplicates
# Use all columns that define a unique address
DUPLICATE_COLUMNS = ['X', 'Y', 'POSTCODE', 'GEMEENTE', 'STRAATNM', 'HUISNR']

# Which duplicate to keep: 'first' or 'last'
KEEP_DUPLICATE = 'first'

# Chunk size for reading large files (adjust based on your RAM)
CHUNK_SIZE = 100000
# =============================================

def merge_csv_files_efficient(csv_files, output_csv, duplicate_cols, keep='first', chunk_size=100000):
    """
    Efficiently merge multiple large CSV files and remove duplicates.
    
    Parameters:
    -----------
    csv_files : list
        List of CSV file paths to merge
    output_csv : str
        Path to output merged CSV file
    duplicate_cols : list
        Column names to use for identifying duplicates
    keep : str
        Which duplicate to keep: 'first' or 'last' (default: 'first')
    chunk_size : int
        Number of rows to process at a time (default: 100000)
    """
    print("=" * 60)
    print("CSV Merger with Deduplication")
    print("=" * 60)
    
    # First pass: merge all files using chunks
    print("\nStep 1: Merging CSV files...")
    temp_merged = "temp_merged.csv"
    first_file = True
    total_rows = 0
    
    for i, csv_file in enumerate(csv_files, 1):
        print(f"\nProcessing file {i}/{len(csv_files)}: {csv_file}")
        
        if not Path(csv_file).exists():
            print(f"  WARNING: File not found, skipping: {csv_file}")
            continue
        
        file_rows = 0
        for chunk in pd.read_csv(csv_file, chunksize=chunk_size):
            file_rows += len(chunk)
            total_rows += len(chunk)
            
            # Write to temp file
            if first_file:
                chunk.to_csv(temp_merged, mode='w', index=False, header=True)
                first_file = False
            else:
                chunk.to_csv(temp_merged, mode='a', index=False, header=False)
        
        print(f"  Rows processed: {file_rows:,}")
    
    print(f"\nTotal rows merged: {total_rows:,}")
    
    # Second pass: remove duplicates using chunks
    print("\nStep 2: Removing duplicates...")
    seen = set()
    rows_written = 0
    duplicates_found = 0
    first_chunk = True
    
    for chunk in pd.read_csv(temp_merged, chunksize=chunk_size):
        # Create a tuple key for each row based on duplicate columns
        chunk['_key'] = chunk[duplicate_cols].apply(
            lambda row: tuple(row.values), axis=1
        )
        
        # Filter out duplicates
        mask = ~chunk['_key'].isin(seen)
        unique_chunk = chunk[mask].copy()
        
        # Update seen set
        seen.update(unique_chunk['_key'])
        
        # Remove the temporary key column
        unique_chunk = unique_chunk.drop(columns=['_key'])
        
        duplicates_in_chunk = len(chunk) - len(unique_chunk)
        duplicates_found += duplicates_in_chunk
        
        # Write unique rows to output
        if len(unique_chunk) > 0:
            if first_chunk:
                unique_chunk.to_csv(output_csv, mode='w', index=False, header=True)
                first_chunk = False
            else:
                unique_chunk.to_csv(output_csv, mode='a', index=False, header=False)
            
            rows_written += len(unique_chunk)
        
        print(f"  Processed: {rows_written:,} unique | {duplicates_found:,} duplicates removed", end='\r')
    
    print(f"\n  Processed: {rows_written:,} unique | {duplicates_found:,} duplicates removed")
    
    # Clean up temp file
    Path(temp_merged).unlink(missing_ok=True)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total input rows:      {total_rows:,}")
    print(f"Unique rows kept:      {rows_written:,}")
    print(f"Duplicates removed:    {duplicates_found:,}")
    print(f"Duplicate rate:        {duplicates_found/total_rows*100:.2f}%")
    print(f"\nOutput saved to: {output_csv}")
    print("=" * 60)

if __name__ == "__main__":
    merge_csv_files_efficient(
        csv_files=CSV_FILES,
        output_csv=OUTPUT_CSV,
        duplicate_cols=DUPLICATE_COLUMNS,
        keep=KEEP_DUPLICATE,
        chunk_size=CHUNK_SIZE
    )