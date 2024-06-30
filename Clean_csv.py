import pandas as pd
import time

start = time.time()

# Define the file paths
input_csv_path = 'adresses_wallonie.csv'  # Replace with your input CSV file path
output_csv_path = 'adresses.csv'  # Replace with your desired output CSV file path

# Read the CSV file
df = pd.read_csv(input_csv_path)

# Specify the columns to keep
columns_to_keep = ['X', 'Y','CODEPOSTAL','ZONE_ADRES','RUE_NOM','NUMERO']  # Replace with the columns you want to keep

# Keep only the specified columns
df = df[columns_to_keep]

# Save the modified DataFrame back to a CSV file
df.to_csv(output_csv_path, index=False)

print(f"Columns {columns_to_keep} have been kept and the new CSV file is saved as {output_csv_path}.")

end = time.time()
print(end-start)
