import pandas as pd
import geopandas as gpd

def load_db_from_excel(filepath):
    # Load your dataset
    # Assuming you have the dataset in a CSV file
    df = pd.DataFrame(pd.read_excel(filepath, header=None))

    # Drop the first row
    df = df.drop(index=0)

    # Extract the second row and set it as the new header
    new_header = df.iloc[0].str.split("\n").str[-1].tolist()
    new_header = [header.replace(" (Lambert 2008)", "") if "Lambert 2008" in header else header for header in new_header]
    df = df[1:]  # Take the data less the header row
    df.columns = new_header  # Set the header row as the df header

    df = df[df['Statut'].isna()]

    # Reset the index of the dataframe
    df.reset_index(drop=True, inplace=True)
    
    columns_to_drop = [5,6,7,10]
    df.drop(df.columns[columns_to_drop], axis=1, inplace=True)

    # Save the new dataframe to a new CSV file
    df.to_csv('Lst_Pharmacies_pub_Extended.csv', index=True)
        
    return df

def create_gdf_new_implentation(gdf, closest_points_old, New_adresse, new_coordinates):
    new_row = {
        'Numéro d\'autorisation': 999999,
        'Nom': closest_points_old.iloc[0,1],
        'Adresse': New_adresse[0],  # Replace with the actual new address if available
        'Code Postal': New_adresse[1],  # Placeholder, replace with actual postal code if available
        'Commune': New_adresse[2],  # Placeholder, replace with actual commune if available
        'X': 123456.789,  # Placeholder for new X coordinate, replace as needed
        'Y': 987654.321,  # Placeholder for new Y coordinate, replace as needed
        'geometry': new_coordinates # Placeholder, replace with actual geometry if available
    }
    # Convert the new row dictionary to a DataFrame
    new_row_df = pd.DataFrame([new_row])

    # Append the existing DataFrame to the new row DataFrame
    df_updated = pd.concat([new_row_df, gdf], ignore_index=True)

    df_updated = gpd.GeoDataFrame(df_updated, geometry='geometry')

    return df_updated