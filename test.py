import pandas as pd
df = pd.DataFrame(pd.read_excel('D:/Pharmacy_Raph/Lst_Pharmacies_pub_Extended.xlsx', header=None))

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
print(df)